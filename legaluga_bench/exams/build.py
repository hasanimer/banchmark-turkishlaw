"""Yazıya dökülmüş ÖSYM sorularını (data/private/exams/raw/*.jsonl) görev setine çevirir.

Adımlar:
1. Aynı kaynağın parçalarını birleştir; iki parçaya bölünmüş (partial) soruları tek kayda indir.
2. Aynı oturumun farklı çekimlerini (ör. HMGS 2026 Eylül A/B) karşılaştır; cevap anahtarı
   uyuşmayan soruları çıkar ve raporla.
3. Hukuk dışı (GKGY), cevap anahtarı olmayan, şıkkı eksik ya da şekle dayalı soruları ayıkla.
4. data/private/tasks/exam_osym.jsonl (telifli; gitignored) ve data/exams_manifest.json
   (yalnız sayılar ve dosya özetleri; public) üret.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..io import DATA_DIR, PRIVATE_DIR, PRIVATE_TASKS_DIR, read_jsonl, write_jsonl
from ..schema import OPTION_LETTERS, Task
from ..scoring.citations import fold

RAW_DIR = PRIVATE_DIR / "exams" / "raw"


@dataclass(frozen=True)
class Session:
    slug: str
    exam: str
    label: str
    year: int
    date_hint: str  # soruda ajana gösterilen sınav zamanı


# Kaynak dosya kökü -> oturum. Aynı oturumun birden çok çekimi aynı slug'ı paylaşır.
SESSIONS: dict[str, Session] = {
    "hmgs_2024_eylul": Session("hmgs-2024-eylul", "HMGS", "HMGS 2024 Eylül", 2024, "Eylül 2024"),
    "hmgs_2025_1": Session("hmgs-2025-1", "HMGS", "HMGS 2025/1", 2025, "2025 yılı 1. oturum"),
    "hmgs_2025_2": Session("hmgs-2025-2", "HMGS", "HMGS 2025/2", 2025, "2025 yılı 2. oturum"),
    "hmgs_2026_nisan": Session("hmgs-2026-nisan", "HMGS", "HMGS 2026 Nisan", 2026, "Nisan 2026"),
    "hmgs_eylul": Session("hmgs-2026-eylul", "HMGS", "HMGS 2026 Eylül", 2026, "Eylül 2026"),
    "hmgs_2026_eylul_b": Session("hmgs-2026-eylul", "HMGS", "HMGS 2026 Eylül", 2026, "Eylül 2026"),
    "kpss_hukuk_2026": Session("kpss-hukuk-2026", "KPSS", "KPSS A Grubu Hukuk 2026", 2026, "2026"),
    "iyoss_2025": Session("iyos-2025", "ÖSYM", "İYÖS 2025", 2025, "2025"),
    "hakimlik_2018_adli": Session("hsa-2018", "HSA", "Hâkim ve Savcı Adaylığı 2018", 2018, "2018"),
    "hakimlik_2019_adli_idari": Session("hsa-2019", "HSA", "Hâkim ve Savcı Adaylığı 2019", 2019, "2019"),
    "hakimlik_2020_gkgy_ortak_adli": Session("hsa-2020", "HSA", "Hâkim ve Savcı Adaylığı 2020", 2020, "2020"),
    "hakimlik_2021": Session("hsa-2021", "HSA", "Hâkim ve Savcı Adaylığı 2021", 2021, "2021"),
    "hakimlik_2022": Session("hsa-2022", "HSA", "Hâkim ve Savcı Adaylığı 2022", 2022, "2022"),
    "hakimlik_2023_adli_alan": Session("hsa-2023-adli", "HSA", "Hâkim ve Savcı Adaylığı 2023 (adli alan)", 2023, "2023"),
    "hakimlik_2023_ortak_alan": Session("hsa-2023-ortak", "HSA", "Hâkim ve Savcı Adaylığı 2023 (ortak alan)", 2023, "2023"),
    "hakimlik_2024_adli_mezun": Session("hsa-2024-adli", "HSA", "Hâkim ve Savcı Adaylığı 2024 (adli)", 2024, "2024"),
    "hakimlik_2025_adli_yargi": Session("hsa-2025-adli", "HSA", "Hâkim ve Savcı Adaylığı 2025 (adli alan)", 2025, "2025"),
    "hakimlik_2025_ortak_alan": Session("hsa-2025-ortak", "HSA", "Hâkim ve Savcı Adaylığı 2025 (ortak alan)", 2025, "2025"),
    "hmgs_unknown_1": Session("unknown-1", "?", "Bilinmeyen kaynak", 0, ""),
}

EXAM_NOTE = (
    "Bu soru {label} sınavından alınmıştır ({date}). Cevabı sınav tarihinde yürürlükte olan "
    "mevzuata göre veriniz."
)


def _norm_ws(s: str) -> str:
    return " ".join((s or "").split())


def _merge_partials(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aynı soru numarasının kayıtlarını birleştirir; en eksiksiz olanı esas alır."""
    rows = sorted(rows, key=lambda r: (r.get("partial", False), -len(r.get("stem") or "")))
    best = dict(rows[0])
    if len(rows) > 1:
        pages = sorted({p for r in rows for p in (r.get("pages") or [])})
        best["pages"] = pages
        opts = dict(best.get("options") or {})
        for r in rows[1:]:
            for k, v in (r.get("options") or {}).items():
                if v and not opts.get(k):
                    opts[k] = v
            if not best.get("answer") and r.get("answer"):
                best["answer"] = r["answer"]
        best["options"] = opts
        stems = [r.get("stem") or "" for r in rows]
        if all(r.get("partial") for r in rows):
            # İki parça: sayfa sırasına göre ekle.
            ordered = sorted(rows, key=lambda r: min(r.get("pages") or [0]))
            best["stem"] = "\n".join(s for s in (r.get("stem") or "" for r in ordered) if s)
        best["partial"] = not (best.get("stem") and all(opts.get(k) for k in OPTION_LETTERS))
        best["has_figure"] = any(r.get("has_figure") for r in rows)
        best["notes"] = " | ".join(n for n in (r.get("notes") or "" for r in rows) if n)
        best["_merged_from"] = len(rows)
        best["_stems_seen"] = len({_norm_ws(s) for s in stems})
    return best


