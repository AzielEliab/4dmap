"""Honesty gaps after the rotating globe. Author: Aziel Eliab only."""

from __future__ import annotations

from pathlib import Path
from urllib.error import URLError

from fourdmap.area import triad_view
from fourdmap.earth import ocean_slice
from fourdmap.ling import PUBLIC_UNREACHABLE, collect_corpus
from fourdmap.ops import dispatch
from fourdmap.scope import LAMB_LENS, SOFTWARES_NOTE, SOFTWARES_ROSTER_HERE

ROOT = Path(__file__).resolve().parents[1]


def _pin(**extra):
    payload = {
        "event": "Harbor fire watch",
        "date": "1912-04-14",
        "lat": 44.65,
        "lon": -63.57,
        "place": "Halifax",
        "who": ["Mara Quill"],
        "surface": "MOCK",
        "src": "operator",
    }
    payload.update(extra)
    return payload


def test_each_pin_carries_an_unfilled_triad_and_a_join_is_not_another_pin() -> None:
    first = dispatch("library_pin", _pin(id="4dm-tri-a"))
    second = dispatch(
        "library_pin",
        _pin(id="4dm-tri-b", event="Second watch", date="1913-01-02", lat=51.51, lon=-0.12, place="London", prev=first["h"]),
        [first["card"]],
    )
    joined = dispatch(
        "join",
        {"left": first["id"], "right": second["id"], "join_type": "T-DELTA"},
        [first["card"], second["card"]],
    )
    plotted = dispatch("plot", {}, [first["card"], second["card"], joined["card"]])
    assert plotted["n"] == 2
    assert plotted["gis"] is False
    triad = plotted["pins"][0]["triad"]
    assert triad["spec"] == "AKM-TRIAD-1.0"
    assert triad["filled"] == 2
    assert triad["met"] is False
    assert triad["collapsed"] is False
    assert triad["posterior_is_truth"] is False
    assert [slot["present"] for slot in triad["slots"]] == [True, True, False, False]
    empty = triad_view({"possibility": {"label": "possibility", "value": 0.4}}, event="", clock="", lat=1.0, lon=2.0)
    assert empty["slots"][0]["present"] is False
    assert empty["filled"] == 1
    assert "stays empty" in empty["slots"][0]["note"]


def test_public_index_cards_stay_undated_and_unpinned() -> None:
    found = collect_corpus(
        public={
            "records": [
                {
                    "title": "Loose catalog card",
                    "record_id": "AZDOC-TEST",
                    "created_utc": "2020-01-01T00:00:00Z",
                    "author": "Aziel Eliab",
                    "triad_display": 45,
                }
            ]
        }
    )
    row = next(item for item in found["candidates"] if item.get("record_id") == "AZDOC-TEST")
    assert row["date"] is None
    assert row["lat"] is None
    assert row["lon"] is None
    assert row["who"] == []
    assert row["seal"] is False
    assert row["era"] == "undated / era unknown"
    assert row["surface"] == "CATALOG"
    assert "upload time is not used" in row["reason"]
    assert "no geo in source" in row["reason"]
    assert "2020" not in row["reason"]
    assert "Elroi" not in row["reason"]
    assert "not an AKM 3-of-4" in row["reason"]
    assert "45" in row["reason"]
    assert "None were sealed." in found["message"]


def test_unreachable_public_index_invents_nothing(monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise URLError("down")

    monkeypatch.setattr("fourdmap.ling.urlopen", boom)
    found = collect_corpus(public=True)
    assert PUBLIC_UNREACHABLE in found["message"]
    assert all(row.get("surface") != "CATALOG" for row in found["candidates"])
    assert any(row.get("event") == "Market morning" for row in found["candidates"])


def test_ocean_layers_do_not_invent_an_image() -> None:
    coast = ocean_slice("coast", 1914)
    assert coast["image"] is False
    assert coast["exact"] is False
    assert "no public coastline-change survey" in coast["note"]
    assert "No public image is drawn." in coast["note"]
    assert "Coastline for 1914" not in coast["note"]
    bathy = ocean_slice("bathymetry", 1914)
    assert bathy["image"] is False
    assert "No public image is drawn." in bathy["note"]
    assert "not 1914" in bathy["note"]


def test_page_and_worker_keep_the_honesty_lines() -> None:
    html = (ROOT / "fourdmap" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "fourdmap" / "static" / "globe.js").read_text(encoding="utf-8")
    home = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
    lattice = (ROOT / "workers/download-tracker/src/lattice.js").read_text(encoding="utf-8")
    assert "Lamb Lens: Service → Clarity → Peace." in html
    assert 'id="layers-close"' in html
    assert 'id="pin-scores"' in html
    assert html.index("<legend>Oceanography</legend>") < html.index("<legend>Major geo features</legend>")
    assert "triadShort" in script
    assert "catalog card, not a geo pin" in script
    assert "placePinScores" in script
    assert "Lamb Lens: Service → Clarity → Peace." in home
    assert "geo[i - 1]" not in home
    assert "geo[i-1]" not in home
    assert "inner.trajectories" in home
    assert "not labeled" in home
    assert "export function citesPair" in lattice
    assert "citesPair(card) ? null : pinFrameOf(card)" in lattice
    assert "exact_point: false" in lattice
    assert LAMB_LENS == "Service → Clarity → Peace"
    assert SOFTWARES_ROSTER_HERE is False
    assert "does not add catalog rows" in SOFTWARES_NOTE
    assert "ShadowLock" in SOFTWARES_NOTE
