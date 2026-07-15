# CLI-only q031 Skill Arena diagnostic

This report covers two fresh, isolated Skill Arena comparisons of the definitive consultation skill after MCP retirement. The recursive structural scan found no MCP key or string value in the authored config or either materialized run config.

## Run disposition

| Run | Eval | Control | Treatment | Decision |
|---|---|---:|---:|---|
| `2026-07-15T20-00-29-037Z-compare` | `eval-vuT-2026-07-15T20:00:38` | 0.4 | timeout/error | Rejected: treatment produced no evaluable output at the 240-second adapter limit. |
| `2026-07-15T20-07-14-326Z-compare` | `eval-3TJ-2026-07-15T20:07:20` | 0.6 | 0.8 | Accepted as a diagnostic: both cells returned evaluated JSON. |

The rejected run is execution evidence only; its 0.4 control result cannot be paired with a missing treatment output. The treatment error was `skill-arena-model=openai-codex/gpt-5.6-luna routing=luna-only failed=true exit=124 / PI Luna attempt timed out after 240 seconds.`.

## Accepted isolated pair

| Cell | Score | Format | Contract | Evidence | Atomic | Negative | Latency (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Control | 0.6 | 1 | 1 | 0 | 0 | 1 | 72,190 |
| CLI treatment | 0.8 | 1 | 1 | 0 | 1 | 1 | 250,181 |

The treatment passed format, response contract, atomic completeness, and important-negative coverage. It failed only evidence validity. The mechanically reproduced check found 2 mismatches among 55 evidence-field checks; all 53 other checks passed.

| Claim | Field | Expected | Actual |
|---|---|---|---|
| `claim-2506-05690v3-002` | `source_path` | `sources/claims/2506.05690v3.jsonl` | `sources/claims/2506-05690v3.jsonl` |
| `claim-2506-05690v3-044` | `source_path` | `sources/claims/2506.05690v3.jsonl` | `sources/claims/2506-05690v3.jsonl` |

Both failures replace the authoritative dotted arXiv source filename with a dashed filename. The answer content and every other checked evidence binding match the config contract.

## Interpretation

The direct deterministic CLI finalizer in `cli-q031-comparison.json` scored **1.0** with all five gates and used no MCP. The accepted fresh agent treatment scored **0.8** because the agent publication step mutated two `source_path` bytes. The isolated result therefore shows that the CLI retrieval/finalization core succeeds without MCP, but an agent can still corrupt exact evidence bytes when no host-enforced publication gate copies validated stdout verbatim.

The treatment's 0.8 versus the control's 0.6 is limited evidence from one question. Cross-family comparisons remain descriptive because the legacy, embedding, classical, entity-graph, adaptive, and definitive rows were produced by separate retained runs and bundles. Exact response objects, summaries, result IDs, latency, named scores, and artifact hashes are retained in `cli-q031-skill-arena-diagnostic.json`.
