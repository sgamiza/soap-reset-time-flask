# SOAP Reset Time

**从SOAP 消息里，把无线单元的各个模块「重置时间」拆成可度量的因果链。**  
**From SOAP messages, break each radio-unit module’s reset time into a measurable causal chain.**

> 复位不是一个点，而是一段被协议自己写下的历史。  
> A reset is not a point in time. It is a history the protocol already wrote down.

---

## 缘起 · Why this exists

无线单元（RU）从失联到重新 on-air，表面上是测试用例里的几个关键字，底层却是一条严格的 OAM 状态机：`moduleReady` → PTP 锁定 → 数据通路锁定 → 载波创建 → 激活 →（必要时）去激活。实验室习惯用 Robot 的墙钟去量「等了多久」，那测到的是**测试夹具的耐心**；真正刻画空口侧行为的，是 SOAP 信封头上那枚未加引号的时间戳。

本仓库把这两种时间源叠在同一套语义上：前者来自 Robot `output.xml` 的 keyword 区间，后者来自 SOAP OAM 流里「谓词命中的第一帧」。两者都不是拍脑袋打点，而是把「什么叫开始、什么叫结束」写成可版本化的 JSON 本体论，让计时从脚本里的魔法数字，变成一份可审计的规则。

On the surface, a radio unit (RU) returning from silence to on-air is a handful of Robot keywords. Underneath sits a disciplined OAM state machine: `moduleReady` → PTP lock → data-path lock → carrier create → activate → (optionally) deactivate. The wall-clock of a test harness measures **how long the fixture was willing to wait**. The timestamps on SOAP envelopes measure **how the air-side machine actually moved**.

This repository overlays both clocks on one vocabulary. Robot `output.xml` contributes keyword intervals; the SOAP stream contributes the first envelope that satisfies a start predicate and the first that satisfies an end predicate. Neither is a handwritten stopwatch. “What counts as begin / end” is a versioned JSON ontology, so timing stops being a magic number inside a script and becomes a rule you can audit.

This tree is a sanitized, rebuildable snapshot. It ships no lab hosts, passwords, serials, or captured dumps.

---

## 它在度量什么 · What is being measured

默认规则把「复位」拆成正交的两层：

| 层 · Layer | 时间源 · Clock | 语义 · Semantics |
|---|---|---|
| 夹具层 · Harness | Robot keyword 墙钟 | Detected → enable → on-air，以及 unlock 后的等待 |
| 协议层 · Protocol | SOAP envelope 时间戳 | PTP、通路同步、Tx/Rx 载波的 create / activate / deactivate |

协议层把每一段耗时定义成 **有序消息流上的一对一阶谓词**：头域 `from`/`to` 的子串、体域 tag 的 local-name、managed object 的 `class`/`distName`、参数的 `newValue`/`prevValue`、以及是否必须看见 `<status>OK</status>`。匹配按 local-name 穿越 SOAP 命名空间，跳过同名但不满足属性的节点，而不是「撞见第一个 tag 就返回」。

结果不是「日志里出现过某字符串」，而是：**在因果顺序里，这个状态跃迁花费了多少秒。**

The default rules split “reset” into two orthogonal layers:

- **Harness time** — Robot keyword wall-clock: detected → enable → on-air, plus unlock waits.
- **Protocol time** — SOAP envelope timestamps: PTP, path sync, Tx/Rx carrier create / activate / deactivate.

Each protocol interval is a **pair of first-order predicates** on an ordered message stream: header `from`/`to` substrings, body tag local-names, managed-object `class`/`distName`, parameter `newValue`/`prevValue`, and an optional `<status>OK</status>` gate. Matching walks SOAP namespaces by local-name and continues past same-named nodes whose attributes fail, instead of returning on the first tag collision.

The number you get is not “a string occurred in a log”. It is: **how many seconds that state transition took, in causal order.**

---

## 完整能力 · Feature list

- 从 `.xml`、`.xml.gz`、嵌套 `rflog_*.zip` 或含上述任一产物的目录中提取 SOAP OAM 流；解压在临时目录完成，不在工作区留下实验室残渣。  
  Ingest SOAP OAM from `.xml`, `.xml.gz`, nested `rflog_*.zip`, or a directory that contains any of those; extraction stays in a temp tree so the workspace is not littered with lab leftovers.
