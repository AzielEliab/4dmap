"""Linguistic pin candidates from upload or corpus text.

Every reachable corpus file is read. A high match can be sealed with
library_pin. A thin match waits. Undated text stays undated.
A repeat of the same event, time, and place folds onto the pin already
on the lattice, and the person set must agree when the text names people.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .earth import BUNDLED_ERAS
from .lattice import pin_frame_of

BADGE = "from corpus/upload"
UNDATED = "undated / era unknown"
NO_TIME = "no time in source"
PLACE_ESTIMATED = "place estimated"
NO_GEO = "no geo in source"
NO_PERSON = "no person in source"
PLACES_PATH = Path(__file__).resolve().parent / "static" / "geo" / "places.json"
CORPUS_PATH = Path(__file__).resolve().parent / "static" / "geo" / "corpus-mention.txt"
CORPUS_DIR = Path(__file__).resolve().parent / "static" / "geo" / "corpus"

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


def era_bucket(date: str | None) -> str:
    """Nearest bundled era. No date stays undated. A year is never invented."""
    digits = ""
    for ch in str(date or ""):
        if ch.isdigit():
            digits += ch
            if len(digits) == 4:
                year = int(digits)
                return str(min(BUNDLED_ERAS, key=lambda item: abs(item - year)))
        elif digits:
            digits = ""
    return UNDATED


def _find_time(text: str) -> str | None:
    clock = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text)
    if not clock:
        return None
    return f"{int(clock.group(1)):02d}:{clock.group(2)}"


def _find_people(text: str, places: list[dict[str, Any]]) -> list[str]:
    blocked = set()
    for place in places:
        for name in [place.get("name"), *(place.get("aliases") or [])]:
            token = str(name or "").strip()
            if token:
                blocked.add(token.casefold())
    found = []
    for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text):
        label = match.group(1).strip()
        if label.casefold() in blocked or label.casefold() in {item.casefold() for item in found}:
            continue
        found.append(label)
        if len(found) == 8:
            break
    return found


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


def _who_key(who: Any) -> tuple[str, ...]:
    if isinstance(who, str):
        who = [part.strip() for part in who.split(",") if part.strip()]
    if not isinstance(who, list):
        return ()
    return tuple(sorted(str(part).strip().casefold() for part in who if str(part).strip()))


def _same_pin(
    frame: dict[str, Any],
    event: str,
    date: str | None,
    place: dict[str, Any] | None,
    who: list[str] | None = None,
) -> bool:
    if str(frame.get("event") or "").casefold() != event.casefold():
        return False
    clock = str(frame.get("clock") or "")
    if date:
        if len(date) >= 10 and len(clock) >= 10:
            if clock[:10] != date[:10]:
                return False
        elif clock[:4] != date[:4]:
            return False
    if who and _who_key(frame.get("who")) != _who_key(who):
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
        clock = _find_time(chunk)
        place = _find_place(chunk, gazetteer)
        people = _find_people(chunk, gazetteer)
        event = _event_phrase(chunk, when_text, str(place.get("name")) if place else None)
        if not date and not place and not event and not people:
            continue
        candidates.append(
            _candidate(
                event=event,
                date=date,
                when_text=when_text,
                clock=clock,
                place=place,
                people=people,
                name=name,
                origin=origin,
                cards=cards,
                surface="MOCK",
                fixture=False,
            )
        )
    return {"ok": True, "candidates": candidates, "n": len(candidates), "badge": BADGE, "source": origin}


def _candidate(
    *,
    event: str,
    date: str | None,
    when_text: str | None,
    clock: str | None,
    place: dict[str, Any] | None,
    people: list[str],
    name: str,
    origin: str,
    cards: list[dict[str, Any]] | None,
    surface: str,
    fixture: bool,
) -> dict[str, Any]:
    bits = []
    if event:
        bits.append(f"'{event}'")
    if when_text:
        bits.append(when_text)
    elif date:
        bits.append(date[:4])
    if clock:
        bits.append(clock)
    if people:
        bits.append(", ".join(people))
    if place:
        bits.append(str(place.get("name")))
    high = bool(date and place and event)
    reason = f"matched {' + '.join(bits)} in {name}" if bits else f"matched a thin line in {name}"
    if not date:
        reason += f". {UNDATED}. A year is not invented."
    if not clock:
        reason += f". {NO_TIME}."
    if place:
        reason += f" {PLACE_ESTIMATED}."
    else:
        reason += f" {NO_GEO}."
    if not people:
        reason += f" {NO_PERSON}."
    if not high:
        reason += " Place, date, or event is thin, so this waits for a person to confirm."
    if fixture:
        reason += " Package fixture, not a recovered library document."
    existing = None
    if event and date and place:
        for card in cards or []:
            frame = pin_frame_of(card) or {}
            if _same_pin(frame, event, date, place, people):
                existing = card.get("id")
                break
    if existing:
        reason = f"Already on the lattice as the same event, time, and place ({event})."
    return {
        "event": event,
        "date": date,
        "time": clock,
        "who": people,
        "place": place.get("name") if place else "",
        "lat": place.get("lat") if place else None,
        "lon": place.get("lon") if place else None,
        "era": era_bucket(date),
        "confidence": "high" if high and not existing else "low",
        "seal": bool(high and not existing),
        "folded": bool(existing),
        "existing_id": existing,
        "reason": reason,
        "badge": BADGE,
        "source": origin,
        "surface": surface if surface in {"MOCK", "REAL"} else "MOCK",
        "fixture": fixture,
    }


def corpus_files() -> list[Path]:
    """Shipped mentions, the corpus directory, and a local corpus folder."""
    found: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        try:
            resolved = path.resolve()
        except OSError:
            return
        if resolved in seen or not resolved.is_file():
            return
        if resolved.suffix.lower() not in {".txt", ".md", ".json"}:
            return
        seen.add(resolved)
        found.append(resolved)

    add(CORPUS_PATH)
    roots = [CORPUS_DIR]
    extra = os.environ.get("FOURDMAP_CORPUS")
    roots.append(Path(extra) if extra else Path.home() / ".4dmap" / "corpus")
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            add(path)
    return found


def _json_records(path: Path, cards: list[dict[str, Any]] | None, places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = data.get("records") if isinstance(data, dict) else data
    if isinstance(data, dict) and "event" in data:
        rows = [data]
    if not isinstance(rows, list):
        return []
    found = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        event = str(row.get("event") or "").strip()
        date = str(row.get("date") or "").strip() or None
        clock = str(row.get("time") or "").strip() or None
        if clock and not re.fullmatch(r"\d{2}:\d{2}", clock):
            clock = _find_time(clock)
        place_name = str(row.get("location") or row.get("place") or "").strip()
        place = _find_place(place_name, places) if place_name else None
        if place is None and row.get("lat") is not None and row.get("lon") is not None:
            try:
                place = {"name": place_name or "reported coordinate", "lat": float(row["lat"]), "lon": float(row["lon"])}
            except (TypeError, ValueError):
                place = None
        people = row.get("who")
        if people is None:
            people = row.get("person")
        if isinstance(people, str):
            people = [part.strip() for part in people.split(",") if part.strip()]
        elif isinstance(people, list):
            people = [str(part).strip() for part in people if str(part).strip()]
        else:
            people = []
        if not event and not date and not place and not people:
            continue
        surface = str(row.get("surface") or "MOCK").upper()
        found.append(
            _candidate(
                event=event,
                date=date,
                when_text=date,
                clock=clock,
                place=place,
                people=people[:8],
                name=path.name,
                origin="corpus",
                cards=cards,
                surface=surface,
                fixture=bool(row.get("fixture")),
            )
        )
    return found


def collect_corpus(cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Read every reachable corpus file. Do not invent a missing row."""
    places = load_places()
    files = corpus_files()
    candidates: list[dict[str, Any]] = []
    names: list[str] = []
    for path in files:
        names.append(path.name)
        if path.suffix.lower() == ".json":
            candidates.extend(_json_records(path, cards, places))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        candidates.extend(propose(text, source="corpus", name=path.name, places=places, cards=cards)["candidates"])
    seen: set[tuple] = set()
    kept = []
    for row in candidates:
        if not row.get("date"):
            kept.append(row)
            continue
        key = (
            str(row.get("event") or "").casefold(),
            str(row.get("date") or ""),
            str(row.get("place") or "").casefold(),
            _who_key(row.get("who")),
        )
        if key in seen and row.get("seal"):
            row = dict(row)
            row["seal"] = False
            row["folded"] = True
            row["confidence"] = "low"
            row["reason"] = f"Already in this corpus read as the same event, time, and place ({row.get('event')})."
        elif row.get("seal"):
            seen.add(key)
        kept.append(row)
    if not names:
        return {
            "ok": True,
            "candidates": [],
            "n": 0,
            "files": [],
            "badge": BADGE,
            "message": "No local corpus mention is on this computer.",
        }
    return {
        "ok": True,
        "candidates": kept,
        "n": len(kept),
        "files": names,
        "badge": BADGE,
        "source": "corpus",
        "message": f"Read {len(names)} corpus files.",
    }
