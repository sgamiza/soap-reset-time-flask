"""Measure start/end SOAP events defined in soap_parser_config.json."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from soap_parser.archive import load_soap_text
from soap_parser.config_loader import load_parser_config
from soap_parser.match import find_in_dom
from soap_parser.xml_messages import iter_soap_lines, normalize_xml, parse_message


@dataclass(frozen=True)
class TimingResult:
    label: str
    column: str
    seconds: Optional[int]
    start: Optional[str]
    end: Optional[str]


def cal_time_from_str(start: str, end: str) -> float:
    return time.mktime(time.strptime(end, "%Y-%m-%d %H:%M:%S")) - time.mktime(
        time.strptime(start, "%Y-%m-%d %H:%M:%S")
    )


def _clean_kwargs(spec: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not spec:
        return {}
    return {key: value for key, value in spec.items() if value is not None}


def find_node_time(soap_list: List[str], **kwargs: Any) -> Optional[str]:
    for line_xml in soap_list:
        xml_time, xml_header, xml_body = parse_message(line_xml)
        if find_in_dom(xml_header, xml_body, **kwargs):
            return xml_time
    return None


def messages_from_text(text: str) -> List[str]:
    return [normalize_xml(line) for line in iter_soap_lines(text)]


def measure_timings(soap_list: List[str], config: Dict[str, Any]) -> List[TimingResult]:
    results: List[TimingResult] = []
    for label, spec in config.items():
        start_time = find_node_time(soap_list, **_clean_kwargs(spec.get("start")))
        end_time = find_node_time(soap_list, **_clean_kwargs(spec.get("end")))
        seconds = None
        if start_time and end_time:
            seconds = int(cal_time_from_str(start_time, end_time))
        column = spec.get("column") or label.split(":")[0].strip()
        results.append(
            TimingResult(
                label=label,
                column=str(column),
                seconds=seconds,
                start=start_time,
                end=end_time,
            )
        )
    return results


def get_times_from_log(
    soap_log_path: Union[str, Path],
    soap_log_config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Optional[int]]]:
    """Robot Framework keyword: return [{label: seconds_or_None}, ...]."""
    config = soap_log_config or load_parser_config()
    soap_list = messages_from_text(load_soap_text(soap_log_path))
    return [{item.label: item.seconds} for item in measure_timings(soap_list, config)]
