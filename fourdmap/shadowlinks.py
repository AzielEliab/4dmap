"""Read the link file written by ShadowLock. Author: Aziel Eliab only.

ShadowLock is a separate Softwares. 4DMap only reads
``~/.shadowlock/links.json`` (format ``shadowlock-links-1``). See
``docs/SHADOWLOCK-LINKS.md``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

FORMAT = "shadowlock-links-1"
ENV_PATH = "SHADOWLOCK_LINKS"


def default_links_path() -> Path:
    return Path.home() / ".shadowlock" / "links.json"


def links_path(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get(ENV_PATH)
    if env:
        return Path(env).expanduser()
    return default_links_path()


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize(raw: Any) -> tuple[list[dict[str, str]], int]:
    if isinstance(raw, list):
        incoming = raw
    elif isinstance(raw, dict) and isinstance(raw.get("links"), list):
        incoming = raw["links"]
    else:
        raise ValueError("links")
    kept: list[dict[str, str]] = []
    skipped = 0
    for item in incoming:
        if not isinstance(item, dict):
            skipped += 1
            continue
        slug = _clean(item.get("slug"))
        input_id = _clean(item.get("input_id"))
        input_path = _clean(item.get("input_path"))
        if not slug or not (input_id or input_path):
            skipped += 1
            continue
        link: dict[str, str] = {"slug": slug}
        if input_id:
            link["input_id"] = input_id
        if input_path:
            link["input_path"] = input_path
        linked_at = _clean(item.get("linked_at"))
        if linked_at:
            link["linked_at"] = linked_at
        label = _clean(item.get("label"))
        if label:
            link["label"] = label
        kind = _clean(item.get("kind"))
        if kind:
            link["kind"] = kind
        kept.append(link)
    kept.sort(key=lambda link: (not link.get("linked_at"), link.get("linked_at") or "", link["slug"]))
    return kept, skipped


def load_shadow_links(explicit: str | None = None) -> dict[str, Any]:
    path = links_path(explicit)
    base: dict[str, Any] = {
        "ok": True,
        "op": "shadow_links",
        "format": FORMAT,
        "path": str(path),
        "found": path.is_file(),
        "n": 0,
        "skipped": 0,
        "links": [],
    }
    if not path.is_file():
        return base
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            **base,
            "ok": False,
            "code": "LINKS_JSON",
            "message": f"{path} is not JSON. Fix the ShadowLock link file, then try again.",
        }
    if isinstance(raw, dict):
        declared = _clean(raw.get("format"))
        if declared and declared != FORMAT:
            return {
                **base,
                "ok": False,
                "code": "LINKS_FORMAT",
                "message": f"{path} uses format {declared!r}. 4DMap reads {FORMAT}.",
            }
    try:
        links, skipped = _normalize(raw)
    except ValueError:
        return {
            **base,
            "ok": False,
            "code": "LINKS_SHAPE",
            "message": f"{path} needs a links array. See docs/SHADOWLOCK-LINKS.md, then try again.",
        }
    base["n"] = len(links)
    base["skipped"] = skipped
    base["links"] = links
    return base


def shadow_text(result: dict[str, Any]) -> str:
    if not result.get("ok"):
        message = str(result.get("message") or "The ShadowLock link file could not be read.")
        return f"{message}\nTry: 4dmap shadow --help\n"
    links = list(result.get("links") or [])
    path = str(result.get("path") or default_links_path())
    if not links:
        return (
            "No ShadowLock links yet.\n"
            "ShadowLock is a separate Softwares. Open ShadowLock to link a software.\n"
            f"4DMap only reads {path}.\n"
            "Next: open ShadowLock, then run 4dmap shadow\n"
        )
    lines = [
        f"ShadowLock links ({len(links)})",
        "ShadowLock is a separate Softwares. This list is read-only.",
    ]
    for link in links:
        when = link.get("linked_at") or "time not recorded"
        lines.append(f"  {when}")
        lines.append(f"    software   {link.get('slug')}")
        if link.get("label"):
            lines.append(f"    label      {link['label']}")
        if link.get("kind"):
            lines.append(f"    kind       {link['kind']}")
        if link.get("input_id"):
            lines.append(f"    input      {link['input_id']}")
        if link.get("input_path"):
            lines.append(f"    path       {link['input_path']}")
    skipped = int(result.get("skipped") or 0)
    if skipped:
        lines.append(f"Skipped {skipped} record(s) with no software slug or input.")
    lines.append("")
    lines.append("Next: 4dmap ui")
    return "\n".join(lines) + "\n"
