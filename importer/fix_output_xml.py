"""Repair truncated Robot output.xml without depending on Robot Framework."""

from __future__ import annotations

import argparse
import re
import time
from datetime import datetime
from pathlib import Path


def _date_to_second(time_string: str) -> float:
    if len(time_string) == 19:
        time_string = time_string.replace(" ", "-").replace(":", "-")
    elif len(time_string) == 14:
        chunks = [time_string[i : i + 2] for i in range(0, 14, 2)]
        time_string = "-".join(chunks).replace("-", "", 1)
    else:
        raise ValueError("unsupported time format")
    return time.mktime(time.strptime(time_string, "%Y-%m-%d-%H-%M-%S"))


def close_unclosed_tags(text: str, timeout_minutes: int = 20) -> str:
    lines = text.splitlines()
    uncomplete = []
    start_match = re.search(r"(\d{8}\s\d{2}:\d{2}:\d{2})", text)
    start_time = start_match.group(1) if start_match else datetime.now().strftime("%Y%m%d %H:%M:%S")
    if start_match:
        end_stamp = _date_to_second(start_time.replace(":", "").replace(" ", "")) + timeout_minutes * 60
        end_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(end_stamp))
    else:
        end_time = datetime.now().strftime("%Y%m%d %H:%M:%S")

    for line in lines:
        open_tag = re.match(r"^<(\w+)(?:\s|>)", line.strip())
        close_tag = re.match(r"^.*</(\w+)>$", line.strip())
        if open_tag and not re.search(r"</%s>" % open_tag.group(1), line):
            uncomplete.append(open_tag.group(1))
        elif close_tag and uncomplete and uncomplete[-1] == close_tag.group(1):
            uncomplete.pop()
    for tag in reversed(uncomplete):
        if tag in {"kw", "suite", "test"}:
            lines.append(
                '<status status="FAIL" endtime="%s" starttime="%s"></status>' % (end_time, start_time)
            )
        lines.append("</%s>" % tag)
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Close truncated Robot output.xml tags")
    parser.add_argument("src")
    parser.add_argument("dest", nargs="?")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args(argv)
    src = Path(args.src)
    dest = Path(args.dest) if args.dest else src
    dest.write_text(close_unclosed_tags(src.read_text(encoding="utf-8", errors="replace"), args.timeout), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
