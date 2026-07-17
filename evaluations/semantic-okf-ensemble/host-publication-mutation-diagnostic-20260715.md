# Host Publication Mutation Diagnostic

## Rejected, non-benchmark evidence

The `2026-07-15T11-08-27-398Z-compare` run (`eval-RBD-2026-07-15T11:08:32`) was intentionally interrupted after 38 of 90 planned answers and is excluded from every benchmark comparison. This document examines only its three completed `q031-graph-routing-boundary` ensemble-treatment rows as diagnostic evidence.

All three rows used the superseded two-mode MCP prototype, produced canonical answer JSON through a successful prepare phase, and received a confirmation receipt that matched the candidate SHA-256 and UTF-8 byte count. Nevertheless, the pre-gate host command was plain `codex`, so it published the agent's free-form final message. Each published message differed from its already confirmed candidate. Zero of three outputs preserved the confirmed bytes, and six evidence fields changed in total.

This is a publication-boundary failure, not an answer-quality result. The rows demonstrate that server-side prepare and confirm are necessary but insufficient when the host later accepts a re-authored message.

## Exact observations

| Raw row | Confirmed candidate | Host-published output | Changed fields | Terminal prepare-confirm sequence |
| --- | --- | --- | ---: | --- |
| `356bb471-f92b-4798-9ddc-6322636eb4cc` | `95c736003003a3c48082eeab1524e8af927e4475f72e80171238f9b083a90ae6` (7,006 bytes) | `d757eba83ac60fb3fd2a6bb9d9d79e2140fcf8e5489f063607821c8d2025fc81` (7,018 bytes) | 1 | yes |
| `89a04468-9b9c-439b-9b0f-7f92de84b048` | `c7d9e703979c7f4bf6ac50a59693fbbff18fd3ce9c10e1d2e23e441c24e96882` (8,177 bytes) | `6c52137ae08d760335b3991d2aba04c5620acd03099d76d939d436f35d55204d` (8,198 bytes) | 3 | yes |
| `f55afa84-1165-41f5-9d3f-ac1b227faa5f` | `186073f94a2416fed2da41e156f80a43684daa27a742d4556c3fe9d8cbb7ca7d` (6,666 bytes) | `e4d8cc3701df5769484d8c13457cab0faccf9554f6c1944c8639aaa5167f1ab7` (6,687 bytes) | 2 | no; one additional prepare followed confirmation |

In every row, the host-published hash also equals the final raw agent-message hash. The mutation therefore occurred when the agent re-authored the answer after confirmation and the pre-gate host accepted that free-form message, not inside the historical MCP prototype.

The six changes were all contract-sensitive evidence fields:

- One `source_path` changed from the authoritative claim JSONL path to a claim Markdown-like path.
- Three `source_path` values gained an extra `claims-` prefix.
- One `source_path` changed the version separator from a dot to a hyphen.
- One `paper_id` was replaced by a source path.

The third row also made one successful prepare call after its confirmation. Its earlier confirmation receipt still bound a canonical candidate, but the extra call independently violates the terminal prepare-then-confirm protocol required for an accepted trace.

## Decision

The definitive comparison must route Codex through the hash-bound host publication wrapper and the four-tool MCP v1.4.0 contract. Preparation returns the closed canonical `semantic-okf-prepared-answer/1.0` envelope with exactly `schema`, `candidate_json`, `response_sha256`, and `byte_count`; confirmation receives only the short digest, never the candidate or envelope. For treatment traces, any failed prepare or confirm publishes nothing and clears the transaction. The wrapper accepts only a final clean suffix of one or more fresh successful prepares followed by exactly one successful terminal digest confirmation. It verifies the envelope, candidate canonicality, hash, UTF-8 length, receipt binding, and order, then atomically publishes the exact `candidate_json` bytes. It rejects an earlier successful confirm, confirm without a fresh prepare after failure, stale or mismatched digest, non-canonical candidate, repeated confirm, or anything after successful confirmation. Controls continue to publish their final raw agent message unchanged. A fresh, complete v1.4.0 90-answer run and independent trace attestation are required before any results are accepted.

## Provenance and retention

- Interrupted execution log: `ac44e2df4cb36ee221b34df5bf6272e8c691590a79815d9b8e021348de8b63dc`.
- Generated pre-gate Promptfoo config: `b5c24502dab70cfed883befb7cd66094137b558ac4fc76ba743dfbf4b86d69df`.
- Raw trace SHA-256 values: `c9ccedaace112f3baedfe4afa1e4d89d8076c22dcd4358856919087a8bad1211`, `5d4beb64daef791c849bcad32df245f6cc138024bab54accdf13efe5929c9961`, and `029575ad71138e5a5b57d78be7aea0a0908e914b73d53e6aa3ea7002c180c04c`.

The machine-readable companion, [`host-publication-mutation-diagnostic-20260715.json`](host-publication-mutation-diagnostic-20260715.json), uses a closed schema and includes exact database-row projection, response, metadata, trace, candidate, receipt, final-message, and host-output hashes. Raw Promptfoo rows and traces remain append-only and ignored; neither full answers nor machine-specific paths are copied into the checked artifacts.
