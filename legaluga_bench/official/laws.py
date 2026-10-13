"""Sık atıf yapılan kanunların güncel tam metnini (değişiklik notlarıyla) resmî kaynaktan indirir.

Sınav sorularının güncellik denetiminde, bir hükmün sınav tarihinden sonra değişip
değişmediğini ağ trafiği yaratmadan yerel metin üzerinde görmek için kullanılır.
Çıktı: data/private/cache/laws/<kanun_no>.txt ve laws_index.json
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging

from bs4 import BeautifulSoup

from ..io import PRIVATE_DIR
from .bedesten import BedestenClient

log = logging.getLogger("lbench.laws")
LAWS_DIR = PRIVATE_DIR / "cache" / "laws"

CORE_LAWS = (
    "2709", "4721", "6098", "6102", "6100", "2004", "5237", "5271", "2577", "2575", "2576", "4857", "5510",
    "6356", "213", "6183", "193", "1136", "6502", "6698", "657", "2942", "7201", "634", "6325", "5718", "5275",
    "5326", "3194", "2886", "4734", "5393", "5216", "6216", "2820", "298", "4483", "6328", "7036", "5235",
    "2802", "6087", "2797", "3065", "492", "6754", "1512", "5651", "3402", "2644", "6362", "5411", "4054",
    "6361", "6758", "2559", "5442", "3091", "2565", "1163", "4734", "4735", "6085", "6764", "5018",
)


async def fetch_laws(numbers: tuple[str, ...] = CORE_LAWS) -> dict[str, dict]:
    LAWS_DIR.mkdir(parents=True, exist_ok=True)
    client = BedestenClient()
    index: dict[str, dict] = {}
    try:
        for no in dict.fromkeys(numbers):
            law = await client.find_law(no)
            if law is None:
                log.warning("%s: Bedesten mevzuat dizininde yok", no)
                continue
            res = await client._post("/mevzuat/getDocumentContent",
                                     {"data": {"documentType": "MEVZUAT", "id": law["mevzuatId"]},
                                      "applicationName": "UyapMevzuat"})
            content = (res.get("data") or {}).get("content")
            if not content:
                continue
            html = base64.b64decode(content).decode("utf-8", errors="replace")
            text = BeautifulSoup(html, "html.parser").get_text("\n", strip=True)
            (LAWS_DIR / f"{no}.txt").write_text(text, encoding="utf-8")
            index[no] = {"name": law.get("mevzuatAdi"), "mevzuat_id": law.get("mevzuatId"),
                         "url": law.get("url"), "chars": len(text)}
            log.info("%s %s (%d karakter)", no, law.get("mevzuatAdi"), len(text))
    finally:
        await client.aclose()
    (LAWS_DIR / "laws_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return index


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    idx = asyncio.run(fetch_laws())
    print(json.dumps({"n_laws": len(idx)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
