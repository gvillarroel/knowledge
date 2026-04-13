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
