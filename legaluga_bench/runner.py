"""Görevleri sistemler üzerinde koşturur; sonuçları sistem başına JSONL'e ekler (kaldığı yerden devam eder)."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import anthropic

from .agent import AgentSettings, run_task
from .io import RESULTS_DIR, append_jsonl, read_models
from .schema import RunRecord, Task
from .systems import SystemConfig, make_provider

log = logging.getLogger("lbench.runner")


def run_dir(run_name: str) -> Path:
    return RESULTS_DIR / run_name


def runs_path(run_name: str, system_id: str) -> Path:
    return run_dir(run_name) / "runs" / f"{system_id}.jsonl"


def completed_task_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {r.task_id for r in read_models(path, RunRecord) if r.error is None}


async def run_system(
    client: anthropic.AsyncAnthropic,
    cfg: SystemConfig,
    tasks: list[Task],
    settings: AgentSettings,
    run_name: str,
    concurrency: int = 4,
    all_configs: dict[str, SystemConfig] | None = None,
) -> int:
    out = runs_path(run_name, cfg.id)
    done = completed_task_ids(out)
    pending = [t for t in tasks if t.id not in done]
    if not pending:
        log.info("%s: bütün görevler zaten tamamlanmış", cfg.id)
        return 0
    sem = asyncio.Semaphore(max(1, concurrency))
    async with make_provider(cfg, all_configs) as provider:
        tools = await provider.list_tools()
        fp_dir = run_dir(run_name) / "systems"
        fp_dir.mkdir(parents=True, exist_ok=True)
        (fp_dir / f"{cfg.id}.json").write_text(
            json.dumps({**provider.fingerprint(), "instructions": provider.instructions,
                        "use_server_instructions": settings.use_server_instructions},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("%s: %d araç, %d görev", cfg.id, len(tools) + len(provider.server_tools()), len(pending))

        async def one(task: Task) -> None:
            async with sem:
                rec = await run_task(client, provider, task, settings)
                append_jsonl(out, rec)
                status = "HATA " + rec.error if rec.error else "ok"
                log.info("%s %s %s (%.1fs, %d araç)", cfg.id, task.id, status, rec.latency_s, rec.n_tool_calls)

        await asyncio.gather(*(one(t) for t in pending))
    return len(pending)


async def run_benchmark(
    configs: list[SystemConfig],
    tasks: list[Task],
    settings: AgentSettings,
    run_name: str,
    concurrency: int = 4,
    all_configs: dict[str, SystemConfig] | None = None,
) -> dict[str, int]:
    client = anthropic.AsyncAnthropic(max_retries=4)
    counts: dict[str, int] = {}
    # Sistemler sırayla koşar: aynı anda tek bir sistemin sunucusuna yük bindirilir.
    for cfg in configs:
        counts[cfg.id] = await run_system(client, cfg, tasks, settings, run_name, concurrency, all_configs)
    return counts
