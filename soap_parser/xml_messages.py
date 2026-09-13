"""Normalize one-line SOAP OAM timestamp records into parseable XML."""

from __future__ import annotations

import datetime
import re
import time
from pathlib import Path
from typing import Iterable, List, Union
from xml.etree.ElementTree import Element, fromstring

TIMESTAMP_RAW = re.compile(r"<timestamp value=([^>\s]+)")
LINE_START = "<timestamp"
LINE_END = "Envelope>"


def normalize_xml(xml_line: str) -> str:
    """Turn `<timestamp value=2021-01-01T00:00:00Z/>...Envelope>` into a tree."""
    match = TIMESTAMP_RAW.search(xml_line)
    if not match:
        raise ValueError("line is not a timestamped SOAP record")
    time_raw = match.group(1).strip('"').rstrip("/")
    if not time_raw.endswith("Z"):
        time_raw += "Z"
    time_struct = time.strptime(time_raw, "%Y-%m-%dT%H:%M:%SZ")
    time_normalize_str = datetime.datetime(*time_struct[:6])
    replaced = re.sub(
        r"<timestamp value=[^>]+>",
        '<timestamp value="%s">' % time_normalize_str,
        xml_line,
        count=1,
    )
    if replaced.endswith("</timestamp>"):
        return replaced
    return replaced + "</timestamp>"


def iter_soap_lines(text: str) -> Iterable[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(LINE_START) and stripped.endswith(LINE_END):
            yield stripped


def soap2list(soap_log_file: Union[str, Path]) -> List[str]:
    path = Path(soap_log_file)
    return list(iter_soap_lines(path.read_text(encoding="utf-8", errors="replace")))


def parse_message(line_xml: str) -> tuple[str, Element, Element]:
    root = fromstring(line_xml)
    envelope = root[0]
    xml_time = root.get("value") or ""
    xml_header = envelope[0]
    xml_body = envelope[1]
    return xml_time, xml_header, xml_body
