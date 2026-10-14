"""Türkçe karar künyesi ve mevzuat atfı ayrıştırma/normalleştirme.

Karar anahtarı: (mahkeme, daire_kodu, esas, karar). Örnekler:
  "Yargıtay 3. HD, E. 2019/1234, K. 2020/567, T. 12.03.2020" -> ("yargitay", "H3", "2019/1234", "2020/567")
  "Danıştay 5. Daire 2018/10 E., 2021/55 K."                  -> ("danistay", "D5", "2018/10", "2021/55")
  "AYM, B. No: 2014/12345"                                    -> ("aym", "BB", "2014/12345", None)
Mevzuat anahtarı: (kanun_no, madde) — "TBK m.344/1" -> ("6098", "344").
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from typing import Any

# --- metin normalleştirme ---------------------------------------------------

_TR_LOWER = str.maketrans({"I": "ı", "İ": "i"})


def tr_lower(s: str) -> str:
    return unicodedata.normalize("NFC", s).translate(_TR_LOWER).lower()


def fold(s: str) -> str:
    """Türkçe harfleri ASCII'ye katlayıp küçük harfe çevirir (karşılaştırma için)."""
    s = tr_lower(s)
    s = s.translate(str.maketrans("çğıöşüâîû", "cgiosuaiu"))
    return re.sub(r"\s+", " ", s).strip()


# --- numara ve tarih ----------------------------------------------------------

_NUM_RE = re.compile(r"(\d{4})\s*/\s*(\d{1,7})")
_GK_NUM_RE = re.compile(r"(\d{4})\s*/\s*(\d{1,2})\s*-\s*(\d{1,7})")  # HGK: 2013/7-591


def norm_number(value: Any) -> str | None:
    """'2019/01234', '2019 / 1234', 'E. 2019/1234' -> '2019/1234'. HGK biçimi korunur: '2013/7-591'."""
    if value is None:
        return None
    s = str(value)
    m = _GK_NUM_RE.search(s)
    if m:
        return f"{m.group(1)}/{int(m.group(2))}-{int(m.group(3))}"
    m = _NUM_RE.search(s)
    if not m:
        return None
    return f"{m.group(1)}/{int(m.group(2))}"


_ANY_NUM_RE = re.compile(r"(?<!\d)(\d{4})\s*/\s*(?:\d{1,2}\s*-\s*)?0*(\d{1,7})(?!\d)")


def numbers_in(text: str) -> list[str]:
    """Metindeki bütün YYYY/N numaraları (JSON alanları dahil), normalleştirilmiş: '2019/1234'."""
    return [f"{y}/{int(n)}" for y, n in _ANY_NUM_RE.findall(text or "")]


def strip_gk_prefix(num: str | None) -> str | None:
    """'2013/7-591' -> '2013/591' (genel kurul esasında daire öneki olmadan karşılaştırma)."""
    if not num:
        return num
    m = re.match(r"^(\d{4})/\d{1,2}-(\d+)$", num)
    return f"{m.group(1)}/{m.group(2)}" if m else num


_MONTHS = {
    "ocak": 1, "subat": 2, "mart": 3, "nisan": 4, "mayis": 5, "haziran": 6,
    "temmuz": 7, "agustos": 8, "eylul": 9, "ekim": 10, "kasim": 11, "aralik": 12,
}


def norm_date(value: Any) -> str | None:
    """'12.03.2020', '12/3/2020', '2020-03-12', '12 Mart 2020' -> '2020-03-12'."""
    if value is None:
        return None
    s = fold(str(value))
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        m = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", s)
        if m:
            d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", s)
            if not m or m.group(2) not in _MONTHS:
                return None
            d, mo, y = int(m.group(1)), _MONTHS[m.group(2)], int(m.group(3))
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


# --- mahkeme ve daire ---------------------------------------------------------


def norm_court(value: Any) -> str | None:
    if not value:
        return None
    s = fold(str(value))
    if "aihm" in s or "insan haklari mahkemesi" in s or "echr" in s:
        return "aihm"
    if "anayasa" in s or re.search(r"\baym\b", s):
        return "aym"
    if "danistay" in s or re.search(r"\bd\.\s*\d", s):
        return "danistay"
    if "bolge adliye" in s or re.search(r"\bbam\b", s):
        return "bam"
    if "bolge idare" in s or re.search(r"\bbim\b", s):
        return "bim"
    if "yargitay" in s or re.search(r"\by\.?\s*\d", s) or s in {"y", "y."}:
        return "yargitay"
    if "mahkemesi" in s:
        return "yerel"
    return None


