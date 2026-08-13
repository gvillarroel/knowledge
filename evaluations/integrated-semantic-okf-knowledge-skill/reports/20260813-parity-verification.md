# Canonical Multi-Family Direct Knowledge Skill Parity Verification

| Dataset | Family | Records | Knowledge files | Consult files | Native query | Façade | Hit citations | Exact get |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| astro-40 | legacy | 416 | 426/426 | 12/12 | 1/1 | 1/1 | 5/5 | 1/1 |
| astro-40 | embeddings | 416 | 430/430 | 10/10 | 1/1 | 1/1 | 5/5 | 1/1 |
| astro-40 | classical | 416 | 432/432 | 7/7 | 1/1 | 1/1 | 5/5 | 1/1 |
| astro-40 | adaptive | 416 | 433/433 | 8/8 | 1/1 | 1/1 | 5/5 | 1/1 |
| astro-40 | entity-graph | 416 | 433/433 | 9/9 | 1/1 | 1/1 | 5/5 | 1/1 |
| astro-40 | ensemble | 416 | 447/447 | 17/17 | 1/1 | 1/1 | 5/5 | 1/1 |
| astro-40 | graphify | 416 | 428/428 | 8/8 | 1/1 | 1/1 | 1/1 | 1/1 |
| astro-40 | turso | 416 | 427/427 | 9/9 | 1/1 | 1/1 | 5/5 | 1/1 |
| graphrag-papers-40 | legacy | 874 | 41/41 | 12/12 | 1/1 | 1/1 | 5/5 | 1/1 |
| graphrag-papers-40 | embeddings | 874 | 45/45 | 10/10 | 1/1 | 1/1 | 5/5 | 1/1 |
| graphrag-papers-40 | classical | 874 | 47/47 | 7/7 | 1/1 | 1/1 | 5/5 | 1/1 |
| graphrag-papers-40 | adaptive | 874 | 48/48 | 8/8 | 1/1 | 1/1 | 5/5 | 1/1 |
| graphrag-papers-40 | entity-graph | 874 | 48/48 | 9/9 | 1/1 | 1/1 | 5/5 | 1/1 |
| graphrag-papers-40 | ensemble | 874 | 61/61 | 17/17 | 1/1 | 1/1 | 5/5 | 1/1 |
| graphrag-papers-40 | graphify | 874 | 43/43 | 8/8 | 1/1 | 1/1 | 3/3 | 1/1 |
| graphrag-papers-40 | turso | 874 | 42/42 | 9/9 | 1/1 | 1/1 | 5/5 | 1/1 |
| quantum-error-correction-papers-40 | legacy | 15 | 25/25 | 12/12 | 1/1 | 1/1 | 5/5 | 1/1 |
| quantum-error-correction-papers-40 | embeddings | 15 | 29/29 | 10/10 | 1/1 | 1/1 | 5/5 | 1/1 |
| quantum-error-correction-papers-40 | classical | 15 | 31/31 | 7/7 | 1/1 | 1/1 | 5/5 | 1/1 |
| quantum-error-correction-papers-40 | adaptive | 15 | 32/32 | 8/8 | 1/1 | 1/1 | 5/5 | 1/1 |
| quantum-error-correction-papers-40 | entity-graph | 15 | 32/32 | 9/9 | 1/1 | 1/1 | 5/5 | 1/1 |
| quantum-error-correction-papers-40 | ensemble | 15 | 46/46 | 17/17 | 1/1 | 1/1 | 5/5 | 1/1 |
| quantum-error-correction-papers-40 | graphify | 15 | 27/27 | 8/8 | 1/1 | 1/1 | 1/1 | 1/1 |
| quantum-error-correction-papers-40 | turso | 15 | 26/26 | 9/9 | 1/1 | 1/1 | 5/5 | 1/1 |

Result: **PASS** across 24 dataset-family cells, 8 canonical families, and 960 bound question cells. All complete knowledge trees and matched consultation packages are byte-identical to the separate stack.

All 24 separate-versus-packaged native query probes and all 24 façade projections matched. All 110 retained hits and 24 exact-record probes resolved locally.

Equivalence basis: Complete knowledge-tree byte equality plus complete consultation-instruction, reference, and runtime byte equality establishes behavior equality for every bound question. One default-route native and façade payload is additionally executed per dataset-family cell.

Boundary: This is a deterministic build, consultation-runtime, query-façade, and citation parity evaluation. It is not a new model-judged Harbor answer-quality run.
