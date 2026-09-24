import json
from pathlib import Path

import pytest

from fourdmap.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_version(capsys) -> None:
    assert main(["version"]) == 0
    out = capsys.readouterr().out
    assert "4dmap 0.3.0" in out
    assert "Aziel Eliab" in out


def test_version_json(capsys) -> None:
    assert main(["version", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["product"] == "4dmap"
    assert data["version"] == "0.3.0"
    assert data["author"] == "Aziel Eliab"


def test_demo(tmp_path) -> None:
    dest = tmp_path / "out.json"
    assert main(["demo", "-o", str(dest)]) == 0
    assert dest.exists()
    text = dest.read_text(encoding="utf-8")
    assert "4dm-example-pin" in text
    assert "limitation" in text


def test_help_does_not_crash(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0
    out = capsys.readouterr().out
    assert "Traceback" not in out
    assert "Common commands" in out
    assert "4dmap ui" in out
    assert "Advanced commands" in out
    assert "Aziel Eliab" in out
    assert "THIS IS NOT" not in out


def test_short_help_flag(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["-h"])
    assert caught.value.code == 0
    assert "Traceback" not in capsys.readouterr().out


def test_cap_help_percent(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["cap", "--help"])
    assert caught.value.code == 0
    assert "Traceback" not in capsys.readouterr().out


def test_bare_welcome(capsys) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "4dmap ui" in out
    assert "4dmap doctor" in out
    assert "Aziel Eliab" in out
    assert "the following arguments are required" not in out


def test_unknown_command(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["bogus"])
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "4dmap --help" in err
    assert "Traceback" not in err


def test_missing_span_ids(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["span"])
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert "Missing" in err
    assert "4dmap span --help" in err
    assert "Traceback" not in err


def test_missing_card_file(capsys) -> None:
    assert main(["pin", "--cards", "no-such-cards.json"]) == 2
    err = capsys.readouterr().err
    assert "No card file" in err
    assert "Traceback" not in err


def test_pin_human_and_json(capsys) -> None:
    assert main(["pin", "--t", "2026-09-10T00:00:00Z", "--src", "synthetic"]) == 0
    human = capsys.readouterr().out
    assert "Pinned a card" in human
    assert not human.lstrip().startswith("{")
    assert "Next: 4dmap ui" in human

    assert main(["--json", "pin", "--t", "2026-09-10T00:00:00Z", "--src", "synthetic"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert data["op"] == "pin"
    assert "cards_out" in data
    assert data["card"]["src"] == "synthetic"
    assert "as_json" not in data["card"]


def test_pin_command_json_flag(capsys) -> None:
    assert main(["pin", "--json", "--t", "2026-09-10T00:00:00Z", "--src", "operator"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert data["cards_out"][0]["src"] == "operator" or data["card"]["src"] == "operator"


def test_doctor_human(capsys) -> None:
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "[ok] version" in out
    assert "All checks passed." in out
    assert "THIS IS NOT" not in out


def test_doctor_json_keeps_machine_shape(capsys) -> None:
    assert main(["doctor", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert isinstance(data["checks"], list)
    assert "limitation" in data


def test_bad_score(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["cap", "--score", "nope"])
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert "Traceback" not in err
    assert "--help" in err


def test_local_page_is_a_workbench() -> None:
    html = (ROOT / "fourdmap" / "static" / "index.html").read_text(encoding="utf-8")
    assert "prefers-color-scheme" in html
    assert ":focus-visible" in html
    assert "#c9a227" in html
    assert 'name="viewport"' in html
    assert 'id="pin-form"' in html
    assert 'id="advanced"' in html
    assert 'id="notes"' in html
    assert 'class="banner"' not in html
    assert "max-width: 520px" in html
    notes_at = html.find('id="notes"')
    assert notes_at != -1
    assert html.find("Not Lumen") == -1 or html.find("not a truth engine") > notes_at
    assert "value || \"{}\"" not in html
    assert "Paste a card bundle" in html
