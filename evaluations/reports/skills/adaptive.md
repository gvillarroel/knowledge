# adaptive: dataset results

[Adaptive generation 7](../evolution/e14/adaptive-generation-007-001/README.md): `{"bm25.title_weight": 8.0}` scored **47.65**, retaining **66.21**. The `title-weight` mechanism records **2 / 3 consecutive evaluable misses** and the family **26 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-007-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-007-001/cta.md) preserve this observation.

[Adaptive generation 6](../evolution/e14/adaptive-generation-006-001/README.md): `{"bm25.title_weight": 4.0}` scored **54.79**, retaining **66.21**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **25 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-006-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-006-001/cta.md) preserve this observation.

[Adaptive generation 5](../evolution/e14/adaptive-generation-005-001/README.md): `{"bm25.k1": 2.0}` scored **65.61**, retaining **66.21**. The `bm25-saturation` mechanism records **2 / 3 consecutive evaluable misses** and the family **24 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-005-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-005-001/cta.md) preserve this observation.

[Adaptive generation 4](../evolution/e14/adaptive-generation-004-001/README.md): `{"bm25.k1": 0.6}` scored **65.52**, retaining **66.21**. The `bm25-saturation` mechanism records **1 / 3 consecutive evaluable misses** and the family **23 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-004-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-004-001/cta.md) preserve this observation.

[Adaptive reaches three normalization misses](../evolution/e14/adaptive-generation-003-001/README.md): construction `bm25.b=0.5` scored **65.78**, below retained **66.21**. This is the third consecutive unique evaluable miss in the mechanism, with **22 / 100 claims**. Its other search opportunities remain open. [Paired applications/categories](../evolution/e14/adaptive-generation-003-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-003-001/cta.md) preserve the measured result. The retained six-family ranking is unchanged.

[Latest E14 observation](../evolution/e14/turso-003-adaptive-002-observations-001/README.md): construction-plan `bm25.b=0.0` scored **62.31**, below retained **66.21**. This is the second consecutive length-normalization miss and 21 / 100 cumulative claims. [Paired groups](../evolution/e14/turso-003-adaptive-002-observations-001/groups.md#adaptive) and [CTA](../evolution/e14/turso-003-adaptive-002-observations-001/cta.md).

[Earlier E14 pending variant](../evolution/e14/generation-001-pending-variants-001/README.md): construction-plan `bm25.b=0.25` scored 64.53 versus retained 66.21. This is one evaluable miss, with zero new proposal charges. [Application/category comparison](../evolution/e14/generation-001-pending-variants-001/groups.md#adaptive) and [CTA](../evolution/e14/generation-001-pending-variants-001/cta.md).

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/consult-semantic-okf-adaptive/SKILL.md)

[Stratified Enterprise evolution E7 and this family's opportunity status](../evolution/e7/README.md)

[Current EnterpriseRAG family evidence and native outcomes](../../../docs/enterprise-family-report-index.md)

[Current E14 starting qualification: 60.04 reference and 66.21 retained nDCG@10](../evolution/e14/adaptive-starting-qualified-001/README.md) · [Applications and question categories](../evolution/e14/adaptive-starting-qualified-001/groups.md) · [CTA](../evolution/e14/adaptive-starting-qualified-001/cta.md)

[Earlier Enterprise evolution E6](../evolution/e6/README.md)

## GraphRAG generalization (60)

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[All compared skills](../datasets/graphrag-papers-parallel-eval-60-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / Adaptive fusion | 99.38% | 100.00% | 100.00% | 2405.80 |

## GraphRAG contradictions (40)

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[All compared skills](../datasets/graphrag-papers-contradiction-eval-40-v1.md)

| Skill family / route | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|
| adaptive / Adaptive fusion | 87.50% | 96.25% | 88.33% | 86.22% | 1995.64 |

## Software architecture books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/software-architecture-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / Adaptive fusion | 85.61% | 95.21% | 90.50% | 4206.12 |

## Data science / AI / ML books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/data-science-ai-ml-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / Adaptive fusion | 91.78% | 99.17% | 93.23% | 5359.04 |

## Astro documentation (40)

Published best route for six families; raw pool 100, document deduplication; standalone selected-route P95.

[All compared skills](../datasets/astro-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / association | 83.50% | 88.80% | 91.50% | 1443.60 |

## Endocrine hygiene

Published best route per family; entity-graph and ensemble are unavailable on this historical contract, not zero-score rows.

[All compared skills](../datasets/endocrine-hygiene.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / bm25 | 95.30% | 98.90% | 95.00% | 26.30 |

## EnterpriseRAG reduced corpus (40)

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

[All compared skills](../datasets/enterprise-rag-bench-40-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / Adaptive fusion | 50.34% | 59.00% | 57.47% | 1190.77 |

## EnterpriseRAG e6 development (40)

Forty exposed development queries on a reference-enriched 985-document corpus. Eight retained primary routes from frozen experimental profiles: five construction and three consultation treatments. Eighteen retained-profile routes are available separately as diagnostics. These maxima do not describe installed defaults, unseen-query quality or official generated-answer accuracy; the terminal decision is separate.

[All compared skills](../datasets/enterprise-rag-e6-development-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / candidate-013 / adaptive | 58.62% | 62.20% | 60.36% | 1305.60 |

## EnterpriseRAG complete documents: incoming / G2 (40)

Fixed incoming-versus-G2 generator replay: 985 complete documents, 40 exposed questions, eight families, eighteen routes and two versions. Both versions use identical explicit body mappings, plans and consultation code. Embeddings uses pinned MiniLM; Ensemble retains hashing. One query pass, descriptive P95, no generated answers, no independent retrieval gate and no promotion. Legacy lexical and Turso SQL are comparator routes. Do not pool with title-only v1/e6 or the S2 agent-answer contract. Each same-route version pair ties in all relevance metrics; numbered catalog rows enumerate alternatives and preserve these ties.

[All compared skills](../datasets/enterprise-rag-generator-g2-fulltext-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| adaptive / G2 / Adaptive fusion | 95.12% | 97.48% | 98.75% | 1608.32 |
| adaptive / Incoming / Adaptive fusion | 95.12% | 97.48% | 98.75% | 1590.00 |

[Cost, time, quality, and measurement limits](../cta/README.md)
