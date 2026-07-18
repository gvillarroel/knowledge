# Semantic OKF papers consultation campaign audit

> **INVALID FOR COMPARISON.** No winner or family ordering may be inferred from this campaign.

- Dataset: `graphrag-papers-40`
- Mode: `consult-only`
- Runtime: Pi `0.73.1` with `openai-codex/gpt-5.3-codex-spark` (`high` thinking)
- Structural artifacts complete: `true`
- Evaluable final responses: 32/320
- Evaluation complete: `false`
- Ranking eligible: `false`
- Invalid reasons: provider-failures, unobservable-family-cohorts, not-all-trials-produced-evaluable-responses
- Semantic correctness: requires a separate blinded/manual review; deterministic anchor coverage is not entailment.

| Family | Results | Evaluable | Quota | Context | Output limit | Interrupted | Contract gate | Min-doc gate | Observed reward |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| adaptive | 40/40 | 5 | 30 | 2 | 1 | 2 | 2/5 | 1/5 | 0.000 |
| classical | 40/40 | 6 | 31 | 3 | 0 | 0 | 4/6 | 0/6 | 0.000 |
| embeddings | 40/40 | 4 | 30 | 4 | 2 | 0 | 2/4 | 2/4 | 0.210 |
| ensemble | 40/40 | 0 | 34 | 0 | 0 | 6 | 0/0 | 0/0 | — |
| entity-graph | 40/40 | 4 | 34 | 0 | 0 | 2 | 0/4 | 1/4 | 0.000 |
| graphify | 40/40 | 0 | 34 | 0 | 0 | 6 | 0/0 | 0/0 | — |
| legacy | 40/40 | 7 | 27 | 5 | 1 | 0 | 0/7 | 5/7 | 0.000 |
| turso | 40/40 | 6 | 34 | 0 | 0 | 0 | 0/6 | 2/6 | 0.000 |

## Cohort observability

| Family | discovery | holdout | hard |
|---|---:|---:|---:|
| adaptive | 2/24 evaluable | 3/6 evaluable | 0/10 evaluable |
| classical | 1/24 evaluable | 5/6 evaluable | 0/10 evaluable |
| embeddings | 1/24 evaluable | 3/6 evaluable | 0/10 evaluable |
| ensemble | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| entity-graph | 0/24 evaluable | 4/6 evaluable | 0/10 evaluable |
| graphify | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| legacy | 4/24 evaluable | 3/6 evaluable | 0/10 evaluable |
| turso | 0/24 evaluable | 6/6 evaluable | 0/10 evaluable |

Metrics above use only complete, scorer-observable final responses. Provider and execution failures are not converted into semantic zeroes. Contract, retrieval, minimum-document, and exact-anchor checks remain distinct from semantic review.
