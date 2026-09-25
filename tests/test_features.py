"""Public geo features and subsurface entrances. Author: Aziel Eliab only."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.request import urlopen

from fourdmap.features import (
    CATALOG_ONLY,
    EMPTY_SUBSURFACE,
    NO_ERA_NAME,
    NO_EXTENT,
    NO_FEATURE,
    _shape_for,
    list_features,
    list_subsurface,
)
from fourdmap.ops import dispatch
from fourdmap.lattice import plot_model
from fourdmap.server import make_server

ROOT = Path(__file__).resolve().parents[1]


def test_major_features_are_cited_and_not_invented() -> None:
    payload = list_features(1914)
    names = {row["name"]: row for row in payload["features"]}
    for required in (
        "Mount Vesuvius",
        "Mariana Trench",
        "Bermuda Islands",
        "Chicxulub crater",
        "Niagara Falls",
        "Nile",
        "Lake Victoria",
    ):
        assert required in names
    assert names["Mount Vesuvius"]["type"] == "volcano"
    assert names["Mariana Trench"]["type"] == "deep"
    assert "Wikidata" in names["Mariana Trench"]["source"]
    bermuda = names["Bermuda Islands"]
    assert bermuda["type"] == "region"
    assert "Natural Earth" in bermuda["source"]
    assert "No mystery polygon is drawn." in bermuda["era_note"]
    assert NO_ERA_NAME in bermuda["era_note"]
    assert names["Nile"]["line"]
    assert names["Lake Victoria"]["type"] == "lake"
    blob = json.dumps(payload).lower()
    assert "triangle" not in blob
    assert "hollow" not in blob
    assert payload["message"] == ""


def test_feature_type_filter_and_missing_type_stay_honest() -> None:
    volcanoes = list_features(2010, "volcano")
    assert volcanoes["n"] >= 1
    assert all(row["type"] == "volcano" for row in volcanoes["features"])
    assert NO_ERA_NAME in volcanoes["features"][0]["era_note"]
    empty = list_features(1914, "not-a-real-type")
    assert empty["n"] == 0
    assert empty["message"] == NO_FEATURE


def test_subsurface_cites_survey_year_and_empty_places() -> None:
    payload = list_subsurface(1914)
    tunnel = next(row for row in payload["features"] if row["name"] == "Channel Tunnel")
    assert tunnel["type"] == "tunnel"
    assert "Survey year 1994" in tunnel["era_note"]
    assert "Wikidata P1619" in tunnel["era_note"]
    assert "not a 1914 survey plate" in tunnel["era_note"]
    assert "no public survey plate in this package" in tunnel["era_note"]
    cave = next(row for row in payload["features"] if row["name"] == "Mammoth Cave")
    assert "no survey year in source" in cave["era_note"]
    other = list_subsurface(1914, "other")
    assert other["n"] == 0
    assert other["message"] == EMPTY_SUBSURFACE
    missed = list_subsurface(1914, lat=0, lon=0)
    assert missed["n"] == 0
    assert missed["message"] == EMPTY_SUBSURFACE
    blob = json.dumps(payload).lower()
    assert "hollow" not in blob


def test_panel_lists_geo_features_above_subsurface() -> None:
    html = (ROOT / "fourdmap" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "fourdmap" / "static" / "globe.js").read_text(encoding="utf-8")
    assert html.index("<legend>Major geo features</legend>") < html.index("<legend>Subsurface</legend>")
    assert 'id="layer-features"' in html
    assert 'id="layer-sub"' in html
    assert "no public subsurface map here." in script
    body = script.split("function showFeature", 1)[1].split("function addCatalogLine", 1)[0]
    assert "library_pin" not in body
    assert "post(" not in body
    assert "It is not an event pin." in body


def test_feature_routes_do_not_seal_pins(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FOURDMAP_LATTICE", str(tmp_path / "lattice.json"))
    httpd = make_server(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    try:
        with urlopen(f"http://127.0.0.1:{port}/v1/features?year=1914&types=deep") as response:
            deeps = json.loads(response.read().decode("utf-8"))
        assert any(row["name"] == "Mariana Trench" for row in deeps["features"])
        with urlopen(f"http://127.0.0.1:{port}/v1/subsurface?year=1914&types=other") as response:
            other = json.loads(response.read().decode("utf-8"))
        assert other["message"] == EMPTY_SUBSURFACE
        with urlopen(f"http://127.0.0.1:{port}/v1/subsurface?lat=0&lon=0&year=2010") as response:
            missed = json.loads(response.read().decode("utf-8"))
        assert missed["message"] == EMPTY_SUBSURFACE
        assert "not a 2010 survey plate" not in missed["message"]
    finally:
        httpd.shutdown()
        thread.join(timeout=2)


def _nile_pins(lat, lon, events):
    cards = []
    dates = ("1912-04-14", "1913-01-02", "1914-06-01")
    for event, date in zip(events, dates):
        out = dispatch(
            "library_pin",
            {
                "event": event,
                "date": date,
                "lat": lat,
                "lon": lon,
                "place": "Nile",
                "src": "operator",
                "note": "place words: Nile",
            },
            cards,
        )
        cards.append(out["card"])
    return cards


def test_features_keep_modern_shape_and_recalibrate_only_with_enough_pins() -> None:
    bare = next(row for row in list_features(1914)["features"] if row["catalog_name"] == "Nile")
    assert NO_EXTENT in bare["era_note"]
    assert CATALOG_ONLY in bare["era_note"]
    assert bare["recalibrated"] is False
    assert bare["disc"] is None
    lat, lon = bare["lat"], bare["lon"]
    shaped, shape = _shape_for({"name": "Nile", "lat": lat, "lon": lon}, 1914)
    assert shape == NO_EXTENT
    assert shaped["lat"] == lat and shaped["lon"] == lon
    dated, dated_note = _shape_for(
        {
            "name": "Nile",
            "lat": lat,
            "lon": lon,
            "extents": [{"year": 1994, "lat": 1.0, "lon": 2.0, "source": "public sheet"}],
        },
        1914,
    )
    assert dated["lat"] == 1.0
    assert "nearest public extent: 1994" in dated_note
    assert "not a 1914 extent" in dated_note

    few = _nile_pins(lat, lon, ("Flood watch", "Bank survey"))
    held = next(row for row in list_features(1914, cards=few)["features"] if row["catalog_name"] == "Nile")
    assert CATALOG_ONLY in held["era_note"]
    assert held["recalibrated"] is False
    same = _nile_pins(lat, lon, ("Flood watch", "Flood watch", "Flood watch"))
    same_row = next(row for row in list_features(1914, cards=same)["features"] if row["catalog_name"] == "Nile")
    assert CATALOG_ONLY in same_row["era_note"]

    cards = _nile_pins(lat, lon, ("Flood watch", "Bank survey", "Delta note"))
    before = {row["catalog_name"] for row in list_features(1914)["features"]}
    tuned = list_features(1914, cards=cards)
    assert {row["catalog_name"] for row in tuned["features"]} == before
    nile = next(row for row in tuned["features"] if row["catalog_name"] == "Nile")
    assert "recalibrated from 3 pins" in nile["era_note"]
    assert "catalog: Nile" in nile["era_note"]
    assert "Posterior ≠ truth." in nile["era_note"]
    assert nile["lat"] == lat and nile["lon"] == lon
    assert nile["disc"]["lat"] == lat and nile["disc"]["lon"] == lon
    assert nile["needs_receipt"] is True
    assert nile["name"] == "Nile"
    later = next(row for row in list_features(2010, cards=cards)["features"] if row["catalog_name"] == "Nile")
    assert NO_EXTENT in later["era_note"]
    assert CATALOG_ONLY in later["era_note"]
    assert "recalibrated from" not in later["era_note"]
    tunnel = next(row for row in list_subsurface(1914, cards=cards)["features"] if row["catalog_name"] == "Channel Tunnel")
    assert "Survey year 1994" in tunnel["era_note"]
    assert NO_EXTENT in tunnel["era_note"]
    assert CATALOG_ONLY in tunnel["era_note"]

    plotted = plot_model(cards)["n"]
    sealed = dispatch("pin", {"axis": "PI", "note": nile["receipt_note"], "src": "4dmap"}, cards)
    after = cards + [sealed["card"]]
    assert plot_model(after)["n"] == plotted
    again = next(row for row in list_features(1914, cards=after)["features"] if row["catalog_name"] == "Nile")
    assert again["needs_receipt"] is False
    script = (ROOT / "fourdmap" / "static" / "globe.js").read_text(encoding="utf-8")
    assert "modern catalog shape; no historical extent in source" in script
    assert CATALOG_ONLY in script
    assert 'axis: "PI"' in script
