from soap_parser.cli import main


def test_cli_sample(tmp_path, capsys):
    from soap_parser.sample_log import build_sample_soap_log

    path = tmp_path / "soap_log.xml"
    path.write_text(build_sample_soap_log(), encoding="utf-8")
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "cost=22 s" in out
    assert "cost=5 s" in out


def test_cli_json(tmp_path, capsys):
    from soap_parser.sample_log import build_sample_soap_log

    path = tmp_path / "soap_log.xml"
    path.write_text(build_sample_soap_log(), encoding="utf-8")
    assert main([str(path), "--json"]) == 0
    assert '"seconds": 22' in capsys.readouterr().out
