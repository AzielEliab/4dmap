"""Linguistic pin candidates from upload or corpus text.

A high match can be sealed with library_pin. A thin match waits.
A repeat of the same event, year, and place folds onto the pin already
on the lattice. Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .lattice import pin_frame_of

BADGE = "from corpus/upload"
PLACES_PATH = Path(__file__).resolve().parent / "static" / "geo" / "places.json"
CORPUS_PATH = Path(__file__).resolve().parent / "static" / "geo" / "corpus-mention.txt"

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}
SKIP = {
    "the", "a", "an", "at", "on", "in", "near", "of", "and", "for", "from",
    "with", "to", "by", "was", "were", "is", "this", "that", "local", "sample",
}


def load_places() -> list[dict[str, Any]]:
    try:
        data = json.loads(PLACES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return list(data.get("places") or [])


def load_corpus_text() -> str:
    try:
        return CORPUS_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z']+", text)


def _find_place(text: str, places: list[dict[str, Any]]) -> dict[str, Any] | None:
    low = text.casefold()
    best = None
    best_len = 0
    for place in places:
        names = [place.get("name"), *(place.get("aliases") or [])]
        for name in names:
            token = str(name or "").strip()
            if len(token) < 4:
                continue
            if re.search(rf"\b{re.escape(token.casefold())}\b", low) and len(token) > best_len:
                best = place
                best_len = len(token)
    return best


def _find_when(text: str) -> tuple[str | None, str | None]:
    iso = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if iso:
        return f"{iso.group(1)}-{iso.group(2)}-{iso.group(3)}", iso.group(0)
    month = re.search(
        r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
        text,
        re.I,
    )
    if month:
        mon = MONTHS[month.group(2).casefold()]
        return f"{int(month.group(3)):04d}-{mon:02d}-{int(month.group(1)):02d}", month.group(0)
    month_year = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
        text,
        re.I,
    )
    if month_year:
        mon = MONTHS[month_year.group(1).casefold()]
        return f"{int(month_year.group(2)):04d}-{mon:02d}-01", month_year.group(0)
    year = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", text)
    if year:
        return f"{year.group(1)}-01-01", year.group(1)
    return None, None


def _event_phrase(text: str, when_text: str | None, place_name: str | None) -> str:
    cleaned = text
    if when_text:
        cleaned = re.sub(re.escape(when_text), " ", cleaned, flags=re.I)
    if place_name:
        cleaned = re.sub(rf"\b{re.escape(place_name)}\b", " ", cleaned, flags=re.I)
    kept = [word for word in _words(cleaned) if word.casefold() not in SKIP and not word.isdigit()]
    if len(kept) < 2:
        return ""
    return " ".join(kept[:8])


def _same_pin(frame: dict[str, Any], event: str, date: str | None, place: dict[str, Any] | None) -> bool:
    if str(frame.get("event") or "").casefold() != event.casefold():
        return False
    if date and str(frame.get("clock") or "")[:4] != date[:4]:
        return False
    if place is None:
        return False
    plat, plon = frame.get("lat"), frame.get("lon")
    if plat is None or plon is None:
        return str(frame.get("place") or "").casefold().find(str(place.get("name") or "").casefold()) >= 0
    return abs(float(plat) - float(place["lat"])) < 0.3 and abs(float(plon) - float(place["lon"])) < 0.3


def propose(
    text: str,
    *,
    source: str = "upload",
    name: str = "upload",
    places: list[dict[str, Any]] | None = None,
    cards: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    raw = str(text or "").strip()
    gazetteer = places if places is not None else load_places()
    origin = "corpus" if source == "corpus" else "upload"
    if not raw:
        return {"ok": True, "candidates": [], "n": 0, "badge": BADGE}
    chunks = [part.strip() for part in re.split(r"[\n.]+", raw) if part.strip()]
    candidates = []
    for chunk in chunks:
        date, when_text = _find_when(chunk)
        place = _find_place(chunk, gazetteer)
        event = _event_phrase(chunk, when_text, str(place.get("name")) if place else None)
        if not date and not place and not event:
            continue
        bits = []
        if event:
            bits.append(f"'{event}'")
        if when_text:
            bits.append(when_text)
        elif date:
            bits.append(date[:4])
        if place:
            bits.append(str(place.get("name")))
        high = bool(date and place and event)
        reason = f"matched {' + '.join(bits)} in {name}"
        if not high:
            reason += ". Place, time, or event is thin, so this waits for a person to confirm."
        existing = None
        if event and date and place:
            for card in cards or []:
                frame = pin_frame_of(card) or {}
                if _same_pin(frame, event, date, place):
                    existing = card.get("id")
                    break
        if existing:
            reason = f"Already on the lattice as the same event, time, and place ({event})."
        candidates.append(
            {
                "event": event,
                "date": date,
                "place": place.get("name") if place else "",
                "lat": place.get("lat") if place else None,
                "lon": place.get("lon") if place else None,
                "confidence": "high" if high and not existing else "low",
                "seal": bool(high and not existing),
                "folded": bool(existing),
                "existing_id": existing,
                "reason": reason,
                "badge": BADGE,
                "source": origin,
                "surface": "MOCK",
            }
        )
    return {"ok": True, "candidates": candidates, "n": len(candidates), "badge": BADGE, "source": origin}
