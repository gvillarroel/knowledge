from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    if sys.version_info < (3, 10):
        print("ERROR: CPython 3.10 or newer is required", file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parents[1]
    template = root / "assets" / "classical-atlas-template.html"
    if not template.is_file():
        print("ERROR: atlas template is missing", file=sys.stderr)
        return 1
    if template.read_text(encoding="utf-8").count("__CLASSICAL_ATLAS_DATA__") != 1:
        print("ERROR: atlas template data placeholder is invalid", file=sys.stderr)
        return 1
    print("PASS: standard-library runtime and atlas template are available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
