"""In-memory 4DM card store. Forks are kept. Fail-closed hashes.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from .card import CardError, make_card, verify_card
from .scope import GENESIS_PREV


class MapStore:
    def __init__(self, cards: Iterable[dict[str, Any]] | None = None) -> None:
        self.cards: list[dict[str, Any]] = []
        if cards:
            for card in cards:
                self.add(card)

    def add(self, card: dict[str, Any]) -> dict[str, Any]:
        if "h" not in card:
            card = make_card(**{k: card.get(k) for k in ("id", "t", "delta", "gamma", "pi", "prev", "src", "note")})
        else:
            verify_card(card)
        self.cards.append(card)
        return card

    def by_id(self, card_id: str) -> dict[str, Any]:
        for card in self.cards:
            if card.get("id") == card_id:
                return card
        raise CardError("NOT_FOUND", f"card {card_id} not found")

    def by_hash(self, h: str) -> dict[str, Any]:
        for card in self.cards:
            if card.get("h") == h:
                return card
        raise CardError("NOT_FOUND", f"hash {h} not found")

    def forks(self) -> list[dict[str, Any]]:
        children: dict[str, list[str]] = defaultdict(list)
        for card in self.cards:
            prev = str(card.get("prev") or GENESIS_PREV)
            children[prev].append(str(card.get("h")))
        out = []
        for prev, hashes in children.items():
            if len(hashes) > 1:
                out.append({"prev": prev, "child_hashes": hashes, "kept": True, "winner": None})
        return out

    def walk(self, tip_id: str) -> list[dict[str, Any]]:
        seen: set[str] = set()
        chain: list[dict[str, Any]] = []
        card = self.by_id(tip_id)
        while True:
            h = str(card.get("h"))
            if h in seen:
                raise CardError("HASH_FAIL", "fail-closed: walk cycle")
            seen.add(h)
            verify_card(card)
            chain.append(card)
            prev = str(card.get("prev") or GENESIS_PREV)
            if prev == GENESIS_PREV or not prev:
                break
            try:
                card = self.by_hash(prev)
            except CardError:
                break
        chain.reverse()
        return chain

    def as_list(self) -> list[dict[str, Any]]:
        return list(self.cards)
