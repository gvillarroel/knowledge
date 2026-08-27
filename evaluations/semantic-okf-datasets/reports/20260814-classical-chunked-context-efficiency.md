# Classical chunked context efficiency

Status: **pass**

This is a deterministic retrospective regression. It verifies unchanged classical
retrieval, exact evidence reconstruction, citation presence, context guard behavior,
and provider-visible payload size. It is not a sealed semantic promotion result.

## Aggregate

- Datasets: 3
- Questions/cells: 120/120
- Full classical retrieval parity: 100.00%
- Default quality-guard pass rate: 100.00%
- Effective quality-guard pass rate: 100.00%
- Exact chunks reconstructed and digest-checked: 1951
- Context byte reduction: 80.42%
- Estimated-token reduction: 83.34%

## Per dataset

| Dataset | Cells | Retrieval parity | Default guard | Effective guard | Byte reduction | Estimated-token reduction |
|---|---:|---:|---:|---:|---:|---:|
| graphrag-papers-40 | 40 | 100.00% | 100.00% | 100.00% | 58.94% | 60.19% |
| astro-40 | 40 | 100.00% | 100.00% | 100.00% | 89.86% | 91.85% |
| quantum-error-correction-papers-40 | 40 | 100.00% | 100.00% | 100.00% | 64.26% | 65.52% |

## Interpretation boundary

The candidate retains the complete immutable knowledge tree and the original
classical search path. The compact context is a derived discovery projection;
linked chunks can be hydrated from exact ledger character ranges, and full search
remains available as a fail-closed diagnostic fallback.

The token metric is the skill's deterministic lexical/UTF-8 proxy. It must not be
reported as native provider billing or as a semantic-quality result.
