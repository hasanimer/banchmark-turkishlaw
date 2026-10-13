"""Genel MCP istemcisi: stdio (yerel süreç) ya da Streamable HTTP (uzak sunucu).

Her sistemin araçları sunucunun kendi açıklamalarıyla ajana aktarılır; araç
açıklamalarının kalitesi de ürünün bir parçası sayılır.
"""

from __future__ import annotations

import asyncio
import json
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from .base import ToolProvider, ToolResult, ToolSpec, expand_env


def _content_to_text(result: Any) -> str:
    parts: list[str] = []
    for block in getattr(result, "content", None) or []:
        btype = getattr(block, "type", None)
        if btype == "text":
            parts.append(block.text)
        elif btype == "resource":
            res = getattr(block, "resource", None)
            text = getattr(res, "text", None)
            parts.append(text if text is not None else f"[kaynak: {getattr(res, 'uri', '')}]")
        elif btype == "image":
            parts.append("[görsel içerik]")
        else:
            parts.append(str(block))
    structured = getattr(result, "structuredContent", None)
    if not parts and structured is not None:
        parts.append(json.dumps(structured, ensure_ascii=False))
    return "\n".join(parts)


@dataclass
class MCPToolProvider(ToolProvider):
    _stack: AsyncExitStack | None = None
    _session: Any = None
    _sem: asyncio.Semaphore | None = None
    _all_tools: list[ToolSpec] = field(default_factory=list)

    async def open(self) -> None:
        from mcp import ClientSession

        cfg = self.config
        self._stack = AsyncExitStack()
        try:
            if cfg.kind == "mcp_stdio":
                from mcp import StdioServerParameters
                from mcp.client.stdio import stdio_client

                if not cfg.command:
                    raise ValueError(f"{cfg.id}: mcp_stdio için 'command' gerekli")
                params = StdioServerParameters(
                    command=expand_env(cfg.command),
                    args=[expand_env(a) for a in cfg.args],
                    env={k: expand_env(v) for k, v in cfg.env.items()} or None,
                )
                read, write = await self._stack.enter_async_context(stdio_client(params))
            elif cfg.kind == "mcp_http":
                from mcp.client.streamable_http import streamablehttp_client

                if not cfg.url:
                    raise ValueError(f"{cfg.id}: mcp_http için 'url' gerekli")
                headers = {k: expand_env(v) for k, v in cfg.headers.items()}
                read, write, _ = await self._stack.enter_async_context(
                    streamablehttp_client(
                        expand_env(cfg.url),
                        headers=headers or None,
                        timeout=30,
                        sse_read_timeout=cfg.call_timeout_s + 30,
                    )
                )
            else:
                raise ValueError(f"{cfg.id}: MCPToolProvider '{cfg.kind}' türünü desteklemez")

            self._session = await self._stack.enter_async_context(ClientSession(read, write))
            await self._session.initialize()
            listed = await self._session.list_tools()
            self._all_tools = [
                ToolSpec(name=t.name, description=t.description or "", input_schema=t.inputSchema or {})
                for t in listed.tools
            ]
            self.tools = [t for t in self._all_tools if self.tool_allowed(t.name)]
            self._sem = asyncio.Semaphore(max(1, cfg.max_concurrency))
        except BaseException:
            await self._stack.aclose()
            self._stack = None
            raise

    async def close(self) -> None:
        if self._stack is not None:
            await self._stack.aclose()
            self._stack = None
            self._session = None

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        if self._session is None or self._sem is None:
            raise RuntimeError(f"{self.system_id}: oturum açık değil")
        if not any(t.name == name for t in self.tools):
            return ToolResult(text=f"Hata: '{name}' bu sistemde tanımlı bir araç değil.", is_error=True)
        async with self._sem:
            try:
                result = await self._session.call_tool(
                    name,
                    arguments or {},
                    read_timeout_seconds=timedelta(seconds=self.config.call_timeout_s),
                )
            except Exception as e:  # noqa: BLE001 - araç hatası ajana iletilir
                return ToolResult(text=f"Hata: araç çağrısı başarısız ({type(e).__name__}: {e})", is_error=True)
            text, truncated = self.clip(_content_to_text(result))
            return ToolResult(text=text, is_error=bool(getattr(result, "isError", False)), truncated=truncated)
