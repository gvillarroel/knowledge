# Semantic OKF Storage Version Decision Report

## Decision

Keep the file-backed version as the default. Use Turso when a consultation can batch relational joins, grouping, filtering, or traversal into bounded SQL. Keep embeddings only for workloads that truly need tuned paraphrase-oriented discovery. Use Graphify when linked-heading orientation and bounded Markdown-neighborhood traversal are useful.

No version replaces the others across every workload.

## Measured result

The operational comparison passed on the same 31-source, 874-record manifest:

| Measure | File-backed | Embedding-backed | Turso-backed | Graphify-backed |
| --- | ---: | ---: | ---: | ---: |
| Published files | 884 | 888 | 885 | 886 |
| Published bytes | 10,888,503 | 21,808,060 | 52,405,559 | 31,704,281 |
| Mean build time | 16,253.3 ms | 176,755.2 ms | 19,765.4 ms | 50,755.4 ms |
| Deterministic rebuild | pass | pass | pass | pass |
| Authoritative core parity | baseline | pass | pass | pass |

Turso used 4.81 times the storage of the file-backed release. Its build was 21.6% slower in the final measured run. The extra size is the relational projection, not a change to the authoritative concepts, record ledger, or RDF graphs.

Graphify used 2.91 times the file-backed storage and built 212.3% more slowly in the final fresh-process run. It remained 39.5% smaller than Turso but was 45.4% larger than the embedding release. Its two derived artifacts contain 10,797 nodes and 13,289 edges with zero orphans. The deterministic logical graph digest was `e996aec29ca6d0f629edd218574d4bb99b09ac87bca9f536a057c02bfdf6ca95`.

End-to-end consultation results were identical:

| Operation | File-backed median | Turso-backed median | Graphify-backed median |
| --- | ---: | ---: | ---: |
| Exact `(source_id, record_id)` lookup | 276.1 ms | 472.5 ms | 1,442.2 ms |
| Group by source and type | 617.9 ms | 484.3 ms | 1,554.3 ms |

The exact lookup result, all 31 aggregate groups, canonical ledger records, and complete authoritative core matched. The file tree and physical Turso database hash remained unchanged after consultation. The validated Turso logical database digest was `f0f6d96b3c31d2dfa3d71c302f7044e980979241bf843ef3574b82b493be565a`.

The practical implication is to batch related relational work. A separate Turso CLI call for each tiny lookup repeatedly pays the isolated-copy and full-verification boundary; a grouped or joined SQL request can recover the database advantage.

Graphify returned identical exact and aggregate results, but its fresh-process full-core-plus-graph validation made exact lookup 422.4% slower than file-backed and aggregation 151.5% slower. These operations intentionally read the authoritative ledger rather than treating the graph projection as factual storage.

## Retrieval result

The embedding version is the only one with vector and hybrid discovery, but capability did not translate into better retrieval quality on the current 30-question corpus:

| Route | Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Mean time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Legacy lexical | 0.7886 | 0.8611 | 0.8002 | 1.0000 | 2.6 ms |
| New lexical | 0.4850 | 0.9167 | 0.5931 | 1.0000 | 1,240.2 ms |
| Vector | 0.4687 | 0.8278 | 0.5534 | 1.0000 | 6,100.0 ms |
| Hybrid | 0.4273 | 0.8889 | 0.5381 | 1.0000 | 6,254.7 ms |
| Graphify structural | 0.4950 | 0.8306 | 0.5794 | 1.0000 | 2,877.1 ms |

All returned evidence remained valid. The legacy and new timing scopes differ, so latency should not be read as an engine-only comparison. The quality result is still clear: the current embedding plan did not beat legacy lexical recall or nDCG.

Graphify slightly exceeded new lexical, vector, and hybrid Recall@10, but remained below legacy lexical recall and nDCG. Its MRR was above vector retrieval and below the other routes. All 30 questions completed without errors, and all 300 returned records passed complete ledger identity, recomputed record digest, derived paper identity, exact concept locator, byte content, and authoritative-body validation. Its mean latency was 132.0% above new lexical and about 53% below the vector and hybrid routes, subject to the same fresh-process caveat.

## Agent usability result

The expanded Skill Arena run, `eval-Tee-2026-07-17T01:41:47`, completed 20/20 cells without adapter errors:

| Profile | Raw pass rate | Contract adjudication |
| --- | ---: | ---: |
| No skill | 0/4 | 0/4 |
| File-backed | 3/4 | 4/4 |
| Embedding-backed | 3/4 | 4/4 |
| Turso-backed | 4/4 | 4/4 |
| Graphify-backed | 4/4 | 4/4 |

The raw file-backed and embedding-backed scores were each 3/4. Both rejected aggregation answers validated first, stopped on corruption, used authoritative RDF, and prohibited repair, but expressed the prohibition inside lists rather than using one of three literal phrases. The assertion now accepts those semantically equivalent forms; the raw report remains unchanged. Graphify passed all four contracts without adjudication.

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

Choose Graphify-backed when:

- Markdown headings and explicit links provide useful structural cues;
- bounded neighborhood traversal is more important than paraphrase similarity;
- a 31.7 MB release and approximately 50.8-second build are acceptable; and
- every discovered result will still be verified against authoritative OKF concepts.

The baseline evidence is in `operational-report.json` and `operational-report.md`. The Graphify evidence is in `graphify-operational-report.json` and `graphify-operational-report.md`. The live agent matrix is in `last_report.md`.
