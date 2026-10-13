"""Puanlardan lider tablosu ve ayrıntılı rapor üretir (Markdown + JSON).

Karşılaştırmalar yalnız iki sistemin de cevapladığı ortak görevler üzerinden yapılır.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..io import RESULTS_DIR, read_models
from ..schema import RunRecord, ScoreRecord, Task
from ..scoring.score_run import latest_runs
from ..scoring.stats import bootstrap_ci, mcnemar_exact, mean, paired_bootstrap_diff

TRACK_TITLES = {
    "exam": "Sınav (HMGS / hâkimlik / KPSS)",
    "statute": "Mevzuat",
    "case_lookup": "Karar bulma",
    "citation_check": "Atıf denetimi",
    "research": "Açık araştırma",
}


def _fmt(x: float | None, pct: bool = True) -> str:
    if x is None or x != x:  # NaN
        return "—"
    return f"{100 * x:.1f}" if pct else f"{x:.2f}"


def build_report(run_name: str, tasks: dict[str, Task], labels: dict[str, str] | None = None) -> dict[str, Any]:
    labels = labels or {}
    scores = read_models(RESULTS_DIR / run_name / "scores.jsonl", ScoreRecord)
    runs = {(r.system_id, r.task_id): r for r in latest_runs(run_name)}
    by_sys_track: dict[tuple[str, str], dict[str, ScoreRecord]] = defaultdict(dict)
    for s in scores:
        by_sys_track[(s.system_id, s.track)][s.task_id] = s
    systems = sorted({s.system_id for s in scores})
    tracks = [t for t in TRACK_TITLES if any(k[1] == t for k in by_sys_track)]

    table: list[dict[str, Any]] = []
    for sid in systems:
        row: dict[str, Any] = {"system": sid, "label": labels.get(sid, sid), "tracks": {}}
        sys_runs = [r for (s, _), r in runs.items() if s == sid]
        row["avg_tool_calls"] = mean([r.n_tool_calls + r.server_tool_uses for r in sys_runs])
        row["avg_latency_s"] = mean([r.latency_s for r in sys_runs])
        row["avg_input_tokens"] = mean([r.input_tokens for r in sys_runs])
        row["avg_output_tokens"] = mean([r.output_tokens for r in sys_runs])
        row["error_rate"] = mean([1.0 if r.error else 0.0 for r in sys_runs])
        row["tool_error_rate"] = mean(
            [0.0 if c.ok else 1.0 for r in sys_runs for c in r.tool_calls]
        ) if any(r.tool_calls for r in sys_runs) else None
        g_vals = []
        fabricated = cited = 0
        for tr in ("case_lookup", "research"):
            for s in by_sys_track.get((sid, tr), {}).values():
                g = s.details.get("grounding", s.details.get("citations", {}).get("grounding"))
                if g is not None:
                    g_vals.append(g)
                c = s.details.get("citations") or {}
                fabricated += c.get("n_fabricated") or 0
                cited += (c.get("n_case_citations") or 0) + (c.get("n_statute_citations") or 0)
        row["grounding"] = mean(g_vals) if g_vals else None
        row["research_fabricated_per_citation"] = (fabricated / cited) if cited else None
        for tr in tracks:
            vals = [s.score for s in by_sys_track.get((sid, tr), {}).values()]
            if vals:
                lo, hi = bootstrap_ci(vals)
                row["tracks"][tr] = {"n": len(vals), "mean": mean(vals), "ci": [lo, hi]}
        table.append(row)

    # Track ortalamalarının eşit ağırlıklı ortalaması (yalnız bütün track'leri koşan sistemler için).
    for row in table:
        if tracks and all(tr in row["tracks"] for tr in tracks):
            row["overall"] = mean([row["tracks"][tr]["mean"] for tr in tracks])

    pairwise: list[dict[str, Any]] = []
    for tr in tracks:
        for i, a in enumerate(systems):
            for b in systems[i + 1 :]:
                sa, sb = by_sys_track.get((a, tr), {}), by_sys_track.get((b, tr), {})
                common = sorted(set(sa) & set(sb))
                if len(common) < 5:
                    continue
                entry: dict[str, Any] = {"track": tr, "a": a, "b": b, "n": len(common)}
                entry.update(paired_bootstrap_diff([sa[t].score for t in common], [sb[t].score for t in common]))
                if tr == "exam":
                    entry["mcnemar"] = mcnemar_exact([bool(sa[t].correct) for t in common],
                                                     [bool(sb[t].correct) for t in common])
                pairwise.append(entry)

    # Sınav: konu ve araç-ilgisi kırılımları
    breakdowns: dict[str, dict[str, dict[str, float]]] = {}
    for key in ("subject", "tool_relevance", "session"):
        agg: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        for (sid, tr), items in by_sys_track.items():
            if tr != "exam":
                continue
            for tid, s in items.items():
                val = tasks[tid].meta.get(key) if tid in tasks else None
                if val:
                    agg[str(val)][sid].append(s.score)
        breakdowns[key] = {g: {sid: mean(v) for sid, v in per.items()} for g, per in sorted(agg.items())}

    # Karar bulma: kaynak katmanına (mahkeme türü) göre kırılım
    strata: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for (sid, tr), items in by_sys_track.items():
        if tr == "case_lookup":
            for tid, s in items.items():
                st = tasks[tid].meta.get("stratum") if tid in tasks else None
                if st:
                    strata[str(st)][sid].append(s.score)
    breakdowns["case_stratum"] = {g: {sid: mean(v) for sid, v in per.items()} for g, per in sorted(strata.items())}

    return {"run": run_name, "systems": systems, "tracks": tracks, "table": table,
            "pairwise": pairwise, "exam_breakdowns": breakdowns}


def render_markdown(rep: dict[str, Any]) -> str:
    tracks = rep["tracks"]
    lines = [f"# Legaluga Law Benchmark — {rep['run']}", ""]
    head = "| Sistem | " + " | ".join(TRACK_TITLES[t] for t in tracks) + " | Genel | Ort. araç çağrısı | Ort. süre (sn) | Hata oranı |"
    lines += [head, "|" + "---|" * (len(tracks) + 5)]
    rows = sorted(rep["table"], key=lambda r: -(r.get("overall") or -1))
    for r in rows:
        cells = []
        for t in tracks:
            c = r["tracks"].get(t)
            cells.append(f"{_fmt(c['mean'])} ({_fmt(c['ci'][0])}–{_fmt(c['ci'][1])}, n={c['n']})" if c else "—")
        lines.append(
            f"| {r['label']} | " + " | ".join(cells) +
            f" | {_fmt(r.get('overall'))} | {_fmt(r['avg_tool_calls'], pct=False)} | {_fmt(r['avg_latency_s'], pct=False)} | {_fmt(r['error_rate'])} |"
        )
    lines += ["", "Puanlar 0-100 ölçeğinde; parantez içi %95 bootstrap güven aralığı.", ""]
    lines += ["## Kaynağa dayanma ve uydurma", "",
              "| Sistem | Dayanak oranı (künye araç çıktısında geçiyor) | Araştırmada uydurma atıf oranı |",
              "|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['label']} | {_fmt(r.get('grounding'))} | {_fmt(r.get('research_fabricated_per_citation'))} |")
    lines.append("")
    if rep["pairwise"]:
        lines += ["## Eşleştirilmiş karşılaştırmalar", "",
                  "| Track | A | B | n | Ort. fark (A−B) | %95 GA | McNemar p |", "|---|---|---|---|---|---|---|"]
        for p in rep["pairwise"]:
            mc = p.get("mcnemar", {}).get("p_value")
            lines.append(
                f"| {TRACK_TITLES[p['track']]} | {p['a']} | {p['b']} | {p['n']} | {_fmt(p['mean_diff'])} | "
                f"{_fmt(p['ci_low'])} – {_fmt(p['ci_high'])} | {'—' if mc is None else f'{mc:.3g}'} |"
            )
        lines.append("")
    for key, title in (("tool_relevance", "Sınav: soru türüne göre"), ("subject", "Sınav: derse göre"),
                       ("session", "Sınav: oturuma göre"), ("case_stratum", "Karar bulma: mahkemeye göre")):
        groups = rep["exam_breakdowns"].get(key) or {}
        if not groups:
            continue
        systems = rep["systems"]
        lines += [f"## {title}", "", "| Grup | " + " | ".join(systems) + " |", "|---|" + "---|" * len(systems)]
        for g, per in groups.items():
            lines.append(f"| {g} | " + " | ".join(_fmt(per.get(s)) for s in systems) + " |")
        lines.append("")
    return "\n".join(lines)


def write_report(run_name: str, tasks: dict[str, Task], labels: dict[str, str] | None = None) -> tuple[Path, Path]:
    rep = build_report(run_name, tasks, labels)
    out_dir = RESULTS_DIR / run_name
    md, js = out_dir / "report.md", out_dir / "report.json"
    md.write_text(render_markdown(rep), encoding="utf-8")
    js.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    return md, js
