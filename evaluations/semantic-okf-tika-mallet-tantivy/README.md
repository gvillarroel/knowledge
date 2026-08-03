# Tika/MALLET/Tantivy evaluation

This study evaluates the standalone
`consult-semantic-okf-tika-mallet-tantivy` skill against the frozen
`graphrag-papers-40` direct-retrieval contract. The builder remains
`build-semantic-okf-tika-mallet`; the consultant adds a pathless in-memory
Tantivy 0.26.0 index to the persisted Tika extraction, MALLET topics, and PPMI
associations.

ADR 0055 defined `fusion` before this evaluation as reciprocal-rank fusion of
the native Tantivy, MALLET topic, and PPMI association rankings. The evaluator
also records the three component routes as diagnostics.

## Canonical result

The checked
[canonical audit](reports/canonical-retrieval-20260727.md)
binds two independently reproduced Tika/MALLET bundles, two Top-10 runs, and
two pool-100 runs. It requires:

- all 40 frozen questions and reviewed binary qrels;
- exact Top-10 and pool-100 replay across the two bundles;
- an exact Top-10 prefix in each pool-100 run;
- identical evaluator inputs, bundle inventory, and record digest;
- independent fixed-seed MALLET rederivation and Tantivy 0.26.0 identity;
- 100% exact evidence validity; and
- an unchanged bundle before and after every run.

The prospectively defined fusion result is 73.50% Recall@10, 84.79% MRR@10,
71.75% nDCG@10, and 470.74 ms P95. Latency excludes the shared deep-validation
setup and remains an operational diagnostic.

## Reproduction

Use new output paths for every run; `generated/` is append-only and ignored.

```powershell
python -B scripts/evaluate_canonical_retrieval.py `
  --bundle BUNDLE `
  --consult-script ../../skills/consult-semantic-okf-tika-mallet-tantivy/scripts/query_semantic_okf_tika_mallet_tantivy.py `
  --java JAVA `
  --mallet-home MALLET_HOME `
  --top-k 10 `
  --output-json NEW_RUN/report.json `
  --output-markdown NEW_RUN/report.md
```

Repeat on both canonical bundles at Top 10 and pool 100, then close the
replicated audit:

```powershell
python -B scripts/audit_canonical_retrieval.py `
  --attempt-10-top10 ATTEMPT_10_TOP10 `
  --attempt-11-top10 ATTEMPT_11_TOP10 `
  --attempt-10-pool100 ATTEMPT_10_POOL100 `
  --attempt-11-pool100 ATTEMPT_11_POOL100 `
  --output-json NEW_AUDIT.json `
  --output-markdown NEW_AUDIT.md
```

This deterministic retrieval result does not replace the separate grounded
Harbor answer evaluation or admit the candidate to the eight-family registry.
