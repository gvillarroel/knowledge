# Refresh bounded EnterpriseRAG current views from explicit aggregates

Status: Accepted

Date: 2026-09-12

## Context

The E14 observation publisher adds immutable gain reports and navigation links.
Current tables and status paragraphs previously required separate manual
updates. They have retained older scores after a newer gain was published, and
manual historical-link relabeling missed a relative link without a directory
prefix. The completed-source catalog cannot own these active-study summaries;
[ADR 0159](0159-preserve-authored-report-indexes-during-catalog-generation.md)
requires that it preserve authored indexes.

## Decision

Add a separate current-view helper after the existing native reporting and
observation publication steps. Its caller names the exact public comparison
and inventory leaves and supplies their SHA-256 digests. The helper never
discovers a winner, follows private provenance, runs a native job or replaces
the frozen reporting pipeline.

Update only the three explicit current-summary sections and obsolete latest
link labels in the established mutable indexes. Preserve each page's title,
publisher insertion anchors and historical bytes outside those regions.
Relabel a prior comparison only when its exact public aggregate appears in
the selected publication's verified public predecessor chain. Cover all eight
family pages, including those with older observations; follow only public E14
comparison aggregates, with a digest check on every visited source. Require the
selected gain's navigation entry in the main indexes and its own family page
before applying a refresh. Other family pages preserve their observation links
and numeric history while losing obsolete latest-comparison labels.

Derive displayed scores, paired counts and application leaders from validated
aggregate fields. Preserve all eight family slots, missing results and ties.
Keep catalog stops and unavailable historical hypotheses attached to the
inventory's own timestamp, following
[ADR 0158](0158-distinguish-catalog-stops-from-hypothesis-coverage.md). Never use
that inventory as the retained quality comparison or as a live reservation
counter. Retain the distinction between development retrieval, generated-answer
quality, all-500 measurement and promotion.

Preflight all planned inputs before any write. Check mode is read-only;
identical files are untouched. Replace each changed index atomically after
checking its original bytes again. A failure after an earlier replacement can
leave a partial multi-file update; no transaction or automatic retry is claimed.

## Scope

The helper supports existing public E14 gain and opportunity-inventory schemas.
It validates their presentation contract, not the original execution authority.
Native normalization, reconciliation, source audits, study boundaries and
publication review remain mandatory. Historical observation leaves, canonical
skills, dataset bytes and frozen runtime files are outside its write scope.

The [maintenance procedure](../../docs/evaluation-datasets-and-reports.md#refresh-current-enterpriserag-summaries)
describes explicit inputs, check/apply behavior and the final diff review.
