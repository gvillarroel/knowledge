# Retrospective QEC expert evaluation

Status: **PASS**. The integrated supervised-profile builder produced the top-ranked treatment on the frozen 40-question workload.

## Primary results

| Rank | Treatment | Recall@10 | MRR@10 | nDCG@10 | Exact evidence | Representative P95 (ms) |
|---:|---|---:|---:|---:|---:|---:|
| 1 | retrospective-supervised-ngram | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 34.006 |
| 2 | baseline-lexical | 74.5833% | 27.4018% | 36.6713% | 100.0000% | 123.550 |

## Candidate replicates

| Replicate | Recall@10 | MRR@10 | nDCG@10 | Exact evidence | P95 (ms) |
|---:|---:|---:|---:|---:|---:|
| 1 | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 32.033 |
| 2 | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 36.305 |
| 3 | 100.0000% | 100.0000% | 100.0000% | 100.0000% | 34.006 |

## Interpretation

Every retained result resolves to the exact immutable ledger record and concept path. Ranking was stable across all replicates, and every quality target reached 100% at Top-10.

## Promotion boundary

All 40 questions and their reviewed qrels were exposed to profile construction. The result measures fixed-workload specialization and cannot support promotion or unseen-query generalization.
