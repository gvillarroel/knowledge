# EnterpriseRAG-Bench reduced evaluation

[Incoming versus G2 generator comparison](../../docs/enterprise-generator-comparison.md)
uses a separate full-text projection and preserves the historical v1 contract.

This directory owns the pinned Onyx acquisition descriptor, evaluator-free
dataset adapter, and direct comparison runner for `enterprise-rag-bench-40-v1`.

The local dataset has **40 questions and 985 documents**, including 85 reference
documents and 900 fixed distractors across nine enterprise source types.
It is a reproducible reduced retrieval diagnostic, not the official full
511,962-document benchmark or a generated-answer score.

**Ingestion scope correction:** v1 omitted the structured body-field mapping and
produced title-only knowledge. Preserve its historical scores with that scope;
use the separate full-text preparation for new answer evaluations. See the
[audit and affected reports](../reports/enterprise-source-skills/ingestion-scope-20260907.md).
The retained [full-text projection and fidelity checker](fulltext_projection.py)
prepares a fresh input without rewriting v1. Its
[commands and regression lessons](../../docs/enterprise-source-skills.md#retained-ingestion-commands)
remain useful after retiring the application-split experiment.

- [Acquisition and selection descriptor](descriptor.json)
- [Source-combination decision](source-combination.json)
- [Preparation, execution, and interpretation guide](../../docs/evaluation-datasets-and-reports.md)
- [Dataset comparison](../reports/datasets/enterprise-rag-bench-40-v1.md)
- [Public leaderboard and external strategy results, checked 2026-09-06](reports/public-results-20260906.md)
- [Cross-dataset report hub](../reports/README.md)

`raw/`, `processed/`, `generated/`, `results/`, and `.venv/` are local and
ignored. The reviewed aggregate publications under `reports/` remain in Git.
Questions and reference answers never enter the builder-visible input tree.

Upstream: [onyx-dot-app/EnterpriseRAG-Bench](https://github.com/onyx-dot-app/EnterpriseRAG-Bench),
MIT license, document release `v1.0.0`, question commit
`d36685e273713975ee20299bbf1ab64165575b3c`. The license is retained with acquired
and prepared local data.
