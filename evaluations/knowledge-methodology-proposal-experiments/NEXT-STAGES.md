# Empirical Validation Stages

Offline ablation 01 tests three recommendations with existing exposed qrels.
The remaining recommendations need different evidence and must not inherit its
retrospective result.

## Stage 2: Claim quality and judge calibration

Targets: KM-001 and KM-002.

Required inputs:

- a frozen set of generated answers from at least two consultation treatments;
- claim decomposition with exact evidence spans;
- two blinded human reviewers plus adjudication;
- clean, factual-error, authority-cue, and verbosity perturbations; and
- pinned judge prompts and model snapshots.

Primary outcomes:

- supported-claim precision and required-claim recall;
- contradiction and unsupported-claim rates;
- human inter-reviewer agreement;
- judge-versus-human agreement by perturbation class; and
- treatment-rank stability with and without automated judges.

Promotion remains prohibited until the judge calibration contract is fixed
before the evaluation cohort is opened.

## Stage 3: Genuine transfer

Target: KM-003.

Required inputs:

- newly pinned paper bytes not present in either current corpus;
- questions written by reviewers who did not inspect current retrieval traces;
- a contamination ledger covering prompts, qrels, traces, and training inputs;
- frozen baseline and candidate digests; and
- one-way release of the new qualification cohort.

The branch must transfer the selected frozen treatment without mutation. Once a
case or diagnostic is revealed, it becomes development evidence permanently.

## Stage 4: Reviewed evidence and corpus governance

Targets: KM-007 and KM-008.

Create double-reviewed evidence cards for the papers used by the audit, then
run an independently screened search delta. Measure evidence-locator validity,
reviewer agreement, screening disagreement, lane saturation, audit time, and
whether conclusions change.

## Stage 5: Semantic and extraction mutation tests

Targets: KM-009 and KM-011.

For SHACL, generate one conforming and one violating fixture for each accepted
shape, mutate each required property independently, and report detection,
false-positive rate, and runtime.

For PDF extraction, freeze a stratified page set containing columns, tables,
equations, footnotes, and figures. Compare at least two extractors, but use
blinded visual review as the authority for reading order and locator fidelity.

## Stage 6: Component-level evolution

Target: KM-010.

Re-express one existing whole-skill mutation as independently sealed extraction,
routing, retrieval, evidence-selection, and synthesis components. Compare diff
size, attribution, deterministic rebuilding, evaluation cost, and quality
against the copied-skill workflow.

No stage may borrow opened evidence from a later stage or convert an exploratory
result into a promotion claim.
