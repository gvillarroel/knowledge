---
adr: "0046"
title: "ADR 0046: Reject the Tantivy Consultation Trace-Distillation Candidate"
summary: "Retain the checked-in standalone Tantivy consultant unchanged after candidate S passed development but failed to qualify on the sealed Harbor holdout."
status: "Accepted"
date: "2026-07-22"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - tantivy
  - bm25
  - harbor
  - trace-distillation
---

# ADR 0046: Reject the Tantivy Consultation Trace-Distillation Candidate

## Status

Accepted.

This decision extends ADR 0043. It does not add Tantivy to the canonical
eight-family registry and does not change the checked-in standalone consultant.

## Context

The first Tantivy consultant established a native, read-only BM25 route over a
validated classical Semantic OKF snapshot. Harbor trace distillation then used
four development questions to improve answer construction without changing the
snapshot or authoritative evidence boundary. Fifteen versioned iterations
explored retrieval fusion, required-term handling, bounded deterministic
finalization, evidence-role selection, and shorter terminal serialization.

The final S candidate retained R's role-driven evidence selection. It raised
the finalizer safety ceiling from 1,200 to 1,600 semantic-text characters while
keeping 1,200 as the drafting target, emitted zero-indent line-anchored JSON,
and prohibited manual evidence reconstruction after a second finalizer error.
Its bundle digest was
`sha256:745be487dc3b6e75a7fa2c28a1f786ffea0366c77853dd51070f2d0fd7155634`.

## Decision

Do not promote candidate S or any preceding development-only variant into
`skills/consult-semantic-okf-tantivy`.

S passed 4/4 development trials with a 1.0 pass rate, no errors, and complete
exact-evidence and mechanical qualification. The disjoint q010/q029 holdout
was evaluable with one attempt per task and zero retries, but both experimental
baseline R and candidate S had mean reward 0.0 and failed mechanical
qualification on both tasks. S additionally failed the exact-evidence gate on
q029. The strict Harbor gate therefore returned `keep-baseline` and
`promoted: false`.

Retain the checked-in standalone Tantivy consultant unchanged and keep it
outside the canonical registry. Preserve the proposal/configuration history
and the redacted compact report under
`evaluations/semantic-okf-tantivy/`. Treat R and S as experimental evidence,
not released skill implementations.

The holdout baseline was experimental candidate R rather than the checked-in
skill. Consequently, this decision rejects S as a promotion from R; it does
not infer that the checked-in skill outperforms either candidate.

## Consequences

Positive:

- the live skill cannot acquire a change that failed its sealed qualification
  boundary;
- exact evidence remains a mandatory gate rather than a soft reward component;
- the complete development path remains auditable without checking in raw
  Harbor artifacts or credentials; and
- future work can target q010/q029 mechanical completion from a frozen result.

Negative:

- the development improvements are not available in the published skill;
- two holdout questions are sufficient for a promotion gate but not for a
  broad quality estimate; and
- another disjoint evaluation is required before any later candidate can be
  promoted.
