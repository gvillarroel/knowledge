# Main Merge Validation: 2026-07-29

## Merged scope

`main` contains three focused commits:

- `0950fb4` adds the 47-paper methodology corpus, standalone review skill,
  restricted read-only reviewer agent, audit, and ADR 0080.
- `aa8eac7` adds the retrospective cross-domain ablation, the minimal frozen QEC
  inputs required to reproduce it, accepted and rejected treatment records,
  deferred stages, and ADR 0081.
- `c8b6186` adds the generated OKF projection and project skill index entry
  required by repository integration tests.

No unrelated dirty worktree files were staged or merged.

## Passing evidence

The following checks passed from a clean `main` worktree:

- methodology manifest deterministic check: 47 sources;
- methodology dataset validation: 47 papers, eight coverage lanes, eleven audit
  recommendations;
- standalone expert verification: 47 records and a bound 57-file knowledge
  tree;
- restricted agent validation: only `review-knowledge-methodology` is default
  and allowed;
- experiment deterministic replay: 80 questions and 21 treatments in each of
  two domains;
- experiment validation: 42 dataset-treatment cells, 1,680 query results, and
  ten bound decisions;
- focused methodology tests: 10 passed;
- semantic OKF registry validation: Astro and GraphRAG passed for all eight
  registered families;
- project OKF bundle check: current and valid;
- OKF tests after projection repair: 14 passed; and
- application coverage gate: 90.9%, above the required 80%.

## Recorded non-passing evidence

The full coverage invocation exposed eight test failures. Two were caused by
the new skill lacking its generated OKF projection; commit `c8b6186` fixed both.
Six residual failures were rerun independently and remain outside this merge:

1. `test_github_sync_clones_and_exports_text_files` expects three exported
   files but the current GitHub repository source exports two.
2. Five `tests/test_semantic_okf_tantivy_evaluation.py` cases require four
   ignored report files that are absent from a clean checkout:
   `trace-distillation-20260722.json`,
   `trace-distillation-query-idf-20260723.json`,
   `trace-distillation-builder-forward-four-20260723.json`, and
   `trace-distillation-round3-endocrine-20260723.json`.

The merge changes none of the failing source, test, or missing-report paths
relative to pre-merge commit `a1079d6`. These failures are recorded rather than
being hidden or expanded into unrelated repairs.

## Promotion boundary

No retrieval treatment is promoted to a production default. The accepted
controls and qualification candidates, rejected defaults, inconclusive
treatments, invalid first attempt, and untested proposals remain recorded in
ADR 0081 and the experiment decision artifacts.
