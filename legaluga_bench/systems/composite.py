"""Birden çok MCP sunucusunu tek sistem olarak sunar (ör. Yargı MCP + Mevzuat MCP).

Bazı açık kaynak araçlar içtihat ve mevzuatı ayrı sunucularda verir; kullanıcılar bunları
birlikte bağlar. Adil karşılaştırma için bu birleşim tek bir sistem olarak ölçülür.
Araç adları çakışırsa ikinci sunucunun aracına `<üye>__` öneki eklenir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import ToolProvider, ToolResult, ToolSpec


@dataclass
class CompositeProvider(ToolProvider):
    members: list[ToolProvider] = field(default_factory=list)
    _route: dict[str, tuple[ToolProvider, str]] = field(default_factory=dict)

    async def open(self) -> None:
        opened: list[ToolProvider] = []
        try:
            for m in self.members:
                await m.open()
                opened.append(m)
        except BaseException:
            for m in reversed(opened):
                await m.close()
            raise
        self.tools = []
        for m in self.members:
            for t in await m.list_tools():
                name = t.name if t.name not in self._route else f"{m.system_id}__{t.name}"[:64]
                self._route[name] = (m, t.name)
                if self.tool_allowed(name):
                    self.tools.append(ToolSpec(name=name, description=t.description, input_schema=t.input_schema))

    async def close(self) -> None:
        for m in reversed(self.members):
            await m.close()

    def server_tools(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for m in self.members:
            out.extend(m.server_tools())
        return out

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        if name not in self._route or not any(t.name == name for t in self.tools):
            return ToolResult(text=f"Hata: '{name}' bu sistemde tanımlı bir araç değil.", is_error=True)
        member, real_name = self._route[name]
        return await member.call_tool(real_name, arguments)

