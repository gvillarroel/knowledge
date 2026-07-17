# Harbor Entity-Graph Answer Contract

## Authority and retrieval

`harbor_answer.py prepare` validates the published snapshot through the copied entity-graph runtime.
It runs the unchanged `fusion` ranking for the exact full question and bounded focused clauses. The
candidate union is deterministic and capped by `facet_limit`, `per_facet`, and `max_supports`.

Each graph result must identify an exact source-record ledger parent. Its section locator, text, and
text hash are checked against `record.body`. The adapter deduplicates by `(source_id, record_id)` and
projects the selected section to a full-record public locator. The support excerpt is bounded and its
range and hash participate in the opaque support ID. The full parent body hash becomes the public
`text_sha256`.

Entity candidates, mention edges, co-mention edges, traversal paths, section IDs, and ranking scores
remain discovery explanations. They cannot be used as support IDs or public evidence.

## Closed draft

The draft has exactly six top-level members: `question_id`, `question_sha256`, `parameters`,
`support_pack_sha256`, `answer`, and `evidence`. `answer` has exactly `summary` and `claims`. Every
claim has exactly `statement` and `evidence_indices`. `evidence` is a unique list of support IDs from
the recomputed pack.

Every evidence index must be an integer in range. The first occurrence of each index across claims
must be `0, 1, ...` and every listed support must be used. This makes public evidence order equal to
claim first-use order.

## Recomputed finalization

`finalize` rebuilds the snapshot and support pack from the exact CLI question and parameters. It
rejects duplicate JSON members, non-standard numbers, a changed question or digest, changed
parameters, a stale pack digest, unknown or altered support IDs, duplicate supports or per-claim
indices, unused evidence, and first-use-order violations. Drafts stored inside the bundle are also
rejected.

Successful output contains only `question_id`, `answer`, and `evidence`, in that order. Every public
evidence row contains only `source_id`, `record_id`, `concept_path`, `source_path`, `record_sha256`,
`locator`, and `text_sha256`. Structural acceptance establishes provenance integrity, not semantic
entailment; keep each claim atomic and verify it against the excerpt and authoritative parent.
