from fourdmap.cli import main


def test_version(capsys) -> None:
    assert main(["version"]) == 0
    out = capsys.readouterr().out
    assert "4dmap 0.3.0" in out
    assert "Aziel Eliab" in out


def test_demo(tmp_path) -> None:
    dest = tmp_path / "out.json"
    assert main(["demo", "-o", str(dest)]) == 0
    assert dest.exists()
    assert "4dm-example-pin" in dest.read_text(encoding="utf-8")
