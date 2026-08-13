# Ensemble Plan

The plan is closed and versioned. Schema `2.0` is the source-generic default. Schema
`1.0` remains accepted without output or ranking changes for frozen paper/claim
reproduction. Unknown or missing members fail; defaults and identity joins are never
inferred.

## Source-generic schema 2.0

The root contains exactly `schema_version`, `adaptive`, `entity_graph`, `embedding`,
`identity`, `policies`, and `quality_gates`.

The three child plans select the same sorted `source_ids`:

- `adaptive` uses its existing schema `1.1`, with
  `passages.markdown_pdf_page_source_ids: []`. Generic sources may use
  `evidence_identity.paper_ids_by_source: {}`; arXiv or paper identity is not required.
- `entity_graph` uses source-generic schema `2.0` and
  `selection.source_ids`.
- `embedding` uses schema `1.0` and the identical `selection.source_ids`.

`identity` contains exactly:

```json
{
  "default_grouping": "source-record-v1",
  "overrides": []
}
```

By default, every exact `(source_id, record_id, record_sha256)` belongs to a group
whose key is the canonical `(source_id, record_id)` value. The builder never joins by
path, prefix, title, URL, filename, paper-like token, or bare `record_id`.

An intentional cross-source equivalence must be declared as one sorted override per
record. Each override contains exactly `source_id`, `record_id`, `namespace`, and
`value`. Records with the same namespace and value receive the same deterministic
group ID. The namespace must be a lowercase stable identifier; the value is an opaque
governed key, not text-derived similarity. Overrides must be unique and ordered by
`(source_id, record_id)` and must name selected authoritative records.

## Legacy schema 1.0

The root contains exactly `schema_version`, `adaptive`, `entity_graph`, `embedding`,
`policies`, and `quality_gates`. Adaptive and embedding selections equal the sorted
union of graph paper and claim sources. The separately declared graph vocabulary is
excluded from those two retrieval selections. Every graph paper source is in the
adaptive PDF-page passage list, and paper identity mappings cover every selected
paper and claim source.

Use schema `1.0` only to reproduce the existing paper, reviewed-claim, and PDF-page
contract. Do not convert generic records into synthetic papers to satisfy it.

## Policies

`policies` contains exactly `default`, `quality`, `fast`, and `robust`. `default`
names one of the three policy objects. Each policy contains:

- `routes`: a unique non-empty array drawn from `adaptive`, `graph_lexical`,
  `graph_fusion`, `bm25`, `association`, and `embedding_hybrid`;
- `weights`: one finite positive weight per route;
- `rrf_k`: the bounded reciprocal-rank-fusion constant;
- `protected_route`: always `adaptive`; and
- `promotion`: `route`, active `confirmation_routes`, `confirmation_depth`,
  `minimum_confirmations`, and `maximum_protected_rank`.

Every policy includes `adaptive` among its weighted routes. In schema `1.0`, fusion
operates over protected paper identities. In schema `2.0`, it operates over protected
crosswalk group IDs. Other routes may reorder that exact protected set but may never
insert or remove a group.

## Quality gates

Both versions require exactly the legacy gates:

- `required_components`: `['adaptive', 'entity_graph', 'embedding']` in that order;
- `protect_candidate_set`, `require_core_parity`, `reviewed_graph_claims_only`,
  `reviewed_embedding_claims_only`, `require_facet_status`, and
  `require_exact_answer_bindings`: all `true`;
- `candidate_edge_weight`: exactly `0.0` for claim-answer expansion; and
- positive bounded graph and embedding claim budgets.

Schema `2.0` additionally requires these exact `true` gates:

- `require_child_plan_parity`;
- `require_total_identity_crosswalk`;
- `require_component_group_parity`;
- `require_exact_passage_evidence`; and
- `claim_only_coverage_requires_bindings`.

Generic search and evidence-pack remain available without reviewed answer bindings.
Coverage-pack, coverage-brief, and finalization are claim-only and fail with a clear
gate when those bindings are absent.

Plans must not contain evaluation question IDs. Keep benchmark cases, qrels, answer
keys, expected sources, and ground truth outside the skill and bundle.
