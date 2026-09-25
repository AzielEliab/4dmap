"""Era border estimates and cited anomaly outlines. Author: Aziel Eliab only."""

from __future__ import annotations

import json
from pathlib import Path

from fourdmap.anomalies import EMPTY, NO_ERA_OUTLINE, list_anomalies, outline_for
from fourdmap.names import border_note, modern_successors

ROOT = Path(__file__).resolve().parents[1]


def test_borders_are_estimated_and_do_not_invent_a_successor() -> None:
    exact = border_note(1914)
    assert exact["exact"] is True
    assert exact["year"] == 1914
    assert "estimated borders; source year 1914." in exact["note"]
    assert "not a surveyed boundary" in exact["note"]
    missing = border_note(1920)
    assert missing["exact"] is False
    assert missing["year"] == 1914
    assert "nearest public borders: 1914." in missing["note"]
    labels = modern_successors(1914)
    assert labels.get("Persia") == "Iran"
    assert "Ottoman Empire" not in labels
    modern_names = set()
    data = json.loads((ROOT / "fourdmap" / "static" / "geo" / "era-2010.geojson").read_text(encoding="utf-8"))
    for feature in data["features"]:
        name = (feature.get("properties") or {}).get("NAME")
        if name:
            modern_names.add(name)
    assert set(labels.values()) <= modern_names
    script = (ROOT / "fourdmap" / "static" / "globe.js").read_text(encoding="utf-8")
    assert "LineDashedMaterial" in script
    assert "estimated borders; source year" in script
    assert "nearest public borders:" in script
    assert "nearest bundled era to this pin" in script


def test_bermuda_triangle_is_a_cited_outline_only() -> None:
    payload = list_anomalies(1914)
    assert payload["n"] == 1
    row = payload["features"][0]
    assert row["name"] == "Bermuda Triangle"
    assert row["group"] == "anomaly"
    assert NO_ERA_OUTLINE in row["era_note"]
    assert "Wikidata P625" in row["source"]
    assert "not a physical phenomenon" in row["era_note"]
    names = {item["name"]: item for item in row["vertices"]}
    assert names["Bermuda"]["qid"] == "Q23635"
    assert names["Bermuda"]["lat"] == 32.32
    assert names["Bermuda"]["lon"] == -64.74
    assert names["Miami"]["qid"] == "Q8652"
    assert names["San Juan"]["qid"] == "Q41211"
    assert len(row["ring"]) == 3
    later = list_anomalies(2010)["features"][0]
    assert later["ring"] == row["ring"]
    assert NO_ERA_OUTLINE in later["era_note"]
    blob = json.dumps(payload).lower()
    for banned in ("cursed", "occult", "disappearance", "hollow"):
        assert banned not in blob
    empty = list_anomalies(1914, "not-a-zone")
    assert empty["n"] == 0
    assert empty["message"] == EMPTY
    shaped, note = outline_for(
        {"name": "Bermuda Triangle", "ring": [[0, 0]], "extents": [{"year": 1994, "ring": [[1, 2], [3, 4], [5, 6]], "source": "public chart"}]},
        1914,
    )
    assert shaped["ring"][0] == [1, 2]
    assert "nearest public outline: 1994" in note
    assert "not a 1914 outline" in note
    html = (ROOT / "fourdmap" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "fourdmap" / "static" / "globe.js").read_text(encoding="utf-8")
    assert html.index("<legend>Major geo features</legend>") < html.index("<legend>Anomaly boundaries</legend>")
    assert html.index("<legend>Anomaly boundaries</legend>") < html.index("<legend>Subsurface</legend>")
    assert "no public anomaly outline here." in script
    body = script.split("Anomaly ·", 1)[1].split("function placeAliasHit", 1)[0]
    assert "library_pin" not in body
    assert "post(" not in body
