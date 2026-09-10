"""Forks are kept. No winner."""

from __future__ import annotations

from fourdmap.card import make_card
from fourdmap.ops import fork
from fourdmap.store import MapStore


def test_fork_keeps_both_branches() -> None:
    parent = make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="parent")
    store = MapStore([parent])
    out = fork({"id": parent["id"]}, store)
    assert out["forks_kept"] is True
    assert out["winner"] is None
    assert len(store.as_list()) == 2
    forks = store.forks()
    assert len(forks) == 1
    assert forks[0]["kept"] is True
    assert forks[0]["winner"] is None
    assert parent["h"] in {store.as_list()[0]["h"], store.as_list()[1]["prev"]}
    assert store.as_list()[1]["prev"] == parent["prev"]
