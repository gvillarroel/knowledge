# Manual CLI query verification

This is a real read-only smoke query for hard question `q030-causal-evidence-map`. It is separate from the 30-question evaluator and does not use MCP. The legacy CLI supports deterministic ledger filtering rather than ranked free-text retrieval, so its `phthalate` check is a functionality and integrity verification, not the evaluator-side TF-IDF baseline.

| Family | CLI mode | Returned | First record | First paper | Evidence valid | Bundle unchanged |
| --- | --- | ---: | --- | --- | --- | --- |
| legacy | ledger | 10 | `method-pmc4016195` | N/A | yes | yes |
| embeddings | lexical | 10 | `sources/markdown/PMC9764248` | PMC9764248 | yes | yes |
| classical | bm25 | 10 | `sources/markdown/PMC5783668` | PMC5783668 | yes | yes |
| adaptive | bm25 | 10 | `sources/markdown/PMC5783668` | PMC5783668 | yes | yes |
| entity-graph | N/A | N/A | N/A | N/A | N/A | N/A |
| ensemble | N/A | N/A | N/A | N/A | N/A | N/A |

Entity-graph and ensemble have no query output because their builders fail closed on the honest PMCID/BioC corpus. Their exact diagnostics are retained in the machine-readable report and the build comparison.

Every returned hit—not only the displayed top five—was independently rebound to `semantic/records.jsonl`. The check covers the record identity, canonical record digest, retained body slice and digest, locator, concept path, and source path. The embeddings CLI does not currently project `record_sha256`, so the verifier transparently reconstructs that digest only after binding the returned source/record identity; the JSON records the rebound count and per-hit digest origin. The compact JSON report records the exact command arguments, validation counts, first five results, and before/after bundle tree hashes.
