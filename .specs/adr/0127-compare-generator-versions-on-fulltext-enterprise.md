# ADR 0127: Compare generator versions on full-text Enterprise sources

## Status

Accepted for a fixed retrospective comparison on 2026-09-07.

## Context

The user requested EnterpriseRAG results for the new skill versions and authorized
pushing skill changes if the results improve. ADR 0126 accepted G2 on a separate
construction-contract validation gate. That result does not measure retrieval.
ADR 0125 also established that historical Enterprise v1/e6 records omitted the
document body, while the S2 experiment used complete bodies and a language-model
agent. These different treatments cannot serve as interchangeable baselines.

## Decision

Freeze the complete incoming generator and the accepted G2 generator before
scoring. Rebuild eight family experts from identical full-text source bytes,
explicit field maps, guidance, family plans and physical layout. Retain the
existing eighteen retrieval comparator routes, forty exposed questions, Top-10,
one pass per query and the existing metric functions. Preserve the learned
MiniLM plan for Embeddings and the hashing plan within Ensemble in both arms.

Use isolated offline containers with explicit read-only mounts. Construction
receives no evaluator questions or qrels. Compare generated knowledge and
consultation bytes, complete source-body fidelity, ordered returned documents,
paired relevance metrics and descriptive resource measurements. Verify G2
reconstruction and its native consultation façade separately.

For Turso, preserve ADR 0031's query-only working-copy boundary. The initial
comparison adapter bypassed that wrapper and failed on a read-only mount before
issuing any query. Bind its connection-lifecycle correction before scoring both
versions, preserve the unsuccessful connection evidence, and retain the exact
SQL and metric functions. This adapter repair changes no knowledge skill and
does not authorize rerunning semantic outcomes.

This is a fixed diagnostic, not an evolution stage. Do not mutate or select a
candidate from the exposed workload, consume another private gate, or reinterpret
the construction acceptance percentage as EnterpriseRAG performance. An equal
retrieval result does not satisfy the user's conditional push authorization.

Publish reviewed aggregates in a separate report directory and catalog entry.
Keep historical scores, sealed studies and local payload paths unchanged. Apply
the title-only warning to the two known historical report contracts rather than
to every future dataset identifier beginning with `enterprise-rag`.

## Consequences

The report can establish version equivalence for this exact workload and identify
its observed route scores. It cannot establish official full-corpus performance,
unseen-query generalization, new semantic answer quality or speed superiority.
Datasets, generated experts and raw results remain ignored. Meaningful comparator
tests, source and artifact integrity checks, resolved report links and the
repository application coverage gate remain required.

[Reproduction and reporting guide](../../docs/enterprise-generator-comparison.md)
