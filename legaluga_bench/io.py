"""Dizinler ve JSONL okuma/yazma yardımcıları."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PUBLIC_TASKS_DIR = DATA_DIR / "tasks"
# Telifli içerik (ÖSYM soruları, yayınevi denemeleri) public repoya girmez.
PRIVATE_DIR = DATA_DIR / "private"
PRIVATE_TASKS_DIR = PRIVATE_DIR / "tasks"
CONFIG_DIR = ROOT / "configs"
RESULTS_DIR = Path(os.environ.get("LBENCH_RESULTS_DIR", ROOT / "results"))

M = TypeVar("M", bound=BaseModel)


def read_jsonl(path: Path) -> Iterator[dict]:
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{lineno}: geçersiz JSON: {e}") from e


def read_models(path: Path, model: type[M]) -> list[M]:
    return [model.model_validate(row) for row in read_jsonl(path)]


def write_jsonl(path: Path, rows: Iterable[BaseModel | dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            data = row.model_dump(mode="json") if isinstance(row, BaseModel) else row
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            n += 1
    return n


def append_jsonl(path: Path, row: BaseModel | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = row.model_dump(mode="json") if isinstance(row, BaseModel) else row
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
