# ADR 0090: Compare All Compatible Retrieval Routes on Private Book Corpora

- Status: Accepted
- Date: 2026-07-30

## Context

The software-architecture corpus had a reviewed 40-question benchmark but only
four classical routes. The data-science, AI, and machine-learning corpus had
38 validated records but no comparative benchmark. Comparing only one family
would not answer which registered retrieval strategy transfers best to these
corpora.

Both corpora contain private commercial books. A valid comparison must preserve
their local-only boundary, use identical authoritative identities across
projections, avoid tuning against qrels, and distinguish retrieval evaluation
from generated-answer evaluation.

Some checked GraphRAG experts contain indexes or profiles learned from a
different corpus. Reusing those corpus-specific artifacts would contaminate a
transfer comparison. The Turso family provides a validated store but no
canonical natural-language ranking route.

## Decision

Freeze and evaluate a fixed population of 18 compatible routes:

- legacy lexical;
- embeddings lexical, vector, and hybrid;
- classical BM25, topic, association, and fusion;
- adaptive fusion;
- entity-graph lexical, entity, traversal, and fusion;
- ensemble fast, quality, and robust;
- Graphify graph search; and
- a disclosed Turso SQL token-overlap comparator.

Use question-independent, source-generic plans for every derived projection.
Use 24 deterministic topic communities for both corpora, record-level hashing
embeddings, and the same Top-10 cutoff. Require exact authoritative record and
hash parity across all eight family bundles before querying.

Retain the existing 30-development/10-hard architecture questions. Freeze a
separate 30-development/10-hard data-science benchmark whose reviewed,
non-exhaustive focus sets collectively cover all 38 records. Run each route
three times and report Recall@10, MRR@10, nDCG@10, full-qrel coverage, exact
identity validity, ranking stability, and representative P95 latency. Rank by
nDCG, then MRR, Recall, and lower latency.

Do not transfer corpus-specific GraphRAG expert artifacts. Report the Turso
comparator as experimental rather than implying that it is an official Turso
ranker. Keep full rankings and generated bundles under ignored paths; track
only paraphrased questions, contracts, aggregate tables, scripts, tests, and
hash-only provenance.

## Consequences

Both private book corpora now have one reproducible, exhaustive route
comparison with explicit population completeness checks. Plans cannot inspect
questions or qrels, and any later mutation after observing results requires a
new evaluation-only cohort.

The tables support retrieval-route selection for these exact corpora. They do
not measure answer synthesis, establish unseen-corpus generalization, or
promote a skill. The architecture all-route comparison uses record-level book
identities and therefore remains distinct from its earlier page-level
four-route evaluation.

On the frozen comparisons, classical fusion ranks first for the architecture
corpus at 92.58% nDCG@10, while ensemble fast ranks first for the
data-science, AI, and machine-learning corpus at 94.44% nDCG@10. Every route
was stable across all three repetitions and every returned record passed exact
identity and hash validation.
