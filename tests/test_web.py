from importer.db import connect, save_report, soap_values_from_results
from importer.robot_output import parse_robot_output
from web.app import create_app


def test_save_and_dashboard(tmp_path, monkeypatch):
    db_path = tmp_path / "demo.sqlite"
    monkeypatch.setenv("RESET_TIME_DB_BACKEND", "sqlite")
    monkeypatch.setenv("RESET_TIME_SQLITE_PATH", str(db_path))
    db = connect()
    save_report(db, parse_robot_output("samples/robot_output.xml"))
    db.close()

    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Reset time" in body
    assert "RFSW-SAMPLE-1.0" in body
    assert "total_reset_time" in body


def test_demo_seed_when_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("RESET_TIME_DB_BACKEND", "sqlite")
    monkeypatch.setenv("RESET_TIME_SQLITE_PATH", str(tmp_path / "empty.sqlite"))
    app = create_app()
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert "RFSW-SAMPLE-1.0" in response.get_data(as_text=True)


def test_soap_values_map_labels_to_columns():
    values = soap_values_from_results(
        [{"PTP sync time between RU and DU": 22}, {"Radio data path sync time": 32}]
    )
    assert values["ptp_sync"] == 22
    assert values["path_sync"] == 32
    assert values["tx_setup"] is None


def test_safe_column_rejects_injection():
    from importer.db import safe_column
    import pytest

    with pytest.raises(ValueError):
        safe_column("ptp;drop table")
