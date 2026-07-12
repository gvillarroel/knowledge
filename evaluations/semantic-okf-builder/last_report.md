# Semantic OKF Builder Lifecycle Smoke Report

## Execution

- Benchmark: `semantic-okf-builder-lifecycle-smoke-compare`
- Eval ID: `eval-ngO-2026-07-12T16:58:28`
- Route: PI `openai-codex/gpt-5.6-luna`, Luna only, one attempt per cell
- Matrix: one prompt, two profiles, two requested and completed cells
- Runtime result: two technical errors, zero model responses

Both profiles reached the required Luna route, but PI exited before producing an answer with `Codex error: The usage limit has been reached`. No fallback model or retry was used. The reported `0/2` rate is therefore not a semantic comparison of the skill and control.

The live run also exposed three non-code lines accidentally prefixed to the copied PowerShell wrapper. They were removed after the run, and the focused runtime test now requires the wrapper to begin with `Set-StrictMode -Version Latest`, rejects alternate or duplicate model arguments, and proves exactly one PI invocation for an accepted Luna route.

Raw live artifacts are under `results/semantic-okf-builder-lifecycle-smoke-compare/2026-07-12T16-58-25-548Z-compare/`.

## Verified preparation

- Both compare configs pass `skill-arena val-conf`.
- The full dry-run plans 14 cells with zero unsupported cells.
- The smoke dry-run plans 2 cells with zero unsupported cells.
- The local reference suite executes and verifies all seven lifecycle cases successfully.
- The benchmark remains strictly Luna-only; a live semantic rerun is pending renewed Luna usage capacity.