- Zip-slip 防护：拒绝 `..` 与绝对路径成员。  
  Zip-slip defence: members with `..` or absolute paths are ignored.
- 计时规则外置为 `config/soap_parser_config.json`，SQL/看板列名稳定（`ptp_sync`、`tx_setup` …），与展示文案解耦。  
  Timing rules live in `config/soap_parser_config.json` with stable SQL/dashboard columns, decoupled from display labels.
- CLI：`python -m soap_parser samples/soap_log.xml`（人类可读或 `--json`）。  
  CLI: `python -m soap_parser samples/soap_log.xml` (human text or `--json`).
- Robot 库：`Library soap_log_parser.py` → `Get Times From Log`；骨架见 `robot/GetResetTime.robot`。  
  Robot library: `Library soap_log_parser.py` then `Get Times From Log`.
- 导入 Robot `output.xml`：关键字耗时 + 可选 SOAP 解析结果写入 SQLite / MySQL；用例名与关键字映射在 `config/importer_config.json`，代码里不写死实验室用例号。  
  Import Robot `output.xml` keyword durations (and optional SOAP results) into SQLite or MySQL; case/keyword names stay in `config/importer_config.json`.
- Flask 看板按软件版本聚合均值；`rru_reset_detected > 0` 才进入复位统计。  
  Flask dashboard averages by software version; only rows with `rru_reset_detected > 0` enter the reset aggregate.
- 默认 SQLite demo（`data/demo.sqlite`），无需 MySQL 即可打开页面。  
  Bundled SQLite demo so the UI runs without MySQL.
- 截断的 Robot XML 补全闭合标签，不依赖 `robot` 包。  
  Repair truncated Robot XML without importing Robot Framework.
- SQL 参数绑定；列名只允许 `[A-Za-z0-9_]`。Robot 侧解析结果用 `ast.literal_eval`，不用 `eval`。  
  Parameterised SQL; column names restricted to `[A-Za-z0-9_]`. Robot payloads parsed with `ast.literal_eval`, never `eval`.
- pytest + GitHub Actions（无设备、无实验室网络）。  
  pytest + GitHub Actions with no devices and no lab network.

---

## 技术栈 · Tech stack

| 角色 · Role | 选择 · Choice |
|---|---|
| 语言 · Language | Python 3.9+ |
| 展示 · Web | Flask 2.2+（Jinja 出表，不绑 pandas） |
| 存储 · Store | SQLite（demo / 本机）或 PyMySQL（`RESET_TIME_DB_BACKEND=mysql`） |
| 测试 · Test | pytest, pytest-cov |
| 协议对象 · Protocol objects | stdlib `xml.etree` + gzip / zipfile |

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

密钥与主机只存在于环境变量或未跟踪的 `.env`。抄 `.env.example`，对照 `CONFIGURATION.md`。

Secrets live only in the environment or an untracked `.env`. Copy `.env.example`; see `CONFIGURATION.md`.

---

## 如何运行 · How to run

### 1. 量一条 SOAP 流 · Measure a SOAP log

```bash
python -m soap_parser samples/soap_log.xml
python -m soap_parser samples/soap_log.xml --json
```

随仓库的合成样本（秒）：PTP 22，通路 32，Tx setup 5，Tx activate 2，Rx setup 6，Rx activate 3，Tx deactivate 4，Rx deactivate 5。  
On the synthetic sample (seconds): PTP 22, path 32, Tx setup 5, Tx activate 2, Rx setup 6, Rx activate 3, Tx deactivate 4, Rx deactivate 5.

Robot：

```robot
*** Settings ***
Library    soap_log_parser.py

*** Test Cases ***
Measure SOAP
    ${soap_parser_result}=    Get Times From Log    ${OUTPUT_DIR}
    Log    ${soap_parser_result}
```

### 2. 演示看板 · Demo dashboard（无 MySQL）

```bash
python flask_reset_time.py
```

打开 http://127.0.0.1:5000/ 。进程会创建 `data/demo.sqlite` 并写入两个示例版本。默认只监听本机回环。  
Open http://127.0.0.1:5000/ . The process creates `data/demo.sqlite` and seeds two sample versions. Bind address defaults to loopback.

