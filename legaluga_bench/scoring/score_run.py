"""Bir koşunun bütün kayıtlarını puanlar ve results/<koşu>/scores.jsonl dosyasına yazar."""

from __future__ import annotations

import functools
import logging
from pathlib import Path
from typing import Any

from ..io import RESULTS_DIR, read_models, write_jsonl
from ..schema import RunRecord, ScoreRecord, Task
from .tracks import SYNC_SCORERS, CitationVerifier, score_research

log = logging.getLogger("lbench.score")


def latest_runs(run_name: str) -> list[RunRecord]:
    """Sistem/görev başına en son kaydı döndürür (yeniden denemelerde eski hatalı kayıtlar atlanır)."""
    runs_dir = RESULTS_DIR / run_name / "runs"
    latest: dict[tuple[str, str], RunRecord] = {}
    for path in sorted(runs_dir.glob("*.jsonl")):
        for rec in read_models(path, RunRecord):
            latest[(rec.system_id, rec.task_id)] = rec
    return list(latest.values())


async def score_run(
    run_name: str,
    tasks: dict[str, Task],
    judge_client: Any = None,
    judge_model: str | None = None,
    verifier: CitationVerifier | None = None,
) -> Path:
    from .judge import judge_answer

    scores: list[ScoreRecord] = []
    missing = 0
    for rec in latest_runs(run_name):
        task = tasks.get(rec.task_id)
        if task is None:
            missing += 1
            continue
        if task.track in SYNC_SCORERS:
            scores.append(SYNC_SCORERS[task.track](task, rec))
        elif task.track == "research":
            if judge_client is None:
                log.warning("research görevi %s hakemsiz atlandı", task.id)
                continue
            judge_fn = functools.partial(judge_answer, judge_client, model=judge_model)
            scores.append(await score_research(task, rec, judge_fn, verifier))
    if missing:
        log.warning("%d kayıt için görev tanımı bulunamadı (görev seti değişmiş olabilir)", missing)
    out = RESULTS_DIR / run_name / "scores.jsonl"
    write_jsonl(out, sorted(scores, key=lambda s: (s.system_id, s.task_id)))
    return out
