# Evidence Drill-Down Evaluation

Fusion first selects up to ten distinct books without qrel access. BM25 then retrieves a bounded number of pages inside each selected book. This is an exact-page diagnostic, not answer-quality scoring.

| Route | Pages per selected book | Source recall | Mean locator recall | Micro locator recall | Any locator coverage | Full locator coverage | Average pages opened |
|---|---:|---:|---:|---:|---:|---:|---:|
| single-pass-fusion | — | 0.917 | 0.067 | 0.071 | 0.200 | 0.000 | 5.9 |
| fusion-source-selection-plus-filtered-bm25 | 1 | 0.917 | 0.067 | 0.071 | 0.200 | 0.000 | 5.9 |
| fusion-source-selection-plus-filtered-bm25 | 3 | 0.917 | 0.133 | 0.143 | 0.400 | 0.000 | 17.7 |
| fusion-source-selection-plus-filtered-bm25 | 5 | 0.917 | 0.233 | 0.250 | 0.500 | 0.000 | 29.5 |
| fusion-source-selection-plus-filtered-bm25 | 10 | 0.917 | 0.300 | 0.321 | 0.600 | 0.000 | 59.0 |

The machine-readable companion preserves only source identities, locators, and hashes; private passage text is excluded.
