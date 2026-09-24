"""Human app screen: one pin action, grouped tools, machine JSON unchanged.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
LOCAL = (ROOT / "fourdmap/static/index.html").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
RUNTIME = (ROOT / "workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")

CONTROL_IDS = (
    "pin-form",
    "pin-t",
    "pin-axis",
    "pin-src",
    "load-example",
    "library-form",
    "lib-event",
    "lib-date",
    "lib-surface",
    "lib-lat",
    "lib-lon",
    "lib-gaz",
    "lib-doc",
    "span-form",
    "span-from",
    "span-to",
    "join-form",
    "join-left",
    "join-right",
    "join-type",
    "fork-btn",
    "lens-btn",
    "example-btn",
    "walk-form",
    "walk-tip",
    "trace-btn",
    "chain-btn",
    "frame-btn",
    "axis-btn",
    "export-btn",
    "memory-cite-btn",
    "memory-observe-btn",
    "plot-btn",
    "possibility-btn",
    "recall-btn",
    "tip-btn",
    "poison-btn",
    "neighbor-btn",
    "lib-demo-btn",
    "import-form",
    "import-json",
    "card-list",
    "last-op",
    "last-json",
    "meshLiveCount",
)


def test_worker_board_is_one_pin_with_grouped_tools() -> None:
    assert "Pin a card" in HOME
    assert 'id="pin-form"' in HOME
    assert "<details" in HOME
    assert "Library upload → 4DMap pin" in HOME
    assert "hashchain lattice" in HOME
    assert "possibility" in HOME
    assert "Four-axis board" in HOME
    assert "T Clock" in HOME
    assert "Δ Interval" in HOME
    assert "Γ Trajectory" in HOME
    assert "Π Pattern" in HOME
    assert "prefers-color-scheme: light" in HOME
    assert ":focus-visible" in HOME
    assert 'id="record-fold"' in HOME
    assert 'summary>Response record</summary>' in HOME
    # The response record is not the status line.
    assert HOME.find('id="last-op"') < HOME.find('id="record-fold"')
    for control_id in CONTROL_IDS:
        assert f'id="{control_id}"' in HOME
    assert "GodLock.AZ" not in HOME
    assert "Everblooming" not in HOME
    assert "everblooming" not in HOME


def test_counters_stay_on_the_worker_page() -> None:
    assert ">Views<" in HOME
    assert ">Downloads<" in HOME
    assert 'id="meshLiveCount"' in HOME
    assert "GET never enables" in HOME
    assert 'id="install-btn"' in HOME
    assert "4dmap-0.3.0.tar.gz" in HOME


def test_loopback_board_matches_without_invented_counters() -> None:
    assert "Pin a card" in LOCAL
    assert "<details" in LOCAL
    assert "prefers-color-scheme: light" in LOCAL
    assert ":focus-visible" in LOCAL
    assert "Aziel Eliab" in LOCAL
    assert "GodLock.AZ" not in LOCAL
    for control_id in CONTROL_IDS:
        if control_id == "meshLiveCount":
            assert control_id not in LOCAL
            continue
        assert f'id="{control_id}"' in LOCAL
    assert ">Views<" not in LOCAL
    assert ">Downloads<" not in LOCAL


def test_machine_routes_stay_json() -> None:
    assert 'Content-Type: "application/json; charset=utf-8"' in INDEX or "application/json" in INDEX
    assert "displayEnvelope" in RUNTIME
    assert "return json(displayEnvelope(op, raw));" in RUNTIME
