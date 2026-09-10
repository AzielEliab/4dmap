"""4DM-CARD schema, canonical encoding, fail-closed SHA-256.

Hashed fields (exclude ``h``):

    id, t, delta, gamma, pi, prev, src, note

UTF-8 JSON, sorted keys, no extra whitespace. Algorithm: SHA-256
lowercase hex. Genesis ``prev`` is 64 zero hex characters.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Any

from .scope import (
    AXIS_FRAME,
    AXIS_GLYPH,
    COMPANIONS,
    GENESIS_PREV,
    PI_EMPTY,
    SCHEMA,
)

CORE_FIELDS = ("delta", "gamma", "id", "note", "pi", "prev", "src", "t")

FORBIDDEN_KEYS = frozenset(
    {
        "legal_name",
        "legalname",
        "full_name",
        "fullname",
        "home",
        "home_address",
        "county",
        "ssn",
        "address",
        "street",
        "residence",
        "dob",
        "date_of_birth",
    }
)

_IDENTITY_PHRASES = (
    re.compile(r"\blegal\s+name\b", re.I),
    re.compile(r"\bhome\s+address\b", re.I),
    re.compile(r"\bcounty\s+of\b", re.I),
    re.compile(r"\b[A-Za-z][A-Za-z .'-]{1,40}\s+County\b"),
)

_INTENT_PHRASES = (
    re.compile(r"\bintent\b", re.I),
    re.compile(r"\bmotive\b", re.I),
    re.compile(r"\bguilt\b", re.I),
    re.compile(r"\bmeant to\b", re.I),
)


class CardError(ValueError):
    """Fail-closed card or join refusal."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def as_dict(self) -> dict[str, Any]:
        return {"ok": False, "refused": True, "code": self.code, "message": self.message}


def _norm_axis_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_norm_axis_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _norm_axis_value(value[k]) for k in sorted(value)}
    return str(value)


def canonical_payload(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "delta": _norm_axis_value(card.get("delta")),
        "gamma": _norm_axis_value(card.get("gamma")),
        "id": str(card.get("id") or ""),
        "note": str(card.get("note") or ""),
        "pi": _norm_axis_value(card.get("pi")),
        "prev": str(card.get("prev") or GENESIS_PREV),
        "src": str(card.get("src") or ""),
        "t": _norm_axis_value(card.get("t")),
    }


def canonical_bytes(card: dict[str, Any]) -> bytes:
    payload = canonical_payload(card)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw.encode("utf-8")


def digest(card: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(card)).hexdigest()


def scan_identity(value: Any, path: str = "") -> None:
    if isinstance(value, dict):
        for key, inner in value.items():
            low = str(key).lower().replace("-", "_")
            if low in FORBIDDEN_KEYS:
                raise CardError(
                    "IDENTITY_LEAK",
                    f"card field {path}{key} is a forbidden identity key (no legal name/home/county)",
                )
            scan_identity(inner, f"{path}{key}.")
        return
    if isinstance(value, (list, tuple)):
        for i, inner in enumerate(value):
            scan_identity(inner, f"{path}{i}.")
        return
    if isinstance(value, str):
        for pat in _IDENTITY_PHRASES:
            if pat.search(value):
                raise CardError(
                    "IDENTITY_LEAK",
                    "card text names a legal name, home, or county — refused",
                )


def scan_intent(value: Any) -> None:
    if isinstance(value, dict):
        for inner in value.values():
            scan_intent(inner)
        return
    if isinstance(value, (list, tuple)):
        for inner in value:
            scan_intent(inner)
        return
    if isinstance(value, str):
        for pat in _INTENT_PHRASES:
            if pat.search(value):
                raise CardError("INTENT_REFUSE", "4DMap does not infer or record intent, motive, or guilt")


def new_id() -> str:
    return "4dm-" + uuid.uuid4().hex[:12]


def make_card(
    *,
    id: str | None = None,
    t: Any = None,
    delta: Any = None,
    gamma: Any = None,
    pi: Any = None,
    prev: str | None = None,
    src: str = "operator",
    note: str = "",
    expected_h: str | None = None,
) -> dict[str, Any]:
    card = {
        "schema": SCHEMA,
        "id": id or new_id(),
        "t": t,
        "delta": delta,
        "gamma": gamma,
        "pi": PI_EMPTY if pi is None else pi,
        "prev": prev or GENESIS_PREV,
        "src": src,
        "note": note,
    }
    scan_identity(card)
    scan_intent(card)
    digest_h = digest(card)
    if expected_h and expected_h != digest_h:
        raise CardError("HASH_FAIL", "fail-closed: supplied h does not match canonical SHA-256")
    card["h"] = digest_h
    return card


def verify_card(card: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise CardError("HASH_FAIL", "fail-closed: card is not an object")
    scan_identity(card)
    scan_intent(card)
    expected = digest(card)
    got = str(card.get("h") or "")
    if got != expected:
        raise CardError("HASH_FAIL", "fail-closed: card hash mismatch")
    return {"ok": True, "id": card.get("id"), "h": expected}


def axis_of(card: dict[str, Any]) -> str:
    if card.get("t") not in (None, "") and card.get("delta") in (None, "") and card.get("gamma") in (None, ""):
        if card.get("pi") in (None, "", PI_EMPTY):
            return "T"
    if card.get("delta") not in (None, ""):
        return "DELTA"
    if card.get("gamma") not in (None, ""):
        return "GAMMA"
    if card.get("pi") not in (None, "", PI_EMPTY):
        return "PI"
    if card.get("t") not in (None, ""):
        return "T"
    return "T"


def normalize_axis(raw: Any) -> str:
    text = str(raw or "T").strip().upper().replace(" ", "")
    text = text.replace("Δ", "DELTA").replace("Γ", "GAMMA").replace("Π", "PI")
    aliases = {
        "T": "T",
        "CLOCK": "T",
        "TIME": "T",
        "D": "DELTA",
        "DELTA": "DELTA",
        "INTERVAL": "DELTA",
        "CHANGE": "DELTA",
        "G": "GAMMA",
        "GAMMA": "GAMMA",
        "TRAJECTORY": "GAMMA",
        "GEOMETRY": "GAMMA",
        "PATTERN": "PI",
        "P": "PI",
        "PI": "PI",
        "PROVENANCE": "PI",
        "PATH": "PI",
    }
    axis = aliases.get(text)
    if axis is None:
        raise CardError("AXIS_REFUSE", f"unknown axis {raw!r}; use T, Δ, Γ, or Π")
    return axis


def companion_cite(src: Any, axis: str | None = None) -> dict[str, Any] | None:
    key = str(src or "").strip().lower()
    info = COMPANIONS.get(key)
    if not info:
        return None
    cite = {
        "software": info["software"],
        "slug": info["slug"],
        "axes": list(info["axes"]),
        "role": "inspection_input",
        "cite_only": True,
        "door": False,
        "merged": False,
    }
    if axis:
        cite["axis"] = axis
    return cite


def card_receipt(card: dict[str, Any]) -> dict[str, Any]:
    """Non-hashed 4DM-CARD receipt. Does not change canonical ``h``."""
    axis = axis_of(card)
    src = str(card.get("src") or "")
    frame = AXIS_FRAME[axis]
    return {
        "schema": SCHEMA,
        "kind": "4DM-CARD",
        "id": card.get("id"),
        "h": card.get("h"),
        "axis": axis,
        "glyph": AXIS_GLYPH[axis],
        "name": frame["name"],
        "meaning": frame["meaning"],
        "src": src,
        "companion": companion_cite(src, axis),
        "role": "inspection",
        "door": False,
        "truth": False,
    }
