# ADR 0124: Report unavailable semantic review pairs without selective retries

## Status

Accepted for transparent reporting on 2026-09-07.

## Context

The fixed Enterprise source-skill comparison completed all eighty native trials.
The separately frozen ADR 0109 reviewer then emitted some invalid status arrays:
for example, eleven required-point statuses for a twelve-point contract. This is
an unavailable reviewer output, not an infrastructure failure or a negative
judgment of an answer. The original review transport, strict validator, raw
responses, errors, and eighty-call limit remain unchanged.

## Decision

Let all eighty predeclared calls settle. Do not retry selected judgments, pad or
repair status arrays, regenerate agent answers, or relabel these failures as
external service failures. Preserve the original unsuccessful review run.

Publish a separate availability supplement using the existing shared validator
and conservative consensus without changes. Include a question only when both
orientations contain complete valid judgments for both answers. Exclude both
arms together when a review is unavailable. This selection uses output
availability, never answer quality. Retain the original case ordinals and bind
all source prompts, packets, answers, and results by their existing digests.

Report the observed semantic denominator explicitly at every aggregation level.
Provide worst/best arithmetic bounds for all forty questions by allowing each
unavailable question's coverage to range from zero to one, and its full-quality
status to range from failure to success. These are missing-data bounds, not
confidence intervals. Missing judgments are not observed zero scores. Application
cohorts overlap and may have different observed denominators.

Native retrieval, citation, usage, and latency metrics retain all forty trials
per arm. The incomplete semantic review does not invalidate completed native
execution, but conditional semantic means cannot establish a full-cohort winner
when their bounds overlap. Reviewer availability can correlate with rubric
complexity, so a complete-case mean is not assumed representative.

## Verification

Test paired exclusion, invalid status counts, and worst/best bounds. Keep the
supplement outside the frozen reviewer runtime. Document the limitation in the
aggregate publication and preserve all prior native and semantic artifacts.

[Original fixed comparison decision](0123-evaluate-agent-selected-enterprise-source-skills.md)
