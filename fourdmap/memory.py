"""Optional AKM-TRIAD-1.0 fabric pairing for 4DMap inspection cards.

AKM is LIVE fabric on aziel-runtime — not a Softwares-tab product,
not a 4DMap companion slug, not a second door. Cite / observe only.
Posterior ≠ truth. No history rewrite. Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from .card import CardError, axis_of, card_receipt, verify_card
from .scope import AKM, AXIS_GLYPH, PRODUCT, SCHEMA, SPEC, __version__


def refuse_akm_abuse(payload: dict[str, Any] | None) -> None:
    payload = payload or {}
    if payload.get("rewrite") or payload.get("history_rewrite") or payload.get("backdate"):
        raise CardError("AKM_REWRITE", "AKM-TRIAD-1.0 does not rewrite history; 4DM-CARD prev chain is fail-closed")
    if payload.get("truth") or payload.get("posterior_is_truth") is True:
        raise CardError("AKM_TRUTH", "posterior ≠ truth; 4DMap receipts are not truth")
    slug = str(payload.get("slug") or payload.get("software") or "").strip().lower().replace("_", "-")
    if payload.get("software_tab") or slug in {"akm", "akm-triad", "akm-triad-1.0", "memory"}:
        raise CardError(
            "AKM_SOFTWARE",
            "AKM-TRIAD-1.0 is LIVE fabric, not a Softwares-tab slug or second door",
        )


def observation_from_card(card: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    verify_card(card)
    axis = axis_of(card)
    fact = str(
        payload.get("fact")
        or (
            f"4DM-CARD {card.get('id')} axis={axis} glyph={AXIS_GLYPH[axis]} "
            f"h={card.get('h')} src={card.get('src')} — inspection receipt, not truth"
        )
    )
    return {
        "kind": "memory_observation",
        "spec": AKM["spec"],
        "subject": str(payload.get("subject") or f"{PRODUCT}:{card.get('id')}"),
        "fact": fact,
        "memory_id": payload.get("memory_id"),
        "use_case": str(payload.get("use_case") or "4dmap-inspection-cite"),
        "card": {
            "schema": SCHEMA,
            "spec": SPEC,
            "id": card.get("id"),
            "h": card.get("h"),
            "axis": axis,
            "glyph": AXIS_GLYPH[axis],
            "src": card.get("src"),
            "prev": card.get("prev"),
        },
        "triad": list(AKM["triad"]),
        "triad_rule": AKM["triad_rule"],
        "posterior_is_truth": False,
        "belief_is_not_truth": True,
        "authorizes_action": False,
        "history_rewrite": False,
        "software_tab": False,
        "door": False,
        "fabric": True,
        "learn": AKM["learn"],
        "fraggate": "memory_observe",
        "http": "POST /v1/memory/observe",
        "note": AKM["note"],
        "author": AKM["author"],
        "fourdmap_version": __version__,
    }


def cite_card(card: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
    refuse_akm_abuse(payload)
    verify_card(card)
    receipt = card_receipt(card)
    return {
        "ok": True,
        "op": "memory_cite",
        "id": card.get("id"),
        "h": card.get("h"),
        "receipt": receipt,
        "cited": True,
        "card_rewritten": False,
        "history_rewrite": False,
        "posterior_is_truth": False,
        "belief_is_not_truth": True,
        "authorizes_action": False,
        "software_tab": False,
        "door": False,
        "fabric": True,
        "akm": AKM,
        "note": "optional AKM-TRIAD-1.0 fabric cite. Inspection card unchanged. Posterior ≠ truth.",
    }


def observe_card(card: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
    refuse_akm_abuse(payload)
    payload = payload or {}
    observation = observation_from_card(card, payload)
    return {
        "ok": True,
        "op": "memory_observe",
        "id": card.get("id"),
        "h": card.get("h"),
        "receipt": card_receipt(card),
        "observation": observation,
        "forwarded": False,
        "card_rewritten": False,
        "history_rewrite": False,
        "posterior_is_truth": False,
        "belief_is_not_truth": True,
        "authorizes_action": False,
        "software_tab": False,
        "door": False,
        "fabric": True,
        "akm": AKM,
        "fraggate": "memory_observe",
        "http": "POST /v1/memory/observe",
        "note": (
            "optional observation packet for FragGate memory_observe. "
            "4DMap does not own AKM. Not forwarded unless the operator uses FragGate. "
            "Posterior ≠ truth. No history rewrite."
        ),
    }
