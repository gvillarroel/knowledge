# Entity Graph: graph reach, rank fusion and document identity

Eight controlled function cases verify that the frozen graph-reach settings can change the retrieved document set. They also show why a candidate-edge weight change can leave the primary fusion unchanged: fusion uses component rank positions, so different magnitudes with identical component rankings produce the same fused scores. **These synthetic cases add no completed EnterpriseRAG trial or family baseline.**

## Exact functions and synthetic inputs

The audit uses the frozen source-generic plan parser, edge constructor, direct-entity scoring, traversal, ranking, reciprocal-rank fusion and document diversification functions. The synthetic inputs contain seven sections from four documents in one application, four candidate terms and thirteen mentions. The native constructor derives seven reviewed `partOfDocument` edges, thirteen candidate mention edges and three candidate co-mention edges. Section, entity and mention extraction, the resolved seed and lexical scores are fixtures.

Each mechanism includes its default configuration and all three declared variants. These are eight cases on the same fixture, not eight independent datasets or native evaluation tasks. Every adjusted plan passes the exact native parser and leaves the derived edge data unchanged.

| Mechanism | Maximum hops | Candidate-edge weight | Returned documents |
| --- | ---: | ---: | ---: |
| graph-reach / default | 3 | 0.3 | 4 |
| graph-reach | 1 | 0.3 | 2 |
| graph-reach | 2 | 0.3 | 3 |
| graph-reach | 4 | 0.3 | 4 |
| graph-noise / default | 3 | 0.3 | 4 |
| graph-noise | 3 | 0.0 | 1 |
| graph-noise | 3 | 0.1 | 4 |
| graph-noise | 3 | 0.6 | 4 |

At candidate-edge weight 0.3, hop settings 1, 2, 3 and 4 return two, three, four and four distinct documents. The runtime also adds mention contributions from reached entities after its edge-traversal loop. The hop setting therefore bounds that loop; it is not a separate claim that every returned section has a strict seed-to-section distance within that number.

## What an unchanged score would mean

At three hops, candidate-edge weights 0.1, 0.3 and 0.6 produce different traversal magnitudes but identical traversal section order, exact fusion score maps and final document order on this fixture. A weight mutation needs to change membership or component order before rank fusion can change. This is a conditional explanation for a possible tie, not evidence that edge weighting is exhausted on EnterpriseRAG.

Setting candidate-edge weight to zero leaves one document. The traversal path records no propagated edge, but direct-entity scores remain equal to their default values and mention-based traversal scores remain nonzero. This parameter controls candidate-edge propagation; it does not disable every contribution from candidate entities or mentions.

The default maximum of one section per document still allows all four documents from the same application. Multiple sections of one document are capped by its explicit document identity. This follows the [source-generic graph contract](../../../../../.specs/adr/0029-source-generic-evidence-graph-and-ensemble.md) and does not impose an application-level one-result cap.

## Native campaign boundary

The source hashes, exact synthetic component scores, rankings, plan hashes and compact fixture inventory are in the aggregate. The audit ran on local Python 3.14.7 and does not attest the Harbor container environment, native construction cost, persisted-snapshot validity or end-to-end query behavior. No benchmark query content or relevance label was used. The normal study guard performed mechanical digest verification.

No candidate was created, no controller miss consumed, no private validation opened and no frozen execution input changed. Entity Graph still requires its original native baseline and development search, including its BM25 and section-granularity mechanisms. Only those jobs can establish its EnterpriseRAG relevance, failures, stopping result and completed opportunity.

[Synthetic observations and source hashes](aggregate.json) · [All-family opportunity inventory](../strategy-coverage.md) · [Campaign](../README.md)
