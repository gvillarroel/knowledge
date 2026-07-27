# Querying with Tantivy BM25

## Integrity before ranking

Inspection verifies the closed classical artifact set, authoritative core tree, classical plan digest, artifact hashes and counts, passing build report, document identities, concept paths, exact record or character-range locators, and text hashes. A corrupt or stale input stops consultation; there is no fallback scan.

## Query semantics

Search uses Tantivy's query parser across `title` and `body`. Natural terms are disjoined by default. Use quotes for a phrase, `AND` or `OR` for Boolean intent, parentheses for grouping, and `title:` or `body:` for explicit field targeting. Regular expressions are disabled.

When the input contains no quoted phrase, field selector, grouping, or
uppercase Boolean operator, the consultant case-folds ASCII alphanumeric terms
and keeps only terms present in the validated persisted classical unigram
lexicon. Each retained original receives weight `3.0`. Deterministic `s`, `es`,
`ies`, `ing`, and `ed` transformations may add at most two variants that also
exist in that immutable unigram lexicon, each at weight `0.35`. This bounded
expansion handles common English inflections without external synonyms, qrels,
or corpus mutation. Any explicit Tantivy syntax is preserved byte-for-byte.
Inspect `parsed_query` and `engine.query_normalization` to verify the choice.

The classical plan's title and body weights are applied as field boosts. Returned `score` values are Tantivy BM25 discovery scores and are meaningful only within one query over one filtered index. Do not compare scores across snapshots or filter sets and do not treat them as evidence.

Tantivy first returns the plan-bounded native candidate pool in score order.
Result selection then keeps no more than
`plan.reranking.max_per_evidence_identity` passages for one `paper_id`, falling
back to `source_id` when a paper identity is absent. This deterministic cap
does not change a BM25 score; it prevents repeated passages from consuming the
entire requested evidence budget. Inspect `candidate_pool`, `identity_cap`,
`identity_policy`, and `returned_identities` in the engine metadata.

## Filters and evidence

Apply `source_id`, `concept_id`, and `concept_type` filters before creating the in-memory index. Repeating one filter kind forms a union; different kinds combine with logical AND. The response reports the number of indexed passages so callers can verify this boundary.

Every result retains `source_id`, `record_id`, `record_sha256`, `concept_id`, `concept_type`, `concept_path`, `source_path`, `paper_id`, `ordinal`, `locator`, `text`, and `text_sha256`. Resolve the locator against the matching authoritative ledger body and open the exact concept path before using a result in an answer.
