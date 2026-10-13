"""configs/systems.yaml dosyasından sistem tanımlarını yükler."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..io import CONFIG_DIR
from .base import SystemConfig, ToolProvider
from .builtin import AnthropicWebSearchProvider, ClosedBookProvider
from .mcp_provider import MCPToolProvider

DEFAULT_SYSTEMS_FILE = CONFIG_DIR / "systems.yaml"


def load_system_configs(path: Path | None = None) -> dict[str, SystemConfig]:
    path = path or DEFAULT_SYSTEMS_FILE
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    systems = raw.get("systems", {})
    out: dict[str, SystemConfig] = {}
    for sid, body in systems.items():
        out[sid] = SystemConfig.model_validate({"id": sid, **(body or {})})
    return out


def make_provider(cfg: SystemConfig) -> ToolProvider:
    if cfg.kind in ("mcp_stdio", "mcp_http"):
        return MCPToolProvider(config=cfg)
    if cfg.kind == "anthropic_web_search":
        return AnthropicWebSearchProvider(config=cfg)
    if cfg.kind == "none":
        return ClosedBookProvider(config=cfg)
    raise ValueError(f"Bilinmeyen sistem türü: {cfg.kind} ({cfg.id})")
