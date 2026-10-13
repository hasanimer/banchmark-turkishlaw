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
import hashlib
import json
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
    def __init__(self, interval_s: float) -> None:
        self.interval = interval_s
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            if now < self._next:
                await asyncio.sleep(self._next - now)
            self._next = time.monotonic() + self.interval

    def penalize(self, seconds: float) -> None:
        self._next = max(self._next, time.monotonic() + seconds)


class BedestenClient:
    def __init__(self, interval_s: float = 3.5, cache_path: Path | None = None, timeout_s: float = 60.0) -> None:
        self._limiter = _RateLimiter(interval_s)
        self._http = httpx.AsyncClient(base_url=BASE_URL, headers=HEADERS, timeout=timeout_s)
        self._cache_path = cache_path or (RESULTS_DIR / ".cache" / "bedesten.json")
        self._cache: dict[str, Any] = {}
        if self._cache_path.exists():
            self._cache = json.loads(self._cache_path.read_text(encoding="utf-8"))

    async def aclose(self) -> None:
        self._save()
        await self._http.aclose()

    def _save(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache_path.write_text(json.dumps(self._cache, ensure_ascii=False), encoding="utf-8")

    async def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        key = hashlib.sha256((endpoint + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
        if key in self._cache:
            return self._cache[key]
        for attempt in range(4):
            await self._limiter.wait()
            r = await self._http.post(endpoint, json=payload)
            if r.status_code == 429:
                retry = float(r.headers.get("Retry-After") or 30)
                self._limiter.penalize(min(max(retry, 1.0), 60.0) + 0.5)
                continue
            if r.status_code >= 500 and attempt < 3:
                self._limiter.penalize(5.0 * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            self._cache[key] = data
            if len(self._cache) % 25 == 0:
                self._save()
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
        # Mevzuat doğrulaması official/mevzuat.py eklendiğinde bağlanacak.
        return "unknown"
