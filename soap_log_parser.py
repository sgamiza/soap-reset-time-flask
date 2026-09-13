"""Robot Framework library: Get Times From Log."""

from soap_parser.timings import get_times_from_log

__all__ = ["get_times_from_log"]


if __name__ == "__main__":
    from soap_parser.cli import main

    raise SystemExit(main())
