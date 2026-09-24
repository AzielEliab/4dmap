"""4DMap CLI: pin, span, join, fork, walk, doctor, ui.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Sequence

from .card import CardError
from .ops import dispatch
from .scope import AUTHOR, DEFAULT_PORT, LIMITATION, LOOPBACK, PRODUCT, __version__


class CliUsage(Exception):
    """A person can fix this without a traceback."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _escape_lone_percent(text: str) -> str:
    """Keep %(name)s placeholders and escape a bare % so help cannot crash."""
    out: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "%":
            if i + 1 < len(text) and text[i + 1] == "%":
                out.append("%%")
                i += 2
                continue
            if i + 1 < len(text) and text[i + 1] == "(":
                out.append("%")
                i += 1
                continue
            out.append("%%")
            i += 1
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


class SafeHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Help text may contain a percent sign (for example a capped score)."""

    def _iter_indented_subactions(self, action):
        for subaction in super()._iter_indented_subactions(action):
            if subaction.help is argparse.SUPPRESS:
                continue
            yield subaction

    def _format_action(self, action: argparse.Action) -> str:
        if isinstance(action, argparse._SubParsersAction):
            parts = [self._format_action(subaction) for subaction in self._iter_indented_subactions(action)]
            return self._join_parts(parts)
        return super()._format_action(action)

    def _expand_help(self, action: argparse.Action) -> str:
        params = dict(vars(action), prog=self._prog)
        for name in list(params):
            if params[name] is argparse.SUPPRESS:
                del params[name]
        for name in list(params):
            value = params[name]
            if hasattr(value, "__name__"):
                params[name] = value.__name__
        if params.get("choices") is not None:
            params["choices"] = ", ".join(str(choice) for choice in params["choices"])
        help_string = self._get_help_string(action) or ""
        return _escape_lone_percent(help_string) % params


class MapParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("formatter_class", SafeHelpFormatter)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        choice = re.search(r"invalid choice: '([^']*)'", message)
        if choice:
            name = choice.group(1) or "that"
            text = f'Unknown command "{name}". Try: 4dmap ui   or   4dmap --help\n'
        elif message.startswith("the following arguments are required:"):
            missing = message.split(":", 1)[1].strip()
            text = f"Missing {missing}.\nTry: {self.prog} --help\n"
        elif message.startswith("unrecognized arguments:"):
            extra = message.split(":", 1)[1].strip()
            text = f"Unexpected {extra}.\nTry: {self.prog} --help\n"
        elif "invalid" in message and "value" in message:
            text = f"{message}.\nTry: {self.prog} --help\n"
        else:
            text = f"{message}.\nTry: {self.prog} --help\n"
        self.exit(2, text)


_SKIP_PAYLOAD = {"command", "cards", "output", "bundle", "as_json", "command_json", "host", "port"}

_TITLES = {
    "pin": "Pinned a card",
    "span": "Spanned an interval",
    "join": "Joined two cards",
    "fork": "Kept both branches",
    "walk": "Walked previous hashes",
    "walk_trace": "Walked the chain with axis receipts",
    "verify_chain": "Verified the previous-hash chain",
    "verify_hash": "Verified the card hash",
    "lens": "Applied a lens",
    "cap": "Applied the ZionPattern cap",
    "card_export": "Exported cards",
    "export": "Exported cards",
    "card_import": "Imported cards",
    "import": "Imported cards",
    "frame_status": "Inspection frame status",
    "frame-status": "Inspection frame status",
    "axis_describe": "Axis description",
    "axis-describe": "Axis description",
    "memory_cite": "Memory cite",
    "memory-cite": "Memory cite",
    "memory_observe": "Memory observe packet",
    "memory-observe": "Memory observe packet",
    "library_pin": "Pinned a library event",
    "library-pin": "Pinned a library event",
    "plot": "Lattice plot",
    "possibility": "Labeled possibility",
    "pattern_recall": "Pattern recall",
    "pattern-recall": "Pattern recall",
    "lattice_tip": "Lattice tips",
    "lattice-tip": "Lattice tips",
    "poison_refuse": "Poison feature recorded on the refuse set",
    "poison-refuse": "Poison feature recorded on the refuse set",
    "neighbor_cite": "Library cite",
    "neighbor-cite": "Library cite",
    "demo": "Synthetic example",
}


def _welcome() -> str:
    return (
        f"4DMap {__version__} places inspection cards on a clock, an interval, a trajectory, and a pattern.\n"
        "\n"
        "Open the local workbench and pin the first card.\n"
        "\n"
        f"  4dmap ui       open http://{LOOPBACK}:{DEFAULT_PORT}/\n"
        "  4dmap doctor   self-check on this computer\n"
        "  4dmap --help   commands and examples\n"
        "\n"
        f"Author: {AUTHOR}\n"
    )


def _load_cards(path: str | None) -> list[dict]:
    if not path:
        return []
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CliUsage(f'No card file at "{path}". Check the path and try again.') from exc
    except OSError as exc:
        raise CliUsage(f'Could not read "{path}". Check the path and try again.') from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CliUsage(f'"{path}" is not JSON. Use a card file from 4dmap export.') from exc
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("cards"), list):
        return data["cards"]
    if isinstance(data, dict):
        return [data]
    raise CliUsage(f'"{path}" is not a card file. Use a card file from 4dmap export.')


def _wants_json(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "as_json", False) or getattr(args, "command_json", False))


def _add_field(lines: list[str], label: str, value: object) -> None:
    if value is None or isinstance(value, (dict, list)):
        return
    lines.append(f"  {label:<12} {value}")


def _human_result(command: str, result: dict) -> str:
    op = str(result.get("op") or command)
    lines = [_TITLES.get(op, _TITLES.get(command, f"Finished {command}"))]
    _add_field(lines, "id", result.get("id"))
    _add_field(lines, "hash", result.get("h"))
    _add_field(lines, "axis", result.get("axis"))
    _add_field(lines, "glyph", result.get("glyph"))
    card = result.get("card")
    if isinstance(card, dict):
        _add_field(lines, "source", card.get("src"))
        if result.get("t") is None:
            _add_field(lines, "time", card.get("t"))
    if isinstance(result.get("pi"), str):
        _add_field(lines, "pattern", result.get("pi"))
    _add_field(lines, "cards", result.get("n"))
    _add_field(lines, "verified", result.get("verified"))
    _add_field(lines, "score", result.get("score"))
    _add_field(lines, "capped", result.get("capped"))
    _add_field(lines, "surface", result.get("surface"))
    _add_field(lines, "silent", result.get("silent"))
    if result.get("synthetic") is True:
        _add_field(lines, "example", "synthetic")
    if isinstance(result.get("cards"), list) and "n" not in result:
        _add_field(lines, "cards", len(result["cards"]))
    note = result.get("note")
    if isinstance(note, str) and note and len(note) <= 160:
        _add_field(lines, "note", note)
    if command == "demo":
        lines.append("")
        lines.append("Next: 4dmap demo -o example.json")
    else:
        lines.append("")
        lines.append("Next: 4dmap ui")
    return "\n".join(lines) + "\n"


def _emit(result: dict, output: str | None, as_json: bool, command: str = "") -> int:
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
        return 0
    if as_json:
        print(rendered)
        return 0
    label = command or str(result.get("op") or "")
    print(_human_result(label, result), end="")
    return 0


def _build_parser() -> MapParser:
    parser = MapParser(
        prog="4dmap",
        usage="4dmap [--json] <command> [options]",
        description=(
            "4DMap places inspection cards on a clock (T), an interval (Δ), "
            "a trajectory (Γ), and a pattern (Π).\n"
            f"Author: {AUTHOR}."
        ),
        epilog=(
            "Advanced commands:\n"
            "  fork             Keep both branches of a card\n"
            "  lens             Apply a lens. Silence returns Π-EMPTY\n"
            "  cap              Apply the ZionPattern cap of 0.75\n"
            "  export           Export 4DM-CARD JSON\n"
            "  import           Import 4DM-CARD JSON\n"
            "  frame-status     Show inspection-frame status\n"
            "  axis-describe    Describe T, Δ, Γ, and Π\n"
            "  walk-trace       Walk a tip with axis receipts\n"
            "  verify-chain     Verify a previous-hash chain\n"
            "  verify-hash      Verify one card hash\n"
            "  memory-cite      Cite memory fabric on a card\n"
            "  memory-observe   Build a memory observe packet from a card\n"
            "  library-pin      Pin a library event on the lattice\n"
            "  plot             List lattice pins and trajectories\n"
            "  possibility      Show a labeled possibility on a card\n"
            "  pattern-recall   Recall patterns from the hashchain lattice\n"
            "  lattice-tip      List lattice tips\n"
            "  poison-refuse    Append a poison feature hash to the refuse set\n"
            "  neighbor-cite    Cite the Aziel Digital Library on a card\n"
            "  server           Same as ui\n"
            "\n"
            "Examples:\n"
            "  4dmap\n"
            "  4dmap ui\n"
            "  4dmap pin --t 2026-09-10T00:00:00Z --src synthetic\n"
            "  4dmap doctor\n"
            "  4dmap pin --json --t 2026-09-10T00:00:00Z --src synthetic\n"
            "\n"
            "Add --json on a command for the machine object.\n"
            f"Author: {AUTHOR}"
        ),
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print machine JSON")
    json_flags = argparse.ArgumentParser(add_help=False)
    json_flags.add_argument("--json", action="store_true", dest="command_json", help="Print machine JSON")

    sub = parser.add_subparsers(
        dest="command",
        metavar="<command>",
        title="Common commands",
        required=False,
        prog="4dmap",
    )

    sub.add_parser("version", parents=[json_flags], help="Print the version and author")
    p_doc = sub.add_parser(
        "doctor",
        parents=[json_flags],
        help="Self-check on this computer. No network",
    )
    p_ui = sub.add_parser(
        "ui",
        help=f"Open the local workbench at http://{LOOPBACK}:{DEFAULT_PORT}/",
    )
    p_ui.add_argument("--host", default=LOOPBACK, help="Loopback address (127.0.0.1)")
    p_ui.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port (default {DEFAULT_PORT})")
    sub.add_parser("server", help=argparse.SUPPRESS)
    p_shadow = sub.add_parser(
        "shadow",
        parents=[json_flags],
        help="Show ShadowLock links from this computer",
        description="Read ~/.shadowlock/links.json and list linked Softwares in time order.",
        epilog="Example: 4dmap shadow --links examples/shadowlock-links.json",
    )
    p_shadow.add_argument(
        "--links",
        default=None,
        help="Link file. Default: ~/.shadowlock/links.json or SHADOWLOCK_LINKS",
    )

    def add_cards(target: argparse.ArgumentParser) -> None:
        target.add_argument("--cards", help="JSON file of existing cards")
        target.add_argument("-o", "--output", help="Write the machine JSON to this file")

    p_pin = sub.add_parser(
        "pin",
        parents=[json_flags],
        help="Pin a clock, interval, trajectory, or pattern card",
        description="Pin a card on T, Δ, Γ, or Π.",
        epilog="Example: 4dmap pin --t 2026-09-10T00:00:00Z --src synthetic",
    )
    p_pin.add_argument("--t", default=None, help="Clock value, such as 2026-09-10T00:00:00Z")
    p_pin.add_argument("--axis", default="T", help="T, DELTA, GAMMA, or PI")
    p_pin.add_argument("--src", default="operator", help="Source cite")
    p_pin.add_argument("--note", default="T pin", help="Short note stored on the card")
    p_pin.add_argument("--value", default=None, help="Axis value when it is not a clock time")
    add_cards(p_pin)

    p_span = sub.add_parser(
        "span",
        parents=[json_flags],
        help="Span an interval between two pins",
        description="Span an interval between two cards already in --cards.",
    )
    p_span.add_argument("--from-id", required=True, help="Id of the first card")
    p_span.add_argument("--to-id", required=True, help="Id of the second card")
    add_cards(p_span)

    p_join = sub.add_parser(
        "join",
        parents=[json_flags],
        help="Join two cards with an allowed type",
        description="Join two cards with an allowed type such as T-DELTA or T-PI.",
    )
    p_join.add_argument("--left", required=True, help="Left card id")
    p_join.add_argument("--right", required=True, help="Right card id")
    p_join.add_argument("--type", dest="join_type", required=True, help="Join type, such as T-DELTA")
    add_cards(p_join)

    p_fork = sub.add_parser(
        "fork",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Keep a sibling branch. Both branches stay.",
    )
    p_fork.add_argument("--id", required=True, help="Card id to fork")
    add_cards(p_fork)

    p_walk = sub.add_parser(
        "walk",
        parents=[json_flags],
        help="Walk previous hashes from a tip",
        description="Walk previous hashes from a tip id.",
    )
    p_walk.add_argument("--tip", required=True, help="Tip card id")
    add_cards(p_walk)

    p_lens = sub.add_parser(
        "lens",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Apply a lens. An empty or missed query returns Π-EMPTY.",
    )
    p_lens.add_argument("--query", default="", help="Text to look for")
    add_cards(p_lens)

    p_cap = sub.add_parser(
        "cap",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Apply the ZionPattern cap of 0.75.",
    )
    p_cap.add_argument("--score", type=float, required=True, help="Number to cap")

    p_demo = sub.add_parser(
        "demo",
        parents=[json_flags],
        help="Print the synthetic example",
        description="Print the synthetic example. It is not a real case.",
    )
    p_demo.add_argument("-o", "--output", help="Write the machine JSON to this file")

    p_export = sub.add_parser(
        "export",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Export cards as 4DM-CARD JSON.",
    )
    add_cards(p_export)
    p_import = sub.add_parser(
        "import",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Import 4DM-CARD JSON. Hashes that do not match are refused.",
    )
    p_import.add_argument("--bundle", required=True, help="JSON file to import")
    add_cards(p_import)
    p_frame = sub.add_parser(
        "frame-status",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Show inspection-frame status.",
    )
    add_cards(p_frame)
    p_axis = sub.add_parser(
        "axis-describe",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Describe T, Δ, Γ, and Π.",
    )
    p_axis.add_argument("--axis", default=None, help="One axis, or all when omitted")
    add_cards(p_axis)
    p_trace = sub.add_parser(
        "walk-trace",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Walk a tip and include axis receipts.",
    )
    p_trace.add_argument("--tip", required=True, help="Tip card id")
    add_cards(p_trace)
    p_chain = sub.add_parser(
        "verify-chain",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Verify the previous-hash chain from a tip.",
    )
    p_chain.add_argument("--tip", required=True, help="Tip card id")
    add_cards(p_chain)
    p_vh = sub.add_parser(
        "verify-hash",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Verify one card hash.",
    )
    p_vh.add_argument("--id", default=None, help="Card id")
    add_cards(p_vh)
    p_mc = sub.add_parser(
        "memory-cite",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Cite memory fabric on a card. The card itself stays unchanged.",
    )
    p_mc.add_argument("--id", required=True, help="Card id")
    add_cards(p_mc)
    p_mo = sub.add_parser(
        "memory-observe",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Build a memory observe packet from a card.",
    )
    p_mo.add_argument("--id", required=True, help="Card id")
    add_cards(p_mo)

    p_lib = sub.add_parser(
        "library-pin",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Pin a library event on the lattice.",
    )
    p_lib.add_argument("--event", required=True, help="Event name")
    p_lib.add_argument("--date", required=True, help="Paper date")
    p_lib.add_argument("--lat", default=None, help="Latitude")
    p_lib.add_argument("--lon", default=None, help="Longitude")
    p_lib.add_argument("--gazetteer-id", dest="gazetteer_id", default=None, help="Gazetteer id")
    p_lib.add_argument("--doc-id", dest="doc_id", default=None, help="Document id")
    p_lib.add_argument("--surface", default="MOCK", choices=("REAL", "MOCK"), help="MOCK or REAL")
    p_lib.add_argument("--src", default="aziel-corpus", help="Source cite")
    p_lib.add_argument("--note", default=None, help="Short note")
    add_cards(p_lib)

    p_plot = sub.add_parser(
        "plot",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="List lattice pins and trajectories.",
    )
    add_cards(p_plot)

    p_pos = sub.add_parser(
        "possibility",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Show a labeled possibility on a card. Possibility and Bayesian stay separate.",
    )
    p_pos.add_argument("--id", default=None, help="Card id")
    p_pos.add_argument("--bayesian", type=float, default=None, help="Optional labeled Bayesian value")
    add_cards(p_pos)

    p_pr = sub.add_parser(
        "pattern-recall",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Recall patterns from the hashchain lattice.",
    )
    add_cards(p_pr)

    p_tip = sub.add_parser(
        "lattice-tip",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="List lattice tips.",
    )
    add_cards(p_tip)

    p_poi = sub.add_parser(
        "poison-refuse",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Append a poison feature hash to the refuse set.",
    )
    p_poi.add_argument("--feature-h", dest="feature_h", default=None, help="Feature hash")
    p_poi.add_argument("--event", default=None, help="Event name")
    p_poi.add_argument("--date", default=None, help="Paper date")
    p_poi.add_argument("--lat", default=None, help="Latitude")
    p_poi.add_argument("--lon", default=None, help="Longitude")
    p_poi.add_argument("--gazetteer-id", dest="gazetteer_id", default=None, help="Gazetteer id")
    add_cards(p_poi)

    p_nb = sub.add_parser(
        "neighbor-cite",
        parents=[json_flags],
        help=argparse.SUPPRESS,
        description="Cite the Aziel Digital Library on a card.",
    )
    p_nb.add_argument("--id", required=True, help="Card id")
    add_cards(p_nb)
    return parser


def _refuse_text(err: CardError) -> str:
    return f"{err.message}\nTry: 4dmap --help\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    raw = list(argv) if argv is not None else None
    if raw == []:
        print(_welcome(), end="")
        return 0
    args = parser.parse_args(raw)

    if not args.command:
        if _wants_json(args):
            print(
                json.dumps(
                    {
                        "ok": True,
                        "product": PRODUCT,
                        "version": __version__,
                        "author": AUTHOR,
                        "next": ["4dmap ui", "4dmap doctor", "4dmap --help"],
                    },
                    indent=2,
                )
            )
            return 0
        print(_welcome(), end="")
        return 0

    as_json = _wants_json(args)

    if args.command == "version":
        if as_json:
            print(json.dumps({"product": PRODUCT, "version": __version__, "author": AUTHOR}, indent=2))
        else:
            print(f"{PRODUCT} {__version__}")
            print(f"author {AUTHOR}")
        return 0

    if args.command == "doctor":
        from .doctor import run_doctor

        return run_doctor(as_json=as_json)

    if args.command in ("ui", "server"):
        from .server import serve

        serve(host=getattr(args, "host", LOOPBACK), port=getattr(args, "port", DEFAULT_PORT))
        return 0

    if args.command == "shadow":
        from .shadowlinks import load_shadow_links, shadow_text

        result = load_shadow_links(getattr(args, "links", None))
        output = getattr(args, "output", None)
        if output or as_json:
            if not result.get("ok") and not output:
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return 2
            return _emit(result, output, True, "shadow")
        if not result.get("ok"):
            print(shadow_text(result), file=sys.stderr, end="")
            return 2
        print(shadow_text(result), end="")
        return 0

    try:
        if args.command == "demo":
            from .example import EXAMPLE_CARDS

            result = {"ok": True, "synthetic": True, "cards": EXAMPLE_CARDS, "limitation": LIMITATION}
            if args.output:
                return _emit(result, args.output, True, "demo")
            return _emit(result, None, as_json, "demo")
        if args.command == "cap":
            result = dispatch("cap", {"score": args.score})
            return _emit(result, None, as_json, "cap")
        op_map = {
            "export": "card_export",
            "import": "card_import",
            "frame-status": "frame_status",
            "axis-describe": "axis_describe",
            "walk-trace": "walk_trace",
            "verify-chain": "verify_chain",
            "verify-hash": "verify_hash",
            "memory-cite": "memory_cite",
            "memory-observe": "memory_observe",
            "library-pin": "library_pin",
            "plot": "plot",
            "possibility": "possibility",
            "pattern-recall": "pattern_recall",
            "lattice-tip": "lattice_tip",
            "poison-refuse": "poison_refuse",
            "neighbor-cite": "neighbor_cite",
        }
        op = op_map.get(args.command, args.command)
        cards = _load_cards(getattr(args, "cards", None))
        payload = {k: v for k, v in vars(args).items() if k not in _SKIP_PAYLOAD and v is not None}
        if args.command == "import":
            payload["bundle"] = _load_cards(args.bundle)
            if isinstance(payload["bundle"], list):
                payload = {"cards": payload["bundle"]}
        if args.command == "possibility" and payload.get("bayesian") is not None:
            payload["bayesian"] = {"label": "bayesian", "value": payload["bayesian"], "cite": "cli"}
        result = dispatch(op, payload, cards)
        result["cards_out"] = cards
        if "card" in result:
            cards = cards + [result["card"]]
            result["cards_out"] = cards
        output = getattr(args, "output", None)
        if output:
            return _emit(result, output, True, args.command)
        return _emit(result, None, as_json, args.command)
    except CliUsage as err:
        print(err.message, file=sys.stderr)
        return 2
    except CardError as err:
        if as_json:
            print(json.dumps(err.as_dict(), indent=2))
        else:
            print(_refuse_text(err), file=sys.stderr, end="")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
