# Querying the Entity-Section Graph

## Choose a route

- `lexical` is section BM25 and is best for rare names, formulas, and exact terms.
- `entity` resolves reviewed and candidate entities, then scores their exact mention and claim-evidence sections.
- `traversal` propagates through bounded reviewed claim and candidate association paths. Reviewed and candidate edge weights stay separate.
- `fusion` combines all three rankings by reciprocal rank and applies a per-paper cap.

Use broad fusion first for synthesis, then focused entity or traversal queries for missing mechanisms, exclusions, and failure conditions. Treat the returned section as a candidate until its authoritative concept and claim record have been opened.

## Reviewed claims

`resolved_entities` exposes exact metadata for reviewed claim nodes: `record_id`, `concept_path`, `record_source_path`, and `claim_evidence`. Each claim-evidence item identifies the paper, PDF-page locator, source path, section ID, and exact text hash. Use these fields instead of reconstructing paths or locators.

The response's `supporting_edge_ids` explains graph connectivity but is not an answer citation. Cite reviewed claim IDs and authoritative paths.

## Multi-paper synthesis

Decompose the question before retrieval. Search separately for each mechanism, condition, contrast, and negative. Build an evidence matrix with one row per atomic statement and columns for claim ID, paper, page, reviewed interpretation, and role in the derivation. Do not draft prose until the required rows are filled.

For comparisons, preserve what each paper actually evaluated, including baselines and conditions. For exclusions, find an explicit reviewed limitation or unsupported-scope claim; graph absence alone is insufficient. If the evidence matrix remains incomplete, abstain or narrow the conclusion.
