"""4DMap product constants. Author: Aziel Eliab only."""

from __future__ import annotations

__version__ = "0.3.0"
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
TARBALL = "4dmap-0.3.0.tar.gz"
PIN_FRAME_KIND = "4DM-PIN-FRAME"
GROWTH = "ON"

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

# Aziel Digital Library is a Research-domain sibling. Cite / pin-frame pairing only.
# Not a 4DMap companion lock. Not a second door. Not GIS.
LIBRARY = {
    "software": "Aziel Digital Library",
    "slug": "aziel-corpus",
    "role": "inspection_input",
    "cite_only": True,
    "door": False,
    "merged": False,
    "map": "https://www.azielcorpuslibrary.net/map",
    "verify_geo": "https://www.azielcorpuslibrary.net/v1/verify-geo",
    "note": (
        "Library Temporal Map pins are paper date × event × geolocation. "
        "Never upload time. Docs without resolvable place+date stay unpinned. "
        "4DMap accepts/emits 4DM-PIN-FRAME receipts on the hashchain lattice."
    ),
    "author": AUTHOR,
}

DISCOVERY = {
    "growth": GROWTH,
    "skill": True,
    "openapi": True,
    "mcp": True,
    "worker_ui": True,
    "reason": "library pin + lattice memory LIVE_OPS",
}

AXIS_FRAME = {
    "T": {
        "glyph": "T",
        "name": "Clock",
        "meaning": "time / when a pin sits",
        "companions": ("temporallock", "staticclock", "chronolock"),
        "ops": ("pin", "card_pin", "library_pin", "span", "card_span", "walk", "walk_trace", "plot"),
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
        "ops": ("stack", "walk", "walk_trace", "pin", "card_pin", "plot"),
    },
    "PI": {
        "glyph": "Π",
        "name": "Pattern",
        "meaning": "provenance / path / class / cohort / absence / silence",
        "companions": ("spectrallock",),
        "ops": ("lens", "class", "cohort", "absence", "pin", "card_pin", "pattern_recall", "poison_refuse", "possibility"),
    },
}

# AKM-TRIAD-1.0 is LIVE fabric on aziel-runtime — not a Softwares-tab product,
# not a 4DMap companion slug, not a second door. Optional card cite/observe only.
AKM = {
    "spec": "AKM-TRIAD-1.0",
    "name": "Adaptive Knowledge Memory",
    "fabric": True,
    "software_tab": False,
    "door": False,
    "slug": None,
    "softwares_product": False,
    "pairing": "optional cite/observe",
    "posterior_is_truth": False,
    "belief_is_not_truth": True,
    "authorizes_action": False,
    "history_rewrite": False,
    "triad": ("E", "C", "P", "B"),
    "triad_rule": "3-of-4",
    "mcp": ("memory_observe", "memory_resolve", "memory_calibrate", "memory_recall", "memory_get"),
    "http": (
        "POST /v1/memory/observe",
        "POST /v1/memory/resolve",
        "POST /v1/memory/calibrate",
        "POST /v1/memory/recall",
    ),
    "learn": "ChainLock learn",
    "note": (
        "LIVE fabric on aziel-runtime. Not a Softwares-tab product. Behind FragGate. "
        "Optional 4DMap inspection-card cite/observe only. Bayesian 3-of-4 triad E/C/P/B. "
        "Posterior ≠ truth. No history rewrite. Author: Aziel Eliab only."
    ),
    "author": AUTHOR,
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

OP_ALIASES = {
    "card_pin": "pin",
    "card_span": "span",
    "card_join": "join",
    "card_walk": "walk",
    "card_list": "list",
    "ingest_pin": "library_pin",
    "plot_pins": "plot",
    "score_hooks": "possibility",
    "possibility_cite": "possibility",
    "lattice_tips": "lattice_tip",
    "neighbor": "neighbor_cite",
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
    "akm": ("AKM_SOFTWARE", "AKM-TRIAD-1.0 is LIVE fabric, not a Softwares-tab slug"),
    "akm_triad": ("AKM_SOFTWARE", "AKM-TRIAD-1.0 is LIVE fabric, not a Softwares-tab slug"),
    "memory_rewrite": ("AKM_REWRITE", "AKM-TRIAD-1.0 does not rewrite history"),
    "posterior_truth": ("AKM_TRUTH", "posterior ≠ truth; 4DMap receipts are not truth"),
    "ml_store": ("LATTICE_ONLY", "adaptive pattern memory is the hashchain lattice, not a detached ML store"),
    "detach_memory": ("LATTICE_ONLY", "recollection stays on tips/prev-hash/pin receipts"),
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
        "aziel-corpus",
        "library",
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
  → Internal Domain Layer (isolated softwares; domains_are_doors:false)  ←──  4DMap
       inspection cards sit HERE as a read-side coordinate frame over
       TemporalLock/StaticClock/ChronoLock/TrajectoryLock/SpectralLock evidence
       (not a hop gate; not a door)
  → TemporalLock → StaticClock → ChainLock-OUT → RESPONSE/RECEIPT"""

PIPELINE_NOTE = (
    "4DMap is not inserted as another sequential gate. It is an inspection "
    "frame in the Internal Domain Layer after AZPIPE (domains_are_doors:false): "
    "engines and operator UI write/read 4DM cards; FragGate grounded claims may "
    "cite join types; ChainLock may stamp a walk when the operator seals. "
    "QNS/QNM do not carry 4DMap photons. FragGate is THE single door."
)
