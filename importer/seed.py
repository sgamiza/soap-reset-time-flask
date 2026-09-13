"""Insert bundled sample rows so the Flask demo has something to show."""

from __future__ import annotations

from typing import Any, Dict, List

DEMO_ROWS: List[Dict[str, Any]] = [
    {
        "report_uuid": "11111111-1111-1111-1111-111111111111",
        "case_date": "2021-06-17 03:16:48",
        "platform_name": "SAMPLE_RU",
        "rru_vesion": "RFSW-SAMPLE-1.0",
        "bbu_vesion": "BBU-SAMPLE-1.0",
        "rru_reset_detected": 5,
        "rru_reset_enable": 40,
        "rru_reset_onair": 20,
        "ptp_sync": 22,
        "path_sync": 32,
        "tx_setup": 5,
        "rx_setup": 6,
        "tx_activate": 2,
        "rx_activate": 3,
        "tx_deact": 4,
        "rx_deact": 5,
    },
    {
        "report_uuid": "22222222-2222-2222-2222-222222222222",
        "case_date": "2021-06-18 04:00:00",
        "platform_name": "SAMPLE_RU",
        "rru_vesion": "RFSW-SAMPLE-1.1",
        "bbu_vesion": "BBU-SAMPLE-1.1",
        "rru_reset_detected": 6,
        "rru_reset_enable": 38,
        "rru_reset_onair": 18,
        "ptp_sync": 20,
        "path_sync": 30,
        "tx_setup": 4,
        "rx_setup": 5,
        "tx_activate": 2,
        "rx_activate": 2,
        "tx_deact": 3,
        "rx_deact": 4,
    },
]


def seed_demo(db) -> None:
    existing = db.fetchall("SELECT COUNT(*) AS n FROM report_reportinfo")
    if existing and int(existing[0]["n"]) > 0:
        return
    for row in DEMO_ROWS:
        db.execute(
            """
            INSERT INTO report_reportinfo (
                report_uuid, case_sum, case_pass_sum, case_fail_sum, case_date,
                report_info_create_time, report_info_update_time, report_path, platform_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["report_uuid"],
                3,
                3,
                0,
                row["case_date"],
                row["case_date"],
                row["case_date"],
                "samples/demo/report.xml",
                row["platform_name"],
            ),
        )
        db.execute(
            """
            INSERT INTO report_report_reportperiod (
                rru_reset_detected, rru_reset_enable, rru_reset_onair,
                rru_unLock_unLock, rru_unLock_onair, cell_unLock_unLock, cell_unLock_onair,
                fk_report_uuid_id
            ) VALUES (?, ?, ?, 0, 0, 0, 0, ?)
            """,
            (
                row["rru_reset_detected"],
                row["rru_reset_enable"],
                row["rru_reset_onair"],
                row["report_uuid"],
            ),
        )
        db.execute(
            """
            INSERT INTO report_reportdetail (
                case_id, case_name, bbu_vesion, rru_vesion, result,
                report_create_time, report_update_time, platform_name, error_msg,
                fk_report_uuid_id, throughputd, throughputu
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "case1",
                "RU_Reset",
                row["bbu_vesion"],
                row["rru_vesion"],
                "pass",
                row["case_date"],
                row["case_date"],
                row["platform_name"],
                "null",
                row["report_uuid"],
                "0",
                "0",
            ),
        )
        db.execute(
            """
            INSERT INTO report_parse_soap_result (
                fk_report_uuid_id, ptp_sync, path_sync, tx_setup, rx_setup,
                tx_activate, rx_activate, tx_deact, rx_deact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["report_uuid"],
                row["ptp_sync"],
                row["path_sync"],
                row["tx_setup"],
                row["rx_setup"],
                row["tx_activate"],
                row["rx_activate"],
                row["tx_deact"],
                row["rx_deact"],
            ),
        )
    db.commit()
