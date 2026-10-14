"""Uzak MCP sunucuları için OAuth 2.1 (dinamik istemci kaydı + PKCE) desteği.

Legaluga, Yargı PRO ve Legal Data Hunter statik anahtar yerine OAuth kullanır. İlk seferde
`python -m legaluga_bench login --system <id>` tarayıcıda bir kez giriş yaptırır; belirteçler
depo dışında (~/.config/legaluga-bench/oauth/<id>.json, yalnız kullanıcı okuyabilir) saklanır ve
sonraki koşular yenileme belirteciyle etkileşimsiz çalışır. Yenileme belirteçleri dönebileceği
için aynı dosyayı paralel süreçler paylaşmamalıdır.
"""

from __future__ import annotations

import asyncio
import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

TOKEN_DIR = Path(os.environ.get("LBENCH_OAUTH_DIR", Path.home() / ".config" / "legaluga-bench" / "oauth"))
CALLBACK_PORT = int(os.environ.get("LBENCH_OAUTH_PORT", "8765"))


class InteractiveLoginRequired(RuntimeError):
    pass


class FileTokenStorage:
    """mcp.client.auth.TokenStorage arayüzü; belirteçleri tek bir JSON dosyasında tutar."""

    def __init__(self, system_id: str) -> None:
        self.path = TOKEN_DIR / f"{system_id}.json"

    def _load(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data), encoding="utf-8")
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.path)

    async def get_tokens(self) -> Any:
        from mcp.shared.auth import OAuthToken

        t = self._load().get("tokens")
        return OAuthToken(**t) if t else None

    async def set_tokens(self, tokens: Any) -> None:
        data = self._load()
        data["tokens"] = tokens.model_dump(mode="json")
        self._save(data)

    async def get_client_info(self) -> Any:
        from mcp.shared.auth import OAuthClientInformationFull

        c = self._load().get("client")
        return OAuthClientInformationFull(**c) if c else None

    async def set_client_info(self, info: Any) -> None:
        data = self._load()
        data["client"] = info.model_dump(mode="json")
        self._save(data)


def make_oauth_provider(system_id: str, server_url: str, scope: str | None, interactive: bool) -> Any:
    from mcp.client.auth import OAuthClientProvider
    from mcp.shared.auth import OAuthClientMetadata

    redirect_uri = f"http://127.0.0.1:{CALLBACK_PORT}/callback"

    async def redirect_handler(url: str) -> None:
        if not interactive:
            raise InteractiveLoginRequired(
                f"{system_id}: OAuth girişi gerekli. Önce `python -m legaluga_bench login --system {system_id}` çalıştırın."
            )
        print(f"\nTarayıcıda açın ve giriş yapın:\n{url}\n", flush=True)
        webbrowser.open(url)

    async def callback_handler() -> tuple[str, str | None]:
        box: dict[str, str | None] = {}

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - http.server arayüzü
                q = parse_qs(urlparse(self.path).query)
                box["code"] = (q.get("code") or [None])[0]
                box["state"] = (q.get("state") or [None])[0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Giriş tamamlandı, bu sekmeyi kapatabilirsiniz.".encode())

            def log_message(self, *args: Any) -> None:
                return None

        server = HTTPServer(("127.0.0.1", CALLBACK_PORT), Handler)
        try:
            await asyncio.to_thread(server.handle_request)
        finally:
            server.server_close()
        if not box.get("code"):
            raise RuntimeError("OAuth geri dönüşünde yetki kodu yok")
        return box["code"], box.get("state")

    metadata = OAuthClientMetadata(
        client_name="legaluga-law-benchmark",
        redirect_uris=[redirect_uri],
        grant_types=["authorization_code", "refresh_token"],
        response_types=["code"],
        token_endpoint_auth_method="none",
        scope=scope,
    )
    return OAuthClientProvider(
        server_url=server_url,
        client_metadata=metadata,
        storage=FileTokenStorage(system_id),
        redirect_handler=redirect_handler,
        callback_handler=callback_handler,
    )
