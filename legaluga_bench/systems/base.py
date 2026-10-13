"""Test edilen sistemlerin (araç sağlayıcıların) ortak arayüzü.

Bir "sistem", ajana sunulan araç kümesidir: Legaluga MCP, Yargı MCP, Legal Data
Hunter, genel web araması ya da hiç araç olmaması (kapalı kitap). Ajan modeli,
istem ve bütçe bütün sistemlerde aynıdır; değişen yalnız araçlardır.
"""

from __future__ import annotations

import fnmatch
import os
import re
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

# Adil karşılaştırma için her sistemin araç çıktısına aynı üst sınır uygulanır.
DEFAULT_RESULT_CHAR_LIMIT = 30_000


class SystemConfig(BaseModel):
    id: str
    label: str
    kind: str = Field(description="mcp_stdio | mcp_http | anthropic_web_search | composite | none")
    description: str = ""
    # mcp_stdio
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    # mcp_http
    url: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    # ortak
    include_tools: list[str] = Field(default_factory=list)
    exclude_tools: list[str] = Field(default_factory=list)
    max_concurrency: int = 4
    call_timeout_s: float = 120.0
    result_char_limit: int = DEFAULT_RESULT_CHAR_LIMIT
    # composite: üye sistem kimlikleri (aynı dosyada tanımlı)
    members: list[str] = Field(default_factory=list)
    # anthropic_web_search
    max_uses: int = 8
    allowed_domains: list[str] = Field(default_factory=list)


class ToolSpec(BaseModel):
    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})

    def to_anthropic(self) -> dict[str, Any]:
        schema = dict(self.input_schema or {})
        schema.setdefault("type", "object")
        return {"name": self.name, "description": self.description[:10_000], "input_schema": schema}


@dataclass
class ToolResult:
    text: str
    is_error: bool = False
    raw: Any = None
    truncated: bool = False


@dataclass
class ToolProvider:
    """Temel sınıf. Alt sınıflar `open`, `close`, `list_tools`, `call_tool` uygular."""

    config: SystemConfig
    tools: list[ToolSpec] = field(default_factory=list)

    @property
    def system_id(self) -> str:
        return self.config.id

    def server_tools(self) -> list[dict[str, Any]]:
        """Anthropic sunucu tarafı araçları (ör. web_search). Çoğu sistem için boş."""
        return []

    async def open(self) -> None:  # pragma: no cover - alt sınıflar
        return None

    async def close(self) -> None:  # pragma: no cover - alt sınıflar
        return None

    async def list_tools(self) -> list[ToolSpec]:
        return self.tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        raise NotImplementedError

    async def __aenter__(self) -> ToolProvider:
        await self.open()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    def tool_allowed(self, name: str) -> bool:
        inc, exc = self.config.include_tools, self.config.exclude_tools
        if inc and not any(fnmatch.fnmatchcase(name, p) for p in inc):
            return False
        return not any(fnmatch.fnmatchcase(name, p) for p in exc)

    def clip(self, text: str) -> tuple[str, bool]:
        limit = self.config.result_char_limit
        if len(text) <= limit:
            return text, False
        note = f"\n\n[... çıktı {len(text)} karakterden {limit} karaktere kısaltıldı ...]"
        return text[:limit] + note, True


_ENV_RE = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


class MissingEnvError(RuntimeError):
    pass


def expand_env(value: str) -> str:
    """`${VAR}` ve `${VAR:-varsayılan}` kalıplarını ortam değişkenleriyle doldurur."""

    def repl(m: re.Match[str]) -> str:
        name, default = m.group(1), m.group(2)
        val = os.environ.get(name)
        if val:
            return val
        if default is not None:
            return default
        raise MissingEnvError(f"Ortam değişkeni tanımlı değil: {name}")

    return _ENV_RE.sub(repl, value)
