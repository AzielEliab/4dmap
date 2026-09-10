"""Typed joins for 4DMap. Illegal joins refuse fail-closed.

Allowed inspection joins: T↔Δ, Δ↔Γ, Γ↔Π, T↔Π.
Refused: Π→T backdate, intent, identity leak.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from .card import (
    CardError,
    axis_of,
    card_receipt,
    companion_cite,
    digest,
    make_card,
    scan_identity,
    scan_intent,
)
from .scope import ALLOWED_JOINS, ILLEGAL_JOINS


def normalize_join_type(raw: str) -> tuple[str, str]:
    text = str(raw or "").strip().upper().replace(" ", "")
    text = text.replace("Δ", "DELTA").replace("Γ", "GAMMA").replace("Π", "PI")
    text = text.replace("↔", "-").replace("->", "-").replace("→", "-").replace("_", "-")
    aliases = {
        "D": "DELTA",
        "INTERVAL": "DELTA",
        "G": "GAMMA",
        "TRAJECTORY": "GAMMA",
        "P": "PI",
        "PATTERN": "PI",
        "CLOCK": "T",
    }
    parts = [p for p in text.split("-") if p]
    if len(parts) != 2:
        raise CardError("JOIN_REFUSE", f"join type must be A-B, got {raw!r}")
    left = aliases.get(parts[0], parts[0])
    right = aliases.get(parts[1], parts[1])
    return left, right


def refuse_join(left_axis: str, right_axis: str, *, backdate: bool = False) -> None:
    pair = (left_axis, right_axis)
    if pair in ILLEGAL_JOINS or backdate:
        raise CardError(
            "PI_T_BACKDATE",
            "illegal join: Π→T backdate refused (pattern cannot rewrite the clock)",
        )
    if pair not in ALLOWED_JOINS:
        raise CardError(
            "JOIN_REFUSE",
            f"illegal join {left_axis}→{right_axis}; allowed T↔Δ, Δ↔Γ, Γ↔Π, T↔Π",
        )


def join_cards(
    left: dict[str, Any],
    right: dict[str, Any],
    join_type: str | None = None,
    *,
    backdate: bool = False,
    note: str = "",
    src: str = "4dmap",
) -> dict[str, Any]:
    scan_identity(left)
    scan_identity(right)
    scan_intent(left)
    scan_intent(right)
    scan_intent(note)
    left_axis = axis_of(left)
    right_axis = axis_of(right)
    if join_type:
        left_axis, right_axis = normalize_join_type(join_type)
    refuse_join(left_axis, right_axis, backdate=backdate)

    cite = {"join": f"{left_axis}-{right_axis}", "left": left.get("id"), "right": right.get("id")}
    fields: dict[str, Any] = {"t": None, "delta": None, "gamma": None, "pi": None}
    if "T" in (left_axis, right_axis):
        fields["t"] = left.get("t") if axis_of(left) == "T" else right.get("t")
    if "DELTA" in (left_axis, right_axis):
        fields["delta"] = cite
    if "GAMMA" in (left_axis, right_axis):
        fields["gamma"] = cite
    if "PI" in (left_axis, right_axis):
        fields["pi"] = cite

    card = make_card(
        t=fields["t"],
        delta=fields["delta"],
        gamma=fields["gamma"],
        pi=fields["pi"],
        prev=str(left.get("h") or ""),
        src=src,
        note=note or f"typed join {left_axis}-{right_axis}",
    )
    # make_card may have set Π-EMPTY when pi is None; re-seal if we already hashed
    if card["h"] != digest(card):
        raise CardError("HASH_FAIL", "fail-closed: join card hash drifted")
    cites = []
    for src, axis in ((left.get("src"), left_axis), (right.get("src"), right_axis), (src, None)):
        cite = companion_cite(src, axis)
        if cite and cite not in cites and cite["slug"] not in {c["slug"] for c in cites}:
            cites.append(cite)
    return {
        "ok": True,
        "join": f"{left_axis}-{right_axis}",
        "allowed": True,
        "card": card,
        "left": left.get("id"),
        "right": right.get("id"),
        "receipt": card_receipt(card),
        "cites": cites,
        "companions_merged": False,
        "second_door": False,
        "note": "typed join cites companion softwares as inspection inputs only",
    }
