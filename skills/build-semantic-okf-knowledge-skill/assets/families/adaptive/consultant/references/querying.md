# Querying Adaptive Semantic OKF

## Integrity before ranking

Ordinary inspection verifies the closed file set, source selection, authoritative bindings, locators, token counts, structural statistics, artifact hashes, and build report. Run `inspect --deep-validation` once for a newly supplied, benchmark, or release-candidate snapshot. Deep validation independently reconstructs the selected passages, BM25 lexicon, windowed PPMI graph, deterministic topic communities, and document-topic weights; it performs no writes. Repeated searches may use ordinary validation after the same immutable snapshot hash has passed deep validation.

## Layer selection

Use `semantic/records.jsonl` for exact identifiers, types, attributes, counts, and paths. Use adaptive search for discovery. Open returned concept Markdown for readable evidence. Use `data.ttl` for accepted domain joins or aggregation, `ontology.ttl` only for schema, and `provenance.ttl` only for lineage. Shapes and validation reports describe contracts and conformance, not domain facts.

## Mode semantics

- `bm25` uses only persisted title/body Bag-of-Words, field lengths, IDF, and plan weights.
- `topic` adds topic-community terms, document-topic cosine similarity, and topic/source MMR.
- `association` propagates query mass twice over normalized PPMI edges, adds the strongest new terms, then applies topic/source MMR.
- `fusion` combines BM25, topic, and association rank positions with reciprocal-rank fusion before MMR. It never adds incomparable raw scores.
- `adaptive` protects the plan-pinned leading full-query identities, decomposes a synthesis query into bounded lexical aspects, ranks every aspect through `fusion`, and combines evidence identities with plan-pinned reciprocal-rank weights. This is the default for broad or conditional questions.

Review `expansion.association_terms`, `expansion.topic_terms`, and `expansion.query_topics`. Expansion is corpus-derived and can amplify ambiguity. A result remains usable only when its authoritative locator supports the intended claim.

For multi-source synthesis, use `adaptive`; inspect `adaptive.aspects` to ensure decomposition preserved the intended contrasts and conditions. A paper ID is the diversity identity when present; otherwise each authoritative record remains independently retrievable. For exact names, IDs, formulas, or rare phrases, prefer `bm25`. Use component modes to diagnose why a candidate entered the adaptive union.

Do not treat one top-10 response as automatic coverage of a synthesis question. Create a checklist of named subjects, requested comparison axes, conditions, exclusions, mechanisms, and important negatives. After the full adaptive query, issue a focused query for each checklist row that lacks authoritative support. Follow passage hits to exact reviewed claim records when claims are required. Draft only after every atomic statement maps to verified evidence and every checklist row is supported or explicitly unresolved; repeated evidence for one row cannot substitute for a missing row.

For a reviewed-claim synthesis contract, use `coverage-pack` before manual follow-up. Its primary result preserves the ordinary full-query evidence pack. Its `coverage_facets` are derived only from punctuation and conjunctions in the supplied query and keep bounded, paper-diversified claim candidates separate for each enumerated system, mechanism, condition, or failure mode. A facet ranking is not evidence that a claim is correct; open and verify the candidate text. If a facet has no suitable candidate, issue a focused query or mark that checklist row unresolved.

Use facet expansion to find candidates, not to enlarge the final evidence list. After coverage closure, minimize support: retain one directly entailing record per atomic statement when possible, use a second only for an explicit join or contrast, and split broader statements. Remove every retrieved record that is not cited by a final statement. Reject topical similarity when the reviewed interpretation does not state the system identity, condition, number, comparison baseline, mechanism, or negative used in the draft. If some facets remain unresolved but the corpus supports a substantive partial comparison, qualify those facets instead of replacing the whole answer with null.

## Contract-ready evidence

Every search response includes `evidence_rows`. Use these rows to locate and verify authoritative records. Locator coordinates address the matching authoritative `semantic/records.jsonl` `record.body`; `concept_path` is the readable Markdown mirror after parsing its YAML frontmatter, not the offset basis. Never derive a record ID from a concept filename or normalize punctuation inside an identity.

For a reviewed-claim answer contract, prefer `evidence-pack`. It applies the persisted lexical, association, and topic signals to verified claim bindings without collapsing multiple claims from the same paper. `ranked_bindings` is ordered evidence for verification. `claim_evidence` copies exact claim IDs, claim concept paths, claim-source paths, paper IDs, and canonical string locators such as `PDF-page-7`. `citations` separately groups sorted integer pages such as `7` by paper. The command does not generate the prose answer.

The user's final response schema can require a different lossless representation. Treat its field names, types, sorting, and cross-field rules as binding. Copy locator fields from `claim_evidence[].locators` as `PDF-page-N` strings and citation page fields from `citations[].pages` as integers. Require each locator's page number to occur in the matching paper citation. A retrieval character range, record locator, canonical locator token, full source fragment, or literal `sources/...#PDF-page-N` string is invalid in an integer array. Do not substitute a paper source path for a claim source path.

Before returning structured output, validate required keys and key order, types, length bounds, sorted uniqueness, exact claim-to-evidence grounding, evidence-to-citation page equality, and required paper/source coverage. If any conversion is ambiguous, abstain instead of guessing.

For the standard structured answer, create an external draft with this closed shape:

```json
{
  "summary": "A verified synthesis within the requested word bound.",
  "claims": [
    {
      "statement": "One atomic statement supported by the selected records.",
      "supporting_claim_ids": ["claim-example-001"]
    }
  ]
}
```

Pipe the draft to `finalize-answer --draft -` in a read-only sandbox, or provide an external draft path, together with the expected question ID and word bounds. The finalizer rejects an in-bundle draft, an unknown claim ID, an empty claim, or an out-of-range summary. It sorts and deduplicates claim IDs, derives sorted paper IDs and integer citation pages, renders locator strings in the final contract's lexical order, and copies exact concept and claim-source paths from verified bindings. Review claim fidelity before returning its output; the finalizer guarantees structural and identity integrity, not semantic entailment.
