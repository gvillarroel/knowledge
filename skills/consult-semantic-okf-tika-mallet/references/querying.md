# Querying Tika and MALLET Semantic OKF

## Mode selection

Use the least expansive mode that answers the discovery need:

- `bm25` for exact terminology, identifiers, filenames, values, and phrases;
- `topic` when the wording is conceptual and related vocabulary may appear in the
  fixed MALLET topics;
- `association` for two-step traversal through local positive-PMI term neighbors;
- `fusion` when recall matters and independent BM25, topic, and association rankings
  should contribute through reciprocal-rank fusion.

All modes use the persisted tokenizer and filters. An unknown or stopword-only query
may validly return no results. Do not switch modes silently: preserve both requested
and effective mode from the result.

## Efficient multi-query grounding

Snapshot validation is intentionally complete and can dominate the cost of a short
query, especially over a cross-filesystem read-only mount. For a question that
needs several independent sources, prefer one `batch-search` process with two to
six distinct broad `--query` values. The snapshot loads and validates once, then
each query uses the same immutable in-memory projection.

Add `--evidence-only` when the consumer needs grounded answer evidence rather than
rank diagnostics. Each compact hit retains rank, a query-focused exact source
substring, its character bounds within the full passage, the full passage length,
and a nested `evidence` object containing the exact source and record identities,
authoritative paths, locator, record hash, and full text hash. Copy the entire
nested object; never retype or derive `concept_path` from `record_id`.
The compact view omits the complete passage, topic weights, component scores, and
expansion diagnostics. `--excerpt-chars` defaults to `1800` and accepts `256`
through `8000`. The identified full passage has already passed snapshot, ledger,
path, locator, and hash validation; do not rerun narrow phrase searches or read
entire concept files unless a required claim remains unsupported by the exact
excerpt.

`batch-search` accepts at most 32 distinct queries. This is a safety ceiling, not a
target. Use two to six broad queries and at most eight hits per query for a
time-bounded multi-source answer. After the required inspection, make this the sole
search invocation: do not spend the answer budget on per-source phrase probes. If
the returned exact excerpts are insufficient, emit the caller's declared null
response rather than launching an unbounded search loop.

For a time-bounded answer, prefer `answer-pack` over raw `batch-search`.
`answer-pack` accepts two through six distinct broad queries, limits each route to
eight hits, fuses duplicate passages by reciprocal rank, retains one passage per
source ID, and emits at most sixteen compact supports. The evaluation workflow uses
three to five queries, `--top-k 6`, `--max-sources 10`, and 1,200-character exact
excerpts. This keeps the complete tool result small enough to reason over directly
without reopening spooled logs or full concept files.

Each support has a stable local ID such as `s01`. Create a draft with top-level
`question_id`, `summary`, and `claims`; each claim contains `statement` and a
nonempty `support_ids` array. `finalize-answer` resolves those IDs, creates
first-use evidence indices, copies the exact grounding objects, validates them
against the snapshot, and writes the final closed answer with no-replace semantics.
Return that final file unchanged.

## Final-answer validation

For the closed JSON answer contract, first assemble a candidate file outside the
bundle. Traverse claims in output order; assign evidence index `0` to the first
hit first used, index `1` to the next previously unused hit, and so on. Reused hits
keep their original index. Then copy each selected hit's nested `evidence` object
in that first-use order.

Run `validate-answer --answer PATH` before emitting the JSON. It rejects duplicate
JSON members, key-order drift in the top-level answer and claims, invalid indices,
incomplete first-use order, duplicate evidence rows, and any evidence object that
is not byte-for-value identical to a validated retrieval document. Do not return a
non-null structured response unless this command reports `status: pass`.

## Filters and diversity

Repeat `--source-id`, `--concept-id`, or `--concept-type` to form a union within one
filter kind. Different kinds combine with logical AND. Filtering happens before
ranking, so excluded documents cannot influence the returned rank set.

The final reranker can favor topic and source diversity and limit repeated evidence
identities. This improves discovery breadth but does not change authority.

## Reading results

Each result contains an authoritative `concept_path`, source and record identities,
an exact record or character-range locator, returned text and its hash, topic
weights, component ranks, and scores. The response also exposes query-topic and
expansion terms so retrieval behavior is inspectable.

After retrieval:

1. Open the returned `concept_path`.
2. Resolve the locator against `semantic/records.jsonl` and confirm the text hash.
3. Check exact metadata in the ledger or use the purpose-appropriate RDF graph for
   schema, lineage, joins, validation, or aggregation.
4. Cite the authoritative path and locator, not the score or topic label.

## Read-only guarantee

Run entry points with `python -B` or set `PYTHONDONTWRITEBYTECODE=1` when even the
copied skill directory must remain byte-identical. Query and deep-validation
temporary files are created outside the bundle and removed afterward. Compare a
full path-and-hash inventory before and after evaluation-critical consultation.
