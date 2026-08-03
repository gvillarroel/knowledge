# ADR 0094: Reject Classical Lossless-Block and Policy-Local Compiler Candidates

## Status

Accepted on 2026-08-02. This ADR accepts the rejection decision through V66.
The evolution stage is stopped without selecting a candidate for validation
or promotion; this is not a candidate acceptance or promotion.

## Context

ADR 0093 retained the canonical Classical consultation skill after v34
preserved six of six holdout answers but reduced mean tokens by only 8.96%
and was cheaper in only four of six cases. Across the broader lineage and the
subsequent one-way studies, the search tested deterministic terminal
compilation, source-role plans, exact fact catalogs, syntax-derived source
units, and lossless opaque source blocks. The acceptance rule remained
conjunctive: more than 30% fewer native input-plus-output tokens on fresh
optimizer-invisible tasks, zero execution errors, no paired metric regression,
and no independently reviewed semantic regression.

Several candidates achieved approximately 98–99% cumulative savings against
the canonical Classical baseline on development or validation cases. None
proved the full conjunction. V28, v45, v51, v52, v53, and v55 failed untouched
mechanical or semantic gates. V34 was semantically equivalent on its holdout
but saved only 8.96% against its same-task experimental parent. V20 and v21
had no untouched semantic acceptance gate. V54 failed released-development
semantic review before validation.

The v65-r6 treatment was the first lossless-block candidate to complete every
offline gate. Its successor validator passed 19 of 19 checks, independent
audit accepted the exact recovery delta, and the realizer sealed and verified
candidate tree
`e7848077f2bd1f717c55c16cb88afdbfeae903047f0b12076cddbe4fde4f9eea`.
The single released-q040 Harbor diagnostic completed without errors or retries
and preserved all 21 paired metrics at 1.0. It nevertheless used 22,374 native
tokens versus 15,325 for exact V62, a 45.9967% increase and 11,647 tokens above
the frozen 10,727 ceiling.

The R6 query result was 3,012 characters smaller than V62, but its provider
schema was 2,602 characters larger. The combined visible surface shrank only
410 characters, and native input fell only 96 tokens. Native output increased
by 7,145 tokens, concentrated in the second completion. This establishes that
further file-section or schema compression alone cannot meet the gate while
R6's observed output-token behavior remains unchanged. This one trajectory
motivates eliminating or tightly bounding that completion; it does not prove
that every future second-completion design must be equally expensive.

V66 therefore proposed a compiler-first route that would terminate after the
query completion when every required component had unique exact-source
support, with intended byte-exact V62 fallback when ambiguity was detected
before candidate-visible bytes. Independent hypothesis audit rejected it
before contract or implementation. It optimized only one
mixed-rendering policy, so fresh nonmatching tasks could legitimately save
zero tokens. It did not freeze a blind comparator, aggregate >30% rule, or
per-case consistency rule. Its unique-support tokenization, normalization,
anchors, scoring, tie-breaking, set bounds, and executable mutation oracle
were also deferred while an independent implementation was already required.
The ambiguity lifecycle did not prove that every fallback decision occurred
before candidate-byte exposure.

## Decision

Do not promote v65-r6, implement v66, or mutate the canonical
`consult-semantic-okf-classical` skill from either treatment.

Preserve R6 as mechanically complete negative evidence: lossless source
transport can retain all observed verifier metrics, but its measured provider
trajectory is more expensive than the immediate experimental parent. Preserve
V66 as a rejected hypothesis because policy-local fail-closed savings cannot
establish the requested global blind reduction and its discovery algorithm is
not reproducible as frozen.

Do not run the R6 forty-case cohort, semantic acceptance review, v25
validation, or v25 holdout. The R6 token gate failed before those actions were
authorized. Keep validation and holdout sealed and retain the canonical skill.

A future treatment requires a new immutable hypothesis that applies across the
complete consultation policy family and freezes, before implementation:

- total maintained-parser or vendored-parser source-unit extraction;
- complete unique-support, ambiguity, scoring, tie, and fallback algorithms;
- coherent compiler-owned answer construction and exact provenance;
- production-faithful one-completion termination tests;
- a finite mutation corpus with exact expected routes and equality checks;
- matched canonical and immediate-parent token comparators; and
- per-case, aggregate, mechanical, semantic, validation, and holdout gates that
  explicitly require more than 30% savings on fresh tasks.

Organize every future treatment as a new study with freshly registered
validation and holdout; the stopped v25 evolution stage cannot be resumed.
Any change to the blind comparator or dataset contract must be declared before
development rather than relaxing a gate after observing results.

Run the stages in order: offline gates first, then development, then one frozen
validation release, and only then the separately sealed holdout. Never use
validation or holdout outcomes to revise a candidate within the same study.

## Consequences

- There is no promoted or end-to-end accepted lower-token Classical
  consultation version as of v66.
- Character counts are diagnostics, not token results. A smaller serialized
  source does not prove fewer native tokens when schemas or completions grow.
- Using `sed` instead of Python is not itself a token optimization. Section
  extraction helps only when it reduces provider-visible text; internal script
  reads consume no model tokens.
- Immediate-parent and canonical-baseline savings must both be labeled. Large
  cumulative savings do not override a failed frozen incremental gate.
- Mechanical completeness does not replace semantic review, and semantic
  quality cannot rescue a failed conjunctive token gate.
- The append-only R6 q040 audit correction is retained as a versioned recovery:
  the originally registered artifact remains frozen, and the corrected v2
  audit preserves the same `REJECT` verdict.
- The complete attempt ledger is
  `evaluations/semantic-okf-classical-token-efficiency-study-v25/private/reviews/classical-token-optimization-attempts-v66-final.md`.
