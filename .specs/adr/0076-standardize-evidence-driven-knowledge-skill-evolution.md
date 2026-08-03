# ADR 0076: Standardize evidence-driven knowledge skill evolution

## Status

Accepted on 2026-07-28.

## Context

The repository now contains several valid but distinct ways to improve
knowledge skills: GEPA instruction evolution, trace distillation, reflective
Pareto search, scalar population search, and candidate/operator coevolution.
The v43–v48 GraphRAG work also showed that knowledge construction, expert
packaging, retrieval adaptation, and consultation quality are separate layers.

Without one routing contract, a future study could select an unsuitable search
method, modify more than one layer in a treatment, expose holdout during
development, treat external failures as semantic zeroes, or call a
retrospective retrieval winner promoted.

## Decision

Adopt `docs/knowledge-skill-evolution-playbook.md` as the repository workflow
for creating, evaluating, evolving, and promoting knowledge skills. Link it
from the root `AGENTS.md` so agents must read it before doing this work.

The workflow requires:

1. `skill-creator` to define or update the skill contract;
2. `harbor-organize-evaluations` before any promotion-capable study;
3. one matched `build-semantic-okf-*` family and isolated execution mode;
4. `build-specialized-skill` when the deliverable is a snapshot-bound expert;
5. `harbor-run-results` for a complete digest-bound baseline;
6. one primary evolution controller per development stage;
7. `harbor-realize-skill-candidate` for unmaterialized mutation contracts;
8. retries only through `harbor-resume-external-failures` and only for proven
   external failures;
9. frozen selection before the one-time untouched holdout release; and
10. promotion only when the exact evaluated digest passes every declared gate.

Trace distillation and Pareto search may be composed in separate stages:
distillation derives evidence-cited hypotheses, candidate realization seals
them, and Pareto search preserves complementary case-level strengths or proposes
bounded merges. A retrospective study with no untouched holdout may publish an
experimental ranking but cannot promote the candidate.

## Consequences

- Agents have one explicit order and decision matrix for all available Harbor
  evolution skills.
- Builder quality and consultant or adapter quality remain causally separable.
- Candidate materialization, evaluation, selection, retry, and promotion have
  distinct owners and append-only evidence.
- Strong retrospective results remain usable without being mislabeled as
  holdout qualification.
- The workflow adds planning and evidence overhead, especially for small
  experiments, but a study that skips those gates must avoid promotion claims.
