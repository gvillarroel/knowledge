# Classical consult-to-builder trace distillation

Date: 2026-07-27

## Consult comparison

| Pos. | Pair / strategy | Mean primary reward | Tasks >= 0.70 | Mechanical gate rate | Reference-valid rate |
|---:|---|---:|---:|---:|---:|
| 1 | Consult candidate v2 | 0.7183 | 66.67% | 100.00% | 100.00% |
| 2 | Frozen consult v1 control | 0.1885 | 0.00% | 33.33% | 66.67% |

This study selected Classical fusion because the current direct benchmark places it
near the quality leaders while retaining low operational latency: nDCG@10 83.23%,
Recall@10 83.46%, and P95 106.76 ms. The trace study used Harbor 0.18.0,
`openrouter/openai/gpt-5.4-mini`, Pi 0.73.1, medium thinking, and zero retries.
All task trees passed deterministic regeneration, leakage checks, and the 40 oracle
quality gates before live use.

The first discovery cohort, q006/q007/q008, found valid retrieval followed by
manual answer-assembly failures. q006 and q007 emitted ledger-valid evidence
outside deterministic first-use order. q008 mixed one evidence identity with
another row's path and hashes. Candidate v1 added an exact evidence compiler and
a bounded structured-answer workflow. It changed the cohort from zero to three
mechanically qualified answers and raised mean reward from 0.0000 to 0.7364, but
only q007 reached 0.70. Its development pass rate was 33.33%, below the required
100%, so holdout stayed closed.

Candidate v1 was then frozen as an experimental control for a new discovery cohort,
q009/q011/q012. None of those three agents invoked the available finalizer. q009
missed the public independent-document minimum and q012 emitted an invalid
reference. Candidate v2 moved the structured-answer requirement ahead of the
ordinary workflow and extended the compiler with an explicit independent-document
minimum backed by the same record-to-document mapping as the verifier.

In development, candidate v2 scored 0.7659, 0.7840, and 0.6049. Every response
passed the response, reference, evidence, and document gates. The semantic utility
of q012 nevertheless remained below 0.70, so the candidate passed two of three
tasks rather than the required three. The agents again did not invoke the
finalizer; the observed improvement therefore cannot be attributed solely to the
compiler. Candidate v2 remains experimental, its holdout stayed closed and unread,
and the source consult skill was not modified.

## Direct builder qualification

| Treatment | Mean direct score | Artifact integrity | Canonical byte identity | Replay identity | Validation workflow | Safe efficient workflow |
|---|---:|---:|---:|---:|---:|---:|
| Source Classical builder, two independent tasks | 0.8333 | 100.00% | 0.00% | 100.00% | 100.00% | 100.00% |

The builder verifier is independent of answer generation. Each of two development
tasks built and validated two snapshots, compared complete sorted SHA-256
inventories, and checked eight pinned canonical artifacts. The two valid Harbor
trials used distinct task checksums and zero retries. Both produced complete,
validated, byte-identical replays and the exact authoritative records digest
`df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc`.
Only the pinned Classical projection byte hashes differed.

Two earlier builder attempts are retained as infrastructure evidence only. Their
agents completed, but a Harbor no-network verifier sidecar failed before scoring.
A subsequent separate verifier proved that this Harbor/Windows setup does not
share `/workspace`. The final append-only v4 tasks use the agent's shared
environment, deduplicate Pi tool calls by call ID, and produced two evaluable
results without exceptions.

## Cross-platform diagnosis

| Retrieval artifact | Windows bytes | Linux bytes | Equal after newline normalization |
|---|---:|---:|---:|
| `classical/associations.jsonl` | 1,526,205 | 1,523,205 | 100.00% |
| `classical/documents.jsonl` | 8,013,522 | 8,012,387 | 100.00% |
| `classical/lexicon.json` | 13,166,138 | 12,585,319 | 100.00% |
| `classical/topics.json` | 242,418 | 229,015 | 100.00% |

An independent Windows build matched the current canonical bundle byte for byte.
An independent build in the qualified Linux container matched both Harbor trials.
The four retrieval data artifacts are identical after CRLF/LF normalization and
parse to equal JSON values. The index and build report differ only in their
self-reported byte sizes and hashes. This is a serialization-portability defect,
not a retrieval-content or answer-quality change.

No builder mutation was promoted. A newline fix cannot show a causal gain inside
Linux-only Harbor because both the source and candidate naturally emit LF there.
It needs a separate cross-platform promotion contract that builds the same
candidate on Windows and Linux, requires one canonical newline policy, and then
re-runs direct retrieval parity. Treating the current byte mismatch as a semantic
builder regression would overstate the evidence.

## Decision

Keep both source skills unchanged. Candidate v2 is useful experimental evidence:
it raised the new-cohort mean by 0.5298 and the threshold pass rate from 0/3 to
2/3 while making every answer mechanically valid. It is not promotable under the
100% development gate, and no holdout result exists.

For the next consult iteration, use a fresh discovery cohort and target semantic
coverage rather than more answer-compilation mechanics. For the builder, first add
a genuine Windows/Linux newline-policy gate; do not optimize downstream QA reward
until direct build identity is portable.

## Evidence

- v1 source discovery:
  `generated/trace-distillation/20260727-consult-v1-proposal-analysis-01/trace-pool.json`
- v1 development and closed holdout:
  `generated/trace-distillation/20260727-consult-v1-promotion-gate-01/`
- v2 frozen-control discovery:
  `generated/trace-distillation/20260727-consult-v2-proposal-analysis-01/trace-pool.json`
- v2 development and closed holdout:
  `generated/trace-distillation/20260727-consult-v2-promotion-gate-04/`
- Direct builder trials:
  `evaluations/semantic-okf-datasets/results/20260727-classical-builder-discovery-baseline-04`
- Cross-platform build artifacts:
  `generated/trace-distillation/20260727-builder-host-windows-v1` and
  `generated/trace-distillation/20260727-builder-host-linux-v1`
- Candidate digests:
  v1 `sha256:0d5a3008676b44e306a5c0709bdc6746e34519e31683635861e9ac015eef6874`;
  v2 `sha256:8e1c861aa34c9c11bef20d35515abf4a94a4ae255ce6b7f842a389bac618e407`
