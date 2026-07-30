# Offline Methodology Ablation 01

## Outcome

- KM-004 chunking: **strong-support** (registered rule: true).
- KM-005 cross-domain baselines: **partial-support** (Pareto frontier: 14 treatments).
- KM-006 uncertainty: **support** (maximum Recall@10 interval width: 0.1625).

All results are retrospective and promotion-ineligible because all qrels were exposed before this run.

## Point winners by domain

| Dataset | Treatment | Recall@10 | MRR@10 | nDCG@10 | Median ms |
|---|---|---:|---:|---:|---:|
| `graphrag-papers-40` | `fixed-512::rrf-hybrid` | 0.8245 | 0.8667 | 0.7870 | 11.373 |
| `quantum-error-correction-papers-40` | `fixed-128::tfidf-char3` | 1.0000 | 0.9521 | 0.9454 | 30.404 |

## Chunking comparisons

| Dataset | Retriever | Best non-document | Recall delta vs document | 95% interval |
|---|---|---|---:|---:|
| `graphrag-papers-40` | `bm25-word` | `fixed-512::bm25-word` | +0.0130 | [-0.0413, +0.0664] |
| `graphrag-papers-40` | `tfidf-char3` | `fixed-128::tfidf-char3` | +0.1363 | [+0.0858, +0.1902] |
| `graphrag-papers-40` | `rrf-hybrid` | `fixed-512::rrf-hybrid` | +0.0396 | [-0.0033, +0.0804] |
| `quantum-error-correction-papers-40` | `bm25-word` | `fixed-512::bm25-word` | +0.0083 | [-0.0292, +0.0458] |
| `quantum-error-correction-papers-40` | `tfidf-char3` | `fixed-128::tfidf-char3` | +0.1375 | [+0.0625, +0.2208] |
| `quantum-error-correction-papers-40` | `rrf-hybrid` | `fixed-512::rrf-hybrid` | +0.0167 | [+0.0000, +0.0500] |

## Cross-domain Pareto frontier

- `document::bm25-word`
- `document::rrf-hybrid`
- `fixed-128::rrf-hybrid`
- `fixed-128::tfidf-char3`
- `fixed-256::tfidf-char3`
- `fixed-512::bm25-word`
- `fixed-512::rrf-hybrid`
- `fixed-512::tfidf-char3`
- `hierarchical-page::bm25-word`
- `hierarchical-page::rrf-hybrid`
- `hierarchical-page::tfidf-char3`
- `page::bm25-word`
- `page::rrf-hybrid`
- `page::tfidf-char3`

## Interpretation

A supported rule means the preregistered signal was observed on these two exposed paper workloads. It does not establish unseen-query performance or answer quality. Document-level qrels cannot show that a retrieved chunk contains the required claim, and runtime is machine-specific.

## Branch decision

Continue KM-004: the character-trigram treatment gained more than 0.13 Recall@10 from chunking in both domains, with paired intervals excluding zero. Do not adopt one global chunk size: the GraphRAG and QEC point winners use different treatments.

Continue KM-005: domain winners differ and multiple treatments remain non-dominated after total hybrid query cost is counted. A single retrospective leaderboard is not enough to select a repository-wide default.

Continue KM-006: the widest Recall@10 interval is materially larger than the registered 0.05 threshold. Future comparisons should carry uncertainty rather than use point ranks alone.

Do not promote any treatment from this retrospective study. The next useful evidence is claim-level answer review, calibrated judges, and a genuinely new transfer cohort.
