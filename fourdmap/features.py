"""Cited public geographic features and subsurface entrances.

Coordinates are copied from the bundled catalogs. This module does not
invent a location, a passage, or an era name. A pin can tighten the
displayed disc only after enough independent receipts share that place
and era. The catalog point stays.
"""

from __future__ import annotations

import json
from pathlib import Path

from .earth import BUNDLED_ERAS
from .lattice import cites_pair, pin_frame_of
from .pattern import distance_km

GEO = Path(__file__).resolve().parent / "static" / "geo"
EMPTY_SUBSURFACE = "no public subsurface map here."
NO_ERA_NAME = "modern catalog name; no era name in source."
NO_EXTENT = "modern catalog shape; no historical extent in source"
CATALOG_ONLY = "catalog only; not enough pins to recalibrate."
NO_PLATE = "no public survey plate in this package."
NO_FEATURE = "No public feature of that type is in this catalog."
SUB_TYPES = ("cave", "cavern", "tunnel", "mine")
MATCH_KM = 80.0
MIN_PINS = 3
MIN_EVENTS = 2


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


def _era_bucket(year: int) -> int:
    return min(BUNDLED_ERAS, key=lambda item: abs(item - year))


def _clock_year(clock) -> int | None:
    digits = ""
    for ch in str(clock or ""):
        if ch.isdigit():
            digits += ch
            if len(digits) == 4:
                return int(digits)
        elif digits:
            digits = ""
    return None


def _shape_for(row: dict, year: int) -> tuple[dict, str]:
    """Use a stored public extent when the catalog has one. Otherwise keep the modern shape."""
    wanted = _year(year)
    extents = [item for item in (row.get("extents") or []) if isinstance(item, dict) and item.get("year")]
    merged = dict(row)
    dated = row.get("era_names") if isinstance(row.get("era_names"), dict) else {}
    bucket = str(_era_bucket(wanted))
    if dated.get(bucket):
        merged["name"] = dated[bucket]
    elif dated.get(str(wanted)):
        merged["name"] = dated[str(wanted)]
    if not extents:
        return merged, NO_EXTENT
    ranked = sorted(
        extents,
        key=lambda item: (0 if int(item["year"]) <= wanted else 1, abs(int(item["year"]) - wanted)),
    )
    chosen = ranked[0]
    for key in ("lat", "lon", "line", "name"):
        if chosen.get(key) not in (None, "", []):
            merged[key] = chosen[key]
    source = (chosen.get("source") or row.get("source") or "public catalog").rstrip(".")
    if int(chosen["year"]) == wanted:
        return merged, f"Public extent {chosen['year']}. Source: {source}"
    return merged, f"nearest public extent: {chosen['year']}. This is not a {wanted} extent. Source: {source}"


def _evidence(cards) -> list[dict]:
    pins = []
    for card in cards or []:
        if not isinstance(card, dict) or cites_pair(card):
            continue
        frame = pin_frame_of(card)
        if not isinstance(frame, dict):
            continue
        if frame.get("lat") is None and not frame.get("place"):
            continue
        pins.append(
            {
                "id": str(card.get("id") or ""),
                "event": str(frame.get("event") or ""),
                "place": str(frame.get("place") or ""),
                "clock": frame.get("clock") or "",
                "lat": frame.get("lat"),
                "lon": frame.get("lon"),
                "src": str(card.get("src") or ""),
                "note": str(card.get("note") or ""),
            }
        )
    return pins


def _catalog_names(row: dict) -> list[str]:
    names = [str(row.get("name") or "")]
    names.extend(str(item) for item in (row.get("aliases") or []))
    return [name for name in names if len(name) >= 4]


def _matches(row: dict, pins: list[dict], year: int) -> list[dict]:
    names = [name.casefold() for name in _catalog_names(row)]
    bucket = _era_bucket(_year(year))
    found = []
    for pin in pins:
        pin_year = _clock_year(pin.get("clock"))
        if pin_year is None or _era_bucket(pin_year) != bucket:
            continue
        blob = f"{pin.get('place') or ''} {pin.get('event') or ''}".casefold()
        named = any(name in blob for name in names)
        near = False
        if pin.get("lat") is not None and pin.get("lon") is not None and row.get("lat") is not None:
            near = distance_km(float(pin["lat"]), float(pin["lon"]), float(row["lat"]), float(row["lon"])) <= MATCH_KM
        if named or near:
            found.append(pin)
    return found


def _already(cards, key: str) -> bool:
    for card in cards or []:
        if isinstance(card, dict) and key in str(card.get("note") or ""):
            return True
    return False


