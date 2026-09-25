"""One hash-chained lattice file for the local UI and the CLI.

The file is ``~/.4dmap/lattice.json`` unless ``FOURDMAP_LATTICE`` is set.
``dispatch`` stays a pure function. The UI server and the CLI load this
file, call the existing ops, and write the same cards back.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .card import CardError

ENV_PATH = "FOURDMAP_LATTICE"
FORMAT = "4dmap-lattice-1"


def lattice_path() -> Path:
    override = os.environ.get(ENV_PATH)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".4dmap" / "lattice.json"


def load_cards() -> list[dict[str, Any]]:
    path = lattice_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CardError("LATTICE_JSON", f"{path} is not JSON. The lattice file was not rewritten.") from exc
    if isinstance(data, list):
        cards = data
    elif isinstance(data, dict) and isinstance(data.get("cards"), list):
        cards = data["cards"]
    else:
        raise CardError("LATTICE_JSON", f"{path} is not a card list.")
    if any(not isinstance(card, dict) for card in cards):
        raise CardError("LATTICE_JSON", f"{path} has a card that is not an object.")
    return cards


def save_cards(cards: list[dict[str, Any]]) -> Path:
    path = lattice_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {"format": FORMAT, "cards": cards}
    path.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
