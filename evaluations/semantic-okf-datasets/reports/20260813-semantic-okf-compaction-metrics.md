# Semantic OKF compaction metrics — 2026-08-13

## Evaluation boundary

This report compares fresh `record-per-file-v1` and `source-packed-v1` builds
made with the current repository code. The physical concept layout is the only
controlled builder variable. The frozen GraphRAG corpus contains 874 logical
records from 31 sources, and retrieval uses the same 40 reviewed questions at
top 10 for both layouts.

The input inventory SHA-256 is
`007a2c4ecbb7802fbb2ea2ca4dc57d3dbf96189d12f19d2db3e5b934bd0207a0`,
the question-set SHA-256 is
`21ca640514c7378c06f3e2a1a02210d079c5c3048fd2d07b14ade15f1c9788ec`,
and every structured-strategy build has the same authoritative ledger SHA-256,
`df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc`.
The prepared manifest SHA-256 is
`a4e83ce7d9630bf57ce4b3c2bf2cb445e34032c3ec46673b4bbed585885b0c37`.

Recall, MRR, and nDCG use binary reviewed qrels after retaining the first rank
per paper or source identity. Evidence validity is stricter than file
existence: every hit must bind to the authoritative ledger, retain exact text
and hashes, resolve a safe locator, and, for packed records, match the expected
collection anchor and complete record body. P95 latency is an operational
observation from one local run and is not a causal cross-family speed ranking.

## Result

| Measure | Record per file | Source packed | Change |
|---|---:|---:|---:|
| Logical records | 874 | 874 | 0 |
| Concept Markdown files | 874 | 31 | -96.45% |
| Concept Markdown bytes | 2,929,939 | 1,887,513 | -35.58% |
| Frontmatter bytes | 1,115,328 | 33,597 | -96.99% |
| Frontmatter share of concept bytes | 38.07% | 1.78% | -36.29 pp |
| Concept files below 4 KiB | 859 | 0 | -100% |
| Compacted ranked routes | 20 | 20 | 0 removed |
| Route-question ranking comparisons | 800 | 800 | 0 mismatches |
| Valid retained hits on compacted routes | 7,998 | 7,998 | 100% valid |
| Worst paper/source quality-metric delta | — | 0.000000 | no regression |

Across all fourteen independently materialized builder packages in the table
below, total files fall from 11,624 to 665 (-94.28%) and total bytes fall from
468,216,932 to 449,894,497 (-3.91%). Retrieval indexes dominate the larger
bundles, so file-count and repeated-metadata savings are much larger than total
byte savings.

## Complete physical bundle table

`Files`, `bytes`, concept files, small files, and frontmatter share are measured
recursively from each fresh bundle. The two RustMallet builder packages are
listed separately because they are independently installable, although their
current build artifacts are identical. Query-only consultant variants are not
double-counted as physical bundles.

| Physical builder | Total files, old -> new | File reduction | Total bytes, old -> new | Byte reduction | Concept files | Concept files <4 KiB | Frontmatter share |
|---|---:|---:|---:|---:|---:|---:|---:|
| Legacy | 884 -> 41 | 95.36% | 11,024,180 -> 9,847,299 | 10.68% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Embeddings | 888 -> 45 | 94.93% | 21,968,853 -> 20,791,972 | 5.36% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Classical | 890 -> 47 | 94.72% | 33,981,934 -> 32,805,053 | 3.46% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Adaptive | 891 -> 48 | 94.61% | 34,715,762 -> 33,538,881 | 3.39% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Entity graph | 891 -> 48 | 94.61% | 30,122,450 -> 28,945,569 | 3.91% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Ensemble | 904 -> 61 | 93.25% | 64,768,522 -> 63,591,641 | 1.82% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Graphify | 886 -> 43 | 95.15% | 31,933,160 -> 30,578,741 | 4.24% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Turso | 885 -> 42 | 95.25% | 52,545,332 -> 48,878,083 | 6.98% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Graphify Next | 886 -> 43 | 95.15% | 31,933,160 -> 30,578,741 | 4.24% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Harbor Graphify | 886 -> 43 | 95.15% | 31,933,160 -> 30,578,741 | 4.24% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Tantivy | 890 -> 47 | 94.72% | 33,383,251 -> 32,206,370 | 3.53% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| RustMallet | 890 -> 47 | 94.72% | 34,476,310 -> 33,299,429 | 3.41% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| RustMallet evolved builder | 890 -> 47 | 94.72% | 34,476,310 -> 33,299,429 | 3.41% | 874 -> 31 | 859 -> 0 | 38.07% -> 1.78% |
| Tika-Mallet physical bundle | 63 -> 63 | 0.00% | 20,954,548 -> 20,954,548 | 0.00% | 15 -> 15 | 0 -> 0 | 1.81% -> 1.81% |

