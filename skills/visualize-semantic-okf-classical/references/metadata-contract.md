# Classical Atlas Metadata Contract

## Required inputs

The knowledge root must contain the authoritative Semantic OKF core and exactly
these six files below `classical/`:

- `index.json`
- `documents.jsonl`
- `lexicon.json`
- `associations.jsonl`
- `topics.json`
- `build-report.json`

The atlas also reads `semantic/records.jsonl`, `semantic/semantic-plan.json`,
`semantic/source-manifest.json`, and `semantic/build-report.json`.

## Projection roles

| Input metadata | Atlas use | Authority |
| --- | --- | --- |
| Semantic records | Titles, types, attributes, identities, concept paths, source paths, years | Authoritative |
| Semantic plan | Bundle description, ontology classes and properties, rules, source declarations | Authoritative contract |
| Source manifest | Physical-source counts, hashes, artifact bindings, validation states | Provenance contract |
| Semantic build report | Record, source, concept, RDF, OWL, and SHACL summaries | Validation metadata |
| Classical documents | Exact passage locators, field lengths, term counts, topic weights, evidence identity | Derived discovery data |
| Lexicon | Vocabulary size, DF/CF/IDF distributions, BM25 parameters, tokenizer, average lengths | Derived discovery data |
| Associations | Persisted co-occurrence and PPMI edges | Derived discovery data |
| Topics | Seeds, weighted terms, community sizes, document-topic coverage | Derived discovery data |
| Contradiction relations and claim attributes | Source-declared rows when explicit `contradicts*` metadata exists; strict review candidates only when proposition identity, scope, and opposition gates pass | Explicit relations retain source authority; strict candidates are non-authoritative review prompts; loose matches are counts only |
| Classical index and report | Algorithms, closed plan, selection, artifact counts, hashes, integrity | Derived contract |

## Reduction rules

Read every row to compute inventories and distributions. Embed all compact
record identities, passage identities, topic weights, source metadata, plans,
reports, and contracts. Reduce large text and term payloads as follows:

- retain passage previews rather than complete passage text;
- retain full metadata for every topic and every topic's top terms;
- retain complete aggregate statistics over the full lexicon;
- retain topic-focused PPMI subgraphs plus aggregate statistics over every
  association row and edge; and
- evaluate every comparable reviewed-claim pair under the same structured
  subject, show at most 48 strict candidates, retain full evaluated, loose,
  rejected, and qualified counts, and never call a candidate confirmed; and
- never copy authoritative bodies into the atlas when a concept path and exact
  locator can identify them.

These reductions keep the external atlas responsive without changing or
reinterpreting the knowledge package.

## Precision-first contradiction contract

Apply this order and fail closed:

1. Treat `contradicts*` fields or a `contradicts` relationship as
   source-declared. Preserve the relation without claiming independent truth
   adjudication.
2. Prefer structured propositions. Accept the same `proposition_key` or the
   same canonical subject, predicate, object, and qualifier tuple only when its
   declared polarity is exactly opposite.
3. For lexical fallback, require the same `subject_term_iri` and
   `object_term_iri`, at least three shared terms with IDF of 1.5 or greater,
   and tightly aligned proposition wording after removing stopwords, polarity
   words, and numeric values.
4. Require one strict signal:
   - direct negation with proposition similarity of at least 0.82;
   - one unambiguous direction reversal with similarity of at least 0.72; or
   - one conflicting numeric value with similarity of at least 0.90.
5. Reject mixed polarity on either side, different dimensions, insufficient
   anchor overlap, insufficient context alignment, and ambiguous negation such
   as `not only`, `not always`, or `not necessarily`.
6. Keep broad strength-versus-limitation and polarity matches only in the
   quality-audit funnel. Never expose them as contradiction rows unless they
   independently pass the strict gate.

The lexical fallback cannot safely unify paper-local subjects across sources.
For reliable cross-source detection, builders should emit shared semantic
subject identifiers and normalized proposition keys, predicates, objects,
qualifiers, baselines, populations, and time scopes.
