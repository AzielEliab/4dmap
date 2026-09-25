"""Approximate area for a pin. Never an exact point.

The shade combines place-word matching, a numeric spread, travel words,
and a local sun/moon/star check. It is an estimate, not proof.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from .card import CardError
from .sky import moon_alt_az, stars_in_text, sun_alt_az

GEO = Path(__file__).resolve().parent / "static" / "geo"
MIN_RADIUS_KM = 8.0
MAX_RADIUS_KM = 1800.0
EARTH_KM = 6371.0

_PHYSICS = (
    (
        re.compile(r"\b(sail|sailed|sailing|ship|voyage|steam|drift|current|afloat)\b", re.I),
        180.0,
        "The report talks about travel on water, so the area allows for drift. It is not a hull's position.",
    ),
    (
        re.compile(r"\b(march|marched|rode|walked|walking|drove|hours)\b", re.I),
        60.0,
        "The report talks about people moving, so the area allows for ground travel. It is not a footprint.",
    ),
    (
        re.compile(r"\b(shell|ballistic|artillery|impact|fell)\b", re.I),
        25.0,
        "The report uses impact language. The spread is a fall zone, not a surveyed crater.",
    ),
    (
        re.compile(r"\b(near|about|around|outside|toward|towards|somewhere)\b", re.I),
        50.0,
        "The wording is approximate, so the area stays wide of a point.",
    ),
)


def triad_view(
    hooks: dict[str, Any] | None,
    *,
    event: Any = None,
    clock: Any = None,
    lat: Any = None,
    lon: Any = None,
    gazetteer_id: Any = None,
) -> dict[str, Any]:
    """AKM 3-of-4 on one pin. Empty slots stay empty. Not a posterior."""
    del lon  # lon is only meaningful together with lat; the anchor check uses lat or a gazetteer id
    hooks = hooks or {}
    possibility = hooks.get("possibility")
    bayesian = hooks.get("bayesian")
    anchor = lat is not None or bool(str(gazetteer_id or "").strip())
    e_present = bool(str(event or "").strip() and str(clock or "").strip() and anchor)
    c_present = isinstance(possibility, dict) and possibility.get("value") is not None
    b_present = isinstance(bayesian, dict) and bayesian.get("value") is not None
    slots = [
        {
            "slot": "E",
            "name": "evidence",
            "present": e_present,
            "note": (
                "The pin has an event, a paper date, and an anchor."
                if e_present
                else "Evidence slot stays empty until the pin has an event, a paper date, and an anchor."
            ),
        },
        {
            "slot": "C",
            "name": "consistency",
            "present": c_present,
            "value": possibility.get("value") if c_present else None,
            "note": "Consistency here is the labeled possibility (time × place). It is not a posterior.",
        },
        {
            "slot": "P",
            "name": "prior",
            "present": False,
            "note": "No prior was cited on this pin.",
        },
        {
            "slot": "B",
            "name": "bayesian",
            "present": b_present,
            "value": bayesian.get("value") if b_present else None,
            "note": "A Bayesian value was cited." if b_present else "No Bayesian value was cited. This slot stays empty.",
        },
    ]
    filled = sum(1 for slot in slots if slot["present"])
    return {
        "spec": "AKM-TRIAD-1.0",
        "rule": "3-of-4",
        "slots": slots,
        "filled": filled,
        "met": filled >= 3,
        "posterior_is_truth": False,
        "possibility": possibility,
        "bayesian": bayesian,
        "collapsed": False,
        "note": "Possibility and Bayesian stay separate. Posterior ≠ truth. A triad score is not proof.",
    }


@lru_cache(maxsize=1)
def _places() -> list[dict[str, Any]]:
    path = GEO / "places.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("places") or [])


@lru_cache(maxsize=4)
def _era(year: int) -> dict[str, Any]:
    path = GEO / f"era-{year}.geojson"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _nearest_era(year: int | None) -> int:
    bundled = (1914, 1945, 1994, 2010)
    if year is None:
        return 2010
    return min(bundled, key=lambda item: abs(item - year))


def _parse_when(clock: str | None) -> tuple[datetime, bool]:
    text = str(clock or "").strip()
    if not text:
        raise CardError("CLOCK_REFUSE", "area estimate needs a paper date")
    date = text[:10]
    timed = "T" in text and len(text) >= 16
    try:
        if timed:
            when = datetime.fromisoformat(text.replace("Z", "+00:00"))
        else:
            when = datetime.fromisoformat(date + "T12:00:00+00:00")
    except ValueError as exc:
        raise CardError("CLOCK_REFUSE", "area estimate needs a paper date") from exc
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc), timed


def _match_place(text: str) -> dict[str, Any] | None:
    low = text.lower()
    best = None
    best_len = 0
    for place in _places():
        names = [place.get("name") or "", *(place.get("aliases") or [])]
        for name in names:
            token = str(name).strip().lower()
            if len(token) < 3:
                continue
            if re.search(rf"\b{re.escape(token)}\b", low) and len(token) > best_len:
                best = place
                best_len = len(token)
    return best


def _ring_span(coords: list) -> tuple[float, float, float, float] | None:
    lats: list[float] = []
    lons: list[float] = []

    def walk(node: Any) -> None:
        if isinstance(node, (list, tuple)) and node and isinstance(node[0], (int, float)):
            lons.append(float(node[0]))
            lats.append(float(node[1]))
            return
        if isinstance(node, list):
            for child in node:
                walk(child)

    walk(coords)
    if not lats:
        return None
    return min(lats), min(lons), max(lats), max(lons)


def _match_border(text: str, year: int) -> dict[str, Any] | None:
    data = _era(year)
    low = text.lower()
    best = None
    best_len = 0
    for feature in data.get("features") or []:
        name = str((feature.get("properties") or {}).get("NAME") or "").strip()
        if len(name) < 4:
            continue
        if re.search(rf"\b{re.escape(name.lower())}\b", low) and len(name) > best_len:
            span = _ring_span((feature.get("geometry") or {}).get("coordinates"))
            if not span:
                continue
            best = {"name": name, "span": span, "year": year}
            best_len = len(name)
    return best


def _destination(lat: float, lon: float, bearing: float, distance_km: float) -> tuple[float, float]:
    ang = distance_km / EARTH_KM
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    lat2 = math.asin(math.sin(lat1) * math.cos(ang) + math.cos(lat1) * math.sin(ang) * math.cos(bearing))
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(ang) * math.cos(lat1),
        math.cos(ang) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), (math.degrees(lon2) + 540) % 360 - 180


def _circle(lat: float, lon: float, radius_km: float, n: int = 72) -> list[dict[str, float]]:
    ring = []
    for i in range(n):
        lat2, lon2 = _destination(lat, lon, 2 * math.pi * i / n, radius_km)
        ring.append({"lat": round(lat2, 5), "lon": round(lon2, 5)})
    return ring


def _bbox_ring(span: tuple[float, float, float, float]) -> list[dict[str, float]]:
    south, west, north, east = span
    pad_lat = max(0.15, (north - south) * 0.08)
    pad_lon = max(0.15, (east - west) * 0.08)
    south -= pad_lat
    north += pad_lat
    west -= pad_lon
    east += pad_lon
    return [
        {"lat": round(south, 4), "lon": round(west, 4)},
        {"lat": round(south, 4), "lon": round(east, 4)},
        {"lat": round(north, 4), "lon": round(east, 4)},
        {"lat": round(north, 4), "lon": round(west, 4)},
    ]


def _precision_km(raw: Any) -> float:
    text = str(raw if raw is not None else "").strip()
    if not text or "." not in text:
        return 80.0
    decimals = len(text.split(".", 1)[1].rstrip("0"))
    if decimals <= 0:
        return 80.0
    return max(1.0, 111.0 / (10 ** min(decimals, 5)))


def estimate_area(payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = payload or {}
    try:
        lat = float(payload.get("lat"))
        lon = float(payload.get("lon"))
    except (TypeError, ValueError) as exc:
        raise CardError("ANCHOR_INCOMPLETE", "area estimate needs a reported latitude and longitude") from exc
    if not -90.0 <= lat <= 90.0 or not -180.0 <= lon <= 180.0:
        raise CardError("ANCHOR_REFUSE", "lat/lon are outside the globe")
    when, timed = _parse_when(str(payload.get("date") or payload.get("clock") or ""))
    event = str(payload.get("event") or "").strip()
    place = str(payload.get("place") or "").strip()
    text = " ".join(part for part in (event, place, str(payload.get("note") or "")) if part)
    year = payload.get("year")
    try:
        year_n = int(year) if year not in (None, "") else when.year
    except (TypeError, ValueError):
        year_n = when.year
    era = _nearest_era(year_n)

    parts: dict[str, str] = {}
    spreads: list[float] = []

    matched = _match_place(text)
    border = _match_border(text, era)
    if border:
        parts["linguistics"] = (
            f"The place words match {border['name']} on the {era} country file "
            "(source: aourednik/historical-basemaps, simplified). "
            "The shade covers that schematic border plus a margin. The file is not a survey."
        )
        south, west, north, east = border["span"]
        height = abs(north - south) * 111.0
        width = abs(east - west) * 111.0 * max(0.2, math.cos(math.radians(lat)))
        spreads.append(max(height, width) / 2)
    elif matched:
        parts["linguistics"] = (
            f"The place words match {matched['name']} in the local name list. "
            f"That name is about {int(matched['scale_km'])} km across, so the match is an area, not a doorstep."
        )
        spreads.append(float(matched["scale_km"]))
    elif place:
        parts["linguistics"] = (
            "Those place words are not in the local name list or the bundled borders. "
            "The area stays wide instead of inventing a town."
        )
        spreads.append(350.0)
    else:
        parts["linguistics"] = (
            "No place words were given. The shade uses the reported anchor and a minimum spread."
        )
        spreads.append(20.0)

    precise = max(_precision_km(payload.get("lat")), _precision_km(payload.get("lon")))
    spreads.append(precise)
    parts["math"] = (
        f"The reported digits support a spread of about {precise:.0f} km before the other checks. "
        "The final shade is the root of the summed squares, and it never shrinks below "
        f"{MIN_RADIUS_KM:.0f} km. A long decimal is still not a surveyed point."
    )

    physics_notes = []
    for pattern, extra, sentence in _PHYSICS:
        if pattern.search(text):
            spreads.append(extra)
            physics_notes.append(sentence)
    if physics_notes:
        parts["physics"] = " ".join(physics_notes)
    else:
        parts["physics"] = (
            "The report has no travel, drift, or impact words, so physics does not tighten the area."
        )

    sun = sun_alt_az(when, lat, lon)
    moon = moon_alt_az(when, lat, lon)
    named = stars_in_text(text, when, lat, lon)
    sky_bits = []
    if not timed:
        spreads.append(40.0)
        sky_bits.append(
            "The paper date has no clock time, so the sky is computed at 12:00 UTC. That hour is a stand-in, not the hour of the event."
        )
    low = text.lower()
    alt = sun["altitude_deg"]
    if re.search(r"\b(noon|midday)\b", low) and alt < 40:
        spreads.append(180.0)
        sky_bits.append(
            f"The wording says noon, but the sun is only about {alt:.0f}° up at this anchor. The area stays wide because the time of day and the place disagree."
        )
    elif re.search(r"\b(night|midnight)\b", low) and alt > 0:
        spreads.append(180.0)
        sky_bits.append(
            f"The wording says night, but the sun is still about {alt:.0f}° above the horizon here. The area stays wide."
        )
    elif re.search(r"\b(dawn|dusk|sunrise|sunset)\b", low):
        if -10 <= alt <= 12:
            sky_bits.append(
                f"Dawn or dusk fits this anchor: the sun is near the horizon ({alt:.0f}°). Horizon light covers the whole region, so it does not pick a point."
            )
        else:
            spreads.append(160.0)
            sky_bits.append(
                f"The wording says dawn or dusk, but the sun altitude here is about {alt:.0f}°. The area stays wide."
            )
    else:
        sky_bits.append(
            f"At the paper date the sun is about {alt:.0f}° above the horizon and the moon about {moon['altitude_deg']:.0f}°. "
            "That sky is the same across this whole region, so it does not pick a point."
        )
    for star in named:
        if star["altitude_deg"] < 0:
            spreads.append(200.0)
            sky_bits.append(
                f"{star['name'].title()} is below the horizon here, so a report that names it does not confirm this anchor."
            )
        else:
            sky_bits.append(
                f"{star['name'].title()} is about {star['altitude_deg']:.0f}° up. It is up across the whole shaded region, not at one point."
            )
    sky_bits.append("Star positions use a short J2000 list, not a full catalog.")
    parts["celestial"] = " ".join(sky_bits)

    radius = math.sqrt(sum(item * item for item in spreads))
    radius = max(MIN_RADIUS_KM, min(MAX_RADIUS_KM, radius))
    ring = _bbox_ring(border["span"]) if border else _circle(lat, lon, radius)
    why = " ".join(
        [
            parts["physics"],
            parts["linguistics"],
            parts["math"],
            parts["celestial"],
            f"The shaded radius used on the globe is about {radius:.0f} km around the reported anchor. This is an estimate, not proof, and not an exact point.",
        ]
    )
    return {
        "ok": True,
        "op": "area_estimate",
        "exact_point": False,
        "estimate": True,
        "proof": False,
        "truth": False,
        "courtroom_proof": False,
        "gis": False,
        "center": {
            "lat": lat,
            "lon": lon,
            "role": "reported anchor, not a surveyed point",
        },
        "radius_km": round(radius, 1),
        "ring": ring,
        "shape": "border" if border else "circle",
        "why": why,
        "parts": parts,
        "matched_place": None if not matched else matched.get("name"),
        "matched_border": None if not border else border.get("name"),
        "era_year": era,
        "era_requested": year_n,
        "era_exact": era == year_n,
        "era_source": "aourednik/historical-basemaps",
        "sky": {
            "sun_altitude_deg": round(sun["altitude_deg"], 1),
            "moon_altitude_deg": round(moon["altitude_deg"], 1),
            "timed": timed,
            "stars": named,
        },
    }
