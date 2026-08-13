# Integrated Classical Knowledge Skill Parity Verification

| Dataset | Records | Questions | Query-route cells | Exact payloads | Rank mismatches | Hit citations | Legacy logical paths | Citation gain | Knowledge files equal | Runtime bytes equal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| graphrag-papers-40 | 874 | 40 | 160 | 160/160 | 0 | 1600/1600 | 1417/1600 | +183 | 47/47 | 1/1 |
| astro-40 | 416 | 40 | 160 | 160/160 | 0 | 1600/1600 | 1600/1600 | +0 | 432/432 | 1/1 |
| quantum-error-correction-papers-40 | 15 | 40 | 160 | 160/160 | 0 | 1527/1527 | 1527/1527 | +0 | 31/31 | 1/1 |

Result: **PASS**. The generated experts matched all 480 separate-stack query payloads exactly across 120 canonical questions and four routes, with 0 ranking mismatches and 0 payload mismatches.

All 1305 authoritative records and all 4727 retained hits have verified physical citations. The generated citation contract resolves 183 retained hits whose legacy logical `concept_path` is intentionally not a physical file in the source-packed layout.

Each dataset also passed a public generated-skill fusion query, deep snapshot validation, exact knowledge-tree comparison, and exact classical-runtime comparison. The generated skills default to `fusion` while retaining explicit `bm25`, `topic`, `association`, and `fusion` routes.

Boundary: This is a deterministic build, retrieval, and citation parity evaluation. It is not a new model-judged Harbor answer-quality run.
