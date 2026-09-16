# EnterpriseRAG: observed runtime phases

Each new original has a separate bounded journal. Complete means the exact 1,024-event sequence is present. A partial journal is censored evidence and never supplies a completed-prefix retrieval score. The native retrieval gate and telemetry completeness are separate facts.

| Strategy | Journal | Started queries | Completed queries | Observed events | Last event/phase |
| --- | --- | ---: | ---: | ---: | --- |
| entity-graph | complete | 500 | 500 | 1024 | completed/response-write |
| ensemble | partial | 265 | 264 | 549 | started/primary-query |

| Completed phase | entity-graph seconds | ensemble seconds |
| --- | ---: | ---: |
| skill-attestation | 0.01 | 0.01 |
| input-loading | 0.00 | 0.00 |
| planning | 0.17 | 0.17 |
| profile | 0.12 | 0.11 |
| knowledge-build | 360.05 | 1376.45 |
| knowledge-validate | 161.73 | 218.17 |
| rebuild-build | 371.78 | 1266.53 |
| rebuild-validate | 128.19 | 213.80 |
| build-parity | 2.86 | 3.38 |
| snapshot-initialization | 99.03 | 221.59 |
| final-integrity | 1.62 | Unavailable |
| response-write | 0.08 | Unavailable |

Planning contains profile application; do not add these nested durations twice. Snapshot initialization contains ledger loading and deep snapshot validation. Missing completion has no inferred duration or interruption cause. Journal I/O and concurrent neighbors affect timing. The original agent limit is 10,800 seconds and each child command keeps its 2,400-second limit; the separate native verifier keeps 180 seconds.

## What the unchanged query code explains

The frozen Ensemble quality policy requires five component routes: adaptive, bm25, embedding_hybrid, graph_fusion and graph_lexical. The adaptive component also runs full-query fusion and any decomposed aspects. One outer quality call can therefore perform several constituent searches.

The frozen Ensemble plan uses the hashing embedding provider. The optional sentence-transformer provider has an exact-configuration model cache, but that branch is inactive here. Entity Graph reuses only its immediately preceding computation across modes when the loaded snapshot, query and filters match. In contrast, Adaptive's non-adaptive search computes all four route-score maps before selecting the requested mode, including for a bm25 request. The full query is visited inside adaptive fusion and again by the separate bm25 component.

These are source observations, not component-level timing measurements. Reusing identical query work is a bounded hypothesis for a future study; no speedup or ranking improvement is established here. Any change must preserve score values, tie order, filters, evidence and snapshot/cache identity, and follow a separately registered validation protocol. This run changes none of these consultant functions.

Source binding within the frozen reference bundle: `_ensemble_snapshot.py` `fbaefb357a3571f6ba2ed8f93a89ef94a66ee00e399985efb58c378cf7bac467`; `_adaptive_snapshot.py` `14a645d0782a12a50d9a0d92b763d0b79545df74c200ccafede33ed04df4b56e`; `_entity_graph_snapshot.py` `805aa0de5ddaff9b25ee71d9e560b511ccb6ea52182145abb407c02ebcaadd51`. All three are under the Ensemble consultant's scripts directory. The pre-registered plan and complete reference commitments remain bound by the [aggregate provenance](aggregate.json).

The read-only lifecycle observer confirmed removal of all four native environments and their exact anonymous workspace volumes. No native retries occurred. [Quality and outcomes](README.md) · [CTA](cta.md)
