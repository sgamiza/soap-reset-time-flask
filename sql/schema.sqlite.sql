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
