# Astro Retrieval Plans

Every plan selects the same sorted set of 416 opaque source IDs from the frozen corpus. `plan-manifest.json` binds each generated file and the complete selection digest.

| Plan | Schema | Retrieval role |
| --- | --- | --- |
| `classical-plan.json` | 1.0 | BM25, lexical association, topic expansion, and diversified reranking |
| `adaptive-plan.json` | 1.1 | Classical signals plus deterministic query-aspect decomposition and protected full-query results |
| `embedding-plan.json` | 1.0 | Pinned MiniLM semantic chunk embeddings; the model ID and revision are fixed |
| `entity-graph-plan.json` | 2.0 | Generic Markdown heading sections, lexical entity extraction, co-mention graph traversal, and rank fusion |
| `ensemble-plan.json` | 2.0 | Adaptive, graph, BM25, and embedding routes under protected-candidate and exact-evidence quality gates |

The legacy builder consumes `../corpus/manifest.json` directly and therefore has no separate plan. The ensemble identity policy is `source-record-v1` with no overrides: it uses exact `(source_id, record_id, record_sha256)` identity and does not infer joins from titles or paths.

These files are derived configuration, not authoritative knowledge. They contain no benchmark question IDs, qrels, labels, answer claims, or evidence locators. Package plan loaders validate all five plan-driven alternatives in `tests/test_semantic_okf_astro_evaluation.py`.
