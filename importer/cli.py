"""Import Robot output.xml into SQLite/MySQL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from importer.db import connect, save_report
from importer.robot_output import parse_robot_output


def iter_output_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("output.xml")):
        yield path
    for path in sorted(root.rglob("*.xml")):
        if path.name != "output.xml":
            yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import Robot output.xml into the reset-time database")
    parser.add_argument("path", nargs="?", default="samples/robot_output.xml")
    args = parser.parse_args(argv)
    target = Path(args.path)
    if not target.exists():
        print("Error: path not found: %s" % target, file=sys.stderr)
        return 1
    db = connect()
    try:
        for xml_file in iter_output_files(target):
            report = parse_robot_output(xml_file)
            try:
                save_report(db, report)
                print(
                    "saved %s platform=%s date=%s"
                    % (xml_file, report["info"]["platform_name"], report["info"]["date"])
                )
            except Exception as exc:
                print("skip %s: %s" % (xml_file, exc), file=sys.stderr)
                db.conn.rollback()
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
