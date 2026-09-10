"""No legal name / home / county. Aziel Eliab only."""

from __future__ import annotations

from pathlib import Path

from fourdmap.card import CardError, make_card
from fourdmap.scope import AUTHOR, LIMITATION

ROOT = Path(__file__).resolve().parents[1]


def test_author_is_aziel_eliab() -> None:
    assert AUTHOR == "Aziel Eliab"
    assert "GodLock.AZ" not in LIMITATION


def test_county_on_card_refuses() -> None:
    try:
        make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="lived in Example County")
        raise AssertionError("expected IDENTITY_LEAK")
    except CardError as err:
        assert err.code == "IDENTITY_LEAK"


def test_forbidden_key_refuses() -> None:
    try:
        make_card(t="2026-09-10T00:00:00Z", src="synthetic", note="n", pi={"county": "x"})
        raise AssertionError("expected IDENTITY_LEAK")
    except CardError as err:
        assert err.code == "IDENTITY_LEAK"


def test_repo_identity_files() -> None:
    for rel in ("README.md", "SKILL.md", "AGENTS.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "Aziel Eliab" in text
        assert "GodLock.AZ" not in text
