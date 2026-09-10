"""4DMap product constants. Author: Aziel Eliab only."""

from __future__ import annotations

__version__ = "0.2.0"
SPEC = "4DM-WP-1.0"
SCHEMA = "4DM-CARD"
PRODUCT = "4dmap"
PRODUCT_NAME = "4DMap"
AUTHOR = "Aziel Eliab"
BUCKET = "Plain"
HOST = "https://4dmap-download-tracker.vibelock.workers.dev"
GITHUB = "https://github.com/AzielEliab/4dmap"
CATALOG = "https://aziel-runtime.vibelock.workers.dev"
DEFAULT_PORT = 8844
LOOPBACK = "127.0.0.1"
ZION_CAP = 0.75
PI_EMPTY = "Π-EMPTY"
GENESIS_PREV = "0" * 64
TARBALL = "4dmap-0.2.0.tar.gz"

AXES = ("T", "DELTA", "GAMMA", "PI")
AXIS_GLYPH = {"T": "T", "DELTA": "Δ", "GAMMA": "Γ", "PI": "Π"}

# Companion softwares are inspection inputs only. Cite / functional pairing.
# Do not merge products. Do not invent a second door.
COMPANIONS = {
    "temporallock": {
        "software": "TemporalLock",
        "slug": "temporallock",
        "axes": ("T", "DELTA"),
        "role": "inspection_input",
        "cite_only": True,
        "door": False,
        "merged": False,
    },
    "staticclock": {
        "software": "StaticClock",
        "slug": "staticclock",
        "axes": ("T",),
        "role": "inspection_input",
        "cite_only": True,
        "door": False,
        "merged": False,
    },
    "chronolock": {
        "software": "ChronoLock",
        "slug": "chronolock",
        "axes": ("T", "DELTA"),
        "role": "inspection_input",
        "cite_only": True,
        "door": False,
        "merged": False,
    },
    "trajectorylock": {
        "software": "TrajectoryLock",
        "slug": "trajectorylock",
        "axes": ("GAMMA",),
        "role": "inspection_input",
        "cite_only": True,
        "door": False,
        "merged": False,
    },
    "spectrallock": {
        "software": "SpectralLock",
        "slug": "spectrallock",
        "axes": ("PI",),
        "role": "inspection_input",
        "cite_only": True,
        "door": False,
        "merged": False,
    },
}

AXIS_FRAME = {
    "T": {
        "glyph": "T",
        "name": "Clock",
        "meaning": "time / when a pin sits",
        "companions": ("temporallock", "staticclock", "chronolock"),
        "ops": ("pin", "card_pin", "span", "card_span", "walk", "walk_trace"),
    },
    "DELTA": {
        "glyph": "Δ",
        "name": "Interval",
        "meaning": "delta / change / span or gap between pins",
        "companions": ("temporallock", "chronolock"),
        "ops": ("span", "card_span", "gap", "walk", "walk_trace"),
    },
    "GAMMA": {
        "glyph": "Γ",
        "name": "Trajectory",
        "meaning": "pattern / geometry / stacked or walked motion of pins",
        "companions": ("trajectorylock",),
        "ops": ("stack", "walk", "walk_trace", "pin", "card_pin"),
    },
    "PI": {
        "glyph": "Π",
        "name": "Pattern",
        "meaning": "provenance / path / class / cohort / absence / silence",
        "companions": ("spectrallock",),
        "ops": ("lens", "class", "cohort", "absence", "pin", "card_pin"),
    },
}

# MASTER-33: 4DMap is an inspection frame after AZPIPE, not an extra door.
MASTER33 = {
    "master": "MASTER-33",
    "door": "fraggate",
    "fraggate_single_door": True,
    "domains_are_doors": False,
    "sequential_gate": False,
    "role": "inspection",
    "layer": "Internal Domain Layer",
    "after": "AZPIPE",
    "software_door": False,
    "fabric": False,
    "software_tab": True,
    "domain": "Research",
    "domain_id": "06",
    "note": (
        "4DMap is a Research-domain inspection frame T/Δ/Γ/Π inside Internal "
        "Domain Layer after AZPIPE. Isolated software, not an additional door. "
        "Not a sequential gate. Not LIVE fabric. FragGate is THE single door."
    ),
}

