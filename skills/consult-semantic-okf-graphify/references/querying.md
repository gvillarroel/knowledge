# Querying the Graphify Projection

Validate once per snapshot revision. Use `records` for exact source/record
identity and `aggregate` for authoritative counts. Use `search` only for
Graphify lexical scoring and bounded BFS discovery, then rely on each result's
hydrated `concept_path`, record digest, and concept digest as evidence.
Search output is deterministic structured JSON: ranked records, seeds, scores,
bounded context nodes, and traversal counts. Each record includes an exact
`concept-file` evidence locator and ledger-derived paper identity; native
Graphify display text is intentionally omitted because its ordering is not a
stable API contract.

Graphify headings and relationships are not factual authority. A search with no
candidate returns zero records and `fallback: null`; disclose that result instead
of silently substituting external knowledge.
