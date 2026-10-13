"""Karar bulma (case_lookup) görevlerinin hazırlanması.

1. `pool`: Bedesten örnekleminin karar bulmaya ayrılan yarısından (atıf denetimiyle ayrık)
   ipucu düzeyleri atanmış havuz üretir (data/private/pilot/case_lookup_pool.jsonl).
2. Anlatımlar resmî tam metinden ayrı bir adımda yazılır ve bağımsız olarak denetlenir.
3. `assemble`: denetlenmiş anlatımlarla altın künyeyi birleştirip data/tasks/case_lookup.jsonl üretir.
"""

from __future__ import annotations

import json
import random
import re
import sys

from ..io import PRIVATE_DIR, PUBLIC_TASKS_DIR, read_jsonl, write_jsonl
from ..schema import Task
from .gold_cases import GOLD_DIR

POOL = PRIVATE_DIR / "pilot" / "case_lookup_pool.jsonl"
DRAFTS = GOLD_DIR / "drafts"
PROMPT_HEAD = "Aşağıda anlatılan mahkeme kararını bulunuz ve künyesini veriniz."


def make_pool(seed: int = 11) -> int:
    rows = [r for r in read_jsonl(GOLD_DIR / "decisions_sample.jsonl") if int(r["text_sha256"][:2], 16) % 2 == 0]
    rng = random.Random(seed)
    for r in rows:
        r["hint_level"] = rng.choice(["L1", "L2"])
    return write_jsonl(POOL, rows)


def _leaks(description: str, gold: dict) -> list[str]:
    """Anlatımda künye numarası ya da karar tarihi sızıntısı var mı (mekanik son denetim)."""
    leaks = []
    for field in ("esas", "karar"):
        num = gold.get(field) or ""
        if num and re.search(rf"(?<!\d){re.escape(num)}(?!\d)", description):
            leaks.append(field)
        y, _, n = num.partition("/")
        if n and re.search(rf"(?<!\d){y}\s*/\s*{n}(?!\d)", description):
            leaks.append(field)
    if gold.get("date"):
        y, m, d = gold["date"].split("-")
        if re.search(rf"{int(d)}[./]0?{int(m)}[./]{y}", description):
            leaks.append("date")
    return sorted(set(leaks))


def assemble() -> dict:
    pool = {r["document_id"]: r for r in read_jsonl(POOL)}
    tasks, skipped, leaked = [], 0, []
    for path in sorted(DRAFTS.glob("case_lookup_*.checked.jsonl")):
        for d in read_jsonl(path):
            g = pool.get(str(d.get("document_id")))
            if g is None or d.get("skip") or d.get("review") == "skipped" or not d.get("description"):
                skipped += 1
                continue
            gold = {k: g[k] for k in ("court", "chamber", "esas", "karar", "date", "document_id")}
            leak = _leaks(d["description"], gold)
            if leak:
                leaked.append({"document_id": g["document_id"], "fields": leak})
                continue
            tasks.append({"gold": gold, "description": d["description"], "pool": g,
                          "distinctiveness": d.get("distinctiveness")})
    tasks.sort(key=lambda t: t["pool"]["document_id"])
    out = []
    for i, t in enumerate(tasks, 1):
        tid = f"case-{i:03d}"
        out.append(Task(
            id=tid, track="case_lookup", split="dev" if i % 7 == 0 else "test",
            prompt=f"{PROMPT_HEAD}\n\n{t['description'].strip()}",
            gold=t["gold"],
            meta={"stratum": t["pool"]["stratum"], "hint_level": t["pool"]["hint_level"],
                  "distinctiveness": t["distinctiveness"], "source_url": t["pool"]["source_url"],
                  "source": "Bedesten tohumlu örneklem; anlatım resmî tam metinden"},
        ))
    write_jsonl(PUBLIC_TASKS_DIR / "case_lookup.jsonl", out)
    return {"n_tasks": len(out), "skipped": skipped, "leaked": leaked}


if __name__ == "__main__":
    if sys.argv[1:] == ["pool"]:
        print(json.dumps({"n_pool": make_pool()}))
    elif sys.argv[1:] == ["assemble"]:
        print(json.dumps(assemble(), ensure_ascii=False))
    else:
        raise SystemExit("kullanım: python -m legaluga_bench.official.gold_case_lookup pool|assemble")
