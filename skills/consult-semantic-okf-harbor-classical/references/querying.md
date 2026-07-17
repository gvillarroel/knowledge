# Querying Classical Semantic OKF

## Compact Harbor support path

Prefer `harbor_answer.py prepare` for an answer task. It invokes the unchanged `fusion` implementation on the complete question and on a bounded set of punctuation- and conjunction-derived facets. It then protects the leading full-query records, allocates one unseen record to each remaining facet where possible, fills the bounded remainder by reciprocal-rank evidence, and deduplicates on exact `(source_id, record_id)` identity. For a one-term facet, the deficit allocator prefers a returned guide over a returned error page before using route rank; this prevents a narrow noun such as `session` from being satisfied only by a troubleshooting fragment. Full-query protection still preserves a highly ranked error record when the complete question requires it.

The support pack is derived and non-authoritative. Each support projects a passage hit to its authoritative parent ledger record, binds the record locator and full-body text hash, and exposes at most the configured number of hash-bound snippets. Snippets are selection aids. Verify that the selected snippet entails the draft statement; do not infer a missing predicate from a rank or filename.

The pack's parameter hash covers the normalized question, family, algorithm, bounds, and validated snapshot hashes. `finalize` reruns the same searches and requires byte-equivalent canonical pack content before accepting a support ID. This intentionally spends deterministic local computation to prevent a stale or edited pack from becoming evidence.

Keep candidate selection separate from final evidence. A pack may contain unused candidates. The draft selects only directly entailing support IDs; the compiler emits only those records and orders them by first claim use. Do not manually copy the pack's candidates into a final `evidence` array.

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
