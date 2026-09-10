"""4DMap product constants. Author: Aziel Eliab only."""

from __future__ import annotations

__version__ = "0.1.0"
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

AXES = ("T", "DELTA", "GAMMA", "PI")
AXIS_GLYPH = {"T": "T", "DELTA": "Δ", "GAMMA": "Γ", "PI": "Π"}

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
