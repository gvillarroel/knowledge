# ADR 0129: Stratified Enterprise family evolution and one joint acceptance gate

## Status

Accepted for the E7 study design on 2026-09-08. Retrieval promotion requires the
terminal evidence described here; preparing the study does not establish gains.

## Context

The user requested evolution of every strategy on an economical stratified
subset, repeated attempts until improvements stop, and a final EnterpriseRAG
comparison. Earlier Enterprise experiments mixed different corpus sizes and,
before the documented ingestion correction, title-only inputs. The existing
full-corpus Classical/Luna measurement is a separate fixed contract.

## Decision

Use 120 public development questions sampled without replacement within the ten
question categories. Freeze the random seed before scoring. Balance categories
over four 30-question measurement blocks and weight each eligible question by
its category population divided by its category sample size. The 112 eligible
questions have weights summing to the 470 eligible questions in the original
workload. Application and reference-count coverage are audits, not extra quotas
or independent validation groups. Every public question has prior exposure.

Use one fixed 6,000-document corpus for every arm. Retain complete document text,
all 722 reference identities, and the previously frozen full-corpus BM25 contexts;
add deterministic distractors with a source-coverage floor. This is explicitly
reference-enriched and retrospective. Resolve the one needed public-ID alias by
the pinned upstream UUID index, preserving the original archive and path binding.
Render only U+0085, U+2028 and U+2029 as LF at the source-adapter boundary because
the native serializers use physical line records. Two characters in two bodies
require this rendering; all other characters remain unchanged. Bind original
and rendered text separately.

Freeze the current generator and its eight matched native builder/consultant
pairs. Use source-packed concepts, exact record identities and evidence hashes,
two independent native builds and validation, and every family's declared query
routes. Embeddings starts with pinned offline MiniLM; Ensemble starts with its
native hashing configuration and includes a learned-embedding mutation. This is
deterministic native skill execution, with no model choosing a skill or generating
answers. The E7 model-call budget is zero.

Use one primary evolution controller, `harbor-reflective-pareto-search`, and the
official candidate realizer for exact profile-only mutations. Construction
treatments cover Embeddings, Classical, Adaptive, Entity Graph and Ensemble;
consultation treatments cover Legacy, Graphify and Turso. A family never combines
the two treatment types. Candidate instructions remain source-generic and carry
no benchmark questions or answers.

The closed inventory has 117 variants per catalog round across all families.
Change mechanisms after three consecutive unique evaluable misses; a strict
weighted nDCG@10 gain above 1e-12 resets the streak. Skip duplicate complete
profiles without another trial. Repeat the catalog after an improving complete
round because later settings may make earlier mechanisms useful. Stop at the
first complete round without improvement. The maximum of five rounds is a
declared resource limit: reaching it with gains must be reported as budget
exhaustion, never proof that no further strategy exists. External failures stop
the affected execution with unavailable fitness and zero automatic retries.

Combine all eight development incumbents into one exact profile asset. Replay
the complete merged package against the unchanged baseline on all eight
development tasks and require per-family score reproduction before freezing.
Then recalculate both frozen arms on all 500 public questions using the same
6,000-document corpus. The 30 questions without reference documents stay in
execution and latency counts but have no retrieval score. This retrospective
comparison cannot change selection.

Only after that comparison, release the previously unconsumed reserved transfer
portfolio once: two source groups with 12 queries and 985 documents each, all
eight families, baseline and merged candidate, 32 native trials. An independent
curator must verify reservation, replay, leakage, native fixtures, access probes
and the complete frozen controls before study sealing. The entire bundle passes
only if native qualification and provenance pass and each family's mean paired
gain across both source groups is nonnegative. A larger aggregate gain cannot
compensate for a regressing family. Reject or accept the joint bundle without
per-family replacement or feedback-driven mutation after release. An unchanged
joint selection preserves the unopened portfolio.

Register all 32 task roots and the ordered `evolve`, `recalculate`, `validate`,
and `publish` stages at study initialization. The all-500 tasks are registered
as previously exposed development material but excluded from evolution jobs.
The final comparison precedes release so no optimizer-visible execution follows
the private gate. Two validation source groups support a descriptive transfer
pilot, not broad independent generalization.

## Supporting implementation changes

Native RDF provenance validation previously materialized the complete graph as
a Python set for every record. Use indexed triple membership instead, preserving
every required provenance check. Apply identical bytes to the eight canonical
builders and their eight vendored copies. Tests forbid repeated graph scans and
still reject a missing required provenance edge.

During generated-expert validation, cache each physical packed text file only
for that validation call. Retain all body, anchor and range checks, then rebind
the complete tree and reject any change. Tests check one read per file, fresh
reads on the next call, and rejection of a mid-validation mutation. These are
ordinary semantics-preserving performance fixes; their usefulness does not imply
a retrieval-quality improvement or authorize profile promotion.

## Publication

Keep datasets, seeds, task contracts, native jobs, traces, candidates and private
gate artifacts under ignored `tmp/e7/`. Publish reviewed aggregates by family,
route, question category, application, dataset contract and cost/time/quality.
Preserve previous reports and identify the existing full-corpus Classical/Luna
result separately. E7 has no official answer Overall, public rank, or full-corpus
claim. See the [operating guide](../../docs/enterprise-stratified-evolution.md).
