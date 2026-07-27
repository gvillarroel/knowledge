---
adr: "0056"
title: "ADR 0056: Retain RustMallet Skills After Complete Trace Distillation"
summary: "Retain the reference-aware consultant and builder baseline after a consult holdout became non-evaluable and a faster one-command builder regressed one untouched holdout cell."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, rust-mallet, references, harbor, trace-distillation, holdout]
---

# ADR 0056: Retain RustMallet Skills After Complete Trace Distillation

## Status

Accepted. This extends ADRs 0045, 0047, and 0052. It supersedes the temporary
provider-blocked state in ADR 0052 with completed GitHub Copilot development and
holdout evidence, without changing the earlier historical decision.

## Context

The experimental RustMallet pair uses a deterministic
`classical/references.json` dictionary with 1,135 compact IDs. Each ID resolves
to one exact seven-field evidence identity. The selected consultant returns
those IDs, and deterministic validation resolves them before scoring.

Two schema-2 Harbor 0.18.0 campaigns used Pi 0.73.1,
`github-copilot/gpt-5.3-codex`, `thinking: high`, exact skill locks, zero
retries, disjoint development and holdout tasks, and non-compensating evidence
and reference-resolution gates.

The consult candidate combined compact search guidance and selected
authoritative text in one preparation call while preserving the selected
parent's breadth buffer and legacy commands. The builder candidate integrated
reference publication natively and added one command that builds, validates
independently, and publishes atomically.

## Decision

Retain the live reference-aware consultant. Its preserving-prepare candidate
passed q007/q019 development 2/2, but the q005/q020 holdout was not evaluable:
q005 failed the mechanical qualification gate on both sides, and one candidate
q020 trial exited 137. Do not treat the remaining q020 reward of `0.780397` as
a complete candidate cell.

Retain builder digest
`sha256:af3b51512084a0d02d12b26d9823c6db1aad50337977e8ed9b403cbafa897af9`.
The one-command candidate digest
`sha256:381e79b5d50001e139bd48b0c30000232e18ce0124f2de5484b591e69d6b2372`
passed development, had zero holdout errors, and passed
`quality_gate=1` plus `reference_dictionary_resolution=1` in every trial. It
improved untouched holdout mean reward from `0.299073` to `0.342348` and reduced
mean trial wall time from 262.25 to 244.97 seconds. Reject it because q015
regressed from `0.130812` to `0.127488`; the frozen rule does not allow a gain
on q025 to compensate for a task regression.

Keep both candidates isolated. Do not copy either into the live skill pair.

## Consequences

- The processed RustMallet data continues to contain the deterministic
  reference dictionary used by consultation.
- Native reference publication and the one-command protocol remain available
  as evaluated experimental assets, not promoted behavior.
- The canonical 40-question direct-retrieval table remains unchanged because
  the rejected candidates do not alter the selected processed snapshot or its
  retrieval rankings.
- The four RustMallet rows retain 100% evidence validity and P95 query times of
  226.69–238.70 ms; RustMallet remains an experimental non-registry comparator.
- q005, q015, q020, and q025 are observed holdout evidence and cannot be reused
  as untouched holdout in a later RustMallet campaign.