_SECTION_WORDS = (
    ("gkgy", ("gkgy", "genel yetenek", "genel kultur")),
    ("idari", ("idari yargi",)),
    ("adli", ("adli yargi",)),
    ("ortak", ("ortak alan",)),
)


def _assign_sections(rows: list[dict[str, Any]]) -> tuple[list[str], dict[str, str]]:
    """Sayfa sırasındaki kayıtlara bölüm etiketi verir: tek bölümlü dosyada "", çok bölümlüde b1, b2, ...

    Bölüm geçişi yalnız gerçek yeniden numaralanmada sayılır: numara 1-2'ye döner, bir önceki numara
    en az 5'tir ve mevcut bölümde en az 5 soru vardır. Karışık sırayla çekilmiş ekran görüntüleri
    (ör. 14'ten sonra 9) ve bir önceki parçanın devamı olan kayıtlar bölüm açmaz. Etiketler kararlı
    kimlik için sıra numarasıdır; exam_guess'ten çıkarılan bölüm adı (ortak/idari/adli/gkgy) ayrıca döner.
    """
    idx, prev, recent, raw = 0, None, [], []
    for r in rows:
        q = int(r["q_no"])
        continuation = bool(r.get("partial")) and q in recent[-3:]
        if prev is not None and not continuation and q <= 2 and prev >= 5 and len(recent) >= 5:
            idx += 1
            recent = []
        raw.append(idx)
        if not continuation:
            prev = q
            recent.append(q)
    if idx == 0:
        return [""] * len(rows), {}
    names: dict[str, str] = {}
    for sec in range(idx + 1):
        text = fold(" ".join(str(r.get("exam_guess") or "") for r, s in zip(rows, raw) if s == sec))
        votes = {name: sum(text.count(w) for w in words) for name, words in _SECTION_WORDS}
        best = max(votes, key=votes.get)
        names[f"b{sec + 1}"] = best if votes[best] > 0 else ""
    return [f"b{s + 1}" for s in raw], names


def _valid(q: dict[str, Any]) -> tuple[bool, str]:
    if not q.get("is_law", True):
        return False, "hukuk_disi"
    if (q.get("answer") or "").upper() not in OPTION_LETTERS:
        return False, "cevap_anahtari_yok"
    opts = q.get("options") or {}
    if not all((opts.get(k) or "").strip() for k in OPTION_LETTERS):
        return False, "sik_eksik"
    if not (q.get("stem") or "").strip():
        return False, "govde_eksik"
    if q.get("partial"):
        return False, "eksik_parca"
    if q.get("has_figure"):
        return False, "sekil"
    return True, "ok"


