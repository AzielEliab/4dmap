"""4DMap ops: pin, span, stack, gap, fork, walk, lens, class, cohort, absence, cap, join.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from .card import CardError, make_card, verify_card
from .joins import join_cards
from .scope import PI_EMPTY, ZION_CAP
from .store import MapStore


def envelope(op: str, result: dict[str, Any]) -> dict[str, Any]:
    title = f"4DMap {op}"
    summary = result.get("message") or result.get("note") or ("ok" if result.get("ok", True) else "refused")
    fields = []
    for key in ("ok", "code", "id", "h", "join", "pi", "score", "capped", "forks_kept"):
        if key in result:
            fields.append({"label": key, "value": str(result[key])})
    return {
        "display": {
            "title": title,
            "summary": summary,
            "fields": fields,
            "next": "Show this 4DMap output, then take the next input.",
        },
        "result": result,
    }


def pin(payload: dict[str, Any], store: MapStore | None = None) -> dict[str, Any]:
    card = make_card(
        t=payload.get("t"),
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or "T pin"),
        prev=payload.get("prev"),
        id=payload.get("id"),
        pi=PI_EMPTY,
    )
    if store is not None:
        store.add(card)
    return {"ok": True, "op": "pin", "axis": "T", "card": card, "id": card["id"], "h": card["h"]}


def span(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    left = store.by_id(str(payload.get("from_id") or payload.get("a") or ""))
    right = store.by_id(str(payload.get("to_id") or payload.get("b") or ""))
    verify_card(left)
    verify_card(right)
    card = make_card(
        t=None,
        delta={"from": left.get("id"), "to": right.get("id"), "from_t": left.get("t"), "to_t": right.get("t")},
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or "Δ span"),
        prev=str(right.get("h") or left.get("h")),
        pi=PI_EMPTY,
    )
    store.add(card)
    return {"ok": True, "op": "span", "axis": "DELTA", "card": card, "id": card["id"], "h": card["h"]}


def stack(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    ids = list(payload.get("ids") or [])
    cards = [store.by_id(str(i)) for i in ids]
    for card in cards:
        verify_card(card)
    stacked = make_card(
        gamma={"stack": [c.get("id") for c in cards], "hs": [c.get("h") for c in cards]},
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or "Γ stack"),
        prev=str(cards[-1]["h"]) if cards else None,
        pi=PI_EMPTY,
    )
    store.add(stacked)
    return {"ok": True, "op": "stack", "axis": "GAMMA", "card": stacked, "id": stacked["id"], "h": stacked["h"]}


def gap(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    card = make_card(
        delta={"gap": True, "from": payload.get("from_id") or payload.get("t0"), "to": payload.get("to_id") or payload.get("t1")},
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or "Δ gap"),
        prev=payload.get("prev"),
        pi=PI_EMPTY,
    )
    store.add(card)
    return {"ok": True, "op": "gap", "axis": "DELTA", "card": card, "id": card["id"], "h": card["h"]}


def fork(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    source = store.by_id(str(payload.get("id") or ""))
    verify_card(source)
    sibling = make_card(
        t=source.get("t"),
        delta=source.get("delta"),
        gamma=source.get("gamma"),
        pi=source.get("pi"),
        prev=str(source.get("prev")),
        src=str(payload.get("src") or source.get("src") or "operator"),
        note=str(payload.get("note") or "fork kept"),
    )
    store.add(sibling)
    forks = store.forks()
    return {
        "ok": True,
        "op": "fork",
        "card": sibling,
        "id": sibling["id"],
        "h": sibling["h"],
        "forks_kept": True,
        "winner": None,
        "forks": forks,
    }


def walk(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    tip = str(payload.get("tip") or payload.get("id") or "")
    chain = store.walk(tip)
    return {"ok": True, "op": "walk", "tip": tip, "cards": chain, "n": len(chain), "forks": store.forks()}


def lens(payload: dict[str, Any], store: MapStore | None = None) -> dict[str, Any]:
    query = str(payload.get("query") or "").strip()
    cards = list((store.as_list() if store is not None else payload.get("cards")) or [])
    if not query:
        return {"ok": True, "op": "lens", "pi": PI_EMPTY, "silent": True, "note": "lens silent → Π-EMPTY"}
    hits = []
    for card in cards:
        blob = " ".join(str(card.get(k) or "") for k in ("id", "note", "src", "t", "pi"))
        if query.lower() in blob.lower():
            hits.append(card.get("id"))
    if not hits:
        return {"ok": True, "op": "lens", "pi": PI_EMPTY, "silent": True, "note": "lens silent → Π-EMPTY"}
    return {"ok": True, "op": "lens", "pi": {"class": "lens-hit", "ids": hits}, "silent": False, "hits": hits}


def classify(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    label = str(payload.get("label") or "").strip()
    if not label:
        return {"ok": True, "op": "class", "pi": PI_EMPTY, "silent": True}
    card = make_card(
        pi={"class": label},
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or f"Π class {label}"),
        prev=payload.get("prev"),
    )
    store.add(card)
    return {"ok": True, "op": "class", "pi": card["pi"], "card": card, "id": card["id"], "h": card["h"]}


def cohort(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    ids = [str(i) for i in (payload.get("ids") or [])]
    if not ids:
        return {"ok": True, "op": "cohort", "pi": PI_EMPTY, "silent": True}
    card = make_card(
        pi={"cohort": ids},
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or "Π cohort"),
        prev=payload.get("prev"),
    )
    store.add(card)
    return {"ok": True, "op": "cohort", "card": card, "id": card["id"], "h": card["h"]}


def absence(payload: dict[str, Any], store: MapStore | None = None) -> dict[str, Any]:
    looked = lens(payload, store)
    if looked.get("silent"):
        return {"ok": True, "op": "absence", "pi": PI_EMPTY, "silent": True, "note": "absence / lens silent → Π-EMPTY"}
    return {"ok": True, "op": "absence", "pi": looked.get("pi"), "silent": False, "hits": looked.get("hits")}


def cap(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        score = float(payload.get("score") if payload.get("score") is not None else payload.get("confidence") or 0)
    except (TypeError, ValueError) as exc:
        raise CardError("CAP_REFUSE", "score must be a number") from exc
    capped = min(max(score, 0.0), ZION_CAP)
    return {
        "ok": True,
        "op": "cap",
        "score": capped,
        "raw": score,
        "capped": score > ZION_CAP,
        "zion_cap": ZION_CAP,
        "note": "ZionPattern cap 75%",
    }


def join(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    left = store.by_id(str(payload.get("left") or payload.get("a") or ""))
    right = store.by_id(str(payload.get("right") or payload.get("b") or ""))
    out = join_cards(
        left,
        right,
        payload.get("join_type") or payload.get("type"),
        backdate=bool(payload.get("backdate")),
        note=str(payload.get("note") or ""),
        src=str(payload.get("src") or "4dmap"),
    )
    store.add(out["card"])
    return out


OPS = {
    "pin": pin,
    "span": span,
    "stack": stack,
    "gap": gap,
    "fork": fork,
    "walk": walk,
    "lens": lens,
    "class": classify,
    "cohort": cohort,
    "absence": absence,
    "cap": cap,
    "join": join,
}


def dispatch(op: str, payload: dict[str, Any] | None = None, cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = payload or {}
    store = MapStore(cards)
    if op == "list":
        return {"ok": True, "op": "list", "cards": store.as_list(), "forks": store.forks()}
    fn = OPS.get(op)
    if fn is None:
        raise CardError("UNKNOWN_OP", f"unknown op {op}")
    if op in {"pin"}:
        return fn(payload, store)
    if op in {"cap"}:
        return fn(payload)
    if op in {"lens", "absence"}:
        return fn(payload, store)
    return fn(payload, store)
