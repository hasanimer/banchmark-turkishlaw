"""Puanlama + rapor üretimi uçtan uca (sentetik koşu kayıtlarıyla)."""

import importlib

from legaluga_bench.schema import RunRecord, Task, ToolCallLog


def test_grounding_and_report(tmp_path, monkeypatch):
    monkeypatch.setenv("LBENCH_RESULTS_DIR", str(tmp_path))
    import legaluga_bench.io as io_mod
    import legaluga_bench.report.leaderboard as lb
    import legaluga_bench.scoring.score_run as sr

    importlib.reload(io_mod)
    importlib.reload(sr)
    importlib.reload(lb)
    from legaluga_bench.agent.parse import parse_final_json
    from legaluga_bench.io import append_jsonl

    gold = {"court": "Yargıtay", "chamber": "3. Hukuk Dairesi", "esas": "2010/119", "karar": "2010/478"}
    tasks = {
        "c1": Task(id="c1", track="case_lookup", prompt="?", gold=gold, meta={"stratum": "yargitay_hukuk"}),
        **{f"e{i}": Task(id=f"e{i}", track="exam", prompt="?", options={k: k for k in "ABCDE"},
                         gold={"answer": "A"}, meta={"subject": "Borçlar Hukuku", "session": "HMGS 2025/1"})
           for i in range(6)},
    }
    answer = '```json\n{"decisions": [{"court": "Yargıtay", "chamber": "3. HD", "esas": "2010/119", "karar": "2010/478"}]}\n```'
    for sid, grounded in (("aracli", True), ("kapali", False)):
        calls = [ToolCallLog(name="karar_ara", numbers_seen=["2010/119", "2010/478"])] if grounded else []
        append_jsonl(tmp_path / "r" / "runs" / f"{sid}.jsonl", RunRecord(
            run_id=f"{sid}-c1", task_id="c1", track="case_lookup", system_id=sid, model="m", started_at="t",
            final_text=answer, parsed=parse_final_json(answer, "case_lookup"), tool_calls=calls,
            n_tool_calls=len(calls)))
        for i in range(6):
            choice = "A" if (sid == "aracli" or i < 2) else "B"
            text = f'{{"choice": "{choice}"}}'
            append_jsonl(tmp_path / "r" / "runs" / f"{sid}.jsonl", RunRecord(
                run_id=f"{sid}-e{i}", task_id=f"e{i}", track="exam", system_id=sid, model="m", started_at="t",
                final_text=text, parsed=parse_final_json(text, "exam")))

    import asyncio

    asyncio.run(sr.score_run("r", tasks))
    md, js = lb.write_report("r", tasks, {"aracli": "Araçlı", "kapali": "Kapalı"})
    rep = lb.build_report("r", tasks)
    rows = {r["system"]: r for r in rep["table"]}
    assert rows["aracli"]["grounding"] == 1.0 and rows["kapali"]["grounding"] is None
    assert rows["aracli"]["tracks"]["exam"]["mean"] == 1.0
    assert abs(rows["kapali"]["tracks"]["exam"]["mean"] - 2 / 6) < 1e-9
    pair = [p for p in rep["pairwise"] if p["track"] == "exam"][0]
    assert pair["mcnemar"]["only_a"] == 4
    text = md.read_text(encoding="utf-8")
    assert "Araçlı" in text and "Karar bulma: mahkemeye göre" in text
