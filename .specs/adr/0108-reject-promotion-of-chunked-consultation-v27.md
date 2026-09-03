# ADR 0108: Reject promotion of chunked consultation v27

## Status

Accepted

## Context

ADR 0106 introduced an additive exact-chunk Classical knowledge-skill builder
without replacing the existing builder. Deterministic checks established
byte-identical authoritative knowledge, exact range hydration, unchanged
search rankings, bounded context, linked metadata, and lower context payloads.
Those checks could not establish semantic answer non-regression.

An append-only Harbor study evolved consultation treatments on q041-q046 and
froze v27 before releasing the disjoint q047-q052 validation cohort. Both
validation arms used Pi 0.84.2, GPT-5.6 Luna, one attempt per case, and the
same digest-pinned compatible Docker environment.

V27 improved mean native reward from 0.162500 to 0.925976 and reduced mean
agent tokens from 447,704.0 to 79,224.7, an 82.30% reduction. It produced
valid evidence in all six cases. Independent blind review still found two of
six semantic regressions, including an explicit coverage omission and a case
with scope conflation, incorrect source attribution, citation mismatch, and a
missing target experiment.

## Decision

Do not promote v27 and do not replace or modify the existing
`build-classical-knowledge-skill` default. Keep
`build-classical-chunked-knowledge-skill` as a separate experimental builder
whose deterministic token, retrieval, and evidence guarantees remain useful
but whose current consultation strategy is not semantically accepted.

Use weighted lexical facet coverage and source/evidence-role reservation as
primary selection constraints. Use bounded Jensen-Shannon divergence only as
a symmetric redundancy penalty after required coverage is satisfied. Do not
use raw cross-entropy as the primary chunk selector because its asymmetry and
unbounded scale do not ensure question-facet or source coverage.

Do not use q047-q052 outcomes to mutate another candidate in this study. A
repair attempt requires a new study with a fresh, disjoint, digest-locked
validation dataset.

## Consequences

- The old Classical builder remains byte-unchanged.
- The additive builder remains available for experimentation and deterministic
  payload measurements, but it must not be described as the new default.
- V27's 82.30% token reduction is an efficiency result, not a promotion claim.
- The best observed semantic trend improved from four regressions in v11's
  independent gate to two regressions in v27's separate independent gate;
  because the cohorts differ, this is directional evidence rather than a
  paired head-to-head claim.
- Future work must open a new study and cannot recycle the released validation
  evidence as optimizer input.
