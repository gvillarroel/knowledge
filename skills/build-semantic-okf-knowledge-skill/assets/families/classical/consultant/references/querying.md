# Querying Classical Semantic OKF

## Integrity before ranking

Ordinary inspection verifies the closed file set, source selection, authoritative bindings, locators, token counts, structural statistics, artifact hashes, and build report. Run `inspect --deep-validation` once for a newly supplied, benchmark, or release-candidate snapshot. Deep validation independently reconstructs the selected passages, BM25 lexicon, windowed PPMI graph, deterministic topic communities, and document-topic weights; it performs no writes. Repeated searches may use ordinary validation after the same immutable snapshot hash has passed deep validation.

## Layer selection

Use `semantic/records.jsonl` for exact identifiers, types, attributes, counts, and paths. Use classical search for discovery. Open returned concept Markdown for readable evidence. Use `data.ttl` for accepted domain joins or aggregation, `ontology.ttl` only for schema, and `provenance.ttl` only for lineage. Shapes and validation reports describe contracts and conformance, not domain facts.

## Mode semantics

- `bm25` uses only persisted title/body Bag-of-Words, field lengths, IDF, and plan weights.
- `topic` adds topic-community terms, document-topic cosine similarity, and topic/source MMR.
- `association` propagates query mass twice over normalized PPMI edges, adds the strongest new terms, then applies topic/source MMR.
- `fusion` combines BM25, topic, and association rank positions with reciprocal-rank fusion before MMR. It never adds incomparable raw scores.

Review `expansion.association_terms`, `expansion.topic_terms`, and `expansion.query_topics`. Expansion is corpus-derived and can amplify ambiguity. A result remains usable only when its authoritative locator supports the intended claim.

For multi-paper synthesis, retrieve a candidate pool deeper than the final evidence count and prefer `topic`, `association`, or `fusion`, which actively penalize repeated topical and paper/source evidence. For exact names, IDs, formulas, or rare phrases, prefer `bm25`.
