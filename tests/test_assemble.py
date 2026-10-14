import asyncio
import json

from legaluga_bench.io import read_jsonl
from legaluga_bench.official import assemble as asm


class FakeClient:
    async def article_text(self, law_no, article, tur="KANUN"):
        return {"text": "Kiracı, belirli süreli sözleşmelerin süresinin bitiminden en az onbeş gün önce bildirimde bulunmadıkça"}

    async def aclose(self):
        pass


class FakeVerifier:
    def __init__(self, client):
        pass

    async def verify_statute(self, law_no, article):
        return "exists" if article == "344" else "not_found"

    async def verify_case(self, c):
        return "exists" if c.get("esas") == "2026/484" else "not_found"


def statute(i, must, accept=("\\b(15|on\\s*bes)\\s*gun",)):
    return {"id": f"statute-x-{i}", "track": "statute", "prompt": "?",
            "gold": {"law_no": "6098", "article": "347", "accept": list(accept), "quote_must_contain": must,
                     "reference_answer": "En az onbeş gün önce bildirim gerekir."}}


def research(i, sources):
    return {"id": f"research-x-{i}", "track": "research", "prompt": "?",
            "gold": {"rubric": [{"point": "p", "weight": 1}], "official_sources": sources}}


def test_assemble_checks_quotes_accept_and_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(asm, "BedestenClient", FakeClient)
    monkeypatch.setattr(asm, "BedestenVerifier", FakeVerifier)
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    rows = [statute(1, ["süresinin bitiminden en az onbeş gün önce"]),
            statute(2, ["en az otuz gün önce"]),
            statute(3, ["onbeş gün"], accept=["\\byirmi\\b"])]
    (drafts / "statute_a.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), "utf-8")
    # Doğrulanmış sürüm varsa ham taslak yerine o okunur.
    (drafts / "research_b.jsonl").write_text(json.dumps(research(9, [])), "utf-8")
    good = research(1, [{"type": "mevzuat", "law_no": "6098", "article": "344"},
                        {"type": "karar", "court": "Yargıtay", "chamber": "3. HD", "esas": "2026/484", "karar": "1"}])
    bad = research(2, [{"type": "karar", "court": "Yargıtay", "chamber": "3. HD", "esas": "2026/999", "karar": "1"}])
    (drafts / "research_b.verified.jsonl").write_text("\n".join(json.dumps(r) for r in (good, bad)), "utf-8")

    s = asyncio.run(asm.assemble("statute", tmp_path / "statute.jsonl", drafts))
    assert [t["id"] for t in read_jsonl(tmp_path / "statute.jsonl")] == ["statute-x-1"]
    assert set(s["rejected"]) == {"statute-x-2", "statute-x-3"}

    s = asyncio.run(asm.assemble("research", tmp_path / "research.jsonl", drafts))
    assert [t["id"] for t in read_jsonl(tmp_path / "research.jsonl")] == ["research-x-1"]
    assert list(s["rejected"]) == ["research-x-2"]
    assert s["files"] == ["research_b.verified.jsonl"]
