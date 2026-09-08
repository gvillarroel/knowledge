# ADR 0121: Preserve interrupted evolution without manufacturing completion

Date: 2026-09-07

Status: Accepted

## Context

Study e5 completed 160 native development trials and its generation-zero archive.
Its second generation produced 159 of 160 TrialResults before the local runtime
stopped. The last Data-science / Ensemble container exited; the root job retained
a null finish timestamp and a stale running count of one. There is no final
generation-one archive and no private validation release.

The owning Pareto analyzer requires complete native jobs. E5's frozen protocol
permits zero retries and selection only from the final generation's archive.
The installed recovery skill's sole incomplete-root exception requires a
different, exact one-trial pre-agent Pi SIGTERM envelope. Missing evidence or a
host interruption alone does not establish that exception.

## Decision

- Preserve all original native files, the incomplete root and stopped container.
  Do not synthesize a TrialResult, mark the job finished, replay the missing cell,
  borrow a result, or substitute the preceding generation's archive for selection.
- Normalize the four completed second-generation jobs through native Harbor
  reporting with their full comparison. Normalize the interrupted job separately
  with the native reporter's explicit `--allow-incomplete` option, without a
  comparison. Bind the unchanged source trees and both reports by digest.
- Publish an explicitly interrupted descriptive catalog across both generations.
  Preserve 320 expected trial slots, 319 observed results, nine complete run
  observations and one incomplete run. Those ten runs represent nine distinct
  profiles and include two baseline observations; neither their means nor query percentiles are
  pooled. The incomplete profile has no comparable mean, gain or dataset win.
- Register the observed sources, reviewed aggregates and interruption decision
  before stopping e5's evolution and unused planned validation/publication stages.
  Retain the canonical construction profile and leave validation sealed.
- A new retrospective analysis cannot be represented as recovered e5 or a
  prospective registration. Native analysis-only support does not waive the
  maintained organizer's requirement to declare a promotion-capable study before
  seeing its candidate results. A future study needs its own valid design,
  independently reviewed data boundaries and acceptance rule before execution.

The interruption is a missing measurement, not an observed semantic failure.
Zero recorded execution errors among completed trials is not a complete or
successful campaign. No private evaluation or promotion is claimed.

## Reporting and repository integrity

The [interruption reporter](../../evaluations/skill-evolution/aggregate_interruption.py)
uses native rewards and verifier aggregates without rescoring questions. It
retains all 717 observed route rows and 319 primary CTA rows, excludes unknown
payload fields and records the unavailable cell in every relevant view.
The complete-generation reporter remains strict and unchanged.

Raw report bytes are evidence: parent-level Git attributes disable line-ending
conversion for evolution reports. This preserves existing CRLF and LF sources
and their SHA-256 commitments without editing registered report directories.
The archived helper sources retain their separately declared LF policy.

## Validation

Twelve interruption reporting tests cover missing and duplicated results,
misleading completion, unsafe labels, native reward disagreement, unknown routes,
invalid quality/timing values, integrity failure, payload omission and immutable
publication. Together with the existing two reporting suites, all 35 checks pass.
The actual four-panel graphic, missing cell, profile means and navigation were
reviewed. The independent workflow review confirms that no implemented recovery
contract applies and that e5 cannot establish a finalist from its incomplete
generation. Full application coverage remains a separate final repository gate.

See the [observed comparison](../../evaluations/reports/evolution/e5/interrupted-development-001/README.md),
[study overview](../../evaluations/reports/evolution/e5/README.md),
[operating guide](../../docs/retrieval-profile-evolution.md), and
[previous lineage decision](0120-preflight-native-profile-and-complete-merge-lineage.md).
