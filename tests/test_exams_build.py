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
    assert manifest["capture_conflicts"] == [{"session": "hmgs-2026-eylul", "section": "", "q_no": 2,
                                              "answers": ["C", "E"]}]
    assert "Soru 1 metni" not in manifest_out.read_text(encoding="utf-8")  # manifest soru metni içermez


def test_restarting_numbering_becomes_sections(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    # Ortak alan 1-10 (s.1-10), idari yargı 1-9 (s.11-19; 9. soru iki parçaya bölünmüş), adli yargı 1-2.
    rows = [q("hakimlik_2018_adli", n, pages=[n], exam_guess="2018 hakimlik ortak alan soruları") for n in range(1, 11)]
    rows += [q("hakimlik_2018_adli", n, pages=[10 + n], exam_guess="İdari yargı soruları", answer="C")
             for n in range(1, 9)]
    rows.append(q("hakimlik_2018_adli", 9, pages=[19], exam_guess="İdari yargı soruları", partial=True, answer=None,
                  options={"A": "a", "B": "b", "C": "", "D": "", "E": ""}))
    write(raw / "hakimlik_2018_adli__p001-019.jsonl", rows)
    write(raw / "hakimlik_2018_adli__p020-021.jsonl", [
        q("hakimlik_2018_adli", 9, pages=[20], exam_guess="İdari yargı soruları", partial=True, answer="E",
          options={"A": "", "B": "", "C": "c", "D": "d", "E": "e"}),
        q("hakimlik_2018_adli", 1, pages=[20], exam_guess="Adli yargı", answer="D"),
        q("hakimlik_2018_adli", 2, pages=[21], exam_guess="Adli yargı", answer="A"),
    ])
    tasks_out, manifest_out = tmp_path / "tasks.jsonl", tmp_path / "manifest.json"
    build(raw, tasks_out, manifest_out)
    tasks = {t["id"]: t for t in read_jsonl(tasks_out)}
    assert set(tasks) == ({f"exam-hsa-2018-b1-q{n:03d}" for n in range(1, 11)}
                          | {f"exam-hsa-2018-b2-q{n:03d}" for n in range(1, 10)}
                          | {"exam-hsa-2018-b3-q001", "exam-hsa-2018-b3-q002"})
    assert tasks["exam-hsa-2018-b2-q009"]["gold"]["answer"] == "E"
    assert tasks["exam-hsa-2018-b2-q009"]["options"]["A"] == "a"
    assert tasks["exam-hsa-2018-b3-q001"]["gold"]["answer"] == "D"
    assert tasks["exam-hsa-2018-b3-q002"]["meta"]["section_name"] == "adli"
    assert tasks["exam-hsa-2018-b2-q001"]["meta"]["section_name"] == "idari"
    assert tasks["exam-hsa-2018-b1-q001"]["meta"]["section_name"] == "ortak"


def test_shuffled_pages_do_not_split_sections(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    order = [3, 1, 2, 5, 4, 7, 6, 14, 9, 10, 11, 12, 13, 8, 15]
    write(raw / "iyoss_2025__p001-015.jsonl", [q("iyoss_2025", n, pages=[i]) for i, n in enumerate(order, 1)])
    tasks_out, manifest_out = tmp_path / "tasks.jsonl", tmp_path / "manifest.json"
    build(raw, tasks_out, manifest_out)
    ids = {t["id"] for t in read_jsonl(tasks_out)}
    assert ids == {f"exam-iyos-2025-q{n:03d}" for n in range(1, 16)}


def test_audit_rejects_doubtful_keys_and_stale_questions(tmp_path):
    raw, audit = tmp_path / "raw", tmp_path / "audit"
    raw.mkdir()
    audit.mkdir()
    write(raw / "hmgs_2025_1__p001-003.jsonl", [q("hmgs_2025_1", n) for n in (1, 2, 3)])
    write(audit / "a.jsonl", [
        {"id": "exam-hmgs-2025-1-q001", "provisions": ["6098 m.344"], "stale_risk": False, "key_check": "consistent"},
        {"id": "exam-hmgs-2025-1-q002", "provisions": [], "stale_risk": False, "key_check": "uncertain"},
        {"id": "exam-hmgs-2025-1-q003", "provisions": [], "stale_risk": True, "key_check": "consistent"},
    ])
    manifest = build(raw, tmp_path / "t.jsonl", tmp_path / "m.json", audit_dir=audit)
    tasks = {t["id"]: t for t in read_jsonl(tmp_path / "t.jsonl")}
    assert set(tasks) == {"exam-hmgs-2025-1-q001"}
    assert tasks["exam-hmgs-2025-1-q001"]["meta"]["audit"]["provisions"] == ["6098 m.344"]
    assert tasks["exam-hmgs-2025-1-q001"]["meta"]["stale_risk"] is False
    assert manifest["rejected"] == {"anahtar_supheli": 1, "guncellik_riski": 1}
    assert manifest["audit"]["n_audited"] == 3
