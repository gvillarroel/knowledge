---
adr: "0009"
title: "ADR 0009: Evaluate GraphRAG Synthesis with a Luna-Only Route"
summary: "Run the GraphRAG cross-paper benchmark exclusively with GPT-5.6 Luna and promote reader-skill changes through trace discovery and paired holdout validation."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags:
  - knowledge
  - evaluation
  - graphrag
  - pi
  - holdout
  - trace-evolution
---

# ADR 0009: Evaluate GraphRAG Synthesis with a Luna-Only Route

## Status

Accepted.

## Context

The GraphRAG study compares answers across fifteen version-pinned papers whose methods often use different terms for semantically related stages. A useful evaluation must isolate knowledge access, require evidence from multiple independent papers, and avoid mixing model-routing failures with semantic failures.

Model retries and an additional model-based judge would introduce different execution paths and extra calls. They would also make it harder to determine whether a completed answer failed because of its content or because a second request failed. Reader-skill changes need a separate anti-overfitting discipline because the same thirty questions are used to expose recurring procedural weaknesses.

This decision is scoped to `evaluations/graphrag-cross-paper/`. It does not rewrite the separately pinned Semantic OKF consultation benchmark or its historical results.

## Decision

The active GraphRAG benchmark will use one PI variant with model `openai-codex/gpt-5.6-luna` for every answer request. Its wrapper requires exactly one matching `--model` value, makes one attempt, enforces a process-tree timeout, and rejects any alternate route. The benchmark will not use a model-based judge. Six deterministic assertions score JSON format, the response contract, existing evidence paths, semantic structure, page citations, and cross-paper evidence.

The full baseline contains thirty prompts and two isolated profiles:

1. `no-skill` has neither the knowledge snapshot nor the reader skill.
2. `skill` has the pinned Semantic OKF snapshot and reader skill.

Each cell is a fresh request. No result is reused across the full baseline, the single-candidate holdout, or the paired confirmation run.

Reader-skill evolution uses a fixed split selected before inspecting candidate results:

- twenty-four discovery prompts provide success and failure traces;
- six prompts form a holdout: q005, q010, q015, q020, q025, and q029;
- the pre-change skill is copied into an immutable baseline directory;
- patch consolidation requires support from at least two independent discovery traces;
- a candidate is promoted only when the same deterministic evaluator shows improved or preserved holdout fitness;
- a paired run places the frozen baseline and unchanged candidate under the same model, prompts, knowledge revision, concurrency, and assertions.

The primary fitness is the fraction of cells that pass all six assertions. Assertion-level totals and failure categories remain mandatory diagnostics so a nominal success-rate increase cannot hide structural regressions.

## Consequences

Positive:

- every active GraphRAG answer follows the same model route;
- one completed answer requires one model call;
- technical transport state cannot be confused with a failed secondary judge;
- deterministic assertions make failures attributable to structure, source coverage, citations, or evidence paths;
- discovery traces can improve the general reading procedure without selecting patches from holdout outcomes;
- paired validation makes baseline-versus-candidate differences easier to interpret.

Negative:

- a single model route has no automatic recovery from quota or runtime failure;
- the deterministic rubric does not directly score prose style or every factual nuance;
- one request per cell leaves some sampling variance, so paired confirmation is required for promotion decisions;
- the two-profile full baseline measures the combined effect of skill plus knowledge access rather than the skill alone.
