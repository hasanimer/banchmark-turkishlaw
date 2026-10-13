"""Sabit model + değişken araç kümesiyle çalışan ajan döngüsü (Anthropic Messages API).

Döngü bilerek elle yazılmıştır: her araç çağrısının süresini ve hatasını
kaydetmek, bütün sistemlere aynı araç bütçesini uygulamak ve `pause_turn`
durumunu (sunucu tarafı web araması) açıkça ele almak gerekir.
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import anthropic

from ..schema import RunRecord, Task, ToolCallLog
from ..scoring.citations import numbers_in
from ..systems.base import ToolProvider
from .parse import parse_final_json
from .prompts import render_system_prompt, render_task_prompt

# Ajan modeli koda gömülmez; LBENCH_AGENT_MODEL ortam değişkeni ya da --model bayrağıyla verilir.
AGENT_MODEL_ENV = "LBENCH_AGENT_MODEL"

BUDGET_EXHAUSTED_MSG = (
    "Araç kullanım bütçen doldu. Artık araç çağırma; elindeki bilgilerle son cevabını "
    "istenen JSON bloğuyla ver."
)


@dataclass
class AgentSettings:
    model: str = field(default_factory=lambda: os.environ.get(AGENT_MODEL_ENV, ""))
    effort: str = "high"
    max_tokens: int = 16_000
    max_turns: int = 16
    max_tool_calls: int = 20
    task_timeout_s: float = 900.0
    today: str = ""
    # MCP sunucusunun initialize talimatlarını sistem istemine ekle (Claude gibi istemcilerin davranışı).
    use_server_instructions: bool = True

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError(f"Ajan modeli belirtilmedi: {AGENT_MODEL_ENV} ortam değişkenini ya da --model bayrağını kullanın")
        if not self.today:
            self.today = datetime.now(timezone.utc).strftime("%d.%m.%Y")


def _usage_add(rec: RunRecord, usage: Any) -> None:
    if usage is None:
        return
    rec.input_tokens += getattr(usage, "input_tokens", 0) or 0
    rec.output_tokens += getattr(usage, "output_tokens", 0) or 0
    rec.cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0) or 0
    stu = getattr(usage, "server_tool_use", None)
    if stu is not None:
        rec.server_tool_uses += getattr(stu, "web_search_requests", 0) or 0


def _text_of(content: list[Any]) -> str:
    return "\n".join(b.text for b in content if getattr(b, "type", None) == "text").strip()


async def _run_tool(provider: ToolProvider, block: Any) -> tuple[dict[str, Any], ToolCallLog]:
    args = block.input if isinstance(block.input, dict) else {}
    started = time.monotonic()
    result = await provider.call_tool(block.name, args)
    latency = time.monotonic() - started
    log = ToolCallLog(
        name=block.name,
        arguments=args,
        ok=not result.is_error,
        error=result.text[:500] if result.is_error else None,
        latency_s=round(latency, 3),
        result_chars=len(result.text),
        result_excerpt=result.text[:300],
        numbers_seen=sorted(set(numbers_in(result.text))),
    )
    tool_result: dict[str, Any] = {
        "type": "tool_result",
        "tool_use_id": block.id,
        "content": result.text or "(boş sonuç)",
    }
    if result.is_error:
        tool_result["is_error"] = True
    return tool_result, log


async def run_task(
    client: anthropic.AsyncAnthropic,
    provider: ToolProvider,
    task: Task,
    settings: AgentSettings,
) -> RunRecord:
    rec = RunRecord(
        run_id=uuid.uuid4().hex,
        task_id=task.id,
        track=task.track,
        system_id=provider.system_id,
        model=settings.model,
        started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    started = time.monotonic()
    try:
        await asyncio.wait_for(_loop(client, provider, task, settings, rec), timeout=settings.task_timeout_s)
    except TimeoutError:
        rec.error = f"zaman aşımı ({settings.task_timeout_s:.0f} sn)"
    except anthropic.APIStatusError as e:
        rec.error = f"API hatası {e.status_code}: {e.message}"
    except anthropic.APIConnectionError as e:
        rec.error = f"bağlantı hatası: {e}"
    rec.latency_s = round(time.monotonic() - started, 3)
    rec.parsed = parse_final_json(rec.final_text, task.track)
    return rec


async def _loop(
    client: anthropic.AsyncAnthropic,
    provider: ToolProvider,
    task: Task,
    settings: AgentSettings,
    rec: RunRecord,
) -> None:
    client_tools = [t.to_anthropic() for t in await provider.list_tools()]
    tools = client_tools + provider.server_tools()
    messages: list[dict[str, Any]] = [{"role": "user", "content": render_task_prompt(task)}]
    params: dict[str, Any] = {
        "model": settings.model,
        "max_tokens": settings.max_tokens,
        "system": render_system_prompt(
            settings.today, provider.instructions if settings.use_server_instructions else ""
        ),
        "output_config": {"effort": settings.effort},
        "cache_control": {"type": "ephemeral"},
    }
    if tools:
        params["tools"] = tools

    budget_spent = False
    for turn in range(settings.max_turns):
        rec.n_turns += 1
        last_turn = turn == settings.max_turns - 1
        if last_turn and tools and not budget_spent and isinstance(messages[-1]["content"], list):
            # Son tur: cevapsız kalmamak için araçları kapatıp son cevabı iste.
            messages[-1]["content"].append({"type": "text", "text": BUDGET_EXHAUSTED_MSG})
            budget_spent = True
        extra: dict[str, Any] = {}
        if budget_spent and tools:
            extra["tool_choice"] = {"type": "none"}
        response = await client.messages.create(messages=messages, **params, **extra)
        _usage_add(rec, response.usage)
        rec.served_model = getattr(response, "model", None)
        rec.stop_reason = response.stop_reason
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "pause_turn":
            # Sunucu tarafı araç (web araması) turu yarıda bıraktı; aynı içerikle devam et.
            continue
        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            rec.error = f"model reddetti ({getattr(details, 'category', None)})"
            rec.final_text = _text_of(response.content)
            return
        tool_blocks = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
        if response.stop_reason != "tool_use" or not tool_blocks:
            rec.final_text = _text_of(response.content)
            if response.stop_reason == "max_tokens":
                rec.error = "max_tokens sınırına ulaşıldı"
            return

        remaining = settings.max_tool_calls - rec.n_tool_calls
        runnable, skipped = tool_blocks[: max(0, remaining)], tool_blocks[max(0, remaining) :]
        outcomes = await asyncio.gather(*(_run_tool(provider, b) for b in runnable))
        results: list[dict[str, Any]] = []
        for tool_result, log in outcomes:
            results.append(tool_result)
            rec.tool_calls.append(log)
        rec.n_tool_calls += len(runnable)
        for b in skipped:
            results.append(
                {"type": "tool_result", "tool_use_id": b.id, "content": BUDGET_EXHAUSTED_MSG, "is_error": True}
            )
        if rec.n_tool_calls >= settings.max_tool_calls:
            budget_spent = True
            results.append({"type": "text", "text": BUDGET_EXHAUSTED_MSG})
        messages.append({"role": "user", "content": results})

    rec.error = rec.error or f"tur sınırı ({settings.max_turns}) aşıldı"
