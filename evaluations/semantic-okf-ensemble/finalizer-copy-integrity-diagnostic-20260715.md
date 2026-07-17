# Finalizer Copy-Integrity Diagnostic

## Outcome

The `2026-07-15T09-58-38-815Z-compare` live run was intentionally stopped and rejected after 46 of 90 planned answers. Its superseded single-tool MCP finalizer prototype completed for all 15 treatment rows, but only 5 visible model outputs were byte-identical to the corresponding finalizer text after trimming outer whitespace. Ten outputs changed at least one character, for an exact-copy rate of 33.33%.

This is not an answer-quality score. It is a transport-integrity failure in the historical prototype: the model could alter an authoritative path while copying an otherwise governed answer. In one q031 row, a versioned source-path separator changed from a dot to a hyphen even though the prototype had returned the correct path. The visible output therefore could not be assumed to retain the candidate's evidence validity. These counts measure neither the later historical v1.3.1 split prepare/confirm protocol nor the active v1.4.0 digest-confirmation protocol.

## Observations

| Question | Treatment rows | Exact visible copies |
| --- | ---: | ---: |
| `q031-graph-routing-boundary` | 3 | 0 |
| `q032-incremental-update-maturity` | 3 | 2 |
| `q033-corruption-specific-defenses` | 3 | 1 |
| `q034-nonmonotonic-context-budget` | 3 | 1 |
| `q035-lossless-enough-evidence-organization` | 3 | 1 |
| **Total** | **15** | **5** |

The stopped run completed 16 knowledge-only, 15 adaptive-control, and 15 ensemble-treatment rows. It is retained only as a diagnostic and must not be merged into an accepted 90-answer comparison.

## Decision

Historical MCP v1.3.1 replaced the single-tool prototype with separate prepare and confirm tools plus a host publication gate. It closed the later free-form publication boundary, but confirmation still required the model to copy the complete `candidate_json`. The frozen full-run attempt `2026-07-15T13-50-35-550Z-compare` (`eval-d9Z-2026-07-15T13:50:43`) failed that remaining step: its first treatment prepared successfully, failed to copy the long candidate into confirmation, did not recover, and stopped the run. That attempt is also rejected and contributes no benchmark row or metric.

The active MCP v1.4.0 protocol keeps separate tools but makes preparation return the closed canonical `semantic-okf-prepared-answer/1.0` envelope with exactly `schema`, `candidate_json`, `response_sha256`, and `byte_count`. The agent reviews the exact candidate and confirms only the envelope's 64-character lowercase hexadecimal `response_sha256`; it never copies the candidate or envelope into confirmation. The server verifies the outstanding digest and returns a receipt binding the exact candidate hash and byte count. The host independently verifies envelope keys, candidate canonicality, digest, UTF-8 length, terminal receipt, and transaction order before atomically publishing the exact `candidate_json` bytes. Confirmation is non-idempotent and terminal. A failed prepare or confirm publishes nothing and clears the transaction; recovery requires a fresh envelope and digest. Stale or mismatched digests, earlier or repeated confirmations, confirmation without a fresh prepare, non-canonical candidates, trailing calls, and envelope, length, hash, or receipt inconsistencies fail closed.

The machine-readable companion, [`finalizer-copy-integrity-diagnostic-20260715.json`](finalizer-copy-integrity-diagnostic-20260715.json), binds the rejected config, skill, and MCP runtime identities without publishing raw answers, reviewer content, or machine-specific paths. Raw Promptfoo rows and Codex traces remain append-only and ignored.
