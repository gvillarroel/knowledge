# Semantic OKF Embedding Evaluation Summary

## Outcome

The embedding-enabled builder and consultant processed the same pinned GraphRAG corpus as the legacy Semantic OKF workflow. The evaluated input set contains 15 Markdown papers and 15 claim JSONL files. The historical vocabulary JSONL remains a required thirty-first core-build input, but it is explicitly excluded from the retrieval projection.

The new build preserves the complete authoritative snapshot byte for byte and adds a non-authoritative retrieval layer:

- authoritative core: 31 declared sources, 874 records, and 884 files;
- retrieval selection: all 30 requested sources, 846 selected records, and only `analysis-vocabulary` excluded;
- retrieval output: 1,811 chunks and 1,811 normalized 384-dimensional vectors;
- splitter: LlamaIndex semantic splitter with buffer size 1 and percentile threshold 90;
- embedder: `sentence-transformers/all-MiniLM-L6-v2` at revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, offline on CPU;
- validation: 30/30 raw inputs verified, zero retrieval errors, and 100% evidence validity under exact ledger, identity, text-hash, concept-path, and locator checks.

The compact schema 1.2 comparison was recomputed over all 30 questions on July 13, 2026. All 1,200 hits in
the top-10 report and all 11,980 hits in the top-100 report passed the stronger evidence-binding
audit. The complete append-only run passed in 1,212.112 seconds and is recorded locally at
`results/runs/20260713-compact-final/run-manifest.json`. Compact hits retain identities, hashes,
lengths, and exact locators without repeating raw evidence text; this reduced the top-10 JSON from
30,900,535 to 1,505,708 bytes and the top-100 JSON from 81,104,537 to 13,282,367 bytes.

The first final build completed in 163.197 seconds and an independent rebuild completed in
190.314 seconds. Their complete output trees were byte-identical at
`1a1f4883a9824fa44b1ec039ff37b9e86a5a04239c6b3ebce2493df66321b920`. An earlier fresh legacy
rebuild completed in 33.5 seconds and was byte-identical to the historical bundle.

## Core parity and size

The legacy and embedding-enabled bundles have the same 884 non-retrieval files and the same logical core-tree SHA-256:

`331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`

The record ledger, source manifest, ontology, data, shapes, provenance, and validation graphs all have identical byte hashes. The embedding layer therefore changes discovery only; it does not change OKF identity, accepted RDF facts, provenance, or validation evidence.

| Bundle | Files | Bytes | Difference |
| --- | ---: | ---: | ---: |
| Legacy | 884 | 10,888,503 | baseline |
| Embedding-enabled | 888 | 21,808,060 | +10,919,557 bytes (+100.3%) |

The additional bytes are exactly the four retrieval artifacts: index, chunks, embeddings, and build report.

## Primary retrieval comparison

The primary comparison retrieves a pool of 100 chunks, maps hits to paper identities, keeps the first rank for each identity, and then calculates the fixed Recall@1/3/5/10, MRR@10, and nDCG@10 cutoffs. This avoids treating repeated chunks from one paper as separate relevant papers.

| Route | Paper Recall@10 | Paper MRR@10 | Paper nDCG@10 | Source Recall@10 | Errors | Evidence validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy lexical | 0.7886 | 0.8611 | 0.8002 | 0.3943 | 0 | 100% |
| New lexical | 0.7813 | **0.9167** | **0.8028** | 0.4040 | 0 | 100% |
| Vector | 0.7392 | 0.8278 | 0.7436 | 0.3922 | 0 | 100% |
| Hybrid | 0.7728 | 0.8889 | 0.7736 | **0.4309** | 0 | 100% |

The legacy lexical route retains the highest aggregate paper Recall@10 by 0.0073 over the new lexical route. The new lexical route has the best first-relevant-result behavior and nDCG. Hybrid retrieval has the best source-level Recall@10 and improves paper Recall@10 over new lexical on 8 of 30 questions, ties on 15, and loses on 7. Vector retrieval improves over new lexical on 6 questions, ties on 13, and loses on 11.

Hybrid gains are concentrated in questions about the common pipeline, local versus global queries, vector/graph combinations, LLM roles, online efficiency, fact-checking versus QA, optimization operators, and static versus agentic retrieval. Vector gains are concentrated in the common pipeline, vector/graph combinations, online efficiency, grounding and safety, optimization operators, and static versus agentic retrieval.

## Chunk-concentration diagnostic

A second comparison evaluates only the first 10 raw chunks before paper-level deduplication. It exposes retrieval concentration rather than document coverage:

| Route | Raw-pool paper Recall@10 | Raw-pool paper nDCG@10 |
| --- | ---: | ---: |
| Legacy lexical | 0.7886 | 0.8002 |
| New lexical | 0.4850 | 0.5931 |
| Vector | 0.4687 | 0.5534 |
| Hybrid | 0.4273 | 0.5381 |

The gap between the raw-pool and identity-collapsed results shows that semantic chunks frequently concentrate several high ranks in the same paper. Consumers that need broad cross-paper synthesis should retrieve a deeper candidate pool and collapse or diversify by the target evidence identity. Consumers that need the best local passage should retain chunk-level ranking.

## Latency interpretation

The legacy timing reuses one in-process index and measures only search. Each new-route timing starts a fresh CLI process and includes full snapshot validation, optional model loading, retrieval, serialization, and parsing. The measured means for the identity-collapsed run were 3.1 ms for legacy lexical, 1.31 seconds for new lexical, 6.19 seconds for vector, and 6.61 seconds for hybrid. These figures prove standalone end-to-end behavior but are not an isolated algorithm-speed comparison. A persistent service that retains the validated snapshot and model in memory was not benchmarked.

## Recommendation

Keep embeddings optional and preserve lexical retrieval as a first-class route. Use lexical search for identifiers, rare terms, and broad corpus coverage; use vector search for paraphrases; use hybrid search when semantic recall and source diversity matter. For broad synthesis, request more chunks than the final evidence count and collapse by the intended evidence identity before applying ranking cutoffs. Always open the returned authoritative concept path before citing a claim.

Machine-readable and generated reports:

- `comparison-report-pool100.json` and `comparison-report-pool100.md`: primary identity-collapsed evaluation;
- `comparison-report.json` and `comparison-report.md`: first-10-chunk concentration diagnostic;
- `input-inventory.json`: exact input hashes and auxiliary contract;
- `retrieval-questions.jsonl`: the 30 questions and reviewed qrels;
- `retrieval-plan.json`: the pinned splitter and embedding configuration.
- `results/runs/20260713-compact-final/run-manifest.json`: local append-only execution evidence,
  including tool, runtime, command, timing, model, deterministic-tree, log, and report hashes.
