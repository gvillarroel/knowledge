# Cross-Source Synthesis

## Plan breadth before depth

Translate the request into explicit clauses and controlled comparison dimensions. Build a source-by-clause ledger with one batched query before reading long concept documents.

Count a source only when a selected record directly supports a requested clause. Topic-adjacent mentions do not satisfy a source minimum. A physical partition inside one declared `source_id` is not automatically an independent authority.

## Discovery query pattern

Start with a bounded candidate query that returns:

- `concept_id`;
- `source_id`;
- `record_id`;
- `title`;
- relevant attribute names and typed values;
- `concept_path`; and
- `source_path`.

Use `record_attributes` to match controlled dimensions. Group and count candidate sources in SQL. Reserve extra candidates before reading deeply so one irrelevant record does not collapse the evidence minimum.

Then fetch complete `concepts.content` for only the selected candidates. Keep the original row identity beside every extracted claim.

## Evidence matrix

Maintain one internal row per claim:

| Field | Meaning |
|---|---|
| clause | Exact requested clause supported |
| dimension | Controlled comparison dimension |
| source_id | Reviewed authority represented by the record |
| concept_id | Stable database record identity |
| concept_path | Exact stored evidence path |
| source_path | Original source locator |
| claim | Paraphrase supported by concept content |
| direct_support | Why the cited content supports the clause |

Reject a candidate when `direct_support` cannot be written without inference beyond the stored content.

## Semantic and provenance joins

Use `rdf_statements` with `graph_name='data'` for domain relationships. Query `graph_name='provenance'` separately to establish origins or locators. Do not let ontology labels, validation messages, or shape constraints stand in for domain evidence.

## Final verification

Before answering:

1. confirm every requested clause has evidence;
2. confirm the independent-source minimum after removing duplicates and weak candidates;
3. confirm all comparison dimensions use the requested controlled names;
4. confirm every path and source was copied from query results;
5. confirm the database logical digest identifies one verified revision; and
6. confirm the database bytes were unchanged by consultation.
