# ADR 0100: Require Proposition Alignment for Contradiction Review

## Status

Accepted on 2026-08-09 for the Classical visualizer approval candidate.

This is a retrospective development decision. It does not promote a knowledge
builder or consultation skill and does not claim holdout-qualified semantic
performance.

## Context

The first contradiction-review projection aligned reviewed claims by a shared
method identifier, contrasting claim roles, rare shared words, and broad
positive, negative, or negation cues. On the real GraphRAG Classical bundle it
returned 30 review candidates from 22,710 same-subject pairs.

Manual review of all 30 candidate interpretations found no logical
contradiction. The observed pairs were compatible restatements, different
analysis dimensions, quality-versus-efficiency trade-offs, partial improvement
versus residual failure, or results under different scopes. The resulting
precision was therefore 0 of 30 on this exposed retrospective audit. Broad
lexical polarity is useful for discovery, but it is not a sufficient display
gate for a section labeled as contradictions.

## Decision

- Rename the projection contract to `classical-contradiction-review/2.0` and
  separate source-declared relations from strict review candidates.
- Display an explicit contradiction relation only as `source-declared`; do not
  call it independently confirmed.
- Admit a structured candidate when the same normalized proposition key has
  opposite declared polarity.
- Admit a lexical candidate only when both claims share the same structured
  subject and analysis dimension, at least three rare proposition anchors, and
  near-identical proposition context. Require exactly one of these conflict
  forms:
  - direct, unambiguous negation;
  - an unambiguous direction reversal from a controlled opposition family; or
  - one conflicting numeric value in otherwise nearly identical context.
- Reject ambiguous constructions such as `not only`, `not always`, mixed
  positive and negative direction on one side, different dimensions, and
  insufficiently aligned conditions or baselines.
- Retain broad lexical matches only as aggregate quality-audit counts. Do not
  expose rejected pairs in the contradiction queue.
- Provide local filters for text, source-declared versus strict status,
  same-source versus cross-source evidence, and strict conflict type.
- Keep every strict candidate labeled as review-required and preserve both
  record identities, concept paths, source identities, and evidence locators.

## Consequences

- The real audit bundle now reports 30 loose signals rejected and zero
  qualified contradictions instead of displaying 30 false positives.
- Precision is favored over recall. Valid contradictions may remain hidden
  when the source metadata lacks normalized subjects, proposition keys,
  predicates, qualifiers, baselines, populations, or time scopes.
- Reliable cross-source detection depends on builders emitting shared semantic
  identifiers or explicit contradiction relations; the visualizer will not
  guess that two paper-local method identifiers denote the same proposition.
- A strict lexical candidate is still not a truth judgment. Users must inspect
  both authoritative evidence locations before accepting it.
- The exposed 30-pair audit may guide this development revision but cannot
  support a broader promotion claim. Future quality claims require a separate,
  frozen labeled cohort with contradictions and hard negatives.
