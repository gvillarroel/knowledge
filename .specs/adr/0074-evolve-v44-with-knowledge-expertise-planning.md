# ADR 0074: Evolve v44 with knowledge-expertise planning

## Status

Accepted on 2026-07-28 for an experimental deterministic retrieval candidate
and retrospective ranking. This is not a holdout-qualified promotion or a
grounded answer-quality claim.

## Context

ADR 0073 materialized `graphrag-trace-expert-v44` after retrospective Harbor
Pareto search. V44 reached 84.97% Recall@10, 92.08% MRR@10, and 83.47%
nDCG@10 on the canonical all-40 retrieval contract, placing it 3 of 24.

The preceding search improved the aggregate result substantially, but it did
not define a reusable contract for maximizing expertise across evidence
fidelity, ranking discrimination, retrieval breadth, robustness, and
efficiency. Ad hoc mutation also made it harder to prove that candidate
instructions were derived only from sanitized development evidence.

All registered GraphRAG retrieval cohorts had already been exposed. The six
registered holdout questions therefore remained unavailable for promotion.

## Decision

Add the atomic `harbor-maximize-knowledge-expertise` skill to the Skill Arena
repository. Its deterministic planner:

- binds the target skill and sanitized development evidence by SHA-256;
- requires evidence-fidelity and robustness gates plus at least one additional
  expertise dimension;
- emits a bounded portfolio from a fixed, benchmark-agnostic operator library;
- performs no Harbor, model, candidate-selection, holdout, or promotion action;
  and
- requires fresh native Harbor jobs for downstream fitness attribution.

The final planner bundle digest is
`sha256:26a0b5a70494edad32078c3764803d16fcd228cd2128997ed9efcd22008f02cf`.
Its v44 plan seal is
`sha256:bc8a2ec8c1d8f0f2aeb0586e8c891e14a57c10d11b8a60289374bc61dc876ea3`.

Use the plan to realize four copied v44 candidates:

- conservative regression gating;
- early-rank calibration;
- cost-aware signal routing; and
- confidence-gated fusion.

Evaluate the baseline and all four candidates on q031-q040 with separate
native Harbor 0.18.0 jobs, Pi 0.73.1, and
`openrouter/openai/gpt-5.4-mini`. Require exact manifest binding, evidence
binding, and mechanical qualification rewards on every trial.

Generation zero retains three non-dominated candidates. Early-rank calibration
improves q034 without a regression, while confidence-gated fusion improves q036
without a regression. Follow Harbor's emitted merge plan and realize one child
that combines the lower RRF constant with answer-independent overlap and
trace-margin weight gating.

Generation one reevaluates the frozen baseline, the early-rank incumbent, and
the merged child. The child is the only archive member and reaches 80.90%
nDCG@10 on q031-q040, compared with 80.79% for v44. The generation seals are:

1. `sha256:1258173f0231a1f085bf2ef40addaca41c141b9b770a098b8b686d8eec6774c5`;
2. `sha256:700e0f7c0384d714662e06444c97caea5170f4bfeea94920b566c752eae2c361`.

Package the exact merged helper as `graphrag-trace-expert-v45`. Its retrieval
contract is `trace-classical-early-confidence-v6`, with RRF constant 20,
trace weight 1.0, default classical weight 2.0, and answer-independent
confidence gating. Evaluate the frozen package at Top 10 and pool 100 on all 40
questions. Replace the v44 row rather than counting two versions of the same
expert.

## Consequences

- V45 reaches 85.39% Recall@10, 92.08% MRR@10, and 83.75% nDCG@10 on all 40
  questions.
- Relative to v44, Recall@10 rises by 0.42 percentage points and nDCG@10 by
  0.29 points; MRR@10 is unchanged.
- V45 remains position 3 of 24, below the `quality` and `fast` ensembles.
- Selected P95 latency rises from 568.22 ms to 573.53 ms.
- All 400 Top-10 evidence rows validate, every query succeeds, and the Top-10
  run is an exact prefix of the pool-100 run.
- The first live Harbor attempt used a 323-character DrvFS artifact path and
  failed during post-agent artifact collection before verification. It is
  retained only as diagnostic evidence. The accepted append-only campaign used
  a 241-character output path and the identical job signature.
- V45 remains experimental because no untouched holdout exists. A newly
  registered, unseen cohort is required for formal promotion.
- This decision evaluates deterministic retrieval only. It does not assign a
  grounded answer-quality rank to the expert guidance.
