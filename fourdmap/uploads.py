"""Content-hashed upload log. Bytes stay under ~/.4dmap/uploads.

The lattice stores hashes the operator attaches to a pin.
The log stores the name, size, time, and SHA-256. Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .card import CardError

ENV_PATH = "FOURDMAP_UPLOADS"
MAX_BYTES = 8_000_000


def uploads_root() -> Path:
    override = os.environ.get(ENV_PATH)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".4dmap" / "uploads"


def _index_path() -> Path:
    return uploads_root() / "index.json"


def list_uploads() -> list[dict[str, Any]]:
    path = _index_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CardError("UPLOAD_JSON", f"{path} is not JSON.") from exc
    rows = data.get("uploads") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise CardError("UPLOAD_JSON", f"{path} is not an upload list.")
    return [row for row in rows if isinstance(row, dict)]


def log_upload(name: str, content: bytes) -> dict[str, Any]:
    if not isinstance(content, (bytes, bytearray)):
        raise CardError("UPLOAD_REFUSE", "upload body must be bytes")
    raw = bytes(content)
    if not raw:
        raise CardError("UPLOAD_REFUSE", "upload is empty")
    if len(raw) > MAX_BYTES:
        raise CardError("UPLOAD_REFUSE", f"upload is larger than {MAX_BYTES} bytes")
    label = Path(str(name or "upload")).name.strip() or "upload"
    if len(label) > 180:
        raise CardError("UPLOAD_REFUSE", "upload name is too long")
    digest = hashlib.sha256(raw).hexdigest()
    root = uploads_root()
    blob = root / "blobs" / digest
    root.joinpath("blobs").mkdir(parents=True, exist_ok=True)
    if not blob.is_file():
        blob.write_bytes(raw)
    rows = list_uploads()
    entry = {
        "name": label,
        "sha256": digest,
        "bytes": len(raw),
        "logged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stored": True,
    }
    rows.append(entry)
    _index_path().write_text(
        json.dumps({"format": "4dmap-uploads-1", "uploads": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    return entry
