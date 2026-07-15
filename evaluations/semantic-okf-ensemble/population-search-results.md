# Definitive ensemble population search

Status: `pass`. The search selected a retrieval-ranking policy over the frozen forty-question benchmark.

## Execution

| Generations | Candidates per generation | Replays per candidate | Questions per replay | Effective parallelism | Candidate outcomes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 10 | 3 | 40 | 1 | 40 |

The evaluator executed 120 deterministic candidate replays, covering 4800 question rankings. Every candidate received a binary pass/fail gate outcome and a keep/discard decision. Thirty-seven candidate evaluations passed and three failed.

## Winner

The accepted variant is `generation-001/candidate-02` with fitness `91.8891506056`. It uses adaptive, graph-fusion, BM25, and embedding-hybrid weights `4:1:5:1`, RRF `k=7`, the consensus tie order, protected adaptive candidates, and the three-of-five graph-lexical promotion gate.

| Cohort | Recall@10 | MRR@10 | nDCG@10 | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| All 40 | 0.8381619769 | 1.0000000000 | 0.8520010048 | 1.0000000000 |
| Hard 10 | 0.9550000000 | 1.0000000000 | 0.8827017521 | 1.0000000000 |

## Generations and plateau

| Generation | Pass | Fail | Best fitness | Best variant |
| ---: | ---: | ---: | ---: | --- |
| 0 | 7 | 3 | 91.7248905513 | `generation-000/candidate-04` |
| 1 | 10 | 0 | 91.8891506056 | `generation-001/candidate-02` |
| 2 | 10 | 0 | 91.8891506056 | `generation-002/candidate-00` |
| 3 | 10 | 0 | 91.8891506056 | `generation-003/candidate-00` |

Generation one produced the final improvement. Generations two and three retained the same best fitness, satisfying the two-generation plateau. A ratio-equivalent doubled-weight candidate tied the winner in generation three, but the simpler 4:1:5:1 representation won the deterministic simplicity tie.

## Rejected alternatives

| Family | Best fitness | Outcome | Reason |
| --- | ---: | --- | --- |
| hard-gate failures | 0.0000000000 | discard | Adaptive-only missed the all-question nDCG floor; semantic-heavy and the initial smoothed RRF missed the hard-ten nDCG floor. |
| route and promotion ablations | 90.3020278981 | discard | Removing semantic scoring, using the fast route set, or removing graph promotion all passed gates but ranked below the accepted policy. |
| single-signal emphasis | 91.4579777857 | discard | BM25-heavy and graph-heavy generation-zero policies did not beat the later balanced lexical policy. |
| local weight neighbors | 91.8585298537 | discard | Nearby adaptive, graph, semantic, BM25, and smoothing changes passed but reduced balanced fitness. |
| larger smoothing constants | 91.8704663553 | discard | RRF constants eight and nine were stable but scored below seven. |
| ratio-equivalent scaling | 91.8891506056 | discard | Doubling every weight reproduced the winner exactly, so the simpler 4:1:5:1 representation won the deterministic simplicity tie. |

## Evidence boundary

The bound raw report is a pre-winner real route trace using weights 1:2:3:2 and RRF k=0. The population evaluator reused only its component rankings, protected paper sets, and independently valid evidence rows to replay candidate ranking policies. It did not rerun the selected policy through the live semantic runtime.

Final-03 adds bounded reviewed semantic-claim retrieval to the post-ranking `coverage-pack` operation. That gate prepares exact answer evidence only after the direct paper order has been selected; it does not change the paper-ranking routes, weights, RRF constant, protected candidate set, promotion rule, or tie order. The profile-gated MCP transport exposes the same coverage operation without altering that ranking policy. Accordingly, the selected ranking and its replay metrics remain applicable to final-03, while the accepted semantic coverage result is evaluated separately in `hard10-coverage-pack-multisignal-mcp-runtime-gate.json`.

Accordingly, this report supports deterministic ranking selection on a frozen optimization target. It does not measure generated-answer correctness or completeness and is not causal Skill Arena evidence. Real runtime, grounded-answer, and isolated Skill Arena control/treatment results are separate evaluations.
