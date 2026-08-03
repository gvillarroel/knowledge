# ADR 0087: Evaluate cross-source contradiction retrieval separately

- Status: Accepted
- Date: 2026-07-30

## Context

The existing GraphRAG retrieval benchmarks reward finding relevant papers, but
they do not directly test whether a strategy can retrieve every source needed
to decide if two or more claims actually contradict one another. Reusing those
questions for evolution would also compromise their value as evidence of
generalization.

## Decision

Create `graphrag-papers-contradiction-eval-40-v1` as an evaluation-only
question extension over the existing fifteen-paper `graphrag-papers-40`
corpus. Do not add source papers. Freeze forty new questions with
source-derived adjudications and exact claim anchors:

- fifteen questions require two papers;
- twenty questions require three papers; and
- five questions require four papers.

Each question must allow the supported conclusion to be a direct
contradiction, a scope-conditioned tension, an evidence-incommensurable result,
or a compatible trade-off. The benchmark must not presuppose that an apparent
conflict is a true contradiction.

Rank the pre-existing compatible twenty-five-strategy population under a
shared Top-10 authoritative-paper identity contract. Use Full evidence@10 as
the primary metric: a query passes only when every required paper is present.
Report Recall@10, MRR@10, nDCG@10, cross-replicate Top-10 stability, and
representative P95 latency as secondary metrics. Recompute metrics from raw
hits and frozen qrels, and require exact evidence validity.

Register the question digest as evaluation-only. It is forbidden input to
knowledge construction, supervised profile forging, evolution, trace
distillation, candidate repair, candidate selection, and optimizer-visible
fitness.

## Consequences

The study measures source retrieval required for contradiction adjudication,
not generated-answer correctness. It supports scoped comparisons over the
existing corpus but does not establish unseen-corpus generalization.

Graphify and Turso remain outside this ranking because neither exposes the
same authoritative-paper Top-10 route. Raw questions, qrels, adjudications,
claim anchors, rankings, and diagnostics remain private; only reviewed
aggregate tables are publishable.

The first frozen result ranks the v45 early confidence-gated specialized
expert first at 92.50% Full evidence@10, followed by RustMallet association at
90.00% and classical association at 87.50%. The v51 supervised-profile expert
reaches 52.50% with 50.00% Top-10 stability, so its supervised profiles do not
generalize well to this contradiction-search scope.
