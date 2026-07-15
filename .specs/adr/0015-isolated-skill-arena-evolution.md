---
adr: "0015"
title: "ADR 0015: Evolve Skills with Isolated Skill Arena Comparisons"
summary: "Use one no-skill control and one single-skill treatment for causal skill evolution; retain the full portfolio only as a routing smoke."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Agent Skill Evaluation"
tags:
  - skills
  - evaluation
  - skill-arena
  - isolation
  - evolution
---

# ADR 0015: Evolve Skills with Isolated Skill Arena Comparisons

## Status

Accepted.

## Context

The initial portfolio smoke installed every repository skill in one treatment profile. It proved that the skill collection can route distinct planning requests and exposed broad regressions quickly, but it could not attribute a result to one skill. Each skill received only one prompt, unrelated skills could influence the same response, and exact command-token assertions produced false negatives for otherwise correct plans.

Durable skill evolution needs evidence that the changed package improves its own task surface without access to sibling skills or repository context. The evaluation must also distinguish external prerequisites from unsafe live mutations: Brave Search, remote `know` integrations, Television sources, and Confluence Cloud require offline or captured-response cases unless a separately authorized live benchmark exists.

## Decision

Use isolated Skill Arena comparisons as the default evolution unit for every canonical skill.

- Compare an isolated `no-skill` control with a treatment that installs exactly one copied canonical skill.
- Send identical prompts and workspace fixtures to both profiles; keep evaluator knowledge in assertions and fixtures rather than task prompts.
- For broad skills, cover at least two naturalistic cases, one generalization case, and one boundary or recovery case across at least three task families.
- Prefer deterministic artifact assertions for local runtimes and semantic assertions for plans. Do not require exact command spelling unless the user request itself requires an exact command contract.
- Keep network access disabled for the default evolution suite. Use local execution for deterministic scripts and offline planning or captured responses for external services.
- Treat the all-skills portfolio comparison as a routing smoke only. Do not use it to claim causal improvement for an individual skill.
- Preserve specialized high-coverage release gates such as the Semantic OKF reader and builder batteries. The isolated four-case compares are fast iteration surfaces, not replacements for deeper domain benchmarks.
- Run `val-conf`, the evaluation-design validator, and a Skill Arena dry-run before live execution. Inspect `merged/report.md` first and `summary.json` for prompt-level evidence.

## Consequences

Positive:

- observed gains and regressions are attributable to one skill;
- sibling skills cannot mask missing instructions or leak authority;
- prompt diversity and boundary behavior are checked before expensive runs;
- local and external-service skills receive appropriate safety-aware evaluation modes;
- false negatives from incidental wording become easier to distinguish from real workflow failures.

Negative:

- the repository maintains more evaluation configs and coverage files;
- a complete smoke requires at least two cells per prompt across eight skills;
- external-service behavior remains partly simulated until separately authorized live tests run;
- deep release batteries still require more time and model quota than the isolated iteration suites.
