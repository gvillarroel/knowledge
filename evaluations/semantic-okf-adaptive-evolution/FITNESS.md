# Frozen-Benchmark Fitness Contract

This contract governs fixed-benchmark evolution of the standalone `build-semantic-okf-adaptive` and `consult-semantic-okf-adaptive` pair. It was recorded before inspecting candidate answer-evidence scores. The immutable inputs are bound by `frozen-benchmark.json`; a benchmark correction requires a new benchmark ID rather than an in-place edit.

## Hard gates

A candidate is discarded if any gate fails:

1. The frozen-benchmark validator passes with manifest SHA-256 `2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414`.
2. Both standalone packages pass package validation and their focused tests.
3. Two real builds from the pinned manifest and adaptive plan validate independently and have identical sorted path-and-byte trees.
4. The authoritative core is unchanged, every returned evidence item validates, and the derived answer-binding artifact contains no frozen question ID.
5. All-40 adaptive paper Recall@10 and nDCG@10 do not regress from the frozen incumbent beyond `1e-8`, which accommodates the incumbent report's eight-decimal rounding.
6. Consultation remains read-only.

## Offline fitness

Passing candidates receive a score from 0 through 100 under one evaluator:

| Component | Weight | Definition |
| --- | ---: | --- |
| Retrieval preservation | 20 | 10 points each for all-40 paper Recall@10 and nDCG@10, capped at the incumbent value. |
| Atomic answer-claim recall | 30 | Macro exact recall at 30 of the curated `answer_claims[].evidence_claim_ids` over the hard 10. |
| Important-negative recall | 15 | Macro exact recall at 30 of `important_negatives[].evidence_claim_ids` over the hard 10. |
| Required-paper recall | 15 | Macro recall at 30 of the required paper identities over the hard 10. |
| Evidence-contract validity | 15 | Exact record, concept, claim-source, locator-token, integer-page, hash, and grouped-citation agreement with independently derived bindings. |
| Operational efficiency | 5 | `min(1, incumbent adaptive-search mean latency / candidate evidence-pack mean latency)`. This is diagnostic because the operations differ; it cannot compensate for a failed gate. |

Exact claim recall is intentionally identity-based. Semantic similarity cannot receive credit for a different claim because the hard ground truth records the authoritative evidence identities needed for each derivation and negative. The evaluator may inspect ground truth only after retrieval; neither skill, bundle, query, nor artifact receives expected claim IDs or answers.

Each hard question is executed three times per candidate in a sequential candidate run. All three structured outputs must be byte-equivalent by parsed JSON value; latency aggregates all 30 executions. Parallel exploratory timing cannot determine survivor order.

## Selection and causal evidence

Generation 0 contains ten explicitly named hypotheses, including untouched candidate 00. Every candidate receives a keep/discard decision under this contract. The top two passing candidates survive. Only finalists proceed to a frozen Skill Arena control/treatment comparison; a portfolio containing several skills is not causal evidence. Reuse of the hard 10 is disclosed as fixed-benchmark optimization, not holdout generalization.
