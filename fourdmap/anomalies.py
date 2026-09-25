"""Cited geographic anomaly outlines. No lore and no invented zones.

A dated public extent is used when the catalog has one. Otherwise the
modern cited outline stays, and the note says so.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
from pathlib import Path

from .earth import BUNDLED_ERAS

GEO = Path(__file__).resolve().parent / "static" / "geo"
EMPTY = "no public anomaly outline here."
NO_ERA_OUTLINE = "modern cited outline; no era outline in source."


def _year(value) -> int:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())[:4]
    return int(digits) if digits else 1914


def _bucket(year: int) -> int:
    return min(BUNDLED_ERAS, key=lambda item: abs(item - year))


def _wanted(types) -> set[str] | None:
    if types is None:
        return None
    if isinstance(types, str):
        items = [part.strip() for part in types.split(",") if part.strip()]
    else:
        items = [str(part).strip() for part in types if str(part).strip()]
    return set(items) if items else None


def outline_for(row: dict, year) -> tuple[dict, str]:
    """Prefer a stored public extent. Never invent a past outline."""
    wanted = _year(year)
    merged = dict(row)
    dated = row.get("era_names") if isinstance(row.get("era_names"), dict) else {}
    bucket = str(_bucket(wanted))
    if dated.get(bucket):
        merged["name"] = dated[bucket]
    elif dated.get(str(wanted)):
        merged["name"] = dated[str(wanted)]
    extents = [item for item in (row.get("extents") or []) if isinstance(item, dict) and item.get("year")]
    if not extents:
        return merged, NO_ERA_OUTLINE
    ranked = sorted(
        extents,
        key=lambda item: (0 if int(item["year"]) <= wanted else 1, abs(int(item["year"]) - wanted)),
    )
    chosen = ranked[0]
    for key in ("lat", "lon", "ring", "name"):
        if chosen.get(key) not in (None, "", []):
            merged[key] = chosen[key]
    source = (chosen.get("source") or row.get("source") or "public citation").rstrip(".")
    if int(chosen["year"]) == wanted:
        return merged, f"Public outline {chosen['year']}. Source: {source}"
    return merged, f"nearest public outline: {chosen['year']}. This is not a {wanted} outline. Source: {source}"


def _public(row: dict, year) -> dict:
    shaped, shape = outline_for(row, year)
    source = (shaped.get("source") or "public citation").rstrip(".")
    extra = (shaped.get("place_note") or "").strip()
    note = f"{extra} {shape} Source: {source}." if extra else f"{shape} Source: {source}."
    ring = shaped.get("ring") or []
    lat = shaped.get("lat")
    lon = shaped.get("lon")
    if ring:
        lon = sum(float(point[0]) for point in ring) / len(ring)
        lat = sum(float(point[1]) for point in ring) / len(ring)
    return {
        "id": row.get("id"),
        "name": shaped.get("name"),
        "catalog_name": row.get("name"),
        "type": row.get("type") or "aoi",
        "lat": lat,
        "lon": lon,
        "ring": shaped.get("ring") or [],
        "vertices": row.get("vertices") or [],
        "source": row.get("source"),
        "source_url": row.get("source_url") or "",
        "aliases": row.get("aliases") or [],
        "era_note": note.strip(),
        "group": "anomaly",
    }


def list_anomalies(year=1914, types=None) -> dict:
    wanted = _year(year)
    chosen = _wanted(types)
    try:
        rows = json.loads((GEO / "anomalies.json").read_text(encoding="utf-8")).get("features") or []
    except (OSError, json.JSONDecodeError):
        rows = []
    if chosen is not None:
        rows = [row for row in rows if row.get("type") in chosen]
    public = [_public(row, wanted) for row in rows]
    return {
        "ok": True,
        "year": wanted,
        "features": public,
        "n": len(public),
        "message": "" if public else EMPTY,
    }
