# EnterpriseRAG E14: Graphify depth-zero cost, time and quality

Each row is its original native observation. Both report zero model calls and provider cost; host and orchestration costs are unpriced. Timing differences are descriptive and were not tested for significance. The primary route is `search`.

| Candidate | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 8.12 | 3086.715 | 3037.652 | 2920.905 | 830.242 | 240091223 | 0.0 |
| versioned-001 | 7.03 | 3101.809 | 3055.472 | 2938.085 | 841.188 | 240091223 | 0.0 |

The depth-zero observation spent 2,938.085 seconds in the required two builds and 3,101.809 seconds in the native job overall. This is the measured cost of the fixed evaluation workflow, not an independently measured steady-state consultation service.

[Result and accounting](README.md) · [Paired groups](groups.md) · [Current retained-family CTA](../turso-generation-002-001/cta.md)
