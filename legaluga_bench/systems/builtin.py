"""Araç gerektirmeyen baz çizgileri: kapalı kitap ve Anthropic sunucu tarafı web araması."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import ToolProvider, ToolResult

WEB_SEARCH_TOOL_TYPE = "web_search_20260209"


@dataclass
class ClosedBookProvider(ToolProvider):
    """Hiç araç yok: modelin kendi bilgisiyle cevap."""

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        return ToolResult(text="Bu sistemde araç yok.", is_error=True)


@dataclass
class AnthropicWebSearchProvider(ToolProvider):
    """Genel web araması baz çizgisi (Anthropic'in sunucu tarafı web_search aracı).

    Arama Anthropic altyapısında çalışır; istemci tarafında yürütülecek araç yoktur.
    """

    def server_tools(self) -> list[dict[str, Any]]:
        tool: dict[str, Any] = {
            "type": WEB_SEARCH_TOOL_TYPE,
            "name": "web_search",
            "max_uses": self.config.max_uses,
        }
        if self.config.allowed_domains:
            tool["allowed_domains"] = list(self.config.allowed_domains)
        return [tool]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        return ToolResult(text="web_search sunucu tarafında çalışır.", is_error=True)
