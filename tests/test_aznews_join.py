"""AZNews stays standalone, 4DMap stays standalone, and the join is not marked live early."""

from __future__ import annotations

import subprocess
from pathlib import Path

from fourdmap.aznews import ABSENT_CODE, LIBRARY_CODE, reset_aznews_store
from fourdmap.card import CardError, verify_card
from fourdmap.ops import dispatch
from fourdmap.scope import LIBRARY, LIVE_OPS

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "ab" * 32
FETCHED = {
    "id": "nw-harbor",
    "date": "2026-03-01",
    "event": "Harbor inspection",
    "place": "Lisbon",
    "wording": "A fetched harbor note with enough words to open again.",
    "score": 3,
    "image_hash": IMAGE,
    "fetched": True,
}


def setup_function() -> None:
    reset_aznews_store()


def teardown_function() -> None:
    reset_aznews_store()


def test_news_ops_are_listed_and_frame_keeps_them_off_the_companion_list() -> None:
    for op in ("news_status", "news_ingest", "news_pin", "news_open"):
        assert op in LIVE_OPS
    status = dispatch("frame_status", {})
    card = status["aznews"]
    assert card["paths"]["standalone"]["op"] == "news_ingest"
    assert card["paths"]["joined"]["ops"] == ["news_pin", "news_open"]
    assert card["paths"]["fourdmap_without_news"]["op"] == "pin"
    assert card["software_tab"] is False
    assert card["live"] is False
    assert card["fourdmap_live"] is False
    assert card["library_map_is_aznews"] is False
    assert card["library_map"] == LIBRARY["map"]
    assert "aznews" not in {row["slug"] for row in status["companions"]}


def test_empty_and_library_do_not_become_news() -> None:
    empty = dispatch("news_ingest", {})
    assert empty["ok"] is False
    assert empty["code"] == ABSENT_CODE
    assert empty["live"] is False
    assert empty["records"] == []
    library = dispatch("news_pin", {"url": LIBRARY["map"], "event": "paper", "date": "1912-04-15", "place": "Atlantic"})
    assert library["code"] == LIBRARY_CODE
    assert library["live"] is False
    assert library["library_map_is_aznews"] is False


def test_pin_still_works_without_a_story() -> None:
    pinned = dispatch("pin", {"t": "2026-09-10T00:00:00Z", "src": "synthetic", "note": "clock only"})
    assert pinned["ok"] is True
    assert pinned["card"]["src"] == "synthetic"
    status = dispatch("news_status", {})
    assert status["live"] is False
    assert status["source_present"] is False
    assert status["fourdmap_live"] is False


def test_fixture_and_supplied_stories_do_not_mark_either_side_live() -> None:
    fixture = dispatch(
        "news_ingest",
        {
            "fixture": True,
            "fixture_label": "fixture — not live news",
            "date": "2026-01-02",
            "event": "fixture drill",
            "place": "fixture quay",
            "wording": "This fixture story is not a fetched article.",
        },
    )
    assert fixture["ok"] is True
    assert fixture["on_map"] is False
    assert fixture["live"] is False
    assert fixture["join_live"] is False
    assert fixture["aznews_live"] is False
    supplied = dispatch(
        "news_pin",
        {
            "date": "2026-02-02",
            "event": "Supplied walk",
            "place": "Rome",
            "wording": "A person typed this story. It was not fetched.",
            "score": 1,
            "image_hash": IMAGE,
        },
    )
    assert supplied["on_map"] is True
    assert supplied["live"] is False
    assert supplied["fetched_from_network"] is False
    opened = dispatch("news_open", {"id": supplied["item_id"]})
    assert opened["wording"] == "A person typed this story. It was not fetched."
    assert opened["summary"].startswith("Opened.")
    assert opened["live"] is False
    assert opened["fourdmap_live"] is False
    assert opened["merged"] is False


