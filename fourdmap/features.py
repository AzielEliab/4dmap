"""Cited public geographic features and subsurface entrances.

Coordinates are copied from the bundled catalogs. This module does not
invent a location, a passage, or an era name.
"""

from __future__ import annotations

import json
from pathlib import Path

GEO = Path(__file__).resolve().parent / "static" / "geo"
EMPTY_SUBSURFACE = "no public subsurface map here."
NO_ERA_NAME = "modern catalog name; no era name in source."
NO_PLATE = "no public survey plate in this package."
NO_FEATURE = "No public feature of that type is in this catalog."
SUB_TYPES = ("cave", "cavern", "tunnel", "mine")


def _load(name: str) -> dict:
    return json.loads((GEO / name).read_text(encoding="utf-8"))


def _year(value) -> int:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())[:4]
    return int(digits) if digits else 1914


def _wanted(types) -> set[str] | None:
    if types is None:
        return None
    if isinstance(types, str):
        items = [part.strip() for part in types.split(",") if part.strip()]
    else:
        items = [str(part).strip() for part in types if str(part).strip()]
    return set(items) if items else None


def era_note(row: dict, year) -> str:
    """Plain era sentence. Dated names are used only when the catalog stored them."""
    wanted = _year(year)
    source = (row.get("source") or "public catalog").rstrip(".")
    extra = (row.get("place_note") or "").strip()
    dated = row.get("era_names") if isinstance(row.get("era_names"), dict) else {}
    if str(wanted) in dated and dated[str(wanted)]:
        text = f"{dated[str(wanted)]}. Source: {source}."
    elif row.get("group") == "subsurface":
        survey = row.get("survey_year")
        prop = row.get("survey_property") or "source date"
        if survey:
            text = (
                f"Survey year {survey} ({prop}). "
                f"This is not a {wanted} survey plate. {NO_PLATE} Source: {source}."
            )
        else:
            text = f"no survey year in source. This is not a {wanted} survey plate. {NO_PLATE} Source: {source}."
    else:
        text = f"{NO_ERA_NAME} Source: {source}."
        if row.get("record_year") and row.get("record_property"):
            text = f"Catalog record year {row['record_year']} ({row['record_property']}). {text}"
    if extra:
        text = f"{extra} {text}"
    return text


def _public(row: dict, year) -> dict:
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "type": row.get("type"),
        "lat": row.get("lat"),
        "lon": row.get("lon"),
        "line": row.get("line"),
        "source": row.get("source"),
        "source_url": row.get("source_url") or "",
        "aliases": row.get("aliases") or [],
        "era_note": era_note(row, year),
        "group": row.get("group") or "feature",
    }


def list_features(year=1914, types=None) -> dict:
    wanted = _year(year)
    chosen = _wanted(types)
    rows = _load("features.json").get("features") or []
    if chosen is not None:
        rows = [row for row in rows if row.get("type") in chosen]
    public = [_public(row, wanted) for row in rows]
    return {
        "ok": True,
        "year": wanted,
        "features": public,
        "n": len(public),
        "message": "" if public else NO_FEATURE,
        "note": NO_ERA_NAME,
    }


def list_subsurface(year=1914, types=None, lat=None, lon=None, radius: float = 3.0) -> dict:
    wanted = _year(year)
    chosen = _wanted(types)
    rows = _load("subsurface.json").get("features") or []
    if chosen is not None:
        known = set(SUB_TYPES)
        if chosen == {"other"}:
            rows = [row for row in rows if row.get("type") not in known]
        else:
            rows = [
                row for row in rows
                if row.get("type") in chosen or ("other" in chosen and row.get("type") not in known)
            ]
    if lat is not None and lon is not None:
        rows = [
            row for row in rows
            if row.get("lat") is not None and row.get("lon") is not None
            and abs(float(row["lat"]) - float(lat)) <= radius
            and abs(float(row["lon"]) - float(lon)) <= radius
        ]
    public = [_public(row, wanted) for row in rows]
    return {
        "ok": True,
        "year": wanted,
        "features": public,
        "n": len(public),
        "message": "" if public else EMPTY_SUBSURFACE,
    }
