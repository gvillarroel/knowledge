# Knowledge Methodology Papers

`knowledge-methodology-papers-47` is a reproducible, version-pinned research
corpus for reviewing how this repository acquires, represents, retrieves,
evaluates, evolves, and publishes knowledge.

It contains 47 full papers across eight coverage lanes. Thirty-two papers are
acquired directly from exact arXiv versions; fifteen page-grounded GraphRAG
papers are reused byte-for-byte from the existing canonical corpus. The
selection is intentionally broad but remains a curated engineering review, not
a claim of exhaustive systematic-review coverage.

## Contents

- `paper-selection.json`: inclusion policy, coverage lanes, exact paper
  versions, and skill relevance.
- `scope.md`: competency questions and authority limits.
- `source-combination.json`: separate-in-bundle decision and identity policy
  for 47 paper authorities stored in two physical partitions.
- `sources/inventory.json`: physical paper inventory and SHA-256 bindings.
- `manifest.json`: 47-source Semantic OKF build plan.
- `bundle/`: validated immutable Semantic OKF snapshot.
- `expert-guidance.md`: reviewed procedure used to build the standalone expert.
- `reports/`: paper-grounded repository methodology audit.

The generated expert is
[`skills/review-knowledge-methodology`](../../skills/review-knowledge-methodology).
The restricted read-only agent contract is
[`agents/knowledge-methodology-reviewer`](../../agents/knowledge-methodology-reviewer).

## Reproduce

```powershell
python evaluations/knowledge-methodology-papers/scripts/acquire_papers.py
python evaluations/knowledge-methodology-papers/scripts/acquire_papers.py --check
python evaluations/knowledge-methodology-papers/scripts/generate_manifest.py
python evaluations/knowledge-methodology-papers/scripts/generate_manifest.py --check
python evaluations/knowledge-methodology-papers/scripts/validate_dataset.py
python skills/build-semantic-okf/scripts/build_semantic_okf.py `
  evaluations/knowledge-methodology-papers/manifest.json `
  evaluations/knowledge-methodology-papers/bundle --output-format json
python skills/build-semantic-okf/scripts/validate_okf_bundle.py `
  evaluations/knowledge-methodology-papers/bundle
python skills/build-semantic-okf/scripts/validate_semantic_okf.py `
  evaluations/knowledge-methodology-papers/bundle --output-format json
python skills/review-knowledge-methodology/scripts/query_expert_knowledge.py verify
python evaluations/knowledge-methodology-papers/scripts/validate_agent.py
```

The acquisition check regenerates the complete source tree in a temporary
location from the pinned PDFs and official arXiv metadata, then compares every
regular file. The Semantic OKF snapshot and expert skill must also be rebuilt
independently when their inputs change.

## Update boundary

Additions require a new selection entry with a versioned arXiv ID, a stated
coverage lane and selection rationale, deterministic acquisition, inventory
regeneration, a new immutable ontology version, expert rebuild, and a
superseding audit. Never silently replace a pinned paper version or rewrite a
prior reviewed report.
