"""Full AI client list stays in README + SKILL."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = (
    "ChatGPT",
    "Grok",
    "Venice",
    "Claude",
    "Cursor",
    "Glama",
    "Perplexity",
    "Copilot",
    "Gemini",
    "Mistral",
    "Meta",
    "Apple",
    "Amazon Q",
    "DuckAssist",
    "You.com",
    "Cohere",
)


def test_readme_and_skill_list_clients() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for name in CLIENTS:
        assert name in readme, name
        assert name in skill, name