Tika correctly remains unchanged because its 15 normalized inputs are
substantive extracted Markdown documents, not repeated structured rows. Merging
them merely to improve a file-count statistic would weaken document identity
and is therefore outside the accepted compaction rule.

## Complete current ranked-retrieval table

The first twenty routes were rerun against both fresh layouts. `Mismatches`
counts questions whose ranked paper/source identities or retained hit list
differed. `Worst delta` is the minimum compact-minus-baseline delta across the
six displayed paper/source quality metrics. All aggregate values and all
per-question rankings were exactly equal. The eight Tika routes use the same
unchanged physical bundle, so their layout delta is identically zero.

| Route | Paper R@10 | Paper MRR@10 | Paper nDCG@10 | Source R@10 | Source MRR@10 | Source nDCG@10 | Valid evidence | P95 ms | Mismatches | Worst delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `legacy_lexical` | 0.793113 | 0.789583 | 0.742192 | 0.396557 | 0.789583 | 0.601416 | 400/400 | 3.77 | 0/40 | 0.000000 |
| `new_lexical` | 0.547473 | 0.888333 | 0.608343 | 0.280195 | 0.887500 | 0.484716 | 400/400 | 63.02 | 0/40 | 0.000000 |
| `vector` | 0.503991 | 0.787500 | 0.547193 | 0.295919 | 0.783333 | 0.481410 | 400/400 | 130.99 | 0/40 | 0.000000 |
| `hybrid` | 0.481451 | 0.900000 | 0.567455 | 0.270656 | 0.897917 | 0.476295 | 400/400 | 222.89 | 0/40 | 0.000000 |
| `entity_graph_lexical` | 0.797568 | 0.966667 | 0.811427 | 0.398784 | 0.966667 | 0.652463 | 400/400 | 194.01 | 0/40 | 0.000000 |
| `entity_graph_entity` | 0.795811 | 0.860417 | 0.767227 | 0.397905 | 0.860417 | 0.620432 | 400/400 | 202.16 | 0/40 | 0.000000 |
| `entity_graph_traversal` | 0.784907 | 0.802083 | 0.740257 | 0.392454 | 0.802083 | 0.596473 | 400/400 | 204.48 | 0/40 | 0.000000 |
| `entity_graph_fusion` | 0.808420 | 0.931250 | 0.798622 | 0.404210 | 0.931250 | 0.642468 | 400/400 | 202.60 | 0/40 | 0.000000 |
| `classical_bm25` | 0.497199 | 0.958333 | 0.609370 | 0.278981 | 0.954167 | 0.511501 | 400/400 | 90.16 | 0/40 | 0.000000 |
| `classical_topic` | 0.824174 | 0.933333 | 0.822497 | 0.412087 | 0.933333 | 0.657527 | 400/400 | 98.10 | 0/40 | 0.000000 |
| `classical_association` | 0.825602 | 0.945833 | 0.825824 | 0.412801 | 0.945833 | 0.659646 | 400/400 | 96.73 | 0/40 | 0.000000 |
| `classical_fusion` | 0.834591 | 0.958333 | 0.832286 | 0.417295 | 0.958333 | 0.665229 | 400/400 | 97.73 | 0/40 | 0.000000 |
| `adaptive_fusion` | 0.838162 | 0.958333 | 0.834272 | 0.419081 | 0.958333 | 0.666819 | 400/400 | 346.35 | 0/40 | 0.000000 |
| `ensemble_quality` | 0.838162 | 1.000000 | 0.851790 | 0.419081 | 1.000000 | 0.679496 | 400/400 | 902.34 | 0/40 | 0.000000 |
| `graphify` (registered, Next, and Harbor) | 0.552930 | 0.840417 | 0.617301 | 0.312224 | 0.839167 | 0.523211 | 400/400 | 204.11 | 0/40 | 0.000000 |
| `tantivy_bm25` | 0.807409 | 0.937500 | 0.810533 | 0.403704 | 0.937500 | 0.651021 | 400/400 | 47.03 | 0/40 | 0.000000 |
| `rust_mallet_bm25` | 0.497199 | 0.958333 | 0.609370 | 0.278981 | 0.954167 | 0.511501 | 400/400 | 97.00 | 0/40 | 0.000000 |
| `rust_mallet_topic` | 0.808003 | 0.950000 | 0.818649 | 0.404002 | 0.950000 | 0.654660 | 399/399 | 100.86 | 0/40 | 0.000000 |
| `rust_mallet_association` | 0.794897 | 0.945833 | 0.808417 | 0.397449 | 0.945833 | 0.647975 | 400/400 | 100.78 | 0/40 | 0.000000 |
| `rust_mallet_fusion` | 0.802825 | 0.958333 | 0.818402 | 0.401412 | 0.958333 | 0.654453 | 399/399 | 99.18 | 0/40 | 0.000000 |
| `tika_mallet_bm25` | 0.815038 | 0.877083 | 0.800370 | 0.407519 | 0.877083 | 0.647089 | 400/400 | 85.33* | same bundle | 0.000000 |
| `tika_mallet_topic` | 0.821179 | 0.884167 | 0.805406 | 0.410589 | 0.884167 | 0.649100 | 400/400 | 82.40* | same bundle | 0.000000 |
| `tika_mallet_association` | 0.785911 | 0.860417 | 0.780004 | 0.392955 | 0.860417 | 0.631147 | 400/400 | 86.64* | same bundle | 0.000000 |
| `tika_mallet_fusion` | 0.748173 | 0.875000 | 0.754360 | 0.374086 | 0.875000 | 0.610941 | 400/400 | 86.36* | same bundle | 0.000000 |
| `tika_mallet_tantivy_tantivy` | 0.776536 | 0.836458 | 0.748340 | 0.388268 | 0.836458 | 0.608883 | 400/400 | 522.60* | same bundle | 0.000000 |
| `tika_mallet_tantivy_topic` | 0.784442 | 0.864167 | 0.752220 | 0.392221 | 0.864167 | 0.612378 | 400/400 | 530.84* | same bundle | 0.000000 |
| `tika_mallet_tantivy_association` | 0.758569 | 0.830833 | 0.724226 | 0.379284 | 0.830833 | 0.590085 | 400/400 | 474.08* | same bundle | 0.000000 |
| `tika_mallet_tantivy_fusion` | 0.735018 | 0.847917 | 0.717507 | 0.367509 | 0.847917 | 0.585052 | 400/400 | 470.74* | same bundle | 0.000000 |

