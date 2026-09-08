# Enterprise ingestion scope correction, 2026-09-07

The historical Enterprise v1 structured manifest omitted the mapping that carries
document bodies into normalized knowledge. It declared `body` in the JSON schema,
but supplied no `fields` mapping. The canonical structured adapter retains mapped
fields, so those records contained their titles and empty mapped attributes.

The reduced source corpus has 985 documents with **6,291,040 body characters**.
Its historical normalized bodies contain **59,742 characters**, derived from
titles. Record count and reproducibility checks alone did not detect this loss.

The [machine-readable audit](ingestion-scope-20260907.json) binds this finding to
**all 114 completed e6 native responses across eight families**. The audit rebases
only subject and ontology IRIs to e6's neutralized manifest; every resulting
normalized record digest matches the corresponding native evidence. Body content
and attributes are unchanged by that identity transformation. The original v1
Embeddings ledger also matches the title-only prototype exactly.

Existing scores, including **63.19 nDCG@10 for the e6 Embeddings control**, remain
measurements of retrieval over that title-based projection. They do not establish
retrieval over complete documents or generated-answer quality. The finding narrows
their interpretation; it does not recompute or replace any native score. Immutable
development, catalog, and terminal publications remain unchanged.

The new source-skill comparison creates a separate `s2` projection with
`fields: {body: documentText}` and the corresponding ontology property. It checks
every original body for exact equality in the authoritative ledger and complete
presence in rendered retrieval text. Both its unified control and nine source
experts use this corrected projection, so their paired comparison is meaningful.
Their scores must not be pooled with the historical title-only scores.

The first `s1` preparation and its two generic technical rehearsals are retained
locally. No forty-question comparison was sealed or executed under `s1`. A
separate Windows UTF-8 reference-decoding fault in those technical rehearsals was
diagnosed by replaying the same response bytes, without generating new answers.
Both faults were resolved before `s2` benchmark execution.

[Audit implementation](../../enterprise-rag-bench/audit_historical_scope.py)
· [Comparison decision](../../../.specs/adr/0123-evaluate-agent-selected-enterprise-source-skills.md)
· [Report hub](../README.md)
