"""Illegal joins refuse. Typed joins allowed."""

from __future__ import annotations

from fourdmap.card import CardError, make_card
from fourdmap.joins import join_cards


def test_pi_to_t_backdate_refuses() -> None:
    t = make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="clock")
    p = make_card(pi={"class": "repeat"}, src="synthetic", note="pattern")
    try:
        join_cards(p, t, "PI-T")
        raise AssertionError("expected PI_T_BACKDATE")
    except CardError as err:
        assert err.code == "PI_T_BACKDATE"


def test_backdate_flag_refuses() -> None:
    t = make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="clock")
    p = make_card(pi={"class": "repeat"}, src="synthetic", note="pattern")
    try:
        join_cards(t, p, "T-PI", backdate=True)
        raise AssertionError("expected backdate refuse")
    except CardError as err:
        assert err.code == "PI_T_BACKDATE"


def test_t_pi_allowed() -> None:
    t = make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="clock")
    p = make_card(pi={"class": "repeat"}, src="synthetic", note="pattern")
    out = join_cards(t, p, "T-PI")
    assert out["ok"] is True
    assert out["join"] == "T-PI"


def test_intent_refuses() -> None:
    t = make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="clock")
    p = make_card(pi={"class": "repeat"}, src="synthetic", note="pattern")
    try:
        join_cards(t, p, "T-PI", note="this proves intent")
        raise AssertionError("expected INTENT_REFUSE")
    except CardError as err:
        assert err.code == "INTENT_REFUSE"
