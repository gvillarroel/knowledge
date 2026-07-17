# Semantic OKF Harbor Campaign Comparison

Campaign: `20260716-pi-spark-one-evolution-pilot`. Status: `complete`. Paired cases: 18.

All sixteen Harbor reward dimensions are reported below. A dash means Harbor did not emit that dimension; it is not silently converted to zero.

## Train

### Gates and retrieval

| Family | Generation | Trials | reward | quality<br>gate | response<br>contract | non<br>null<br>answer | reference<br>validity | all<br>evidence<br>valid | evidence<br>validity | evidence<br>recall | evidence<br>precision | complete<br>qrel<br>coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy | baseline | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.7500 | 1.0000 |
| legacy | evolved | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| embeddings | baseline | 1 | 0.2704 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 0.5000 | 0.0000 |
| embeddings | evolved | 1 | 0.9906 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 |
| classical | baseline | 1 | 0.9604 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 |
| classical | evolved | 1 | 0.9947 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 |
| adaptive | baseline | 1 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4286 | 1.0000 |
| adaptive | evolved | 1 | 0.9947 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6000 | 1.0000 |
| entity-graph | baseline | 1 | 0.0000 | 0.0000 | — | — | — | — | — | — | — | — |
| entity-graph | evolved | 1 | 0.6221 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 0.4000 | 0.0000 |
| ensemble | baseline | 1 | 0.7665 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 0.6667 | 0.0000 |
| ensemble | evolved | 1 | 0.6028 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 0.2222 | 0.0000 |

### Ranking and hard-question completeness

| Family | Generation | Trials | mrr | ndcg | required<br>document<br>coverage | authoritative<br>evidence<br>completeness | atomic<br>claim<br>evidence<br>completeness | important<br>negative<br>evidence<br>completeness |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| legacy | evolved | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| embeddings | baseline | 1 | 1.0000 | 0.7039 | 0.6667 | 0.0000 | 0.0000 | 0.0000 |
| embeddings | evolved | 1 | 1.0000 | 0.9060 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| classical | baseline | 1 | 0.3333 | 0.6039 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| classical | evolved | 1 | 1.0000 | 0.9469 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| adaptive | baseline | 1 | 0.5000 | 0.6979 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| adaptive | evolved | 1 | 1.0000 | 0.9469 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| entity-graph | baseline | 1 | — | — | — | — | — | — |
| entity-graph | evolved | 1 | 1.0000 | 0.6714 | 0.6667 | 0.6667 | 0.6000 | 0.5000 |
| ensemble | baseline | 1 | 1.0000 | 0.7654 | 0.6667 | 0.6667 | 0.8000 | 1.0000 |
| ensemble | evolved | 1 | 0.5000 | 0.4776 | 0.6667 | 0.6667 | 0.6000 | 0.5000 |

### Runtime and resources

| Family | Generation | Errors | Mean latency (s) | Total input tokens | Total cache tokens | Total output tokens |
|---|---|---:|---:|---:|---:|---:|
| legacy | baseline | 0 | 87.5425 | 1,246,462 | 1,169,792 | 13,422 |
| legacy | evolved | 0 | 60.2597 | 451,356 | 398,080 | 14,904 |
| embeddings | baseline | 0 | 108.4041 | 223,775 | 166,016 | 14,576 |
| embeddings | evolved | 0 | 104.4822 | 108,423 | 84,864 | 9,054 |
| classical | baseline | 0 | 196.8081 | 1,163,264 | 1,092,992 | 17,523 |
| classical | evolved | 0 | 153.9317 | 363,528 | 332,032 | 7,729 |
| adaptive | baseline | 0 | 506.4299 | 1,534,743 | 1,465,728 | 22,134 |
| adaptive | evolved | 0 | 127.8301 | 346,869 | 316,800 | 10,064 |
| entity-graph | baseline | 1 | 600.1005 | 1,605,081 | 1,484,160 | 4,889 |
| entity-graph | evolved | 0 | 141.1216 | 606,985 | 554,112 | 15,053 |
| ensemble | baseline | 0 | 510.3977 | 293,060 | 262,912 | 10,638 |
| ensemble | evolved | 0 | 379.6208 | 857,829 | 797,184 | 17,311 |

## Dev

### Gates and retrieval

