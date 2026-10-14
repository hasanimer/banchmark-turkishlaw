"""Adalet Bakanlığı Bedesten servisi için bağımsız istemci (altın veri ve atıf doğrulama).

Bu istemci hiçbir test edilen sistemin kodunu ya da sunucusunu kullanmaz; doğrudan
resmî uç noktalara gider. Bedesten IP başına yaklaşık 30 saniyede 10 istek kabul
ettiği için istekler ~3,5 sn aralıkla sıralanır ve sonuçlar diskte önbelleğe alınır.

Önemli sınır: Bedesten her kararı yayımlamaz. "not_found", kararın Bedesten'de
bulunamadığı anlamına gelir; kararın hiç var olmadığının kesin kanıtı değildir.
"""

from __future__ import annotations

import asyncio
import base64
import fcntl
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..io import RESULTS_DIR
from ..scoring.citations import case_key, norm_number, strip_gk_prefix

BASE_URL = "https://bedesten.adalet.gov.tr"
HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "AdaletApplicationName": "UyapMevzuat",
    "Content-Type": "application/json; charset=utf-8",
    "Origin": "https://mevzuat.adalet.gov.tr",
    "Referer": "https://mevzuat.adalet.gov.tr/",
    "User-Agent": "LegalugaLawBenchmark/0.1 (+https://github.com/hasanimer/banchmark-turkishlaw)",
}

ITEM_TYPES = {"yargitay": "YARGITAYKARARI", "danistay": "DANISTAYKARAR", "bam": "ISTINAFHUKUK", "yerel": "YERELHUKUK"}

_COUNCILS = {
    "HGK": "Hukuk Genel Kurulu", "CGK": "Ceza Genel Kurulu", "BGK": "Büyük Genel Kurulu",
    "HDBK": "Hukuk Daireleri Başkanlar Kurulu", "CDBK": "Ceza Daireleri Başkanlar Kurulu",
    "IDDK": "İdare Dava Daireleri Kurulu", "VDDK": "Vergi Dava Daireleri Kurulu",
    "IBK": "İçtihatları Birleştirme Kurulu",
}


def birim_adi(court: str | None, chamber: str | None) -> str | None:
    """Kanonik daire kodunu (H3, C12, D5, HGK...) Bedesten'in birimAdi değerine çevirir."""
    if not chamber:
        return None
    if chamber in _COUNCILS:
        return _COUNCILS[chamber]
    kind, num = chamber[0], chamber[1:]
    if not num.isdigit():
        return None
    if kind == "H":
        return f"{int(num)}. Hukuk Dairesi"
    if kind == "C":
        return f"{int(num)}. Ceza Dairesi"
    if kind == "D" and court == "danistay":
        return f"{int(num)}. Daire"
    return None


def number_phrase(esas: str | None, karar: str | None) -> str | None:
    """'2010/119', '2010/478' -> '+"2010 119" +"2010 478"' (Bedesten eğik çizgiyi kabul etmez)."""
    parts = []
    for num in (esas, karar):
        if num:
            base = num.split("-")[-1] if "-" in num else num.split("/")[-1]
            year = num.split("/")[0]
            parts.append(f'+"{year} {int(base)}"')
    return " ".join(parts) or None


class _RateLimiter:
    """Süreçler arası ortak hız sınırı: aynı makinedeki bütün istemciler tek bir sıraya girer.

    Bedesten sınırı IP başınadır; birden çok süreç (ör. paralel altın veri ajanları) aynı
    dosya kilidini paylaşarak istekleri `interval_s` aralıkla gönderir.
    """

    def __init__(self, interval_s: float, state_path: Path) -> None:
        self.interval = interval_s
        self._state = state_path
        self._state.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    def _update(self, fn: Any) -> float:
        with open(self._state.with_suffix(".lock"), "a+") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            try:
                try:
                    nxt = float(self._state.read_text() or 0)
                except (FileNotFoundError, ValueError):
                    nxt = 0.0
                new_next, wait_s = fn(nxt, time.time())
                if new_next != nxt:
                    self._state.write_text(str(new_next))
                return wait_s
            finally:
                fcntl.flock(lk, fcntl.LOCK_UN)

    async def wait(self) -> None:
        async with self._lock:
            while True:
                wait_s = self._update(lambda nxt, now: (now + self.interval, 0.0) if now >= nxt else (nxt, nxt - now))
                if wait_s <= 0:
                    return
                await asyncio.sleep(min(wait_s, 5.0))

    def penalize(self, seconds: float) -> None:
        self._update(lambda nxt, now: (max(nxt, now + seconds), 0.0))


