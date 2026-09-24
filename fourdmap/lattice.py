"""Hashchain lattice for library pins, possibility hooks, and pattern memory.

Pins and scores read/write lattice-linked 4DM-CARD receipts (tips, prev-hash).
Adaptive recollection walks the chain — not a detached ML store.
NO-REWRITE / append-only. Scores are not courtroom proof. Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

from .card import CardError, axis_of, card_receipt, make_card, scan_identity, scan_intent, verify_card
from .scope import (
    AXIS_GLYPH,
    GENESIS_PREV,
    LIBRARY,
    PI_EMPTY,
    PIN_FRAME_KIND,
    SCHEMA,
    ZION_CAP,
)

_DATE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})([T ](\d{2}:\d{2}(:\d{2})?)(Z|[+-]\d{2}:\d{2})?)?$"
)
_GAZETTEER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
_POISON_MARKERS = ("poison", "malware", "payload_drop", "__proto__", "constructor.prototype")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, str) else _canonical(value)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def clock_of(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, dict):
        for key in ("clock", "date", "paper_date", "t"):
            inner = clock_of(value.get(key))
            if inner:
                return inner
        return None
    text = str(value).strip()
    if not text:
        return None
    if _DATE.match(text):
        if "T" not in text and " " not in text:
            return text + "T00:00:00Z"
        return text.replace(" ", "T")
    return None


def parse_clock(payload: dict[str, Any]) -> str | None:
    for key in ("date", "paper_date", "t", "clock"):
        got = clock_of(payload.get(key))
        if got:
            return got
    t = payload.get("t")
    if isinstance(t, dict):
        return clock_of(t)
    return None


def _num(raw: Any, name: str) -> float | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        raise CardError("ANCHOR_REFUSE", f"{name} must be a finite number, not a boolean")
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise CardError("ANCHOR_REFUSE", f"{name} is not a number") from exc
    if not math.isfinite(value):
        raise CardError("ANCHOR_REFUSE", f"{name} is not finite")
    return value


def validate_anchor(
    lat: Any = None,
    lon: Any = None,
    gazetteer_id: Any = None,
    *,
    require_place: bool = False,
) -> dict[str, Any]:
    lat_n = _num(lat, "lat")
    lon_n = _num(lon, "lon")
    if (lat_n is None) ^ (lon_n is None):
        raise CardError("ANCHOR_REFUSE", "lat and lon must be supplied together")
    if lat_n is not None and not -90.0 <= lat_n <= 90.0:
        raise CardError("ANCHOR_REFUSE", "lat must be inside [-90, 90]")
    if lon_n is not None and not -180.0 <= lon_n <= 180.0:
        raise CardError("ANCHOR_REFUSE", "lon must be inside [-180, 180]")
    gaz = None
    if gazetteer_id not in (None, ""):
        gaz = str(gazetteer_id).strip()
        scan_identity(gaz)
        scan_intent(gaz)
        if not _GAZETTEER.match(gaz):
            raise CardError("ANCHOR_REFUSE", "gazetteer_id must be an opaque place token, not a DNS/ICANN name")
        if "." in gaz and gaz.rsplit(".", 1)[-1].isalpha() and ":" not in gaz:
            raise CardError("ANCHOR_REFUSE", "gazetteer_id is not a domain; no fake ICANN")
    if require_place and lat_n is None and not gaz:
        raise CardError("ANCHOR_INCOMPLETE", "library pin needs lat/lon or a gazetteer id (paper place)")
    return {"lat": lat_n, "lon": lon_n, "gazetteer_id": gaz}


def feature_hash(
    event: str | None,
    clock: str | None,
    lat: float | None,
    lon: float | None,
    gazetteer_id: str | None,
) -> str:
    payload = {
        "clock": clock or "",
        "event": str(event or "").strip().lower(),
        "gazetteer_id": gazetteer_id or "",
        "lat": None if lat is None else round(float(lat), 5),
        "lon": None if lon is None else round(float(lon), 5),
    }
    return sha256_hex(payload)


def _surface_of(raw: Any) -> str:
    text = str(raw or "MOCK").strip().upper()
    if text in {"REAL", "LIVE"}:
        return "REAL"
    if text in {"MOCK", "SYNTHETIC", "EXAMPLE"}:
        return "MOCK"
    raise CardError("SURFACE_REFUSE", "surface must be REAL or MOCK")


def _unwrap_ingest(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("ingest"), dict):
        return {**payload, **payload["ingest"]}
    if isinstance(payload.get("pin_frame"), dict):
        return {**payload, **payload["pin_frame"]}
    if isinstance(payload.get("descriptor"), dict):
        return {**payload, **payload["descriptor"]}
    return payload


def refuse_feature_set(cards: list[dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for card in cards or []:
        pi = card.get("pi")
        if not isinstance(pi, dict) or not pi.get("refuse"):
            continue
        feature = str(pi.get("feature_h") or "").strip().lower()
        if len(feature) == 64 and all(c in "0123456789abcdef" for c in feature):
            out.add(feature)
    return out


def _poison_text(*parts: Any) -> None:
    blob = " ".join(str(p or "") for p in parts).lower()
    for mark in _POISON_MARKERS:
        if mark in blob:
            raise CardError("POISON_REFUSE", "poison feature refused (hash/feature only; not stored as payload)")
    for part in parts:
        if isinstance(part, dict) and part.get("poison"):
            raise CardError("POISON_REFUSE", "poison flag refused")


def labeled_score(label: str, value: Any, **extra: Any) -> dict[str, Any] | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise CardError("SCORE_REFUSE", f"{label} must be a number") from exc
    if not math.isfinite(number):
        raise CardError("SCORE_REFUSE", f"{label} is not finite")
    number = min(max(number, 0.0), 1.0)
    out = {
        "label": label,
        "value": number,
        "truth": False,
        "courtroom_proof": False,
        **extra,
    }
    return out


def possibility_hooks(
    *,
    clock: str | None,
    event: str | None,
    lat: float | None,
    lon: float | None,
    gazetteer_id: str | None,
    bayesian: Any = None,
    incoming_possibility: Any = None,
    collapsed_score: Any = None,
) -> dict[str, Any]:
    if collapsed_score not in (None, ""):
        raise CardError(
            "SCORE_COLLAPSE",
            "unlabeled score refused — cite possibility and bayesian separately",
        )
    clock_part = 0.4 if clock else 0.0
    if lat is not None and lon is not None:
        geo_part = 0.4
        geo_kind = "latlon"
    elif gazetteer_id:
        geo_part = 0.25
        geo_kind = "gazetteer"
    else:
        geo_part = 0.0
        geo_kind = "none"
    event_part = 0.2 if str(event or "").strip() else 0.0
    computed = min(clock_part + geo_part + event_part, 1.0)
    if incoming_possibility not in (None, ""):
        if isinstance(incoming_possibility, dict):
            incoming = incoming_possibility.get("value")
            if str(incoming_possibility.get("label") or "").lower() not in {"", "possibility", "plausibility"}:
                raise CardError("SCORE_COLLAPSE", "incoming possibility must keep label=possibility")
        else:
            incoming = incoming_possibility
        cited = labeled_score("possibility", incoming, axes=["T", "geo"], source="cited")
        possibility = labeled_score("possibility", computed, axes=["T", "geo"], source="computed")
        # Keep both labeled; do not average into one unlabeled number.
        hooks = {
            "possibility": possibility,
            "possibility_cited": cited,
        }
    else:
        hooks = {"possibility": labeled_score("possibility", computed, axes=["T", "geo"], source="computed")}
    bayes = None
    if isinstance(bayesian, dict):
        label = str(bayesian.get("label") or "bayesian").strip().lower()
        if label not in {"bayesian", "posterior", "triad"}:
            raise CardError("SCORE_COLLAPSE", "bayesian input must keep label=bayesian")
        bayes = labeled_score(
            "bayesian",
            bayesian.get("value") if bayesian.get("value") is not None else bayesian.get("score"),
            cite=str(bayesian.get("cite") or bayesian.get("src") or "library"),
            triad=bayesian.get("triad"),
            posterior_is_truth=False,
        )
    elif bayesian not in (None, ""):
        bayes = labeled_score("bayesian", bayesian, cite="library", posterior_is_truth=False)
    hooks["bayesian"] = bayes
    hooks["collapsed"] = False
    hooks["courtroom_proof"] = False
    hooks["zion_cap"] = ZION_CAP
    hooks["geo_kind"] = geo_kind
    hooks["note"] = (
        "possibility = time×geo plausibility. bayesian = cited belief input. "
        "They are not one number. Neither is truth or courtroom proof."
    )
    return hooks


def _pin_labels(raw: dict[str, Any]) -> tuple[list[str], str, list[str]]:
    who_raw = raw.get("who")
    if who_raw is None:
        who_raw = raw.get("person")
    if isinstance(who_raw, str):
        who = [part.strip() for part in who_raw.split(",") if part.strip()]
    elif isinstance(who_raw, list):
        who = [str(part).strip() for part in who_raw if str(part).strip()]
    else:
        who = []
    if len(who) > 8:
        raise CardError("WHO_REFUSE", "a pin keeps at most 8 person labels")
    for label in who:
        if len(label) > 80:
            raise CardError("WHO_REFUSE", "a person label must be 80 characters or fewer")
    place = str(raw.get("place") or "").strip()
    if len(place) > 240:
        raise CardError("PLACE_REFUSE", "place words must be 240 characters or fewer")
    uploads_raw = raw.get("uploads") or []
    if isinstance(uploads_raw, str):
        uploads_raw = [part.strip() for part in uploads_raw.split(",") if part.strip()]
    if not isinstance(uploads_raw, list):
        raise CardError("UPLOAD_REFUSE", "uploads must be a list of SHA-256 hashes")
    uploads: list[str] = []
    for item in uploads_raw:
        digest = str(item).strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise CardError("UPLOAD_REFUSE", "each upload must be a SHA-256 hex hash")
        uploads.append(digest)
    return who, place, uploads


def parse_ingest(payload: dict[str, Any], cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    raw = _unwrap_ingest(payload or {})
    scan_identity(raw)
    scan_intent(raw)
    if raw.get("poison") or raw.get("poison_feature"):
        raise CardError("POISON_REFUSE", "poison feature refused (hash/feature only)")
    if raw.get("upload_time") and not (raw.get("date") or raw.get("paper_date") or raw.get("t")):
        raise CardError("CLOCK_REFUSE", "library pins use paper date, never upload time")
    event = str(raw.get("event") or raw.get("title") or "").strip()
    clock = parse_clock(raw)
    if not clock:
        raise CardError("CLOCK_REFUSE", "library pin needs a paper date (event date), never upload time")
    if not event:
        raise CardError("EVENT_REFUSE", "library pin needs an event descriptor")
    who, place, uploads = _pin_labels(raw)
    _poison_text(event, raw.get("note"), raw.get("gazetteer_id"), place, " ".join(who))
    nested_t = raw.get("t") if isinstance(raw.get("t"), dict) else {}
    anchor = validate_anchor(
        raw.get("lat") if raw.get("lat") is not None else nested_t.get("lat"),
        raw.get("lon") if raw.get("lon") is not None else nested_t.get("lon"),
        raw.get("gazetteer_id") or raw.get("gazetteer") or nested_t.get("gazetteer_id"),
        require_place=True,
    )
    feature = feature_hash(event, clock, anchor["lat"], anchor["lon"], anchor["gazetteer_id"])
    refused = refuse_feature_set(cards or [])
    if feature in refused:
        raise CardError("POISON_REFUSE", "feature hash is on the lattice refuse set")
    surface = _surface_of(raw.get("surface") or raw.get("reality") or payload.get("surface"))
    src = str(raw.get("src") or payload.get("src") or "aziel-corpus").strip().lower()
    if src in {"library", "aziel-digital-library", "azielcorpus"}:
        src = "aziel-corpus"
    doc_id = raw.get("doc_id") or raw.get("document_id") or raw.get("cursor")
    if doc_id:
        doc_id = str(doc_id).strip()
        scan_identity(doc_id)
    hooks = possibility_hooks(
        clock=clock,
        event=event,
        lat=anchor["lat"],
        lon=anchor["lon"],
        gazetteer_id=anchor["gazetteer_id"],
        bayesian=raw.get("bayesian") or payload.get("bayesian"),
        incoming_possibility=raw.get("possibility") or raw.get("possibility_score") or payload.get("possibility"),
        collapsed_score=raw.get("score") if "possibility" not in raw and "bayesian" not in raw else None,
    )
    t = {
        "kind": PIN_FRAME_KIND,
        "clock": clock,
        "event": event,
        "lat": anchor["lat"],
        "lon": anchor["lon"],
        "gazetteer_id": anchor["gazetteer_id"],
        "doc_id": doc_id,
        "surface": surface,
        "feature_h": feature,
        "who": who,
        "place": place,
        "uploads": uploads,
    }
    if isinstance(hooks.get("bayesian"), dict) and hooks["bayesian"].get("value") is not None:
        t["bayesian"] = {
            "label": "bayesian",
            "value": hooks["bayesian"]["value"],
            "cite": hooks["bayesian"].get("cite") or "library",
            "posterior_is_truth": False,
        }
    return {
        "t": t,
        "event": event,
        "clock": clock,
        "lat": anchor["lat"],
        "lon": anchor["lon"],
        "gazetteer_id": anchor["gazetteer_id"],
        "doc_id": doc_id,
        "surface": surface,
        "src": src,
        "feature_h": feature,
        "hooks": hooks,
        "note": str(raw.get("note") or payload.get("note") or f"{surface} library pin {event}"),
        "prev": raw.get("prev") or payload.get("prev"),
        "id": raw.get("id") or payload.get("id"),
    }


def pin_frame_of(card: dict[str, Any]) -> dict[str, Any] | None:
    t = card.get("t")
    if isinstance(t, dict) and (t.get("kind") == PIN_FRAME_KIND or t.get("lat") is not None or t.get("gazetteer_id") or t.get("event")):
        return t
    return None


def emit_pin_frame(card: dict[str, Any], hooks: dict[str, Any] | None = None) -> dict[str, Any]:
    frame = pin_frame_of(card) or {}
    receipt = card_receipt(card)
    return {
        "kind": PIN_FRAME_KIND,
        "schema": SCHEMA,
        "id": card.get("id"),
        "h": card.get("h"),
        "prev": card.get("prev"),
        "axis": "T",
        "glyph": "T",
        "src": card.get("src"),
        "event": frame.get("event"),
        "clock": frame.get("clock") or clock_of(card.get("t")),
        "lat": frame.get("lat"),
        "lon": frame.get("lon"),
        "gazetteer_id": frame.get("gazetteer_id"),
        "doc_id": frame.get("doc_id"),
        "surface": frame.get("surface") or ("MOCK" if str(card.get("src") or "") == "synthetic" else "REAL"),
        "feature_h": frame.get("feature_h"),
        "library": LIBRARY,
        "receipt": receipt,
        "hooks": hooks,
        "truth": False,
        "courtroom_proof": False,
        "gis": False,
    }


def library_cite() -> dict[str, Any]:
    return {
        "software": LIBRARY["software"],
        "slug": LIBRARY["slug"],
        "role": LIBRARY["role"],
        "cite_only": True,
        "door": False,
        "merged": False,
        "map": LIBRARY["map"],
        "verify_geo": LIBRARY["verify_geo"],
        "note": LIBRARY["note"],
    }


def tips_of(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    referenced = {str(c.get("prev") or "") for c in cards or [] if str(c.get("prev") or "") and str(c.get("prev")) != GENESIS_PREV}
    tips = []
    for card in cards or []:
        h = str(card.get("h") or "")
        if h and h not in referenced:
            tips.append({"id": card.get("id"), "h": h, "prev": card.get("prev"), "axis": axis_of(card), "glyph": AXIS_GLYPH[axis_of(card)]})
    return tips


def plot_model(cards: list[dict[str, Any]]) -> dict[str, Any]:
    pins = []
    trajectories = []
    for card in cards or []:
        verify_card(card)
        frame = pin_frame_of(card)
        if frame and (frame.get("lat") is not None or frame.get("gazetteer_id")):
            hooks = possibility_hooks(
                clock=frame.get("clock"),
                event=frame.get("event"),
                lat=frame.get("lat"),
                lon=frame.get("lon"),
                gazetteer_id=frame.get("gazetteer_id"),
                bayesian=frame.get("bayesian"),
            )
            pins.append(
                {
                    "id": card.get("id"),
                    "h": card.get("h"),
                    "prev": card.get("prev"),
                    "clock": frame.get("clock"),
                    "event": frame.get("event"),
                    "lat": frame.get("lat"),
                    "lon": frame.get("lon"),
                    "gazetteer_id": frame.get("gazetteer_id"),
                    "surface": frame.get("surface"),
                    "feature_h": frame.get("feature_h"),
                    "src": card.get("src"),
                    "axis": "T",
                    "who": frame.get("who") or [],
                    "place": frame.get("place") or "",
                    "uploads": frame.get("uploads") or [],
                    "possibility": hooks.get("possibility"),
                    "bayesian": hooks.get("bayesian"),
                    "exact_point": False,
                }
            )
        gamma = card.get("gamma")
        if isinstance(gamma, dict) and isinstance(gamma.get("stack"), list):
            trajectories.append({"kind": "stack", "ids": list(gamma["stack"]), "hs": list(gamma.get("hs") or []), "card_id": card.get("id")})
        delta = card.get("delta")
        if isinstance(delta, dict) and delta.get("from") and delta.get("to"):
            trajectories.append({"kind": "span", "from": delta.get("from"), "to": delta.get("to"), "card_id": card.get("id")})
    by_id = {p["id"]: p for p in pins}
    for traj in trajectories:
        if traj.get("kind") == "span":
            a, b = by_id.get(traj.get("from")), by_id.get(traj.get("to"))
            if a and b and a.get("lat") is not None and b.get("lat") is not None:
                traj["from_xy"] = {"lat": a["lat"], "lon": a["lon"]}
                traj["to_xy"] = {"lat": b["lat"], "lon": b["lon"]}
    return {
        "ok": True,
        "op": "plot",
        "pins": pins,
        "trajectories": trajectories,
        "n": len(pins),
        "gis": False,
        "truth": False,
        "courtroom_proof": False,
        "note": "Inspection plot of lattice pins. Not GIS 4D. REAL vs MOCK labeled on each pin.",
    }


def library_pin(payload: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = parse_ingest(payload, cards)
    prev = parsed.get("prev")
    if not prev:
        tips = tips_of(cards)
        prev = tips[-1]["h"] if tips else GENESIS_PREV
    card = make_card(
        id=parsed.get("id"),
        t=parsed["t"],
        src=parsed["src"],
        note=parsed["note"],
        prev=prev,
        pi=PI_EMPTY,
    )
    frame = emit_pin_frame(card, parsed["hooks"])
    return {
        "ok": True,
        "op": "library_pin",
        "axis": "T",
        "glyph": "T",
        "card": card,
        "id": card["id"],
        "h": card["h"],
        "prev": card["prev"],
        "feature_h": parsed["feature_h"],
        "surface": parsed["surface"],
        "pin_frame": frame,
        "hooks": parsed["hooks"],
        "possibility": parsed["hooks"].get("possibility"),
        "bayesian": parsed["hooks"].get("bayesian"),
        "collapsed": False,
        "library": library_cite(),
        "lattice": True,
        "ml_store": False,
        "rewrite": False,
        "truth": False,
        "courtroom_proof": False,
        "companion": library_cite() if parsed["src"] == "aziel-corpus" else None,
        "receipt": card_receipt(card),
    }


def score_on_lattice(payload: dict[str, Any], cards: list[dict[str, Any]], store_add) -> dict[str, Any]:
    card = payload.get("card")
    if card is None and payload.get("id"):
        wanted = str(payload["id"])
        card = next((c for c in cards if c.get("id") == wanted), None)
    if card is None and (payload.get("event") or payload.get("date") or payload.get("ingest") or payload.get("pin_frame")):
        pinned = library_pin(payload, cards)
        store_add(pinned["card"])
        card = pinned["card"]
        hooks = pinned["hooks"]
    elif isinstance(card, dict):
        verify_card(card)
        frame = pin_frame_of(card) or {}
        hooks = possibility_hooks(
            clock=frame.get("clock") or clock_of(card.get("t")),
            event=frame.get("event"),
            lat=frame.get("lat"),
            lon=frame.get("lon"),
            gazetteer_id=frame.get("gazetteer_id"),
            bayesian=payload.get("bayesian"),
            incoming_possibility=payload.get("possibility") or payload.get("possibility_score"),
            collapsed_score=payload.get("score") if payload.get("possibility") is None and payload.get("bayesian") is None else None,
        )
    else:
        raise CardError("NOT_FOUND", "possibility needs a pin card, id, or library ingest")
    score_card = make_card(
        pi={
            "scores": {
                "possibility": hooks.get("possibility"),
                "bayesian": hooks.get("bayesian"),
            },
            "collapsed": False,
            "courtroom_proof": False,
            "lattice": True,
            "ml_store": False,
            "pin_id": card.get("id"),
            "pin_h": card.get("h"),
        },
        src=str(payload.get("src") or card.get("src") or "4dmap"),
        note=str(payload.get("note") or "possibility + bayesian hooks (labeled, not collapsed)"),
        prev=str(card.get("h") or GENESIS_PREV),
        t=None,
    )
    store_add(score_card)
    return {
        "ok": True,
        "op": "possibility",
        "id": score_card["id"],
        "h": score_card["h"],
        "prev": score_card["prev"],
        "card": score_card,
        "pin": {"id": card.get("id"), "h": card.get("h")},
        "hooks": hooks,
        "possibility": hooks.get("possibility"),
        "bayesian": hooks.get("bayesian"),
        "collapsed": False,
        "courtroom_proof": False,
        "lattice": True,
        "ml_store": False,
        "rewrite": False,
        "receipt": card_receipt(score_card),
        "note": hooks.get("note"),
    }


def pattern_recall(payload: dict[str, Any], cards: list[dict[str, Any]], store_add) -> dict[str, Any]:
    for card in cards:
        verify_card(card)
    counts: dict[str, dict[str, Any]] = {}
    for card in cards:
        frame = pin_frame_of(card)
        if not frame or not frame.get("feature_h"):
            continue
        key = str(frame["feature_h"])
        row = counts.setdefault(key, {"feature_h": key, "n": 0, "event": frame.get("event"), "ids": [], "hs": []})
        row["n"] += 1
        row["ids"].append(card.get("id"))
        row["hs"].append(card.get("h"))
    recurring = [row for row in counts.values() if row["n"] >= 2]
    recurring.sort(key=lambda r: (-r["n"], r["feature_h"]))
    tips = tips_of(cards)
    prev = str(payload.get("prev") or (tips[-1]["h"] if tips else GENESIS_PREV))
    memory_card = make_card(
        pi={
            "lattice": True,
            "ml_store": False,
            "patterns": [{"feature_h": r["feature_h"], "n": r["n"], "event": r.get("event")} for r in recurring],
            "store": "hashchain",
            "tips": [t["h"] for t in tips],
        },
        src=str(payload.get("src") or "4dmap"),
        note=str(payload.get("note") or "lattice pattern recall (hash/feature only)"),
        prev=prev,
    )
    store_add(memory_card)
    return {
        "ok": True,
        "op": "pattern_recall",
        "card": memory_card,
        "id": memory_card["id"],
        "h": memory_card["h"],
        "prev": memory_card["prev"],
        "patterns": recurring,
        "n": len(recurring),
        "tips": tips,
        "lattice": True,
        "ml_store": False,
        "rewrite": False,
        "receipt": card_receipt(memory_card),
        "note": "Recurring event patterns counted on the hashchain lattice. Not a detached ML store.",
    }


def poison_refuse(payload: dict[str, Any], cards: list[dict[str, Any]], store_add) -> dict[str, Any]:
    raw = _unwrap_ingest(payload or {})
    feature = str(raw.get("feature_h") or raw.get("feature") or "").strip().lower()
    if not feature:
        event = str(raw.get("event") or "").strip()
        clock = parse_clock(raw)
        anchor = validate_anchor(raw.get("lat"), raw.get("lon"), raw.get("gazetteer_id"), require_place=False)
        if not event and not clock and anchor["lat"] is None and not anchor["gazetteer_id"]:
            raise CardError("POISON_REFUSE", "poison refuse needs a feature hash or event/date/geo to hash")
        feature = feature_hash(event, clock, anchor["lat"], anchor["lon"], anchor["gazetteer_id"])
    if len(feature) != 64 or any(c not in "0123456789abcdef" for c in feature):
        feature = sha256_hex(feature)
    tips = tips_of(cards)
    prev = str(payload.get("prev") or (tips[-1]["h"] if tips else GENESIS_PREV))
    card = make_card(
        pi={"refuse": True, "feature_h": feature, "kind": "poison", "store": "hashchain", "ml_store": False},
        src=str(payload.get("src") or "4dmap"),
        note=str(payload.get("note") or "poison feature refuse (hash only)"),
        prev=prev,
    )
    store_add(card)
    return {
        "ok": True,
        "op": "poison_refuse",
        "card": card,
        "id": card["id"],
        "h": card["h"],
        "prev": card["prev"],
        "feature_h": feature,
        "refused_set": sorted(refuse_feature_set(list(cards) + [card])),
        "payload_stored": False,
        "lattice": True,
        "ml_store": False,
        "rewrite": False,
        "receipt": card_receipt(card),
        "note": "Refuse set is append-only on the lattice. Feature hash only. No rewrite.",
    }


def lattice_tip(cards: list[dict[str, Any]]) -> dict[str, Any]:
    for card in cards:
        verify_card(card)
    tips = tips_of(cards)
    return {
        "ok": True,
        "op": "lattice_tip",
        "tips": tips,
        "n": len(tips),
        "cards": len(cards),
        "genesis": GENESIS_PREV,
        "rewrite": False,
        "ml_store": False,
        "lattice": True,
        "note": "Tips are cards whose h is not cited as prev. Append-only.",
    }


def neighbor_cite(payload: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, Any]:
    card = payload.get("card")
    card_id = str(payload.get("id") or payload.get("card_id") or payload.get("tip") or "")
    if card is None and card_id:
        card = next((c for c in cards if c.get("id") == card_id), None)
    if not isinstance(card, dict):
        raise CardError("4DM-MISSING", "Unknown card_id. Cite a neighbor on a declared card.")
    verify_card(card)
    neighbors = [library_cite()]
    src = str(card.get("src") or "")
    from .card import companion_cite

    cited = companion_cite(src, axis_of(card))
    if cited:
        neighbors.append(cited)
    return {
        "ok": True,
        "op": "neighbor_cite",
        "id": card.get("id"),
        "h": card.get("h"),
        "join_type": "neighbor",
        "neighbors": neighbors,
        "library": library_cite(),
        "receipt": card_receipt(card),
        "companions_merged": False,
        "second_door": False,
        "note": "Research-domain neighbor cite. Aziel Digital Library + inspection companions. Products are not merged.",
    }
