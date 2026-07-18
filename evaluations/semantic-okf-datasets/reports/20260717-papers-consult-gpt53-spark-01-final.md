# Semantic OKF papers consultation campaign

- Dataset: `graphrag-papers-40`
- Mode: `consult-only`
- Runtime: Pi `0.73.1` with `openai-codex/gpt-5.3-codex-spark` (`high` thinking)
- Results: 320/320 trials; complete: `true`

| Family | Trials | Technical | Reward | Gate | Contract | Precision | Recall | MRR | NDCG | Input M | Output k |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| classical | 40/40 | 34 | 0.044 | 0.075 | 0.125 | 0.833 | 0.370 | 0.917 | 0.483 | 17.82 | 152.2 |
| embeddings | 40/40 | 35 | 0.033 | 0.050 | 0.075 | 0.519 | 0.390 | 0.800 | 0.476 | 11.12 | 132.2 |
| adaptive | 40/40 | 35 | 0.021 | 0.050 | 0.075 | 0.468 | 0.553 | 0.492 | 0.457 | 22.24 | 166.2 |
| ensemble | 40/40 | 40 | 0.000 | 0.000 | 0.000 | — | — | — | — | 6.45 | 145.3 |
| entity-graph | 40/40 | 37 | 0.000 | 0.000 | 0.025 | 0.439 | 0.421 | 0.583 | 0.444 | 14.47 | 130.6 |
| graphify | 40/40 | 40 | 0.000 | 0.000 | 0.000 | — | — | — | — | 1.93 | 20.2 |
| legacy | 40/40 | 33 | 0.000 | 0.000 | 0.000 | 0.802 | 0.659 | 0.719 | 0.641 | 24.48 | 219.0 |
| turso | 40/40 | 34 | 0.000 | 0.000 | 0.000 | 0.709 | 0.603 | 0.889 | 0.659 | 12.50 | 157.3 |

## Cohort outcomes

Each cell is `reward mean; quality-gate passes; technical failures`.

| Family | Discovery (24) | Holdout (6) | Hard (10) |
|---|---:|---:|---:|
| classical | 0.000; 0/24; 23 tech | 0.293; 3/6; 1 tech | 0.000; 0/10; 10 tech |
| embeddings | 0.020; 1/24; 23 tech | 0.140; 1/6; 2 tech | 0.000; 0/10; 10 tech |
| adaptive | 0.012; 1/24; 22 tech | 0.095; 1/6; 3 tech | 0.000; 0/10; 10 tech |
| ensemble | 0.000; 0/24; 24 tech | 0.000; 0/6; 6 tech | 0.000; 0/10; 10 tech |
| entity-graph | 0.000; 0/24; 24 tech | 0.000; 0/6; 3 tech | 0.000; 0/10; 10 tech |
| graphify | 0.000; 0/24; 24 tech | 0.000; 0/6; 6 tech | 0.000; 0/10; 10 tech |
| legacy | 0.000; 0/24; 20 tech | 0.000; 0/6; 3 tech | 0.000; 0/10; 10 tech |
| turso | 0.000; 0/24; 24 tech | 0.000; 0/6; 0 tech | 0.000; 0/10; 10 tech |

Retrieval means use observed verifier values. Gate and contract rates count missing technical outcomes as failures; the JSON report records both variants and each observed denominator.
