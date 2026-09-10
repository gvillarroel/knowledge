# Preserve pytest exit status in coverage checks

Status: Accepted. Date: 2026-09-10.

## Context

The application coverage command launched pytest through `python -m trace`.
The installed Python 3.14 trace CLI catches `SystemExit` and does not propagate
its code. Coverage run 024 therefore returned zero and reported 90.7% coverage
despite one test failing with a Windows file-access error. The separate log
inspection required by [ADR 0116](0116-local-enterprise-rag-dataset-and-aggregate-report-hub.md)
detected the failure before publication.

## Decision

Run pytest through the public `trace.Trace` API in a small dedicated subprocess
entry point. Return pytest's actual exit status and write trace artifacts in
`finally`, including on unsuccessful runs. Preserve the existing application
scope, coverage calculation and 80% default threshold. The parent coverage
command must stop on a nonzero test exit before reporting threshold success.

Exercise the real subprocess with passing tests, an assertion failure, a
collection error, invalid arguments and no collected tests. Retain coverage
artifacts for executed probes. Keep manual review of the test summary and
coverage total, particularly for historical reports from the former wrapper.

## Consequences

Coverage percentage alone cannot make a failed test suite successful. This
change affects repository verification only; it changes no skill candidate,
dataset, native evaluation, score, search budget or acceptance boundary.
The failed historical run remains preserved and requires a fresh verification
run after this correction. Its Windows file-access failure is not evidence of
a retrieval-quality loss.
