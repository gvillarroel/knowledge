---
adr: "0025"
title: "ADR 0025: Confirm Semantic OKF Answers by Prepared Digest"
summary: "Return a canonical prepared-answer envelope, confirm only its short digest, and let the host verify and atomically publish the bound candidate bytes."
status: "Accepted"
date: "2026-07-15"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - answer-publication
  - digest-confirmation
  - mcp
  - quality-gates
  - skill-arena
---

# ADR 0025: Confirm Semantic OKF Answers by Prepared Digest

## Status

Accepted.

This decision extends ADR 0023 and supersedes only the v1.3.1 long-candidate
confirmation handshake in ADR 0024. ADR 0024's reviewed benchmark,
paper-diversified coverage, host-publication boundary, and non-compensating quality
gates remain accepted.

## Context

The authoritative Semantic OKF answer is canonical JSON constructed from reviewed
claim bindings. The agent must inspect its meaning before publication, but publication
must not depend on the agent reproducing a long canonical string without changing one
byte.

Three rejected experiments isolated that boundary. A historical single-tool
constructor produced the intended candidate for 15 treatment rows, but only 5 visible
answers copied it exactly. A later two-mode prototype confirmed correct candidate
hashes, yet the ordinary host published a different free-form final message in all
three inspected q031 rows. MCP v1.3.1 added a host gate and split preparation from
confirmation, but still required the agent to copy the complete `candidate_json` into
the confirm call.

The frozen full-run attempt `2026-07-15T13-50-35-550Z-compare`
(`eval-d9Z-2026-07-15T13:50:43`) failed that remaining copy step. Its first treatment
prepared successfully, failed to copy the long candidate into confirmation, and did
not recover. The runner stopped at the first treatment protocol failure. The attempt
is rejected and supplies no benchmark row or answer-quality metric.

## Decision

Use MCP runtime v1.4.0 and keep evidence review separate from transport:

1. `semantic_okf_prepare_answer` independently validates coverage and constructs the
   canonical answer. It stores the exact UTF-8 candidate for the active transaction
   and returns a closed canonical envelope with schema
   `semantic-okf-prepared-answer/1.0`. The envelope contains exactly `schema`,
   `candidate_json`, `response_sha256`, and `byte_count`.
2. The agent semantically reviews the exact `candidate_json` string without editing,
   reformatting, reordering, or parsing and reserializing it. If the answer needs
   repair, the agent prepares a new envelope before confirmation.
3. `semantic_okf_confirm_answer` accepts only `response_sha256`, constrained to 64
   lowercase hexadecimal characters. The agent sends the final prepared envelope's
   digest and never copies `candidate_json`, the envelope, or other long candidate
   text into confirmation.
4. The server verifies that the digest matches the outstanding prepared candidate,
   consumes that candidate, and returns the closed
   `semantic-okf-answer-confirmation-receipt/1.0` receipt. The receipt binds status,
   `response_sha256`, and `byte_count` to the exact candidate. Confirmation is
   non-idempotent, succeeds once, and is the terminal tool call.
5. The host publication wrapper parses the prepare result as a strict envelope,
   rejects extra or missing keys, verifies that `candidate_json` is the exact
   canonical serialization of a JSON object, recomputes its UTF-8 SHA-256 and byte
   count, verifies the terminal digest-only confirmation and receipt, and atomically
   writes the exact `candidate_json` bytes to the single absolute
   output-last-message path.

Any failed prepare or confirm clears the transaction and publishes nothing. Recovery
requires a fresh successful prepare and its new digest. An earlier successful confirm,
confirmation without a fresh prepare after failure, a stale or mismatched digest,
repeated confirmation, a non-canonical candidate, any tool call after successful
confirmation, or any envelope, hash, length, receipt, or ordering inconsistency fails
closed. No candidate from an abandoned transaction remains eligible. Control profiles
continue to publish their ordinary final messages unchanged.

An independent trace attestor must enforce the same envelope, digest, receipt,
terminal-sequence, and published-byte invariants. The host wrapper and attestor are
separate enforcement layers; neither retrieval scores nor server success can
compensate for a publication failure.

## Alternatives rejected

- Keep v1.3.1 and retry copying the complete candidate into confirmation. The frozen
  full-run failure shows that this remains an avoidable model-mediated transport risk.
- Trust a free-form final agent message after preparation or confirmation. Earlier
  diagnostics changed authoritative IDs and paths at that boundary.
- Treat server confirmation alone as publication. A valid receipt does not constrain
  what an ordinary host writes afterward.
- Confirm a digest without independently parsing the prepared envelope and verifying
  canonicality, byte length, receipt binding, and exact host output. That would move
  the unchecked boundary rather than close it.

## Evidence and acceptance boundary

The historical diagnostics justify this protocol but contribute no answer-quality
row. The accepted retrieval metrics and reviewed coverage results remain unchanged:
the diversified hard-10 union covers 44/44 atomic groups, 13/13 important-negative
groups, all required papers, and 713/713 exact bindings. Those measurements establish
candidate availability and evidence identity, not generated-answer correctness.

Final answer-output metrics remain pending until a fresh, complete v1.4.0 90-answer
Skill Arena run passes runtime attestation, host publication, independent preparation,
blinded semantic review, aggregation, and repository validation. Results from
`eval-d9Z` must not be resumed, merged, or reported as accepted metrics.

## Consequences

Positive:

- the model reviews the complete answer but confirms only a short fixed-shape value;
- the server receipt and host output remain bound to the same canonical candidate;
- stale, mismatched, repeated, trailing, and post-failure confirmations fail closed;
- the authoritative core and all retrieval artifacts remain read-only; and
- controls remain transparent, preserving the isolated Skill Arena estimand.

Negative:

- preparation now has a versioned response envelope that the server, skill, wrapper,
  attestor, tests, and evaluation contract must evolve together;
- the host must retain and validate structured tool events rather than treating the
  final model message as sufficient; and
- a failed transaction deliberately requires a new preparation even when the agent
  believes the earlier candidate was unchanged.
