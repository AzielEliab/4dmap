"""Pattern matrix on the existing lattice. No second chain.

A tether exists only when pins share a person, place, or cause,
or a receipt already joins them, or they name the same ShadowLock input.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import math
from typing import Any

from .lattice import cites_pair, pin_frame_of


def _year(clock: Any) -> int | None:
    text = str(clock or "")
    digits = ""
    for ch in text:
        if ch.isdigit():
            digits += ch
            if len(digits) == 4:
                return int(digits)
        elif digits:
            digits = ""
    return None


def _days(clock: Any) -> int | None:
    text = str(clock or "")[:10]
    parts = text.split("-")
    if len(parts) < 3:
        year = _year(clock)
        return year * 365 if year else None
    try:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None
    return year * 365 + month * 30 + day


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(a)))


def plain_distance(km: float) -> str:
    if km < 1:
        return "under 1 km apart"
    rounded = int(round(km))
    if rounded >= 1000:
        text = f"{rounded:,}"
    else:
        text = str(rounded)
    return f"about {text} km apart"


def plain_delta(earlier: Any, later: Any) -> str:
    a, b = _days(earlier), _days(later)
    if a is None or b is None:
        return "the time gap is not on the pins"
    delta = b - a
    if abs(delta) < 2:
        return "the same day"
    sign = "later" if delta > 0 else "earlier"
    span = abs(delta)
    if span < 50:
        return f"about {span} days {sign}"
    if span < 540:
        return f"about {max(1, round(span / 30))} months {sign}"
    return f"about {max(1, round(span / 365))} years {sign}"


def _people(frame: dict[str, Any]) -> set[str]:
    who = frame.get("who") or []
    if isinstance(who, str):
        who = [who]
    return {str(part).strip().casefold() for part in who if str(part).strip()}


def _place_words(frame: dict[str, Any]) -> set[str]:
    text = str(frame.get("place") or "").casefold()
    words = []
    token = ""
    for ch in text:
        if ch.isalpha() or ch == "'":
            token += ch
        elif token:
            if len(token) >= 4:
                words.append(token)
            token = ""
    if token and len(token) >= 4:
        words.append(token)
    skip = {"near", "from", "with", "this", "that", "harbor", "harbour"}
    return {word for word in words if word not in skip}


def _cause(frame: dict[str, Any]) -> str:
    return str(frame.get("cause") or "").strip().casefold()


def _pins(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for card in cards or []:
        if cites_pair(card):
            continue
        frame = pin_frame_of(card) or {}
        if frame.get("lat") is None or frame.get("lon") is None:
            continue
        rows.append(
            {
                "id": card.get("id"),
                "event": frame.get("event") or card.get("id"),
                "clock": frame.get("clock"),
                "lat": float(frame["lat"]),
                "lon": float(frame["lon"]),
                "place": frame.get("place") or "",
                "who": frame.get("who") or [],
                "cause": frame.get("cause") or "",
                "people": _people(frame),
                "places": _place_words(frame),
                "cause_key": _cause(frame),
            }
        )
    return rows


def _edge(a: dict[str, Any], b: dict[str, Any], reason: str) -> dict[str, Any]:
    km = distance_km(a["lat"], a["lon"], b["lat"], b["lon"])
    first, second = (a, b) if (_days(a["clock"]) or 0) <= (_days(b["clock"]) or 0) else (b, a)
    delta = plain_delta(first["clock"], second["clock"])
    return {
        "from": a["id"],
        "to": b["id"],
        "from_event": a["event"],
        "to_event": b["event"],
        "from_lat": a["lat"],
        "from_lon": a["lon"],
        "to_lat": b["lat"],
        "to_lon": b["lon"],
        "reason": reason,
        "delta": delta,
        "distance": plain_distance(km),
        "km": round(km, 1),
    }


def _join_ids(card: dict[str, Any]) -> tuple[str, str] | None:
    for field in ("delta", "gamma", "pi"):
        body = card.get(field)
        if isinstance(body, dict) and body.get("left") and body.get("right"):
            return str(body["left"]), str(body["right"])
    return None


def _shadow_ids(link: dict[str, Any]) -> set[str]:
    found = set()
    for key in ("input_id", "slug", "label"):
        text = str(link.get(key) or "").strip()
        if len(text) >= 4:
            found.add(text.casefold())
    return found


def pattern_matrix(cards: list[dict[str, Any]] | None, shadow_links: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Read tethers off the lattice. A prev-hash alone is not a tether.

    Reasons keep the strongest plain label. An explicit "why tethered"
    note on a join outranks a shared person, place, or cause.
    """
    pins = _pins(cards or [])
    by_id = {pin["id"]: pin for pin in pins}
    chosen: dict[tuple[str, str], tuple[int, str]] = {}
    written: set[tuple[str, str]] = set()

    def consider(a: dict[str, Any] | None, b: dict[str, Any] | None, reason: str, rank: int, on_lattice: bool = False) -> None:
        if not a or not b:
            return
        key = tuple(sorted((str(a["id"]), str(b["id"]))))
        if key[0] == key[1]:
            return
        prev = chosen.get(key)
        if prev is None or rank < prev[0]:
            chosen[key] = (rank, reason)
        if on_lattice:
            written.add(key)

    for i, left in enumerate(pins):
        for right in pins[i + 1 :]:
            shared = sorted(left["people"] & right["people"])
            if shared:
                label = shared[0]
                pretty = next((str(p) for p in (left["who"] or []) if str(p).casefold() == label), label)
                consider(left, right, f"shared person {pretty}", 2)
            places = sorted(left["places"] & right["places"])
            if places:
                consider(left, right, f"shared place {places[0]}", 3)
            if left["cause_key"] and left["cause_key"] == right["cause_key"]:
                consider(left, right, f"shared cause {left['cause']}", 4)

    for card in cards or []:
        pair = _join_ids(card)
        if pair:
            a, b = by_id.get(pair[0]), by_id.get(pair[1])
            note = str(card.get("note") or "receipt join")
            low = note.casefold()
            if "why tethered" in low or "tether" in low:
                consider(a, b, note, 1, True)
            elif "join" in low:
                consider(a, b, note, 5, True)
            else:
                consider(a, b, f"receipt join · {note}", 5, True)
        delta = card.get("delta")
        if isinstance(delta, dict) and delta.get("from") and delta.get("to"):
            consider(by_id.get(str(delta["from"])), by_id.get(str(delta["to"])), "lattice neighbor", 7, True)
        gamma = card.get("gamma")
        if isinstance(gamma, dict) and isinstance(gamma.get("stack"), list):
            stacked = [str(item) for item in gamma["stack"]]
            for index in range(len(stacked) - 1):
                consider(by_id.get(stacked[index]), by_id.get(stacked[index + 1]), "lattice neighbor", 7, True)

    shadow_tokens: list[set[str]] = []
    for link in shadow_links or []:
        if isinstance(link, dict):
            tokens = _shadow_ids(link)
            if tokens:
                shadow_tokens.append(tokens)
    if shadow_tokens:
        for i, left in enumerate(pins):
            blob_l = f"{left['event']} {left['place']}".casefold()
            for right in pins[i + 1 :]:
                blob_r = f"{right['event']} {right['place']}".casefold()
                for tokens in shadow_tokens:
                    if any(token in blob_l and token in blob_r for token in tokens):
                        consider(left, right, "ShadowLock link", 6)
                        break

    edges = []
    for key, (_rank, reason) in chosen.items():
        edge = _edge(by_id[key[0]], by_id[key[1]], reason)
        edge["on_lattice"] = key in written
        edges.append(edge)

    if not edges:
        return {
            "ok": True,
            "op": "pattern_matrix",
            "edges": [],
            "rows": [],
            "n": 0,
            "message": "No connected pattern yet.",
            "lattice": True,
            "ml_store": False,
        }

    rows = []
    for pin in pins:
        neighbors = []
        for edge in edges:
            if edge["from"] != pin["id"] and edge["to"] != pin["id"]:
                continue
            other = edge["to_event"] if edge["from"] == pin["id"] else edge["from_event"]
            neighbors.append(f"{other} · {edge['reason']} · {edge['delta']} · {edge['distance']}")
        if not neighbors:
            continue
        rows.append(
            {
                "event": pin["event"],
                "time": pin["clock"] or "",
                "place": pin["place"] or "",
                "tethered": neighbors,
            }
        )
    return {
        "ok": True,
        "op": "pattern_matrix",
        "edges": edges,
        "rows": rows,
        "n": len(edges),
        "message": "",
        "lattice": True,
        "ml_store": False,
    }
