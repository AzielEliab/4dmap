"""Π-EMPTY when the lens is silent."""

from __future__ import annotations

from fourdmap.example import EXAMPLE_PIN
from fourdmap.ops import absence, lens
from fourdmap.scope import PI_EMPTY
from fourdmap.store import MapStore


def test_empty_query_is_pi_empty() -> None:
    out = lens({"query": ""}, MapStore())
    assert out["pi"] == PI_EMPTY
    assert out["silent"] is True


def test_miss_is_pi_empty() -> None:
    out = lens({"query": "no-such-pattern"}, MapStore([EXAMPLE_PIN]))
    assert out["pi"] == PI_EMPTY
    assert out["silent"] is True


def test_absence_silent() -> None:
    out = absence({"query": ""}, MapStore([EXAMPLE_PIN]))
    assert out["pi"] == PI_EMPTY
