"""Globe surface, shared lattice, and area estimate. Author: Aziel Eliab only."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
import threading

from fourdmap.area import estimate_area
from fourdmap.chainfile import FORMAT, load_cards
from fourdmap.cli import main
from fourdmap.ops import dispatch
from fourdmap.server import make_server
from fourdmap.sky import sun_alt_az
from fourdmap.uploads import log_upload

ROOT = Path(__file__).resolve().parents[1]


def test_page_is_a_globe() -> None:
    html = (ROOT / "fourdmap" / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "fourdmap" / "static" / "globe.js").read_text(encoding="utf-8")
    assert 'id="globe"' in html
    assert 'id="layers"' in html
    assert 'id="era"' in html
    assert 'id="search"' in html
    assert "Why this area" in html
    assert "Blank earth" in html
    assert "Satellite" in html
    assert "Street view" in html
    assert "LiDAR" in html
    assert "not an exact point" in html
    assert "/static/globe.js" in html
    assert "three.module.min.js" in script
    assert "unpkg.com" not in html
    assert "cdn.jsdelivr.net" not in html
    vendor = ROOT / "fourdmap" / "static" / "vendor" / "three.module.min.js"
    assert vendor.is_file()
    assert "Three.js" in vendor.read_text(encoding="utf-8")[:200]
    assert (ROOT / "fourdmap" / "static" / "geo" / "land.geojson").is_file()
    assert (ROOT / "fourdmap" / "static" / "geo" / "era-1914.geojson").is_file()
    assert (ROOT / "fourdmap" / "static" / "geo" / "era-2010.geojson").is_file()


def test_sun_is_high_at_the_equator_on_the_equinox() -> None:
    when = datetime(2010, 3, 20, 12, 0, tzinfo=timezone.utc)
    sun = sun_alt_az(when, 0, 0)
    assert sun["altitude_deg"] > 80


def test_area_is_a_region_not_a_point() -> None:
    area = estimate_area(
        {
            "event": "Harbor fire watch",
            "date": "1912-04-14T09:00:00Z",
            "lat": "44.65",
            "lon": "-63.57",
            "place": "sailed near Halifax",
            "year": 1914,
        }
    )
    assert area["exact_point"] is False
    assert area["proof"] is False
    assert area["radius_km"] >= 8
    assert len(area["ring"]) >= 4
    why = area["why"].lower()
    assert "point" in why
    assert "halifax" in why
    assert "sun" in why
    for key in ("physics", "linguistics", "math", "celestial"):
        assert area["parts"][key]
    border = estimate_area(
        {"event": "border check", "date": "1914-08-01", "lat": 49.6, "lon": 6.1, "place": "Luxembourg", "year": 1914}
    )
    assert border["exact_point"] is False
    assert border["matched_border"] == "Luxembourg"
    assert border["era_source"] == "aourednik/historical-basemaps"


def test_cli_and_ui_share_one_lattice(tmp_path, monkeypatch, capsys) -> None:
    path = tmp_path / "lattice.json"
    monkeypatch.setenv("FOURDMAP_LATTICE", str(path))
    assert main([
        "library-pin", "--json",
        "--event", "Harbor fire watch",
        "--date", "1912-04-14",
        "--lat", "44.65",
        "--lon", "-63.57",
        "--place", "Halifax",
        "--who", "Mara Quill",
        "--surface", "MOCK",
        "--src", "operator",
    ]) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["op"] == "library_pin"
    assert first["card"]["t"]["who"] == ["Mara Quill"]
    assert main([
        "--json", "library-pin",
        "--event", "Second watch",
        "--date", "1913-01-02",
        "--lat", "51.51",
        "--lon", "-0.12",
        "--who", "Mara Quill",
        "--surface", "MOCK",
    ]) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["card"]["prev"] == first["h"]
    stored = load_cards()
    assert [card["id"] for card in stored] == [first["id"], second["id"]]
    assert json.loads(path.read_text(encoding="utf-8"))["format"] == FORMAT
    tip = dispatch("lattice_tip", {}, stored)
    assert tip["tips"][0]["h"] == second["h"]
    chain = dispatch("verify_chain", {"tip": second["id"]}, stored)
    assert chain["verified"] == 2


def test_explicit_cards_do_not_replace_the_lattice(tmp_path, monkeypatch, capsys) -> None:
    path = tmp_path / "lattice.json"
    monkeypatch.setenv("FOURDMAP_LATTICE", str(path))
    bundle = tmp_path / "bundle.json"
    bundle.write_text("[]", encoding="utf-8")
    assert main(["pin", "--cards", str(bundle), "--t", "2026-09-10T00:00:00Z", "--src", "synthetic"]) == 0
    capsys.readouterr()
    assert not path.exists()


def test_upload_is_hashed(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FOURDMAP_UPLOADS", str(tmp_path / "uploads"))
    entry = log_upload("note.txt", b"harbor report")
    assert len(entry["sha256"]) == 64
    assert entry["bytes"] == len(b"harbor report")
    again = log_upload("note.txt", b"harbor report")
    assert again["sha256"] == entry["sha256"]


def test_server_appends_to_the_same_chain(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FOURDMAP_LATTICE", str(tmp_path / "lattice.json"))
    httpd = make_server(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    try:
        def post(op, payload):
            body = json.dumps({"payload": payload}).encode("utf-8")
            from urllib.request import Request
            req = Request(f"http://127.0.0.1:{port}/v1/{op}", data=body, headers={"Content-Type": "application/json"})
            with urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))

        first = post("library_pin", {
            "event": "Harbor fire watch",
            "date": "1912-04-14",
            "lat": 44.65,
            "lon": -63.57,
            "who": ["Mara Quill"],
            "place": "Halifax",
            "surface": "MOCK",
            "src": "operator",
        })
        second = post("library_pin", {
            "event": "Second watch",
            "date": "1913-01-02",
            "lat": 51.51,
            "lon": -0.12,
            "who": ["Mara Quill"],
            "surface": "MOCK",
            "src": "operator",
        })
        assert second["prev"] == first["h"]
        plotted = post("plot", {})
        assert plotted["n"] == 2
        assert plotted["pins"][0]["who"] == ["Mara Quill"]
        assert plotted["pins"][0]["possibility"]["label"] == "possibility"
        assert plotted["gis"] is False
        with urlopen(f"http://127.0.0.1:{port}/static/vendor/three.module.min.js") as response:
            assert response.status == 200
            assert b"Three.js" in response.read(80)
    finally:
        httpd.shutdown()
        thread.join(timeout=2)
