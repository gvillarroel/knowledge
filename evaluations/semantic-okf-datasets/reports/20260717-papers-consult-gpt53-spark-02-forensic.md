# Semantic OKF papers consultation campaign audit

> **INVALID FOR COMPARISON.** No winner or family ordering may be inferred from this campaign.

- Dataset: `graphrag-papers-40`
- Mode: `consult-only`
- Runtime: Pi `0.73.1` with `openai-codex/gpt-5.3-codex-spark` (`high` thinking)
- Structural artifacts complete: `false`
- Evaluable final responses: 0/320
- Evaluation complete: `false`
- Ranking eligible: `false`
- Invalid reasons: incomplete-or-missing-artifacts, scheduled-execution-incomplete, provider-failures, unobservable-family-cohorts, not-all-trials-produced-evaluable-responses
- Semantic correctness: requires a separate blinded/manual review; deterministic anchor coverage is not entailment.

| Family | Results | Evaluable | Quota | Context | Output limit | Interrupted | Contract gate | Min-doc gate | Observed reward |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| adaptive | 1/40 | 0 | 1 | 0 | 0 | 0 | 0/0 | 0/0 | — |
| classical | 0/40 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | — |
| embeddings | 0/40 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | — |
| ensemble | 0/40 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | — |
| entity-graph | 0/40 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | — |
| graphify | 0/40 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | — |
| legacy | 0/40 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | — |
| turso | 0/40 | 0 | 0 | 0 | 0 | 0 | 0/0 | 0/0 | — |

## Cohort observability

| Family | discovery | holdout | hard |
|---|---:|---:|---:|
| adaptive | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| classical | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| embeddings | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| ensemble | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| entity-graph | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| graphify | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| legacy | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |
| turso | 0/24 evaluable | 0/6 evaluable | 0/10 evaluable |

Metrics above use only complete, scorer-observable final responses. Provider and execution failures are not converted into semantic zeroes. Contract, retrieval, minimum-document, and exact-anchor checks remain distinct from semantic review.
