#!/usr/bin/env python3
"""Verify the standalone ensemble consultant runtime imports."""

from __future__ import annotations

import json

from _ensemble_snapshot import (
    ALGORITHM_ID,
    ANSWER_GATE_ID,
    COVERAGE_ALGORITHM_ID,
    GENERIC_ALGORITHM_ID,
    GENERIC_ANSWER_BRIEF_ALGORITHM_ID,
    GENERIC_ANSWER_GATE_ID,
    GENERIC_SCHEMA_VERSION,
    SCHEMA_VERSION,
)


def main() -> int:
    """Report the package's deterministic and optional semantic runtime contract."""

    print(
        json.dumps(
            {
                "status": "pass",
                "schema_versions": [SCHEMA_VERSION, GENERIC_SCHEMA_VERSION],
                "runtime": "semantic-okf-ensemble-query-python",
                "model_required": "quality-policy-only",
                "network_required": False,
                "algorithms": {
                    "direct_search": ALGORITHM_ID,
                    "generic_direct_search": GENERIC_ALGORITHM_ID,
                    "coverage": COVERAGE_ALGORITHM_ID,
                    "answer_gate": ANSWER_GATE_ID,
                    "generic_answer_gate": GENERIC_ANSWER_GATE_ID,
                    "generic_answer_brief": GENERIC_ANSWER_BRIEF_ALGORITHM_ID,
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
