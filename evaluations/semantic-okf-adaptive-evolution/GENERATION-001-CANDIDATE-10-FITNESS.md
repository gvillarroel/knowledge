# Adaptive Candidate Offline Fitness

Candidate: `candidate-10-facet-coverage-finalizer`. Frozen benchmark: `semantic-okf-adaptive-frozen-40-plus-hard10-v1`.

Hard-gate status: **pass**. Fitness: **81.62/100**.

| Metric | Value |
| --- | ---: |
| All-40 paper Recall@10 | 0.838162 |
| All-40 paper nDCG@10 | 0.834272 |
| Hard-10 atomic answer-claim Recall@30 | 0.600000 |
| Hard-10 important-negative claim Recall@30 | 0.750000 |
| Hard-10 required-paper Recall@30 | 0.980000 |
| Evidence-contract validity | 1.000000 |
| Mean evidence-pack latency (ms) | 554.694 |

## Gate checks

- PASS — frozen_benchmark: 2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414
- PASS — read_only: 891 files unchanged
- PASS — question_id_isolation: leaked IDs: []
- PASS — core_parity: pass
- PASS — retrieval_recall_no_regression: candidate 0.838161977; incumbent 0.838161980
- PASS — retrieval_ndcg_no_regression: candidate 0.834272030; incumbent 0.834272030
- PASS — retrieval_evidence_validity: 1.0
- PASS — answer_evidence_validity: 1.000000000

## Per-question exact retrieval

| Question | Answer claims | Negatives | Papers | Contract |
| --- | ---: | ---: | ---: | ---: |
| q031-graph-routing-boundary | 0.500 | 1.000 | 1.000 | 1.000 |
| q032-incremental-update-maturity | 0.600 | 1.000 | 0.800 | 1.000 |
| q033-corruption-specific-defenses | 0.500 | 1.000 | 1.000 | 1.000 |
| q034-nonmonotonic-context-budget | 0.500 | 0.500 | 1.000 | 1.000 |
| q035-lossless-enough-evidence-organization | 0.500 | 0.333 | 1.000 | 1.000 |
| q036-evaluation-leakage-and-stage-separation | 0.800 | 1.000 | 1.000 | 1.000 |
| q037-domain-construction-under-constraints | 0.800 | 1.000 | 1.000 | 1.000 |
| q038-failure-aware-query-router | 0.750 | 0.667 | 1.000 | 1.000 |
| q039-baseline-bound-efficiency-claims | 0.800 | 0.667 | 1.000 | 1.000 |
| q040-answer-source-control | 0.250 | 0.333 | 1.000 | 1.000 |
