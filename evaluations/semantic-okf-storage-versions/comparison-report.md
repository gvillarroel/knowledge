# Semantic OKF Storage Version Decision Report

## Decision

Keep the file-backed version as the default. Use the Turso-backed version when a consultation can batch relational joins, grouping, filtering, or traversal into bounded SQL. Keep the embedding-backed version only for workloads that truly need paraphrase-oriented candidate discovery, and retune its retrieval plan before assuming that vector or hybrid search improves quality.

No version replaces the others across every workload.

## Measured result

The operational comparison passed on the same 31-source, 874-record manifest:

| Measure | File-backed | Embedding-backed | Turso-backed |
| --- | ---: | ---: | ---: |
| Published files | 884 | 888 | 885 |
| Published bytes | 10,888,503 | 21,808,060 | 52,405,559 |
| Mean build time | 16,253.3 ms | 176,755.2 ms | 19,765.4 ms |
| Deterministic rebuild | pass | pass | pass |
| Authoritative core parity | baseline | pass | pass |

Turso used 4.81 times the storage of the file-backed release. Its build was 21.6% slower in the final measured run. The extra size is the relational projection, not a change to the authoritative concepts, record ledger, or RDF graphs.

End-to-end consultation results were identical:

| Operation | File-backed median | Turso-backed median | Difference |
| --- | ---: | ---: | ---: |
| Exact `(source_id, record_id)` lookup | 276.1 ms | 472.5 ms | Turso 71.1% slower |
| Group by source and type | 617.9 ms | 484.3 ms | Turso 21.6% faster |

The exact lookup result, all 31 aggregate groups, canonical ledger records, and complete authoritative core matched. The file tree and physical Turso database hash remained unchanged after consultation. The validated Turso logical database digest was `f0f6d96b3c31d2dfa3d71c302f7044e980979241bf843ef3574b82b493be565a`.

The practical implication is to batch related relational work. A separate Turso CLI call for each tiny lookup repeatedly pays the isolated-copy and full-verification boundary; a grouped or joined SQL request can recover the database advantage.

## Retrieval result

The embedding version is the only one with vector and hybrid discovery, but capability did not translate into better retrieval quality on the current 30-question corpus:

| Route | Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Mean time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Legacy lexical | 0.7886 | 0.8611 | 0.8002 | 1.0000 | 2.6 ms |
| New lexical | 0.4850 | 0.9167 | 0.5931 | 1.0000 | 1,240.2 ms |
| Vector | 0.4687 | 0.8278 | 0.5534 | 1.0000 | 6,100.0 ms |
| Hybrid | 0.4273 | 0.8889 | 0.5381 | 1.0000 | 6,254.7 ms |

All returned evidence remained valid. The legacy and new timing scopes differ, so latency should not be read as an engine-only comparison. The quality result is still clear: the current embedding plan did not beat legacy lexical recall or nDCG.

## Agent usability result

The closing Skill Arena run, `eval-Uch-2026-07-14T11:02:11`, completed 16/16 cells without adapter errors:

| Profile | Raw pass rate | Contract adjudication |
| --- | ---: | ---: |
| No skill | 0/4 | 0/4 |
| File-backed | 4/4 | 4/4 |
| Embedding-backed | 4/4 | 4/4 |
| Turso-backed | 2/4 | 4/4 |

Both raw Turso failures were evaluator false negatives, not missing workflow steps. The conceptual-discovery answer used `knowledge.db`, `records --contains`, bounded SQL fallback, provenance, and authoritative concept verification. The aggregation answer validated every release layer and ran the correct grouped `SELECT` over accepted normalized records. The assertions had required incidental helper spelling and `rdf_statements`, respectively. The final config accepts the supported semantic contracts and passes schema, prompt-design, and dry-run validation; the raw report remains unchanged.

Because each cell has one model sample, this matrix establishes that every package can guide the requested tasks but does not establish a statistically significant ranking between instruction sets.

## Selection guide

Choose file-backed when:

- minimum artifact size and dependencies matter;
- direct Markdown, JSONL, or SPARQL access is sufficient;
- most requests are isolated exact lookups; or
- maximum portability is more important than a SQL surface.

Choose Turso-backed when:

- agents need bounded SQL, joins, grouping, or typed attribute filters;
- one query can batch enough structured work to amortize verification;
- the additional 41.5 MB database projection is acceptable; and
- the Rust Turso runtime can be installed and pinned.

Choose embedding-backed when:

- paraphrases and conceptual similarity are necessary discovery inputs;
- the local model runtime and longer build are acceptable; and
- a revised retrieval plan demonstrates a measurable quality gain on the target questions.

The detailed raw evidence is in `operational-report.json`, the concise operational result is in `operational-report.md`, and the live agent matrix is in `last_report.md`.
