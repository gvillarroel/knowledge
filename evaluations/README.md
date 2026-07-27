# Evaluation workspace

This directory contains reproducible evaluation definitions, validators, and
compact reviewed documentation. Large or sensitive evaluation data stays local
and is ignored by Git.

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

