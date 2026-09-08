# classical: dataset results

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/consult-semantic-okf-classical/SKILL.md)

[Enterprise evolution of this family](../evolution/e6/README.md)

## GraphRAG generalization (60)

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[All compared skills](../datasets/graphrag-papers-parallel-eval-60-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / Classical association | 99.60% | 100.00% | 100.00% | 664.65 |
| classical / Classical fusion | 99.38% | 100.00% | 100.00% | 671.43 |
| classical / Classical topic | 99.31% | 100.00% | 100.00% | 665.76 |
| classical / Classical BM25 | 98.11% | 98.33% | 100.00% | 665.72 |

## GraphRAG contradictions (40)

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[All compared skills](../datasets/graphrag-papers-contradiction-eval-40-v1.md)

| Skill family / route | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|
| classical / Classical association | 87.50% | 96.25% | 88.33% | 86.83% | 454.25 |
| classical / Classical fusion | 87.50% | 96.25% | 88.33% | 86.22% | 455.04 |
| classical / Classical topic | 87.50% | 96.25% | 85.83% | 84.63% | 450.19 |
| classical / Classical BM25 | 65.00% | 86.25% | 90.00% | 81.93% | 435.86 |

## Software architecture books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/software-architecture-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / Fusion | 92.58% | 97.29% | 97.50% | 1832.07 |
| classical / Association | 92.56% | 97.29% | 97.50% | 1799.42 |
| classical / Topic | 92.56% | 97.29% | 97.50% | 1882.90 |
| classical / BM25 | 84.18% | 83.75% | 95.00% | 1858.98 |

## Data science / AI / ML books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/data-science-ai-ml-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / BM25 | 93.08% | 98.33% | 94.06% | 1766.70 |
| classical / Association | 80.54% | 78.54% | 91.25% | 1594.91 |
| classical / Fusion | 80.54% | 78.54% | 91.25% | 1735.27 |
| classical / Topic | 80.54% | 78.54% | 91.25% | 1727.19 |

## Astro documentation (40)

Published best route for six families; raw pool 100, document deduplication; standalone selected-route P95.

[All compared skills](../datasets/astro-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / association | 83.50% | 88.80% | 91.50% | 1430.10 |

## Endocrine hygiene

Published best route per family; entity-graph and ensemble are unavailable on this historical contract, not zero-score rows.

[All compared skills](../datasets/endocrine-hygiene.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / bm25 | 95.30% | 98.90% | 95.00% | 20.60 |

## EnterpriseRAG reduced corpus (40)

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

[All compared skills](../datasets/enterprise-rag-bench-40-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / BM25 | 58.90% | 64.56% | 60.56% | 38.79 |
| classical / Association | 47.21% | 45.86% | 56.25% | 43.36 |
| classical / Topic | 46.47% | 45.86% | 55.00% | 39.68 |
| classical / Fusion | 43.42% | 42.46% | 56.25% | 41.14 |

## EnterpriseRAG e6 development (40)

Forty exposed development queries on a reference-enriched 985-document corpus. Eight retained primary routes from frozen experimental profiles: five construction and three consultation treatments. Eighteen retained-profile routes are available separately as diagnostics. These maxima do not describe installed defaults, unseen-query quality or official generated-answer accuracy; the terminal decision is separate.

[All compared skills](../datasets/enterprise-rag-e6-development-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / candidate-014 / fusion | 48.21% | 45.86% | 57.50% | 39.30 |

## EnterpriseRAG complete documents: incoming / G2 (40)

Fixed incoming-versus-G2 generator replay: 985 complete documents, 40 exposed questions, eight families, eighteen routes and two versions. Both versions use identical explicit body mappings, plans and consultation code. Embeddings uses pinned MiniLM; Ensemble retains hashing. One query pass, descriptive P95, no generated answers, no independent retrieval gate and no promotion. Legacy lexical and Turso SQL are comparator routes. Do not pool with title-only v1/e6 or the S2 agent-answer contract. Each same-route version pair ties in all relevance metrics; numbered catalog rows enumerate alternatives and preserve these ties.

[All compared skills](../datasets/enterprise-rag-generator-g2-fulltext-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| classical / G2 / BM25 | 97.85% | 98.59% | 98.75% | 256.65 |
| classical / Incoming / BM25 | 97.85% | 98.59% | 98.75% | 252.10 |
| classical / G2 / Association | 90.33% | 88.64% | 98.75% | 251.54 |
| classical / G2 / Fusion | 90.33% | 88.64% | 98.75% | 252.28 |
| classical / G2 / Topic | 90.33% | 88.64% | 98.75% | 251.49 |
| classical / Incoming / Association | 90.33% | 88.64% | 98.75% | 248.69 |
| classical / Incoming / Fusion | 90.33% | 88.64% | 98.75% | 247.81 |
| classical / Incoming / Topic | 90.33% | 88.64% | 98.75% | 249.50 |

[Cost, time, quality, and measurement limits](../cta/README.md)
