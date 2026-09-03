# ADR 0112: Use pinned tau3 banking as a retrospective knowledge-retrieval diagnostic

- Status: Accepted
- Date: 2026-08-23

## Context

The repository needs an external knowledge benchmark that combines a nontrivial document corpus with task-level relevance evidence. Harbor publishes `sierra-research/tau3-bench`, whose banking-knowledge domain contains 97 customer-service tasks, 698 Rho-Bank documents, and required-document annotations.

The public Harbor adapter embeds task configs but its Dockerfiles clone the latest `tau2-bench` revision. Current upstream task data can therefore drift from the published task payload. The task scenarios and qrels are also visible during adapter development, so this evidence cannot satisfy the sealed-validation boundary adopted by ADR 0111.

Classical fusion diversification treats `source_id` as its fallback evidence identity. Packing all 698 records into one JSONL source would consequently impose one shared evidence identity and invalidate diversified top-k comparisons.

## Decision

Use the tau3 banking-knowledge domain as a retrospective, non-promotional retrieval diagnostic with these controls:

1. Pin `tau2-bench` release `v1.0.0` at commit `17e07b1da2bbc0cadfddeea36412686e0604127b`.
2. Digest-lock the 698-document tree and the 97 downloaded Harbor task configs, and require exact Harbor/upstream task parity.
3. Preserve one Semantic OKF source identity per upstream document.
4. Keep builder-visible corpus input physically separate from task queries and qrels.
5. Use `task.user_scenario.instructions` as an explicitly labeled oracle-context query and `task.required_documents` as binary qrels.
6. Compare local retrieval with the exact upstream `rank_bm25.BM25Okapi` lowercase-whitespace baseline.
7. Report Harbor `install-only` runs solely as setup compatibility evidence. Do not assign a conversational reward when the user simulator and verifier did not run.
8. Do not use this inspected cohort for promotion, evolution, or sealed validation. A promotion study must begin with fresh organizer-owned development and validation data.

## Consequences

The diagnostic is reproducible, detects source-identity adapter errors, and provides broad retrieval coverage without model inference. It can support regression testing and inform future task construction.

The metric is an oracle-context ceiling rather than a live conversational result. It does not test fact elicitation, response quality, or action execution. Its qrels are no longer sealed, and the full tau3 end-to-end path remains unavailable without the benchmark's required model credentials.
