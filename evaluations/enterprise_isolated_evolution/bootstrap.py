"""Lock the process before importing the fixed planner or reading its input."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def main() -> None:
    """Apply irreversible restrictions and execute the sole decision policy."""
    root = Path(__file__).parent
    spec = importlib.util.spec_from_file_location("sandbox_runtime", root / "sandbox_runtime.py")
    sandbox = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sandbox)
    receipt = sandbox.lock_process()
    print(json.dumps({"schema": "enterprise-optimizer-ready/1.0", "lock": receipt}, sort_keys=True), flush=True)
    spec = importlib.util.spec_from_file_location("enterprise_frozen_planner", root / "planner.py")
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)
    planner.main()


if __name__ == "__main__":
    main()
