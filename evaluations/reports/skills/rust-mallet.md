# rust-mallet: dataset results

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/consult-semantic-okf-rust-mallet/SKILL.md)

## GraphRAG generalization (60)

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[All compared skills](../datasets/graphrag-papers-parallel-eval-60-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| rust-mallet / RustMallet association | 98.91% | 100.00% | 100.00% | 677.64 |
| rust-mallet / RustMallet fusion | 98.85% | 100.00% | 100.00% | 684.80 |
| rust-mallet / RustMallet topic | 98.68% | 100.00% | 100.00% | 682.38 |
| rust-mallet / RustMallet BM25 | 98.11% | 98.33% | 100.00% | 650.81 |

## GraphRAG contradictions (40)

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[All compared skills](../datasets/graphrag-papers-contradiction-eval-40-v1.md)

| Skill family / route | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|
| rust-mallet / RustMallet association | 90.00% | 97.08% | 88.33% | 87.09% | 492.97 |
| rust-mallet / RustMallet fusion | 87.50% | 96.25% | 88.33% | 85.86% | 496.45 |
| rust-mallet / RustMallet topic | 87.50% | 96.25% | 84.17% | 83.49% | 497.68 |
| rust-mallet / RustMallet BM25 | 65.00% | 86.25% | 90.00% | 81.93% | 470.43 |

[Cost, time, quality, and measurement limits](../cta/README.md)
