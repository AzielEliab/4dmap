"""MASTER-33: 4DMap is an inspection frame after AZPIPE, not a door."""

from __future__ import annotations

from pathlib import Path

from fourdmap.ops import dispatch
from fourdmap.scope import AUTHOR, LIVE_OPS, MASTER33, PIPELINE, PIPELINE_NOTE

ROOT = Path(__file__).resolve().parents[1]


def test_master33_inspection_not_door() -> None:
    assert MASTER33["master"] == "MASTER-33"
    assert MASTER33["door"] == "fraggate"
    assert MASTER33["fraggate_single_door"] is True
    assert MASTER33["domains_are_doors"] is False
    assert MASTER33["sequential_gate"] is False
    assert MASTER33["software_door"] is False
    assert MASTER33["fabric"] is False
    assert MASTER33["role"] == "inspection"
    assert MASTER33["after"] == "AZPIPE"
    assert MASTER33["layer"] == "Internal Domain Layer"
    assert MASTER33["domain"] == "Research"
    assert AUTHOR == "Aziel Eliab"


def test_frame_status_matches_master33() -> None:
    status = dispatch("frame_status", {})
    assert status["ok"] is True
    assert status["domains_are_doors"] is False
    assert status["sequential_gate"] is False
    assert status["software_door"] is False
    assert status["door"] == "fraggate"
    assert status["role"] == "inspection"
    assert status["mesh"]["default_off"] is True
    assert status["mesh"]["get_enables"] is False
    assert status["mesh"]["node_gate"] is False
    assert "card_export" in status["live_ops"]
    assert "wipe" in status["refuse_ops"]
    slugs = {c["slug"] for c in status["companions"]}
    assert slugs == {"temporallock", "staticclock", "chronolock", "trajectorylock", "spectrallock"}
    assert "akm" not in slugs
    assert status["akm"]["software_tab"] is False
    assert status["akm"]["door"] is False
    assert "memory_cite" in status["live_ops"]
    assert all(c["cite_only"] and c["door"] is False and c["merged"] is False for c in status["companions"])


def test_axis_describe_cites_companions() -> None:
    all_axes = dispatch("axis_describe", {})
    assert set(all_axes["axes"]) == {"T", "DELTA", "GAMMA", "PI"}
    assert all_axes["domains_are_doors"] is False
    t = dispatch("axis_describe", {"axis": "T"})
    slugs = {c["slug"] for c in t["axes"]["T"]["companions"]}
    assert slugs == {"temporallock", "staticclock", "chronolock"}
    gamma = dispatch("axis_describe", {"axis": "Γ"})
    assert gamma["axes"]["GAMMA"]["companions"][0]["software"] == "TrajectoryLock"


def test_pipeline_copy_not_hop_gate() -> None:
    assert "not a hop gate" in PIPELINE.lower() or "not a hop gate" in PIPELINE_NOTE.lower()
    assert "AZPIPE" in PIPELINE
    assert "FragGate" in PIPELINE or "FragGate" in PIPELINE_NOTE


def test_repo_docs_keep_inspection_framing() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    paper = (ROOT / "docs/4DM-WP-1.0.md").read_text(encoding="utf-8")
    home = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
    engine = (ROOT / "workers/download-tracker/src/engine.js").read_text(encoding="utf-8")
    for blob in (readme, skill, paper, home, engine):
        assert "Aziel Eliab" in blob
        assert "GodLock.AZ" not in blob
        assert "domains_are_doors" in blob or "not a hop gate" in blob.lower() or "not an extra door" in blob.lower() or "not a Softwares door" in blob
    assert "0.2.0" in readme
    assert "card_export" in LIVE_OPS
    assert 'VERSION = "0.2.0"' in engine
    assert "4dmap-0.2.0.tar.gz" in home
    assert "GET never enables" in readme
