# E7 mutation configuration audit

Observed at 2026-09-08T17:08:23.992269+00:00. This is a synthetic configuration audit, not an EnterpriseRAG trial.

**All 117 declared variants were checked at their configuration boundary.** The 82 construction variants reached their requested plan fields and were accepted by the exact frozen native builder plan parsers. The 35 consultation variants reached the expected hooks in the fixed runtime bridge, using fixture dependencies for graph and SQL storage.

| Family | Channel | Variants checked | Evidence scope |
| --- | --- | ---: | --- |
| adaptive | construction | 20 | native-builder-plan-parser |
| classical | construction | 17 | native-builder-plan-parser |
| embeddings | construction | 8 | native-builder-plan-parser |
| ensemble | construction | 21 | native-builder-plan-parser |
| entity-graph | construction | 16 | native-builder-plan-parser |
| graphify | consultation | 13 | fixed-bridge-with-fixture-dependencies |
| legacy | consultation | 11 | fixed-bridge-with-fixture-dependencies |
| turso | consultation | 11 | fixed-bridge-with-fixture-dependencies |

The construction checks use synthetic source selections, repeat the plan transformation and verify that other families and the opposite treatment channel are unchanged. Consultation checks run the frozen bridge and lexical/fusion functions, while graph traversal and database dependencies are fixtures. They do not prove native graph or SQL execution, dataset performance, successful builds within budget, or completed opportunities. Those require the original Harbor campaign.

## Adaptive constraint found

The frozen plan has `adaptive.protected_full_results=10`, and the primary cutoff is 10. When the full-query ranking contains at least ten distinct source-record identities, the adaptive runtime copies those ten identities first and truncates the result to ten. Changing only `aspect_weight` cannot then change the returned identity order, although it changes numeric fusion scores.

A synthetic probe called the exact frozen `_search_adaptive` function with twenty full-query identities and reversed aspect rankings. All three declared aspect weights (0, 0.5 and 1) preserved the protected top ten. A separate sensitivity control with protection set to zero changed the ranking, confirming that the component signals were not inert. That control exists only in memory for the fixture; it is outside the E7 catalog and was not made into a skill or benchmark candidate.

This does not establish how often the condition occurs in EnterpriseRAG. Shorter full-query rankings can still admit aspect results. Adaptive also retains its other construction mechanisms, which can change the protected full-query ranking. An unchanged aspect-weight result must therefore not be interpreted as evidence that query decomposition is globally exhausted.

The frozen campaign is unchanged. Any later study of the protection budget requires its own predeclared mutation contract and validation boundary. This report changes interpretation and preserves a useful limitation; it does not change selection or promote a profile.

[Aggregate checks and source hashes](aggregate.json) · [Strategy coverage](../strategy-coverage.md) · [Native campaign status](../README.md)
