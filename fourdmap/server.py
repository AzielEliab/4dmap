"""Loopback-only 4DMap workbench. Binds 127.0.0.1. No telemetry."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .card import CardError
from .ops import dispatch
from .scope import AUTHOR, DEFAULT_PORT, LIVE_OPS, LOOPBACK, __version__

STATIC = Path(__file__).resolve().parent / "static"


def make_server(host: str = LOOPBACK, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    if host not in {"127.0.0.1", "localhost", LOOPBACK}:
        raise ValueError("4dmap ui binds loopback only")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:  # noqa: A003
            return

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "private, no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in {"/", "/index.html"}:
                html = (STATIC / "index.html").read_bytes()
                self._send(200, html, "text/html; charset=utf-8")
                return
            if path == "/v1/health":
                payload = json.dumps({
                    "ok": True,
                    "product": "4dmap",
                    "version": __version__,
                    "author": AUTHOR,
                    "loopback": True,
                    "ops": list(LIVE_OPS),
                    "domains_are_doors": False,
                    "role": "inspection",
                }).encode()
                self._send(200, payload, "application/json; charset=utf-8")
                return
            self._send(404, b'{"error":"not found"}', "application/json; charset=utf-8")

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send(400, b'{"error":"JSON body required"}', "application/json")
                return
            if not path.startswith("/v1/"):
                self._send(404, b'{"error":"not found"}', "application/json")
                return
            op = path[4:].strip("/")
            try:
                result = dispatch(op, body.get("payload") or body, body.get("cards"))
                out = json.dumps(result, ensure_ascii=False).encode("utf-8")
                self._send(200, out, "application/json; charset=utf-8")
            except CardError as err:
                out = json.dumps(err.as_dict(), ensure_ascii=False).encode("utf-8")
                self._send(400, out, "application/json; charset=utf-8")

    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = LOOPBACK, port: int = DEFAULT_PORT) -> None:
    httpd = make_server(host=host, port=port)
    print(f"Open http://{host}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
