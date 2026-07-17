# Harbor Ensemble Answer Contract

## Authority and candidate union

`harbor_answer.py prepare` validates the complete published ensemble through the copied runtime. It
executes one declared policy—`quality` or `fast`—for the exact full question and bounded focused
clauses. The policy itself is unchanged. The adapter forms a deterministic round-robin union capped
by `facet_limit`, `per_facet`, and `max_supports`, so a focused facet may contribute an exact
source-record candidate missing from the full-query protected set.

Every hit must carry an exact `(source_id, record_id, record_sha256)` identity and matching crosswalk
passage evidence. The passage locator, text, and hash are checked against authoritative
`record.body`. Results are deduplicated by `(source_id, record_id)` and projected to full-record
public evidence. Each bounded excerpt's range and hash participate in its opaque support ID; the
full parent body hash becomes public `text_sha256`.

Adaptive expansions, embeddings, graph edges, group IDs, route rankings, and scores remain
discovery signals. They are not support IDs and cannot become public factual evidence.

## Closed draft

The draft has exactly six top-level members: `question_id`, `question_sha256`, `parameters`,
`support_pack_sha256`, `answer`, and `evidence`. `answer` has exactly `summary` and `claims`. Every
claim has exactly `statement` and `evidence_indices`. `evidence` is a unique list of support IDs from
the recomputed pack.

Every evidence index must be an integer in range. The first occurrence of each index across claims
must be `0, 1, ...` and every listed support must be used. This makes public evidence order equal to
claim first-use order.

## Recomputed finalization

`finalize` reloads the ensemble and rebuilds the candidate union from the exact CLI question,
policy, and numeric parameters. It rejects duplicate JSON members, non-standard numbers, a changed
question or digest, parameter drift, stale pack digests, unknown or altered support IDs, duplicate
supports or per-claim indices, unused evidence, and first-use-order violations. Drafts stored inside
the bundle are also rejected.

Successful output contains only `question_id`, `answer`, and `evidence`, in that order. Every public
evidence row contains only `source_id`, `record_id`, `concept_path`, `source_path`, `record_sha256`,
`locator`, and `text_sha256`. Structural acceptance establishes provenance integrity, not semantic
entailment; keep each claim atomic and verify it against the excerpt and authoritative parent.
