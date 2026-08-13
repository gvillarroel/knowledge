# Querying the Turso Knowledge Database

## Choose the cheapest table

1. Use `records` for exact identity, source, type, title, provenance locator, normalized body, and canonical JSON.
2. Use `record_attributes` for exact typed attribute filters, controlled dimensions, and repeated values.
3. Use `concepts` for complete human-readable Markdown evidence.
4. Use `rdf_statements` for semantic traversal, joins, and graph-specific assertions.
5. Use `sources` for source inventories and declared record counts.
6. Use `artifacts` for the semantic plan, source manifest, ontology, shapes, and validation report.
7. Use `bundle_metadata` only for revision, engine, schema, and integrity context.

Run `verify` once per database revision before relying on query results. Use the high-level commands for common filters and raw SQL only when joins, grouping, or aggregation materially reduce work.

## Table relationships

```text
sources.source_id
  -> records.source_id
       -> concepts.concept_id
       -> record_attributes.concept_id

rdf_statements.subject/object
  <-> records.subject_iri when a normalized record owns that RDF subject
```

`rdf_statements.graph_name` is exactly `data`, `ontology`, or `provenance`. Select it explicitly.

## Parameterized SQL examples

Exact records from one source:

```sql
SELECT concept_id, record_id, title, concept_path
FROM records
WHERE source_id = :source
ORDER BY concept_id
```

Exact scalar attribute:

```sql
SELECT r.concept_id, r.title, a.value_text, r.concept_path
FROM records AS r
JOIN record_attributes AS a ON a.concept_id = r.concept_id
WHERE a.name = :attribute
  AND a.value_json = :canonical_json_value
ORDER BY r.concept_id, a.ordinal
```

Source and type counts:

```sql
SELECT source_id, concept_type, COUNT(*) AS records
FROM records
GROUP BY source_id, concept_type
ORDER BY source_id, concept_type
```

Domain relationship traversal:

```sql
SELECT s.title AS subject_title,
       t.predicate,
       o.title AS object_title,
       s.concept_path AS subject_evidence,
       o.concept_path AS object_evidence
FROM rdf_statements AS t
JOIN records AS s ON s.subject_iri = t.subject
LEFT JOIN records AS o ON o.subject_iri = t.object
WHERE t.graph_name = 'data'
  AND t.predicate = :predicate
ORDER BY s.concept_id, t.object
```

Lineage for selected records:

```sql
SELECT r.concept_id, r.source_id, r.source_path,
       t.predicate, t.object, t.datatype, t.language
FROM records AS r
JOIN rdf_statements AS t ON t.subject = r.origin_iri
WHERE t.graph_name = 'provenance'
  AND r.source_id = :source
ORDER BY r.concept_id, t.predicate, t.object
```

Bind every variable through repeated `--param NAME=JSON`. For a SQL comparison with `value_json`, pass the canonical JSON string as a JSON string. Prefer the `records --attribute NAME JSON_VALUE` command when possible because it canonicalizes the value automatically.

## Graph ownership

- `data`: accepted domain assertions generated from reviewed mappings.
- `ontology`: declared classes, properties, domains, ranges, and ontology metadata.
- `provenance`: sources, origins, locators, and derivation links.
- shapes and validation report: stored text artifacts, never domain assertions.

Do not combine graph names just because they share RDF terms. Add `ontology` only for schema questions and `provenance` only for lineage.

## SQL restrictions

The helper accepts one bounded `SELECT`, `WITH`, or `EXPLAIN` statement. It rejects mutation and administration tokens, transactions, database attachment, pragmas in user SQL, extensions, and file functions. Turso additionally enforces `query_only=1` on the connection.

Use unique output aliases. Use `--limit` during discovery and `--all` only after the result cardinality is understood. A truncated result is not evidence of the full population.

## Evidence discipline

Return exact `concept_id`, `concept_path`, `source_id`, and `source_path` values from rows. Never reconstruct generated paths. Read `concepts.content` before treating a discovered record as narrative evidence. Match typed values through `value_json`, `value_type`, datatype, and language rather than display strings when the distinction matters.
