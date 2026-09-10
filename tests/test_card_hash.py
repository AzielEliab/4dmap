"""Fail-closed 4DM-CARD hashes."""

from __future__ import annotations

from fourdmap.card import CardError, digest, make_card, verify_card
from fourdmap.example import EXAMPLE_PIN


def test_example_pin_hash_stable() -> None:
    assert EXAMPLE_PIN["h"] == digest(EXAMPLE_PIN)
    verify_card(EXAMPLE_PIN)


def test_same_fields_same_hash() -> None:
    a = make_card(id="same", t="2026-09-10T00:00:00Z", src="synthetic", note="n", pi="Π-EMPTY")
    b = make_card(id="same", t="2026-09-10T00:00:00Z", src="synthetic", note="n", pi="Π-EMPTY")
    assert a["h"] == b["h"]
    assert len(a["h"]) == 64


def test_broken_hash_refuses() -> None:
    broken = dict(EXAMPLE_PIN)
    broken["h"] = "0" * 64
    try:
        verify_card(broken)
        raise AssertionError("expected HASH_FAIL")
    except CardError as err:
        assert err.code == "HASH_FAIL"


def test_note_change_changes_hash() -> None:
    a = make_card(id="n1", t="2026-09-10T00:00:00Z", src="synthetic", note="one")
    b = make_card(id="n1", t="2026-09-10T00:00:00Z", src="synthetic", note="two")
    assert a["h"] != b["h"]
