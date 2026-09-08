# EnterpriseRAG: incoming versus G2 generator

**Result: retrieval is unchanged.** All 720 paired question/route cells returned identical ordered documents. All 18 routes have zero change in nDCG@10, Recall@10, MRR@10 and complete evidence coverage. The conditional request to push skill changes after an EnterpriseRAG improvement is not satisfied; no commit or push was made.

[By route](#complete-route-comparison) · [CTA](cta.md) · [Question categories](categories.md) · [Machine-readable comparison](comparison.json) · [Reproduction guide](../../../docs/enterprise-generator-comparison.md) · [Report hub](../README.md)

The fixed comparison uses 985 complete documents, 6,291,040 original body characters, nine source types, 40 previously exposed questions, eight knowledge families, and Top-10 retrieval. Sixteen builds and 1,440 direct query executions completed. This is a retrospective reduced-corpus diagnostic, not an official EnterpriseRAG full-corpus run, a new independent gate, or generated-answer accuracy.

The complete frozen generator inventories match the incoming parent and accepted G2 candidate from the construction study: native skill digest prefixes `db2a2d8d09f6` and `50341f2c7937`, respectively. No generator or consultant was mutated for this replay.

## Family comparison

Each row shows the highest observed route within that family for this fixed input; it does not select or promote a default. Scores use a 0–100 scale. Route choice is identical for both versions.

| Family | Highest observed route | Incoming nDCG@10 | G2 nDCG@10 | Change (points) |
|---|---|---:|---:|---:|
| legacy | legacy-lexical | 88.83 | 88.83 | 0.00 |
| embeddings | embeddings-lexical | 93.63 | 93.63 | 0.00 |
| classical | classical-bm25 | 97.85 | 97.85 | 0.00 |
| adaptive | adaptive-fusion | 95.12 | 95.12 | 0.00 |
| entity-graph | entity-graph-lexical | 95.43 | 95.43 | 0.00 |
| ensemble | ensemble-quality | 97.86 | 97.86 | 0.00 |
| graphify | graphify-search | 19.00 | 19.00 | 0.00 |
| turso | turso-lexical-sql | 69.40 | 69.40 | 0.00 |

## Complete route comparison

| Family / route | Incoming nDCG@10 | G2 nDCG@10 | Change | G2 Recall@10 | G2 MRR@10 | Identical pairs |
|---|---:|---:|---:|---:|---:|---:|
| ensemble-quality | 97.86 | 97.86 | 0.00 | 97.48 | 100.00 | 40/40 |
| classical-bm25 | 97.85 | 97.85 | 0.00 | 98.59 | 98.75 | 40/40 |
| ensemble-fast | 96.58 | 96.58 | 0.00 | 97.48 | 100.00 | 40/40 |
| entity-graph-lexical | 95.43 | 95.43 | 0.00 | 96.01 | 97.50 | 40/40 |
| adaptive-fusion | 95.12 | 95.12 | 0.00 | 97.48 | 98.75 | 40/40 |
| ensemble-robust | 95.12 | 95.12 | 0.00 | 97.48 | 98.75 | 40/40 |
| embeddings-lexical | 93.63 | 93.63 | 0.00 | 94.88 | 95.62 | 40/40 |
| classical-association | 90.33 | 90.33 | 0.00 | 88.64 | 98.75 | 40/40 |
| classical-fusion | 90.33 | 90.33 | 0.00 | 88.64 | 98.75 | 40/40 |
| classical-topic | 90.33 | 90.33 | 0.00 | 88.64 | 98.75 | 40/40 |
| legacy-lexical | 88.83 | 88.83 | 0.00 | 92.50 | 91.19 | 40/40 |
| embeddings-hybrid | 88.38 | 88.38 | 0.00 | 94.83 | 89.11 | 40/40 |
| entity-graph-fusion | 77.02 | 77.02 | 0.00 | 82.67 | 79.69 | 40/40 |
| embeddings-vector | 76.98 | 76.98 | 0.00 | 82.28 | 79.67 | 40/40 |
| entity-graph-entity | 75.19 | 75.19 | 0.00 | 81.30 | 77.50 | 40/40 |
| turso-lexical-sql | 69.40 | 69.40 | 0.00 | 77.36 | 71.48 | 40/40 |
| entity-graph-traversal | 56.17 | 56.17 | 0.00 | 69.51 | 56.52 | 40/40 |
| graphify-search | 19.00 | 19.00 | 0.00 | 23.85 | 23.30 | 40/40 |

## What G2 changes

All eight generated knowledge trees, native consultation scripts, consultation instructions, guidance and façade are byte-identical between versions. Each expert changes only `expert-manifest.json` and adds `references/source-coverage.json`. All 985 original bodies survive exactly in each of the sixteen experts.

G2 makes omitted structured-field decisions explicit and records normalized source coverage. Its separately accepted construction gate improved from 6/8 to 8/8 cases, through correct rejection of ambiguous inputs. That is a construction-contract improvement, not +25 points in EnterpriseRAG retrieval. See the unchanged [G2 construction report](../evolution/generator-g2/README.md).

## Historical comparisons and limits

The v1/e6 title-only scores use a different source-text contract. The S2 unified expert score of 84.26 measures final evidence selected by a language-model agent and uses another execution contract. Neither is a causal baseline for this direct complete-document replay. See the [historical ingestion audit](../enterprise-source-skills/ingestion-scope-20260907.md) and [S2 report](../enterprise-source-skills/s2/README.md).

No private validation was opened, no new mutation or application split was introduced, and no answer-generation model was called. Embeddings uses MiniLM at the existing pinned revision; Ensemble retains its deterministic hashing component. Complete storage does not remove the embedding encoder context limit. One query pass per version does not establish query stability or a speed advantage.

Before the successful replay, both versions rejected the same malformed guidance. The corrected guide was frozen in a new replay; the failed setup produced zero retrieval scores and is preserved locally.

The Turso adapter initially opened the published read-only database directly. Its engine required a sidecar and rejected that connection before any question was scored. Following the existing native consultant and ADR 0031, both versions were then scored on digest-checked temporary copies under `PRAGMA query_only=1`. The published experts remained read-only and byte-identical. The query SQL, metrics, skills, data and plans did not change; no semantic result was rerun. The adapter amendment is separately hash-bound.

Frozen comparison binding SHA-256: `5468e7a8694dda1b4721ce19b39a2fadb09ca40d4a4411e571ba30bb1fbadb67`. Construction and retrieval receipt hashes are included in the machine-readable report. Questions, qrels, source documents and raw results remain ignored.

## Verification closure

[All eight reconstruction and consultation checks](verification.md) passed. The application gate completed with 1,405 passing tests and 90.7% coverage. The unchanged-retrieval result and conditional no-push decision remain in force.
