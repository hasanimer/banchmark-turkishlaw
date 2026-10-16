"""Mevzuat ve araştırma taslaklarını resmî kaynakla mekanik olarak denetleyip görev dosyasına yazar.

Taslaklar (data/gold/drafts/<track>_<alan>.jsonl) elle/ajanla resmî metinden hazırlanır; bir
doğrulama geçişi varsa onun çıktısı (<ad>.verified.jsonl) tercih edilir. Buradaki denetim
ikisinden de bağımsızdır ve yalnız Bedesten'e bakar:

- statute: her ``quote_must_contain`` parçası resmî madde metninde aynen geçmeli; her ``accept``
  düzenli ifadesi derlenmeli ve başvuru cevabıyla eşleşmeli.
- research: ``official_sources`` içindeki her madde ve karar Bedesten'de bulunmalı.

Denetimi geçemeyen görev dışarıda kalır ve nedeni raporda yazılır.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..io import DATA_DIR, PUBLIC_TASKS_DIR, read_jsonl, write_jsonl
from ..schema import Task
from ..scoring.citations import fold
from .bedesten import BedestenClient, BedestenVerifier

DRAFTS_DIR = DATA_DIR / "gold" / "drafts"


def draft_files(track: str, drafts_dir: Path = DRAFTS_DIR) -> list[Path]:
    """Her alan için doğrulanmış sürüm varsa onu, yoksa ham taslağı döndürür."""
    out = []
    for path in sorted(drafts_dir.glob(f"{track}_*.jsonl")):
        if path.name.count(".") > 1:  # .verified / .review / .checked
            continue
        verified = path.with_name(path.stem + ".verified.jsonl")
        out.append(verified if verified.exists() else path)
    return out


def _squash(s: str) -> str:
    # Resmî metin HTML'den geldiği için tırnak ve kesme işaretleri farklı kodlanabilir.
    s = fold(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s)


async def check_statute(task: dict[str, Any], client: BedestenClient) -> list[str]:
    problems: list[str] = []
    g = task.get("gold") or {}
    # accept ifadeleri alternatiftir (biri eşleşirse cevap doğru sayılır): başvuru cevabı en az
    # birine uymalı.
    accept = g.get("accept") or []
    matched = False
    for pat in accept:
        try:
            matched = matched or bool(re.search(fold(pat), fold(g.get("reference_answer") or "")))
        except re.error as e:
            problems.append(f"accept derlenemiyor: {pat} ({e})")
    if not accept:
        problems.append("accept yok")
    elif not matched:
        problems.append("başvuru cevabı hiçbir accept ifadesiyle eşleşmiyor")
    must = g.get("quote_must_contain") or []
    if must:
        art = await client.article_text(str(g.get("law_no")), str(g.get("article")))
        text = (art or {}).get("text")
        if not text:
            problems.append(f"resmî madde metni alınamadı: {g.get('law_no')} m.{g.get('article')}")
        else:
            body = _squash(text)
            problems += [f"alıntı resmî metinde yok: {s!r}" for s in must if _squash(s) not in body]
    return problems


async def check_research(task: dict[str, Any], verifier: BedestenVerifier) -> list[str]:
    problems: list[str] = []
    g = task.get("gold") or {}
    if not g.get("rubric"):
        problems.append("rubrik yok")
    for src in g.get("official_sources") or []:
        if src.get("type") == "mevzuat":
            status = await verifier.verify_statute(str(src.get("law_no")), str(src.get("article")))
            # Geçici/ek maddeler ve dizinde olmayan kanunlar 'unknown' döner; bunlar elde kontrol edilir.
            if status == "not_found":
                problems.append(f"madde bulunamadı: {src.get('law_no')} m.{src.get('article')}")
        elif src.get("type") == "karar":
            status = await verifier.verify_case(src)
            if status != "exists":
                problems.append(f"karar {status}: {src.get('chamber')} {src.get('esas')} E. {src.get('karar')} K.")
    return problems


async def assemble(track: str, out_path: Path | None = None, drafts_dir: Path = DRAFTS_DIR) -> dict[str, Any]:
    client = BedestenClient()
    verifier = BedestenVerifier(client)
    kept: list[Task] = []
    rejected: dict[str, list[str]] = {}
    try:
        for path in draft_files(track, drafts_dir):
            for row in read_jsonl(path):
                if row.get("track") != track:
                    continue
                if track == "statute":
                    problems = await check_statute(row, client)
                else:
                    problems = await check_research(row, verifier)
                if problems:
                    rejected[row["id"]] = problems
                    continue
                meta = dict(row.get("meta") or {})
                meta["draft_file"] = path.name
                kept.append(Task(id=row["id"], track=track, split=row.get("split", "test"), prompt=row["prompt"],
                                 gold=row["gold"], meta=meta))
    finally:
        await client.aclose()
    ids = [t.id for t in kept]
    if len(ids) != len(set(ids)):
        raise ValueError(f"yinelenen görev kimliği: {sorted({i for i in ids if ids.count(i) > 1})}")
    write_jsonl(out_path or (PUBLIC_TASKS_DIR / f"{track}.jsonl"), kept)
    return {"track": track, "n_tasks": len(kept), "rejected": rejected,
            "files": [p.name for p in draft_files(track, drafts_dir)]}
