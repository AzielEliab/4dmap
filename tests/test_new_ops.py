"""0.2.0 FragGate-safe ops: export/import, frame, axis, walk_trace, verify_chain."""

from __future__ import annotations

from fourdmap.card import CardError, make_card
from fourdmap.ops import dispatch
from fourdmap.scope import LIVE_OPS, PI_EMPTY


def _two_pins():
    a = make_card(t="2026-09-10T00:00:00Z", src="temporallock", note="T pin A")
    b = make_card(t="2026-09-10T01:00:00Z", src="staticclock", note="T pin B", prev=a["h"])
    return a, b


def test_live_ops_lists_new_names() -> None:
    for op in (
        "card_export",
        "card_import",
        "frame_status",
        "axis_describe",
        "walk_trace",
        "verify_chain",
        "card_new",
        "card_pin",
        "verify_hash",
    ):
        assert op in LIVE_OPS


def test_pin_across_axes() -> None:
    t = dispatch("card_pin", {"t": "2026-09-10T00:00:00Z", "axis": "T", "src": "temporallock"})
    assert t["ok"] is True
    assert t["axis"] == "T"
    assert t["receipt"]["kind"] == "4DM-CARD"
    assert t["companion"]["software"] == "TemporalLock"
    assert t["companion"]["cite_only"] is True
    assert t["companion"]["door"] is False

    delta = dispatch("pin", {"axis": "DELTA", "value": "changed", "src": "chronolock"})
    assert delta["axis"] == "DELTA"
    assert delta["card"]["delta"]["change"] == "changed"

    gamma = dispatch("pin", {"axis": "GAMMA", "value": "arc", "src": "trajectorylock"})
    assert gamma["axis"] == "GAMMA"
    assert gamma["card"]["gamma"]["geometry"] == "arc"

    pi = dispatch("pin", {"axis": "PI", "value": "cohort-a", "src": "spectrallock"})
    assert pi["axis"] == "PI"
    assert pi["card"]["pi"] == "cohort-a"


def test_span_records_axis_pair() -> None:
    a, b = _two_pins()
    out = dispatch("card_span", {"from_id": a["id"], "to_id": b["id"]}, [a, b])
    assert out["ok"] is True
    assert out["card"]["delta"]["from_axis"] == "T"
    assert out["card"]["delta"]["to_axis"] == "T"
    assert out["companions_merged"] is False
    slugs = {c["slug"] for c in out["cites"]}
    assert "temporallock" in slugs
    assert "staticclock" in slugs


def test_join_cites_companions_not_merged() -> None:
    t = make_card(t="2026-09-10T00:00:00Z", src="temporallock", note="clock")
    p = make_card(pi={"class": "repeat"}, src="spectrallock", note="pattern")
    out = dispatch("card_join", {"left": t["id"], "right": p["id"], "join_type": "T-PI"}, [t, p])
    assert out["ok"] is True
    assert out["second_door"] is False
    assert out["companions_merged"] is False
    slugs = {c["slug"] for c in out["cites"]}
    assert slugs == {"temporallock", "spectrallock"}


def test_export_import_roundtrip() -> None:
    a, b = _two_pins()
    exported = dispatch("card_export", {}, [a, b])
    assert exported["format"] == "4DM-CARD-JSON"
    assert exported["domains_are_doors"] is False
    assert exported["n"] == 2
    imported = dispatch("card_import", {"bundle": exported["bundle"]}, [])
    assert imported["n"] == 2
    assert imported["cards"][0]["h"] == a["h"]


def test_import_broken_hash_refuses() -> None:
    a, _ = _two_pins()
    broken = dict(a)
    broken["h"] = "0" * 64
    try:
        dispatch("card_import", {"bundle": {"cards": [broken]}}, [])
        raise AssertionError("expected HASH_FAIL")
    except CardError as err:
        assert err.code == "HASH_FAIL"


def test_walk_trace_and_verify_chain() -> None:
    a, b = _two_pins()
    span = dispatch("span", {"from_id": a["id"], "to_id": b["id"]}, [a, b])
    store = [a, b, span["card"]]
    traced = dispatch("walk_trace", {"tip": span["card"]["id"]}, store)
    assert traced["ok"] is True
    assert traced["n"] >= 2
    assert traced["steps"][-1]["axis"] == "DELTA"
    assert traced["genesis"] is True
    chain = dispatch("verify_chain", {"tip": span["card"]["id"]}, store)
    assert chain["verified"] == chain["n"]
    assert chain["broken"] is None
    hashed = dispatch("verify_hash", {"id": a["id"]}, store)
    assert hashed["ok"] is True
    assert hashed["h"] == a["h"]


def test_card_new_and_aliases() -> None:
    out = dispatch("card_new", {"t": "2026-09-10T00:00:00Z", "src": "operator", "note": "new"})
    assert out["card"]["pi"] == PI_EMPTY
    listed = dispatch("card_list", {}, [out["card"]])
    assert len(listed["cards"]) == 1
    walked = dispatch("card_walk", {"tip": out["card"]["id"]}, [out["card"]])
    assert walked["n"] == 1


def test_refuse_fantasy_and_stub_ops() -> None:
    for op, code in (
        ("truth_score", "STUB_REFUSE"),
        ("lumen_panel", "STUB_REFUSE"),
        ("wipe", "FANTASY_OP"),
        ("merge_products", "FANTASY_OP"),
        ("enable_door", "FANTASY_OP"),
    ):
        try:
            dispatch(op, {})
            raise AssertionError(f"expected {op} refuse")
        except CardError as err:
            assert err.code == code
