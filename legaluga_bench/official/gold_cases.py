"""Bedesten'den katmanlı, tohumlu karar örneklemi (karar bulma ve atıf denetimi altın verisi için).

Hiçbir test edilen sistem kullanılmaz: kararlar doğrudan resmî Bedesten servisinden
rastgele seçilir, tam metinleri indirilir ve yerelde önbelleğe alınır. Çıktı:
  data/gold/decisions_sample.jsonl   (künye + documentId + metin özeti; public)
  data/private/cache/decisions/<documentId>.txt (tam metin; yerel)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from ..io import DATA_DIR, PRIVATE_DIR, write_jsonl
from ..scoring.citations import case_key, norm_date
from .bedesten import BedestenClient

log = logging.getLogger("lbench.gold")

GOLD_DIR = DATA_DIR / "gold"
TEXT_CACHE = PRIVATE_DIR / "cache" / "decisions"


@dataclass(frozen=True)
class Stratum:
    name: str
    item_type: str
    chambers: tuple[str | None, ...]
    years: tuple[int, int]
    n: int
    phrase: str = "dava"


def _hukuk(n: int) -> tuple[str, ...]:
    return tuple(f"{i}. Hukuk Dairesi" for i in range(1, n + 1))


def _ceza(n: int) -> tuple[str, ...]:
    return tuple(f"{i}. Ceza Dairesi" for i in range(1, n + 1))


STRATA: tuple[Stratum, ...] = (
    Stratum("yargitay_hukuk", "YARGITAYKARARI", _hukuk(12), (2017, 2026), 36),
    Stratum("yargitay_hgk", "YARGITAYKARARI", ("Hukuk Genel Kurulu",), (2014, 2026), 10),
    Stratum("yargitay_ceza", "YARGITAYKARARI", _ceza(12), (2017, 2026), 24, phrase="suç"),
    Stratum("yargitay_cgk", "YARGITAYKARARI", ("Ceza Genel Kurulu",), (2014, 2026), 6, phrase="suç"),
    Stratum("danistay_daire", "DANISTAYKARAR", tuple(f"{i}. Daire" for i in range(2, 14)), (2016, 2026), 20),
    Stratum("danistay_kurul", "DANISTAYKARAR", ("İdare Dava Daireleri Kurulu", "Vergi Dava Daireleri Kurulu"),
            (2014, 2026), 8),
    Stratum("bam_hukuk", "ISTINAFHUKUK", (None,), (2019, 2026), 20),
)


def _iso(d: date, end: bool = False) -> str:
    return f"{d.isoformat()}T{'23:59:59.999' if end else '00:00:00.000'}Z"


def _cache_text(doc_id: str, text: str) -> str:
    TEXT_CACHE.mkdir(parents=True, exist_ok=True)
    (TEXT_CACHE / f"{doc_id}.txt").write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode()).hexdigest()


async def sample_decisions(
    seed: int = 20261013,
    min_chars: int = 2500,
    max_chars: int = 60_000,
    client: BedestenClient | None = None,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    own = client is None
    client = client or BedestenClient()
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    try:
        for st in STRATA:
            got, attempts = 0, 0
            while got < st.n and attempts < st.n * 6:
                attempts += 1
                chamber = rng.choice(st.chambers)
                year = rng.randint(*st.years)
                start = date(year, 1, 1) + timedelta(days=rng.randint(0, 358))
                end = start + timedelta(days=6)
                res = await client.search(st.phrase, item_type=st.item_type, birim=chamber,
                                          start=_iso(start), end=_iso(end, True), size=10,
                                          sort_direction=rng.choice(["asc", "desc"]))
                items = [e for e in res["items"] if e.get("documentId") not in seen and e.get("esasNo") and e.get("kararNo")]
                if not items:
                    continue
                e = rng.choice(items)
                text = await client.get_document_text(e["documentId"])
                if not text or not (min_chars <= len(text) <= max_chars):
                    continue
                seen.add(e["documentId"])
                court = {"YARGITAYKARARI": "Yargıtay", "DANISTAYKARAR": "Danıştay",
                         "ISTINAFHUKUK": "Bölge Adliye Mahkemesi"}[st.item_type]
                rec = {
                    "document_id": e["documentId"],
                    "stratum": st.name,
                    "court": court,
                    "chamber": e.get("birimAdi"),
                    "esas": e.get("esasNo"),
                    "karar": e.get("kararNo"),
                    "date": norm_date(e.get("kararTarihiStr")),
                    "item_type": st.item_type,
                    "source_url": f"https://mevzuat.adalet.gov.tr/ictihat/{e['documentId']}",
                    "text_chars": len(text),
                    "text_sha256": _cache_text(e["documentId"], text),
                }
                rec["key"] = case_key(rec).short()
                out.append(rec)
                got += 1
                log.info("%s %d/%d %s", st.name, got, st.n, rec["key"])
            if got < st.n:
                log.warning("%s: yalnız %d/%d karar bulundu", st.name, got, st.n)
    finally:
        if own:
            await client.aclose()
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    rows = asyncio.run(sample_decisions())
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    n = write_jsonl(GOLD_DIR / "decisions_sample.jsonl", rows)
    print(json.dumps({"n": n, "path": str(GOLD_DIR / "decisions_sample.jsonl")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
