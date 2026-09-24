"""4DMap ops: pin/span/walk across T/Δ/Γ/Π plus lattice library pins.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
from typing import Any

from .area import estimate_area
from .card import (
    CardError,
    axis_of,
    card_receipt,
    companion_cite,
    make_card,
    normalize_axis,
    verify_card,
)
from .joins import join_cards
from .lattice import (
    lattice_tip,
    library_pin,
    neighbor_cite,
    pattern_recall,
    plot_model,
    poison_refuse,
    score_on_lattice,
)
from .memory import cite_card, observe_card
from .scope import (
    AXIS_FRAME,
    AXIS_GLYPH,
    AKM,
    AUTHOR,
    BUCKET,
    COMPANIONS,
    DISCOVERY,
    LIBRARY,
    GUARDRAIL,
    LIMITATION,
    LIVE_OPS,
    MASTER33,
    OP_ALIASES,
    PI_EMPTY,
    PIPELINE,
    PIPELINE_NOTE,
    PRODUCT,
    PRODUCT_NAME,
    REFUSE_OPS,
    SCHEMA,
    SPEC,
    ZION_CAP,
    __version__,
)
from .store import MapStore


def envelope(op: str, result: dict[str, Any]) -> dict[str, Any]:
    title = f"4DMap {op}"
    summary = result.get("message") or result.get("note") or ("ok" if result.get("ok", True) else "refused")
    fields = []
    for key in (
        "ok",
        "code",
        "id",
        "h",
        "join",
        "pi",
        "score",
        "capped",
        "forks_kept",
        "axis",
        "glyph",
        "n",
        "verified",
        "format",
        "role",
        "surface",
        "feature_h",
        "lattice",
        "collapsed",
    ):
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


def _with_receipt(result: dict[str, Any]) -> dict[str, Any]:
    card = result.get("card")
    if isinstance(card, dict):
        result.setdefault("receipt", card_receipt(card))
        result.setdefault("axis", result["receipt"]["axis"])
        result.setdefault("glyph", result["receipt"]["glyph"])
    return result


def _wants_library_pin(payload: dict[str, Any]) -> bool:
    if payload.get("ingest") or payload.get("pin_frame") or payload.get("descriptor"):
        return True
    if payload.get("event") or payload.get("gazetteer_id") or payload.get("gazetteer"):
        return True
    if payload.get("lat") is not None or payload.get("lon") is not None:
        return True
    if payload.get("date") or payload.get("paper_date") or payload.get("doc_id"):
        return True
    return False


def pin(payload: dict[str, Any], store: MapStore | None = None) -> dict[str, Any]:
    if _wants_library_pin(payload) and normalize_axis(payload.get("axis") or "T") == "T":
        cards = store.as_list() if store is not None else []
        out = library_pin(payload, cards)
        if store is not None:
            store.add(out["card"])
        return _with_receipt(out)
    axis = normalize_axis(payload.get("axis") or "T")
    src = str(payload.get("src") or "operator")
    note = str(payload.get("note") or f"{AXIS_GLYPH[axis]} pin")
    kwargs: dict[str, Any] = {
        "src": src,
        "note": note,
        "prev": payload.get("prev"),
        "id": payload.get("id"),
        "pi": PI_EMPTY,
    }
    if axis == "T":
        kwargs["t"] = payload.get("t")
    elif axis == "DELTA":
        kwargs["delta"] = payload.get("delta") or {"change": payload.get("value") or payload.get("t")}
        kwargs["t"] = payload.get("t")
    elif axis == "GAMMA":
        kwargs["gamma"] = payload.get("gamma") or {"geometry": payload.get("value") or payload.get("t")}
        kwargs["t"] = payload.get("t")
    else:
        kwargs["pi"] = payload.get("pi") if payload.get("pi") is not None else (payload.get("value") or PI_EMPTY)
        kwargs["t"] = payload.get("t")
    card = make_card(**kwargs)
    if store is not None:
        store.add(card)
    return _with_receipt(
        {
            "ok": True,
            "op": "pin",
            "axis": axis,
            "glyph": AXIS_GLYPH[axis],
            "card": card,
            "id": card["id"],
            "h": card["h"],
            "companion": companion_cite(src, axis),
        }
    )


def span(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    left = store.by_id(str(payload.get("from_id") or payload.get("a") or ""))
    right = store.by_id(str(payload.get("to_id") or payload.get("b") or ""))
    verify_card(left)
    verify_card(right)
    from_axis = axis_of(left)
    to_axis = axis_of(right)
    src = str(payload.get("src") or "operator")
    delta = {
        "from": left.get("id"),
        "to": right.get("id"),
        "from_t": left.get("t"),
        "to_t": right.get("t"),
        "from_axis": from_axis,
        "to_axis": to_axis,
        "from_glyph": AXIS_GLYPH[from_axis],
        "to_glyph": AXIS_GLYPH[to_axis],
    }
    card = make_card(
        t=None,
        delta=delta,
        src=src,
        note=str(payload.get("note") or "Δ span"),
        prev=str(right.get("h") or left.get("h")),
        pi=PI_EMPTY,
    )
    store.add(card)
    cites = [c for c in (companion_cite(left.get("src"), from_axis), companion_cite(right.get("src"), to_axis), companion_cite(src, "DELTA")) if c]
    return _with_receipt(
        {
            "ok": True,
            "op": "span",
            "axis": "DELTA",
            "glyph": "Δ",
            "card": card,
            "id": card["id"],
            "h": card["h"],
            "cites": cites,
            "companions_merged": False,
        }
    )


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
    return _with_receipt({"ok": True, "op": "stack", "axis": "GAMMA", "glyph": "Γ", "card": stacked, "id": stacked["id"], "h": stacked["h"]})


def gap(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    card = make_card(
        delta={"gap": True, "from": payload.get("from_id") or payload.get("t0"), "to": payload.get("to_id") or payload.get("t1")},
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or "Δ gap"),
        prev=payload.get("prev"),
        pi=PI_EMPTY,
    )
    store.add(card)
    return _with_receipt({"ok": True, "op": "gap", "axis": "DELTA", "glyph": "Δ", "card": card, "id": card["id"], "h": card["h"]})


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
    return _with_receipt(
        {
            "ok": True,
            "op": "fork",
            "card": sibling,
            "id": sibling["id"],
            "h": sibling["h"],
            "forks_kept": True,
            "winner": None,
            "forks": forks,
        }
    )


def _trace_steps(chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    steps = []
    for i, card in enumerate(chain):
        axis = axis_of(card)
        steps.append(
            {
                "i": i,
                "id": card.get("id"),
                "h": card.get("h"),
                "prev": card.get("prev"),
                "axis": axis,
                "glyph": AXIS_GLYPH[axis],
                "src": card.get("src"),
                "companion": companion_cite(card.get("src"), axis),
                "note": card.get("note"),
            }
        )
    return steps


def walk(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    tip = str(payload.get("tip") or payload.get("id") or "")
    chain = store.walk(tip)
    return {
        "ok": True,
        "op": "walk",
        "tip": tip,
        "cards": chain,
        "n": len(chain),
        "forks": store.forks(),
        "steps": _trace_steps(chain),
    }


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
    return _with_receipt({"ok": True, "op": "class", "pi": card["pi"], "card": card, "id": card["id"], "h": card["h"]})


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
    return _with_receipt({"ok": True, "op": "cohort", "card": card, "id": card["id"], "h": card["h"]})


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


def card_new(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    card = make_card(
        id=payload.get("id"),
        t=payload.get("t"),
        delta=payload.get("delta"),
        gamma=payload.get("gamma"),
        pi=payload.get("pi"),
        prev=payload.get("prev"),
        src=str(payload.get("src") or "operator"),
        note=str(payload.get("note") or "4DM-CARD"),
        expected_h=payload.get("expected_h") or payload.get("h"),
    )
    store.add(card)
    return _with_receipt({"ok": True, "op": "card_new", "card": card, "id": card["id"], "h": card["h"]})


def verify_hash(payload: dict[str, Any], store: MapStore | None = None) -> dict[str, Any]:
    card = payload.get("card")
    if card is None and store is not None and (payload.get("id") or payload.get("h")):
        if payload.get("id"):
            card = store.by_id(str(payload["id"]))
        else:
            card = store.by_hash(str(payload["h"]))
    if not isinstance(card, dict):
        raise CardError("HASH_FAIL", "fail-closed: card is not an object")
    checked = verify_card(card)
    return {"ok": True, "op": "verify_hash", **checked, "receipt": card_receipt(card)}


def card_export(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    cards = store.as_list()
    for card in cards:
        verify_card(card)
    bundle = {
        "format": "4DM-CARD-JSON",
        "schema": SCHEMA,
        "spec": SPEC,
        "version": __version__,
        "product": PRODUCT,
        "author": AUTHOR,
        "role": "inspection",
        "domains_are_doors": False,
        "cards": cards,
        "n": len(cards),
        "forks": store.forks(),
    }
    return {"ok": True, "op": "card_export", **bundle, "bundle": bundle}


def card_import(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    raw = payload.get("bundle") if payload.get("bundle") is not None else payload.get("json")
    if raw is None:
        raw = payload
    if isinstance(raw, str):
        raw = json.loads(raw)
    if isinstance(raw, list):
        incoming = raw
    elif isinstance(raw, dict):
        if isinstance(raw.get("cards"), list):
            incoming = raw["cards"]
        elif isinstance(raw.get("bundle"), dict) and isinstance(raw["bundle"].get("cards"), list):
            incoming = raw["bundle"]["cards"]
        elif raw.get("id") and raw.get("h"):
            incoming = [raw]
        else:
            incoming = []
    else:
        raise CardError("IMPORT_REFUSE", "card_import expects a JSON object or card list")
    imported = []
    existing_h = {c.get("h") for c in store.as_list()}
    for card in incoming:
        if not isinstance(card, dict):
            raise CardError("IMPORT_REFUSE", "each imported card must be an object")
        verify_card(card)
        if card.get("h") not in existing_h:
            store.add(card)
            existing_h.add(card.get("h"))
        imported.append(card)
    return {
        "ok": True,
        "op": "card_import",
        "format": "4DM-CARD-JSON",
        "n": len(imported),
        "cards": imported,
        "forks": store.forks(),
        "receipts": [card_receipt(c) for c in imported],
    }


def frame_status(payload: dict[str, Any] | None = None, store: MapStore | None = None) -> dict[str, Any]:
    _ = payload
    n = len(store.as_list()) if store is not None else 0
    companions = [
        {
            "software": info["software"],
            "slug": slug,
            "axes": list(info["axes"]),
            "role": "inspection_input",
            "cite_only": True,
            "door": False,
            "merged": False,
        }
        for slug, info in COMPANIONS.items()
    ]
    return {
        "ok": True,
        "op": "frame_status",
        "product": PRODUCT,
        "name": PRODUCT_NAME,
        "version": __version__,
        "spec": SPEC,
        "schema": SCHEMA,
        "bucket": BUCKET,
        "author": AUTHOR,
        "cards": n,
        "live_ops": list(LIVE_OPS),
        "refuse_ops": list(REFUSE_OPS),
        "companions": companions,
        "mesh": {"default_off": True, "get_enables": False, "node_gate": False},
        "library": LIBRARY,
        "growth": DISCOVERY["growth"],
        "discovery": DISCOVERY,
        "akm": AKM,
        "limitation": LIMITATION,
        "guardrail": GUARDRAIL,
        "pipeline": PIPELINE,
        "pipeline_note": PIPELINE_NOTE,
        **MASTER33,
    }


def axis_describe(payload: dict[str, Any] | None = None, store: MapStore | None = None) -> dict[str, Any]:
    payload = payload or {}
    wanted = payload.get("axis")
    axes = {}
    for key, frame in AXIS_FRAME.items():
        if wanted and normalize_axis(wanted) != key:
            continue
        axes[key] = {
            **frame,
            "companions": [
                {
                    "software": COMPANIONS[slug]["software"],
                    "slug": slug,
                    "role": "inspection_input",
                    "cite_only": True,
                    "door": False,
                    "merged": False,
                }
                for slug in frame["companions"]
            ],
            "ops": list(frame["ops"]),
        }
    if wanted and not axes:
        raise CardError("AXIS_REFUSE", f"unknown axis {wanted!r}")
    return {
        "ok": True,
        "op": "axis_describe",
        "axis": normalize_axis(wanted) if wanted else None,
        "axes": axes,
        "role": "inspection",
        "domains_are_doors": False,
        "n": len(store.as_list()) if store is not None else 0,
    }


def walk_trace(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    walked = walk(payload, store)
    steps = walked["steps"]
    return {
        "ok": True,
        "op": "walk_trace",
        "tip": walked["tip"],
        "n": walked["n"],
        "steps": steps,
        "cards": walked["cards"],
        "forks": walked["forks"],
        "genesis": bool(steps) and str(steps[0].get("prev") or "").strip("0") == "",
        "role": "inspection",
    }


def verify_chain(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    tip = str(payload.get("tip") or payload.get("id") or "")
    chain = store.walk(tip)
    hashes = []
    for card in chain:
        checked = verify_card(card)
        hashes.append(checked["h"])
    return {
        "ok": True,
        "op": "verify_chain",
        "tip": tip,
        "verified": len(hashes),
        "n": len(hashes),
        "hashes": hashes,
        "broken": None,
        "steps": _trace_steps(chain),
        "forks": store.forks(),
    }


def _card_from_payload(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    if isinstance(payload.get("card"), dict):
        return payload["card"]
    card_id = str(payload.get("id") or payload.get("tip") or "")
    if card_id:
        return store.by_id(card_id)
    raise CardError("NOT_FOUND", "memory cite/observe needs a card id or card object")


def memory_cite(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    return cite_card(_card_from_payload(payload, store), payload)


def memory_observe(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    return observe_card(_card_from_payload(payload, store), payload)


def _library_pin(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    out = library_pin(payload, store.as_list())
    store.add(out["card"])
    return _with_receipt(out)


def _plot(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    _ = payload
    return plot_model(store.as_list())


def _possibility(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    return _with_receipt(score_on_lattice(payload, store.as_list(), store.add))


def _pattern_recall(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    return _with_receipt(pattern_recall(payload, store.as_list(), store.add))


def _lattice_tip(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    _ = payload
    return lattice_tip(store.as_list())


def _poison_refuse(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    return _with_receipt(poison_refuse(payload, store.as_list(), store.add))


def _neighbor_cite(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    return neighbor_cite(payload, store.as_list())


def _area_estimate(payload: dict[str, Any], store: MapStore) -> dict[str, Any]:
    _ = store
    return estimate_area(payload)


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
    "card_new": card_new,
    "verify_hash": verify_hash,
    "card_export": card_export,
    "card_import": card_import,
    "frame_status": frame_status,
    "axis_describe": axis_describe,
    "walk_trace": walk_trace,
    "verify_chain": verify_chain,
    "memory_cite": memory_cite,
    "memory_observe": memory_observe,
    "library_pin": _library_pin,
    "plot": _plot,
    "possibility": _possibility,
    "pattern_recall": _pattern_recall,
    "lattice_tip": _lattice_tip,
    "poison_refuse": _poison_refuse,
    "neighbor_cite": _neighbor_cite,
    "area_estimate": _area_estimate,
}


def _refuse(op: str) -> None:
    if op in REFUSE_OPS:
        code, message = REFUSE_OPS[op]
        raise CardError(code, message)


def dispatch(op: str, payload: dict[str, Any] | None = None, cards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = payload or {}
    resolved = OP_ALIASES.get(op, op)
    _refuse(op)
    _refuse(resolved)
    store = MapStore(cards)
    if resolved in {"list", "card_list"}:
        return {"ok": True, "op": "list", "cards": store.as_list(), "forks": store.forks(), "receipts": [card_receipt(c) for c in store.as_list()]}
    if resolved == "example":
        from .example import EXAMPLE_CARDS

        return {"ok": True, "synthetic": True, "cards": EXAMPLE_CARDS, "limitation": LIMITATION}
    fn = OPS.get(resolved)
    if fn is None:
        raise CardError("UNKNOWN_OP", f"unknown op {op}")
    if resolved == "cap":
        return fn(payload)
    return fn(payload, store)
