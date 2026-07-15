# Ensemble Plan

The plan is closed and versioned as `1.0`. Its root contains exactly `schema_version`, `adaptive`, `entity_graph`, `embedding`, `policies`, and `quality_gates`. Unknown or missing members fail; defaults are never inferred.

## Component plans

`adaptive`, `entity_graph`, and `embedding` contain complete child plans. Their schemas are documented in [adaptive-plan.md](adaptive-plan.md), [entity-graph-plan.md](entity-graph-plan.md), and [retrieval-plan.md](retrieval-plan.md).

The adaptive and embedding `selection.source_ids` arrays must be identical. They must also equal the sorted union of the graph `paper_source_ids` and `claim_source_ids`. The graph `vocabulary_source_id` is authoritative auxiliary input for graph derivation but is excluded from adaptive and embedding retrieval.

Every graph paper source must appear in `adaptive.passages.markdown_pdf_page_source_ids`. `adaptive.evidence_identity.paper_ids_by_source` must cover every selected paper and claim source so all routes share a stable paper identity.

## Policies

`policies` contains exactly `default`, `quality`, `fast`, and `robust`. `default` names one of the three policy objects. Each policy contains:

- `routes`: a unique non-empty array drawn from `adaptive`, `graph_lexical`, `graph_fusion`, `bm25`, `association`, and `embedding_hybrid`;
- `weights`: one finite positive weight per route;
- `rrf_k`: the bounded reciprocal-rank-fusion constant;
- `protected_route`: always `adaptive`; and
- `promotion`: `route`, active `confirmation_routes`, `confirmation_depth`, `minimum_confirmations`, and `maximum_protected_rank`.

Every policy includes `adaptive` among its weighted scoring routes. Promotion and confirmation routes are executed in addition to scoring routes, so they need not receive fusion weights. A route may confirm itself when the declared policy intentionally counts its own vote or implements a documented no-op promotion.

## Quality gates

`quality_gates` contains exactly:

- `required_components`: `['adaptive', 'entity_graph', 'embedding']` in that order;
- `protect_candidate_set`, `require_core_parity`, `reviewed_graph_claims_only`, `reviewed_embedding_claims_only`, `require_facet_status`, and `require_exact_answer_bindings`: all `true`;
- `candidate_edge_weight`: exactly `0.0` for answer-evidence expansion; and
- positive bounded `maximum_graph_claims_per_facet`, `maximum_graph_claims_total`,
  `maximum_embedding_claims_per_facet`, and `maximum_embedding_claims_total` values.

The embedding claim budget applies only after filtering the pinned hybrid index to
declared claim sources and intersecting hits with reviewed exact answer bindings. It
does not grant similarity scores factual authority.

Plans must not contain evaluation question IDs. Keep benchmark cases, qrels, answer keys, expected papers, and ground truth outside the skill and bundle.
