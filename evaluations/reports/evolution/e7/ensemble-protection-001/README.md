# Ensemble: ranking opportunity inside a fixed Adaptive result set

The frozen source-generic Ensemble policy can change document order with route weights, but preserves exactly the document groups returned by its Adaptive component. **A controlled eight-case audit verified both behaviors.** This is a synthetic function audit; Ensemble has not yet completed a native EnterpriseRAG trial in E7.

## What was exercised

The audit executes exact AST copies of the frozen grouping, fusion, candidate-set gate and evidence-normalization functions. Snapshot construction and component payload delivery are fixtures. It uses 15 synthetic source-record identities, two protected-set sizes (ten and four), and the baseline plus all three declared quality-weight variants. The graph payloads include five independent records absent from the protected set. The embedding payload reverses the protected order and also includes those independent records in the four-protected-record fixture. The query and record content are synthetic; no benchmark question or reference label is read.

| Protected records | Quality weights: Adaptive / graph fusion / BM25 / embedding hybrid | Returned records | Outside records admitted | Order differs from the matching baseline |
| ---: | --- | ---: | ---: | --- |
| 10 | [4, 1, 5, 1] | 10 | 0 | No |
| 10 | [4, 1, 5, 3] | 10 | 0 | Yes |
| 10 | [2, 1, 3, 5] | 10 | 0 | Yes |
| 10 | [1, 1, 1, 8] | 10 | 0 | Yes |
| 4 | [4, 1, 5, 1] | 4 | 0 | No |
| 4 | [4, 1, 5, 3] | 4 | 0 | No |
| 4 | [2, 1, 3, 5] | 4 | 0 | Yes |
| 4 | [1, 1, 1, 8] | 4 | 0 | Yes |

Every case preserves the exact protected set. The weight-sensitive order changes show that allocation is an active ranking mechanism, rather than a universally inert parameter. With only four protected records, the result still contains four records; it does not backfill from independent auxiliary evidence. The fixture also executes the exact identity join and evidence normalization, but does not run a native build, persisted-snapshot validation or an embedding provider.

## Meaning for the upcoming native trials

With unchanged successful Adaptive output, changing only the quality weights or the embedding representation can reorder protected document groups. Such a change can affect nDCG and MRR, but cannot add document groups or improve recall and full-reference coverage through new documents. The E7 primary objective remains nDCG@10, so an actual ranking gain is a valid improvement even when recall is unchanged.

The Adaptive construction mutations in the Ensemble catalog can change the protected set itself and retain a separate opportunity to improve coverage. This audit does not predict the frequency or size of either kind of gain on EnterpriseRAG, establish a baseline score, count as a native opportunity, or consume a miss in the controller.

This protection is an intentional part of the [generic Ensemble contract](../../../../../.specs/adr/0029-source-generic-evidence-graph-and-ensemble.md). A future experiment that admits auxiliary document groups would change that contract and require a separate registered treatment with exact evidence, regression and independent-validation gates. No such candidate or new study is created here.

[Synthetic observations and source hashes](aggregate.json) · [All-family opportunity inventory](../strategy-coverage.md) · [Campaign](../README.md)
