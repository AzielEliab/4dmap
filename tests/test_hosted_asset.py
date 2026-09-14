"""DEFAULT_ASSET 4dmap-0.3.0.tar.gz must be hosted in Worker public/.

Catalog/runtime expect product 0.3.0. Serving a missing ASSETS file is
HTTP 404 {error: asset not hosted}. Mesh remain-OFF. Dual-surface stays.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "workers/download-tracker/public"
ASSET_NAME = "4dmap-0.3.0.tar.gz"
ASSET = PUBLIC / ASSET_NAME


def test_default_asset_citations() -> None:
    home = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
    engine = (ROOT / "workers/download-tracker/src/engine.js").read_text(encoding="utf-8")
    install = (ROOT / "install.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    scope = (ROOT / "fourdmap/scope.py").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'DEFAULT_ASSET = "4dmap-0.3.0.tar.gz"' in home
    assert 'VERSION = "0.3.0"' in engine
    assert 'TARBALL = "4dmap-0.3.0.tar.gz"' in engine
    assert 'ASSET="${FOURDMAP_ASSET:-4dmap-0.3.0.tar.gz}"' in install
    assert "4dmap-0.3.0.tar.gz" in readme
    assert "download?asset=4dmap-0.3.0.tar.gz" in readme
    assert '__version__ = "0.3.0"' in scope
    assert 'TARBALL = "4dmap-0.3.0.tar.gz"' in scope
    assert "asset=4dmap-0.3.0.tar.gz" in pyproject
    assert "Aziel Eliab" in home
    assert "GodLock.AZ" not in home


def test_public_hosts_default_tarball() -> None:
    assert ASSET.is_file(), f"missing hosted asset {ASSET} — run tools/pack_counted_tarball.sh"
    assert ASSET.stat().st_size > 10_000
    with tarfile.open(ASSET, "r:gz") as tf:
        names = tf.getnames()
    assert "4dmap-0.3.0/pyproject.toml" in names
    assert "4dmap-0.3.0/fourdmap/scope.py" in names
    assert "4dmap-0.3.0/install.sh" in names
    assert "4dmap-0.3.0/workers/download-tracker/src/home.js" in names
    assert "4dmap-0.3.0/README.md" in names
    nested = [n for n in names if n.endswith(".tar.gz")]
    assert nested == [], nested
    assert all(n == "4dmap-0.3.0" or n.startswith("4dmap-0.3.0/") for n in names)
