import pytest

from legaluga_bench.agent.parse import extract_json, parse_final_json
from legaluga_bench.schema import RunRecord, Task
from legaluga_bench.scoring.stats import bootstrap_ci, mcnemar_exact, paired_bootstrap_diff
from legaluga_bench.scoring.tracks import (
    score_case_lookup,
    score_citation_check,
    score_exam,
    score_research,
    score_statute,
)


def run_for(task: Task, text: str, error: str | None = None) -> RunRecord:
    return RunRecord(run_id="r1", task_id=task.id, track=task.track, system_id="s", model="m",
                     started_at="2026-10-13T00:00:00+00:00", final_text=text,
                     parsed=parse_final_json(text, task.track), error=error)


def test_extract_json_prefers_last_block():
    text = 'Önce {"a": 1}\n```json\n{"choice": "B"}\n```\nsonra ```json\n{"choice": "D", "x": "}"}\n```'
    assert extract_json(text) == {"choice": "D", "x": "}"}


def test_exam_choice_fallbacks():
    t = Task(id="e1", track="exam", prompt="?", options={k: k for k in "ABCDE"}, gold={"answer": "C"})
    assert score_exam(t, run_for(t, '```json\n{"choice": "C", "dayanak": ["TBK m.1"]}\n```')).correct
    assert score_exam(t, run_for(t, "Doğru cevap: C")).correct
    assert score_exam(t, run_for(t, '{"choice": "c)"}')).correct
    r = score_exam(t, run_for(t, "Bilmiyorum"))
    assert r.score == 0 and r.details["answered"] is False


def test_statute_scoring():
    t = Task(id="s1", track="statute", prompt="?",
             gold={"law_no": "6098", "article": "344", "accept": [r"on\s*iki\s*ay", r"12\s*ay"],
                   "quote_must_contain": ["tüketici fiyat endeksindeki"]})
    good = ('```json\n{"answer": "Önceki kira yılının on iki aylık ortalaması", "law_no": "6098", "article": "344/1",'
            ' "quoted_text": "...tüketici fiyat endeksindeki on iki aylık ortalamalara göre değişim oranını geçmemek..."}\n```')
    s = score_statute(t, run_for(t, good))
    assert s.score == pytest.approx(1.0) and s.correct
    wrong_article = good.replace('"article": "344/1"', '"article": "345"')
    assert score_statute(t, run_for(t, wrong_article)).score == pytest.approx(0.7)


def test_case_lookup_reciprocal_rank():
    gold = {"court": "Yargıtay", "chamber": "3. Hukuk Dairesi", "esas": "2010/119", "karar": "2010/478",
            "date": "2010-01-21"}
    t = Task(id="c1", track="case_lookup", prompt="?", gold=gold)
    second = ('```json\n{"decisions": [{"court": "Yargıtay", "chamber": "3. HD", "esas": "2010/120", "karar": "2010/400"},'
              ' {"court": "Yargıtay", "chamber": "3. HD", "esas": "2010/119", "karar": "2010/478", "date": "21.01.2010"}]}\n```')
    s = score_case_lookup(t, run_for(t, second))
    assert s.score == pytest.approx(0.5) and s.details["rank"] == 2 and s.details["date_ok"]
    assert score_case_lookup(t, run_for(t, "bulamadım")).score == 0


def test_citation_check_scoring():
    t = Task(id="k1", track="citation_check", prompt="?", gold={"items": [
        {"verdict": "var"}, {"verdict": "yok"}, {"verdict": "tarih_hatali", "correct_date": "21.01.2010"}]})
    text = ('```json\n{"items": [{"index": 1, "verdict": "var"}, {"index": 2, "verdict": "var"},'
            ' {"index": 3, "verdict": "tarih_hatali", "correct_date": "21.01.2010"}]}\n```')
    s = score_citation_check(t, run_for(t, text))
    assert s.score == pytest.approx(2 / 3, abs=1e-3)
    assert s.details["fabricated_caught"] == 0 and s.details["fabricated_total"] == 1
    no_date = text.replace(', "correct_date": "21.01.2010"', "")
    assert score_citation_check(t, run_for(t, no_date)).score == pytest.approx((1 + 0.75) / 3, abs=1e-3)


class FakeVerifier:
    async def verify_case(self, c):
        return "exists" if c.get("esas") in ("2010/119", "2010 / 119") else "not_found"

    async def verify_statute(self, law, art):
        return "exists"


async def test_research_combines_rubric_and_validity():
    t = Task(id="r1", track="research", prompt="?", gold={"rubric": [{"point": "x", "weight": 1}]})

    async def judge(q, rubric, answer, ref):
        return {"score": 1.0}

    text = ('Cevap. Yargıtay 3. HD E. 2010/119, K. 2010/478 ve Yargıtay 3. HD E. 2019/8841, K. 2019/5874.\n'
            '```json\n{"answer": "Cevap", "citations": [{"type": "mevzuat", "law_no": "6098", "article": "344"}]}\n```')
    s = await score_research(t, run_for(t, text), judge, FakeVerifier())
    # 3 atıf: 2 geçerli (1 karar + 1 madde), 1 uydurma -> geçerlilik 2/3
    assert s.details["citations"]["n_fabricated"] == 1
    assert s.score == pytest.approx(0.7 + 0.3 * 2 / 3, abs=1e-3)
    no_cites = await score_research(t, run_for(t, '```json\n{"answer": "Cevap", "citations": []}\n```'), judge,
                                    FakeVerifier())
    assert no_cites.score == pytest.approx(0.7)
    unverified = await score_research(t, run_for(t, text), judge, None)
    assert unverified.score == pytest.approx(1.0)


def test_stats():
    lo, hi = bootstrap_ci([1.0] * 10)
    assert lo == hi == 1.0
    d = paired_bootstrap_diff([1, 1, 1, 0], [0, 0, 1, 0])
    assert d["mean_diff"] == pytest.approx(0.5) and d["n"] == 4
    mc = mcnemar_exact([True] * 10 + [False] * 2, [False] * 10 + [False] * 2)
    assert mc["only_a"] == 10 and mc["p_value"] < 0.01
    assert mcnemar_exact([True], [True])["p_value"] == 1.0


def test_grounding_unknown_for_external_runs_without_tool_outputs():
    from legaluga_bench.schema import RunRecord, ToolCallLog
    from legaluga_bench.scoring.tracks import grounding

    run = RunRecord(run_id="r", task_id="t", track="case_lookup", system_id="s", model="m", runner="external",
                    started_at="", tool_calls=[ToolCallLog(name="WebSearch")])
    cases = [{"court": "Yargıtay", "chamber": "3. HD", "esas": "2010/119", "karar": "2010/478"}]
    assert grounding(run, cases) is None


def test_text_citation_repeating_structured_one_is_not_double_counted():
    from legaluga_bench.schema import RunRecord
    from legaluga_bench.scoring.tracks import collect_citations

    text = ("BAM'lar arasındaki görüş ayrılığını gideren 2025/1495 E., 2025/3048 K. sayılı karar...\n"
            '```json\n{"answer": "x", "citations": [{"type": "karar", "court": "Yargıtay", '
            '"chamber": "3. Hukuk Dairesi", "esas": "2025/1495", "karar": "2025/3048"}]}\n```')
    from legaluga_bench.agent.parse import parse_final_json
    run = RunRecord(run_id="r", task_id="t", track="research", system_id="s", model="m", started_at="",
                    final_text=text, parsed=parse_final_json(text, "research"))
    cases, _ = collect_citations(run)
    assert len(cases) == 1 and cases[0]["court"] == "Yargıtay"
