"""AKM-TRIAD-1.0 is fabric pairing only — not a Softwares slug or door."""

from __future__ import annotations

from pathlib import Path

from fourdmap.card import CardError, make_card
from fourdmap.ops import dispatch
from fourdmap.scope import AKM, COMPANIONS, LIVE_OPS

ROOT = Path(__file__).resolve().parents[1]


def test_akm_is_fabric_not_software() -> None:
    assert AKM["spec"] == "AKM-TRIAD-1.0"
    assert AKM["fabric"] is True
    assert AKM["software_tab"] is False
    assert AKM["door"] is False
    assert AKM["slug"] is None
    assert AKM["softwares_product"] is False
    assert AKM["posterior_is_truth"] is False
    assert AKM["history_rewrite"] is False
    assert tuple(AKM["triad"]) == ("E", "C", "P", "B")
    assert "akm" not in COMPANIONS
    assert "memory" not in COMPANIONS
    assert "memory_cite" in LIVE_OPS
    assert "memory_observe" in LIVE_OPS


def test_memory_cite_leaves_card_unchanged() -> None:
    card = make_card(t="2026-09-10T00:00:00Z", src="temporallock", note="T pin")
    before = card["h"]
    out = dispatch("memory_cite", {"id": card["id"]}, [card])
    assert out["ok"] is True
    assert out["cited"] is True
    assert out["card_rewritten"] is False
    assert out["history_rewrite"] is False
    assert out["posterior_is_truth"] is False
    assert out["software_tab"] is False
    assert out["door"] is False
    assert out["h"] == before
    assert out["akm"]["software_tab"] is False


def test_memory_observe_builds_fraggate_packet() -> None:
    card = make_card(t="2026-09-10T00:00:00Z", src="staticclock", note="T pin")
    out = dispatch("memory_observe", {"id": card["id"]}, [card])
    obs = out["observation"]
    assert out["forwarded"] is False
    assert obs["kind"] == "memory_observation"
    assert obs["spec"] == "AKM-TRIAD-1.0"
    assert obs["fraggate"] == "memory_observe"
    assert obs["http"] == "POST /v1/memory/observe"
    assert obs["card"]["h"] == card["h"]
    assert obs["posterior_is_truth"] is False
    assert obs["software_tab"] is False
    assert obs["door"] is False
    assert "inspection receipt, not truth" in obs["fact"]


def test_memory_observe_refuses_rewrite_and_software_slug() -> None:
    card = make_card(t="2026-09-10T00:00:00Z", src="operator", note="T pin")
    try:
        dispatch("memory_observe", {"id": card["id"], "history_rewrite": True}, [card])
        raise AssertionError("expected AKM_REWRITE")
    except CardError as err:
        assert err.code == "AKM_REWRITE"
    try:
        dispatch("memory_cite", {"id": card["id"], "slug": "akm", "software_tab": True}, [card])
        raise AssertionError("expected AKM_SOFTWARE")
    except CardError as err:
        assert err.code == "AKM_SOFTWARE"
    try:
        dispatch("memory_cite", {"id": card["id"], "posterior_is_truth": True}, [card])
        raise AssertionError("expected AKM_TRUTH")
    except CardError as err:
        assert err.code == "AKM_TRUTH"


def test_refuse_akm_as_software_op() -> None:
    for op, code in (("akm", "AKM_SOFTWARE"), ("posterior_truth", "AKM_TRUTH"), ("memory_rewrite", "AKM_REWRITE")):
        try:
            dispatch(op, {})
            raise AssertionError(f"expected {op} refuse")
        except CardError as err:
            assert err.code == code


def test_frame_status_akm_pointer() -> None:
    status = dispatch("frame_status", {})
    slugs = {c["slug"] for c in status["companions"]}
    assert "akm" not in slugs
    assert status["akm"]["software_tab"] is False
    assert status["akm"]["door"] is False
    assert status["akm"]["spec"] == "AKM-TRIAD-1.0"


def test_docs_do_not_tab_akm() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    paper = (ROOT / "docs/4DM-WP-1.0.md").read_text(encoding="utf-8")
    for blob in (readme, skill, paper):
        assert "AKM-TRIAD-1.0" in blob
        assert "not a Softwares-tab" in blob or "Not a Softwares-tab" in blob
        assert "posterior ≠ truth" in blob or "Posterior ≠ truth" in blob
