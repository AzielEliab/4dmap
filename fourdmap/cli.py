"""4DMap CLI: pin, span, join, fork, walk, doctor, ui.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .card import CardError
from .ops import dispatch
from .scope import AUTHOR, DEFAULT_PORT, LIMITATION, PRODUCT, __version__


def _load_cards(path: str | None) -> list[dict]:
    if not path:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("cards"), list):
        return data["cards"]
    return [data]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="4dmap",
        description="4DMap — inspection coordinate frame (4DM-WP-1.0). Not a truth engine.",
        epilog=LIMITATION,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help="Print package version.")
    p_doc = sub.add_parser("doctor", help="Self-check: hash, illegal join, fork keep, Π-EMPTY. No network.")
    p_doc.add_argument("--json", action="store_true", dest="as_json")
    p_ui = sub.add_parser("ui", help=f"Serve the local UI on 127.0.0.1:{DEFAULT_PORT} (loopback only).")
    p_ui.add_argument("--host", default="127.0.0.1")
    p_ui.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub.add_parser("server", help="Alias of ui.")

    def add_cards(p: argparse.ArgumentParser) -> None:
        p.add_argument("--cards", help="JSON file of existing cards")
        p.add_argument("-o", "--output", help="Write JSON result")

    p_pin = sub.add_parser("pin", help="Pin a T clock card")
    p_pin.add_argument("--t", required=True)
    p_pin.add_argument("--src", default="operator")
    p_pin.add_argument("--note", default="T pin")
    add_cards(p_pin)

    p_span = sub.add_parser("span", help="Span Δ between two pins")
    p_span.add_argument("--from-id", required=True)
    p_span.add_argument("--to-id", required=True)
    add_cards(p_span)

    p_join = sub.add_parser("join", help="Typed join T↔Δ, Δ↔Γ, Γ↔Π, T↔Π")
    p_join.add_argument("--left", required=True)
    p_join.add_argument("--right", required=True)
    p_join.add_argument("--type", dest="join_type", required=True)
    add_cards(p_join)

    p_fork = sub.add_parser("fork", help="Fork a card; both branches are kept")
    p_fork.add_argument("--id", required=True)
    add_cards(p_fork)

    p_walk = sub.add_parser("walk", help="Walk prev hashes from a tip")
    p_walk.add_argument("--tip", required=True)
    add_cards(p_walk)

    p_lens = sub.add_parser("lens", help="Apply a lens; silent → Π-EMPTY")
    p_lens.add_argument("--query", default="")
    add_cards(p_lens)

    p_cap = sub.add_parser("cap", help="ZionPattern cap 75%")
    p_cap.add_argument("--score", type=float, required=True)

    p_demo = sub.add_parser("demo", help="Run the synthetic example (not a real case)")
    p_demo.add_argument("-o", "--output")
    return parser


def _write(result: dict, output: str | None) -> int:
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "version":
        print(f"{PRODUCT} {__version__}")
        print(f"author {AUTHOR}")
        return 0

    if args.command == "doctor":
        from .doctor import run_doctor

        return run_doctor(as_json=args.as_json)

    if args.command in ("ui", "server"):
        from .server import serve

        serve(host=getattr(args, "host", "127.0.0.1"), port=getattr(args, "port", DEFAULT_PORT))
        return 0

    try:
        if args.command == "demo":
            from .example import EXAMPLE_CARDS

            result = {"ok": True, "synthetic": True, "cards": EXAMPLE_CARDS, "limitation": LIMITATION}
            return _write(result, args.output)
        if args.command == "cap":
            return _write(dispatch("cap", {"score": args.score}), None)
        cards = _load_cards(getattr(args, "cards", None))
        payload = {k: v for k, v in vars(args).items() if k not in {"command", "cards", "output"} and v is not None}
        result = dispatch(args.command, payload, cards)
        result["cards_out"] = cards
        if "card" in result:
            cards = cards + [result["card"]]
            result["cards_out"] = cards
        return _write(result, getattr(args, "output", None))
    except CardError as err:
        print(json.dumps(err.as_dict(), indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
