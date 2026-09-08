# ADR 0117: Evolve retrieval construction profiles through native Harbor

Status: Accepted. Date: 2026-09-06.

## Context

The user authorized active skill evolution after the EnterpriseRAG diagnostic
and the evidence-driven roadmap. Historical internal retrieval workloads are
already exposed and cannot become independent validation by renaming them.

## Decision

Use the unchanged integrated knowledge-skill package as the baseline for a
bounded construction-profile experiment spanning eight vendored families and
18 existing retrieval routes. Only an explicit profile helper, its configuration,
its documentation, and the package entry instructions may change. Builder and
consultant implementations remain fixed during this treatment. The native
Harbor agent executes these deterministic components without an instruction
model. This is a retrieval-runtime experiment, separate from the Luna-only
agent/grounded-answer studies governed by ADR 0011.

The dataset authoring skill owns seeded nuisance variation and source grouping;
the organizer owns locks and one-way releases; the candidate realizer owns
isolated complete bundles; reflective Pareto search owns development comparison
and selection; the native reporter owns completed-job normalization. None of
those responsibilities is replaced with a new optimizer or job-result format.

Register all four historical corpora as development. Treat their annotation
lineage conservatively as one group. Reserve two newly selected, source-separated
BEIR-derived cohorts for one frozen finalist. A twelve-query, reference-enriched
slice supports a bounded transfer check, not an official BEIR/EnterpriseRAG rank
or a broad generalization claim. Public pretraining exposure is unresolved.

Run native Harbor with evaluator-free inputs, a staged package, offline model
weights, and networking disabled. Verifiers run in a separate container and
independently bind all five evidence identity fields. The trusted curator may
author and audit reference contracts before sealing; candidate generation must
never inspect private tasks or gate outcomes. The host filesystem is not an
adversarial security boundary. Its curator/controller access is explicitly
trusted; actual candidate execution receives only its current task inputs.

Legacy lexical ranking and Turso SQL ranking retain the existing diagnostic
comparators. Other routes import their staged consultants. The top-level expert
generator is checked separately on synthetic examples; retrieval experiments do
not demonstrate instruction following or generated answer quality. Turso reads
an exact scratch copy because its driver creates WAL sidecars; the authoritative
knowledge tree must remain unchanged.

## Consequences

ADR 0118 qualifies a separate Graphify correctness repair before a new frozen
baseline is used. Every profile and its control share that repaired code; the
construction-profile treatment and its mutable-path boundary remain unchanged.

Profiles may improve different corpora and can remain complementary options.
Keep failures, regressions, and non-evaluable runs. Freeze one development
finalist before the terminal validation gate; do not tune or reselect afterward.
Preserve canonical defaults unless a passing gate supports the stated scope.
Keep raw tasks, candidates, models, trajectories, and per-case feedback ignored;
publish reviewed aggregate comparisons and reproducible procedures in English.

See the [evolution playbook](../../docs/knowledge-skill-evolution-playbook.md),
[dataset authoring decision](0115-author-leakage-resistant-harbor-evaluation-datasets.md),
and [dataset/report boundary](0116-local-enterprise-rag-dataset-and-aggregate-report-hub.md).
