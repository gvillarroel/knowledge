# Entity-Graph Format

`entity-graph/` is a closed, non-authoritative retrieval projection bound to the authoritative core tree, record-ledger digest, exact selected-source inventory, complete plan, algorithm identifiers, artifact hashes, and summary counts.

## Artifacts

- `entities.jsonl` stores authoritative document identities and extracted candidate phrases in schema `2.0`. Legacy `1.0` stores reviewed methods, dimensions, papers, and claims.
- `sections.jsonl` stores exact `record.body` text, character locators, source-scoped document identity, source and record digests, concept identity, heading path, token counts, and text hash. Legacy `1.0` retains PDF-page rows.
- `mentions.jsonl` stores deterministic normalized phrase matches. Every mention is a candidate discovery assertion.
- `edges.jsonl` stores exact evidence-section references and weights. Schema `2.0` uses `partOfDocument`, `mentionedInSection`, and `coMentionedWith`; legacy `1.0` retains its reviewed-claim predicates.
- `lexicon.json` stores section-level BM25 document frequency, inverse document frequency, and average length.
- `index.json` stores authority markers, core and source bindings, the plan, algorithm identities, artifact bindings, and summary.
- `build-report.json` stores the independently reproduced validation result.

## Schema 2.0 identity and locator contract

The durable document identity is `(source_id, record_id)`. `document_id` is a deterministic hash-derived spelling of that tuple, not a substitute for the structured identity. `record_sha256` binds the normalized ledger record, while `source_content_sha256` independently binds the complete physical source membership and bytes.

Each section locator has the closed form:

```json
{
  "target": "record-body",
  "kind": "character-range",
  "start": 0,
  "end": 120,
  "fragment": "record-body-..."
}
```

The exact evidence text must equal `record.body[start:end]` and its UTF-8 SHA-256 must equal `text_sha256`. `source_path` identifies the physical origin, and `concept_path` identifies its authoritative readable mirror; the character offsets address neither of those files directly.

`partOfDocument` is reviewed only as a structural identity binding. It does not assert that document prose is externally true. Candidate phrases, mentions, co-mentions, weights, paths, and rankings remain discovery-only.

## Legacy schema 1.0

Legacy reviewed-claim projection uses `hasReviewedClaim`, `objectTerm`, `aboutPaper`, `supportedBySection`, and `partOfPaper`. Multi-page claims create one `supportedBySection` edge per page. This representation remains accepted to reproduce frozen bundles.

## Validation

Validation rejects unknown files or keys, links, unsafe paths, duplicate or collision-prone identities, broken references, stale core/source/record hashes, invalid body ranges, mismatched text hashes, non-finite weights, schema drift, artifact mismatch, and any difference from complete deterministic rederivation.
