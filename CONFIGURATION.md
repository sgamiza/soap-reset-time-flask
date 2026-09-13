# Configuration

All secrets stay in the environment or a local untracked `.env`. Copy `.env.example` and fill only what you need.

| Variable | Meaning | Default |
|---|---|---|
| `RESET_TIME_DB_BACKEND` | `sqlite` or `mysql` | `sqlite` |
| `RESET_TIME_SQLITE_PATH` | SQLite file for demo / local import | `data/demo.sqlite` |
| `MYSQL_HOST` | MySQL host | `127.0.0.1` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_USER` | MySQL user | `YOUR_USER` |
| `MYSQL_PASSWORD` | MySQL password | empty |
| `MYSQL_DATABASE` | Database name | `reset_time` |
| `RESET_TIME_PLATFORM` | Optional dashboard filter on `platform_name` | empty (all) |
| `FLASK_HOST` | Bind address | `127.0.0.1` |
| `FLASK_PORT` | HTTP port | `5000` |
| `SOAP_PARSER_CONFIG` | Override timing JSON | `config/soap_parser_config.json` |
| `IMPORTER_CONFIG` | Override Robot keyword/case map | `config/importer_config.json` |

MySQL schema: `sql/schema.mysql.sql`.

SQLite schema is created automatically on connect; the same DDL is in `sql/schema.sqlite.sql`.
