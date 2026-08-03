# Registered Semantic OKF token ranking

This aggregate table keeps knowledge-folder construction and consultation as
separate units. Harbor input usage already includes cached input; therefore
total tokens are input plus output, while cache is shown only as a diagnostic
subset and is not added again.

## Knowledge-folder construction

Each value is the mean of two qualified one-folder builder calls. The two
independent replicas produced byte-identical knowledge trees for every
strategy.

| Rank (low to high) | Strategy | Folders | Mean input (cache included) | Mean cache (subset) | Mean output | Mean total tokens per folder |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Classical | 2 | 4,686.50 | 2,112.00 | 1,048.00 | 5,734.50 |
| 2 | Entity Graph | 2 | 5,002.50 | 2,240.00 | 1,296.50 | 6,299.00 |
| 3 | Embeddings | 2 | 5,625.00 | 2,496.00 | 918.00 | 6,543.00 |
| 4 | Adaptive | 2 | 5,816.00 | 3,264.00 | 1,066.00 | 6,882.00 |
| 5 | Legacy | 2 | 5,859.00 | 3,264.00 | 1,144.50 | 7,003.50 |
| 6 | Ensemble | 2 | 5,991.00 | 1,856.00 | 1,300.00 | 7,291.00 |
| 7 | Turso | 2 | 7,327.50 | 3,776.00 | 1,229.50 | 8,557.00 |
| 8 | Graphify | 2 | 8,009.00 | 4,352.00 | 1,827.00 | 9,836.00 |

The across-strategy construction mean is 7,268.25 total tokens per folder
across 16 qualified folders.

## Consultation

Each strategy received the same six held-out questions. The primary mean
includes every submitted query because failed queries still consume tokens.
The complete-response mean is diagnostic only: strategies with failures
completed different question subsets.

| Rank by submitted mean | Strategy | Submitted queries | Runtime errors | Complete responses | Mean total tokens per submitted query | Mean total tokens per complete response |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Graphify | 6 | 6 | 0 | 325,279.00 | — |
| 2 | Ensemble | 6 | 6 | 0 | 1,099,499.50 | — |
| 3 | Embeddings | 6 | 1 | 5 | 1,397,144.33 | 1,517,508.60 |
| 4 | Classical | 6 | 1 | 5 | 1,539,005.33 | 1,419,480.80 |
| 5 | Legacy | 6 | 0 | 6 | 1,585,536.83 | 1,585,536.83 |
| 6 | Adaptive | 6 | 2 | 4 | 1,871,644.67 | 1,612,571.75 |
| 7 | Turso | 6 | 0 | 6 | 2,109,545.83 | 2,109,545.83 |
| 8 | Entity Graph | 6 | 3 | 3 | 2,433,148.67 | 1,614,260.00 |

The overall submitted-query mean is 1,545,100.52 total tokens across 48
queries, including 19 runtime errors. Graphify and Ensemble are not valid
low-cost winners because neither produced a complete response. Among the two
zero-error strategies, Legacy is lower-cost and Turso is higher-cost.

## Deterministic retrieval helpers

All 25 registered direct-retrieval route variants make zero LLM calls and use
zero LLM tokens during retrieval. This scope excludes any later grounded
answer-generation agent.
