# GraphRAG Cross-Paper Semantic Study Scope

## Objective

Measure how an isolated PI agent answers complex synthesis questions when fifteen independent GraphRAG papers describe related pipeline stages, methods, tasks, strengths, and limitations with different terminology.

## Source policy

The corpus contains fifteen version-pinned arXiv PDFs. Each paper remains a separate logical Semantic OKF source and scholarly authority. The PDF inventory records the accepted binary digest, page count, extracted-text digest, and extractor version. A source-specific reviewed claim layer makes common analysis dimensions queryable without merging papers, selecting a winner, or asserting equivalence between differently named methods.

## Processing policy

The preparation pipeline downloads only the pinned PDF versions, verifies SHA-256 digests, extracts page-addressable Markdown, and checks deterministic re-extraction. Strict Python adapters ingest every declared paper and claim source. The build produces distinct data, ontology, provenance, SHACL, validation, ledger, and concept layers.

## Evaluation policy

Thirty questions test cross-paper synthesis rather than isolated fact lookup. Questions cover graph construction, representations, retrieval units, traversal strategies, context organization, generation tasks, reasoning, verification, safety, cost, updates, and evaluation. The hidden host-side rubric requires multiple independent papers per answer and keeps gold criteria outside both isolated workspaces.

The comparison has two profiles:

1. `no-skill`: no snapshot and no Semantic OKF reader capability.
2. `consult-skill`: a pinned snapshot plus the pinned, read-only `consult-semantic-okf` skill.

Both profiles use PI with GPT-5.6 Luna for every answer request. There is no alternate model route or retry in a primary score. The benchmark scores deterministic response structure, controlled dimensions, page citations, and cross-paper evidence; qualitative trace review is performed after the fixed run so a second model call cannot turn an otherwise complete cell into a technical error. This two-arm design measures the augmented access path (reader procedure plus knowledge), not the causal contribution of the skill independently from corpus access.

The active generator emits the full comparison, five-question smoke comparison, six-question consultation holdout, and 30-question skill-only retest. It also emits a separately labeled two-question technical-recovery manifest whose results are forbidden from being merged into the primary score. All active manifests use only GPT-5.6 Luna and install only `consult-semantic-okf` in the treatment overlay.

## Historical evaluation artifacts

The 2026-07-12 baseline, skill-evolution, improved-holdout, and paired-holdout runs predate the lifecycle/consultation skill split. Their reports, result workspaces, frozen evolution inputs, and `paired-holdout-evaluation.yaml` retain the evaluated `build-semantic-okf` snapshot and are immutable historical evidence. The active generator intentionally does not rewrite that paired manifest or its recorded hashes. Future paired studies must create a new frozen `consult-semantic-okf` baseline instead of reusing the historical lifecycle-skill baseline.

## Exclusions

- The study does not treat a shared RDF graph as an access-control boundary.
- It does not claim that the selected papers exhaust GraphRAG research.
- It does not infer `owl:sameAs` relationships or silently canonicalize paper-specific method names.
- It does not use validation reports or SHACL shapes as domain evidence.
