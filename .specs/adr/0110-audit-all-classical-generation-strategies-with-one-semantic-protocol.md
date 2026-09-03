# ADR 0110: Audit all Classical generation strategies with one semantic protocol

## Status

Superseded by ADR 0111

## Context

The Classical chunking program accumulated several development generations.
Its native Harbor reward measures response structure, evidence qualification,
and anchor mechanics, while historical semantic checks covered only selected
candidates and used different review methods. Comparing those columns as if
they were one quality measurement could reward file layout or whole-record
locators instead of answer correctness.

Two historical cohorts, q019-q024 and q041-q046, contain authored semantic
rubrics but predate separate hard-ground-truth artifacts. The independent
q047-q052 validation cohort contains both semantic rubrics and hard ground
truth. Inventing retrospective truth for the older tasks would create a new,
unregistered evaluator contract.

## Decision

Re-adjudicate every completed, comparable Classical strategy job with the
solution-agnostic protocol adopted by ADR 0109. Review complete populations in
two counterbalanced orientations per case with Pi, GPT-5.6 Luna, high thinking,
and conservative consensus. Exclude solution mechanics, job identity, native
reward, and token usage from reviewer-visible prompts.

Label q019-q024 and q041-q046 `rubric-only`. Label q047-q052 `rubric+truth`.
Compare strategies only against the canonical answer from the same cohort and
never declare a cross-cohort winner. Treat complete responses with no semantic
answer content as answer-quality failures; reserve infrastructure exclusion for
actual provider, execution, or verifier failures.

Use strict paired non-regression as the semantic gate. Any `regressed` or
`mixed` case rejects a treatment even when its aggregate coverage, mechanical
reward, or token efficiency improves. Preserve the earlier development table
byte-for-byte and mark its semantic column as superseded in the current-facing
copy.

The audit covers 22 strategy rows in three cohorts and 36 counterbalanced Luna
review calls. No treatment passes the strict semantic gate:

- q019-q024 treatments reduce mean agent tokens by 68.09% to 96.24%, but every
  treatment has at least one paired semantic regression;
- q041-q046 treatments reduce mean agent tokens by 88.15% to 91.37%, but every
  treatment has at least two paired regressions; and
- q047-q052 v27 reduces mean agent tokens by 82.30%, but has three regressions,
  one mixed case, and lower aggregate required-point coverage than canonical.

The complete reviewed aggregate is published as
`complete-solution-agnostic-all-strategies-r1.table.md`. Private prompts,
judgments, normalized answers, and job paths remain excluded from publication.

## Consequences

- Native reward remains useful for mechanical diagnostics but cannot establish
  semantic quality or promotion eligibility.
- The measured regressions are answer-prose regressions under a solution-blind
  review, not artifacts of how knowledge files or locators are stored.
- Aggregate improvements identify hypotheses for a future study, not a winner
  in this released study.
- No audited treatment is promoted. Any repair must start a new study with new,
  digest-locked validation data; these released outcomes cannot feed mutation
  in the current study.
