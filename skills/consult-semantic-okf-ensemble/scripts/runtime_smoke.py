#!/usr/bin/env python3
"""Verify the standalone ensemble consultant runtime imports."""

from __future__ import annotations

import json

from _ensemble_snapshot import (
    ALGORITHM_ID,
    ANSWER_GATE_ID,
    COVERAGE_ALGORITHM_ID,
    SCHEMA_VERSION,
)


def main() -> int:
    """Report the package's deterministic and optional semantic runtime contract."""

    print(
        json.dumps(
            {
                "status": "pass",
                "schema_version": SCHEMA_VERSION,
                "runtime": "semantic-okf-ensemble-query-python",
                "model_required": "quality-policy-only",
                "network_required": False,
                "algorithms": {
                    "direct_search": ALGORITHM_ID,
                    "coverage": COVERAGE_ALGORITHM_ID,
                    "answer_gate": ANSWER_GATE_ID,
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