_GENERAL_BODIES = {
    # Yargıtay
    "hukuk genel kurulu": "HGK", "hgk": "HGK",
    "ceza genel kurulu": "CGK", "cgk": "CGK",
    "buyuk genel kurul": "BGK", "bgk": "BGK",
    "hukuk daireleri baskanlar kurulu": "HDBK", "hdbk": "HDBK",
    "ceza daireleri baskanlar kurulu": "CDBK", "cdbk": "CDBK",
    "ictihadi birlestirme": "IBK", "ibk": "IBK", "ibgk": "IBK", "ictihatlari birlestirme": "IBK",
    # Danıştay
    "idari dava daireleri kurulu": "IDDK", "iddk": "IDDK",
    "vergi dava daireleri kurulu": "VDDK", "vddk": "VDDK",
}


def norm_chamber(court: str | None, value: Any) -> str | None:
    """Daireyi kanonik koda çevirir: Yargıtay 'H3'/'C12'/'HGK', Danıştay 'D5'/'IDDK', AYM bireysel 'BB',
    bölge adliye 'ANKARA-H25' (şehir biliniyorsa)."""
    if value is None:
        return None
    s = fold(str(value))
    if court in ("bam", "bim"):
        city_m = re.match(r"^([a-z]+)\s+(?:bolge\s+(?:adliye|idare)|bam\b|bim\b)", s)
        rest = norm_chamber(None, re.sub(r"^.*?(?:bolge\s+(?:adliye|idare)\s+mahkemesi|\bbam\b|\bbim\b)\s*", "", s))
        if rest:
            rest = "H" + rest[1:] if rest.startswith("D") and "hukuk" in s else rest
            return f"{city_m.group(1).upper()}-{rest}" if city_m else rest
        return None
    for key, code in _GENERAL_BODIES.items():
        if re.search(rf"\b{re.escape(key)}\b", s):
            return code
    m = re.match(r"^([hcd])\s*(\d{1,2})$", s.replace(".", ""))
    if m:
        return f"{m.group(1).upper()}{int(m.group(2))}"
    m = re.search(r"(\d{1,2})\s*\.?\s*(hukuk|ceza|hd|cd|daire|d\b)", s)
    if m:
        n, kind = int(m.group(1)), m.group(2)
        if court == "danistay" or (kind in ("daire", "d") and court not in ("yargitay", "bam")):
            return f"D{n}"
        if kind in ("hukuk", "hd"):
            return f"H{n}"
        if kind in ("ceza", "cd"):
            return f"C{n}"
        return f"D{n}"
    if court == "aym":
        if "bireysel" in s or "basvuru" in s:
            return "BB"
        if "norm" in s or "iptal" in s or "itiraz" in s:
            return "ND"
    return None


def chamber_equal(a: str, b: str) -> bool:
    """BAM dairelerinde bir tarafta şehir yoksa yalnız daire kısmı karşılaştırılır."""
    if a == b:
        return True
    if ("-" in a) != ("-" in b):
        return a.split("-")[-1] == b.split("-")[-1]
    return False


@dataclass(frozen=True)
class CaseKey:
    court: str | None
    chamber: str | None
    esas: str | None
    karar: str | None

    def short(self) -> str:
        return f"{self.court}|{self.chamber}|E.{self.esas}|K.{self.karar}"


def case_key(c: dict[str, Any]) -> CaseKey:
    court = norm_court(c.get("court") or c.get("mahkeme"))
    chamber = norm_chamber(court, c.get("chamber") or c.get("daire"))
    if court == "aym" and (c.get("basvuru_no") or c.get("bb_no")):
        return CaseKey("aym", "BB", norm_number(c.get("basvuru_no") or c.get("bb_no")), None)
    return CaseKey(
        court,
        chamber,
        norm_number(c.get("esas") or c.get("esas_no")),
        norm_number(c.get("karar") or c.get("karar_no")),
    )


@dataclass
class CaseMatch:
    esas: bool = False
    karar: bool = False
    chamber: bool | None = None
    court: bool | None = None
    date: bool | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def exact(self) -> bool:
        """Esas + karar numarası tutuyor ve (biliniyorsa) daire/mahkeme çelişmiyor."""
        return self.esas and self.karar and self.chamber is not False and self.court is not False


