# Querying the Entity-Section Graph

For a Harbor-style contracted answer, use `scripts/harbor_answer.py` first. It invokes the same
`fusion` route over the full question and bounded focused clauses, returns compact parent-record
support, and requires recomputed finalization. Use the lower-level modes below only for diagnosis or
additional read-only context; never bypass the finalizer for a contracted response.

## Choose a route

- `lexical` is exact-section BM25 and favors rare names, formulas, and terminology.
- `entity` resolves authoritative document identities and candidate phrases, then follows document bindings and exact mentions.
- `traversal` propagates through bounded structural and candidate association paths. Reviewed structural and candidate weights remain separate.
- `fusion` combines all three rankings by reciprocal rank and applies a per-document cap in schema `2.0` or per-paper cap in legacy `1.0`.

Use broad fusion first for synthesis, then focused entity or traversal queries for missing mechanisms, exclusions, and failure conditions. A result is a discovery candidate until its authoritative record-body slice has been opened and interpreted in context.

## Source-generic evidence

Schema `2.0` returns a structured `document_identity`, deterministic `document_id`, `source_id`, `record_id`, source and record digests, subject IRI, concept identity, source and concept paths, heading path, exact locator, evidence text, and text hash. Copy these fields. Do not infer them from a title, URL, or path.

The locator target is `record-body`. Verify evidence against the matching row in `semantic/records.jsonl`:

```text
record.body[locator.start:locator.end] == result.text
sha256(result.text as UTF-8) == result.text_sha256
```

`supporting_edge_ids` explains graph discovery. It is not a factual citation. A `partOfDocument` edge certifies structural membership only; mention and co-mention edges remain candidates.

## Legacy reviewed claims

Schema `1.0` `resolved_entities` exposes reviewed claim metadata: `record_id`, `concept_path`, `record_source_path`, and `claim_evidence`. Preserve those exact fields and verify the reviewed claim plus every PDF-page locator. Do not retrofit paper/page semantics onto schema `2.0` sources.

## Multi-document synthesis

Decompose the question into mechanisms, conditions, contrasts, and negatives. Build an evidence matrix with one row per atomic statement and columns for source ID, record ID, record digest, concept path, locator, text hash, and role in the derivation. Do not draft prose until every required row is present.

For comparisons, preserve the conditions each source actually describes. For exclusions, find explicit source evidence; graph absence is not evidence of absence. If the matrix remains incomplete, abstain or narrow the conclusion.
