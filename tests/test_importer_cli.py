from importer.cli import main


def test_import_cli(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("RESET_TIME_DB_BACKEND", "sqlite")
    monkeypatch.setenv("RESET_TIME_SQLITE_PATH", str(tmp_path / "import.sqlite"))
    assert main(["samples/robot_output.xml"]) == 0
    out = capsys.readouterr().out
    assert "SAMPLE_RU" in out
    assert main([str(tmp_path / "missing.xml")]) == 1