def match_case(pred: dict[str, Any], gold: dict[str, Any]) -> CaseMatch:
    p, g = case_key(pred), case_key(gold)
    m = CaseMatch()
    if g.court == "aym" and g.chamber == "BB":
        m.esas = p.esas is not None and p.esas == g.esas
        m.karar = m.esas
        m.court = None if p.court is None else p.court == "aym"
        return m
    m.esas = p.esas is not None and strip_gk_prefix(p.esas) == strip_gk_prefix(g.esas)
    m.karar = p.karar is not None and p.karar == g.karar
    m.court = None if (p.court is None or g.court is None) else p.court == g.court
    m.chamber = None if (p.chamber is None or g.chamber is None) else chamber_equal(p.chamber, g.chamber)
    pd, gd = norm_date(pred.get("date") or pred.get("tarih")), norm_date(gold.get("date") or gold.get("tarih"))
    m.date = None if (pd is None or gd is None) else pd == gd
    return m


# --- serbest metinden künye çıkarma -------------------------------------------

_CASE_TEXT_RE = re.compile(
    r"(?P<court>Yargıtay|Yarg\.|Y\.|Danıştay|D\.|Anayasa Mahkemesi|AYM|Bölge Adliye Mahkemesi|BAM)?"
    r"[\s,]*(?P<chamber>\d{1,2}\s*\.?\s*(?:Hukuk|Ceza)?\s*(?:Dairesi|D\.|HD|CD|Daire)|HGK|CGK|İBK|IBK|İDDK|IDDK|VDDK|Hukuk Genel Kurulu|Ceza Genel Kurulu)?"
    r"[\s,:;-]*(?:E(?:sas)?\.?\s*(?:No\.?)?\s*:?\s*)(?P<esas>\d{4}\s*/\s*\d{1,2}(?:\s*-\s*\d{1,7})?|\d{4}\s*/\s*\d{1,7})"
    r"[\s,;-]*(?:K(?:arar)?\.?\s*(?:No\.?)?\s*:?\s*)(?P<karar>\d{4}\s*/\s*\d{1,7})"
    r"(?:[\s,;-]*(?:T(?:arih)?\.?\s*:?\s*)?(?P<date>\d{1,2}[./]\d{1,2}[./]\d{4}))?",
    re.I,
)
_CASE_TEXT_RE_SUFFIX = re.compile(
    r"(?P<esas>\d{4}\s*/\s*\d{1,7})\s*E\.?\s*,?\s*(?P<karar>\d{4}\s*/\s*\d{1,7})\s*K\.?",
    re.I,
)


def extract_case_citations(text: str) -> list[dict[str, Any]]:
    """Serbest metindeki karar künyelerini kaba biçimde çıkarır (hallucination denetimi için)."""
    out: list[dict[str, Any]] = []
    seen: set[tuple[str | None, str | None]] = set()
    for m in _CASE_TEXT_RE.finditer(text or ""):
        item = {k: (v.strip() if isinstance(v, str) else v) for k, v in m.groupdict().items()}
        key = (norm_number(item["esas"]), norm_number(item["karar"]))
        if key not in seen:
            seen.add(key)
            out.append(item)
    for m in _CASE_TEXT_RE_SUFFIX.finditer(text or ""):
        key = (norm_number(m.group("esas")), norm_number(m.group("karar")))
        if key not in seen:
            seen.add(key)
            # Künyenin önündeki 80 karakterde mahkeme/daire adı aranır.
            ctx = (text or "")[max(0, m.start() - 80) : m.start()]
            court = norm_court(ctx)
            chamber_m = re.search(r"(\d{1,2}\s*\.?\s*(?:Hukuk|Ceza)?\s*(?:Dairesi|HD|CD|Daire)|HGK|CGK)", ctx, re.I)
            out.append(
                {"court": court, "chamber": chamber_m.group(1) if chamber_m else None,
                 "esas": m.group("esas"), "karar": m.group("karar"), "date": None}
            )
    return out


# --- mevzuat atıfları ------------------------------------------------------------

