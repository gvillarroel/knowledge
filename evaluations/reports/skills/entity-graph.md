# entity-graph: dataset results

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/consult-semantic-okf-entity-graph/SKILL.md)

[Stratified Enterprise evolution E7 and this family's opportunity status](../evolution/e7/README.md)

[Current EnterpriseRAG family evidence and native outcomes](../../../docs/enterprise-family-report-index.md)

[Earlier Enterprise evolution E6](../evolution/e6/README.md)

## GraphRAG generalization (60)

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[All compared skills](../datasets/graphrag-papers-parallel-eval-60-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / Entity Graph lexical | 92.70% | 98.89% | 92.55% | 485.78 |
| entity-graph / Entity Graph fusion | 86.05% | 97.78% | 86.81% | 478.67 |
| entity-graph / Entity Graph entity | 81.77% | 95.83% | 82.39% | 471.66 |
| entity-graph / Entity Graph traversal | 75.89% | 93.89% | 75.22% | 478.05 |

## GraphRAG contradictions (40)

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[All compared skills](../datasets/graphrag-papers-contradiction-eval-40-v1.md)

| Skill family / route | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|
| entity-graph / Entity Graph lexical | 67.50% | 88.12% | 70.44% | 68.19% | 497.28 |
| entity-graph / Entity Graph fusion | 65.00% | 87.92% | 66.46% | 65.27% | 505.72 |
| entity-graph / Entity Graph traversal | 62.50% | 86.88% | 63.47% | 63.48% | 501.14 |
| entity-graph / Entity Graph entity | 60.00% | 86.25% | 66.42% | 64.93% | 493.58 |

## Software architecture books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/software-architecture-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / Lexical | 88.98% | 98.33% | 89.25% | 5473.10 |
| entity-graph / Fusion | 83.50% | 97.50% | 81.33% | 5612.20 |
| entity-graph / Entity | 81.76% | 93.54% | 81.15% | 4262.95 |
| entity-graph / Traversal | 80.30% | 92.92% | 80.92% | 4336.46 |

## Data science / AI / ML books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/data-science-ai-ml-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / Lexical | 90.31% | 99.17% | 88.75% | 14174.95 |
| entity-graph / Fusion | 85.83% | 97.50% | 86.88% | 14003.99 |
| entity-graph / Entity | 80.29% | 96.67% | 78.42% | 13957.18 |
| entity-graph / Traversal | 51.20% | 79.58% | 43.55% | 11329.79 |

## Astro documentation (40)

Published best route for six families; raw pool 100, document deduplication; standalone selected-route P95.

[All compared skills](../datasets/astro-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / entity | 70.60% | 88.10% | 72.90% | 1626.60 |

## Endocrine hygiene

Published best route per family; entity-graph and ensemble are unavailable on this historical contract, not zero-score rows.

[All compared skills](../datasets/endocrine-hygiene.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / N/A | N/A | N/A | N/A | N/A |

## EnterpriseRAG reduced corpus (40)

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

[All compared skills](../datasets/enterprise-rag-bench-40-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / Lexical | 59.40% | 63.73% | 60.78% | 83.17 |
| entity-graph / Fusion | 46.73% | 58.04% | 47.33% | 92.52 |
| entity-graph / Entity | 45.25% | 56.58% | 46.67% | 82.75 |
| entity-graph / Traversal | 43.27% | 50.33% | 46.04% | 82.57 |

## EnterpriseRAG e6 development (40)

Forty exposed development queries on a reference-enriched 985-document corpus. Eight retained primary routes from frozen experimental profiles: five construction and three consultation treatments. Eighteen retained-profile routes are available separately as diagnostics. These maxima do not describe installed defaults, unseen-query quality or official generated-answer accuracy; the terminal decision is separate.

[All compared skills](../datasets/enterprise-rag-e6-development-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / candidate-010 / fusion | 48.19% | 58.59% | 48.34% | 39.53 |

## EnterpriseRAG complete documents: incoming / G2 (40)

Fixed incoming-versus-G2 generator replay: 985 complete documents, 40 exposed questions, eight families, eighteen routes and two versions. Both versions use identical explicit body mappings, plans and consultation code. Embeddings uses pinned MiniLM; Ensemble retains hashing. One query pass, descriptive P95, no generated answers, no independent retrieval gate and no promotion. Legacy lexical and Turso SQL are comparator routes. Do not pool with title-only v1/e6 or the S2 agent-answer contract. Each same-route version pair ties in all relevance metrics; numbered catalog rows enumerate alternatives and preserve these ties.

[All compared skills](../datasets/enterprise-rag-generator-g2-fulltext-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| entity-graph / G2 / Lexical | 95.43% | 96.01% | 97.50% | 770.35 |
| entity-graph / Incoming / Lexical | 95.43% | 96.01% | 97.50% | 762.10 |
| entity-graph / G2 / Fusion | 77.02% | 82.67% | 79.69% | 776.15 |
| entity-graph / Incoming / Fusion | 77.02% | 82.67% | 79.69% | 766.50 |
| entity-graph / G2 / Entity | 75.19% | 81.30% | 77.50% | 773.58 |
| entity-graph / Incoming / Entity | 75.19% | 81.30% | 77.50% | 771.29 |
| entity-graph / G2 / Traversal | 56.17% | 69.51% | 56.52% | 769.98 |
| entity-graph / Incoming / Traversal | 56.17% | 69.51% | 56.52% | 764.75 |

[Cost, time, quality, and measurement limits](../cta/README.md)
