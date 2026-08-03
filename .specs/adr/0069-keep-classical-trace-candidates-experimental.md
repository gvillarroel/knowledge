# ADR 0069: Keep Classical trace candidates experimental

## Status

Accepted on 2026-07-27.

## Context

Classical fusion is a strong direct-retrieval strategy with nDCG@10 83.23%,
Recall@10 83.46%, and P95 latency 106.76 ms. A two-stage Harbor trace-distillation
study therefore tested its consult and builder skills.

The first consult candidate converted three manually assembled, mechanically
invalid answers into three mechanically qualified answers. Only one of three
reached the required 0.70 primary threshold. A second candidate was developed from
a fresh q009/q011/q012 discovery cohort. It raised mean reward from 0.1885 to
0.7183, made all three answers mechanically valid, and raised the threshold pass
count from zero to two. q012 remained at 0.6049, below the required threshold.
Development requires a 100% pass rate.

Neither development cohort passed. In accordance with the trace-distillation
contract, both holdouts remained closed and unread. The agents also did not invoke
the generated finalizer during the second development run, so the gain cannot be
credited solely to the compiler.

The builder study added direct metrics for artifact integrity, snapshot identity,
reproducibility, validation, workflow safety, and efficiency. Two independent
Harbor tasks produced valid byte-identical replays and the exact authoritative
records digest. They differed from the Windows-built canonical Classical
projection only in CRLF versus LF serialization. The retrieval JSON values were
equal after newline normalization.

## Decision

Do not promote either consult candidate. Keep candidate v2 only as an experimental
artifact and leave `skills/consult-semantic-okf-classical` unchanged. A future
iteration must use a fresh discovery cohort and focus on semantic evidence
coverage, not reuse failed development evidence as mutation evidence.

Do not mutate or promote the Classical builder from this study. Leave
`skills/build-semantic-okf-classical` unchanged. Treat the observed projection
hash difference as a cross-platform serialization defect rather than a retrieval
quality regression.

Before changing the builder's newline behavior, define a paired Windows/Linux
promotion contract that requires one canonical newline policy, exact logical
retrieval-data parity, independent validation, and unchanged direct retrieval
metrics. Linux-only Harbor evidence cannot establish that cross-platform gain.

## Consequences

- The source consult and builder skills remain at their pre-study digests.
- Candidate v2 records a substantial development improvement without weakening the
  100% promotion gate.
- No holdout score or promotion claim exists for either consult candidate.
- Builder evaluation now has a reusable direct causal surface instead of relying
  on downstream answer reward.
- Cross-platform byte identity is a separate follow-up; current Linux and Windows
  projections contain the same retrieval data after newline normalization.
