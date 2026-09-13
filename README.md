# SOAP Reset Time (Flask)

## Project overview and purpose

Measure radio-unit (RU) reset and carrier setup/activate/deactivate timings from SOAP OAM logs, optionally import Robot Framework `output.xml`, and show averages in a small Flask dashboard.

Logs are one timestamped SOAP envelope per line. Timing rules live in JSON: each metric is a start message plus an end message (tag name, from/to, managed-object attributes, parameter changes). The default rules cover PTP lock, radio data-path lock, and Tx/Rx carrier create/activate/deactivate.

This repository is a sanitized, rebuildable snapshot. It does not contain lab hosts, passwords, product serials, or captured logs.

## Feature list

- Parse SOAP OAM logs from `.xml`, `.xml.gz`, nested `rflog_*.zip`, or a directory that contains any of those
- JSON timing rules (`config/soap_parser_config.json`) with stable SQL column names
- Command line: `python -m soap_parser samples/soap_log.xml`
- Robot Framework library: `Library soap_log_parser.py` then `Get Times From Log`
- Import Robot `output.xml` keyword durations (reset / unlock / on-air) into SQLite or MySQL
- Flask dashboard grouped by software version
- Bundled SQLite demo so the web UI runs without MySQL
- Repair truncated Robot XML tags without depending on Robot Framework
- pytest + GitHub Actions (no devices, no lab network)

## Tech stack and dependencies

- Python 3.9+
- Flask
- PyMySQL (only when `RESET_TIME_DB_BACKEND=mysql`)
- pytest / pytest-cov for tests

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## How to run and use

### 1. Measure a SOAP log

```bash
python -m soap_parser samples/soap_log.xml
python -m soap_parser samples/soap_log.xml --json
```

Expected sample costs (seconds): PTP 22, path 32, Tx setup 5, Tx activate 2, Rx setup 6, Rx activate 3, Tx deactivate 4, Rx deactivate 5.

Robot:

```robot
*** Settings ***
Library    soap_log_parser.py

*** Test Cases ***
Measure SOAP
    ${soap_parser_result}=    Get Times From Log    ${OUTPUT_DIR}
    Log    ${soap_parser_result}
```

A skeleton case is in `robot/GetResetTime.robot`.

### 2. Demo dashboard (no MySQL)

```bash
python flask_reset_time.py
```

Open http://127.0.0.1:5000/ . The app creates `data/demo.sqlite` and seeds two sample versions.

### 3. Import Robot output

```bash
python save_history_data_to_mysql.py samples/robot_output.xml
```

Default backend is SQLite. For MySQL, copy `.env.example`, fill `MYSQL_*`, set `RESET_TIME_DB_BACKEND=mysql`, and apply `sql/schema.mysql.sql`.

### 4. Tests

```bash
python -m pytest -v --cov=soap_parser --cov=importer --cov=web --cov-report=term-missing
```

## Timing rules

Each metric in `config/soap_parser_config.json`:

| Field | Meaning |
|---|---|
| `column` | SQL/dashboard name (`ptp_sync`, `tx_setup`, …) |
| `start` / `end` | Message matchers |
| `xml_tag_name` | Tag to find in the SOAP body |
| `msg_from` / `msg_to` | Substring match on header `from` / `to` |
| `xml_tag_attrib` | Attribute substrings (`class`, `distName`) |
| `managed_parameter_change` | `parameterName` / `newValue` / optional `prevValue` |
| `should_contain_list` | All of these texts or tags must exist |
| `check_status` | Require body `<status>OK</status>` |

Importer keyword/case names are in `config/importer_config.json` so lab-specific case titles stay out of the code.

## Project file structure

```text
.
├── README.md
├── CONFIGURATION.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── flask_reset_time.py          # web entry
├── soap_log_parser.py          # Robot library + CLI wrapper
├── save_history_data_to_mysql.py
├── config/
│   ├── soap_parser_config.json
│   └── importer_config.json
├── soap_parser/               # offline-testable parser
├── importer/                  # Robot XML → database
├── web/                       # Flask app + template
├── sql/
├── samples/
│   ├── soap_log.xml           # synthetic log (generated)
│   └── robot_output.xml
├── robot/
├── tests/
└── .github/workflows/ci.yml
```

## Sanitization notes

- Database host/user/password are environment variables only; no defaults that point at a lab
- Sample SOAP uses `BTS_OM_SAMPLE` / `SAMPLE_RU` identifiers
- Captured SOAP dumps, Robot suites, artifactory URLs, and unrelated upgrade scripts are not included
- Flask binds to `127.0.0.1` unless `FLASK_HOST` is set