def test_fetched_item_is_live_only_after_both_paths_and_an_open() -> None:
    alone = dispatch("news_ingest", FETCHED)
    assert alone["path"] == "standalone"
    assert alone["on_map"] is False
    assert alone["live"] is False
    assert alone["aznews_live"] is False
    pinned = dispatch("news_pin", {"id": FETCHED["id"]})
    assert pinned["on_map"] is True
    assert pinned["card"]["src"] == "aznews-fetch"
    verify_card(pinned["card"])
    assert pinned["live"] is False
    opened = dispatch("news_open", {"id": pinned["id"]})
    assert opened["wording"] == FETCHED["wording"]
    assert opened["round_trip"] is True
    assert opened["join_live"] is True
    assert opened["aznews_live"] is True
    assert opened["live"] is True
    assert opened["fourdmap_live"] is False
    assert opened["catalog_live"] is False
    assert opened["fetched_from_network"] is False
    assert opened["feed_configured"] is False
    assert opened["merged"] is False
    assert opened["software_tab"] is False
    assert opened["cross_tether"]["azos_updated"] is False
    assert opened["cross_tether"]["interface_updated"] is False
    assert opened["cross_tether"]["runtime_claimed"] is False
    status = dispatch("news_status", {})
    assert status["join_live"] is True
    assert status["fourdmap_live"] is False


def test_pin_without_standalone_store_stays_not_live() -> None:
    reset_aznews_store()
    pinned = dispatch("news_pin", FETCHED)
    opened = dispatch("news_open", {"id": pinned["id"]})
    assert opened["ok"] is True
    assert opened["wording"] == FETCHED["wording"]
    assert opened["join_live"] is False
    assert opened["aznews_live"] is False
    assert opened["live"] is False


def test_stateless_records_do_not_use_the_process_desk() -> None:
    reset_aznews_store()
    first = dispatch("news_ingest", {**FETCHED, "records": []})
    reset_aznews_store()
    second = dispatch("news_pin", {**FETCHED, "records": first["records"]})
    reset_aznews_store()
    third = dispatch("news_open", {"id": FETCHED["id"], "records": second["records"]})
    assert third["join_live"] is True
    assert third["fourdmap_live"] is False
    desk = dispatch("news_status", {})
    assert desk["live"] is False
    assert desk["records"] == []


def test_forged_open_flag_does_not_mark_the_join_live() -> None:
    stored = dispatch("news_ingest", {**FETCHED, "records": []})
    row = dict(stored["records"][0])
    row["on_map"] = True
    row["opened"] = True
    row["open_receipt"] = {"open_hash": "0" * 64}
    status = dispatch("news_status", {"records": [stored["records"][0], row]})
    assert status["live"] is False
    assert status["join_live"] is False


def test_same_story_is_not_written_twice() -> None:
    dispatch("news_ingest", FETCHED)
    try:
        dispatch("news_ingest", FETCHED)
        raise AssertionError("expected AZNEWS-DOUBLE")
    except CardError as err:
        assert err.code == "AZNEWS-DOUBLE"


def test_human_pages_name_both_paths_and_do_not_pretend_a_feed() -> None:
    page = (ROOT / "fourdmap/static/index.html").read_text(encoding="utf-8")
    globe = (ROOT / "fourdmap/static/globe.js").read_text(encoding="utf-8")
    home = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
    assert "does not fetch a feed" in page
    assert 'id="news-save"' in page and 'id="news-pin"' in page and 'id="news-open"' in page
    for blob in (globe, home):
        assert "news_ingest" in blob
        assert "news_pin" in blob
        assert "news_open" in blob
    assert "does not fetch a feed" in home


def test_worker_news_script_passes() -> None:
    script = ROOT / "workers/download-tracker/scripts/verify-aznews.mjs"
    completed = subprocess.run(
        ["node", str(script)],
        cwd=script.parent,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "ok aznews-4dmap" in completed.stdout