LIVE_OPS = (
    "health",
    "skill",
    "pin",
    "span",
    "stack",
    "gap",
    "fork",
    "walk",
    "lens",
    "class",
    "cohort",
    "absence",
    "cap",
    "join",
    "list",
    "example",
    "card_new",
    "card_pin",
    "card_span",
    "card_join",
    "card_walk",
    "card_list",
    "verify_hash",
    "card_export",
    "card_import",
    "frame_status",
    "axis_describe",
    "walk_trace",
    "verify_chain",
)

OP_ALIASES = {
    "card_pin": "pin",
    "card_span": "span",
    "card_join": "join",
    "card_walk": "walk",
    "card_list": "list",
}

REFUSE_OPS = {
    "truth_score": ("STUB_REFUSE", "truth_score is stub — 4DMap is not a truth engine"),
    "lumen_panel": ("STUB_REFUSE", "lumen_panel is stub — 4DMap is not Lumen"),
    "invent_mark": ("STUB_REFUSE", "invent_mark is stub — 4DMap does not invent marks"),
    "backdate_class": ("STUB_REFUSE", "backdate_class is stub — Π cannot rewrite T"),
    "wipe": ("FANTASY_OP", "destructive wipe is refused"),
    "purge": ("FANTASY_OP", "destructive purge is refused"),
    "delete_all": ("FANTASY_OP", "destructive delete_all is refused"),
    "merge_products": ("FANTASY_OP", "companion softwares are cite-only; products are not merged"),
    "enable_door": ("FANTASY_OP", "4DMap is not a Softwares door; FragGate remains THE single door"),
}

ALLOWED_JOINS = frozenset(
    {
        ("T", "DELTA"),
        ("DELTA", "T"),
        ("DELTA", "GAMMA"),
        ("GAMMA", "DELTA"),
        ("GAMMA", "PI"),
        ("PI", "GAMMA"),
        ("T", "PI"),
    }
)

# Π→T is the backdate direction. Inspection T↔Π is T-PI only.
ILLEGAL_JOINS = frozenset({("PI", "T")})

ALLOWED_SRC = frozenset(
    {
        "temporallock",
        "staticclock",
        "chronolock",
        "trajectorylock",
        "spectrallock",
        "operator",
        "4dmap",
        "synthetic",
    }
)

LIMITATION = (
    "THIS IS: an inspection coordinate frame (4DM-WP-1.0) over TemporalLock / "
    "StaticClock / ChronoLock / TrajectoryLock / SpectralLock evidence. Cards "
    "are 4DM-CARD receipts with fail-closed SHA-256. Forks are kept. ZionPattern "
    "confidence is capped at 75%. A silent lens returns Π-EMPTY. "
    "THIS IS NOT: a truth engine; Lumen; GIS 4D; a Node Gate; certified forensics; "
    "an identity store. Receipts are not truth. No legal name, home, or county "
    "on cards. QNS/QNM do not carry 4DMap photons. Author: Aziel Eliab only."
)

GUARDRAIL = (
    "4DMap stamps inspection coordinates. It does not certify facts, solve cases, "
    "name people, infer intent, or backdate a clock from a pattern. "
    "P(pattern | cards) is capped at 0.75 and is not P(the world is true). "
    "Synthetic examples must never be presented as real-case findings."
)

PIPELINE = """PUBLIC/AGENTS/UI → FragGate → SweepGate → ChainLock-IN → DecisionGATE → AZPIPE
  → Domain Doors (isolated engines)  ←──  4DMap inspection cards sit HERE as
       a read-side coordinate frame over TemporalLock/StaticClock/ChronoLock/
       TrajectoryLock/SpectralLock evidence (not a hop gate)
  → TemporalLock → StaticClock → ChainLock-OUT → RESPONSE/RECEIPT"""

PIPELINE_NOTE = (
    "4DMap is not inserted as another sequential gate. It is a domain-door / "
    "inspection frame: engines and operator UI write/read 4DM cards; FragGate "
    "grounded claims may cite join types; ChainLock may stamp a walk when the "
    "operator seals. QNS/QNM do not carry 4DMap photons."
)
