---
adr: "0011"
title: "ADR 0011: Use GPT-5.6 Luna Exclusively for Active Semantic OKF Evaluations"
summary: "Remove GPT-5.3 and cross-model fallback from every active Semantic OKF benchmark route while preserving completed results as history."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags:
  - evaluation
  - semantic-okf
  - luna
  - reproducibility
---

# ADR 0011: Use GPT-5.6 Luna Exclusively for Active Semantic OKF Evaluations

## Status

Accepted.

This decision supersedes the active model-routing and cross-model fallback portions of ADR 0007. It extends the Luna-only constraint recorded for the GraphRAG evaluation in ADR 0009 to every active Semantic OKF builder and consultant benchmark.

## Context

The original consultation benchmark attempted GPT-5.3 first and used GPT-5.6 Luna as a runtime or result-derived fallback. That design made a completed score a mixture of model behavior, fallback policy, and skill access. It also conflicted with the requirement that the current tests evaluate GPT-5.6 Luna directly and consistently.

Completed result files must still describe what actually ran. Rewriting them to claim a different model would destroy provenance, so the routing change applies to active generators, manifests, wrappers, and future runs rather than historical evidence.

## Decision

All active Semantic OKF evaluation cells invoke `openai-codex/gpt-5.6-luna` directly through PI. Active manifests and wrappers must not reference GPT-5.3, Spark, a primary/fallback model pair, or any cross-model retry path.

Technical or semantic retries may be generated only as explicit GPT-5.6 Luna calls. Reports must identify those calls as retries and must replace, rather than cherry-pick against, the selected failed cell when producing a composite score.

Historical manifests, results, reports, and frozen skill snapshots remain immutable. Documentation must label any mixed-model or formerly combined-skill artifact as historical and must not expose it as the default active command.

## Consequences

Positive:

- every active score has one unambiguous model identity;
- skill/control comparisons no longer depend on a hidden cross-model routing policy;
- builder and consultant benchmarks use the same model family and can be interpreted consistently;
- historical experimental provenance remains intact.

Negative:

- prior mixed-model scores are not directly comparable to new Luna-only scores;
- a Luna outage produces a failed or incomplete cell instead of routing to another model;
- resuming old runs requires an explicit historical workflow rather than the active benchmark command.
