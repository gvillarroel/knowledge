# Source and Release Boundaries

## Interpret sources correctly

Use `sources` and `records.source_id` to distinguish reviewed authorities inside one release.

- Separate declarations represent separate authorities and provenance scopes.
- A single declaration may represent a reviewed homogeneous partition union across several physical files.
- A canonical fused source represents upstream entity resolution; do not reinterpret it as its original authorities unless its stored provenance explicitly preserves them.

Repeated `record_id` values can be valid across different `source_id` values. Use `concept_id` or `(source_id, record_id)` for non-RDF identity. Use the complete `subject_iri` for RDF identity.

## Do not infer isolation

Source separation inside one database is not access control. All accepted domain rows and `data` statements in the same `knowledge.db` are visible to the reader. Use separate releases and databases for tenant, permission, license, retention, deletion, independent-version, or ontology-version boundaries.

Do not attach another database or query a remote database to answer a cross-release request. Require each authorized database as an explicit input and keep its revision digest attached to its evidence. The bundled helper intentionally rejects `ATTACH`.

## Verify revisions

Use `verify` and retain `logical_sha256` with the answer or evidence plan when revision identity matters. Do not combine results produced from changing database revisions as though they were one snapshot.
