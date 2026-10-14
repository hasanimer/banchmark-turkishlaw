"""Veri modelleri: görevler, sistem çıktıları ve puanlar.

Her görev (Task) tek bir JSON satırıdır. Track'e özgü altın cevap `gold`
alanında durur; ajanın görmediği bilgiler (kaynak, dayanak ipucu vb.) `meta`
alanındadır. Koşu kayıtları (RunRecord) ve puanlar (ScoreRecord) da JSONL
olarak saklanır; böylece her aşama ayrı ayrı yeniden üretilebilir.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Track = Literal["exam", "statute", "case_lookup", "citation_check", "research"]
TRACKS: tuple[str, ...] = ("exam", "statute", "case_lookup", "citation_check", "research")
OPTION_LETTERS: tuple[str, ...] = ("A", "B", "C", "D", "E")


class Task(BaseModel):
    """Benchmark'taki tek bir görev."""

    id: str
    track: Track
    split: Literal["dev", "test"] = "test"
    prompt: str = Field(description="Ajanın gördüğü soru/görev metni (Türkçe).")
    options: dict[str, str] | None = Field(
        default=None, description="Çoktan seçmeli sorularda A-E şıkları."
    )
    gold: dict[str, Any] = Field(
        default_factory=dict, description="Track'e özgü altın cevap; ajana gösterilmez."
    )
    meta: dict[str, Any] = Field(default_factory=dict)


class ToolCallLog(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    ok: bool = True
    error: str | None = None
    latency_s: float = 0.0
    result_chars: int = 0
    result_excerpt: str = ""
    # Araç çıktısında geçen YYYY/N numaraları (esas/karar/başvuru); dayanak (grounding) metriği için.
    numbers_seen: list[str] = Field(default_factory=list)


class RunRecord(BaseModel):
    """Bir sistemin bir göreve verdiği cevabın ham kaydı."""

    run_id: str
    task_id: str
    track: Track
    system_id: str
    model: str
    served_model: str | None = None
    runner: Literal["harness", "external"] = "harness"
    started_at: str
    latency_s: float = 0.0
    n_turns: int = 0
    n_tool_calls: int = 0
    tool_calls: list[ToolCallLog] = Field(default_factory=list)
    server_tool_uses: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    stop_reason: str | None = None
    final_text: str = ""
    parsed: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ScoreRecord(BaseModel):
    run_id: str
    task_id: str
    system_id: str
    track: Track
    score: float = Field(ge=0.0, le=1.0)
    correct: bool | None = None
    details: dict[str, Any] = Field(default_factory=dict)
