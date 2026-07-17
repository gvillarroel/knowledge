# Semantic OKF Harbor Paired Comparison

Split: `dev`. Paired trials: 1. Status: `complete`.

| Metric | Baseline | Evolved | Delta |
|---|---:|---:|---:|
| quality_gate | 0.0000 | 1.0000 | +1.0000 |
| reward | 0.0000 | 0.9920 | +0.9920 |

Latency, tokens, and cost are diagnostic dimensions and are not folded into evidence quality.

- Baseline mean latency: 600.019192
- Evolved mean latency: 250.193212
- Baseline total cost: 0
- Evolved total cost: 0

Deterministic evidence metrics remain separate from semantic answer correctness. A failed quality gate cannot be offset by another score.
