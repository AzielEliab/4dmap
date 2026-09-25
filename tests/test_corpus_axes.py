"""Corpus files across geo, date, time, person, and location. Author: Aziel Eliab only."""

from __future__ import annotations

from fourdmap.ling import NO_GEO, NO_PERSON, NO_TIME, PLACE_ESTIMATED, UNDATED, collect_corpus, era_bucket
from fourdmap.ops import dispatch


def _by_event(payload, event):
    return next(row for row in payload["candidates"] if row["event"] == event)


def test_every_shipped_corpus_file_is_read_and_dated_pins_keep_their_era() -> None:
    found = collect_corpus()
    names = set(found["files"])
    for required in (
        "corpus-mention.txt",
        "1914-cairo.json",
        "1945-rome.json",
        "1994-tokyo.json",
        "2010-lisbon.json",
        "undated-london.json",
    ):
        assert required in names
    assert found["n"] >= 6
    cairo = _by_event(found, "River gauge")
    assert cairo["seal"] is True
    assert cairo["date"] == "1914-06-02"
    assert cairo["time"] == "07:40"
    assert cairo["who"] == ["Ned Brooks"]
    assert cairo["place"] == "Cairo"
    assert cairo["era"] == "1914"
    assert PLACE_ESTIMATED in cairo["reason"]
    assert cairo["surface"] == "MOCK"
    assert "not a recovered library document" in cairo["reason"]
    rome = _by_event(found, "Station count")
    assert rome["era"] == "1945"
    assert rome["who"] == ["Mara Quill"]
    tokyo = _by_event(found, "Harbor list")
    assert tokyo["era"] == "1994"
    assert tokyo["time"] is None
    assert NO_TIME in tokyo["reason"]
    lisbon = _by_event(found, "Quay note")
    assert lisbon["era"] == "2010"
    paris = _by_event(found, "Market morning")
    assert paris["seal"] is True
    assert paris["era"] == "1914"
    assert era_bucket("1920-05-03") == "1914"
    undated = _by_event(found, "Loose margin")
    assert undated["date"] is None
    assert undated["era"] == UNDATED
    assert undated["seal"] is False
    assert UNDATED in undated["reason"]
    assert NO_GEO not in undated["reason"]
    assert NO_PERSON not in undated["reason"]
    thin = next(row for row in found["candidates"] if row.get("date") == "1916-01-01")
    assert thin["seal"] is False
    assert "waits for a person" in thin["reason"]
    assert NO_GEO in thin["reason"]
    assert NO_PERSON in thin["reason"]


def test_same_people_fold_and_a_different_person_does_not() -> None:
    pinned = dispatch(
        "library_pin",
        {
            "event": "River gauge",
            "date": "1914-06-02",
            "time": "07:40",
            "lat": 30.04,
            "lon": 31.24,
            "place": "Cairo",
            "who": ["Ned Brooks"],
            "surface": "MOCK",
            "src": "aziel-corpus",
        },
    )
    assert pinned["card"]["t"]["time"] == "07:40"
    again = collect_corpus([pinned["card"]])
    cairo = _by_event(again, "River gauge")
    assert cairo["folded"] is True
    assert cairo["seal"] is False
    other = dispatch(
        "library_pin",
        {
            "event": "Station count",
            "date": "1945-05-01",
            "lat": 41.89,
            "lon": 12.49,
            "place": "Rome",
            "who": ["Ada Quill"],
            "surface": "MOCK",
            "src": "operator",
        },
    )
    mixed = collect_corpus([other["card"]])
    rome = _by_event(mixed, "Station count")
    assert rome["folded"] is False
    assert rome["seal"] is True
    assert rome["who"] == ["Mara Quill"]
