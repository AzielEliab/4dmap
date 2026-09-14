"""Self-check for 4DMap. No network, no telemetry."""

from __future__ import annotations

import json
from typing import Callable

from .card import CardError, digest, make_card, verify_card
from .example import EXAMPLE_PIN
from .joins import join_cards
from .ops import cap, dispatch, lens
from .scope import (
    AKM,
    AUTHOR,
    DISCOVERY,
    GUARDRAIL,
    LIMITATION,
    LIVE_OPS,
    MASTER33,
    PRODUCT,
    SPEC,
    ZION_CAP,
    __version__,
)
from .store import MapStore

Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__ == "0.3.0" and SPEC == "4DM-WP-1.0":
        return _ok("version", f"{__version__} {SPEC}")
    return _fail("version", f"{__version__} {SPEC}")


def _check_identity() -> Check:
    if AUTHOR != "Aziel Eliab":
        return _fail("identity", AUTHOR)
    blob = LIMITATION + GUARDRAIL + AUTHOR
    if "GodLock.AZ" in blob or "GodLock.AZ" in AUTHOR:
        return _fail("identity", "forbidden identity label leaked")
    return _ok("identity", AUTHOR)


def _check_hash() -> Check:
    again = digest(EXAMPLE_PIN)
    if again != EXAMPLE_PIN["h"]:
        return _fail("hash", "example pin hash unstable")
    verify_card(EXAMPLE_PIN)
    broken = dict(EXAMPLE_PIN)
    broken["h"] = "0" * 64
    try:
        verify_card(broken)
        return _fail("hash", "broken hash accepted")
    except CardError as err:
        if err.code != "HASH_FAIL":
            return _fail("hash", err.code)
    return _ok("hash", EXAMPLE_PIN["h"][:16])


def _check_illegal_join() -> Check:
    t = make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="clock")
    p = make_card(pi={"class": "repeat"}, src="synthetic", note="pattern")
    store = MapStore([t, p])
    try:
        join_cards(p, t, "PI-T")
        return _fail("join", "Π→T accepted")
    except CardError as err:
        if err.code != "PI_T_BACKDATE":
            return _fail("join", err.code)
    try:
        join_cards(p, t, backdate=True)
        return _fail("join", "backdate flag accepted")
    except CardError:
        pass
    ok = join_cards(t, p, "T-PI")
    if not ok.get("ok"):
        return _fail("join", "T-PI refused")
    store.add(ok["card"])
    return _ok("join", "T-PI allowed; Π→T refused")


def _check_forks() -> Check:
    a = make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="parent")
    store = MapStore([a])
    dispatch("fork", {"id": a["id"]}, store.as_list())
    # dispatch used a fresh store; fork in-place
    store = MapStore([a])
    from .ops import fork

    fork({"id": a["id"]}, store)
    forks = store.forks()
    if not forks or not forks[0].get("kept") or forks[0].get("winner") is not None:
        return _fail("fork", str(forks))
    if len(store.as_list()) != 2:
        return _fail("fork", "sibling not kept")
    return _ok("fork", "both branches kept")


def _check_pi_empty() -> Check:
    silent = lens({"query": ""}, MapStore())
    if silent.get("pi") != "Π-EMPTY":
        return _fail("pi", str(silent))
    miss = lens({"query": "no-such-pattern"}, MapStore([EXAMPLE_PIN]))
    if miss.get("pi") != "Π-EMPTY":
        return _fail("pi", str(miss))
    return _ok("pi", "Π-EMPTY when lens silent")


def _check_cap() -> Check:
    out = cap({"score": 0.99})
    if out["score"] != ZION_CAP or not out["capped"]:
        return _fail("cap", str(out))
    return _ok("cap", "ZionPattern 75%")


def _check_limitation() -> Check:
    low = LIMITATION.lower()
    needed = ("not: a truth engine", "lumen", "gis", "certified forensics", "node gate")
    missing = [n for n in needed if n not in low]
    if missing:
        return _fail("limitation", f"missing {missing}")
    return _ok("limitation", "honest banner")


