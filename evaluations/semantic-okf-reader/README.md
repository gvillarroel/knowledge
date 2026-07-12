# Semantic OKF Reader v2: 300-Question PI Comparison

The active v2 benchmark measures grounded consultation of an existing Semantic
OKF snapshot. It does not test source ingestion, manifest editing, bundle
construction, or refresh behavior.

## Active v2 contract

- `no-skill` receives `fixtures/workspaces/base-v2/`, with no snapshot and no
  Semantic OKF skill.
- `skill` receives `fixtures/workspaces/reader-v2-overlay/`, containing the
  pinned 60-record, 40-source snapshot and only the independently pinned
  `consult-semantic-okf` skill.
- Both profiles receive the same prompt, read-only sandbox, network policy,
  response contract, and deterministic assertions.
- Every active request uses PI with `openai-codex/gpt-5.6-luna`. The
  `bin/pi-luna.ps1` wrapper requires exactly one matching model argument and
  makes exactly one attempt. There is no active alternate model, fallback, or
  model-based judge.
- Each question is an independent model request. No row may depend on workspace
  mutations or state from another row.

The active generated manifests are `evaluation.yaml` and
`smoke-evaluation.yaml`. Their benchmark IDs include `v2`, and `coverage.json`
records `benchmark_generation: v2` plus the pinned consultation-skill tree
hash. The old `base/` and `skill-overlay/` directories are immutable v1
fixtures and are not referenced by either active manifest.

## Coverage and scoring

The battery contains exactly 300 semantically distinct questions covering
typed facts, bidirectional relations, multi-hop joins, typed filters,
aggregation, provenance, ontology and SHACL contracts, asserted negatives,
missingness, and bundle integrity. Hidden normalized answers, alternative
minimal evidence sets, query descriptors, and semantic signatures remain in
`questions.jsonl`, outside both materialized execution workspaces.

Named metrics remain separate:

- `semantic-accuracy` compares the normalized answer with the host-side oracle.
- `evidence-grounding` requires one reviewed sufficient evidence subset for a
  non-null answer.
- `evidence-path-validity` rejects paths absent from the pinned v2 snapshot.
- `response-format` and `response-contract` measure the JSON envelope without
  conflating transport completion with semantic correctness.

A compliant `no-skill` abstention passes the response and evidence discipline
checks but intentionally fails semantic accuracy. Query-layer metadata records
coverage; it does not claim to measure latency, tokens, or tool calls.

## Generate and validate active v2

Run from the repository root:

```powershell
python evaluations\semantic-okf-reader\scripts\generate_benchmark.py
python evaluations\semantic-okf-reader\scripts\generate_benchmark.py --check

skill-arena val-conf evaluations\semantic-okf-reader\evaluation.yaml
skill-arena val-conf evaluations\semantic-okf-reader\smoke-evaluation.yaml

skill-arena evaluate evaluations\semantic-okf-reader\evaluation.yaml --dry-run
skill-arena evaluate evaluations\semantic-okf-reader\smoke-evaluation.yaml --dry-run
```

The full active comparison expands to 600 cells: 300 prompts, two profiles, and
one Luna request per cell. The smoke manifest selects five questions and
expands to ten cells. Run the smoke comparison before spending quota on the
full evaluation.

## Historical v1 artifacts

The completed v1 experiment used the combined `build-semantic-okf` snapshot and
a Spark-to-Luna runtime route. Its results, reports, selection manifests,
recovery manifests, merge scripts, and fixture trees remain unchanged for
auditability:

- `fixtures/workspaces/base/`
- `fixtures/workspaces/skill-overlay/`
- `final_report.md`, `last_report.md`, and the other checked-in v1 reports
- `technical-*-evaluation.yaml`, `luna-fallback-evaluation.yaml`, and their
  selection records
- the technical and semantic resume/merge utilities under `scripts/`

Those files describe or reproduce v1 only. They are not active model routes and
must not be interpreted as v2 results. A future v2 live run must write a new
report rather than overwrite a historical v1 report.
