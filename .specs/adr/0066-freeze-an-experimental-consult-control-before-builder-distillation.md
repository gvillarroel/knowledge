# ADR 0066: Freeze an experimental consult control before builder distillation

## Status

Accepted on 2026-07-27.

## Context

The Tika/MALLET/Tantivy pair needs separate consultation and builder improvement
stages. Changing both skills in one Harbor treatment would make any reward movement
ambiguous. The revised trace-distillation contract also keeps holdout inaccessible
until a candidate passes every development task and required mechanical gate.

Consult candidate v39 scored `0.7174`, `0.6608`, and `0.7819` on q006-q008. Candidate
v42 improved mean reward and exact response transport but passed only one of three
development tasks, compared with two for v39. Neither candidate qualified for
holdout or promotion.

The generated build-consult task tree and raw canonical-text input are valid, but
the available Linux Harbor images do not contain Java. The builder contract requires
a hash-bound Java 17-or-later runtime and forbids downloading it during a trial.

## Decision

Use the exact v39 consultation artifact and digest as an experimental fixed control
for later builder trials. Do not copy it into the source skill, call it promoted, or
open consultation holdout.

Evaluate builder mutations only after a local Linux JDK 17-or-later runtime is
mounted read-only and identically into every baseline, candidate, and holdout cell.
Keep the raw-input and prebuilt-knowledge execution modes isolated.

Select a consultation control by development pass count first and mean reward only
as a tie-breaker. This preserves the gate's all-task objective instead of selecting
v42 solely for its higher mean.

## Consequences

- Builder comparisons have one digest-bound consultation confound control.
- The consultation source skill remains unchanged and unpromoted.
- Builder trace distillation is blocked by an explicit infrastructure prerequisite,
  not silently replaced by a host-side or prebuilt-bundle shortcut.
- A future Linux JDK mount must be recorded by path and tree digest before the
  builder baseline is submitted.
