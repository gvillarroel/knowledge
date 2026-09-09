# Graphify: depth and fusion have a verified ranking opportunity

A local synthetic audit confirms that the frozen Graphify query function can change the returned document set when depth changes. It also demonstrates a case where visiting more nodes leaves the top ten unchanged. The frozen lexical fusion function changes order under the declared weight variants. **These are function fixtures; Graphify has no completed native EnterpriseRAG measurement in E7 at this checkpoint.**

## Traversal and authoritative document hydration

The audit runs the exact frozen `Snapshot.search` and concept-hydration methods with the installed Graphify 0.9.17 scoring, seed selection and breadth-first traversal. Two manually constructed directed graphs reference twelve synthetic Markdown records. Snapshot construction is a fixture; no knowledge builder or persisted-snapshot validation runs. Returned document hashes match the synthetic Markdown bytes in every case.

| Depth | Chain: visited / returned | Branch: visited / returned | Branch top ten unchanged from depth 1 |
| ---: | --- | --- | --- |
| 0 | 1 / 1 | 1 / 1 | No |
| 1 | 2 / 2 | 11 / 10 | Yes |
| 2 | 3 / 3 | 12 / 10 | Yes |
| 3 | 4 / 4 | 12 / 10 | Yes |
| 4 | 5 / 5 | 12 / 10 | Yes |
| 5 | 6 / 6 | 12 / 10 | Yes |
| 6 | 7 / 7 | 12 / 10 | Yes |

All seven depths cover the default depth 2 and the six declared variants. On the chain, deeper traversal adds eligible documents, returning one through seven records. On the branch, increasing depth from 1 to 2 visits twelve nodes instead of eleven, while the ordered top ten stays identical. This behavior follows the native ordering: query score first, distance second, then stable label and node identity. More graph reach alone does not establish a relevance gain.

## Lexical fusion and exact mutation attribution

A separate synthetic pair of graph and lexical ranked lists exercises the frozen reciprocal-rank fusion function at all four lexical weights: 0.5, 1, 2 and 4. It produces three distinct document orders; weights 2 and 4 tie on this fixture. This verifies a ranking opportunity without estimating an Enterprise effect or counting a successful candidate.

The frozen bridge requests ten graph results while lexical fusion is disabled. Enabling a positive lexical weight requests up to one hundred graph results and one hundred lexical results before fusion returns ten. A native gain from first enabling this mechanism would therefore belong to the complete declared consultation treatment, including its candidate-pool change.

The three rank-decay variants explicitly set lexical weight to 1 as well as `rrf_k` to 5, 20 or 60. Applying each variant to a synthetic parent with depth 3 and lexical weight 4 preserves depth and resets the weight to 1. If an actual retained parent has another weight, the next native comparison changes both fields; its result must not be attributed solely to rank decay. All changes remain within Graphify consultation, and other family profiles stay identical.

## Evidence scope

The host used Python 3.14.7, NetworkX 3.6.1 and Graphify 0.9.17. Loaded Graphify module hashes, frozen source hashes, exact synthetic rankings and fixture document hashes are retained in the aggregate. This host audit does not attest the Harbor container dependency environment or native build budget.

No benchmark query content or relevance label was used by the fixtures. The normal study guard performed mechanical digest verification. There were no Harbor calls, model calls, new candidates, scored questions, private-validation use or controller misses. The frozen E7 catalog and runtime remain unchanged. Only the original native family search can establish its baseline, gains, plateau and completed evaluation opportunity.

[Synthetic observations and source hashes](aggregate.json) · [All-family opportunity inventory](../strategy-coverage.md) · [Campaign](../README.md)
