"""Track bazında puanlama. Her fonksiyon (Task, RunRecord) alır, ScoreRecord döndürür.

Puanlar 0-1 arasıdır. Ayrıntılar (`details`) raporda alt metrik olarak kullanılır.
Formüller docs/METODOLOJI.md içinde belgelenmiştir; değiştirilirse orası da güncellenmelidir.
"""

from __future__ import annotations

import re
from typing import Any, Protocol

from ..schema import RunRecord, ScoreRecord, Task
from .citations import (
    case_key,
    extract_case_citations,
    extract_statute_citations,
    fold,
    match_case,
    norm_article,
    norm_date,
    norm_law_no,
    statute_key,
    strip_gk_prefix,
)


class CitationVerifier(Protocol):
    """Atıfları resmî kaynakta doğrular.

    Dönüş: 'exists' | 'not_found' | 'unknown'; kararlarda ayrıca 'chamber_mismatch'
    (numara var ama atıfta gösterilen dairede değil). Geçerlilik oranında yalnız
    'exists' geçerli sayılır; 'not_found' uydurma sayılır.
    """

    async def verify_case(self, citation: dict[str, Any]) -> str: ...

    async def verify_statute(self, law_no: str, article: str) -> str: ...


def grounding(run: RunRecord, cases: list[dict[str, Any]]) -> float | None:
    """Cevaptaki karar künyelerinden, esas ve karar numarası ajanın araç çıktılarında geçenlerin oranı.

    Araç kullanmayan sistemlerde (kapalı kitap) ve hiç künye verilmeyen cevaplarda None döner.
    Yüksek oran, künyenin modelin belleğinden değil aracın döndürdüğü kaynaktan geldiğini gösterir.
    """
    seen = {n for tc in run.tool_calls for n in tc.numbers_seen}
    keys = [case_key(c) for c in cases]
    keys = [k for k in keys if k.esas and (k.karar or k.chamber == "BB")]
    if not keys or not run.tool_calls:
        return None
    ok = sum(1 for k in keys if strip_gk_prefix(k.esas) in seen and (k.karar is None or k.karar in seen))
    return ok / len(keys)


def _record(task: Task, run: RunRecord, score: float, correct: bool | None, **details: Any) -> ScoreRecord:
    return ScoreRecord(
        run_id=run.run_id,
        task_id=task.id,
        system_id=run.system_id,
        track=task.track,
        score=max(0.0, min(1.0, round(score, 4))),
        correct=correct,
        details={"error": run.error, **details},
    )


# --- sınav ------------------------------------------------------------------------


def score_exam(task: Task, run: RunRecord) -> ScoreRecord:
    gold = (task.gold.get("answer") or "").strip().upper()
    choice = run.parsed.get("choice")
    correct = bool(choice) and choice == gold
    dayanak = run.parsed.get("dayanak") or []
    return _record(task, run, 1.0 if correct else 0.0, correct, choice=choice, gold=gold,
                   answered=choice is not None, n_dayanak=len(dayanak) if isinstance(dayanak, list) else 0)


# --- mevzuat ------------------------------------------------------------------------


def _any_regex(patterns: list[str], text: str) -> bool:
    folded = fold(text)
    return any(re.search(fold(p), folded) for p in patterns)


def score_statute(task: Task, run: RunRecord) -> ScoreRecord:
    """0.5 cevap doğruluğu + 0.3 doğru madde + 0.2 aktarılan metnin sadakati."""
    g = task.gold
    p = run.parsed
    answer_text = " ".join(str(p.get(k) or "") for k in ("answer", "quoted_text")) or run.final_text
    accept = g.get("accept") or []
    answer_ok = bool(accept) and _any_regex(accept, answer_text)

    gold_law, gold_art = norm_law_no(g.get("law_no")), norm_article(g.get("article"))
    pred_law, pred_art = norm_law_no(p.get("law_no")), norm_article(p.get("article"))
    if not (pred_law and pred_art):
        for c in p.get("citations") or []:
            if isinstance(c, dict):
                pred_law, pred_art = statute_key(c)
                if pred_law and pred_art:
                    break
    if not (pred_law and pred_art):
        found = extract_statute_citations(run.final_text)
        if found:
            pred_law, pred_art = found[0]["law_no"], found[0]["article"]
    article_ok = gold_law is not None and pred_law == gold_law and (
        gold_art is None or (pred_art or "").split("/")[0] == gold_art.split("/")[0]
    )

    must = g.get("quote_must_contain") or []
    quoted = fold(str(p.get("quoted_text") or ""))
    fidelity = (sum(1 for s in must if fold(s) in quoted) / len(must)) if must else (1.0 if article_ok else 0.0)

    score = 0.5 * answer_ok + 0.3 * article_ok + 0.2 * fidelity
    return _record(task, run, score, answer_ok and article_ok, answer_ok=answer_ok, article_ok=article_ok,
                   quote_fidelity=round(fidelity, 3), pred_law=pred_law, pred_article=pred_art)


# --- karar bulma ---------------------------------------------------------------------


def score_case_lookup(task: Task, run: RunRecord) -> ScoreRecord:
    """Doğru kararın sırasına göre karşılıklı sıra puanı (1, 1/2, 1/3); yoksa 0."""
    gold = task.gold
    decisions = [d for d in (run.parsed.get("decisions") or []) if isinstance(d, dict)][:3]
    if not decisions:
        decisions = extract_case_citations(run.final_text)[:3]
    rank = None
    partial = False
    for i, d in enumerate(decisions, 1):
        m = match_case(d, gold)
        if m.exact:
            rank = i
            break
        if m.esas or m.karar:
            partial = True
    score = 1.0 / rank if rank else 0.0
    date_ok = None
    if rank:
        date_ok = norm_date(decisions[rank - 1].get("date")) == norm_date(gold.get("date")) if gold.get("date") else None
    return _record(task, run, score, rank == 1, rank=rank, partial_number_match=partial,
                   date_ok=date_ok, n_returned=len(decisions), grounding=grounding(run, decisions),
                   predicted=[case_key(d).short() for d in decisions], gold=case_key(gold).short())


