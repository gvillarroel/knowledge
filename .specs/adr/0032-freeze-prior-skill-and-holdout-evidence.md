---
adr: "0032"
title: "ADR 0032: Freeze Prior Skills and Holdout Evidence During Iterative Evolution"
summary: "Compare a frozen prior skill with a candidate, separate development from qualification, and exclude infrastructure-failed adapter cells from semantic claims."
status: "Accepted"
date: "2026-07-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Agent Skill Evaluation"
tags:
  - skills
  - evaluation
  - skill-arena
  - holdout
  - reproducibility
---

# ADR 0032: Freeze Prior Skills and Holdout Evidence During Iterative Evolution

## Status

Accepted.

## Context

ADR 0015 establishes isolated no-skill and single-skill comparisons. Repeated evolution introduces another attribution problem: once development failures change a skill, the current path no longer represents the prior treatment, and rerunning the same prompts cannot demonstrate generalization. Multi-adapter matrices also risk treating timeouts, quota exhaustion, truncated planner output, or judge failures as semantic skill failures.

The second md2conf evolution exposed both concerns. A byte-identical prior snapshot enabled direct comparison after the canonical skill changed. A separately authored holdout prevented development prompts from becoming qualification evidence. The additional Antigravity route produced mostly infrastructure failures, while one semantic rubric rejected a workflow explicitly supported by the stable tool and skill contract.

## Decision

Extend the isolated evolution workflow with frozen prior and held-out evidence.

- Before editing a candidate, copy the complete prior skill package into an evaluation-owned snapshot and verify byte hashes.
- Keep development and qualification prompts in separate configs and fixture roots. Do not tune the candidate from qualification outputs within the same evolution pass.
- Compare no-skill, frozen-prior, and candidate profiles on identical qualification cells.
- Use raw runner statistics and artifact presence to distinguish infrastructure errors from semantic assertion failures. Exclude adapter routes dominated by timeouts, quota failures, or truncated progress output from semantic acceptance claims.
- Report raw rubric results before any manual adjudication. A manual correction is allowed only when the evaluator contradicts verified task or tool contracts; document the contradiction and show both raw and corrected results.
- Treat a targeted post-development regression as evidence for a specific repaired case, not as a replacement for the varied development or held-out corpora.
- Corroborate version-sensitive local-tool claims with deterministic execution on disposable copies when the external service itself is not authorized.

## Consequences

Positive:

- prior and candidate behavior remain attributable after canonical files change;
- development gains cannot be presented as unseen qualification;
- cross-adapter failures no longer become misleading semantic scores;
- evaluator defects remain auditable instead of silently changing acceptance;
- deterministic local evidence complements planning-only agent evaluations.

Negative:

- evaluation packages retain duplicated frozen skill files and additional reports;
- qualification matrices cost more model time and may encounter provider quotas;
- manual adjudication requires explicit technical evidence and cannot be reduced to one headline percentage;
- a non-regressing holdout does not by itself prove a held-out improvement.