`*` Tika timing is retained from its digest-bound canonical report because the
physical Tika bundle did not change. Its quality rows contribute 3,200 valid
hits out of 3,200. The Tika bounded consultant uses the same retrieval snapshot
as Tika-Mallet and is therefore not duplicated as another route.

The registered Graphify, Graphify Next, and Harbor Graphify builds all produce
the same 10,797-node, 13,504-edge graph with SHA-256
`cbce57ea1c66deed82367cc8d4935d06c6b8541d7a7edcf7d0416f2e9b3610e9`.
Each compact graph is byte-identical to its record-per-file baseline.

The reference-aware RustMallet consultation mutation is also not duplicated as
an independent ranking row: its canonical 320 route-question comparisons had
zero ranking mismatches against RustMallet. The native reference-dictionary
builder candidate remains deliberately unpromoted because its holdout included
a negative task delta. The current `build-semantic-okf-rust-mallet-evolved`
package therefore remains the quality-preserving baseline builder shown in the
physical table.

## Turso parity

Turso exposes exact read-only records, RDF statements, and SQL rather than a
ranked top-10 route, so Recall, MRR, and nDCG do not apply. Both layouts pass
full database validation with 874 records, 874 concepts, 31 sources, 8,574
attributes, and 18,435 RDF statements. The complete record query is byte
identical across layouts with SHA-256
`cd51abe2903726f6ed98640a28fb70b5bddc9d6401286b8f36aad7ef55f330c7`;
the complete RDF query is byte identical with SHA-256
`823817cb59cf3697ba6ab06d08157c8a63caa30b0d174df65fc4d8aebbf11bf5`.
The database-level logical digests differ only because stored physical concept
and layout-bound artifact content intentionally differs.

## Acceptance conclusion

The accepted optimization changes physical materialization only. It removes no
logical record, evidence candidate, RDF assertion, provenance statement, or
retrieval route. There were no empty normalized GraphRAG records that could be
deleted safely, so size-based deletion remains rejected. Source-level packing
is accepted because it achieves the file and metadata reduction while every
measured quality metric, ranked hit, and exact-query result is preserved.
