"""Ajan döngüsü: sahte Anthropic istemcisi ve sahte araç sağlayıcısıyla uçtan uca."""

from dataclasses import dataclass, field
from types import SimpleNamespace as NS
from typing import Any

from legaluga_bench.agent.loop import AgentSettings, run_task
from legaluga_bench.schema import Task
from legaluga_bench.systems.base import SystemConfig, ToolProvider, ToolResult, ToolSpec


def text(t):
    return NS(type="text", text=t)


def tool_use(i, name, inp):
    return NS(type="tool_use", id=f"tu{i}", name=name, input=inp)


def resp(content, stop):
    return NS(content=content, stop_reason=stop, model="test-model",
              usage=NS(input_tokens=10, output_tokens=5, cache_read_input_tokens=0, server_tool_use=None))


class FakeMessages:
    def __init__(self, script):
        self.script = list(script)
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs):
        # Döngü mesaj listesini sonradan büyüttüğü için çağrı anındaki hâli saklanır.
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.script.pop(0)


class FakeClient:
    def __init__(self, script):
        self.messages = FakeMessages(script)


@dataclass
class FakeProvider(ToolProvider):
    calls: list = field(default_factory=list)

    async def list_tools(self):
        return [ToolSpec(name="karar_ara", description="ara", input_schema={"type": "object", "properties": {}})]

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if arguments.get("fail"):
            return ToolResult(text="hata", is_error=True)
        return ToolResult(text=f"sonuç:{arguments.get('q')}")


TASK = Task(id="e1", track="exam", prompt="Soru?", options={k: k for k in "ABCDE"}, gold={"answer": "B"})


async def test_tool_loop_and_parse():
    client = FakeClient([
        resp([text("arıyorum"), tool_use(1, "karar_ara", {"q": "x"}), tool_use(2, "karar_ara", {"fail": True})],
             "tool_use"),
        resp([text('```json\n{"choice": "B"}\n```')], "end_turn"),
    ])
    prov = FakeProvider(config=SystemConfig(id="fake", label="Fake", kind="none"))
    rec = await run_task(client, prov, TASK, AgentSettings(model="test-model", today="13.10.2026"))
    assert rec.error is None and rec.parsed["choice"] == "B"
    assert rec.n_tool_calls == 2 and [c.ok for c in rec.tool_calls] == [True, False]
    second_call_msgs = client.messages.calls[1]["messages"]
    results = second_call_msgs[-1]["content"]
    assert results[0]["tool_use_id"] == "tu1" and results[1]["is_error"] is True
    assert client.messages.calls[0]["tools"][0]["name"] == "karar_ara"
    assert "13.10.2026" in client.messages.calls[0]["system"]


async def test_budget_exhaustion_forces_final_answer():
    client = FakeClient([
        resp([tool_use(1, "karar_ara", {"q": 1}), tool_use(2, "karar_ara", {"q": 2}),
              tool_use(3, "karar_ara", {"q": 3})], "tool_use"),
        resp([text('```json\n{"choice": "A"}\n```')], "end_turn"),
    ])
    prov = FakeProvider(config=SystemConfig(id="fake", label="Fake", kind="none"))
    rec = await run_task(client, prov, TASK, AgentSettings(model="test-model", max_tool_calls=2, today="x"))
    assert rec.n_tool_calls == 2 and len(prov.calls) == 2
    last_user = client.messages.calls[1]["messages"][-1]["content"]
    assert last_user[2]["is_error"] is True  # bütçe dışı kalan çağrı çalıştırılmadı
    assert client.messages.calls[1]["tool_choice"] == {"type": "none"}
    assert rec.parsed["choice"] == "A"


async def test_pause_turn_continues_and_refusal_recorded():
    client = FakeClient([resp([text("...")], "pause_turn"), resp([text("Cevap: E")], "end_turn")])
    prov = FakeProvider(config=SystemConfig(id="fake", label="Fake", kind="none"))
    rec = await run_task(client, prov, TASK, AgentSettings(model="test-model", today="x"))
    assert rec.n_turns == 2 and rec.parsed["choice"] == "E"
    assert client.messages.calls[1]["messages"][-1]["role"] == "assistant"

    refused = NS(content=[], stop_reason="refusal", model="m", stop_details=NS(category="cyber"),
                 usage=NS(input_tokens=1, output_tokens=0, cache_read_input_tokens=0, server_tool_use=None))
    rec2 = await run_task(FakeClient([refused]), prov, TASK, AgentSettings(model="test-model", today="x"))
    assert rec2.error and "reddetti" in rec2.error


async def test_turn_limit_requests_answer_without_tools():
    loop_resp = [resp([tool_use(i, "karar_ara", {"q": i})], "tool_use") for i in range(2)]
    client = FakeClient(loop_resp + [resp([text('{"choice": "C"}')], "end_turn")])
    prov = FakeProvider(config=SystemConfig(id="fake", label="Fake", kind="none"))
    rec = await run_task(client, prov, TASK, AgentSettings(model="test-model", max_turns=3, today="x"))
    assert rec.parsed["choice"] == "C" and rec.error is None
    assert client.messages.calls[2]["tool_choice"] == {"type": "none"}