| Family | Generation | Trials | reward | quality<br>gate | response<br>contract | non<br>null<br>answer | reference<br>validity | all<br>evidence<br>valid | evidence<br>validity | evidence<br>recall | evidence<br>precision | complete<br>qrel<br>coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy | baseline | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.5000 | 1.0000 |
| legacy | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | 1.0000 |
| embeddings | baseline | 1 | 0.4850 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| embeddings | evolved | 1 | 0.7037 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 0.3333 | 0.0000 |
| classical | baseline | 1 | 0.7263 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 0.3333 | 0.0000 |
| classical | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 1.0000 |
| adaptive | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 1.0000 |
| adaptive | evolved | 1 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.7500 | 0.5000 | 0.2500 | 0.0000 |
| entity-graph | baseline | 1 | 0.5477 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 |
| entity-graph | evolved | 1 | 0.7263 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 | 0.0000 |
| ensemble | baseline | 1 | 0.0000 | 0.0000 | — | — | — | — | — | — | — | — |
| ensemble | evolved | 1 | 0.9920 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | 1.0000 |

### Ranking and hard-question completeness

| Family | Generation | Trials | mrr | ndcg | required<br>document<br>coverage | authoritative<br>evidence<br>completeness | atomic<br>claim<br>evidence<br>completeness | important<br>negative<br>evidence<br>completeness |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| legacy | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| embeddings | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 0.1667 | 0.2000 | 0.0000 |
| embeddings | evolved | 1 | 0.5000 | 0.3869 | 0.5000 | 0.8333 | 0.8000 | 1.0000 |
| classical | baseline | 1 | 1.0000 | 0.6131 | 0.5000 | 0.8333 | 0.8000 | 1.0000 |
| classical | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| adaptive | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| adaptive | evolved | 1 | 0.5000 | 0.3869 | 0.5000 | 0.8333 | 0.8000 | 1.0000 |
| entity-graph | baseline | 1 | 1.0000 | 0.8772 | 1.0000 | 0.1667 | 0.2000 | 0.5000 |
| entity-graph | evolved | 1 | 1.0000 | 0.6131 | 0.5000 | 0.8333 | 0.8000 | 1.0000 |
| ensemble | baseline | 1 | — | — | — | — | — | — |
| ensemble | evolved | 1 | 1.0000 | 0.9197 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Runtime and resources

| Family | Generation | Errors | Mean latency (s) | Total input tokens | Total cache tokens | Total output tokens |
|---|---|---:|---:|---:|---:|---:|
| legacy | baseline | 0 | 57.7484 | 897,389 | 834,432 | 12,490 |
| legacy | evolved | 0 | 114.0891 | 1,215,631 | 1,144,576 | 14,895 |
| embeddings | baseline | 0 | 232.7952 | 430,627 | 357,888 | 17,652 |
| embeddings | evolved | 0 | 144.1915 | 687,622 | 633,216 | 15,655 |
| classical | baseline | 0 | 108.4257 | 221,053 | 175,488 | 8,386 |
| classical | evolved | 0 | 128.4808 | 620,709 | 573,184 | 9,992 |
| adaptive | baseline | 0 | 147.9444 | 1,063,699 | 992,000 | 15,449 |
| adaptive | evolved | 0 | 196.5782 | 494,593 | 452,352 | 15,702 |
| entity-graph | baseline | 0 | 181.9275 | 1,032,364 | 952,704 | 19,386 |
| entity-graph | evolved | 0 | 145.4070 | 921,056 | 852,992 | 21,380 |
| ensemble | baseline | 1 | 600.0192 | 422,742 | 357,504 | 4,841 |
| ensemble | evolved | 0 | 250.1932 | 576,139 | 525,184 | 15,554 |

## Holdout

### Gates and retrieval

| Family | Generation | Trials | reward | quality<br>gate | response<br>contract | non<br>null<br>answer | reference<br>validity | all<br>evidence<br>valid | evidence<br>validity | evidence<br>recall | evidence<br>precision | complete<br>qrel<br>coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy | baseline | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.4000 | 1.0000 |
| legacy | evolved | 1 | 0.9920 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | 1.0000 |
| embeddings | baseline | 1 | 0.6577 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4000 | 1.0000 |
| embeddings | evolved | 1 | 0.9877 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4000 | 1.0000 |
| classical | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4000 | 1.0000 |
| classical | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 1.0000 |
| adaptive | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | 1.0000 |
| adaptive | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 |
| entity-graph | baseline | 1 | 0.4000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 |
| entity-graph | evolved | 1 | 0.4663 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 0.2000 | 0.0000 |
| ensemble | baseline | 1 | 0.9920 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4000 | 1.0000 |
| ensemble | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 |

### Ranking and hard-question completeness

| Family | Generation | Trials | mrr | ndcg | required<br>document<br>coverage | authoritative<br>evidence<br>completeness | atomic<br>claim<br>evidence<br>completeness | important<br>negative<br>evidence<br>completeness |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| legacy | evolved | 1 | 1.0000 | 0.9197 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| embeddings | baseline | 1 | 1.0000 | 0.8772 | 1.0000 | 0.5000 | 0.4000 | 0.5000 |
| embeddings | evolved | 1 | 1.0000 | 0.8772 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| classical | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| classical | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| adaptive | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| adaptive | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| entity-graph | baseline | 1 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| entity-graph | evolved | 1 | 1.0000 | 0.6131 | 0.5000 | 0.5000 | 0.6000 | 0.0000 |
| ensemble | baseline | 1 | 1.0000 | 0.9197 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ensemble | evolved | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Runtime and resources

