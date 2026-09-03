---
adr: "0115"
title: "ADR 0115: Author Leakage-Resistant Harbor Evaluation Datasets"
summary: "Use a standalone skill to freeze semantic families, one-way evaluation splits, replayable nuisance variation, hardware strata, and aggregate-only execution reports."
status: "Accepted"
date: "2026-09-02"
product: "knowledge"
owner: "Platform Architecture"
area: "Evaluation Governance"
tags: [harbor, datasets, evaluation, validation, holdout, reproducibility]
---

# ADR 0115: Author Leakage-Resistant Harbor Evaluation Datasets

## Context

Knowledge-skill evolution needs task diversity without letting repeated
optimization memorize one question set or accidental adapter conventions such
as a fixed working directory or `answer.txt` output. Comparisons must also make
hardware, token, cost, and duration trade-offs visible without exposing sealed
tasks or private Harbor traces.

## Decision

- Adopt the standalone
  [`harbor-author-evaluation-datasets` skill](../../skills/harbor-author-evaluation-datasets/SKILL.md)
  for new Harbor task-dataset design in this repository.
- Assign semantic families before task variants and keep related sources,
  templates, oracles, and near-duplicates in one split. Only `development` is
  optimizer-visible. Release sealed `validation` once for one frozen,
  digest-bound winner; any feedback-driven revision starts a new study with
  fresh validation. A separately declared `holdout` is an optional third final
  gate.
- Vary only nuisance surfaces that the task contract declares equivalent,
  including working directory, input location, output filename, and accepted
  response form. Select those variants with task-keyed deterministic seeds,
  record the realized private plan, and never randomize verifier behavior at
  runtime.
- Treat CPU/GPU model and count, memory, storage, cache policy, concurrency,
  network policy, runtime image, and timeouts as explicit resource strata or
  locked comparison metadata. A changed hardware envelope is a changed task
  world unless the estimand predeclares it.
- Consolidate only validated schema-version-1 `final-report.json` artifacts
  produced by `harbor-run-results`. The presentation layer may report aggregate
  outcomes, input/cached/output/reasoning tokens, cost, agent time, wall time,
  throughput, coverage, and baseline deltas, with accessible static SVGs. It
  must omit task identities, prompts, answers, per-case results, diagnostics,
  trajectories, and raw paths.
- Keep private plans, seeds, generated tasks, native jobs, and sealed evidence
  outside Git. Track only reviewed aggregate publications whose release is
  authorized by the study protocol.

## Consequences

Dataset authors gain a reproducible way to test semantic capability across
multiple response surfaces rather than rewarding memorized filesystem
conventions. Evolution evidence remains separated from one-way validation, and
optional holdout remains available for a stricter final claim.

The consolidator is not a second scorer and does not establish fairness across
unrelated reports. Native Harbor reports and the organizer's digest locks remain
the sources of truth; missing or partial usage observations stay explicit, and
release-safe SVGs cannot be used as feedback for the same evolution study.

Operational details live in the
[dataset-authoring contract](../../skills/harbor-author-evaluation-datasets/references/dataset-authoring-contract.md)
and the
[knowledge-skill evolution playbook](../../docs/knowledge-skill-evolution-playbook.md).
