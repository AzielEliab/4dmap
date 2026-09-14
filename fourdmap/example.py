"""Synthetic 4DMap cards. Never present as a real case."""

from __future__ import annotations

from .card import make_card
from .lattice import feature_hash
from .scope import GENESIS_PREV, PI_EMPTY, PIN_FRAME_KIND

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

_EXAMPLE_LIB_EVENT = "synthetic paper event — not a real case"
_EXAMPLE_LIB_CLOCK = "1912-04-15T00:00:00Z"
EXAMPLE_LIBRARY_PIN = make_card(
    id="4dm-example-library-pin",
    t={
        "kind": PIN_FRAME_KIND,
        "clock": _EXAMPLE_LIB_CLOCK,
        "event": _EXAMPLE_LIB_EVENT,
        "lat": 41.726,
        "lon": -49.947,
        "gazetteer_id": None,
        "doc_id": "AZDOC-MOCK",
        "surface": "MOCK",
        "feature_h": feature_hash(_EXAMPLE_LIB_EVENT, _EXAMPLE_LIB_CLOCK, 41.726, -49.947, None),
    },
    src="synthetic",
    note="MOCK library pin — not a real case. Paper date × event × geo.",
    prev=EXAMPLE_SPAN["h"],
    pi=PI_EMPTY,
)

EXAMPLE_CARDS = [EXAMPLE_PIN, EXAMPLE_SPAN, EXAMPLE_LIBRARY_PIN]
