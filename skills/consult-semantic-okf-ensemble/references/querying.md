# Definitive Ensemble Query Contract

## Authority and integrity

The ensemble is one closed, derived projection over the unchanged Semantic OKF core.
Loading verifies the ensemble plan and report, the three component index hashes, equal
core trees, all component schemas, and exact parity between reviewed graph claim nodes
and adaptive answer bindings. Deep validation additionally rederives deterministic
adaptive and graph artifacts. Consultation performs no writes.

## Direct policies

All policies first obtain the adaptive top-k results and deduplicate them by paper.
That exact paper set is protected. Other routes may only reorder it, so irrelevant
semantic or graph candidates cannot reduce direct paper recall.

- `quality` uses persisted adaptive fusion, graph fusion, BM25, and pinned embedding
  hybrid ranks. It promotes the graph-lexical leader only when it is already protected
  and appears inside the configured depth on enough independent routes.
- `fast` uses adaptive and graph-lexical reciprocal ranks with the same protected-set
  and confirmation discipline.
- `robust` is an adaptive-only no-op ensemble used for diagnosis and reproducibility.

Concept filters disable graph contributions explicitly because the graph API cannot
apply those filters before scoring. The output names disabled routes. The quality
policy never silently converts an unavailable semantic route to lexical search.

Every direct result is the exact adaptive representative passage for that protected
paper. The ensemble changes rank metadata, not authoritative identity, text, locator,
or hash fields. `evidence_rows` remain the source for verification.

## Coverage policy

The adaptive coverage pack retains the full reviewed-record ranking and separate
punctuation/conjunction-derived facets. Two complementary extensions run on the full
question and each facet. The graph extension resolves corpus entities, traverses at
most two hops over reviewed edges, assigns candidate edges zero weight, and selects
only reviewed claim nodes with exact adaptive bindings. The pinned semantic extension
filters the hybrid index to declared claim sources, intersects every hit with a
reviewed exact answer binding, and contributes no factual authority. Both extensions
enforce separate per-facet and global budgets.

Within each semantic per-facet budget, the
`adaptive-paper-conditioned-claim-diversification-v1` reranker keeps a global prefix,
then retains up to six semantically ranked claims from each of the first three distinct
papers selected by adaptive retrieval before filling from the global rank. This
deterministic gate adds evidence depth only inside papers the independent adaptive
route already selected; it cannot introduce a paper or exceed the existing caps.

The compact brief preserves the complete deduplicated union but does not page it by
claim identifier. `persisted-idf-facet-consensus-priority-v1` orders claims by the
persisted adaptive IDF cosine against the full question and derived facets, then by
independent-route consensus, distinct facet coverage, full-query support, weighted
RRF, paper ID, and claim ID. Every page binds the same priority-order hash. This makes
the most directly relevant and independently corroborated evidence visible first
without filtering a candidate, consulting benchmark IDs, or changing authority.

`union_claim_ids` is an inspection budget, not evidence that every candidate entails
the question. Open exact paths and verify each candidate. Never copy a candidate entity
label, traversal score, embedding score, co-mention, or inferred relation into the
answer as a fact.

## Final-answer gate

The gated draft must account for every derived facet in order. Supported and partial
facets require a nonempty atomic statement and at least one claim from the current
coverage union. Unresolved facets require a nonempty limitation statement and no claim
IDs. At least one facet must be supported or partial.

The underlying deterministic finalizer accepts only reviewed claim bindings and emits
the established response contract:

- `question_id` is copied exactly;
- claim IDs are exact authoritative record IDs;
- evidence paths and locator strings are copied from bindings;
- citation pages are sorted integers grouped by paper;
- evidence is sorted and deduplicated deterministically.

Structural success does not prove the prose is entailed. Check every atomic statement,
requested condition, comparison baseline, exclusion, and important negative manually.
The packaged CLI is the only answer transport. Pipe an in-memory draft to
`finalize-answer --draft -`, keep stdout and stderr separate, require a zero exit, and
parse stdout before returning it verbatim. The finalizer recomputes the unpaged
coverage union, rejects unsupported claims, and constructs every contract-sensitive
identity from verified bindings. A caller must not hand-author or reserialize the
accepted response.

## Failure behavior

Stop rather than guessing when the bundle is mutable or stale, a component is absent,
core hashes differ, the exact embedding revision is unavailable for `quality` or
coverage, a
returned locator does not reconstruct authoritative text, a required facet lacks
support, or the response contract cannot be satisfied losslessly. Select `fast` or
`robust` explicitly when their documented tradeoff is acceptable.
