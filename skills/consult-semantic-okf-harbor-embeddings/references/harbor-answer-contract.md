# Closed Harbor Answer Contract

## Authority model

Chunk scores, vectors, facets, support IDs, ranks, and excerpts are derived discovery artifacts.
They are non-authoritative. Every selected chunk is resolved through the already validated retrieval
binding to its ledger parent. The finalizer copies public evidence metadata from that parent and
hashes the complete body selected by `{"kind":"record","target":"record.body"}`.

The snapshot and model cache remain read-only. The compiler writes only to standard output unless
the caller redirects output outside the bundle.

## Support pack

`prepare` binds these values into `support_pack_sha256`:

- schema version;
- exact question ID and SHA-256 of the exact normalized question input;
- all retrieval parameters, including mode;
- ordered facet text; and
- ordered parent supports, chunk provenance, exact body hashes, and bounded excerpts.

Copy the emitted `draft_template`. Do not synthesize its binding values or recreate an opaque
support ID.

## Draft schema

The draft has exactly `question_id`, `question_sha256`, `parameters`, `support_pack_sha256`, `answer`,
and `evidence`. `answer` has exactly `summary` and `claims`. Keep the summary within 450 words and
the claim array within 64 items. Each claim has exactly `statement` and
`evidence_indices`.

The draft `evidence` array contains support ID strings. List each support where a claim first needs
it. Every listed support must be used, every claim must cite at least one in-range index, and
duplicate indices or support IDs are forbidden.

## Parent-window behavior

The excerpt centers on the matching chunk's authoritative parent range when possible and remains a
bounded discovery aid. Public evidence deliberately selects the complete parent body so its locator
is source-generic, exactly reproducible from the ledger, and able to preserve qualifications outside
the chunk boundary. The response should still cite only parents that directly support its claims.

## Public result

`finalize` emits exactly `question_id`, `answer`, and `evidence`. Each evidence row contains exactly
`source_id`, `record_id`, `concept_path`, `source_path`, `record_sha256`, `locator`, and `text_sha256`
in that order. Do not edit the result.

## Failure handling

Treat a nonzero exit as a closed gate. Repair the draft or rerun `prepare`; never bypass validation
by assembling evidence manually. If the question, mode, model availability, retrieval snapshot, or
parameter set changes, discard the old pack and rerun preparation.
