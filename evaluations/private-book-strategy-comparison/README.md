# Private Book Retrieval Strategy Comparison

This workflow evaluates every compatible registered Semantic OKF retrieval
route against the same private-book record ledger. It builds source-generic,
question-independent projections and then executes 18 routes with an identical
Top-10 cutoff and three repetitions.

The route population is:

- legacy lexical;
- embeddings lexical, vector, and hybrid;
- classical BM25, topic, association, and fusion;
- adaptive fusion;
- entity-graph lexical, entity, traversal, and fusion;
- ensemble fast, quality, and robust;
- Graphify graph search; and
- a declared Turso SQL token-overlap comparator.

The Turso comparator is reported separately because the validated Turso store
does not define a canonical natural-language ranker. Corpus-specific GraphRAG
experts are excluded: their checked artifacts contain evidence learned from a
different corpus and cannot be transferred without contaminating this study.

## Reproduce

Create a new append-only generated root for each dataset:

```powershell
python evaluations/private-book-strategy-comparison/scripts/prepare_strategy_bundles.py `
  --manifest evaluations/<dataset>/manifest.json `
  --output-root evaluations/<dataset>/generated/<run-id>
```

The preparation command independently validates every derived family and
requires exact authoritative-ledger parity across all seven projections.

Then run the comparison:

```powershell
python evaluations/private-book-strategy-comparison/scripts/evaluate_all_routes.py `
  --dataset-id <dataset-id> `
  --title "<report title>" `
  --questions evaluations/<dataset>/benchmark/retrieval-questions.jsonl `
  --legacy-bundle evaluations/<dataset>/processed/<legacy-bundle> `
  --bundle-root evaluations/<dataset>/generated/<run-id> `
  --output-json evaluations/<dataset>/results/<result>.json `
  --output-markdown evaluations/<dataset>/reports/all-route-comparison.md
```

Full per-question rankings remain under ignored `results/` paths. The tracked
Markdown reports contain only aggregate metrics. The comparison measures
retrieval quality, identity validity, repeatability, and latency; it does not
measure generated-answer quality.

The consolidated metric table is
[`all-dataset-summary.md`](all-dataset-summary.md). Dataset-specific reports
retain the complete ranking and latency values.
