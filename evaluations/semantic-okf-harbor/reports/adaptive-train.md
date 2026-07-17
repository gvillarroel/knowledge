# Semantic OKF Harbor Paired Comparison

Split: `train`. Paired trials: 1. Status: `complete`.

| Metric | Baseline | Evolved | Delta |
|---|---:|---:|---:|
| all_evidence_valid | 1.0000 | 1.0000 | +0.0000 |
| atomic_claim_evidence_completeness | 1.0000 | 1.0000 | +0.0000 |
| authoritative_evidence_completeness | 1.0000 | 1.0000 | +0.0000 |
| complete_qrel_coverage | 1.0000 | 1.0000 | +0.0000 |
| evidence_precision | 0.4286 | 0.6000 | +0.1714 |
| evidence_recall | 1.0000 | 1.0000 | +0.0000 |
| evidence_validity | 1.0000 | 1.0000 | +0.0000 |
| important_negative_evidence_completeness | 1.0000 | 1.0000 | +0.0000 |
| mrr | 0.5000 | 1.0000 | +0.5000 |
| ndcg | 0.6979 | 0.9469 | +0.2490 |
| non_null_answer | 1.0000 | 1.0000 | +0.0000 |
| quality_gate | 0.0000 | 1.0000 | +1.0000 |
| reference_validity | 0.0000 | 1.0000 | +1.0000 |
| required_document_coverage | 1.0000 | 1.0000 | +0.0000 |
| response_contract | 1.0000 | 1.0000 | +0.0000 |
| reward | 0.0000 | 0.9947 | +0.9947 |

Latency, tokens, and cost are diagnostic dimensions and are not folded into evidence quality.

- Baseline mean latency: 506.429902
- Evolved mean latency: 127.830116
- Baseline total cost: 0
- Evolved total cost: 0

Deterministic evidence metrics remain separate from semantic answer correctness. A failed quality gate cannot be offset by another score.
