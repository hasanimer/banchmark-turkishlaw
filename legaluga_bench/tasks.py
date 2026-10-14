"""Görev setini yükleme ve seçme (track, split, örnekleme)."""

from __future__ import annotations

import random
from collections.abc import Iterable
from pathlib import Path

from .io import PRIVATE_TASKS_DIR, PUBLIC_TASKS_DIR, read_models
from .schema import Task


def task_files(dirs: Iterable[Path] = (PUBLIC_TASKS_DIR, PRIVATE_TASKS_DIR)) -> list[Path]:
    files: list[Path] = []
    for d in dirs:
        if d.exists():
            files.extend(sorted(d.glob("*.jsonl")))
    return files


def load_tasks(
    tracks: Iterable[str] | None = None,
    split: str | None = None,
    limit_per_track: int | None = None,
    seed: int = 2026,
    meta_filters: dict[str, str] | None = None,
    files: Iterable[Path] | None = None,
) -> list[Task]:
    wanted = set(tracks) if tracks else None
    seen: set[str] = set()
    tasks: list[Task] = []
    for path in files or task_files():
        for t in read_models(path, Task):
            if t.id in seen:
                raise ValueError(f"Yinelenen görev kimliği: {t.id} ({path})")
            seen.add(t.id)
            if wanted and t.track not in wanted:
                continue
            if split and t.split != split:
                continue
            if meta_filters and any(str(t.meta.get(k)) != v for k, v in meta_filters.items()):
                continue
            tasks.append(t)
    if limit_per_track:
        rng = random.Random(seed)
        by_track: dict[str, list[Task]] = {}
        for t in tasks:
            by_track.setdefault(t.track, []).append(t)
        tasks = []
        for track in sorted(by_track):
            items = by_track[track]
            tasks.extend(sorted(rng.sample(items, min(limit_per_track, len(items))), key=lambda t: t.id))
    return tasks