class BedestenClient:
    def __init__(self, interval_s: float = 3.5, cache_dir: Path | None = None, timeout_s: float = 60.0) -> None:
        self._cache_dir = cache_dir or (RESULTS_DIR / ".cache" / "bedesten")
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._limiter = _RateLimiter(interval_s, self._cache_dir.parent / "bedesten_rate.next")
        self._http = httpx.AsyncClient(base_url=BASE_URL, headers=HEADERS, timeout=timeout_s)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _cache_get(self, key: str) -> dict[str, Any] | None:
        path = self._cache_dir / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def _cache_put(self, key: str, data: dict[str, Any]) -> None:
        path = self._cache_dir / f"{key}.json"
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)

    async def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        key = hashlib.sha256((endpoint + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
        cached = self._cache_get(key)
        if cached is not None:
            return cached
        for attempt in range(6):
            await self._limiter.wait()
            try:
                r = await self._http.post(endpoint, json=payload)
            except httpx.TransportError:
                self._limiter.penalize(5.0 * (attempt + 1))
                continue
            if r.status_code == 429:
                retry = float(r.headers.get("Retry-After") or 30)
                self._limiter.penalize(min(max(retry, 1.0), 60.0) + 0.5)
                continue
            if r.status_code >= 500 and attempt < 5:
                self._limiter.penalize(5.0 * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            self._cache_put(key, data)
            return data
        raise RuntimeError(f"Bedesten {endpoint}: tekrar denemeler tükendi")

    async def search(
        self,
        phrase: str,
        item_type: str = "YARGITAYKARARI",
        birim: str | None = None,
        start: str | None = None,
        end: str | None = None,
        page: int = 1,
        size: int = 10,
        sort_direction: str = "desc",
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "pageSize": size, "pageNumber": page, "itemTypeList": [item_type], "phrase": phrase,
            "sortFields": ["KARAR_TARIHI"], "sortDirection": sort_direction,
        }
        if birim:
            data["birimAdi"] = birim
        if start:
            data["kararTarihiStart"] = start
        if end:
            data["kararTarihiEnd"] = end
        res = await self._post("/emsal-karar/searchDocuments",
                               {"data": data, "applicationName": "UyapMevzuat", "paging": True})
        d = res.get("data") or {}
        return {"total": d.get("total") or 0, "items": d.get("emsalKararList") or []}

    async def find_case(self, citation: dict[str, Any]) -> list[dict[str, Any]] | None:
        """Künyeye birebir uyan Bedesten kayıtlarını döndürür; aranamıyorsa None."""
        key = case_key(citation)
        item_type = ITEM_TYPES.get(key.court or "")
        phrase = number_phrase(key.esas, key.karar)
        if item_type is None or phrase is None or not (key.esas and key.karar):
            return None
        birim = birim_adi(key.court, key.chamber)
        res = await self.search(phrase, item_type=item_type, birim=birim)
        if res["total"] == 0 and birim:
            # Daire yanlış yazılmış olabilir: bütün dairelerde ara; çağıran birimAdi'yi karşılaştırır.
            res = await self.search(phrase, item_type=item_type)
        want_esas = strip_gk_prefix(key.esas)
        return [
            e for e in res["items"]
            if strip_gk_prefix(norm_number(e.get("esasNo"))) == want_esas and norm_number(e.get("kararNo")) == key.karar
        ]

    # --- mevzuat --------------------------------------------------------------------

    async def find_law(self, law_no: str, tur: str = "KANUN") -> dict[str, Any] | None:
        """Numarasıyla kanun kaydı (mevzuatId, ad, mevzuat.gov.tr bağlantısı). Birden çok tertip varsa 5. tertip öne alınır."""
        res = await self._post("/mevzuat/searchDocuments", {
            "data": {"pageSize": 10, "pageNumber": 1, "mevzuatTurList": [tur], "mevzuatNo": str(law_no),
                     "sortFields": ["RESMI_GAZETE_TARIHI"], "sortDirection": "desc"},
            "applicationName": "UyapMevzuat", "paging": True,
        })
        items = [m for m in ((res.get("data") or {}).get("mevzuatList") or []) if str(m.get("mevzuatNo")) == str(law_no)]
        if not items:
            return None
        items.sort(key=lambda m: 0 if m.get("mevzuatTertip") == 5 else 1)
        return items[0]

    async def article_index(self, mevzuat_id: str) -> dict[str, str]:
        """Madde numarası -> maddeId (yalnız numaralı maddeler)."""
        res = await self._post("/mevzuat/mevzuatMaddeTree", {"data": {"mevzuatId": str(mevzuat_id)},
                                                             "applicationName": "UyapMevzuat"})
        out: dict[str, str] = {}
        stack = [res.get("data") or {}]
        while stack:
            node = stack.pop()
            if node.get("maddeNo") is not None and node.get("maddeId"):
                out.setdefault(str(node["maddeNo"]), str(node["maddeId"]))
            stack.extend(node.get("children") or [])
        return out

    async def article_text(self, law_no: str, article: str, tur: str = "KANUN") -> dict[str, Any] | None:
        law = await self.find_law(law_no, tur)
        if law is None:
            return None
        idx = await self.article_index(law["mevzuatId"])
        madde_id = idx.get(str(int(str(article).split("/")[0]))) if str(article).split("/")[0].isdigit() else None
        if madde_id is None:
            return {"law": law, "article": article, "text": None}
        res = await self._post("/mevzuat/getDocumentContent", {"data": {"documentType": "MADDE", "id": madde_id},
                                                               "applicationName": "UyapMevzuat"})
        d = res.get("data") or {}
        html = base64.b64decode(d.get("content") or b"").decode("utf-8", errors="replace")
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True) if html else None
        return {"law": law, "article": article, "madde_id": madde_id, "text": text}

    # --- kararlar --------------------------------------------------------------------

    async def get_document_text(self, document_id: str) -> str | None:
        res = await self._post("/emsal-karar/getDocumentContent",
                               {"data": {"documentId": str(document_id)}, "applicationName": "UyapMevzuat"})
        d = res.get("data") or {}
        content, mime = d.get("content"), d.get("mimeType")
        if not content:
            return None
        raw = base64.b64decode(content)
        if mime == "text/html":
            return BeautifulSoup(raw.decode("utf-8", errors="replace"), "html.parser").get_text("\n", strip=True)
        return None  # PDF kararlar şimdilik metne çevrilmiyor


class BedestenVerifier:
    """CitationVerifier: karar atıflarını Bedesten'de, madde atıflarını mevzuat servisinde denetler."""

    def __init__(self, client: BedestenClient | None = None) -> None:
        self.client = client or BedestenClient()

    async def verify_case(self, citation: dict[str, Any]) -> str:
        """'exists' | 'chamber_mismatch' (numara var ama başka dairede) | 'not_found' | 'unknown'."""
        try:
            hits = await self.client.find_case(citation)
        except (httpx.HTTPError, RuntimeError):
            return "unknown"
        if hits is None:
            return "unknown"
        if not hits:
            return "not_found"
        key = case_key(citation)
        if key.chamber is None:
            return "exists"
        chambers = {case_key({"court": key.court, "chamber": h.get("birimAdi")}).chamber for h in hits}
        return "exists" if key.chamber in chambers else "chamber_mismatch"

    async def verify_statute(self, law_no: str, article: str) -> str:
        """Kanun numarası ve madde Bedesten mevzuat ağacında var mı. Geçici/ek maddeler denetlenemez."""
        base = str(article).split("/")[0]
        if not base.isdigit():
            return "unknown"
        try:
            law = await self.client.find_law(law_no)
            if law is None:
                # Bedesten dizini her kanunu içermez; kanunun bulunamaması uydurma kanıtı değildir.
                return "unknown"
            idx = await self.client.article_index(law["mevzuatId"])
        except (httpx.HTTPError, RuntimeError):
            return "unknown"
        if not idx:
            return "unknown"
        return "exists" if str(int(base)) in idx else "not_found"
