# Semantic OKF Harbor Paired Comparison

Split: `train`. Paired trials: 1. Status: `complete`.

| Metric | Baseline | Evolved | Delta |
|---|---:|---:|---:|
| all_evidence_valid | 1.0000 | 1.0000 | +0.0000 |
| atomic_claim_evidence_completeness | 0.8000 | 0.6000 | -0.2000 |
| authoritative_evidence_completeness | 0.6667 | 0.6667 | +0.0000 |
| complete_qrel_coverage | 0.0000 | 0.0000 | +0.0000 |
| evidence_precision | 0.6667 | 0.2222 | -0.4444 |
| evidence_recall | 0.6667 | 0.6667 | +0.0000 |
| evidence_validity | 1.0000 | 1.0000 | +0.0000 |
| important_negative_evidence_completeness | 1.0000 | 0.5000 | -0.5000 |
| mrr | 1.0000 | 0.5000 | -0.5000 |
| ndcg | 0.7654 | 0.4776 | -0.2877 |
| non_null_answer | 1.0000 | 1.0000 | +0.0000 |
| quality_gate | 1.0000 | 1.0000 | +0.0000 |
| reference_validity | 1.0000 | 1.0000 | +0.0000 |
| required_document_coverage | 0.6667 | 0.6667 | +0.0000 |
| response_contract | 1.0000 | 1.0000 | +0.0000 |
| reward | 0.7665 | 0.6028 | -0.1638 |

Latency, tokens, and cost are diagnostic dimensions and are not folded into evidence quality.

- Baseline mean latency: 510.397687
- Evolved mean latency: 379.620811
- Baseline total cost: 0
- Evolved total cost: 0

Deterministic evidence metrics remain separate from semantic answer correctness. A failed quality gate cannot be offset by another score.