LAW_ABBREVIATIONS: dict[str, str] = {
    "anayasa": "2709", "ay": "2709",
    "tmk": "4721", "medeni kanun": "4721", "turk medeni kanunu": "4721",
    "tbk": "6098", "borclar kanunu": "6098", "turk borclar kanunu": "6098",
    "ttk": "6102", "ticaret kanunu": "6102", "turk ticaret kanunu": "6102",
    "hmk": "6100", "hukuk muhakemeleri kanunu": "6100",
    "iik": "2004", "icra ve iflas kanunu": "2004",
    "tck": "5237", "turk ceza kanunu": "5237",
    "cmk": "5271", "ceza muhakemesi kanunu": "5271",
    "iyuk": "2577", "idari yargilama usulu kanunu": "2577",
    "is kanunu": "4857", "ik": "4857",
    "ssgssk": "5510", "sosyal sigortalar ve genel saglik sigortasi kanunu": "5510",
    "vuk": "213", "vergi usul kanunu": "213",
    "aauk": "6183", "amme alacaklarinin tahsil usulu hakkinda kanun": "6183",
    "avukatlik kanunu": "1136", "av.k": "1136",
    "tkhk": "6502", "tuketicinin korunmasi hakkinda kanun": "6502",
    "kvkk": "6698", "kisisel verilerin korunmasi kanunu": "6698",
    "dmk": "657", "devlet memurlari kanunu": "657",
    "kmk": "634", "kat mulkiyeti kanunu": "634",
    "tebligat kanunu": "7201",
    "harclar kanunu": "492",
    "kamulastirma kanunu": "2942",
    "mohuk": "5718", "milletlerarasi ozel hukuk ve usul hukuku hakkinda kanun": "5718",
    "cgtihk": "5275", "ceza ve guvenlik tedbirlerinin infazi hakkinda kanun": "5275",
    "kabahatler kanunu": "5326",
    "gvk": "193", "gelir vergisi kanunu": "193",
    "kdvk": "3065",
    "vergi mahkemeleri": "2576",
    "arabuluculuk": "6325", "hukuk uyusmazliklarinda arabuluculuk kanunu": "6325",
    "is mahkemeleri kanunu": "7036",
    "tapu kanunu": "2644",
    "imar kanunu": "3194",
    "polis vazife ve salahiyet kanunu": "2559", "pvsk": "2559",
}

_LAW_NO_RE = re.compile(r"(\d{2,4})\s*sayılı", re.I)
_ARTICLE_RE = re.compile(r"(?:\bm(?:adde)?\.?\s*|(?<=\s))(\d{1,4})(?:\s*/\s*\d+)?(?:\s*\.?\s*madde)?", re.I)


def norm_law_no(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    m = re.fullmatch(r"\d{1,5}", s)
    if m:
        return str(int(s))
    m = _LAW_NO_RE.search(s)
    if m:
        return str(int(m.group(1)))
    f = fold(s).rstrip(".")
    if f in LAW_ABBREVIATIONS:
        return LAW_ABBREVIATIONS[f]
    for name, no in sorted(LAW_ABBREVIATIONS.items(), key=lambda kv: -len(kv[0])):
        if len(name) > 4 and name in f:
            return no
    return None


def norm_article(value: Any) -> str | None:
    """'344', 'm.344/1', '344. madde', 'geçici 1' -> '344' / 'gecici-1'."""
    if value is None:
        return None
    s = fold(str(value))
    m = re.search(r"(gecici|ek)\s*(?:madde)?\s*(\d+)", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2))}"
    m = re.search(r"(\d{1,4})\s*/?\s*([a-z])?\b", s)
    if not m:
        return None
    art = str(int(m.group(1)))
    if m.group(2) and len(m.group(2)) == 1 and m.group(2) not in "fbm":
        art += f"/{m.group(2).upper()}"
    return art


def statute_key(c: dict[str, Any]) -> tuple[str | None, str | None]:
    return norm_law_no(c.get("law_no") or c.get("kanun_no") or c.get("law")), norm_article(
        c.get("article") or c.get("madde")
    )


_STATUTE_TEXT_RE = re.compile(
    r"(?P<law>(?:\d{2,4}\s*sayılı\s*[\wçğıöşüÇĞİÖŞÜ' ]{0,60}?(?:Kanun|Kanunu|KHK|Yönetmelik)\w*)|"
    r"\b(?:TBK|TMK|TTK|HMK|İİK|IİK|TCK|CMK|İYUK|IYUK|VUK|AAUK|TKHK|KVKK|DMK|KMK|MÖHUK|MOHUK|İK|AY|Anayasa)\b)"
    r"[\s'’]*(?:'?(?:nun|nın|un|ın|ün|in)\s*)?"
    r"(?:m\.?|md\.?|madde)?\s*(?P<art>\d{1,4})(?:\s*/\s*\d+)?\s*(?:\.?\s*madde\w*)?",
    re.I,
)


def extract_statute_citations(text: str) -> list[dict[str, Any]]:
    out, seen = [], set()
    for m in _STATUTE_TEXT_RE.finditer(text or ""):
        key = (norm_law_no(m.group("law")), norm_article(m.group("art")))
        if key[0] and key[1] and key not in seen:
            seen.add(key)
            out.append({"type": "mevzuat", "law_no": key[0], "article": key[1], "raw": m.group(0).strip()})
    return out
