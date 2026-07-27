---
adr: "0052"
title: "ADR 0052: Retain RustMallet Skills After Provider-Blocked Distillation"
summary: "Keep the live RustMallet builder and consultant unchanged because the preserving-prepare candidate passed local qualification but produced no evaluable Harbor development or holdout evidence."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - rust-mallet
  - harbor
  - trace-distillation
  - evidence
---

# ADR 0052: Retain RustMallet Skills After Provider-Blocked Distillation

## Status

Accepted.

This decision extends ADR 0045. It neither reverses the prior native-builder
rejection nor adds RustMallet to the canonical eight-family Harbor registry.

## Context

Two qualified consult discovery traces showed repeated orchestration around the
existing `search` and `show` commands. A schema-2 trace-distillation candidate
therefore combined those operations while preserving all successful retrieval
interpretations, selected authoritative text, legacy commands, and the bounded
breadth buffer.

The candidate passed structural validation, Python compilation, and a real
snapshot preparation check. Promotion still requires candidate development on
the exact discovery tasks and a separate untouched holdout.

## Decision

Retain both live RustMallet skills and keep the new candidate isolated.

The Spark development job completed two Harbor trials, but both ended with a
provider quota signal before agent execution. The strict external-failure audit
did not permit retries because nonzero auxiliary scorer gates conflicted with
the external classification. A consistently paired non-Spark preflight was
also non-evaluable because the model is unsupported for the account.

Do not interpret either provider result as a semantic reward of zero. Do not
open or replace the reserved q005/q020 holdout, and do not promote from local
qualification alone.

## Consequences

- `skills/build-semantic-okf-rust-mallet-evolved` remains the builder baseline
  retained by ADR 0045.
- `skills/consult-semantic-okf-rust-mallet-evolved` remains the selected
  reference-aware consultant.
- The preserving-prepare assets and deterministic proposal generator remain
  available for a fresh append-only campaign.
- A future campaign must use one supported model profile with usable quota,
  pass q007/q019 development at 100%, and only then open q005/q020.
- The provider-blocked runs do not change canonical retrieval metrics or the
  general comparison table.

## Evidence

See
`evaluations/semantic-okf-rust-mallet/preserving-prepare-trace-distillation-summary.json`
and its Markdown companion for trace IDs, candidate digest, mechanical
qualification, provider classifications, resume audit, and holdout isolation.
