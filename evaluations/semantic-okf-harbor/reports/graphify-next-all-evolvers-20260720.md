# Graphify Next All-Evolver Harbor Evaluation

Date: 2026-07-20

Decision: retain `build-semantic-okf-graphify-next` unchanged. The bounded root
search-text candidate wins development and the overall holdout mean, but it is
not promotable because one holdout task regresses.

## Candidate

The realized candidate adds a normalized, search-only `norm_label` to existing
`record-root` nodes. Its source-grounded body contribution is capped at 4,096
characters. Visible labels, graph topology, authoritative records, generated
views, and `consult-semantic-okf-graphify` remain unchanged.

The realization seal passed. Native Harbor locked the baseline as
`sha256:1e0176ce507ff81bec4488b33585bea140ac26a5cf0b04c3c0fcdc0ffd43ee41`
and the candidate as
`sha256:7072d31cf78f6c448153418a0762478d5eced79297fc7e2b24dc32812c2c7459`.

## Native Harbor results

Reward is the arithmetic mean of Recall@10, Recall@20, MRR@10, and nDCG@10.
Every row has `bundle_valid=1`, `evidence_valid=1`, no trial error, and 100%
pass rate.

| Cohort | Dataset | Builder | R@10 | R@20 | MRR@10 | nDCG@10 | Reward | Delta | Decision |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Development | Astro train+dev (32) | Baseline | 0.768229 | 0.799479 | 0.495399 | 0.520595 | 0.645926 | — | Control |
| Development | Astro train+dev (32) | cap4096 | 0.838542 | 0.877604 | 0.682329 | 0.653821 | 0.763074 | +0.117148 | Win |
| Development | Papers discovery (24) | Baseline | 0.664595 | 0.673127 | 0.850694 | 0.717198 | 0.726404 | — | Control |
| Development | Papers discovery (24) | cap4096 | 0.760412 | 0.884473 | 0.906250 | 0.801100 | 0.838059 | +0.111655 | Win |
| Holdout | Astro (8) | Baseline | 0.958333 | 0.958333 | 0.900000 | 0.873063 | 0.922432 | — | Control |
| Holdout | Astro (8) | cap4096 | 0.875000 | 0.916667 | 1.000000 | 0.884276 | 0.918986 | -0.003447 | Regression |
| Holdout | Papers (6) | Baseline | 0.798016 | 0.818849 | 0.750000 | 0.713750 | 0.770154 | — | Control |
| Holdout | Papers (6) | cap4096 | 0.759392 | 0.827844 | 0.833333 | 0.732725 | 0.788323 | +0.018170 | Win |

Development mean reward improves from `0.686165` to `0.800566`
(`+0.114402`, +16.67%). Holdout mean improves from `0.846293` to `0.853655`
(`+0.007361`), but the frozen zero-regression policy blocks promotion because
the Astro holdout reward decreases.

## Evolution-engine outcomes

| Harbor skill | Outcome | Useful result |
|---|---|---|
| `harbor-realize-skill-candidate` | Passed | Materialized, validated, digest-sealed, and re-verified cap4096. |
| `harbor-population-search` | Passed, promotion blocked | Selected cap4096 on development; formal holdout gate recorded `task-regression`. |
| `harbor-reflective-pareto-search` | Development passed | Archive size is one; cap4096 dominates baseline on both development cases. Independent holdout jobs used different source paths, so its stricter holdout provenance check rejected them instead of duplicating population's decision. |
| `harbor-run-results` | Passed | Produced separate lock-and-trial comparisons for development and holdout. |
| `harbor-evolve-skill` (GEPA) | Dry-run and doctor passed | Split and runtime are valid, but GEPA can mutate only `SKILL.md`; the measured gain is script-owned, so a live run would not causally test the mutation. |
| `harbor-trace-distillation` | Failed closed | Harbor 0.18 lock omitted the explicit null `retry.include_exceptions` field required by the trace schema-2 importer. No patch was inferred. |
| `harbor-operator-coevolution` | Failed closed | Its local-task identity contract rejected the task directory basename versus the declared `org/name` result identity. No operator credit was fabricated. |
| `harbor-resume-external-failures` | Failed closed | The same local-task identity mismatch prevented retry classification. Successful fresh jobs supersede the failed harness attempts. |
| `harbor-metaskill-evolution` | Not runnable | No producer-published, hash-chained meta-policy ledger exists for this campaign. |

No outputs were merged into the source skill. The only semantically promising
mutation failed the release gate, while the other engines either confirmed its
development dominance or correctly rejected incompatible evidence contracts.

## Evidence

- Development comparison: `evaluations/semantic-okf-datasets/results/20260720-graphify-all-evolvers-02/native-evidence/run-results-development/final-report.json`
- Holdout comparison: `evaluations/semantic-okf-datasets/results/20260720-graphify-all-evolvers-02/native-evidence/run-results-holdout/final-report.json`
- Population gate: `evaluations/semantic-okf-datasets/results/20260720-graphify-all-evolvers-02/native-evidence/population-gated-v2/holdout/generation-000/attempt-000/result.json`
- Pareto archive: `evaluations/semantic-okf-datasets/results/20260720-graphify-all-evolvers-02/native-evidence/pareto/development/generation-000/pareto-archive.json`

