"""Flask dashboard for aggregated RU reset / SOAP timings."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, render_template

from importer.db import connect
from importer.seed import seed_demo

HERE = Path(__file__).resolve().parent
DASHBOARD_SQL = """
SELECT
    AVG(time2.ptp_sync) AS ptp_sync,
    AVG(time2.path_sync) AS path_sync,
    AVG(time2.tx_setup) AS tx_setup,
    AVG(time2.rx_setup) AS rx_setup,
    AVG(time2.tx_activate) AS tx_activate,
    AVG(time2.rx_activate) AS rx_activate,
    AVG(time2.tx_deact) AS tx_deact,
    AVG(time2.rx_deact) AS rx_deact,
    AVG(time1.rru_reset_detected) AS reset_detected,
    AVG(time1.rru_reset_enable) AS reset_enable,
    AVG(time1.rru_reset_onair) AS reset_onair,
    AVG(time1.rru_reset_detected) + AVG(time1.rru_reset_enable) + AVG(time1.rru_reset_onair) AS total_reset_time,
    version1.rru_vesion AS ru_version,
    version1.bbu_vesion AS bbu_version
FROM report_report_reportperiod AS time1
LEFT JOIN report_parse_soap_result AS time2
    ON time1.fk_report_uuid_id = time2.fk_report_uuid_id
LEFT JOIN report_reportinfo AS info1
    ON time1.fk_report_uuid_id = info1.report_uuid
LEFT JOIN report_reportdetail AS version1
    ON time1.fk_report_uuid_id = version1.fk_report_uuid_id
WHERE time1.rru_reset_detected > 0
"""


def _round_row(row: dict) -> dict:
    out = {}
    for key, value in row.items():
        if isinstance(value, float):
            out[key] = round(value, 2)
        else:
            out[key] = value
    return out


def load_rows():
    db = connect()
    try:
        if db.backend == "sqlite":
            seed_demo(db)
        sql = DASHBOARD_SQL
        params = []
        platform = (os.environ.get("RESET_TIME_PLATFORM") or "").strip()
        if platform:
            sql += " AND info1.platform_name = ?"
            params.append(platform)
        sql += " GROUP BY version1.rru_vesion LIMIT 20"
        return [_round_row(row) for row in db.fetchall(sql, params)]
    finally:
        db.close()


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(HERE / "templates"))

    @app.route("/")
    def dashboard():
        rows = load_rows()
        columns = [
            "ptp_sync",
            "path_sync",
            "tx_setup",
            "rx_setup",
            "tx_activate",
            "rx_activate",
            "tx_deact",
            "rx_deact",
            "reset_detected",
            "reset_enable",
            "reset_onair",
            "total_reset_time",
            "ru_version",
            "bbu_version",
        ]
        backend = (os.environ.get("RESET_TIME_DB_BACKEND") or "sqlite").strip().lower()
        return render_template(
            "index.html",
            rows=rows,
            columns=columns,
            demo=(backend != "mysql"),
        )

    return app


def main() -> None:
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    create_app().run(host=host, port=port)


if __name__ == "__main__":
    main()
