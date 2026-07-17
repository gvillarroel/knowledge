# Semantic OKF Harbor Paired Comparison

Split: `train`. Paired trials: 1. Status: `complete`.

| Metric | Baseline | Evolved | Delta |
|---|---:|---:|---:|
| quality_gate | 0.0000 | 1.0000 | +1.0000 |
| reward | 0.0000 | 0.6221 | +0.6221 |

Latency, tokens, and cost are diagnostic dimensions and are not folded into evidence quality.

- Baseline mean latency: 600.100505
- Evolved mean latency: 141.121586
- Baseline total cost: 0
- Evolved total cost: 0

Deterministic evidence metrics remain separate from semantic answer correctness. A failed quality gate cannot be offset by another score.
