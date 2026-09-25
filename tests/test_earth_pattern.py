"""Era frames, pattern tethers, and corpus matches. Author: Aziel Eliab only."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.request import urlopen

from fourdmap.earth import lidar_slice, ocean_slice, satellite_slice, topo_slice
from fourdmap.names import NO_ERA_LABEL, era_label
from fourdmap.ling import BADGE, load_corpus_text, propose
from fourdmap.ops import dispatch
from fourdmap.pattern import pattern_matrix
from fourdmap.scope import LIVE_OPS
from fourdmap.server import make_server

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


def test_satellite_names_the_real_frame() -> None:
    early = satellite_slice(1914)
    assert early["exact"] is False
    assert early["frame_year"] == 2000
    assert "nearest public frame: 2000" in early["note"]
    assert "not 1914" in early["note"]
    assert "1914 imagery" not in early["note"].replace("not 1914 imagery", "")
    later = satellite_slice(2010)
    assert later["exact"] is True
    assert later["frame_date"] == "2010-07-01"
    assert "not 2010" not in later["note"]
    assert "NASA GIBS" in later["note"]


def test_lidar_and_ocean_cite_the_public_slice() -> None:
    lidar = lidar_slice(1914)
    assert "modern elevation" in lidar["note"]
    assert "no LiDAR for this era" in lidar["note"]
    assert lidar["image"] is False
    early = ocean_slice("sst", 1914)
    assert early["exact"] is False
    assert "nearest public frame: 1981" in early["note"]
    assert "not 1914" in early["note"]
    later = ocean_slice("sst", 2010)
    assert later["exact"] is True
    assert later["frame_date"] == "2010-07-01"
    bathy = ocean_slice("bathymetry", 1914)
    assert bathy["frame_year"] == 2023
    assert "not 1914" in bathy["note"]
    assert bathy["image"] is False
    ice = ocean_slice("seaice", 1910)
    assert "nearest public frame: 1978" in ice["note"]


def test_shared_person_is_one_tether_and_strangers_are_not() -> None:
    first = dispatch("library_pin", _pin(id="4dm-pat-a"))
    second = dispatch(
        "library_pin",
        _pin(id="4dm-pat-b", event="Second watch", date="1913-01-02", lat=51.51, lon=-0.12, place="London", prev=first["h"]),
        [first["card"]],
    )
    cards = [first["card"], second["card"]]
    matrix = pattern_matrix(cards)
    assert matrix["n"] == 1
    edge = matrix["edges"][0]
    assert "shared person" in edge["reason"]
    assert "Mara" in edge["reason"]
    assert "km apart" in edge["distance"]
    assert edge["on_lattice"] is False
    assert matrix["rows"]
    stranger = dispatch(
        "library_pin",
        _pin(id="4dm-pat-c", event="Quiet bell", date="1915-02-02", who=["Ada North"], place="Paris", lat=48.86, lon=2.35),
        [],
    )
    alone = pattern_matrix([first["card"], stranger["card"]])
    assert alone["n"] == 0
    assert alone["message"] == "No connected pattern yet."
    chained = pattern_matrix(cards)
    assert chained["n"] == 1


def test_cause_span_and_explicit_tether_share_one_chain() -> None:
    left = dispatch("library_pin", _pin(id="4dm-cause-a", who=["Ada North"], cause="warehouse fire"))
    right = dispatch(
        "library_pin",
        _pin(
            id="4dm-cause-b",
            event="Second bell",
            date="1913-06-01",
            lat=48.86,
            lon=2.35,
            place="Paris",
            who=["Ned Brooks"],
            cause="warehouse fire",
            prev=left["h"],
        ),
        [left["card"]],
    )
    caused = pattern_matrix([left["card"], right["card"]])
    assert caused["n"] == 1
    assert caused["edges"][0]["reason"] == "shared cause warehouse fire"
    spanned = dispatch("span", {"from_id": left["id"], "to_id": right["id"]}, [left["card"], right["card"]])
    neighbors = pattern_matrix([left["card"], right["card"], spanned["card"]])
    assert neighbors["n"] == 1
    assert neighbors["edges"][0]["on_lattice"] is True
    joined = dispatch(
        "join",
        {"left": left["id"], "right": right["id"], "join_type": "T-PI", "note": "why tethered: shared cause warehouse fire"},
        [left["card"], right["card"]],
    )
    sealed = pattern_matrix([left["card"], right["card"], joined["card"]])
    assert sealed["edges"][0]["reason"].startswith("why tethered")
    assert sealed["edges"][0]["on_lattice"] is True
    plotted = dispatch("plot", {}, [left["card"], right["card"], joined["card"]])
    assert plotted["n"] == 2


def test_shadow_link_needs_the_same_name_on_both_pins() -> None:
    east = dispatch("library_pin", _pin(id="4dm-sh-a", event="Morning intake east", who=["Ada North"]))
    west = dispatch(
        "library_pin",
        _pin(id="4dm-sh-b", event="Morning intake west", date="1913-01-02", lat=51.51, lon=-0.12, place="London", who=["Ned Brooks"]),
        [east["card"]],
    )
    quiet = pattern_matrix([east["card"], west["card"]], [{"label": "Hold review", "slug": "peacelock", "input_id": "hold/sample"}])
    assert quiet["n"] == 0
    linked = pattern_matrix(
        [east["card"], west["card"]],
        [{"label": "Morning intake", "slug": "azmail", "input_id": "inbox/sample"}],
    )
    assert linked["n"] == 1
    assert linked["edges"][0]["reason"] == "ShadowLock link"


def test_corpus_match_seals_folds_and_waits() -> None:
    text = load_corpus_text()
    found = propose(text, source="corpus", name="corpus-mention.txt")
    assert found["badge"] == "from corpus/upload"
    high = next(row for row in found["candidates"] if row["seal"])
    assert high["badge"] == BADGE
    assert high["event"] == "Market morning"
    assert high["date"] == "1920-05-03"
    assert high["place"] == "Paris"
    assert "Paris" in high["reason"]
    assert "1920" in high["reason"]
    low = next(row for row in found["candidates"] if "1916" in row["reason"])
    assert low["seal"] is False
    assert "waits for a person" in low["reason"]
    pinned = dispatch(
        "library_pin",
        _pin(id="4dm-corp", event="Market morning", date="1920-05-03", lat=48.86, lon=2.35, place="Paris", who=[]),
    )
    folded = propose("Market morning in Paris on 3 May 1920.", source="upload", name="note.txt", cards=[pinned["card"]])
    row = folded["candidates"][0]
    assert row["folded"] is True
    assert row["seal"] is False
    assert row["existing_id"] == pinned["id"]


def test_topography_is_separate_from_lidar_and_names_the_dem() -> None:
    early = topo_slice(1914)
    later = topo_slice(2010)
    assert early["layer"] == "topography"
    assert early["image"] is True
    assert "SRTM_Color_Index" in early["url"]
    assert "modern topography; no era sheet for this year." in early["note"]
    assert "not a 1914 topographic sheet" in early["note"]
    assert "NASA SRTM" in early["note"]
    assert "2000-02-11" in early["note"]
    assert "not a 2010 topographic sheet" in later["note"]
    assert "no LiDAR" not in early["note"]
    lidar = lidar_slice(1914)
    assert lidar["layer"] == "lidar"
    assert early["source"] != lidar["source"]


def test_era_names_come_from_the_basemap_and_are_not_invented() -> None:
    anatolia = era_label(38.9, 35.4, 1914, "inland")
    assert anatolia["era_name"] == "Ottoman Empire"
    assert anatolia["modern_name"] == "Turkey"
    assert anatolia["place_line"].startswith("Ottoman Empire")
    assert "Modern name: Turkey" in anatolia["place_line"]
    assert "Ottoman Empire" in anatolia["terms"]
    assert "Turkey" in anatolia["terms"]
    assert anatolia["era_name"] != "Constantinople"
    today = era_label(38.9, 35.4, 2010, "inland")
    assert today["era_name"] == "Turkey"
    assert "Modern name:" not in today["place_line"]
    istanbul = era_label(41.01, 28.98, 1914, "Istanbul")
    assert istanbul["era_name"] == ""
    assert istanbul["city"] == "Istanbul"
    assert NO_ERA_LABEL in istanbul["place_line"]
    assert "constantinople" in [term.casefold() for term in istanbul["terms"]]
    assert istanbul["city_era"] is None


def test_page_lists_ocean_pattern_and_corpus() -> None:
    html = (ROOT / "fourdmap" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "fourdmap" / "static" / "globe.js").read_text(encoding="utf-8")
    assert "Oceanography" in html
    assert 'id="chip-satellite"' in html
    assert 'id="pattern"' in html
    assert 'id="corpus-sync"' in html
    assert 'id="act-tether"' in html
    assert "No connected pattern yet." in html
    assert "from corpus/upload" in html
    assert "Event, person, time, or place" in html
    assert "Topography" in html
    assert 'id="chip-topo"' in html
    assert 'id="layer-topo"' in html
    assert "refreshPlaceLabels" in script
    assert "why tethered" in script
    assert "timeHit" in script
    for op in ("library_pin", "lattice_tip", "verify_chain"):
        assert op in LIVE_OPS
    assert "pattern_matrix" not in LIVE_OPS


def test_frame_and_pattern_routes_do_not_invent_tiles(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FOURDMAP_LATTICE", str(tmp_path / "lattice.json"))
    httpd = make_server(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    try:
        with urlopen(f"http://127.0.0.1:{port}/v1/layers/frame?layer=topography&year=1914") as response:
            topo = json.loads(response.read().decode("utf-8"))
        assert "modern topography; no era sheet for this year." in topo["note"]
        with urlopen(f"http://127.0.0.1:{port}/v1/places/era?lat=38.9&lon=35.4&year=1914") as response:
            place = json.loads(response.read().decode("utf-8"))
        assert place["era_name"] == "Ottoman Empire"
        assert place["modern_name"] == "Turkey"
        with urlopen(f"http://127.0.0.1:{port}/v1/layers/frame?layer=satellite&year=1914") as response:
            frame = json.loads(response.read().decode("utf-8"))
        assert frame["frame_year"] == 2000
        assert "nearest public frame: 2000" in frame["note"]
        with urlopen(f"http://127.0.0.1:{port}/v1/pattern") as response:
            matrix = json.loads(response.read().decode("utf-8"))
        assert matrix["message"] == "No connected pattern yet."
        with urlopen(f"http://127.0.0.1:{port}/v1/corpus") as response:
            corpus = json.loads(response.read().decode("utf-8"))
        assert any(row.get("seal") for row in corpus["candidates"])
    finally:
        httpd.shutdown()
        thread.join(timeout=2)
