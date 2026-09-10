"""Suite mesh Live Nodes + QNM-BUILD-1.0 + QNS-CD-1.0 cross-map.

Default OFF. GET never enables. live|locked|isolated. No Node Gate.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = (ROOT / "workers/download-tracker/src/mesh.js").read_text(encoding="utf-8")
RUNTIME = (ROOT / "workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
HOME = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
WRANGLER = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")


def test_mesh_contract_default_off_qnm_law() -> None:
    assert 'QNM_SPEC = "QNM-BUILD-1.0"' in MESH
    assert "MESH_DEFAULT_OFF = true" in MESH
    assert "MESH_ANONYMITY_NETWORK = false" in MESH
    assert "MESH_NODE_GATE = false" in MESH
    assert "MESH_AUTO_HEAL = false" in MESH
    assert 'MESH_PRODUCT = "4dmap"' in MESH
    assert 'MESH_PATH = "/v1/mesh"' in MESH
    assert "live|locked|isolated" in MESH
    assert "enabled_default: false" in MESH
    assert "Aziel Eliab" in MESH
    assert 'QNS_CD_SPEC = "QNS-CD-1.0"' in MESH
    assert "GET never enables" in MESH
    assert "/v1/qnsd" not in MESH


def test_wrangler_ready() -> None:
    assert 'name = "4dmap-download-tracker"' in WRANGLER
    assert "AZIEL_RUNTIME" in WRANGLER
    assert "4DMAP_DOWNLOADS" in WRANGLER
    assert 'binding = "DOWNLOADS"' in WRANGLER
    assert 'id = "e962292069794bcc8cb89e3f559cfa43"' in WRANGLER
    assert "/v1/mesh" in WRANGLER


def test_index_routes_mesh_before_runtime() -> None:
    assert "handleMeshApi" in INDEX
    assert INDEX.find("handleMeshApi") < INDEX.find("handleRuntimeApi")
    assert "GET /v1/mesh never enables" in INDEX


def test_homepage_board_and_pipeline() -> None:
    assert "Four-axis board" in HOME
    assert "T Clock" in HOME
    assert "Δ Interval" in HOME
    assert "Γ Trajectory" in HOME
    assert "Π Pattern" in HOME
    assert "Domain Doors" in HOME
    assert "not a hop gate" in HOME
    assert "GET never enables" in HOME
    assert "Plain" in HOME
    assert "Everblooming sigil" in HOME


def test_readme_cites_worker_download() -> None:
    assert "4dmap-download-tracker.vibelock.workers.dev/download" in README
    assert "4dmap-download-tracker.vibelock.workers.dev/" in README
    assert "GET never enables" in README
    assert "4DM-WP-1.0" in README
    assert "Plain" in README


def test_skill_dual_surface() -> None:
    assert "slug=4dmap" in SKILL
    assert "FragGate is LIVE" in SKILL
    assert "FragGate is LIVE" in README
    assert "FG-HALLUC-TOOL" not in SKILL
    assert "FG-HALLUC-TOOL" not in README
    assert "GET never enables" in SKILL
    assert "Π-EMPTY" in SKILL or "PI-EMPTY" in SKILL or "Π-EMPTY" in RUNTIME
