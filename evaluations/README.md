# Evaluation workspace

This directory contains reproducible evaluation definitions, validators, and
compact reviewed documentation. Large or sensitive evaluation data stays local
and is ignored by Git.

## Current report

Read [`LATEST-REPORT.md`](LATEST-REPORT.md) for the current ordered comparison
of Semantic OKF build/consult pairs, experimental candidates, grounded Harbor
status, and capability-only evaluations. It orders evidence by comparability
and recency without moving immutable or digest-bound artifacts.

Read
[`SKILL-EXPLORATION-AND-EVOLUTION.md`](SKILL-EXPLORATION-AND-EVOLUTION.md)
for the consolidated history of what was tried, which skill and evolution
strategy were used, the observed result, and whether each candidate was
promoted, rejected, retained, or left as retrospective evidence.

The current
[two-stage token report](semantic-okf-datasets/reports/20260730-semantic-okf-token-usage.md)
ranks all eight registered strategy families separately for one-folder
construction and submitted consultation queries. It also preserves runtime
error counts so incomplete answers cannot be mistaken for efficient ones.

The newest direct-retrieval addition is the replicated
[supervised-profile v51 specialized expert](semantic-okf-specialized-experts/reports/definitive-experts-20260728.md).
It is position 1 of 25 on the retrospective all-40 GraphRAG direct contract.
The same study includes a separate Astro expert ranked first on its frozen
route comparison. These ranks apply only to the deterministic helpers; the
associated guidance has no grounded-answer leaderboard position or
holdout-qualified promotion.

The paper-grounded review of the repository's knowledge methodology is in
[`knowledge-methodology-papers`](knowledge-methodology-papers/README.md). It
contains a version-pinned 47-paper corpus, validated Semantic OKF snapshot,
restricted reviewer agent, and prioritized audit. It is a methodology review,
not another row in the retrieval leaderboard.

The branch-scoped empirical follow-up is in
[`knowledge-methodology-proposal-experiments`](knowledge-methodology-proposal-experiments/README.md).
Its first preregistered retrospective study compares 21 chunking/retrieval
treatments across the GraphRAG and QEC paper workloads. These results test
methodological hypotheses but remain promotion-ineligible.

## Final-report presentation

Every current-facing final evaluation report starts with one compact primary
comparison table in this shape:

| Pos. | Pair / strategy | Dataset metric 1 | Dataset metric 2 |
|---:|---|---:|---:|
| 1 | `<strategy, pair, or version>` | `<measured value>` | `<measured value>` |

The primary table follows these rules:

- the first column is a sequential position for rankable, directly comparable
  rows;
- the second column identifies the strategy, build/consult pair, candidate, or
  version being compared;
- every remaining column is a metric produced by the named test dataset and
  evaluation contract, aggregated across its declared cohort, with units shown
  in the header or value;
- status, decision, outcome, acceptance, and promotion labels are not table
  columns; report those separately in prose or an eligibility section;
- rows from different datasets or evaluation contracts are not mixed; and
- a strategy without every displayed metric is omitted from the ranked table
  and explained immediately after it instead of receiving placeholder values.

Diagnostic tables may follow the primary comparison, but they must remain
clearly labeled and must not imply a ranking when coverage is incomplete.
Validate the current report with:

```powershell
python evaluations/validate_final_report.py evaluations/LATEST-REPORT.md
python evaluations/validate_comparison_contract.py \
  evaluations/LATEST-REPORT.comparison.json
```

The companion contract conforms to
[`final-report-comparison.schema.json`](final-report-comparison.schema.json).
It binds one dataset, cohort, candidate budget, identity grouping, and metric
contract. Each metric declares its aggregation, unit, direction, and display
precision; each alternative supplies a complete finite numeric metric map. The
Markdown table is its checked human-readable projection, so rows are
alternatives and metric columns are aggregate dataset results.

## Repository boundary

Keep these files in Git:

- evaluation code and tests;
- dataset descriptors, schemas, and deterministic manifests;
- compact plans, questions, and reviewed ground truth;
- documentation and accepted aggregate reports that contain no prompts,
  responses, traces, secrets, or holdout internals; and
- Harbor study publication indexes and explicitly reviewed aggregate tables.

Keep these files outside Git:

- acquired or staged source data;
- processed knowledge snapshots and indexes;
- generated tasks and bundles;
- Harbor jobs, trials, traces, answers, and verifier diagnostics;
- model caches, runtime environments, and credentials; and
- intermediate reports or review batches.

## Local layout

New and migrated studies should use the following layout:

```text
evaluations/<study>/
  README.md
  manifests/          # compact reproducibility contracts; tracked
  scripts/            # generators and validators; tracked
  publication/        # reviewed aggregate projection only; tracked selectively
  raw/                # acquired or staged inputs; ignored
  processed/          # snapshots, indexes, and derived data; ignored
  generated/          # generated tasks and bundles; ignored
  results/            # append-only executions and diagnostics; ignored
```

The shared `evaluations/.gitignore` also covers legacy `runs/`, `artifacts/`,
`runtime/`, and `trace-distillation/` directories anywhere below this tree.
Study-local `.gitignore` files may add narrower rules but must not expose any of
these shared artifact directories.

Do not move immutable live results merely to make the tree look uniform.
Existing paths may be bound by hashes or referenced by an ADR. Leave those
artifacts in place; the shared ignore policy keeps them local. Use `raw/` and
`processed/` for all new work and for unbound data that can be migrated safely.

Before committing evaluation changes, check the visible projection:

```powershell
git status --short --untracked-files=all -- evaluations
git check-ignore -v evaluations/<study>/raw/<file>
git check-ignore -v evaluations/<study>/processed/<file>
```

For the canonical Semantic OKF Harbor datasets, also follow
`semantic-okf-datasets/README.md` and validate the complete registry before
running Harbor.

## Private local corpora

The [`data-science-ai-ml-books`](data-science-ai-ml-books/README.md) study
binds 38 English EPUB books from two user-provided Google Drive folders into a
deterministic local Semantic OKF corpus. Its copyrighted source and extracted
text remain ignored, and it is intentionally excluded from the canonical
Harbor registry until a separate reviewed evaluation contract exists.
