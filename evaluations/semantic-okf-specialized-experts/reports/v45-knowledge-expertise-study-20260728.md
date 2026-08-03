# V45 Knowledge-Expertise Harbor Study

Date: 2026-07-28

## Evaluation boundary

This study evolves `graphrag-trace-expert-v44` with a deterministic
knowledge-expertise planner followed by native Harbor 0.18.0 reflective Pareto
search. The development cohort is q031-q040 from `graphrag-papers-40`.
Every available retrieval cohort had prior exposure, so all claims are
retrospective. No Harbor holdout was opened and no formal promotion is claimed.

Every accepted Harbor job installs exactly one complete expert bundle. Pi
0.73.1 with `openrouter/openai/gpt-5.4-mini` reads the installed skill and
executes one fixed query-helper command. The verifier scores the raw retrieval
artifact and requires exact manifest binding, exact evidence binding, one
authoritative paper identity per result, finite metrics, and zero query or
verifier errors.

The accepted development job signature is
`sha256:538dd2b859ae808fea0b4f3891b3954635844808991fb24c7d27ec774adc518d`.
The shared development profile digest is
`sha256:f22acfc826407d5f9b88c47c31f6fb4fe4dc387ce41f490386e6323a92b611c8`.

## Skill Arena expertise planner

The new Skill Arena bundle
`harbor-maximize-knowledge-expertise` plans candidate portfolios without
evaluating them. It binds the target tree and sanitized development projection,
requires explicit expertise dimensions, emits only fixed benchmark-agnostic
operators, and leaves all fitness attribution to fresh native Harbor jobs.

The final four-file bundle digest is
`sha256:26a0b5a70494edad32078c3764803d16fcd228cd2128997ed9efcd22008f02cf`.
The v44 target digest is
`sha256:d00ad8df9a26bca34cbae86f6ad8a6ca816223d6083a2584eda144bfea7a26cb`;
the sanitized development evidence digest is
`sha256:83ed4d31703741ef327c56c2a34b301a8119afda60119e4ec46ff53b23948a17`;
and the self-sealed plan is
`sha256:bc8a2ec8c1d8f0f2aeb0586e8c891e14a57c10d11b8a60289374bc61dc876ea3`.

The plan covers five expertise dimensions: evidence fidelity, ranking
discrimination, retrieval breadth, robustness, and efficiency. It emits four
candidate operators and explicitly records zero Harbor calls, zero model calls,
zero reward reads, and zero holdout access during planning.

## Infrastructure correction

The first append-only live attempt used a deeply nested 323-character DrvFS
artifact path. Five baseline agents completed, but Harbor encountered
`OSError: [Errno 5] Input/output error` while collecting
`artifacts/logs/artifacts`; no verifier ran and no semantic result was accepted.

The diagnostic attempt remains unchanged and excluded. The accepted campaign
uses a 241-character output path. Dry-run and doctor passed again, and the
recomputed job signature remained byte-identical. All subsequent 80 accepted
trials completed with verifier results and zero errors.

## Pareto generations

Generation zero compares v44 with all four planner mutations.

| Candidate | Recall@10 | MRR@10 | nDCG@10 | Errors | Archive |
|---|---:|---:|---:|---:|---|
| Frozen v44 baseline | 95.50% | 83.33% | 80.7863% | 0 | No |
| Conservative gate | 95.50% | 83.33% | 80.6834% | 0 | Yes |
| Early-rank calibration | 95.50% | 83.33% | 80.8561% | 0 | Yes |
| Cost-aware routing | 95.50% | 83.33% | 80.7863% | 0 | No |
| Confidence-gated fusion | 95.50% | 83.33% | 80.8330% | 0 | Yes |

Early-rank calibration ties v44 on nine cases and improves q034. Confidence
gating ties v44 on nine cases and improves q036. Harbor emits a merge plan for
their complementary case strengths. The generation-zero seal is
`sha256:1258173f0231a1f085bf2ef40addaca41c141b9b770a098b8b686d8eec6774c5`.

The merged child changes only the bound query helper and manifest. It combines
RRF constant 20 with answer-independent top-rank overlap and trace-margin
weight gating. The realizer seals its tree as
`sha256:b97ae74c458a884d7e6f133f6ea7b6770d3b6413101cd3c4eae561f4d271c029`;
the operator realization seal is
`sha256:20712879125b110e3c89e6feea3d4cc8ccd69d377d30c7b29abf01f84ef0d3b9`.

Generation one reevaluates the baseline, early-rank incumbent, and merge.

| Candidate | Recall@10 | MRR@10 | nDCG@10 | Errors | Archive |
|---|---:|---:|---:|---:|---|
| Frozen v44 baseline | 95.50% | 83.33% | 80.7863% | 0 | No |
| Early-rank incumbent | 95.50% | 83.33% | 80.8561% | 0 | No |
| Early/confidence merge | 95.50% | 83.33% | 80.9028% | 0 | Yes |

The merge is the sole archive member. It preserves both parent improvements,
has no development-case regression against v44, and passes every required
reward gate. The generation-one seal is
`sha256:700e0f7c0384d714662e06444c97caea5170f4bfeea94920b566c752eae2c361`.

## Materialized v45

`build-specialized-skill` packages the selected helper as
`graphrag-trace-expert-v45` and reproduces the complete output byte for byte.

- retrieval contract: `trace-classical-early-confidence-v6`;
- query helper:
  `500687cab38cabdef53d1d6d3ebd8361cea7bc2f4d3a05097607ddccb0dd4eb1`;
- generated expert tree:
  `f7f13efebc041d8d4e6ebdc8cde6bd1a7c9623083446d2e2e94e15aca87e4f98`;
- expert manifest:
  `aaba0d020df54c7162b5a55c38320a05a04af741388d7b1f64ac7afbbb5995f9`;
- guidance:
  `b864b4c1d396dc9b6fd76e9de4ea8dfc18e6ee2ec27423c98c4b5ad0128e7cdb`;
  and
- unchanged 108-file knowledge tree:
  `e787e3ef4a2c2a3a624be0803a3536ab24c2dcdd66e4b894c2d0ec10634f1d9e`.

The package validator, manifest verification, representative search, and
byte-identical packaging check all pass.

## All-40 evaluation and rank

The frozen v45 package was evaluated independently at Top 10 and pool 100. The
Top-10 ranking is an exact prefix of the larger run for every question. All 400
Top-10 evidence rows validate, the query error count is zero, and both runs have
identical expert, knowledge, builder, packager, question, planner, Pareto, and
realization bindings.

| Version | Recall@10 | MRR@10 | nDCG@10 | P95 | Position |
|---|---:|---:|---:|---:|---:|
| V44 trace/classical hybrid | 84.97% | 92.08% | 83.47% | 568.22 ms | 3 of 24 |
| V45 early confidence-gated hybrid | 85.39% | 92.08% | 83.75% | 573.53 ms | 3 of 24 |
| Change | +0.42 pp | 0.00 pp | +0.29 pp | +5.31 ms | unchanged |

V45 remains below the `quality` and `fast` ensembles and above adaptive fusion.
This is a deterministic retrieval rank, not a grounded answer-quality rank.

## Promotion boundary

The planner, realizers, and Harbor archives all preserve the absence of an
untouched holdout. V45 is therefore an experimental package supported by
retrospective evidence. Formal promotion requires a newly registered cohort
that was not inspected during planning, mutation, or selection.
