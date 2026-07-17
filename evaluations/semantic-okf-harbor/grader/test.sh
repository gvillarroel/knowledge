#!/usr/bin/env bash
set -euo pipefail

ground_truth=()
if [[ -f /tests/hard-ground-truth.json ]]; then
  ground_truth=(--ground-truth /tests/hard-ground-truth.json)
fi

python /tests/score.py \
  --pi-log /logs/agent/pi.txt \
  --question /tests/question.json \
  --ledger /tests/records.jsonl \
  --crosswalk /tests/source-combination.json \
  --authority-root /tests/authority \
  --reward /logs/verifier/reward.json \
  --diagnostics /logs/verifier/diagnostics.json \
  "${ground_truth[@]}"
