# Overview

## Restrictions
- ONLY DOCUMENTS IN ENGLISH
- Read SPEC.md to understand the global requirements

## Codex Completion Hook
- Before finishing any implementation task, run the repository coverage check and review the total application coverage result.
- Use `python scripts/check_coverage.py --threshold 80` as the default final coverage gate unless the task explicitly asks for a stricter threshold.
- If the total application coverage is below `80%`, do not stop at reporting it. Add or improve unit tests until the coverage result is at least `80%`, then rerun the coverage check.
- Treat the stricter requirement in `SPEC.md` as the long-term target when work touches broad functionality, but `80%` is the minimum completion gate for routine Codex task closure.

## Decision Records
- Record durable technical or workflow decisions as ADRs under `.specs/adr/*.md`.
- Read existing ADRs before changing a previously chosen technical direction.

## Semantic OKF Evaluation Datasets
- Use `evaluations/semantic-okf-datasets/` as the canonical registry for the `astro-40` and `graphrag-papers-40` Harbor datasets. Read its `README.md` before creating or running evaluation tasks.
- Validate all pinned descriptors and all eight build/consult strategy pairs with `python evaluations/semantic-okf-datasets/dataset_tool.py validate --dataset all`.
- Keep the two execution modes isolated:
  - `build-consult` installs the matched build and consult skills, mounts evaluator-free raw input read-only at `/dataset`, builds `/workspace/knowledge`, and must not mount prebuilt knowledge.
  - `consult-only` installs only the matched consult skill, mounts the exact processed snapshot read-only at `/knowledge`, and must not mount raw sources or a build skill.
- Prepare deterministic raw input with `python evaluations/semantic-okf-datasets/dataset_tool.py prepare --dataset <dataset> --family <family>` and immediately repeat with `--check`. The generated `input-manifest.json` records the exact family-specific host build and validation command shapes.
- Generate each mode with `python evaluations/semantic-okf-datasets/generate_harbor_tasks.py --dataset <dataset> --family <family> --mode <build-consult|consult-only>`. `astro-40` requires `--bundle <validated-bundle>`; `graphrag-papers-40` defaults to its checked bundle.
- Validate each generated mode with the matching `validate_harbor_tasks.py` command. Do not run Harbor unless deterministic regeneration, leakage checks, and all 40 oracle quality gates pass.
- Create a redacted cross-platform rehearsal with `python evaluations/semantic-okf-datasets/run_harbor.py --dataset <dataset> --family <family> --mode <mode> --cohort <cohort> --dry-run`. Run live Harbor only from Linux or WSL after inspecting the receipt.
- Treat `generated/` and `results/` as ignored, append-only evaluation artifacts. Never overwrite a live result path or serialize authentication content.
