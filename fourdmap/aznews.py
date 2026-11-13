"""AZNews beside 4DMap.

AZNews can store a story with no pin. 4DMap can pin a date, an event, and a
place with no story. The join stores one item both ways and reads it back
from the pin. This module does not fetch a feed, does not write AZ-OS, and
does not write the human interface. A fixture never flips a live flag.
The join is marked live only after one complete fetched item has been stored
off the map and read back from a pin.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .card import CardError, make_card, scan_identity, scan_intent
from .scope import AUTHOR, GENESIS_PREV, LIBRARY, PI_EMPTY, PIN_FRAME_KIND

ABSENT_CODE = "AZNEWS-SOURCE-ABSENT"
LIBRARY_CODE = "AZNEWS-NOT-LIBRARY"
ABSENT_MODULE = "fourdmap/aznews.py"
ABSENT_SOURCE = "public Aziel news feed"
JOIN = "aznews-4dmap"
LIBRARY_MAP = LIBRARY["map"]
_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})([T ](\d{2}:\d{2}(:\d{2})?)(Z|[+-]\d{2}:\d{2})?)?$")
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_USER_RE = re.compile(r"^[a-zA-Z0-9._-]{1,80}$")

_RECORDS: list[dict[str, Any]] = []


def reset_aznews_store() -> None:
    """Clear the in-process desk. Tests and doctor use this. No file is deleted."""
    _RECORDS.clear()


def _sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _sentence(text: str) -> str:
    return " ".join(str(text or "").split())


def _username(payload: dict[str, Any]) -> str:
    raw = payload.get("username")
    name = "operator" if raw in (None, "") else str(raw).strip()
    if not _USER_RE.match(name):
        raise CardError(
            "AZNEWS-USERNAME-ABSENT",
            "A news receipt needs a short username handle. A legal name is not stored.",
        )
    scan_identity(name)
    return name


def _clock(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text or not _DATE_RE.match(text):
        return None
    if "T" not in text and " " not in text:
        return f"{text}T00:00:00Z"
    return text.replace(" ", "T")


def _image_hash(raw: Any) -> str | None:
    if raw in (None, ""):
        return None
    if isinstance(raw, str):
        text = raw.strip().lower()
    elif isinstance(raw, dict):
        text = str(raw.get("content_hash") or raw.get("sha256") or "").strip().lower()
    else:
        text = ""
    if not _HASH_RE.match(text):
        raise CardError(
            "AZNEWS-ITEM-INCOMPLETE",
            "An image hash must be 64 hex characters. This package does not fetch image bytes.",
        )
    return text


def _score(raw: Any) -> float | None:
    if raw in (None, ""):
        return None
    if isinstance(raw, bool) or isinstance(raw, (list, dict)):
        raise CardError("AZNEWS-SCORE", "A score must be a finite number. Nothing was written.")
    try:
        number = float(raw)
    except (TypeError, ValueError) as exc:
        raise CardError("AZNEWS-SCORE", "A score must be a finite number. Nothing was written.") from exc
    if number != number or number in (float("inf"), float("-inf")):
        raise CardError("AZNEWS-SCORE", "A score must be a finite number. Nothing was written.")
    if number.is_integer():
        return int(number)
    return number


def _place(raw: dict[str, Any]) -> dict[str, Any]:
    place = str(raw.get("place") or raw.get("geo") or "").strip()
    lat = raw.get("lat")
    lon = raw.get("lon")
    if (lat in (None, "")) != (lon in (None, "")):
        raise CardError("AZNEWS-ANCHOR", "Latitude and longitude must be supplied together.")
    flat = flon = None
    if lat not in (None, ""):
        try:
            flat = float(lat)
            flon = float(lon)
        except (TypeError, ValueError) as exc:
            raise CardError("AZNEWS-ANCHOR", "Latitude and longitude must be numbers.") from exc
        if flat < -90 or flat > 90 or flon < -180 or flon > 180:
            raise CardError("AZNEWS-ANCHOR", "Latitude must be between -90 and 90, and longitude between -180 and 180.")
    if not place and flat is None:
        raise CardError("AZNEWS-ANCHOR", "A news item needs a place, or a latitude and longitude.")
    return {"place": place, "lat": flat, "lon": flon}


def _mentions_library(payload: dict[str, Any]) -> bool:
    src = str(payload.get("src") or payload.get("source") or "").strip().lower()
    if src in {"aziel-corpus", "library", "aziel-digital-library", "azielcorpus"}:
        return True
    blobs = [payload.get("map"), payload.get("source_url"), payload.get("url")]
    item = payload.get("item")
    if isinstance(item, dict):
        blobs.extend([item.get("map"), item.get("source_url"), item.get("url"), item.get("src"), item.get("source")])
    for blob in blobs:
        text = str(blob or "")
        if LIBRARY_MAP in text or text.strip().lower() in {"aziel-corpus", "library"}:
            return True
    return False


def _item_from(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("item") if isinstance(payload.get("item"), dict) else payload
    if not isinstance(raw, dict):
        raise CardError("AZNEWS-ITEM-INCOMPLETE", "A news item must be an object.")
    scan_identity(raw)
    scan_intent(raw)
    fixture = bool(payload.get("fixture") or raw.get("fixture"))
    fetched = bool(payload.get("fetched") or raw.get("fetched")) and not fixture
    if fixture:
        label = str(payload.get("fixture_label") or raw.get("fixture_label") or "").strip()
        if "fixture" not in label.lower() or len(label) > 80:
            raise CardError(
                "AZNEWS-FIXTURE-UNLABELED",
                "A test fixture must carry a short label that says fixture. An unlabeled item is not a news source.",
            )
    else:
        label = ""
    event = str(raw.get("event") or "").strip()
    wording = str(raw.get("wording") or raw.get("body") or "").strip()
    headline = str(raw.get("headline") or "").strip() or wording[:240]
    clock = _clock(raw.get("date") or raw.get("paper_date"))
    if not clock:
        raise CardError("AZNEWS-CLOCK", "A news item needs a paper date. Upload time is not the event date.")
    if not event:
        raise CardError("AZNEWS-EVENT", "A news item needs an event.")
    if not wording:
        raise CardError("AZNEWS-ITEM-INCOMPLETE", "A news item needs wording so it can be opened in plain language.")
    if len(event) > 240 or len(headline) > 240 or len(wording) > 8000:
        raise CardError("AZNEWS-ITEM-INCOMPLETE", "Event, headline, and wording exceed the allowed length.")
    anchor = _place(raw)
    image = _image_hash(raw.get("image") if raw.get("image") is not None else raw.get("image_hash"))
    score = _score(raw.get("score") if raw.get("score") is not None else payload.get("score"))
    if fetched and score is None:
        raise CardError("AZNEWS-ITEM-INCOMPLETE", "A fetched item needs a score. None was filled in.")
    if fetched and not image:
        raise CardError(
            "AZNEWS-ITEM-INCOMPLETE",
            "A fetched item needs an image content hash. This package does not fetch image bytes.",
        )
    item_id = str(raw.get("id") or raw.get("item_id") or "").strip()
    item = {
        "date": clock,
        "event": event,
        "headline": headline,
        "wording": wording,
        "place": anchor["place"],
        "lat": anchor["lat"],
        "lon": anchor["lon"],
        "image_hash": image,
        "image_gap": image is None,
        "score": score,
        "fixture": fixture,
        "fixture_label": label,
        "fetched": fetched,
        "origin": "fixture" if fixture else ("fetch" if fetched else "supplied"),
    }
    if not item_id:
        item_id = "nw-" + _document_hash(item)[:12]
    if len(item_id) > 80:
        raise CardError("AZNEWS-ITEM-INCOMPLETE", "An item id must stay within 80 characters.")
    item["id"] = item_id
    return item


def _document_hash(item: dict[str, Any]) -> str:
    return _sha(
        {
            "date": item.get("date"),
            "event": item.get("event"),
            "fetched": bool(item.get("fetched")),
            "fixture": bool(item.get("fixture")),
            "image_hash": item.get("image_hash"),
            "place": item.get("place"),
            "score": item.get("score"),
            "wording": item.get("wording"),
        }
    )


def _open_hash(document_hash: str, wording: str) -> str:
    return _sha({"document_hash": document_hash, "op": "news_open", "wording": wording})


def _uses_explicit_records(payload: dict[str, Any]) -> bool:
    return "records" in payload


def _load_explicit(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("records")
    if not isinstance(raw, list):
        raise CardError("AZNEWS-ITEM-INCOMPLETE", "records must be a list of news receipts.")
    loaded: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict) or not isinstance(row.get("item"), dict):
            raise CardError("AZNEWS-ITEM-INCOMPLETE", "A news receipt must contain its item.")
        item = dict(row["item"])
        digest = _document_hash(item)
        if str(row.get("document_hash") or "") != digest:
            raise CardError("HASH_FAIL", "news record hash does not match the item")
        opened = bool(row.get("opened")) and bool(row.get("on_map"))
        open_receipt = row.get("open_receipt") if isinstance(row.get("open_receipt"), dict) else None
        if opened:
            expected = _open_hash(digest, str(item.get("wording") or ""))
            if not open_receipt or open_receipt.get("open_hash") != expected:
                opened = False
                open_receipt = None
        loaded.append(
            {
                "document_hash": digest,
                "on_map": bool(row.get("on_map")),
                "opened": opened,
                "item": item,
                "pin_id": row.get("pin_id"),
                "card": row.get("card") if isinstance(row.get("card"), dict) else None,
                "receipt": row.get("receipt") if isinstance(row.get("receipt"), dict) else {},
                "open_receipt": open_receipt,
                "username": row.get("username") or "operator",
            }
        )
    return loaded


def _desk(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    if _uses_explicit_records(payload):
        return _load_explicit(payload), True
    return _RECORDS, False


def _export(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in records:
        out.append(
            {
                "document_hash": row["document_hash"],
                "on_map": row["on_map"],
                "opened": row["opened"],
                "item": row["item"],
                "pin_id": row.get("pin_id"),
                "card": row.get("card"),
                "receipt": row.get("receipt"),
                "open_receipt": row.get("open_receipt"),
                "username": row.get("username"),
            }
        )
    return out


def _fetched_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in records
        if row["item"].get("fetched") is True and row["item"].get("fixture") is not True and row["item"].get("origin") == "fetch"
    ]


def _join_ready(records: list[dict[str, Any]]) -> bool:
    flags: dict[str, set[str]] = {}
    for row in _fetched_rows(records):
        bucket = flags.setdefault(row["document_hash"], set())
        bucket.add("map" if row["on_map"] else "alone")
        if row["on_map"] and row.get("opened"):
            bucket.add("opened")
    return any({"alone", "map", "opened"} <= marks for marks in flags.values())


def _cross() -> dict[str, Any]:
    return {
        "azos_updated": False,
        "interface_updated": False,
        "runtime_claimed": False,
        "runtime_done": False,
        "note": (
            "This package does not update AZ-OS, the human interface, or aziel-runtime. "
            "Those desks keep their own stores."
        ),
    }


def _flags(records: list[dict[str, Any]]) -> dict[str, Any]:
    ready = _join_ready(records)
    fetched = bool(_fetched_rows(records))
    if ready and not fetched:
        raise CardError("AZNEWS-LIVE", "join live was set without a fetched item")
    return {
        "live": ready,
        "join_live": ready,
        "joined": ready,
        "aznews_live": ready,
        "fourdmap_live": False,
        "catalog_live": False,
        "feed_configured": False,
        "fetched_from_network": False,
        "merged": False,
        "installed": False,
        "engine_installed": False,
        "software_tab": False,
        "mcp_tool": False,
        "second_door": False,
        "door": "fraggate",
        "domains_are_doors": False,
        "source_present": fetched,
        "fixture_is_source": False,
        "library_map_is_aznews": False,
        "library_cite_merged": False,
    }


def _seal(record: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    ready = _join_ready(records)
    flags = _flags(records)
    record.update(flags)
    record["aznews"] = join_card(records)
    record["cross_tether"] = _cross()
    record["author"] = AUTHOR
    if record.get("refused") is True or record.get("ok") is False:
        record["live"] = False
        record["join_live"] = False
        record["joined"] = False
        record["aznews_live"] = False
        record["round_trip"] = False
        card = dict(record.get("aznews") or {})
        card["live"] = False
        card["join_live"] = False
        card["aznews_live"] = False
        record["aznews"] = card
    if record.get("fourdmap_live") is True:
        raise CardError("AZNEWS-LIVE", "4DMap is marked live")
    if record.get("merged") is True or record.get("software_tab") is True or record.get("installed") is True:
        raise CardError("AZNEWS-LIVE", "AZNews is marked merged, installed, or listed as its own Softwares card")
    if record.get("live") is True and not ready:
        raise CardError("AZNEWS-LIVE", "join live is true before a fetched item is stored both ways and opened")
    if record.get("catalog_live") is True or record.get("feed_configured") is True or record.get("fetched_from_network") is True:
        raise CardError("AZNEWS-LIVE", "a feed was marked live though this package did not fetch one")
    return record


def join_card(records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = _RECORDS if records is None else records
    flags = _flags(rows)
    return {
        "name": "AZNews",
        "spec": JOIN,
        "standalone": True,
        "fourdmap_standalone": True,
        "joined_into": "4dmap",
        "software_tab": False,
        "mcp_tool": False,
        "catalog_slug": None,
        "installed": False,
        "merged": False,
        "live": flags["live"],
        "join_live": flags["join_live"],
        "aznews_live": flags["aznews_live"],
        "fourdmap_live": False,
        "catalog_live": False,
        "feed_configured": False,
        "fetched_from_network": False,
        "source_present": flags["source_present"],
        "library_map": LIBRARY_MAP,
        "library_map_is_aznews": False,
        "library_cite_merged": False,
        "absent_code": None if flags["source_present"] else ABSENT_CODE,
        "absent_module": ABSENT_MODULE,
        "absent_source": ABSENT_SOURCE,
        "paths": {
            "standalone": {"callable": True, "op": "news_ingest"},
            "joined": {"callable": True, "ops": ["news_pin", "news_open"]},
            "fourdmap_without_news": {"callable": True, "op": "pin"},
        },
        "cross_tether": _cross(),
        "author": AUTHOR,
    }


def _summary(op: str, item: dict[str, Any] | None, records: list[dict[str, Any]], *, on_map: bool = False) -> str:
    ready = _join_ready(records)
    if item is None:
        return _sentence(
            "No news source is present. AZNews can store a story without a pin (news_ingest). "
            "4DMap can pin without a story. The join (news_pin, news_open) reads a stored story back from a pin. "
            f"{ABSENT_MODULE} does not fetch a feed. No {ABSENT_SOURCE} is configured. "
            "The join is not marked live. AZNews is not marked live. 4DMap is not marked live."
        )
    if item.get("fixture"):
        where = "on a 4DMap pin" if on_map else "on the AZNews standalone path"
        return _sentence(
            f"A labeled fixture was stored {where}. Date {item['date']}, event {item['event']}. "
            "A fixture is not a news source. The join is not marked live. AZNews is not marked live. 4DMap is not marked live."
        )
    if ready:
        return _sentence(
            f"A fetched item is stored on AZNews and read back from a 4DMap pin. Date {item['date']}, event {item['event']}. "
            "The join is live for that item. This package did not GET a feed. "
            "4DMap is not marked live as a product. AZNews is not a Softwares card and is not merged. "
            "AZ-OS and the human interface were not updated."
        )
    if item.get("fetched") and on_map:
        return _sentence(
            f"A fetched item is on a 4DMap pin. Date {item['date']}, event {item['event']}. "
            "The standalone AZNews copy is not stored yet, or the pin was not opened, so the join is not marked live. "
            "AZNews is not marked live. 4DMap is not marked live."
        )
    if item.get("fetched"):
        return _sentence(
            f"A fetched item is stored on the AZNews standalone path. Date {item['date']}, event {item['event']}. "
            "It is not yet read back from a 4DMap pin, so the join is not marked live. "
            "AZNews is not marked live. 4DMap is not marked live."
        )
    where = "on a 4DMap pin" if on_map else "on the AZNews standalone path, not on a pin"
    return _sentence(
        f"A supplied item is stored {where}. Date {item['date']}, event {item['event']}. "
        "It was not fetched by this package. The join is not marked live. AZNews is not marked live. 4DMap is not marked live."
    )


def _refuse(op: str, code: str, text: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    summary = _sentence(text)
    return _seal(
        {
            "ok": False,
            "refused": True,
            "op": op,
            "code": code,
            "absent_module": ABSENT_MODULE if code == ABSENT_CODE else None,
            "absent_source": ABSENT_SOURCE if code == ABSENT_CODE else None,
            "message": summary,
            "summary": summary,
            "note": summary,
            "records": _export(records),
        },
        records,
    )


def _receipt(item: dict[str, Any], username: str, records: list[dict[str, Any]], *, on_map: bool) -> dict[str, Any]:
    document_hash = _document_hash(item)
    prev = records[-1]["receipt"]["primary"] if records and records[-1].get("receipt") else GENESIS_PREV
    primary = _sha({"document_hash": document_hash, "prev": prev, "on_map": on_map})
    secondary = _sha({"document_hash": document_hash, "username": username, "on_map": on_map})
    for row in records:
        receipt = row.get("receipt") or {}
        if receipt.get("secondary") == secondary:
            raise CardError(
                "AZNEWS-DOUBLE",
                "This document is already stored for that username on this path. It was not written again.",
            )
    return {
        "kind": "aznews-receipt",
        "document_hash": document_hash,
        "primary": primary,
        "primary_prev": prev,
        "secondary": secondary,
        "on_map": on_map,
        "username": username,
        "wording": item["wording"],
        "image_hash": item.get("image_hash"),
        "score": item.get("score"),
        "author": AUTHOR,
    }


def _store_item(item: dict[str, Any], payload: dict[str, Any], records: list[dict[str, Any]], *, on_map: bool, card: dict[str, Any] | None) -> dict[str, Any]:
    username = _username(payload)
    receipt = _receipt(item, username, records, on_map=on_map)
    row = {
        "document_hash": receipt["document_hash"],
        "on_map": on_map,
        "opened": False,
        "item": item,
        "pin_id": card.get("id") if card else None,
        "card": card,
        "receipt": receipt,
        "open_receipt": None,
        "username": username,
    }
    records.append(row)
    return row


def _result(op: str, item: dict[str, Any], row: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    summary = _summary(op, item, records, on_map=bool(row["on_map"]))
    body: dict[str, Any] = {
        "ok": True,
        "refused": False,
        "op": op,
        "path": "joined" if row["on_map"] else "standalone",
        "on_map": row["on_map"],
        "fixture": item.get("fixture") is True,
        "fixture_is_source": False,
        "fixture_label": item.get("fixture_label") or None,
        "item_id": item["id"],
        "date": item["date"],
        "event": item["event"],
        "headline": item["headline"],
        "wording": item["wording"],
        "place": item["place"],
        "lat": item["lat"],
        "lon": item["lon"],
        "image_hash": item.get("image_hash"),
        "image_gap": item.get("image_gap") is True,
        "score": item.get("score"),
        "document_hash": row["document_hash"],
        "receipt": row["receipt"],
        "records": _export(records),
        "summary": summary,
        "note": summary,
        "round_trip": _join_ready(records),
    }
    if row.get("card"):
        body["card"] = row["card"]
        body["id"] = row["card"].get("id")
        body["h"] = row["card"].get("h")
        body["pin_frame"] = {
            "kind": PIN_FRAME_KIND,
            "date": item["date"],
            "event": item["event"],
            "place": item["place"],
            "lat": item["lat"],
            "lon": item["lon"],
            "surface": "MOCK" if item.get("fixture") else "REAL",
        }
    return _seal(body, records)


def _has_item(payload: dict[str, Any]) -> bool:
    raw = payload.get("item") if isinstance(payload.get("item"), dict) else payload
    if not isinstance(raw, dict):
        return False
    return any(raw.get(key) not in (None, "") for key in ("event", "wording", "body", "date", "headline", "place", "geo"))


def _prev_hash(payload: dict[str, Any], cards: list[dict[str, Any]] | None) -> str:
    if payload.get("prev"):
        return str(payload["prev"])
    if cards:
        last = cards[-1]
        if isinstance(last, dict) and last.get("h"):
            return str(last["h"])
    return GENESIS_PREV


def _pin_card(item: dict[str, Any], prev: str) -> dict[str, Any]:
    src = "aznews-fixture" if item.get("fixture") else ("aznews-fetch" if item.get("fetched") else "aznews")
    note = f"{'Fixture' if item.get('fixture') else 'News'} pin {item['event']}"
    return make_card(
        t={
            "kind": PIN_FRAME_KIND,
            "clock": item["date"],
            "event": item["event"],
            "place": item["place"],
            "lat": item["lat"],
            "lon": item["lon"],
            "surface": "MOCK" if item.get("fixture") else "REAL",
            "fixture": item.get("fixture") is True,
            "join": "aznews",
            "news_id": item["id"],
        },
        src=src,
        note=note,
        prev=prev,
        pi=PI_EMPTY,
    )


def _match(payload: dict[str, Any], records: list[dict[str, Any]], *, on_map: bool) -> dict[str, Any] | None:
    pool = [row for row in records if row["on_map"] is on_map] if on_map else list(records)
    wanted = str(payload.get("item_id") or payload.get("pin_id") or payload.get("id") or "").strip()
    raw = payload.get("item") if isinstance(payload.get("item"), dict) else payload
    if not wanted and isinstance(raw, dict):
        wanted = str(raw.get("id") or raw.get("item_id") or "").strip()
    if wanted:
        for row in pool:
            if row["item"].get("id") == wanted or row.get("pin_id") == wanted:
                return row
        return None
    if not isinstance(raw, dict):
        return None
    clock = _clock(raw.get("date") or raw.get("paper_date"))
    event = str(raw.get("event") or "").strip()
    place = str(raw.get("place") or raw.get("geo") or "").strip()
    if not clock or not event:
        return None
    for row in pool:
        item = row["item"]
        if item.get("date") == clock and item.get("event") == event and (not place or item.get("place") == place):
            return row
    return None


def news_status(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    if _mentions_library(payload):
        records, _explicit = _desk(payload)
        return _refuse(
            "news_status",
            LIBRARY_CODE,
            "The library map is a corpus cite. It is not AZNews and it is not this join.",
            records,
        )
    records, _explicit = _desk(payload)
    summary = _summary("news_status", None, records)
    if _join_ready(records):
        summary = _summary("news_status", _fetched_rows(records)[-1]["item"], records, on_map=True)
    elif not _fetched_rows(records):
        summary = _summary("news_status", None, records)
    return _seal(
        {
            "ok": True,
            "refused": False,
            "op": "news_status",
            "code": None if _fetched_rows(records) else ABSENT_CODE,
            "absent_module": ABSENT_MODULE,
            "absent_source": ABSENT_SOURCE,
            "standalone_items": sum(1 for row in records if not row["on_map"]),
            "pins": sum(1 for row in records if row["on_map"]),
            "paths": join_card(records)["paths"],
            "summary": summary,
            "note": summary,
            "records": _export(records),
            "round_trip": _join_ready(records),
        },
        records,
    )


def news_ingest(payload: dict[str, Any], cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    _ = cards
    if _mentions_library(payload):
        records, _explicit = _desk(payload)
        return _refuse(
            "news_ingest",
            LIBRARY_CODE,
            "The library map is a corpus cite. Pass it to library_pin. It is not AZNews.",
            records,
        )
    records, _explicit = _desk(payload)
    if not _has_item(payload):
        return _refuse(
            "news_ingest",
            ABSENT_CODE,
            f"AZNews refused this ingest. No news source is present. {ABSENT_MODULE} returned no item, and no {ABSENT_SOURCE} is configured. Nothing was written.",
            records,
        )
    item = _item_from(payload)
    row = _store_item(item, payload, records, on_map=False, card=None)
    return _result("news_ingest", item, row, records)


def news_pin(payload: dict[str, Any], cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if _mentions_library(payload):
        records, _explicit = _desk(payload)
        return _refuse(
            "news_pin",
            LIBRARY_CODE,
            "The library map is a corpus cite. Passing it to news_pin refuses. Use library_pin for a corpus card.",
            records,
        )
    records, _explicit = _desk(payload)
    if not _has_item(payload):
        found = _match(payload, records, on_map=False)
        if found is None:
            return _refuse(
                "news_pin",
                ABSENT_CODE,
                f"AZNews refused this pin. No news source is present. {ABSENT_MODULE} returned no item, and no {ABSENT_SOURCE} is configured. Nothing was written.",
                records,
            )
        item = dict(found["item"])
    else:
        item = _item_from(payload)
    card = _pin_card(item, _prev_hash(payload, cards))
    row = _store_item(item, payload, records, on_map=True, card=card)
    return _result("news_pin", item, row, records)


def news_open(payload: dict[str, Any], cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    _ = cards
    if _mentions_library(payload):
        records, _explicit = _desk(payload)
        return _refuse("news_open", LIBRARY_CODE, "The library map is not an AZNews item.", records)
    records, _explicit = _desk(payload)
    path = str(payload.get("path") or "joined").strip().lower()
    on_map = path not in {"standalone", "aznews"}
    if not records:
        return _refuse(
            "news_open",
            ABSENT_CODE,
            f"AZNews refused this open. No news source is present. {ABSENT_MODULE} has no stored item. Nothing was invented.",
            records,
        )
    found = _match(payload, records, on_map=on_map)
    if found is None:
        return _refuse(
            "news_open",
            "AZNEWS-NO-MATCH",
            "No stored item matches that id, date, event, and place. Nothing was invented.",
            records,
        )
    if on_map and not found["on_map"]:
        return _refuse("news_open", "AZNEWS-NO-MATCH", "That story is not pinned. Nothing was invented.", records)
    item = found["item"]
    if found["on_map"] and not found.get("opened"):
        found["opened"] = True
        found["open_receipt"] = {"op": "news_open", "open_hash": _open_hash(found["document_hash"], item["wording"])}
    summary = "Opened. " + _summary("news_open", item, records, on_map=bool(found["on_map"]))
    return _seal(
        {
            "ok": True,
            "refused": False,
            "op": "news_open",
            "path": "joined" if found["on_map"] else "standalone",
            "on_map": found["on_map"],
            "fixture": item.get("fixture") is True,
            "fixture_is_source": False,
            "item_id": item["id"],
            "id": found.get("pin_id"),
            "date": item["date"],
            "event": item["event"],
            "headline": item["headline"],
            "wording": item["wording"],
            "place": item["place"],
            "score": item.get("score"),
            "image_hash": item.get("image_hash"),
            "document_hash": found["document_hash"],
            "open_receipt": found.get("open_receipt"),
            "records": _export(records),
            "summary": summary,
            "note": summary,
            "round_trip": _join_ready(records),
        },
        records,
    )


def run_aznews(op: str, payload: dict[str, Any] | None = None, cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = payload or {}
    if op == "news_status":
        return news_status(payload)
    if op == "news_ingest":
        return news_ingest(payload, cards)
    if op == "news_pin":
        return news_pin(payload, cards)
    if op == "news_open":
        return news_open(payload, cards)
    raise CardError("UNKNOWN_OP", f"unknown op {op}")
