# Isolated Semantic QA Control

This workspace intentionally contains no Semantic OKF snapshot and no reader skill.

The benchmark prompt defines the response schema. Do not infer or fabricate facts that are not available through declared capabilities.

`bin/pi-spark-luna-fallback.ps1` preserves UTF-8 input and output, runs the requested PI model first, and retries with the configured fallback model only when the primary PI process exits unsuccessfully. It never falls back because an answer fails a semantic assertion and never retries when both model identifiers are the same.
