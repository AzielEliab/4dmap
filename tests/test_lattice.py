"""Library pin frames + hashchain lattice memory. Author: Aziel Eliab only."""

from __future__ import annotations

from fourdmap.card import CardError, verify_card
from fourdmap.ops import dispatch
from fourdmap.scope import DISCOVERY, LIBRARY, LIVE_OPS, PIN_FRAME_KIND


def _ingest(**extra):
    body = {
        "event": "synthetic paper event",
        "date": "1912-04-15",
        "lat": 41.726,
        "lon": -49.947,
        "surface": "MOCK",
        "src": "aziel-corpus",
        "note": "MOCK library pin — not a real case",
    }
    body.update(extra)
    return body


def test_live_ops_include_lattice() -> None:
    for op in ("library_pin", "plot", "possibility", "pattern_recall", "lattice_tip", "poison_refuse", "neighbor_cite"):
        assert op in LIVE_OPS
    assert DISCOVERY["growth"] == "ON"
    assert LIBRARY["slug"] == "aziel-corpus"


def test_library_pin_accepts_ingest_and_emits_frame() -> None:
    out = dispatch("library_pin", _ingest())
    assert out["ok"] is True
    assert out["surface"] == "MOCK"
    assert out["axis"] == "T"
    assert out["lattice"] is True
    assert out["ml_store"] is False
    assert out["rewrite"] is False
    assert out["courtroom_proof"] is False
    assert out["collapsed"] is False
    card = out["card"]
    verify_card(card)
    assert card["t"]["kind"] == PIN_FRAME_KIND
    assert card["t"]["clock"] == "1912-04-15T00:00:00Z"
    assert card["t"]["event"] == "synthetic paper event"
    assert card["t"]["lat"] == 41.726
    assert out["pin_frame"]["kind"] == PIN_FRAME_KIND
    assert out["possibility"]["label"] == "possibility"
    assert out["possibility"]["truth"] is False
    assert out["bayesian"] is None
    assert out["library"]["slug"] == "aziel-corpus"
    assert out["library"]["cite_only"] is True


def test_pin_alias_routes_library_ingest() -> None:
    out = dispatch("pin", _ingest(gazetteer_id="geonames:12345", lat=None, lon=None))
    assert out["op"] == "library_pin"
    assert out["card"]["t"]["gazetteer_id"] == "geonames:12345"


def test_malformed_and_poison_anchors_refuse() -> None:
    try:
        dispatch("library_pin", _ingest(lat=200, lon=0))
        raise AssertionError("expected ANCHOR_REFUSE")
    except CardError as err:
        assert err.code == "ANCHOR_REFUSE"
    try:
        dispatch("library_pin", {"event": "x", "date": "1912-04-15", "surface": "MOCK"})
        raise AssertionError("expected ANCHOR_INCOMPLETE")
    except CardError as err:
        assert err.code == "ANCHOR_INCOMPLETE"
    try:
        dispatch("library_pin", _ingest(event="poison payload_drop"))
        raise AssertionError("expected POISON_REFUSE")
    except CardError as err:
        assert err.code == "POISON_REFUSE"
    try:
        dispatch("library_pin", {"event": "x", "upload_time": "2026-09-14T00:00:00Z", "lat": 1, "lon": 1, "surface": "MOCK"})
        raise AssertionError("expected CLOCK_REFUSE")
    except CardError as err:
        assert err.code == "CLOCK_REFUSE"
    try:
        dispatch("library_pin", _ingest(gazetteer_id="example.notld", lat=None, lon=None))
        raise AssertionError("expected ANCHOR_REFUSE")
    except CardError as err:
        assert err.code == "ANCHOR_REFUSE"


def test_possibility_and_bayesian_stay_labeled() -> None:
    pinned = dispatch("library_pin", _ingest(bayesian={"label": "bayesian", "value": 0.41, "cite": "library"}))
    assert pinned["possibility"]["label"] == "possibility"
    assert pinned["bayesian"]["label"] == "bayesian"
    assert pinned["bayesian"]["value"] == 0.41
    assert pinned["hooks"]["collapsed"] is False
    scored = dispatch("possibility", {"id": pinned["id"], "bayesian": {"label": "bayesian", "value": 0.3, "cite": "akm"}}, [pinned["card"]])
    assert scored["card"]["prev"] == pinned["h"]
    assert scored["possibility"]["label"] == "possibility"
    assert scored["bayesian"]["label"] == "bayesian"
    assert scored["collapsed"] is False
    verify_card(scored["card"])
    try:
        dispatch("possibility", {"id": pinned["id"], "score": 0.88}, [pinned["card"]])
        raise AssertionError("expected SCORE_COLLAPSE")
    except CardError as err:
        assert err.code == "SCORE_COLLAPSE"


def test_pattern_recall_and_poison_use_lattice() -> None:
    a = dispatch("library_pin", _ingest(id="4dm-lat-a"))
    b = dispatch("library_pin", _ingest(id="4dm-lat-b", prev=a["h"]))
    store = [a["card"], b["card"]]
    recalled = dispatch("pattern_recall", {}, store)
    assert recalled["ml_store"] is False
    assert recalled["lattice"] is True
    assert recalled["n"] >= 1
    assert recalled["patterns"][0]["n"] == 2
    assert recalled["card"]["prev"] in {a["h"], b["h"]}
    verify_card(recalled["card"])
    poisoned = dispatch("poison_refuse", {"feature_h": a["feature_h"]}, store)
    assert poisoned["payload_stored"] is False
    assert a["feature_h"] in poisoned["refused_set"]
    try:
        dispatch("library_pin", _ingest(prev=poisoned["h"]), store + [poisoned["card"]])
        raise AssertionError("expected POISON_REFUSE")
    except CardError as err:
        assert err.code == "POISON_REFUSE"
    try:
        dispatch("ml_store", {})
        raise AssertionError("expected LATTICE_ONLY")
    except CardError as err:
        assert err.code == "LATTICE_ONLY"


def test_plot_and_lattice_tip_and_neighbor() -> None:
    a = dispatch("library_pin", _ingest(id="4dm-plot-a"))
    b = dispatch("library_pin", _ingest(id="4dm-plot-b", date="1913-01-01", prev=a["h"]))
    store = [a["card"], b["card"]]
    plotted = dispatch("plot", {}, store)
    assert plotted["gis"] is False
    assert plotted["n"] == 2
    assert {p["surface"] for p in plotted["pins"]} == {"MOCK"}
    tips = dispatch("lattice_tip", {}, store)
    assert tips["rewrite"] is False
    assert tips["n"] == 1
    assert tips["tips"][0]["h"] == b["h"]
    cited = dispatch("neighbor_cite", {"id": a["id"]}, store)
    assert cited["neighbors"][0]["slug"] == "aziel-corpus"
    assert cited["companions_merged"] is False
    try:
        dispatch("neighbor_cite", {}, [])
        raise AssertionError("expected 4DM-MISSING")
    except CardError as err:
        assert err.code == "4DM-MISSING"


def test_frame_status_growth_on() -> None:
    status = dispatch("frame_status", {})
    assert status["growth"] == "ON"
    assert status["discovery"]["openapi"] is True
    assert status["library"]["slug"] == "aziel-corpus"
    assert "library_pin" in status["live_ops"]
