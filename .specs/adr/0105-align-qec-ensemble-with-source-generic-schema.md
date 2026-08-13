---
adr: "0105"
title: "ADR 0105: Align the QEC Ensemble Plan with the Source-Generic Schema"
summary: "Keep QEC ensemble schema 2.0 and use exact full-record adaptive passages while preserving PDF-page passages in the standalone adaptive plan."
status: "Accepted"
date: "2026-08-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Evaluation Datasets"
tags: [qec, ensemble, semantic-okf, datasets]
---

# ADR 0105: Align the QEC Ensemble Plan with the Source-Generic Schema

## Status

Accepted.

## Context

The registered QEC ensemble plan declares ensemble schema `2.0` and an
entity-graph schema `2.0` child, but its embedded adaptive child was copied
verbatim from the standalone adaptive plan and retained a nonempty
`markdown_pdf_page_source_ids` list. The accepted ensemble schema `2.0`
contract requires that list to be empty so all components share exact
full-record source identity. The canonical ensemble builder correctly rejected
the contradictory plan.

Changing the root to legacy paper/claim schema `1.0` would be incorrect because
QEC uses the source-generic entity graph and does not provide the legacy split
paper/claim vocabulary contract. Removing page segmentation from the
standalone adaptive plan would also unnecessarily reduce its exact PDF-page
retrieval behavior.

## Decision

- Keep the QEC ensemble root and entity-graph child at schema `2.0`.
- Deep-copy the standalone adaptive, embedding, and entity-graph plans when
  composing the ensemble plan so composition cannot mutate their accepted
  standalone artifacts.
- Set only the ensemble copy of
  `adaptive.passages.markdown_pdf_page_source_ids` to an empty array. Retain the
  complete page-source list in `plans/adaptive-plan.json`.
- Regenerate the deterministic QEC benchmark, update the registry's exact
  ensemble-plan digest, restage the evaluator-free family input, and require an
  immediate deterministic `--check`.
- Add a regression assertion that the standalone adaptive plan retains page
  segmentation while the schema `2.0` ensemble copy uses full records.

## Consequences

The registered QEC ensemble input now satisfies the same closed schema that
its builder and consultant enforce, while standalone adaptive evaluation keeps
its page-level evidence behavior. Dataset sources, questions, cohorts, and
evaluation boundaries are unchanged; only the invalid composed plan and its
derived digest change.
