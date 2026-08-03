#!/usr/bin/env bash
set -euo pipefail

python /tests/score.py \
  --pi-log /logs/agent/pi.txt \
  --retrieval /logs/agent/retrieval.json \
  --question /tests/question.json \
  --ledger /tests/records.jsonl \
  --reward /logs/verifier/reward.json \
  --diagnostics /logs/verifier/diagnostics.json
