"""Loopback-only 4DMap workbench. Binds 127.0.0.1. No telemetry."""

from __future__ import annotations

import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .card import CardError
from .chainfile import load_cards, save_cards
from .layers import fetch_satellite, lidar_lookup, street_lookup
from .ops import dispatch
from .scope import AUTHOR, DEFAULT_PORT, LIVE_OPS, LOOPBACK, __version__
from .shadowlinks import load_shadow_links
from .uploads import list_uploads, log_upload

STATIC = Path(__file__).resolve().parent / "static"
_STATIC_TYPES = {
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".geojson": "application/geo+json; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".txt": "text/plain; charset=utf-8",
}


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

        def _json(self, status: int, result: dict) -> None:
            self._send(status, json.dumps(result, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def _static_file(self, path: str) -> None:
            rel = path[len("/static/") :]
            if not rel or ".." in rel.split("/"):
                self._send(404, b'{"error":"not found"}', "application/json; charset=utf-8")
                return
            root = STATIC.resolve()
            file = (root / rel).resolve()
            if not str(file).startswith(str(root)) or not file.is_file():
                self._send(404, b'{"error":"not found"}', "application/json; charset=utf-8")
                return
            ctype = _STATIC_TYPES.get(file.suffix.lower(), "application/octet-stream")
            self._send(200, file.read_bytes(), ctype)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            if path in {"/", "/index.html"}:
                html = (STATIC / "index.html").read_bytes()
                self._send(200, html, "text/html; charset=utf-8")
                return
            if path.startswith("/static/"):
                self._static_file(path)
                return
            if path == "/v1/shadow_links":
                result = load_shadow_links()
                status = 200 if result.get("ok") else 400
                self._json(status, result)
                return
            if path == "/v1/uploads":
                try:
                    rows = list_uploads()
                except CardError as err:
                    self._json(400, err.as_dict())
                    return
                self._json(200, {"ok": True, "op": "uploads", "uploads": rows, "n": len(rows)})
                return
            if path == "/v1/tiles/satellite":
                fetched = fetch_satellite()
                if not fetched.get("available"):
                    fetched.pop("body", None)
                    self._json(502, fetched)
                    return
                self._send(200, fetched["body"], fetched.get("content_type") or "image/jpeg")
                return
            if path in {"/v1/tiles/street", "/v1/tiles/lidar"}:
                qs = parse_qs(parsed.query)
                try:
                    lat = float((qs.get("lat") or [""])[0])
                    lon = float((qs.get("lon") or [""])[0])
                except ValueError:
                    message = "not available here" if path.endswith("street") else "no LiDAR here"
                    self._json(200, {"ok": True, "available": False, "message": message, "reason": "A pin anchor is required."})
                    return
                result = street_lookup(lat, lon) if path.endswith("street") else lidar_lookup(lat, lon)
                self._json(200, result)
                return
            if path == "/v1/health":
                payload = {
                    "ok": True,
                    "product": "4dmap",
                    "version": __version__,
                    "author": AUTHOR,
                    "loopback": True,
                    "ops": list(LIVE_OPS),
                    "domains_are_doors": False,
                    "role": "inspection",
                }
                self._json(200, payload)
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
            if not isinstance(body, dict):
                self._send(400, b'{"error":"JSON object required"}', "application/json")
                return
            if path == "/v1/upload":
                self._upload(body)
                return
            if not path.startswith("/v1/"):
                self._send(404, b'{"error":"not found"}', "application/json")
                return
            op = path[4:].strip("/")
            explicit = "cards" in body and body.get("cards") is not None
            try:
                cards = body.get("cards") if explicit else load_cards()
                if cards is None:
                    cards = []
                result = dispatch(op, body.get("payload") or body, cards)
                if not explicit:
                    merged = list(cards)
                    seen = {card.get("h") for card in merged}
                    fresh = result.get("card")
                    if isinstance(fresh, dict) and fresh.get("h") not in seen:
                        merged.append(fresh)
                        seen.add(fresh.get("h"))
                    if op == "card_import":
                        for card in result.get("cards") or []:
                            if isinstance(card, dict) and card.get("h") not in seen:
                                merged.append(card)
                                seen.add(card.get("h"))
                    path_written = save_cards(merged)
                    result["cards_out"] = merged
                    result["lattice_file"] = str(path_written)
                self._json(200, result)
            except CardError as err:
                self._json(400, err.as_dict())

        def _upload(self, body: dict) -> None:
            encoded = body.get("content_b64") or ""
            try:
                content = base64.b64decode(str(encoded), validate=True)
            except (ValueError, TypeError):
                self._json(400, {"ok": False, "refused": True, "code": "UPLOAD_REFUSE", "message": "upload content_b64 is not base64"})
                return
            try:
                entry = log_upload(str(body.get("name") or "upload"), content)
            except CardError as err:
                self._json(400, err.as_dict())
                return
            self._json(200, {"ok": True, "op": "upload", "upload": entry})

    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = LOOPBACK, port: int = DEFAULT_PORT) -> None:
    httpd = make_server(host=host, port=port)
    print(f"Open http://{host}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
