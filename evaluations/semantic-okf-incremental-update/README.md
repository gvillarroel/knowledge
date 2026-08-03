# Incremental Semantic OKF Paper Update

This evaluation exercises the incremental refresh boundary with real,
version-pinned arXiv PDFs.

The baseline contains:

- `arXiv:2005.11401v4`, *Retrieval-Augmented Generation for
  Knowledge-Intensive NLP Tasks*.

The delta adds:

- `arXiv:2603.18012v1`, *DynaRAG: Bridging Static and Dynamic Knowledge in
  Retrieval-Augmented Generation*.

The run downloads both PDFs, extracts deterministic page-delimited text,
creates a validated baseline snapshot with an external cache, confirms that a
ledger query for `DynaRAG` has no result, adds the second paper, refreshes the
complete snapshot, and confirms that:

- exactly one physical file was processed;
- the unchanged baseline paper was reused;
- the new paper is present with its exact concept path;
- its text supports the selective external-API behavior; and
- the original paper remains queryable.

Run from the repository root:

```bash
python evaluations/semantic-okf-incremental-update/run_incremental_paper_update.py
```

By default, every execution creates a new append-only directory under
`results/`. Pass `--run-dir` to select a new explicit destination. The run
fails rather than overwriting an existing path. PDFs, extracted text, caches,
snapshots, and receipts are generated evidence and remain ignored.

This is a deterministic artifact and retrieval acceptance run, not a semantic
answer-quality benchmark or a promotion study.
