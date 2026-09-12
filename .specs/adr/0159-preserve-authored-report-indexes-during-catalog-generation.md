# Preserve authored report indexes during catalog generation

Status: Accepted

Date: 2026-09-12

## Context

The report catalog renders reviewed completed aggregates. Published indexes
also contain authored observations from an active EnterpriseRAG study, including
newer retained scores, catalog stops and historical measurement limitations.
Regenerating the completed-source catalog directly over those indexes could
erase the newer summaries and restore outdated comparisons.

The [repository guide](../../docs/repository-guide.md) requires build tools to
preserve authored documentation. [ADR 0158](0158-distinguish-catalog-stops-from-hypothesis-coverage.md)
also distinguishes current terminal evidence from earlier observation snapshots.

## Decision

1. Preflight every catalog destination before writing any new file. Reject
   escaping paths, aliases of the same output, non-file destinations and any
   existing file with different content.
2. Leave identical existing files untouched. Create missing files exclusively;
   never truncate a file that appeared after preflight. An I/O failure can leave
   newly created files, but does not authorize replacing an existing report.
3. Allow an explicit output directory for review. Generate a later revision in
   a fresh directory and compare it with the published hub before integrating
   changes. Do not add an overwrite switch for curated indexes.
4. Keep check mode read-only. A missing or differing file is reported as drift,
   not repaired automatically.

## Scope

This changes publication mechanics only. Aggregate selection, scoring, native
evaluation, study admission and candidate promotion remain unchanged. Reviewed
E14 observations and fixed historical report leaves retain their own evidence
and publication boundaries. The generator does not select a new current
EnterpriseRAG incumbent or replace the campaign's reporting pipeline.

The [report maintenance procedure](../../docs/evaluation-datasets-and-reports.md#maintain-the-report-hub)
documents generation and review of the candidate catalog.
