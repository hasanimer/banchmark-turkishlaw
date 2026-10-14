"""Atıf denetimi (citation_check) görevlerini resmî örneklemden üretir.

Her görev bir "dilekçe taslağında geçen" 5 karar atfıdır. Atıf türleri:
  var           gerçek künye, doğru tarih (Bedesten örnekleminden)
  tarih_hatali  gerçek karar, tarih kaydırılmış (doğru tarih altın veride)
  yok           karar numarası değiştirilmiş; Bedesten'in BÜTÜN dairelerinde bulunmadığı doğrulanır
  yok           hiç var olmamış daire (Yargıtay 24-27. Hukuk Dairesi, Danıştay 18-19. Daire)
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from datetime import date, timedelta
from typing import Any

from ..io import PUBLIC_TASKS_DIR, read_jsonl, write_jsonl
from ..schema import Task
from ..scoring.citations import case_key
from .bedesten import BedestenClient, ITEM_TYPES, number_phrase
from .gold_cases import GOLD_DIR

log = logging.getLogger("lbench.gold")

ITEMS_PER_TASK = 5
PLAN = (["var"] * 8) + (["tarih_hatali"] * 4) + (["yok_numara"] * 5) + (["yok_daire"] * 3)

PROMPT_HEAD = (
    "Bir meslektaşınızın hazırladığı dilekçe taslağında aşağıdaki karar atıfları geçmektedir. "
    "Dilekçe mahkemeye verilmeden önce her atfı denetleyiniz."
)


def _fmt_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}.{m}.{y}"


def render_citation(c: dict[str, Any], style: int) -> str:
    court, chamber, esas, karar = c["court"], c["chamber"], c["esas"], c["karar"]
    when = _fmt_date(c["date"]) if c.get("date") else None
    if court == "Bölge Adliye Mahkemesi":
        head = chamber  # "Ankara Bölge Adliye Mahkemesi 25. Hukuk Dairesi"
    else:
        head = f"{court} {chamber}"
    if style == 0:
        return f"{head}, E. {esas}, K. {karar}" + (f", T. {when}" if when else "")
    if style == 1:
        return f"{head}'nin {when + ' tarihli, ' if when else ''}{esas} E., {karar} K. sayılı kararı"
    return f"{head} {esas} Esas, {karar} Karar" + (f" ({when})" if when else "")


async def _number_absent(client: BedestenClient, c: dict[str, Any]) -> bool:
    """Değiştirilmiş künyenin Bedesten'de hiçbir dairede bulunmadığını doğrular."""
    key = case_key(c)
    item_type = ITEM_TYPES.get(key.court or "")
    phrase = number_phrase(key.esas, key.karar)
    if not item_type or not phrase:
        return False
    res = await client.search(phrase, item_type=item_type)
    return res["total"] == 0


def _shift_date(iso: str, rng: random.Random) -> str:
    d = date.fromisoformat(iso)
    delta = rng.choice([-1, 1]) * rng.randint(3, 75)
    return (d + timedelta(days=delta)).isoformat()


async def build_citation_tasks(seed: int = 7, n_tasks: int = 20) -> list[Task]:
    rows = list(read_jsonl(GOLD_DIR / "decisions_sample.jsonl"))
    pool = [r for r in rows if int(r["text_sha256"][:2], 16) % 2 == 1]  # karar bulmadan ayrık yarı
    rng = random.Random(seed)
    rng.shuffle(pool)
    client = BedestenClient()
    items: list[dict[str, Any]] = []
    try:
        for i, r in enumerate(pool):
            if len(items) >= n_tasks * ITEMS_PER_TASK:
                break
            kind = PLAN[i % len(PLAN)]
            base = {k: r[k] for k in ("court", "chamber", "esas", "karar", "date")}
            if kind == "var":
                items.append({"shown": base, "verdict": "var", "document_id": r["document_id"]})
            elif kind == "tarih_hatali":
                shown = {**base, "date": _shift_date(r["date"], rng)}
                items.append({"shown": shown, "verdict": "tarih_hatali", "correct_date": _fmt_date(r["date"]),
                              "document_id": r["document_id"]})
            elif kind == "yok_numara":
                year, seq = r["karar"].split("/")
                for _ in range(5):
                    new = max(1, int(seq) + rng.choice([-1, 1]) * rng.randint(7, 900))
                    shown = {**base, "karar": f"{year}/{new}"}
                    if await _number_absent(client, shown):
                        items.append({"shown": shown, "verdict": "yok", "fabrication": "karar_numarasi"})
                        break
            else:  # yok_daire
                if r["court"] == "Yargıtay":
                    shown = {**base, "chamber": f"{rng.randint(24, 27)}. Hukuk Dairesi"}
                elif r["court"] == "Danıştay":
                    shown = {**base, "chamber": f"{rng.choice([18, 19])}. Daire"}
                else:
                    continue
                items.append({"shown": shown, "verdict": "yok", "fabrication": "olmayan_daire"})
    finally:
        await client.aclose()

    rng.shuffle(items)
    tasks: list[Task] = []
    for t in range(len(items) // ITEMS_PER_TASK):
        group = items[t * ITEMS_PER_TASK : (t + 1) * ITEMS_PER_TASK]
        lines = [f"{j}. {render_citation(it['shown'], rng.randint(0, 2))}" for j, it in enumerate(group, 1)]
        tasks.append(Task(
            id=f"cite-{t + 1:03d}",
            track="citation_check",
            split="dev" if t < 3 else "test",
            prompt=PROMPT_HEAD + "\n\n" + "\n".join(lines),
            gold={"items": [{k: v for k, v in it.items() if k != "shown"} for it in group]},
            meta={"source": "Bedesten örneklemi + doğrulanmış mutasyonlar", "shown": [it["shown"] for it in group]},
        ))
    return tasks


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    tasks = asyncio.run(build_citation_tasks())
    n = write_jsonl(PUBLIC_TASKS_DIR / "citation_check.jsonl", tasks)
    print(json.dumps({"n_tasks": n}, ensure_ascii=False))


if __name__ == "__main__":
    main()
