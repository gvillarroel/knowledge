# Frozen Tantivy Consumer Contract

Read the active consultation freeze receipt before changing this builder. A
builder evaluation is attributable only when the live
`consult-semantic-okf-tantivy` tree matches both recorded digests.

The frozen consumer validates the authoritative core and the closed
`classical/` artifact set before creating an in-memory Tantivy index. It
requires:

- `classical/index.json`, `documents.jsonl`, `lexicon.json`,
  `associations.jsonl`, `topics.json`, and `build-report.json`;
- exact artifact hashes, sizes, counts, algorithm identifiers, plan hash, and
  authoritative core-tree binding;
- exact record or character-range locators whose text and SHA-256 resolve
  against `semantic/records.jsonl`;
- a nonempty unigram vocabulary in `lexicon.json`;
- positive integer `plan.reranking.candidate_pool` and
  `plan.reranking.max_per_evidence_identity` values; and
- stable `paper_id`, with `source_id` as the fallback evidence identity.

The consumer preserves explicit Tantivy query syntax. Syntax-free natural text
is case-folded, tokenized to ASCII alphanumeric terms, and intersected with the
persisted unigram vocabulary. It retrieves the plan-bounded native candidate
pool and retains at most the configured number of passages for each paper or
source identity without changing native BM25 scores.

Builder candidates may change deterministic passage derivation or plan-bound
statistics only when all authoritative locators, hashes, schema members, and
validation rules remain exact. Never patch the consumer to accommodate a
candidate.
