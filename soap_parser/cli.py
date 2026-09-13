"""CLI: python -m soap_parser PATH_TO_XML_OR_DIR"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from soap_parser.archive import load_soap_text
from soap_parser.config_loader import load_parser_config
from soap_parser.timings import measure_timings, messages_from_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure RU SOAP OAM timings from a log")
    parser.add_argument("path", nargs="?", default=".", help="xml / gz / zip / directory")
    parser.add_argument("--config", help="path to soap_parser_config.json")
    parser.add_argument("--json", action="store_true", dest="as_json", help="print JSON")
    args = parser.parse_args(argv)

    target = Path(args.path)
    try:
        config = load_parser_config(args.config)
        results = measure_timings(messages_from_text(load_soap_text(target)), config)
    except Exception as exc:
        print("Error: %s" % exc, file=sys.stderr)
        return 1

    if args.as_json:
        print(
            json.dumps(
                [
                    {
                        "label": item.label,
                        "column": item.column,
                        "seconds": item.seconds,
                        "start": item.start,
                        "end": item.end,
                    }
                    for item in results
                ],
                indent=2,
            )
        )
        return 0

    for item in results:
        if item.seconds is None:
            print("%s\t not found" % item.label)
        else:
            print(
                "%s\t cost=%s s\t start/end: %s / %s"
                % (item.label, item.seconds, item.start, item.end)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