# --- atıf denetimi --------------------------------------------------------------------

_VERDICTS = {"var", "tarih_hatali", "yok", "belirsiz"}


def score_citation_check(task: Task, run: RunRecord) -> ScoreRecord:
    """Her atıf için doğru hüküm 1 puan; 'tarih_hatali' hükmünde doğru tarih de verilmişse tam, verilmemişse 0.75."""
    gold_items = task.gold.get("items") or []
    pred = {int(it.get("index", 0)): it for it in (run.parsed.get("items") or []) if isinstance(it, dict)}
    per_item: list[dict[str, Any]] = []
    total = 0.0
    for i, g in enumerate(gold_items, 1):
        p = pred.get(i, {})
        verdict = str(p.get("verdict", "")).strip().lower()
        verdict = verdict if verdict in _VERDICTS else "cevapsiz"
        s = 0.0
        if verdict == g["verdict"]:
            s = 1.0
            if g["verdict"] == "tarih_hatali" and g.get("correct_date"):
                s = 1.0 if norm_date(p.get("correct_date")) == norm_date(g["correct_date"]) else 0.75
        total += s
        per_item.append({"index": i, "gold": g["verdict"], "pred": verdict, "score": s})
    n = len(gold_items) or 1
    fabricated = [x for x in per_item if x["gold"] == "yok"]
    genuine = [x for x in per_item if x["gold"] == "var"]
    return _record(
        task, run, total / n, total == len(gold_items),
        items=per_item,
        fabricated_caught=sum(1 for x in fabricated if x["pred"] == "yok"),
        fabricated_total=len(fabricated),
        genuine_wrongly_rejected=sum(1 for x in genuine if x["pred"] == "yok"),
        genuine_total=len(genuine),
    )


# --- açık araştırma ---------------------------------------------------------------------


def collect_citations(run: RunRecord) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Cevaptaki karar ve mevzuat atıflarını (JSON alanı + serbest metin) toplar."""
    cases: list[dict[str, Any]] = []
    statutes: list[dict[str, Any]] = []
    for c in run.parsed.get("citations") or []:
        if not isinstance(c, dict):
            continue
        if c.get("type") == "mevzuat" or c.get("law_no"):
            statutes.append(c)
        elif c.get("esas") or c.get("karar") or c.get("basvuru_no"):
            cases.append(c)
    seen_cases = {case_key(c) for c in cases}
    for c in extract_case_citations(run.final_text):
        if case_key(c) not in seen_cases:
            cases.append(c)
            seen_cases.add(case_key(c))
    seen_st = {statute_key(c) for c in statutes}
    for c in extract_statute_citations(run.final_text):
        if statute_key(c) not in seen_st:
            statutes.append(c)
            seen_st.add(statute_key(c))
    return cases, statutes


async def verify_citations(run: RunRecord, verifier: CitationVerifier | None) -> dict[str, Any]:
    cases, statutes = collect_citations(run)
    out: dict[str, Any] = {"n_case_citations": len(cases), "n_statute_citations": len(statutes),
                           "grounding": grounding(run, cases)}
    if verifier is None:
        return out
    case_results = [await verifier.verify_case(c) for c in cases]
    st_results = []
    for c in statutes:
        law, art = statute_key(c)
        st_results.append(await verifier.verify_statute(law, art) if law and art else "unknown")
    checked = [r for r in case_results + st_results if r != "unknown"]
    out.update(
        case_verdicts=[{"citation": case_key(c).short(), "result": r} for c, r in zip(cases, case_results)],
        statute_verdicts=[{"citation": f"{statute_key(c)[0]} m.{statute_key(c)[1]}", "result": r}
                          for c, r in zip(statutes, st_results)],
        n_fabricated=sum(1 for r in case_results + st_results if r == "not_found"),
        citation_validity=(sum(1 for r in checked if r == "exists") / len(checked)) if checked else None,
    )
    return out


async def score_research(
    task: Task,
    run: RunRecord,
    judge_fn: Any,
    verifier: CitationVerifier | None = None,
) -> ScoreRecord:
    """0.7 rubrik puanı (kör hakem) + 0.3 atıf geçerliliği (resmî kaynakta bulunan atıf oranı).

    Hiç atıf yoksa geçerlilik terimi 0'dır (araştırma sorusu kaynak ister). Doğrulayıcı
    yoksa ya da hiçbir atıf denetlenemediyse puan yalnız rubrikten gelir.
    """
    answer = str(run.parsed.get("answer") or "") or run.final_text
    judged = await judge_fn(task.prompt, task.gold.get("rubric") or [], answer, task.gold.get("reference_answer"))
    cit = await verify_citations(run, verifier)
    rubric_score = float(judged.get("score", 0.0))
    n_cited = cit["n_case_citations"] + cit["n_statute_citations"]
    if verifier is not None and n_cited == 0:
        score = 0.7 * rubric_score
    elif verifier is not None and cit.get("citation_validity") is not None:
        score = 0.7 * rubric_score + 0.3 * float(cit["citation_validity"])
    else:
        score = rubric_score
    return _record(task, run, score, None, rubric_score=rubric_score, judge=judged, citations=cit)


SYNC_SCORERS = {
    "exam": score_exam,
    "statute": score_statute,
    "case_lookup": score_case_lookup,
    "citation_check": score_citation_check,
}
