---
adr: "0063"
title: "ADR 0063: Keep Raw and Processed Evaluation Data Outside Git"
summary: "Adopt one evaluations-wide ignore boundary for acquired inputs, derived snapshots, generated tasks, and append-only execution artifacts."
status: "Accepted"
date: "2026-07-26"
product: "knowledge"
owner: "Platform Architecture"
area: "Evaluation Operations"
tags: [knowledge, evaluation, harbor, git, artifacts, reproducibility]
---

# ADR 0063: Keep Raw and Processed Evaluation Data Outside Git

## Status

Accepted. This standardizes the artifact boundaries already required by ADRs
0017, 0021, 0024, 0029, 0030, 0034, and 0035.

## Context

Evaluation studies accumulated different local directory conventions. Some
studies supplied their own ignore rules for `generated/` and `results/`, while
newer studies without a local rule exposed thousands of generated tasks,
Harbor trials, traces, snapshots, and runtime files as untracked repository
content.

Those files are large, append-only, sometimes sensitive, and reproducible from
the checked-in evaluation definitions. Moving completed studies can also break
path or digest bindings, so a repository cleanup must not rewrite immutable
evidence merely to normalize directory names.

## Decision

Maintain a shared `evaluations/.gitignore` that ignores the following directory
names at every depth:

- `raw/` and `processed/`;
- `generated/`, `results/`, and `runs/`;
- `artifacts/`, `runtime/`, and `trace-distillation/`; and
- local caches, environments, and interpreter output.

Use `raw/` for new acquired or staged inputs. Use `processed/` for new
knowledge snapshots, indexes, normalized corpora, and other derived data.
Existing immutable evidence may remain at its current path when moving it
would invalidate a recorded digest or reference.

Keep reproducibility code, compact manifests, schemas, questions, reviewed
ground truth, and documentation visible to Git. Harbor study directories use a
stricter deny-by-default allowlist: only their `.gitignore`, generated
publication indexes, and explicitly reviewed aggregate tables may be tracked.

Public visibility metadata does not make a raw report safe to commit. A report
must be reviewed as an aggregate projection with no task content, prompts,
responses, traces, secrets, or holdout internals before publication.

## Consequences

Generated evaluation trees no longer flood repository status output, and new
studies share the same raw-versus-processed boundary without duplicating ignore
rules.

The local artifacts are not deleted. Reproducibility depends on checked-in
descriptors and scripts plus any externally pinned source or snapshot, while
append-only evidence stays in its existing local location.

Already tracked raw artifacts are not silently untracked by this decision.
They require a separate reviewed migration because Git ignore rules do not
affect tracked files and historical references may bind their exact paths.
