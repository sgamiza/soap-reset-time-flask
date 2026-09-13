"""SQLite demo + optional MySQL backend. Credentials come from environment variables only."""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from soap_parser.config_loader import load_parser_config

COLUMN_RE = re.compile(r"^[A-Za-z0-9_]+$")
SOAP_COLUMNS = (
    "ptp_sync",
    "path_sync",
    "tx_setup",
    "rx_setup",
    "tx_activate",
    "rx_activate",
    "tx_deact",
    "rx_deact",
)
SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS report_reportinfo (
    report_uuid TEXT PRIMARY KEY,
    case_sum INTEGER,
    case_pass_sum INTEGER,
    case_fail_sum INTEGER,
    case_date TEXT,
    report_info_create_time TEXT,
    report_info_update_time TEXT,
    report_path TEXT,
    platform_name TEXT,
    UNIQUE(case_date, platform_name)
);
CREATE TABLE IF NOT EXISTS report_reportdetail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    case_name TEXT,
    bbu_vesion TEXT,
    rru_vesion TEXT,
    result TEXT,
    report_create_time TEXT,
    report_update_time TEXT,
    platform_name TEXT,
    error_msg TEXT,
    fk_report_uuid_id TEXT,
    throughputd TEXT,
    throughputu TEXT
);
CREATE TABLE IF NOT EXISTS report_report_reportperiod (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rru_reset_detected INTEGER,
    rru_reset_enable INTEGER,
    rru_reset_onair INTEGER,
    rru_unLock_unLock INTEGER,
    rru_unLock_onair INTEGER,
    cell_unLock_unLock INTEGER,
    cell_unLock_onair INTEGER,
    fk_report_uuid_id TEXT
);
CREATE TABLE IF NOT EXISTS report_parse_soap_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fk_report_uuid_id TEXT,
    ptp_sync INTEGER,
    path_sync INTEGER,
    tx_setup INTEGER,
    rx_setup INTEGER,
    tx_activate INTEGER,
    rx_activate INTEGER,
    tx_deact INTEGER,
    rx_deact INTEGER
);
"""


def sqlite_path() -> Path:
    raw = os.environ.get("RESET_TIME_SQLITE_PATH", "data/demo.sqlite")
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def backend_name() -> str:
    return (os.environ.get("RESET_TIME_DB_BACKEND") or "sqlite").strip().lower()


class Database:
    def __init__(self, conn: Any, backend: str):
        self.conn = conn
        self.backend = backend

    def close(self) -> None:
        self.conn.close()

    def commit(self) -> None:
        self.conn.commit()

    def _sql(self, sql: str) -> str:
        if self.backend == "mysql":
            return sql.replace("?", "%s")
        return sql

    def execute(self, sql: str, params: Sequence[Any] = ()) -> Any:
        cursor = self.conn.cursor()
        cursor.execute(self._sql(sql), params)
        return cursor

    def fetchall(self, sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        cursor = self.execute(sql, params)
        rows = cursor.fetchall()
        if self.backend == "sqlite":
            return [dict(row) for row in rows]
        columns = [item[0] for item in cursor.description]
        return [dict(zip(columns, row)) for row in rows]


def connect(init_sqlite: bool = True) -> Database:
    name = backend_name()
    if name == "mysql":
        import pymysql

        conn = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "YOUR_USER"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "reset_time"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.Cursor,
        )
        return Database(conn, "mysql")

    conn = sqlite3.connect(str(sqlite_path()))
    conn.row_factory = sqlite3.Row
    db = Database(conn, "sqlite")
    if init_sqlite:
        conn.executescript(SQLITE_SCHEMA)
        conn.commit()
    return db


def safe_column(name: str) -> str:
    column = name.split(":")[0].strip().replace(" ", "_").lower()
    if not COLUMN_RE.match(column):
        raise ValueError("unsafe SQL column: %s" % name)
    return column


def soap_values_from_results(soap_results: Iterable[Dict[str, Optional[int]]]) -> Dict[str, Optional[int]]:
    values = {column: None for column in SOAP_COLUMNS}
    try:
        config = load_parser_config()
        label_to_column = {
            label: safe_column(str(spec.get("column") or label)) for label, spec in config.items()
        }
    except Exception:
        label_to_column = {}
    for item in soap_results:
        for label, seconds in item.items():
            column = label_to_column.get(label)
            if column is None:
                try:
                    column = safe_column(str(label))
                except ValueError:
                    continue
            if column in values:
                values[column] = seconds
    return values


def save_report(db: Database, report: Dict[str, Any]) -> None:
    info = report["info"]
    period = report["period"]
    details = report["details"]
    soap_results = report.get("soap_results") or []
    db.execute(
        """
        INSERT INTO report_reportinfo (
            report_uuid, case_sum, case_pass_sum, case_fail_sum, case_date,
            report_info_create_time, report_info_update_time, report_path, platform_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            info["report_uuid"],
            info["case_sum"],
            info["case_pass_sum"],
            info["case_fail_sum"],
            info["time"],
            info["time"],
            info["time"],
            info["report_path"],
            info["platform_name"],
        ),
    )
    db.execute(
        """
        INSERT INTO report_report_reportperiod (
            rru_reset_detected, rru_reset_enable, rru_reset_onair,
            rru_unLock_unLock, rru_unLock_onair, cell_unLock_unLock, cell_unLock_onair,
            fk_report_uuid_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            period["rru_reset_detected"],
            period["rru_reset_enable"],
            period["rru_reset_onair"],
            period["rru_unLock_unLock"],
            period["rru_unLock_onair"],
            period["cell_unLock_unLock"],
            period["cell_unLock_onair"],
            period["fk_report_uuid_id"],
        ),
    )
    for detail in details:
        db.execute(
            """
            INSERT INTO report_reportdetail (
                case_id, case_name, bbu_vesion, rru_vesion, result,
                report_create_time, report_update_time, platform_name, error_msg,
                fk_report_uuid_id, throughputd, throughputu
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                detail["case_id"],
                detail["case_name"],
                detail["bbu_vesion"],
                detail["rru_vesion"],
                detail["result"],
                detail["report_create_time"],
                detail["report_update_time"],
                detail["platform_name"],
                detail["error_msg"],
                detail["fk_report_uuid_id"],
                detail["throughputd"],
                detail["throughputu"],
            ),
        )
    soap_values = soap_values_from_results(soap_results)
    db.execute(
        """
        INSERT INTO report_parse_soap_result (
            fk_report_uuid_id, ptp_sync, path_sync, tx_setup, rx_setup,
            tx_activate, rx_activate, tx_deact, rx_deact
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            info["report_uuid"],
            soap_values["ptp_sync"],
            soap_values["path_sync"],
            soap_values["tx_setup"],
            soap_values["rx_setup"],
            soap_values["tx_activate"],
            soap_values["rx_activate"],
            soap_values["tx_deact"],
            soap_values["rx_deact"],
        ),
    )
    db.commit()
