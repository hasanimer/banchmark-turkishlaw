import json

from legaluga_bench.exams.build import build
from legaluga_bench.io import read_jsonl

OPTS = {k: f"şık {k}" for k in "ABCDE"}


def q(stem_file, qno, **kw):
    row = {"source_file": stem_file, "pages": [qno], "q_no": qno, "stem": f"Soru {qno} metni",
           "options": dict(OPTS), "answer": "B", "subject": "Borçlar Hukuku", "is_law": True,
           "has_figure": False, "partial": False, "tool_relevance": "statute", "basis_hint": [], "notes": ""}
    row.update(kw)
    return row


def write(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def test_build_merges_partials_filters_and_compares_captures(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    write(raw / "hmgs_2025_1__p001-002.jsonl", [
        q("hmgs_2025_1", 1),
        q("hmgs_2025_1", 2, stem="Olay: A, B'ye", options={"A": "a", "B": "b", "C": "", "D": "", "E": ""},
          answer=None, partial=True, pages=[2]),
        q("hmgs_2025_1", 3, is_law=False, subject="GKGY-Türkçe"),
        q("hmgs_2025_1", 4, answer=None),
        q("hmgs_2025_1", 5, has_figure=True),
    ])
    write(raw / "hmgs_2025_1__p003-004.jsonl", [
        q("hmgs_2025_1", 2, stem="kira borcunu ödemedi. Buna göre hangisi doğrudur?",
          options={"A": "", "B": "", "C": "c", "D": "d", "E": "e"}, answer="D", partial=True, pages=[3]),
    ])
    # Aynı oturumun iki çekimi: 1. soru uyuşuyor, 2. soru uyuşmuyor.
    write(raw / "hmgs_eylul__p001-002.jsonl", [q("hmgs_eylul", 1, answer="A"), q("hmgs_eylul", 2, answer="C")])
    write(raw / "hmgs_2026_eylul_b__p001-002.jsonl", [q("hmgs_2026_eylul_b", 1, answer="A"),
                                                      q("hmgs_2026_eylul_b", 2, answer="E")])
    tasks_out, manifest_out = tmp_path / "tasks.jsonl", tmp_path / "manifest.json"
    manifest = build(raw, tasks_out, manifest_out)

    tasks = {t["id"]: t for t in read_jsonl(tasks_out)}
    assert set(tasks) == {"exam-hmgs-2025-1-q001", "exam-hmgs-2025-1-q002", "exam-hmgs-2026-eylul-q001"}
    merged = tasks["exam-hmgs-2025-1-q002"]
    assert merged["options"] == {"A": "a", "B": "b", "C": "c", "D": "d", "E": "e"}
    assert merged["gold"]["answer"] == "D"
    assert "Olay: A, B'ye" in merged["prompt"] and "kira borcunu" in merged["prompt"]
    assert "HMGS 2025/1" in merged["prompt"]
    assert tasks["exam-hmgs-2026-eylul-q001"]["meta"]["captures_agree"] == 2
    assert manifest["rejected"] == {"hukuk_disi": 1, "cevap_anahtari_yok": 1, "sekil": 1, "cekim_uyusmazligi": 1}
    assert manifest["capture_conflicts"] == [{"session": "hmgs-2026-eylul", "q_no": 2, "answers": ["C", "E"]}]
    assert "Soru 1 metni" not in manifest_out.read_text(encoding="utf-8")  # manifest soru metni içermez
