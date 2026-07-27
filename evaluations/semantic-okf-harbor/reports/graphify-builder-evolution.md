# Graphify Builder Evolution

Date: 2026-07-20

Decision: promote the accepted `build-semantic-okf-harbor-graphify` implementation into the official `build-semantic-okf-graphify` skill for deterministic retrieval with the unchanged `consult-semantic-okf-graphify`. Retain the campaign-named package as historical evidence. Do not treat the change as a strict Harbor answer-compiler improvement.

## Frozen boundary

- The consultation skill was not edited. Both Harbor receipts bind the same consult tree SHA-256: `f27bf956b8656f62c3de8bf883a15a3cd3a60674826cabbf814f7b027f32917f`.
- The authoritative core is byte-identical across baseline and evolved bundles.
- Two independent final builds have graph logical SHA-256 `5541ba21da0116a435cbb60392327e03259c81049cfb6610266499837322366d`.
- The final graph preserves 6,390 nodes and adds 30 validated reciprocal cross-partition similarity edges: 6,389 → 6,419 edges.

## Full benchmark

| Bundle | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms |
|---|---:|---:|---:|---:|---:|---:|
| Baseline builder | 68.5% | 45.8% | 0.556 | 0.530 | 265/265 | 137.4 |
| Official promoted builder | **77.3%** | **57.5%** | **0.579** | **0.578** | 301/301 | 81.6 |

## Isolated cohorts

| Cohort | Bundle | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 |
|---|---|---:|---:|---:|---:|
| Discovery, 32 | Baseline | 66.4% | 46.9% | 0.470 | 0.467 |
| Discovery, 32 | Evolved | **73.7%** | 46.9% | **0.499** | **0.509** |
| Holdout, 8 | Baseline | 77.1% | 41.7% | 0.900 | 0.783 |
| Holdout, 8 | Evolved | **91.7%** | **100.0%** | 0.900 | **0.852** |

## Discovery mutations

| Mutation | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Mean ms | Decision |
|---|---:|---:|---:|---:|---:|---|
| Baseline | 66.4% | 46.9% | 0.470 | 0.467 | 82.9 | Control |
| Rare-token root label | 66.4% | 46.9% | 0.469 | 0.466 | 119.1 | Reject |
| First-occurrence root label | 66.4% | 46.9% | 0.469 | 0.466 | 120.0 | Reject |
| Unrestricted TF-IDF, K=3 | 64.8% | 46.9% | 0.473 | 0.473 | 85.5 | Reject |
| Unrestricted TF-IDF, K=1 | 70.1% | 42.7% | 0.489 | 0.489 | 82.6 | Reject: hard regression |
| Unrestricted TF-IDF, K=2 | 63.8% | 42.7% | 0.482 | 0.469 | 85.8 | Reject |
| Cross-partition TF-IDF, K=1 | 68.0% | 42.7% | 0.488 | 0.484 | 83.6 | Reject: hard regression |
| Reciprocal cross-partition TF-IDF, K=1 | **73.7%** | 46.9% | **0.499** | **0.509** | 87.6 | Freeze |

## Harbor trace

| q032 bundle | Reward | Response contract | All evidence valid | Complete qrel coverage | Required-document coverage | Diagnostic |
|---|---:|---:|---:|---:|---:|---|
| Baseline | 0.000 | 0 | 0 | 1.0 | 1.0 | Invalid `locator` shape |
| Evolved | 0.000 | 0 | 0 | 0.0 | 0.5 | Invalid `locator` shape |

The agent-level Harbor comparison is not positive. Both runs fail the same non-compensating response-contract gate because the frozen consult does not emit the grader's required locator and retained-text hash shape. The builder cannot repair that interface without violating the explicit no-consult-change boundary. Promotion is therefore limited to the direct consultation retrieval path demonstrated by the 40-question evaluation.
