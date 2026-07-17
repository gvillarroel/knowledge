# Semantic OKF Harbor Paired Comparison

Split: `dev`. Paired trials: 1. Status: `complete`.

| Metric | Baseline | Evolved | Delta |
|---|---:|---:|---:|
| all_evidence_valid | 1.0000 | 0.0000 | -1.0000 |
| atomic_claim_evidence_completeness | 1.0000 | 0.8000 | -0.2000 |
| authoritative_evidence_completeness | 1.0000 | 0.8333 | -0.1667 |
| complete_qrel_coverage | 1.0000 | 0.0000 | -1.0000 |
| evidence_precision | 0.6667 | 0.2500 | -0.4167 |
| evidence_recall | 1.0000 | 0.5000 | -0.5000 |
| evidence_validity | 1.0000 | 0.7500 | -0.2500 |
| important_negative_evidence_completeness | 1.0000 | 1.0000 | +0.0000 |
| mrr | 1.0000 | 0.5000 | -0.5000 |
| ndcg | 1.0000 | 0.3869 | -0.6131 |
| non_null_answer | 1.0000 | 1.0000 | +0.0000 |
| quality_gate | 1.0000 | 0.0000 | -1.0000 |
| reference_validity | 1.0000 | 1.0000 | +0.0000 |
| required_document_coverage | 1.0000 | 0.5000 | -0.5000 |
| response_contract | 1.0000 | 1.0000 | +0.0000 |
| reward | 1.0000 | 0.0000 | -1.0000 |

Latency, tokens, and cost are diagnostic dimensions and are not folded into evidence quality.

- Baseline mean latency: 147.944442
- Evolved mean latency: 196.578191
- Baseline total cost: 0
- Evolved total cost: 0

Deterministic evidence metrics remain separate from semantic answer correctness. A failed quality gate cannot be offset by another score.