def _split_for(task_id: str, dev_fraction: float = 0.15) -> str:
    h = int(hashlib.sha256(task_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "dev" if h < dev_fraction else "test"


def build(
    raw_dir: Path = RAW_DIR,
    tasks_out: Path | None = None,
    manifest_out: Path | None = None,
) -> dict[str, Any]:
    # Kaynak dosya başına kayıtlar, sayfa sırasıyla. Bazı derlemelerde (ör. 2018-2019 hâkimlik)
    # soru numarası her bölümde (ortak alan, idari yargı, adli yargı) 1'den yeniden başlar; bölümler
    # sayfa sırasında numaranın geriye düşmesinden ayırt edilir.
    by_stem: dict[str, list[tuple[tuple[int, str, int], dict[str, Any]]]] = defaultdict(list)
    for path in sorted(raw_dir.glob("*.jsonl")):
        for i, row in enumerate(read_jsonl(path)):
            if row.get("q_no") is None:
                continue
            stem = row.get("source_file") or path.name.split("__")[0]
            first_page = min(row.get("pages") or [0])
            by_stem[stem].append(((first_page, path.name, i), row))

    by_stem_q: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    section_names: dict[tuple[str, str], str] = {}
    for stem, items in by_stem.items():
        items.sort(key=lambda x: x[0])
        sections, names = _assign_sections([row for _, row in items])
        for label, name in names.items():
            section_names[(stem, label)] = name
        for (_, row), label in zip(items, sections):
            by_stem_q[(stem, label, int(row["q_no"]))].append(row)

    # oturum -> (bölüm, soru no) -> [(kaynak, birleşik kayıt)]
    by_session: dict[str, dict[tuple[str, int], list[tuple[str, dict[str, Any]]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for (stem, label, qno), rows in by_stem_q.items():
        sess = SESSIONS.get(stem)
        if sess is None:
            continue
        by_session[sess.slug][(label, qno)].append((stem, _merge_partials(rows)))

    tasks: list[Task] = []
    rejected: Counter[str] = Counter()
    capture_conflicts: list[dict[str, Any]] = []
    per_session: dict[str, Counter[str]] = defaultdict(Counter)
    for slug, qs in sorted(by_session.items()):
        for (label, qno), versions in sorted(qs.items()):
            sess = SESSIONS[versions[0][0]]
            valid = [(s, q) for s, q in versions if _valid(q)[0]]
            if not valid:
                reason = _valid(versions[0][1])[1]
                rejected[reason] += 1
                per_session[slug][f"red:{reason}"] += 1
                continue
            answers = {q["answer"].upper() for _, q in valid}
            if len(answers) > 1:
                capture_conflicts.append({"session": slug, "section": label, "q_no": qno, "answers": sorted(answers)})
                rejected["cekim_uyusmazligi"] += 1
                per_session[slug]["red:cekim_uyusmazligi"] += 1
                continue
            stem, q = valid[0]
            task_id = f"exam-{slug}-q{qno:03d}" if not label else f"exam-{slug}-{label}-q{qno:03d}"
            note = EXAM_NOTE.format(label=sess.label, date=sess.date_hint) if sess.year else ""
            tasks.append(
                Task(
                    id=task_id,
                    track="exam",
                    split=_split_for(task_id),
                    prompt=(f"{note}\n\n" if note else "") + q["stem"].strip(),
                    options={k: q["options"][k].strip() for k in OPTION_LETTERS},
                    gold={"answer": q["answer"].upper(), "answer_source": "ÖSYM aday ekranı cevap anahtarı"},
                    meta={
                        "exam": sess.exam,
                        # 2024 ve sonrası oturumlar ana puanı oluşturur; öncekiler arşiv olarak ayrı raporlanır.
                        "tier": "guncel" if sess.year >= 2024 else "arsiv",
                        "session": sess.label,
                        "session_slug": slug,
                        "year": sess.year,
                        "q_no": qno,
                        "section": label or None,
                        "section_name": section_names.get((stem, label)) or None,
                        "subject": q.get("subject"),
                        "tool_relevance": q.get("tool_relevance"),
                        "basis_hint": q.get("basis_hint") or [],
                        "source_files": sorted({s for s, _ in valid}),
                        "captures_agree": len(valid) if len(valid) > 1 else None,
                        "transcription_notes": q.get("notes") or "",
                    },
                )
            )
            per_session[slug]["kabul"] += 1

    write_jsonl(tasks_out or (PRIVATE_TASKS_DIR / "exam_osym.jsonl"), tasks)

    manifest = {
        "description": "ÖSYM sınav soruları görev seti özeti. Soru metinleri telif nedeniyle repoda yer almaz; "
                       "data/private altında üretilir.",
        "n_tasks": len(tasks),
        "by_session": {k: dict(v) for k, v in sorted(per_session.items())},
        "by_subject": dict(Counter(t.meta.get("subject") for t in tasks).most_common()),
        "by_tool_relevance": dict(Counter(t.meta.get("tool_relevance") for t in tasks).most_common()),
        "by_split": dict(Counter(t.split for t in tasks)),
        "rejected": dict(rejected),
        "capture_conflicts": capture_conflicts,
        "sources": _source_hashes(),
    }
    (manifest_out or (DATA_DIR / "exams_manifest.json")).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def _source_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    src = PRIVATE_DIR / "sources"
    for stem in SESSIONS:
        for path in src.glob(f"*/{stem}.pdf"):
            h = hashlib.sha256(path.read_bytes()).hexdigest()
            out[stem] = h
    return out
