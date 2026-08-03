# ADR 0095: Reject V34 After Direct Canonical Semantic Revalidation

## Status

Accepted on 2026-08-02. This ADR rejects exact V34 after a direct matched
revalidation against the canonical Classical consultation baseline. It does
not accept or promote a replacement candidate.

## Context

ADR 0094 concluded that no lower-token Classical consultation candidate had
proved the complete acceptance conjunction through V66. Exact V34 remained a
particularly important unresolved ancestor because an earlier study reported
strong token savings and a favorable semantic comparison, while later
evidence showed that its behavior could vary across otherwise matched runs.

Study v26 therefore reran the exact frozen V34 candidate against a fresh
canonical baseline on the same released six-case development cohort. Both
jobs used Harbor 0.18.0, `gpt-5.3-codex-spark`, high reasoning, matched
consult-only mounts, zero configured retries, and native provider-reported
input-plus-output token accounting.

The canonical baseline completed six of six cases with no errors or retries
and used 6,015,810 native tokens in total, with a mean of 1,002,635 and a
median of 779,410. Exact V34 also completed six of six cases with no errors or
retries and used 79,744 native tokens in total, with a mean of 13,290.667 and
a median of 12,782. This is a 98.674426% reduction in total tokens, and V34
was cheaper in every paired case. All 21 numeric verifier metrics were 1.0 in
all six V34 cases.

Those automatic metrics did not establish semantic equivalence. An
independent reviewer, isolated from candidate construction, compared the
paired answers and rejected V34 for semantic regressions in four of six
cases. The regressions included process or metadata prose in place of a
fully direct answer and overly rigid exact-count behavior that omitted
relevant supporting documents. The fail-closed comparison consequently
passed the execution, retry, token, median, per-case cost, and numeric-metric
gates but failed the semantic non-regression gate.

This result also resolves the apparent contradiction between V34's very low
token count and its earlier favorable review. The token reduction is real,
but the quality behavior is not sufficiently stable to satisfy a zero-
degradation requirement. A structurally permissive automatic verifier can
miss answer-level semantic loss.

## Decision

Reject exact V34 and do not release v26 validation or holdout. Keep both
sealed, stop the v26 evolution and promotion stages, and retain the canonical
Classical consultation skill.

Treat the 98.674426% reduction as diagnostic evidence, not as an accepted
optimization. Do not promote a candidate solely because all numeric verifier
metrics pass. Every future candidate must pass an independent paired semantic
non-regression review in addition to execution, retry, token, and numeric
metric gates.

Continue the search only in a new organized study with fresh, digest-locked,
optimizer-invisible validation and holdout cohorts. Screen conservative
ancestors and new mutations on released development data first. Freeze one
winner before releasing validation, and never feed validation or holdout
outcomes back into candidate evolution in the same study.

## Consequences

- There is still no promoted end-to-end lower-token Classical consultation
  version.
- V34 proves that approximately 98.67% token reduction is mechanically
  possible on the measured cohort, but not that quality is preserved.
- Numeric verifier parity is necessary but insufficient; independent paired
  semantic review is a mandatory acceptance gate.
- Exact-count answer policies require particular scrutiny because optional
  relevant evidence may improve an answer without violating the requested
  minimum.
- The v26 comparison and semantic review remain immutable evidence, and its
  validation and holdout datasets remain unreleased.
- Further work proceeds in a fresh study rather than revising v26 after its
  failed acceptance gate.
