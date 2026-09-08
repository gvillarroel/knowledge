# EnterpriseRAG-Bench reduced-corpus evaluation

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | entity-graph / Lexical | 59.40% | 63.73% | 60.78% | 83.17 ms |
| 2 | embeddings / Lexical | 59.07% | 61.86% | 61.50% | 10.28 ms |
| 3 | classical / BM25 | 58.90% | 64.56% | 60.56% | 38.79 ms |
| 4 | legacy / Lexical | 57.50% | 61.92% | 59.86% | 3.57 ms |
| 5 | ensemble / Quality | 55.38% | 59.00% | 60.36% | 1315.92 ms |
| 6 | ensemble / Fast | 52.29% | 59.00% | 59.07% | 1224.41 ms |
| 7 | embeddings / Hybrid | 51.47% | 59.91% | 53.97% | 47.66 ms |
| 8 | adaptive / Adaptive fusion | 50.34% | 59.00% | 57.47% | 1190.77 ms |
| 9 | ensemble / Robust | 50.34% | 59.00% | 57.47% | 1141.87 ms |
| 10 | classical / Association | 47.21% | 45.86% | 56.25% | 43.36 ms |
| 11 | entity-graph / Fusion | 46.73% | 58.04% | 47.33% | 92.52 ms |
| 12 | classical / Topic | 46.47% | 45.86% | 55.00% | 39.68 ms |
| 13 | entity-graph / Entity | 45.25% | 56.58% | 46.67% | 82.75 ms |
| 14 | classical / Fusion | 43.42% | 42.46% | 56.25% | 41.14 ms |
| 15 | entity-graph / Traversal | 43.27% | 50.33% | 46.04% | 82.57 ms |
| 16 | turso / Lexical SQL comparator | 40.32% | 49.87% | 40.85% | 52.04 ms |
| 17 | embeddings / Vector | 32.64% | 36.92% | 37.80% | 34.76 ms |
| 18 | graphify / Graph search | 13.63% | 17.37% | 20.42% | 128.30 ms |

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

All eight unchanged build/consult families passed two builds and independent validation. All 18 routes completed 40 questions in three repetitions: 2,160 query executions. Authoritative record identities and hashes were checked before scoring.

## Category diagnostics

Each category contains five selected questions. Highest observed nDCG@10 is descriptive at this small denominator; ties are retained and categories are not independent organization-level samples.

| Category | Questions | Highest observed route(s) | nDCG@10 |
|---|---:|---|---:|
| basic | 5 | ensemble-quality | 46.67% |
| completeness | 5 | embeddings-lexical | 84.79% |
| conflicting info | 5 | classical-bm25 | 81.91% |
| constrained | 5 | embeddings-lexical | 80.00% |
| intra document reasoning | 5 | adaptive-fusion; classical-association; classical-bm25; classical-fusion; classical-topic; ensemble-fast; ensemble-quality; ensemble-robust; entity-graph-lexical; legacy-lexical | 40.00% |
| miscellaneous | 5 | classical-bm25; embeddings-lexical; ensemble-fast; ensemble-quality; entity-graph-lexical; legacy-lexical | 60.00% |
| project related | 5 | entity-graph-lexical | 86.75% |
| semantic | 5 | embeddings-hybrid; embeddings-lexical; embeddings-vector | 20.00% |

## Cost, time, and integrity

Provider cost: **USD 0.00**. Model calls: **0**. LLM tokens: **0**. Local machine cost and generated-answer correctness were not measured. Embeddings use deterministic 384-dimensional hashing; Turso uses the actual pinned Turso engine.

P95 excludes process initialization and uses repeated-query caches within a fresh process per route. The shared workstation also ran repository validation during part of this measurement. Treat latency as local diagnostic evidence, not a controlled hardware comparison or a speed winner.

Every family rebuilt byte-identically, including the Turso database. The independent Turso validator also checked its logical database contents. Input and executable hashes were checked before and after scoring.

## Dataset and interpretation

The pinned archive contains 511,962 document files. This derived dataset contains 985 documents: 85 reference documents and 900 deterministic distractors. Forty questions cover eight grounded categories. The full 500-question bank and complete archive remain local. Four colliding document IDs are quarantined; one repeated upstream qrel entry has set semantics. No ambiguous ID was required by the selected questions.

The reference-enriched corpus is not the official full-corpus Onyx benchmark. High-level and information-not-found categories require separate answer/abstention evaluation. No skill was evolved, no gold answer entered the builder input, and no promotion is claimed.

[Aggregate run details](comparison.json) · [Validated table contract](final-report.comparison.json) · [Dataset guide](../../../../docs/evaluation-datasets-and-reports.md) · [Cross-dataset hub](../../../reports/README.md)
