# Interim comparison: baseline and neural-record

[Study overview](../README.md) · [Exact aggregate evidence](aggregates.json) · [Every paired default-route cell](cells.csv)

This is a snapshot of two fully completed development profiles from a five-profile generation. The other three profiles are still pending or running. It establishes neither a final ranking nor selection, independent validation or promotion. Validation remains sealed.

Each profile completed all 32 dataset-by-family cells with zero execution errors and evidence integrity 1 throughout. Native Harbor reporting verified their locks and trial results without a comparison warning. The table displays binary nDCG@10 on a 0–100 scale, equally averaged across the 32 predeclared family-default routes. These are reduced internal retrieval measurements, not official EnterpriseRAG answer-quality scores.

| Profile | Completed cells | Errors | Primary nDCG@10 | Native job wall min | Aggregate agent min, all routes | Provider charge USD |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 32 / 32 | 0 | 66.49 | 117.20 | 172.06 | 0.00 |
| neural-record | 32 / 32 | 0 | 67.72 | 110.04 | 161.62 | 0.00 |

Observed mean change: **1.22 percentage points**. Paired cells: **5 improved, 24 unchanged, 3 regressed**. Unrounded native values determine those counts. This observation does not select the candidate or open validation.

Native job wall time includes setup and concurrent execution. Aggregate agent time sums all 32 agents and includes two builds, validation, initialization and every declared route. These shared-host CPU timings describe the whole evaluation, not one production query or an isolated causal speedup. Instruction-model tokens and provider billing are zero; local execution cost is not priced.

## Dataset averages

Each row averages all eight predeclared family-default routes, not the strongest route.

| Dataset | Baseline | Neural-record | Change, pp |
|---|---:|---:|---:|
| architecture | 77.10 | 77.56 | 0.47 |
| astro | 70.43 | 69.88 | -0.54 |
| data-science | 73.59 | 77.08 | 3.49 |
| enterprise | 44.87 | 46.34 | 1.48 |

## Skill-family averages

Each row averages the four development datasets.

| Family | Baseline | Neural-record | Change, pp |
|---|---:|---:|---:|
| adaptive | 77.77 | 77.77 | 0.00 |
| classical | 74.97 | 74.97 | 0.00 |
| embeddings | 65.65 | 75.63 | 9.98 |
| ensemble | 78.94 | 78.74 | -0.20 |
| entity-graph | 71.37 | 71.37 | 0.00 |
| graphify | 45.90 | 45.90 | 0.00 |
| legacy | 70.69 | 70.69 | 0.00 |
| turso | 46.67 | 46.67 | 0.00 |

## Interpretation and next boundary

The source-generic neural profile replaces hashing with the pinned local MiniLM model in Embeddings and Ensemble, preserving record chunks and every consultation implementation. The other six families are controls. The cell CSV preserves every paired result, including regressions.

The full generation must finish before the owning controller's native archive can support complementary merges or final selection. The predeclared final-archive rule and one-way independent gate remain unchanged. This reporting step creates no archive, candidate, native evaluation, selection or private release; its original native evidence was checked unchanged before and after normalization.

All source questions, references, task identities, trajectories and raw native reports remain local and ignored. The public JSON contains only aggregate metrics, public taxonomy and source digests.