def _check_frame() -> Check:
    if MASTER33.get("domains_are_doors") is not False:
        return _fail("frame", "domains must not be doors")
    if MASTER33.get("sequential_gate") is not False:
        return _fail("frame", "4DMap must not be a sequential gate")
    if MASTER33.get("door") != "fraggate" or MASTER33.get("role") != "inspection":
        return _fail("frame", str(MASTER33))
    if MASTER33.get("software_door") is not False:
        return _fail("frame", "4DMap must not be a Softwares door")
    needed = (
        "card_export",
        "card_import",
        "frame_status",
        "axis_describe",
        "walk_trace",
        "verify_chain",
        "memory_cite",
        "memory_observe",
        "library_pin",
        "plot",
        "possibility",
        "pattern_recall",
        "lattice_tip",
        "poison_refuse",
        "neighbor_cite",
    )
    missing = [op for op in needed if op not in LIVE_OPS]
    if missing:
        return _fail("frame", f"missing LIVE_OPS {missing}")
    try:
        dispatch("truth_score", {})
        return _fail("frame", "truth_score accepted")
    except CardError as err:
        if err.code != "STUB_REFUSE":
            return _fail("frame", err.code)
    status = dispatch("frame_status", {})
    if status.get("domains_are_doors") is not False or status.get("get_enables") is True:
        return _fail("frame", "frame_status framing drifted")
    if status.get("mesh", {}).get("get_enables") is True:
        return _fail("frame", "mesh GET must never enable")
    akm = status.get("akm") or {}
    if akm.get("software_tab") is not False or akm.get("door") is not False:
        return _fail("frame", "AKM must not be a Softwares slug or door")
    if akm.get("posterior_is_truth") is True or akm.get("history_rewrite") is True:
        return _fail("frame", "AKM posterior/history framing drifted")
    if "akm" in {c.get("slug") for c in status.get("companions") or []}:
        return _fail("frame", "AKM must not appear as a companion software")
    if AKM.get("software_tab") is not False:
        return _fail("frame", "AKM constant leaked onto Softwares tab")
    if status.get("growth") != "ON" or DISCOVERY.get("growth") != "ON":
        return _fail("frame", "Worker discovery Growth-ON missing")
    return _ok("frame", "MASTER-33 inspection frame; FragGate single door")


def _check_lattice() -> Check:
    mock = {
        "event": "synthetic paper event",
        "date": "1912-04-15",
        "lat": 41.726,
        "lon": -49.947,
        "surface": "MOCK",
        "src": "aziel-corpus",
        "note": "doctor MOCK library pin",
    }
    pinned = dispatch("library_pin", mock)
    if pinned.get("surface") != "MOCK" or pinned.get("ml_store") is True:
        return _fail("lattice", "library pin must be lattice-linked MOCK/REAL, not ML")
    if pinned.get("hooks", {}).get("possibility", {}).get("label") != "possibility":
        return _fail("lattice", "possibility hook unlabeled")
    if pinned.get("collapsed") is not False:
        return _fail("lattice", "scores collapsed")
    try:
        dispatch("library_pin", {"event": "x", "date": "1912-04-15", "lat": 200, "lon": 0, "surface": "MOCK"})
        return _fail("lattice", "malformed lat accepted")
    except CardError as err:
        if err.code != "ANCHOR_REFUSE":
            return _fail("lattice", err.code)
    try:
        dispatch("possibility", {"id": pinned["id"], "score": 0.9}, [pinned["card"]])
        return _fail("lattice", "unlabeled score accepted")
    except CardError as err:
        if err.code != "SCORE_COLLAPSE":
            return _fail("lattice", err.code)
    try:
        dispatch("ml_store", {})
        return _fail("lattice", "detached ML store accepted")
    except CardError as err:
        if err.code != "LATTICE_ONLY":
            return _fail("lattice", err.code)
    return _ok("lattice", "library pin + labeled scores + hashchain refuse")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_hash,
    _check_illegal_join,
    _check_forks,
    _check_pi_empty,
    _check_cap,
    _check_limitation,
    _check_frame,
    _check_lattice,
)


def run_doctor(*, as_json: bool = False) -> int:
    rows = [fn() for fn in CHECKS]
    ok = all(item[1] for item in rows)
    if as_json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "product": PRODUCT,
                    "author": AUTHOR,
                    "checks": [{"name": n, "ok": passed, "detail": d} for n, passed, d in rows],
                    "limitation": LIMITATION,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(f"4DMap doctor — {AUTHOR}")
        for name, passed, detail in rows:
            mark = "ok" if passed else "FAIL"
            print(f"  [{mark}] {name}: {detail}")
        print(LIMITATION if ok else "doctor failed")
    return 0 if ok else 1