def _recalibrate(row: dict, pins: list[dict], year: int, cards) -> dict:
    catalog_name = str(row.get("name") or "")
    matched = _matches(row, pins, year)
    events = sorted({pin["event"] for pin in matched if pin.get("event")})
    enough = len(matched) >= MIN_PINS and len(events) >= MIN_EVENTS
    label = catalog_name
    disc = None
    if enough:
        votes: dict[str, str] = {}
        for pin in matched:
            place = str(pin.get("place") or "").casefold()
            for name in _catalog_names(row):
                if name.casefold() in place:
                    votes[name.casefold()] = name
        if len(votes) == 1:
            label = next(iter(votes.values()))
        anchored = [pin for pin in matched if pin.get("lat") is not None and pin.get("lon") is not None]
        if len(anchored) >= 2 and row.get("lat") is not None:
            spread = max(
                distance_km(float(pin["lat"]), float(pin["lon"]), float(row["lat"]), float(row["lon"]))
                for pin in anchored
            )
            disc = {
                "lat": row["lat"],
                "lon": row["lon"],
                "radius_km": round(min(120.0, max(40.0, spread + 10.0)), 1),
            }
        why = (
            f"{len(matched)} pins in the {_era_bucket(_year(year))} era slice agree on this catalog place"
            f" ({', '.join(events)}). The disc is their spread around the catalog point, not a new feature. Posterior ≠ truth."
        )
        recal = f"recalibrated from {len(matched)} pins. {why} catalog: {catalog_name}."
        pin_ids = ",".join(sorted(pin["id"] for pin in matched if pin.get("id")))
        key = f"recalibrated · {row.get('id')} · {pin_ids}"
        receipt = f"recalibrated from {len(matched)} pins · {key} · {why} catalog: {catalog_name}. Posterior ≠ truth."
        return {
            "label": label,
            "recalibrated": True,
            "recal": recal,
            "disc": disc,
            "n": len(matched),
            "receipt_key": key,
            "receipt_note": receipt,
            "needs_receipt": not _already(cards, key),
        }
    return {
        "label": catalog_name,
        "recalibrated": False,
        "recal": CATALOG_ONLY,
        "disc": None,
        "n": len(matched),
        "receipt_key": "",
        "receipt_note": "",
        "needs_receipt": False,
    }


def era_note(row: dict, year, cards=None) -> str:
    """Shape, survey, and pin-evidence sentences for one catalog feature."""
    wanted = _year(year)
    shaped, shape = _shape_for(row, wanted)
    source = (shaped.get("source") or "public catalog").rstrip(".")
    extra = (shaped.get("place_note") or "").strip()
    evidence = _recalibrate(shaped, _evidence(cards), wanted, cards)
    if shaped.get("group") == "subsurface":
        survey = shaped.get("survey_year")
        prop = shaped.get("survey_property") or "source date"
        if survey:
            head = f"Survey year {survey} ({prop}). This is not a {wanted} survey plate. {NO_PLATE}"
        else:
            head = f"no survey year in source. This is not a {wanted} survey plate. {NO_PLATE}"
        text = f"{head} {shape}. {evidence['recal']}"
    else:
        text = f"{NO_ERA_NAME} Source: {source}. {shape}. {evidence['recal']}"
        if shaped.get("record_year") and shaped.get("record_property"):
            text = f"Catalog record year {shaped['record_year']} ({shaped['record_property']}). {text}"
    if extra:
        text = f"{extra} {text}"
    return text


def _public(row: dict, year, cards=None) -> dict:
    wanted = _year(year)
    shaped, _shape = _shape_for(row, wanted)
    evidence = _recalibrate(shaped, _evidence(cards), wanted, cards)
    return {
        "id": row.get("id"),
        "name": evidence["label"],
        "catalog_name": shaped.get("name"),
        "type": row.get("type"),
        "lat": shaped.get("lat"),
        "lon": shaped.get("lon"),
        "line": shaped.get("line"),
        "source": row.get("source"),
        "source_url": row.get("source_url") or "",
        "aliases": row.get("aliases") or [],
        "era_note": era_note(row, wanted, cards),
        "group": row.get("group") or "feature",
        "disc": evidence["disc"],
        "recalibrated": evidence["recalibrated"],
        "pin_count": evidence["n"],
        "needs_receipt": evidence["needs_receipt"],
        "receipt_note": evidence["receipt_note"],
        "receipt_key": evidence["receipt_key"],
    }


def list_features(year=1914, types=None, cards=None) -> dict:
    wanted = _year(year)
    chosen = _wanted(types)
    rows = _load("features.json").get("features") or []
    if chosen is not None:
        rows = [row for row in rows if row.get("type") in chosen]
    public = [_public(row, wanted, cards) for row in rows]
    return {
        "ok": True,
        "year": wanted,
        "features": public,
        "n": len(public),
        "message": "" if public else NO_FEATURE,
        "note": NO_ERA_NAME,
    }


def list_subsurface(year=1914, types=None, lat=None, lon=None, radius: float = 3.0, cards=None) -> dict:
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
    public = [_public(row, wanted, cards) for row in rows]
    return {
        "ok": True,
        "year": wanted,
        "features": public,
        "n": len(public),
        "message": "" if public else EMPTY_SUBSURFACE,
    }
