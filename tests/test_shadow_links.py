"""ShadowLock link file on the local 4DMap workbench."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.request import urlopen

from fourdmap.cli import main
from fourdmap.server import make_server
from fourdmap.shadowlinks import FORMAT, load_shadow_links

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = {
    "format": FORMAT,
    "links": [
        {
            "slug": "peacelock",
            "kind": "lock",
            "input_id": "hold/sample",
            "input_path": "samples/hold.json",
            "linked_at": "2026-09-24T16:30:00Z",
            "label": "Hold review",
        },
        {
            "slug": "azmail",
            "kind": "plain",
            "input_id": "inbox/sample",
            "linked_at": "2026-09-24T14:00:00Z",
            "label": "Morning intake",
        },
        {"slug": "", "input_id": "skip-me"},
    ],
}


def test_missing_file_is_empty(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("SHADOWLOCK_LINKS", raising=False)
    missing = tmp_path / "links.json"
    result = load_shadow_links(str(missing))
    assert result["ok"] is True
    assert result["found"] is False
    assert result["n"] == 0
    assert result["links"] == []
    assert result["format"] == FORMAT


def test_links_sort_and_skip(tmp_path) -> None:
    path = tmp_path / "links.json"
    path.write_text(json.dumps(SAMPLE), encoding="utf-8")
    result = load_shadow_links(str(path))
    assert result["ok"] is True
    assert result["found"] is True
    assert result["n"] == 2
    assert result["skipped"] == 1
    assert [item["slug"] for item in result["links"]] == ["azmail", "peacelock"]
    assert result["links"][0]["label"] == "Morning intake"
    assert result["links"][0]["kind"] == "plain"
    assert result["links"][1]["input_path"] == "samples/hold.json"


def test_kind_is_not_invented(tmp_path) -> None:
    path = tmp_path / "links.json"
    path.write_text(
        json.dumps({"links": [{"slug": "azmail", "input_id": "inbox/sample"}]}),
        encoding="utf-8",
    )
    link = load_shadow_links(str(path))["links"][0]
    assert link == {"slug": "azmail", "input_id": "inbox/sample"}


def test_bad_json(tmp_path) -> None:
    path = tmp_path / "links.json"
    path.write_text("{", encoding="utf-8")
    result = load_shadow_links(str(path))
    assert result["ok"] is False
    assert result["code"] == "LINKS_JSON"


def test_wrong_format(tmp_path) -> None:
    path = tmp_path / "links.json"
    path.write_text(json.dumps({"format": "other", "links": []}), encoding="utf-8")
    result = load_shadow_links(str(path))
    assert result["code"] == "LINKS_FORMAT"


def test_cli_empty(capsys, tmp_path) -> None:
    assert main(["shadow", "--links", str(tmp_path / "missing.json")]) == 0
    out = capsys.readouterr().out
    assert "No ShadowLock links yet." in out
    assert "Next:" in out


def test_cli_human_and_json(capsys, tmp_path) -> None:
    path = tmp_path / "links.json"
    path.write_text(json.dumps(SAMPLE), encoding="utf-8")
    assert main(["shadow", "--links", str(path)]) == 0
    human = capsys.readouterr().out
    assert "azmail" in human
    assert "Morning intake" in human
    assert "inbox/sample" in human
    assert human.index("azmail") < human.index("peacelock")
    assert not human.lstrip().startswith("{")

    assert main(["shadow", "--json", "--links", str(path)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["op"] == "shadow_links"
    assert data["n"] == 2
    assert data["links"][0]["slug"] == "azmail"


def test_cli_bad_json(capsys, tmp_path) -> None:
    path = tmp_path / "links.json"
    path.write_text("nope", encoding="utf-8")
    assert main(["shadow", "--links", str(path)]) == 2
    err = capsys.readouterr().err
    assert "not JSON" in err
    assert "Traceback" not in err


def test_page_has_shadow_layer() -> None:
    html = (ROOT / "fourdmap" / "static" / "index.html").read_text(encoding="utf-8")
    assert "Softwares · Shadow" in html
    assert "No ShadowLock links yet." in html
    assert "/v1/shadow_links" in html
    assert 'id="pin-form"' in html
    assert html.find('id="shadow"') < html.find('id="advanced"')


def test_readme_documents_path() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    doc = (ROOT / "docs" / "SHADOWLOCK-LINKS.md").read_text(encoding="utf-8")
    assert "~/.shadowlock/links.json" in readme
    assert FORMAT in doc
    assert "slug" in doc
    assert "linked_at" in doc


def test_local_get_reads_env(tmp_path, monkeypatch) -> None:
    path = tmp_path / "links.json"
    path.write_text(json.dumps(SAMPLE), encoding="utf-8")
    monkeypatch.setenv("SHADOWLOCK_LINKS", str(path))
    httpd = make_server(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    try:
        with urlopen(f"http://127.0.0.1:{port}/v1/shadow_links") as response:
            body = json.loads(response.read().decode("utf-8"))
        assert body["n"] == 2
        assert body["links"][1]["slug"] == "peacelock"
        with urlopen(f"http://127.0.0.1:{port}/v1/health") as response:
            health = json.loads(response.read().decode("utf-8"))
        assert health["ok"] is True
        assert health["product"] == "4dmap"
        assert "shadow_links" not in health["ops"]
    finally:
        httpd.shutdown()
        thread.join(timeout=2)


def test_env_path(tmp_path, monkeypatch) -> None:
    path = tmp_path / "from-env.json"
    path.write_text(json.dumps({"links": [{"slug": "aznet", "input_path": "pair.json"}]}), encoding="utf-8")
    monkeypatch.setenv("SHADOWLOCK_LINKS", str(path))
    result = load_shadow_links()
    assert result["links"][0]["slug"] == "aznet"
    assert result["links"][0]["input_path"] == "pair.json"
