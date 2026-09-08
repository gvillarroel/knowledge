# EnterpriseRAG evolution sweep

Native development ranking on 40 previously exposed queries and a reduced, reference-enriched 985-document corpus. All eight families completed their declared finite tactic catalogs or per-tactic three-miss plateaus. These are retrieval scores; official full-corpus answer quality is a different metric.

[All attempts](attempts.csv) · [All routes](routes.csv) · [Cost, time and quality](CTA.md) · [Strategy stopping ledger](strategies.md)

| Family | Treatment | Baseline nDCG@10 | Best nDCG@10 | Gain pp | New candidates |
|---|---|---:|---:|---:|---:|
| [embeddings](by-skill/embeddings.md) | construction | 63.19 | 63.19 | 0.00 | 6 |
| [ensemble](by-skill/ensemble.md) | construction | 55.66 | 61.37 | 5.70 | 18 |
| [graphify](by-skill/graphify.md) | consultation | 13.63 | 60.36 | 46.73 | 13 |
| [legacy](by-skill/legacy.md) | consultation | 57.50 | 59.62 | 2.12 | 10 |
| [turso](by-skill/turso.md) | consultation | 40.32 | 59.62 | 19.30 | 10 |
| [adaptive](by-skill/adaptive.md) | construction | 50.69 | 58.62 | 7.93 | 18 |
| [classical](by-skill/classical.md) | construction | 44.35 | 48.21 | 3.86 | 16 |
| [entity-graph](by-skill/entity-graph.md) | construction | 47.28 | 48.19 | 0.91 | 15 |

Every control contains that family's best completely measured historical Enterprise configuration, including pinned MiniLM where useful. Every number above is a fresh native measurement, with historical parity checked before any child. One aggregate Harbor case per family contains all 40 queries; this is one Enterprise source/annotation group, not 40 independent transfer cases.

The exact selected family and private gate outcome are reported separately in the campaign decision. Development maxima alone do not promote a canonical default.

![Baseline and best development scores](comparison.png)