### 3. 导入 Robot 报告 · Import Robot output

```bash
python save_history_data_to_mysql.py samples/robot_output.xml
```

默认后端仍是 SQLite。要接 MySQL：填写 `MYSQL_*`，设 `RESET_TIME_DB_BACKEND=mysql`，执行 `sql/schema.mysql.sql`。  
Default backend remains SQLite. For MySQL, fill `MYSQL_*`, set `RESET_TIME_DB_BACKEND=mysql`, and apply `sql/schema.mysql.sql`.

### 4. 单测 · Tests

```bash
python -m pytest -v --cov=soap_parser --cov=importer --cov=web --cov-report=term-missing
```

---

## 计时规则即本体论 · Timing rules as ontology

`config/soap_parser_config.json` 里每一项度量都是一个命名的区间。改规则等于改「时间」的定义，而不必改匹配引擎。

Each metric in `config/soap_parser_config.json` is a named interval. Changing the JSON changes the definition of time; the matcher stays put.

| 字段 · Field | 含义 · Meaning |
|---|---|
| `column` | SQL / 看板列名（`ptp_sync`、`tx_setup` …） |
| `start` / `end` | 区间两端的消息谓词 |
| `xml_tag_name` | SOAP body 中要找的 tag |
| `msg_from` / `msg_to` | 头域 `from` / `to` 的子串（如 `BTS` ⊂ `BTS_OM_SAMPLE`） |
| `xml_tag_attrib` | 属性子串（`class`、`distName`） |
| `managed_parameter_change` | `parameterName` / `newValue` / 可选 `prevValue` |
| `should_contain_list` | 文本或 tag 必须同时出现（合取） |
| `check_status` | 要求 body 含 `<status>OK</status>` |

导入侧的用例名、关键字名在 `config/importer_config.json`。实验室内部编号不应进入 Python。

Importer case and keyword names live in `config/importer_config.json` so site-specific titles never harden into Python.

---

## 目录结构 · File structure

```text
.
├── README.md                      # 中英双语 · bilingual
├── CONFIGURATION.md               # 环境变量 · env vars
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── flask_reset_time.py            # Web 入口 · web entry
├── soap_log_parser.py           # Robot 库 + CLI 包装
├── save_history_data_to_mysql.py
├── config/
│   ├── soap_parser_config.json  # 协议层区间本体论
│   └── importer_config.json     # 夹具层关键字映射
├── soap_parser/                 # 可离线单测的谓词引擎
├── importer/                    # Robot XML → 库
├── web/                         # Flask + 模板
├── sql/                         # SQLite / MySQL DDL
├── samples/                     # 合成日志，非捕获
│   ├── soap_log.xml
│   └── robot_output.xml
├── robot/
├── tests/
└── .github/workflows/ci.yml
```

从这份树可以零外部依赖地重建：解析器、导入器、看板、合成样本与 CI。  
The tree is sufficient to rebuild the parser, importer, dashboard, synthetic fixtures, and CI with no external lab.

---

## 边界 · What this tree refuses to be

- 它不是协议栈，也不复现 OAM 会话；它只在**已经发生的痕迹**上做一阶匹配。  
  Not a protocol stack and not an OAM session replica — only first-order matching over traces that already happened.
- 它不是性能分析器：粒度是秒，不是示波器。  
  Not a profiler: granularity is seconds, not an oscilloscope.
- 凭据不进仓库；样本标识是 `BTS_OM_SAMPLE` / `SAMPLE_RU`。  
  Credentials never land in git; samples use `BTS_OM_SAMPLE` / `SAMPLE_RU`.
- Flask 默认 `127.0.0.1`。把 `FLASK_HOST` 改成 `0.0.0.0` 等于主动把看板暴露给网段，那是你的决定，不是默认。  
  Flask binds to `127.0.0.1` unless you set `FLASK_HOST`. Binding `0.0.0.0` is a conscious exposure, not the default.

时间一旦被规则化，争论就可以从「我记得它很快」变成「你用的那条谓词，和我的是不是同一条」。  
Once time is a rule, the argument stops being “I remember it was fast” and becomes “are we using the same predicate?”
