"""Komut satırı: python -m legaluga_bench <komut> ...

Komutlar:
  systems         Tanımlı sistemleri ve gerekli ortam değişkenlerini listeler (--probe: bağlanıp araçları sayar)
  tasks           Görev setinin özetini verir
  build-exams     Yazıya dökülmüş ÖSYM sorularından sınav görevlerini üretir
  run             Görevleri seçilen sistemlerde koşturur
  import-runs     Harness dışında üretilmiş koşu kayıtlarını (JSONL) bir koşuya ekler
  score           Bir koşuyu puanlar
  report          Lider tablosu ve ayrıntılı rapor üretir
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from collections import Counter

from .io import RESULTS_DIR, append_jsonl, read_models
from .schema import TRACKS, RunRecord


def _csv(value: str | None) -> list[str] | None:
    return [v.strip() for v in value.split(",") if v.strip()] if value else None


def cmd_systems(args: argparse.Namespace) -> int:
    from .systems import load_system_configs, make_provider
    from .systems.base import MissingEnvError, expand_env

    configs = load_system_configs()
    for sid, cfg in configs.items():
        status = "hazır"
        try:
            for v in [cfg.command or "", cfg.url or "", *cfg.args, *cfg.env.values(), *cfg.headers.values()]:
                expand_env(v)
        except MissingEnvError as e:
            status = f"eksik: {e}"
        print(f"{sid:22s} {cfg.kind:22s} {status}  — {cfg.label}")
        if args.probe and status == "hazır" and cfg.kind.startswith("mcp"):

            async def probe(c=cfg) -> None:
                async with make_provider(c) as p:
                    tools = await p.list_tools()
                    print(f"    {len(tools)} araç: " + ", ".join(t.name for t in tools))

            try:
                asyncio.run(probe())
            except Exception as e:  # noqa: BLE001
                print(f"    bağlantı hatası: {type(e).__name__}: {e}")
    return 0


def cmd_tasks(args: argparse.Namespace) -> int:
    from .tasks import load_tasks

    tasks = load_tasks(tracks=_csv(args.tracks), split=args.split)
    print(f"Toplam {len(tasks)} görev")
    for (track, split), n in sorted(Counter((t.track, t.split) for t in tasks).items()):
        print(f"  {track:16s} {split:5s} {n}")
    return 0


def cmd_build_exams(args: argparse.Namespace) -> int:
    from .exams.build import build

    manifest = build()
    print(json.dumps({k: manifest[k] for k in ("n_tasks", "by_session", "rejected", "by_split")},
                     ensure_ascii=False, indent=2))
    if manifest["capture_conflicts"]:
        print(f"Çekim uyuşmazlığı: {len(manifest['capture_conflicts'])} soru (exams_manifest.json)")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    from .agent import AgentSettings
    from .runner import run_benchmark
    from .systems import load_system_configs
    from .tasks import load_tasks

    configs = load_system_configs()
    wanted = _csv(args.systems) or list(configs)
    unknown = [s for s in wanted if s not in configs]
    if unknown:
        print(f"Bilinmeyen sistem(ler): {', '.join(unknown)}", file=sys.stderr)
        return 2
    tasks = load_tasks(tracks=_csv(args.tracks), split=args.split, limit_per_track=args.limit, seed=args.seed)
    if not tasks:
        print("Seçime uyan görev yok.", file=sys.stderr)
        return 2
    if not args.model:
        print("Ajan modeli belirtilmedi: --model ya da LBENCH_AGENT_MODEL kullanın.", file=sys.stderr)
        return 2
    settings = AgentSettings(model=args.model, effort=args.effort, max_tool_calls=args.max_tool_calls,
                             max_turns=args.max_turns)
    if args.today:
        settings.today = args.today
    meta = {"model": settings.model, "effort": settings.effort, "max_tool_calls": settings.max_tool_calls,
            "max_turns": settings.max_turns, "today": settings.today, "systems": wanted,
            "n_tasks": len(tasks), "tracks": sorted({t.track for t in tasks})}
    out = RESULTS_DIR / args.run_name
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_config.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = asyncio.run(run_benchmark([configs[s] for s in wanted], tasks, settings, args.run_name, args.concurrency))
    print(json.dumps(counts, ensure_ascii=False))
    return 0


def cmd_import_runs(args: argparse.Namespace) -> int:
    n = 0
    for rec in read_models(args.file, RunRecord):
        rec.runner = "external"
        append_jsonl(RESULTS_DIR / args.run_name / "runs" / f"{rec.system_id}.jsonl", rec)
        n += 1
    print(f"{n} kayıt eklendi")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    from .scoring.score_run import score_run
    from .tasks import load_tasks

    tasks = {t.id: t for t in load_tasks()}
    judge_client = None
    verifier = None
    if not args.no_judge:
        import anthropic

        judge_client = anthropic.AsyncAnthropic(max_retries=4)
    if not args.no_verify:
        from .official.bedesten import BedestenVerifier

        verifier = BedestenVerifier()
    out = asyncio.run(score_run(args.run_name, tasks, judge_client, args.judge_model, verifier))
    print(f"Puanlar: {out}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from .report.leaderboard import write_report
    from .systems import load_system_configs
    from .tasks import load_tasks

    tasks = {t.id: t for t in load_tasks()}
    labels = {sid: c.label for sid, c in load_system_configs().items()}
    md, js = write_report(args.run_name, tasks, labels)
    print(md.read_text(encoding="utf-8"))
    print(f"\nRapor: {md}\nJSON: {js}")
    return 0


def main(argv: list[str] | None = None) -> int:
    from dotenv import load_dotenv

    load_dotenv()
    p = argparse.ArgumentParser(prog="legaluga_bench", description="Legaluga Law Benchmark")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("systems", help="sistemleri listele")
    s.add_argument("--probe", action="store_true", help="MCP sunucularına bağlanıp araçları listele")
    s.set_defaults(fn=cmd_systems)

    s = sub.add_parser("tasks", help="görev özetini göster")
    s.add_argument("--tracks")
    s.add_argument("--split", choices=["dev", "test"])
    s.set_defaults(fn=cmd_tasks)

    s = sub.add_parser("build-exams", help="ÖSYM sorularından sınav görevlerini üret")
    s.set_defaults(fn=cmd_build_exams)

    s = sub.add_parser("run", help="benchmark koşusu")
    s.add_argument("--run-name", required=True)
    s.add_argument("--systems", help="virgülle ayrılmış sistem kimlikleri (varsayılan: hepsi)")
    s.add_argument("--tracks", help=f"virgülle ayrılmış: {','.join(TRACKS)}")
    s.add_argument("--split", choices=["dev", "test"])
    s.add_argument("--limit", type=int, help="track başına en çok görev (sabit tohumla örneklem)")
    s.add_argument("--seed", type=int, default=2026)
    s.add_argument("--model", default=os.environ.get("LBENCH_AGENT_MODEL"),
                   help="ajan modeli (Anthropic model kimliği); varsayılan LBENCH_AGENT_MODEL")
    s.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    s.add_argument("--max-tool-calls", type=int, default=20)
    s.add_argument("--max-turns", type=int, default=16)
    s.add_argument("--concurrency", type=int, default=4)
    s.add_argument("--today", help="istemdeki 'bugünün tarihi' (GG.AA.YYYY); tekrarlanabilirlik için sabitleyin")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("import-runs", help="harici koşu kayıtlarını ekle")
    s.add_argument("--run-name", required=True)
    s.add_argument("--file", required=True, type=lambda x: __import__("pathlib").Path(x))
    s.set_defaults(fn=cmd_import_runs)

    s = sub.add_parser("score", help="koşuyu puanla")
    s.add_argument("--run-name", required=True)
    s.add_argument("--judge-model")
    s.add_argument("--no-judge", action="store_true", help="açık araştırma görevlerini puanlama")
    s.add_argument("--no-verify", action="store_true", help="atıfları resmî kaynakta doğrulama")
    s.set_defaults(fn=cmd_score)

    s = sub.add_parser("report", help="rapor üret")
    s.add_argument("--run-name", required=True)
    s.set_defaults(fn=cmd_report)

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return args.fn(args)
