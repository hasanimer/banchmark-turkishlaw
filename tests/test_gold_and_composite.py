from dataclasses import dataclass, field

import pytest

from legaluga_bench.official.bedesten import birim_adi, number_phrase
from legaluga_bench.official.gold_case_lookup import _leaks
from legaluga_bench.scoring.judge import blind, external_judge, weighted_score
from legaluga_bench.systems.base import SystemConfig, ToolProvider, ToolResult, ToolSpec
from legaluga_bench.systems.composite import CompositeProvider


def test_case_description_leak_check():
    gold = {"esas": "2010/119", "karar": "2010/478", "date": "2010-01-21"}
    assert _leaks("Kiracı, 2010 yılında tespit davası açmış ...", gold) == []
    assert _leaks("2010/119 esas sayılı dosyada ...", gold) == ["esas"]
    assert _leaks("karar 2010 / 478 numarasıyla", gold) == ["karar"]
    assert _leaks("21.01.2010 tarihinde verilen kararda", gold) == ["date"]
    assert _leaks("TBK m.344 uyarınca 2.000 TL ...", gold) == []


def test_bedesten_query_helpers():
    assert number_phrase("2010/119", "2010/478") == '+"2010 119" +"2010 478"'
    assert number_phrase("2013/7-591", "2017/954") == '+"2013 591" +"2017 954"'
    assert birim_adi("yargitay", "H3") == "3. Hukuk Dairesi"
    assert birim_adi("yargitay", "C12") == "12. Ceza Dairesi"
    assert birim_adi("danistay", "D5") == "5. Daire"
    assert birim_adi("yargitay", "HGK") == "Hukuk Genel Kurulu"
    assert birim_adi("danistay", "VDDK") == "Vergi Dava Daireleri Kurulu"


async def test_external_judge_and_blinding():
    rubric = [{"point": "a", "weight": 2}, {"point": "b", "weight": 1}]
    fn = external_judge({("t1", "s1"): {"criteria": [{"index": 1, "score": 1}, {"index": 2, "score": 0.5}]}}, "t1", "s1")
    out = await fn("q", rubric, "ans", None)
    assert out["score"] == pytest.approx((2 + 0.5) / 3, abs=1e-3)
    missing = await external_judge({}, "t1", "s2")("q", rubric, "ans", None)
    assert missing["score"] == 0 and "error" in missing
    assert weighted_score(rubric, []) == 0
    assert "Legaluga" not in blind("Legaluga MCP ile karar_ara aracını kullandım")
    assert "Bedesten" in blind("Bedesten kaydına göre")


@dataclass
class Member(ToolProvider):
    names: list = field(default_factory=list)
    calls: list = field(default_factory=list)

    async def open(self):
        self.tools = [ToolSpec(name=n) for n in self.names]
        self.instructions = f"{self.system_id} talimatı"

    async def list_tools(self):
        return self.tools

    async def call_tool(self, name, arguments):
        self.calls.append(name)
        return ToolResult(text=f"{self.system_id}:{name}")


async def test_composite_routes_and_prefixes_collisions():
    a = Member(config=SystemConfig(id="a", label="A", kind="none"), names=["search", "only_a"])
    b = Member(config=SystemConfig(id="b", label="B", kind="none"), names=["search", "only_b"])
    comp = CompositeProvider(config=SystemConfig(id="ab", label="AB", kind="composite", exclude_tools=["only_b"]),
                             members=[a, b])
    await comp.open()
    names = [t.name for t in await comp.list_tools()]
    assert names == ["search", "only_a", "b__search"]
    assert (await comp.call_tool("b__search", {})).text == "b:search"
    assert (await comp.call_tool("search", {})).text == "a:search"
    assert (await comp.call_tool("only_b", {})).is_error  # dışlanan araç
    assert "a talimatı" in comp.instructions and "b talimatı" in comp.instructions
    fp = comp.fingerprint()
    assert fp["n_tools"] == 3 and len(fp["tools_sha256"]) == 64


def test_outside_coverage_citations_are_not_called_fabricated():
    from legaluga_bench.official.bedesten import outside_coverage

    assert outside_coverage({"court": "Yargıtay", "chamber": "İBK", "esas": "1990/4", "karar": "1991/3"})
    assert outside_coverage({"court": "Yargıtay", "chamber": "HGK", "esas": "2007/422", "karar": "2007/536"})
    assert not outside_coverage({"court": "Yargıtay", "chamber": "3. HD", "esas": "2026/484", "karar": "2026/3681"})
