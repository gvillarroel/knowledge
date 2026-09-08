# specialized-expert: dataset results

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/build-specialized-skill/SKILL.md)

## GraphRAG generalization (60)

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[All compared skills](../datasets/graphrag-papers-parallel-eval-60-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| specialized-expert / Specialized expert early confidence-gated hybrid | 99.03% | 100.00% | 99.17% | 989.63 |
| specialized-expert / Specialized expert Ensemble quality + trace v48 | 97.24% | 100.00% | 96.67% | 4855.90 |
| specialized-expert / Specialized expert supervised profiles v51 | 41.03% | 71.11% | 34.11% | 142.67 |

## GraphRAG contradictions (40)

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[All compared skills](../datasets/graphrag-papers-contradiction-eval-40-v1.md)

| Skill family / route | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|
| specialized-expert / Specialized expert early confidence-gated hybrid | 92.50% | 97.71% | 88.33% | 85.11% | 941.60 |
| specialized-expert / Specialized expert Ensemble quality + trace v48 | 87.50% | 96.25% | 78.96% | 81.35% | 4088.78 |
| specialized-expert / Specialized expert supervised profiles v51 | 52.50% | 77.92% | 41.30% | 48.08% | 47.04 |

## Quantum error correction (40)

All 40 qrels were exposed to supervised-profile construction. In-sample fixed-workload comparison only; no promotion or unseen-query claim.

[All compared skills](../datasets/quantum-error-correction-papers-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| specialized-expert / retrospective-supervised-ngram | 100.00% | 100.00% | 100.00% | 34.01 |
| specialized-expert / baseline-lexical | 36.67% | 74.58% | 27.40% | 123.55 |

[Cost, time, quality, and measurement limits](../cta/README.md)
