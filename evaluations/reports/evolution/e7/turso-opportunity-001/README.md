# Turso: SQL baseline and in-memory BM25 consultation

The frozen Turso treatments can change ranking, but their execution must be described precisely. The baseline uses a parameterized SQL substring-presence comparator. A nonempty evolution profile reads the canonical records from the same Turso database and runs BM25 in memory. The registered route remains `lexical-sql` in both cases. **This audit adds no EnterpriseRAG score or completed native family opportunity.**

## What the controlled audit executed

The exact frozen Turso builder created two independent bundles from twelve authored Markdown files belonging to one synthetic logical source. Both builds passed OKF, semantic, database-integrity and database-to-bundle validation, with twelve records, twelve concepts and one source. Their logical database digests match. Full read-side verification also passed for both database revisions.

The runtime smoke test passed on local CPython 3.14.7 with the actual `pyturso==0.6.1` distribution and Turso Database engine. The published databases were quiescent before consultation. Queries used verified scratch copies with `PRAGMA query_only=1`; both published byte hashes remained unchanged. Every returned record exactly matched its canonical database JSON.

Three synthetic queries were run through the exact SQL comparator and the frozen `LexicalIndex` implementation. The eleven declared Turso variants were each applied independently to the baseline profile, producing twelve configurations and thirty-six query calls including the SQL baseline. These calls do not simulate the controller's evolving parent sequence and do not select a candidate.

| Synthetic query | Distinct orders across the eleven BM25 configurations |
| --- | ---: |
| `photon` | 4 |
| `quasar` | 6 |
| `quasar photon` | 9 |

These counts establish that the frozen parameter settings have a ranking opportunity on controlled inputs. They are neither accuracy scores nor evidence that any particular setting improves EnterpriseRAG.

## Attribute the first BM25 change correctly

| Property | Empty-profile baseline | Nonempty Turso profile |
| --- | --- | --- |
| Authoritative storage | Actual local Turso database | Same actual local Turso database |
| Ranking execution | Parameterized SQL for each query | Canonical rows loaded once; in-memory BM25 for each query |
| Match semantics | Presence of each query-token substring in title and body | Exact normalized token matches |
| Scoring | One point per present query token | IDF, term saturation, length normalization and title weighting |
| Tie order | Ascending record ID | Ascending record ID |
| Registered route ID | `lexical-sql` | `lexical-sql` |

For example, the fixture document containing `quasarism` but no exact `quasar` token is returned by the SQL query for `quasar` and excluded by all eleven BM25 configurations. The first nonempty-profile comparison therefore changes the ranking algorithm and match semantics as well as introducing BM25 parameters. Subsequent BM25 parameter comparisons must be attributed against their actual retained parent.

The route name does not establish that BM25 runs inside SQL, that a database index has been added, or that SQL joins, typed filters and semantic traversal have been optimized. The Turso schema is unchanged. Loading all records also has an initialization and memory cost; this small audit does not measure campaign performance or establish a memory bound.

## Scope of the pending native opportunity

The builder, validators, read-side verifier and ranking functions ran locally. The complete Harbor bridge dispatch was not run here, and this audit does not attest the container environment or end-to-end native Enterprise behavior. The frozen bridge source was digest-verified for treatment attribution. No benchmark query content or relevance label was used; the study guard performed mechanical digest checks.

Turso still needs its own original native baseline and development search. Its shared BM25 implementation with Legacy does not prove equivalent corpus records or eliminate that requirement. No new study or campaign candidate was created, no miss consumed, no private gate opened and no skill promoted. The eleven declared parameter variants remain unchanged.

[Synthetic observations, validation receipts and source hashes](aggregate.json) · [All-family opportunity inventory](../strategy-coverage.md) · [Campaign](../README.md)
