# Tika/MALLET/Tantivy reflective Pareto evaluation

Date: 2026-07-27

## Evaluation

This study uses the Harbor reflective Pareto search rather than trace distillation.
Each candidate is a complete standalone skill bundle, each Harbor job installs
exactly one evaluated skill, and selection uses a case-level reward vector rather
than an aggregate-only winner. Development and holdout are physically separate.
Holdout is opened only for a development-qualified archive member.

The consultation evaluation uses three frozen `consult-only` discovery questions
over the immutable Tika/MALLET/Tantivy snapshot. The verifier checks the response
contract, exact evidence identities, valid independent-document minimums, focus-set
coverage, and retrieval utility. The primary reward is non-compensating: a response
with an invalid evidence row or insufficient focus coverage receives zero even when
its prose is useful.

The builder evaluation is direct and excludes consultation. Each task mounts only
immutable ingestion and retrieval plans, a qualified Linux JDK 17 runtime, and
read-only Tika and MALLET installations. The agent must publish two absent
destinations, independently validate both snapshots, and prove a byte-identical
sorted path/SHA-256 inventory. The verifier scores artifact integrity, authoritative
snapshot identity, reproducibility, runtime-contract compliance, required validation
invocations, and workflow efficiency.

## Consultation development

The generation-zero archive retained only the frozen source baseline. Four
generation-one branches then tested facet planning, final-answer repair, a mandatory
finalizer, and a compact finalizer. The strongest partial behavior came from the
mandatory-finalizer branch: it produced mechanically valid q013 and q016 answers but
lost the closing evidence-array bracket on q014. The compact branch repaired that
formatting instruction but did not follow the required `answer-pack` and
`finalize-answer` path consistently.

| Candidate | q013 | q014 | q016 | Mean | Pass rate | Qualified |
|---|---:|---:|---:|---:|---:|---|
| Frozen source baseline | 0.0000 | 0.0000 | 0.7503 | 0.2501 | 33.3% | No |
| Compact finalizer | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0% | No |

The compact candidate had no provider or infrastructure failures. q013 contained one
crossed locator/hash identity after the agent assembled evidence manually, q014 had
valid evidence identities but only five valid independent documents against a
minimum of seven, and q016 had five invalid evidence rows. The Pareto archive is
empty, generation seal
`sha256:214405a9f2be54f09a52b8600f0450e17cb8b217eefe7cb0ba770a7783e4219a`,
and consultation holdout was not used. The source consultation skill remains
unchanged.

## Builder verifier correction

The first direct-builder verifier counted Pi `message_start` and `message_end`
copies of the same tool call and treated script `--help` probes as real build or
validation invocations. That made the workflow-efficiency component unsuitable for
selection. The completed artifact and reproducibility evidence from that attempt is
preserved, but its command metrics are excluded from promotion.

Task schema 1.2 accepts only completed Pi message events and excludes `--help`
probes from invocation counts. Its deterministic four-task tree has SHA-256
`af158cc04929df48fc539d423e7e3ede70d95d876c3680eebeeb859440568005`.
The corrected behavior is covered by a synthetic duplicate-event regression test.

## Builder candidate

Candidate `v46-qualified-runtime` descends from the mechanically successful v45
runtime-contract bundle. In a caller-declared no-install environment, it verifies
all pinned Python distributions already supplied by the qualified image and uses the
current CPython 3.12 interpreter directly. It forbids a redundant virtual
environment, `pip install`, and network access in that branch. It also fixes the
requested sequence to one runtime smoke, two builds, two independent validations,
and one inventory comparison, without `--help` probes or repeated successful steps.

## Builder development

| Candidate | qualified-runtime-a | qualified-runtime-b | Mean | Passed |
|---|---:|---:|---:|---:|
| Frozen source baseline | 0.7917 | 0.6250 | 0.7083 | 0/2 |
| v46-qualified-runtime | 1.0000 | 1.0000 | 1.0000 | 2/2 |

The candidate passed every reward component in both development cases: artifact
integrity, authoritative snapshot identity, reproducibility, runtime-contract
compliance, required validations, and workflow efficiency. The development archive
therefore selected only v46. Its sealed bundle digest is
`sha256:3a1d2bfb66def8a911ffe7197740eef90a9638dab0522eb39f12a8c369f5c908`;
the generation seal is
`sha256:d0b2ec45fe66670ca9f1cb0d6f8ae3cfc5a1df8704c064c6c9f66b1822956944`.

## Builder holdout and promotion

The frozen holdout ran two independent attempts per case.

| Candidate | qualified-runtime-c | qualified-runtime-d | Overall mean | Regressed cases |
|---|---:|---:|---:|---:|
| Frozen source baseline | 0.7917 | 0.7083 | 0.7500 | — |
| v46-qualified-runtime | 1.0000 | 1.0000 | 1.0000 | 0 |

The promotion gate accepted v46 with a mean gain of `+0.2500`, four of four
candidate trials at `1.0000`, no candidate errors, complete required rewards, and
no case regression. Every candidate snapshot contains 30 authoritative records
with records SHA-256
`b64917f411ea57a18114ba44d7a4779564d528542b3c6ec6084d96a4ddf40805`.
The source builder was replaced by the exact holdout-copied candidate bundle and
matches the selected digest. The source consultation skill was not changed.

## Validation

- The canonical `astro-40` and `graphrag-papers-40` registries and all eight
  registered build/consult pairs pass validation.
- The direct comparison contract passes with 23 measured strategies and three
  aggregate metrics.
- The metric-only final-report table passes with all 23 comparable direct routes.
- The focused consultation, builder, Harbor-runtime, trace-adapter, and Pareto
  scorer suite passes 37 tests.
- The repository coverage gate passes all 751 tests with 90.9% total application
  coverage against the required 80% threshold.
