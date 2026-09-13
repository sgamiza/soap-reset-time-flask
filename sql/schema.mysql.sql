CREATE TABLE IF NOT EXISTS report_reportinfo (
    report_uuid VARCHAR(64) PRIMARY KEY,
    case_sum INT,
    case_pass_sum INT,
    case_fail_sum INT,
    case_date DATETIME,
    report_info_create_time DATETIME,
    report_info_update_time DATETIME,
    report_path VARCHAR(255),
    platform_name VARCHAR(64),
    UNIQUE KEY uniq_date_platform (case_date, platform_name)
);

CREATE TABLE IF NOT EXISTS report_reportdetail (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    case_id VARCHAR(32),
    case_name VARCHAR(128),
    bbu_vesion VARCHAR(128),
    rru_vesion VARCHAR(128),
    result VARCHAR(16),
    report_create_time DATETIME,
    report_update_time DATETIME,
    platform_name VARCHAR(64),
    error_msg TEXT,
    fk_report_uuid_id VARCHAR(64),
    throughputd VARCHAR(32),
    throughputu VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS report_report_reportperiod (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    rru_reset_detected INT,
    rru_reset_enable INTEGER,
    rru_reset_onair INT,
    rru_unLock_unLock INT,
    rru_unLock_onair INT,
    cell_unLock_unLock INT,
    cell_unLock_onair INT,
    fk_report_uuid_id VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS report_parse_soap_result (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    fk_report_uuid_id VARCHAR(64),
    ptp_sync INT,
    path_sync INT,
    tx_setup INTEGER,
    rx_setup INT,
    tx_activate INT,
    rx_activate INT,
    tx_deact INT,
    rx_deact INT
);
