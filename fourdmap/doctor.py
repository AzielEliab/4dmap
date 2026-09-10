"""Self-check for 4DMap. No network, no telemetry."""

from __future__ import annotations

import json
from typing import Callable

from .card import CardError, digest, make_card, verify_card
from .example import EXAMPLE_PIN
from .joins import join_cards
from .ops import cap, dispatch, lens
from .scope import AUTHOR, GUARDRAIL, LIMITATION, PRODUCT, SPEC, ZION_CAP, __version__
from .store import MapStore

Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__ == "0.1.0" and SPEC == "4DM-WP-1.0":
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


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_hash,
    _check_illegal_join,
    _check_forks,
    _check_pi_empty,
    _check_cap,
    _check_limitation,
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
