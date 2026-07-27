# Querying Tika/MALLET Semantic OKF with Tantivy

## Mode selection

Use the least expansive mode that fits the discovery task:

- `tantivy` for exact terms, identifiers, filenames, values, phrases, fielded
  queries, or explicit Boolean syntax;
- `topic` when conceptual wording needs fixed MALLET topic vocabulary;
- `association` for two-step propagation through local positive-PMI neighbors;
- `fusion` when recall matters and native Tantivy, association, and topic rankings
  should contribute through reciprocal-rank fusion.

All lexical routes execute through Tantivy `0.26.0` over one pathless in-memory
index. The topic route also blends the expanded Tantivy score with the persisted
MALLET document-topic vector. Do not silently switch modes.

## Query parsing and expansion

Quoted phrases, `title:` or `body:` selectors, parentheses, and uppercase `AND`,
`OR`, or `NOT` preserve explicit Tantivy syntax. Regex queries are disabled.

Syntax-free text is tokenized as ASCII alphanumerics and bounded to persisted
unigram vocabulary when possible. The result reports both `query` and
`parsed_query`. Topic and association terms come only from the validated
MALLET/PPMI projection and are added as safe lexical terms. Inspect
`engine.lexical_queries` to see the exact text parsed for every component.

Tantivy scores and expansion weights are not calibrated probabilities. Use scores
and component ranks only to inspect discovery behavior.

## Filters and indexing

Repeat `--source-id`, `--concept-id`, or `--concept-type` to form a union within a
filter kind. Different kinds combine with logical AND. Filtering happens before
the Tantivy schema and index are created, so excluded passages cannot affect
statistics or ranking. The index exists only in process memory and is discarded
when the command exits.

The native route retains Tantivy score order while enforcing the snapshot plan's
evidence-identity cap. Topic, association, and fusion routes use the plan's bounded
diversity reranker. Neither policy changes evidence authority.

## Efficient multi-query grounding

Snapshot validation can dominate a short query. Prefer one `batch-search` process
for two to six broad queries so the immutable projection loads once.

Add `--evidence-only` for a compact exact-evidence view. Each hit retains the
engine disclosure, query-focused exact substring, its bounds, full passage length,
and a nested `evidence` object with exact source and record identities, paths,
locator, record hash, and passage hash. Copy the nested object; never derive a
concept path from a record ID.

For a bounded answer, prefer `answer-pack` with three to five broad queries,
`--top-k 6`, `--max-sources 10`, and the default 1,200-character excerpts. It
fuses duplicate passages, retains one passage per source ID, and assigns support
IDs such as `s01`.

Create a draft with exactly `question_id`, `summary`, and `claims`; each claim has
`statement` and a nonempty `support_ids` array. Run `finalize-answer` to copy exact
evidence, assign first-use indices, validate the complete response, and write it to
a new path outside the bundle.

## Final-answer validation

Use `validate-answer --answer PATH` for a manually assembled response. It rejects:

- duplicate JSON members or key-order drift;
- empty claims, invalid indices, or incomplete first-use order;
- duplicate evidence rows; and
- any evidence object that is not value-identical to a validated retrieval passage.

Do not return a non-null structured answer unless validation reports `status:
pass`.

## Reading results

Each diagnostic result includes authoritative identities and locators, exact text
and hash, native and derived scores, component ranks, topic weights, expansions,
Tantivy runtime details, index hashes, and filters.

After retrieval:

1. Open the returned `concept_path`.
2. Resolve its locator against `semantic/records.jsonl`.
3. Confirm the selected text and SHA-256.
4. Use the ledger for metadata or a purpose-selected RDF graph for joins,
   aggregation, schema, provenance, shapes, or validation.
5. Cite the authoritative path and locator rather than a score or topic.

## Read-only guarantee

Run entry points with `python -B` or set `PYTHONDONTWRITEBYTECODE=1` when the copied
skill directory must remain byte-identical. Query and deep-validation scratch
state stays outside the bundle and is removed. Compare a complete path-and-hash
inventory before and after evaluation-critical consultation.
