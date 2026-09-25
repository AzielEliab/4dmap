"""Era place names from the bundled basemap. No invented city names.

A country or region label is the NAME on the era GeoJSON that contains
the point. A city keeps the modern name in the local list, with a plain
note, unless that list has no dated era label. Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .earth import BUNDLED_ERAS
from .lattice import cites_pair, pin_frame_of
from .pattern import distance_km

GEO = Path(__file__).resolve().parent / "static" / "geo"
MODERN_YEAR = 2010
NO_ERA_LABEL = "modern name; no era label in source."
SOURCE = "aourednik/historical-basemaps"

_POLYS: dict[int, list[tuple[str, float, list]]] = {}
_CITIES: list[dict[str, Any]] | None = None


def _year(value: Any) -> int:
    text = str(value or "")
    digits = ""
    for ch in text:
        if ch.isdigit():
            digits += ch
            if len(digits) == 4:
                return int(digits)
        elif digits:
            break
    return min(BUNDLED_ERAS, key=lambda item: abs(item - 1914))


def bundled_year(value: Any) -> int:
    year = _year(value)
    return min(BUNDLED_ERAS, key=lambda item: abs(item - year))


def _ring_contains(ring: list, lon: float, lat: float) -> bool:
    inside = False
    if len(ring) < 3:
        return False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = float(ring[i][0]), float(ring[i][1])
        xj, yj = float(ring[j][0]), float(ring[j][1])
        if (yi > lat) != (yj > lat):
            denom = yj - yi
            if denom == 0:
                j = i
                continue
            cross = (xj - xi) * (lat - yi) / denom + xi
            if lon < cross:
                inside = not inside
        j = i
    return inside


def _polys_contain(polys: list, lon: float, lat: float) -> bool:
    for poly in polys:
        if not poly or not _ring_contains(poly[0], lon, lat):
            continue
        if any(_ring_contains(hole, lon, lat) for hole in poly[1:]):
            continue
        return True
    return False


def _bbox_area(polys: list) -> float:
    xs: list[float] = []
    ys: list[float] = []
    for poly in polys:
        if not poly:
            continue
        for point in poly[0]:
            xs.append(float(point[0]))
            ys.append(float(point[1]))
    if not xs:
        return 0.0
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def _polygons(year: int) -> list[tuple[str, float, list]]:
    if year in _POLYS:
        return _POLYS[year]
    path = GEO / f"era-{year}.geojson"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _POLYS[year] = []
        return _POLYS[year]
    rows = []
    for feature in data.get("features") or []:
        name = str((feature.get("properties") or {}).get("NAME") or "").strip()
        geom = feature.get("geometry") or {}
        kind = geom.get("type")
        coords = geom.get("coordinates") or []
        if kind == "Polygon":
            polys = [coords]
        elif kind == "MultiPolygon":
            polys = coords
        else:
            continue
        if not name:
            continue
        rows.append((name, _bbox_area(polys), polys))
    _POLYS[year] = rows
    return rows


def polygon_name(year: Any, lat: float, lon: float) -> str:
    best = ""
    best_area = None
    for name, area, polys in _polygons(bundled_year(year)):
        if not _polys_contain(polys, lon, lat):
            continue
        if best_area is None or area < best_area:
            best = name
            best_area = area
    return best


def _cities() -> list[dict[str, Any]]:
    global _CITIES
    if _CITIES is not None:
        return _CITIES
    try:
        data = json.loads((GEO / "places.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _CITIES = []
        return _CITIES
    _CITIES = list(data.get("places") or [])
    return _CITIES


def match_city(lat: float, lon: float, place_text: str = "") -> dict[str, Any] | None:
    text = str(place_text or "").casefold()
    cities = _cities()
    if text:
        best = None
        best_len = 0
        for city in cities:
            names = [city.get("name"), *(city.get("aliases") or [])]
            for name in names:
                token = str(name or "").strip()
                if len(token) < 4:
                    continue
                if token.casefold() in text and len(token) > best_len:
                    best = city
                    best_len = len(token)
        if best:
            return best
    nearest = None
    nearest_km = None
    for city in cities:
        try:
            km = distance_km(lat, lon, float(city["lat"]), float(city["lon"]))
        except (KeyError, TypeError, ValueError):
            continue
        limit = max(float(city.get("scale_km") or 40), 40)
        if km <= limit and (nearest_km is None or km < nearest_km):
            nearest = city
            nearest_km = km
    return nearest


def era_label(lat: Any, lon: Any, year: Any, place: str = "") -> dict[str, Any]:
    try:
        flat, flon = float(lat), float(lon)
    except (TypeError, ValueError):
        return {"ok": False, "message": "A latitude and longitude are required."}
    shown = bundled_year(year)
    era_name = polygon_name(shown, flat, flon)
    modern_name = polygon_name(MODERN_YEAR, flat, flon)
    city = match_city(flat, flon, place)
    city_name = str(city.get("name") or "") if city else ""
    aliases = [str(item) for item in (city.get("aliases") or [])] if city else []
    terms: list[str] = []
    for item in BUNDLED_ERAS:
        found = polygon_name(item, flat, flon)
        if found and found not in terms:
            terms.append(found)
    for token in (city_name, place, *aliases):
        text = str(token or "").strip()
        if text and text not in terms:
            terms.append(text)
    lines: list[str] = []
    if era_name:
        lines.append(era_name)
    elif str(place or "").strip():
        lines.append(str(place).strip())
    if modern_name and modern_name != era_name:
        lines.append(f"Modern name: {modern_name}")
    if city_name and city_name != era_name:
        city_line = f"{city_name}. {NO_ERA_LABEL}"
        if lines and lines[0] == city_name:
            lines[0] = city_line
        else:
            lines.append(city_line)
    return {
        "ok": True,
        "year": shown,
        "era_name": era_name,
        "modern_name": modern_name,
        "modern_year": MODERN_YEAR,
        "city": city_name,
        "city_era": None,
        "city_note": NO_ERA_LABEL if city_name else "",
        "source": SOURCE,
        "place_line": "\n".join(lines),
        "terms": terms,
        "invented": False,
    }


def label_cards(cards: list[dict[str, Any]] | None, year: Any) -> list[dict[str, Any]]:
    rows = []
    for card in cards or []:
        if cites_pair(card):
            continue
        frame = pin_frame_of(card) or {}
        if frame.get("lat") is None or frame.get("lon") is None:
            continue
        row = era_label(frame.get("lat"), frame.get("lon"), year, str(frame.get("place") or ""))
        row["id"] = card.get("id")
        rows.append(row)
    return rows
