# Long-Candidate Confirmation Diagnostic

## Rejected experiment

The frozen full-run attempt `2026-07-15T13-50-35-550Z-compare`
(`eval-d9Z-2026-07-15T13:50:43`) planned the complete 90-answer Cartesian product
for the three isolated Skill Arena profiles, ten hard questions, and three
repetitions. It exercised the historical MCP v1.3.1 publication protocol, in which
preparation produced the canonical answer but confirmation required the agent to copy
the complete `candidate_json` string into a second tool call.

The first ensemble-treatment execution prepared successfully, then failed the
long-candidate confirmation copy and did not recover with a fresh preparation. The
append-only runner stopped at that first treatment protocol failure. The run did not
complete the frozen product and is rejected in full. It contributes no benchmark row,
generated-answer score, treatment delta, or causal evidence.

## Interpretation

This is a protocol-reliability result, not an answer-quality result. The successful
prepare shows that the governed constructor reached a candidate; the failed confirm
shows that asking the model to reproduce that long canonical value remained a
transport risk even after host-side publication was gated. No inference about claim
correctness, completeness, grounding, evidence validity, or response-contract quality
can be made from the interrupted attempt.

The failure is consistent with the earlier rejected diagnostics:

- the [single-tool copy-integrity diagnostic](finalizer-copy-integrity-diagnostic-20260715.md)
  found only 5/15 exact visible treatment copies; and
- the [host-publication mutation diagnostic](host-publication-mutation-diagnostic-20260715.md)
  found 0/3 q031 host messages byte-identical to valid confirmed candidates when the
  host still accepted a free-form final response.

Those experiments isolate different boundaries. The first showed that free-form
copying is unsafe, the second showed that server confirmation alone does not constrain
host output, and `eval-d9Z` showed that copying the long candidate into confirmation
is itself an unnecessary failure point.

## Resulting protocol

MCP v1.4.0 replaces only that long-copy step. `semantic_okf_prepare_answer` returns the
closed canonical `semantic-okf-prepared-answer/1.0` envelope containing exactly
`schema`, `candidate_json`, `response_sha256`, and `byte_count`. The agent reviews the
exact candidate but calls `semantic_okf_confirm_answer` with only the envelope's
64-character lowercase hexadecimal `response_sha256`. The server verifies the
outstanding digest and returns a receipt binding the exact candidate hash and UTF-8
byte count.

The host independently validates the strict envelope, canonical candidate, digest,
length, final clean transaction, and receipt before atomically publishing the exact
`candidate_json` bytes. A failed prepare or confirm publishes nothing and requires a
fresh prepare and digest. Stale or mismatched digests, repeated confirmation,
confirmation without a fresh prepare after failure, non-canonical candidates, and
trailing calls fail closed.

This protocol is recorded in
[ADR 0025](../../.specs/adr/0025-digest-confirmed-semantic-okf-publication.md). Final
answer-output metrics remain pending a fresh, complete v1.4.0 90-answer run and
independent trace attestation. Raw execution artifacts remain append-only and ignored;
they must not be resumed, merged, or promoted into a checked benchmark report.
