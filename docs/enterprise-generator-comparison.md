# EnterpriseRAG comparison of generator versions

[Documentation index](README.md) · [Generator construction acceptance](knowledge-generator-evolution.md)
· [Full-text comparison report](../evaluations/reports/enterprise-generator-g2/README.md)
· [Comparison decision](../.specs/adr/0127-compare-generator-versions-on-fulltext-enterprise.md)

Compare the incoming generator with the independently accepted G2 generator on
the same full-text Enterprise sources. This fixed replay isolates the generator
change. Freeze identical plans, source selection, guidance, knowledge layout,
cutoff, consultants and runtime between versions. Keep the earlier title-only
v1/e6 contracts and the S2 model-generated answer experiment separate.

The corpus contains 985 documents and 40 previously exposed questions. It is a
reference-enriched retrieval diagnostic, not the official full-corpus benchmark
or an independent promotion gate. Do not select another mutation from these
results or feed a consumed private construction gate back into evolution.

## Inputs and execution

The ignored replay lives under `tmp/enterprise-g2-replay/`. Its `binding.json`
freezes both complete generator inventories, evaluator code, inputs, questions,
local embedding model, runtime image, budgets and comparison policy before
retrieval. The preceding `tmp/enterprise-g2-comparison/` attempt retains a shared
guidance-format rejection: zero completed builds and zero retrieval scores.

The original Turso comparator attempted to open the mounted release directly,
and the engine rejected sidecar creation before the first query. Its corrected
adapter follows [ADR 0031](../.specs/adr/0031-turso-backed-semantic-okf-skills.md):
validate a quiescent release, copy it into an isolated temporary directory, open
the copy in query-only mode, and preserve the original bytes. Both versions use
the same fix, bound before scoring by `turso-amendment.json`. Their completed
scores live in `evaluation-v2/`; the failed original attempt remains in place.
No skills, SQL, relevance metrics, data or plans changed, and no semantic outcome
was rerun. The other seventeen routes retain the original frozen evaluator.

Prepare a separate projection with the retained
[full-text ingestion commands](enterprise-source-skills.md#retained-ingestion-commands).
Use application guidance with the four required generator headings. Supply the
same exact family plan to both versions; retain the plans and hashes locally.
Never mount evaluator questions, answers or prior results into construction.

The reusable adapter is
[`compare_generator_versions.py`](../evaluations/enterprise-rag-bench/compare_generator_versions.py).
It runs one explicit build or one family's retrieval measurements. Example
container paths are shown below; mount source, generator, evaluator, experts
and pinned model read-only, with a fresh writable output directory. Use the
same pinned dependency image for both versions and disable network access.

```bash
python -B /opt/enterprise/tool/compare_generator_versions.py build \
  --family embeddings --generator /generator --input /input \
  --plan /input/plans/embeddings.json --expert /out/enterprise-expert \
  --output /out/build.json

python -B /opt/enterprise/tool/compare_generator_versions.py score \
  --family embeddings --expert /expert --questions /questions.json \
  --helpers /opt/enterprise/tool --output /out/score.json
```

The tool directory contains this adapter, `fulltext_projection.py`, the exact
existing `evaluate_all_routes.py`, and its legacy comparator
`compare_retrieval.py`. Builds use the complete standalone generator and its
matched native validator. Check source-body fidelity, deterministic reconstruction,
generated verification, native-to-façade parity, physical citations, and exact
lookup separately from retrieval scores.

The eight-family replay retains 18 comparator routes, Top-10, and one pass per
query in each version. Legacy lexical and Turso token-overlap SQL are historical
comparator routes, not claims about their generated default search modes.
Embeddings uses the previously pinned MiniLM revision. The Ensemble plan retains
its declared hashing component. These backends do not change between versions.

## Reading and publishing results

Compare pair coverage, ordered document identities, relevance metrics, content
fidelity, generated knowledge and consultation files before interpreting a
delta. A normalized coverage receipt improves auditability but is not a retrieval
score. Single-pass timings do not support speed or query-stability claims.
Missing model-generated answer quality remains unavailable.

Keep raw questions, qrels, outputs, generators and expert bundles ignored. Publish
reviewed English aggregates with source hashes, family/route comparisons,
category diagnostics, CTA measurements, limitations and the conditional push
decision. Link them from the dataset, skill and CTA catalog without replacing
historical evidence.
