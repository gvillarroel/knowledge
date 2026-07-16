# Endocrine-Hygiene Semantic OKF Build Comparison

Run: `20260715-endocrine-builds-05`
Status: **pass**
Corpus: 15 papers and 31 declared sources (30 authoritative paper/claim sources plus 1 auxiliary vocabulary).

| Family | Expected | Observed | Build validation | Determinism | Core hash |
| --- | --- | --- | --- | --- | --- |
| legacy | success | success | pass | pass | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| embeddings | success | success | pass | pass | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| classical | success | success | pass | pass | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| entity-graph | incompatible | expected-incompatibility | N/A | pass | `N/A` |
| adaptive | success | success | pass | pass | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| ensemble | incompatible | expected-incompatibility | N/A | pass | `N/A` |

## Gates

- Authoritative-core parity: **pass**.
- Two executions per family: **pass**.
- Entity-graph incompatibility is expected because authoritative BioC passage headings are not PDF-page headings.
- Ensemble incompatibility is expected because the unchanged adaptive component accepts only canonical versioned arXiv identity mappings while this corpus uses real PMCIDs.

Raw commands, stdout, stderr, bundle trees, and both attempts remain append-only under the ignored run directory. The JSON report retains exact hashes and bounded diagnostics.
