"""Synthetic 4DMap cards. Never present as a real case."""

from __future__ import annotations

from .card import make_card
from .scope import GENESIS_PREV, PI_EMPTY

EXAMPLE_PIN = make_card(
    id="4dm-example-pin",
    t="2026-09-10T00:00:00Z",
    src="synthetic",
    note="synthetic T pin — not a real case",
    prev=GENESIS_PREV,
    pi=PI_EMPTY,
)

EXAMPLE_SPAN = make_card(
    id="4dm-example-span",
    delta={"from": EXAMPLE_PIN["id"], "to": "4dm-example-later", "from_t": EXAMPLE_PIN["t"], "to_t": "2026-09-10T01:00:00Z"},
    src="synthetic",
    note="synthetic Δ span — not a real case",
    prev=EXAMPLE_PIN["h"],
    pi=PI_EMPTY,
)

EXAMPLE_CARDS = [EXAMPLE_PIN, EXAMPLE_SPAN]
