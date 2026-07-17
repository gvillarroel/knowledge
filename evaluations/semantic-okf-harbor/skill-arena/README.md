# Skill Arena paired controls

This directory contains six narrow Skill Arena V1 comparisons that complement the primary Harbor campaign. Each file compares exactly one frozen baseline consultation skill with exactly one independently named Harbor-guided evolution. No file combines skill families, so each planned comparison preserves a direct baseline/treatment contrast.

## Fixed design

- Prompt: the byte-equivalent q031 instruction generated at `evaluations/semantic-okf-harbor/generated/tasks/train/q031/instruction.md`.
- Agent: Pi with `openai-codex/gpt-5.3-codex-spark`, high reasoning effort, one request per cell.
- Workspace: the same family-specific Astro bundle for both profiles, materialized at `knowledge/` from the pinned `20260716-astro-generic-01` build.
- Capabilities: one consultation skill per profile; no MCP capability is declared.
- Profiles: one checked-in baseline package and one checked-in evolved package. `config-manifest.json` binds both source trees to the hashes frozen before development and holdout evaluation.
- Assertions: JSON shape, evidence-reference closure, first-use evidence ordering, and required evidence metadata. Qrels, expected source identities, expected claims, and answers are deliberately absent.

The prompt corpus was not authored for Skill Arena: it is the already frozen Harbor training prompt. A separate prompt-coverage file is therefore intentionally omitted. These files are one-case causal diagnostics, not estimates of aggregate or holdout quality. Harbor supplies the live execution, evidence validation, hard-answer gates, token accounting, and latency measurements.

## Reproduce from a clean clone

The configs reference checked-in skill packages directly and do not depend on `snapshots/content/`. Rebuild the ignored, append-only accepted bundle set at the pinned path before running Skill Arena:

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
$python = (Resolve-Path .venv/Scripts/python.exe).Path
$runId = "20260716-astro-generic-01"
$runDir = "evaluations/semantic-okf-astro/results/runs/$runId"

& $python evaluations/semantic-okf-astro/scripts/run_builds.py `
  --run-id $runId --python $python `
  --report "$runDir/build-comparison.json" `
  --markdown "$runDir/build-comparison.md"
```

The build command derives all six family bundles from checked corpus inputs and plans. Then validate and plan every pair:

```powershell
Get-ChildItem evaluations/semantic-okf-harbor/skill-arena/q031-*-paired.yaml | ForEach-Object {
  skill-arena val-conf $_.FullName
  skill-arena evaluate $_.FullName --dry-run
}
```

Dry-run success proves schema validity, source materialization, supported Pi skill cells, and the two-cell execution plan. It is not a model-quality result. See `last_report.md` for the recorded check and `config-manifest.json` for immutable bindings.
