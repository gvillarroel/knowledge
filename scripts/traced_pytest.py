"""Write stdlib trace coverage while preserving pytest's process exit status."""
from __future__ import annotations

import argparse
import trace

import pytest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverdir", required=True)
    parser.add_argument("--ignore-dir", action="append", default=[])
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    pytest_args = args.pytest_args
    if pytest_args[:1] == ["--"]:
        pytest_args = pytest_args[1:]

    tracer = trace.Trace(count=True, trace=False, ignoredirs=args.ignore_dir)
    try:
        return int(tracer.runfunc(pytest.main, pytest_args))
    finally:
        tracer.results().write_results(
            show_missing=True, summary=True, coverdir=args.coverdir,
        )


if __name__ == "__main__":
    raise SystemExit(main())
