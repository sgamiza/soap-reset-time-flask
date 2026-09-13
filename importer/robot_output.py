"""Parse Robot Framework output.xml into report rows."""

from __future__ import annotations

import ast
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from xml.etree.ElementTree import Element, parse

from soap_parser.xmlutil import local_name

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "importer_config.json"


def load_importer_config(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    candidates = []
    if path:
        candidates.append(Path(path))
    env_path = os.environ.get("IMPORTER_CONFIG")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(DEFAULT_CONFIG)
    for candidate in candidates:
        if candidate.is_file():
            with candidate.open(encoding="utf-8") as handle:
                return json.load(handle)
    return {"keyword_timings": {}}


def _children(node: Element, name: str) -> List[Element]:
    return [child for child in list(node) if local_name(child.tag) == name]


def _first(node: Element, name: str) -> Optional[Element]:
    for child in _children(node, name):
        return child
    return None


def _iter(node: Element, name: str):
    for el in node.iter():
        if local_name(el.tag) == name:
            yield el


def _robot_time_to_sql(value: str) -> str:
    array = time.strptime(value.split(".")[0], "%Y%m%d %H:%M:%S")
    return time.strftime("%Y-%m-%d %H:%M:%S", array)


def _robot_time_to_stamp(value: str) -> int:
    array = time.strptime(value.split(".")[0], "%Y%m%d %H:%M:%S")
    return int(time.mktime(array))


def _status_runtime(kw_node: Element) -> Optional[int]:
    for status in _children(kw_node, "status"):
        if status.get("status") != "PASS":
            continue
        start = status.get("starttime")
        end = status.get("endtime")
        if not start or not end:
            continue
        return _robot_time_to_stamp(end) - _robot_time_to_stamp(start)
    return None


def keyword_runtime(test_el: Element, keyword: str, after: Optional[str] = None) -> int:
    kws = [child for child in list(test_el) if local_name(child.tag) == "kw" and not child.get("type")]
    for index, kw in enumerate(kws):
        if after is None:
            if kw.get("name") == keyword:
                runtime = _status_runtime(kw)
                return runtime if runtime is not None else 0
        elif kw.get("name") == after:
            if index + 1 < len(kws) and kws[index + 1].get("name") == keyword:
                runtime = _status_runtime(kws[index + 1])
                return runtime if runtime is not None else 0
    return 0


def _msg_text(msg: Element) -> str:
    return "".join(msg.itertext())


def parse_soap_parser_result(root: Element) -> List[Dict[str, Optional[int]]]:
    for msg in _iter(root, "msg"):
        text = _msg_text(msg).strip()
        if "soap_parser_result" not in text:
            continue
        payload = text.split("=", 1)[-1].strip()
        try:
            parsed = ast.literal_eval(payload)
        except (ValueError, SyntaxError):
            continue
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    return []


def parse_robot_output(xml_file: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    path = Path(xml_file)
    tree = parse(path)
    root = tree.getroot()
    report_uuid = str(uuid.uuid4())
    config = config or load_importer_config()
    timings_cfg = config.get("keyword_timings") or {}

    tests = list(_iter(root, "test"))
    rru_product_name = None
    bbu_sw_version = None
    rru_sw_version = None
    for msg in _iter(root, "msg"):
        text = _msg_text(msg)
        if "RRU_PRODUCT_NAME" in text and rru_product_name is None:
            rru_product_name = text.split("=")[-1].split()[0]
        if "BBU_SW_VERSION" in text and bbu_sw_version is None:
            bbu_sw_version = text.split("=")[-1].split()[0]
        if "RU_SW_VERSION" in text and rru_sw_version is None:
            rru_sw_version = text.split("=")[-1].split()[0]
        if "${RU_REAL_BUILD_NAME}" in text and rru_sw_version is None:
            rru_sw_version = text.split("=")[-1].split()[0]

    details = []
    for index, test in enumerate(tests, start=1):
        status_el = _first(test, "status")
        if status_el is None:
            continue
        status = (status_el.get("status") or "").lower()
        error_msg = "null"
        if status == "fail" and status_el.text:
            error_msg = status_el.text.split("The last error was:")[-1]
        start = status_el.get("starttime") or "20200101 00:00:00"
        end = status_el.get("endtime") or start
        details.append(
            {
                "case_id": "case%s" % index,
                "case_name": test.get("name") or "",
                "bbu_vesion": bbu_sw_version,
                "rru_vesion": rru_sw_version,
                "result": status,
                "report_create_time": _robot_time_to_sql(start),
                "report_update_time": _robot_time_to_sql(end),
                "platform_name": rru_product_name or "SAMPLE_RU",
                "error_msg": error_msg,
                "fk_report_uuid_id": report_uuid,
                "throughputd": "0",
                "throughputu": "0",
            }
        )

    suite_status = None
    for suite in _children(root, "suite"):
        suite_status = _first(suite, "status") or suite_status
    report_time = "2020-01-01 12:00:00"
    report_date = "20200101"
    if suite_status is not None and suite_status.get("starttime"):
        report_time = _robot_time_to_sql(suite_status.get("starttime"))
        report_date = time.strftime(
            "%Y%m%d", time.strptime(suite_status.get("starttime").split(".")[0], "%Y%m%d %H:%M:%S")
        )

    pass_count = 0
    fail_count = 0
    stats = next(_iter(root, "statistics"), None)
    if stats is not None:
        suite_stats = _first(stats, "suite")
        if suite_stats is not None:
            stat = _first(suite_stats, "stat")
            if stat is not None:
                pass_count = int(stat.get("pass") or 0)
                fail_count = int(stat.get("fail") or 0)
    if pass_count + fail_count == 0:
        pass_count = sum(1 for item in details if item["result"] == "pass")
        fail_count = sum(1 for item in details if item["result"] == "fail")

    period = {
        "rru_reset_detected": 0,
        "rru_reset_enable": 0,
        "rru_reset_onair": 0,
        "rru_unLock_unLock": 0,
        "rru_unLock_onair": 0,
        "cell_unLock_unLock": 0,
        "cell_unLock_onair": 0,
        "fk_report_uuid_id": report_uuid,
    }
    tests_by_name = {test.get("name"): test for test in tests}
    mapping = {
        "rru_reset_detected": "rru_reset_detected",
        "rru_reset_enable": "rru_reset_enable",
        "rru_reset_onair": "rru_reset_onair",
        "rru_unlock": "rru_unLock_unLock",
        "rru_unlock_onair": "rru_unLock_onair",
        "cell_unlock": "cell_unLock_unLock",
        "cell_unlock_onair": "cell_unLock_onair",
    }
    for key, spec in timings_cfg.items():
        case_name = spec.get("case")
        keyword = spec.get("keyword")
        after = spec.get("after")
        test_el = tests_by_name.get(case_name)
        if test_el is None or not keyword:
            continue
        dest = mapping.get(key, key)
        period[dest] = keyword_runtime(test_el, keyword, after=after)

    info = {
        "case_sum": pass_count + fail_count,
        "case_pass_sum": pass_count,
        "case_fail_sum": fail_count,
        "time": report_time,
        "report_uuid": report_uuid,
        "date": report_date,
        "platform_name": rru_product_name or "SAMPLE_RU",
        "report_path": "samples/%s/%s/report.xml" % (report_date, rru_product_name or "SAMPLE_RU"),
    }
    return {
        "info": info,
        "period": period,
        "details": details,
        "soap_results": parse_soap_parser_result(root),
    }