| Family | Generation | Errors | Mean latency (s) | Total input tokens | Total cache tokens | Total output tokens |
|---|---|---:|---:|---:|---:|---:|
| legacy | baseline | 0 | 66.9405 | 1,662,200 | 1,551,488 | 14,931 |
| legacy | evolved | 0 | 53.4844 | 763,307 | 691,712 | 15,942 |
| embeddings | baseline | 0 | 223.8598 | 608,250 | 518,656 | 16,148 |
| embeddings | evolved | 0 | 113.2557 | 198,595 | 174,336 | 8,688 |
| classical | baseline | 0 | 104.0741 | 1,245,939 | 1,177,600 | 14,396 |
| classical | evolved | 0 | 55.0578 | 176,840 | 149,248 | 6,489 |
| adaptive | baseline | 0 | 385.5551 | 1,482,269 | 1,391,232 | 18,860 |
| adaptive | evolved | 0 | 101.4794 | 138,941 | 118,272 | 4,334 |
| entity-graph | baseline | 0 | 190.3569 | 1,484,043 | 1,420,160 | 17,477 |
| entity-graph | evolved | 0 | 153.0730 | 1,414,088 | 1,317,248 | 14,981 |
| ensemble | baseline | 0 | 422.7772 | 415,612 | 380,288 | 12,522 |
| ensemble | evolved | 0 | 244.9540 | 283,644 | 248,960 | 9,462 |

## Promotion gates

| Family | Decision | Runtime | Contract | Non-null | Reference | All evidence | Quality | Dev reward | Hard completeness | Deterministic 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| legacy | promoted | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| embeddings | promoted | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| classical | promoted | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| adaptive | rejected | pass | pass | pass | pass | fail | fail | fail | fail | pass |
| entity-graph | promoted | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| ensemble | pending | pass | pass | pass | pass | pass | pass | pass | pending | pass |

## Excluded runs

These roots are documented for auditability but never participate in any aggregate or promotion decision.

| Result root | Category | Reason |
|---|---|---|
| `results/20260716-baseline-dev-classical-q032` | pre_fix_grader | This run predates the EOF-normalization grader repair; the corresponding grader-r1 run is authoritative. |
| `results/20260716-baseline-dev-embeddings-q032` | pre_fix_grader | This run predates the EOF-normalization grader repair; the corresponding grader-r1 run is authoritative. |
| `results/20260716-baseline-dev-legacy-q032` | pre_agent_auth_failure | Pi exited before agent execution because the ephemeral OpenAI Codex authentication mount was unavailable; the authenticated grader-r1 run is authoritative. |
| `results/20260716-baseline-dev-legacy-q032-auth-r1` | pre_fix_grader | This authenticated run predates the EOF-normalization grader repair; the corresponding grader-r1 run is authoritative. |
| `results/20260716-evolved-dev-classical-q032` | pre_fix_grader | This run predates the EOF-normalization grader repair; the corresponding grader-r1 run is authoritative. |
| `results/20260716-evolved-dev-embeddings-q032` | pre_fix_grader | This run predates the EOF-normalization grader repair; the corresponding grader-r1 run is authoritative. |
| `results/20260716-evolved-dev-legacy-q032` | pre_agent_auth_failure | Pi exited before agent execution because the ephemeral OpenAI Codex authentication mount was unavailable; the authenticated grader-r1 run is authoritative. |
| `results/20260716-evolved-dev-legacy-q032-auth-r1` | pre_fix_grader | This authenticated run predates the EOF-normalization grader repair; the corresponding grader-r1 run is authoritative. |
| `results/20260716-evolved-train-ensemble-q031` | pre_agent_auth_failure | Pi exited before agent execution because the ephemeral OpenAI Codex authentication mount was unavailable; the auth-r1 run is authoritative. |
| `results/20260716-evolved-train-ensemble-q031-auth-r2` | delayed_duplicate | This redundant delayed retry never produced a terminal trial result; the completed auth-r1 run is authoritative. |
| `results/20260716-evolved-train-entity-graph-q031` | pre_agent_auth_failure | Pi exited before agent execution because the ephemeral OpenAI Codex authentication mount was unavailable; the auth-r1 run is authoritative. |

Promotion gates are non-compensating: one failed required check rejects the candidate. Mechanical evidence sufficiency and response-contract compliance do **not** establish semantic answer correctness; that requires a separate answer review.
