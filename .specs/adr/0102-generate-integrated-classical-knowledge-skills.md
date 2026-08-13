---
adr: "0102"
title: "ADR 0102: Generate Integrated Classical Knowledge Skills"
summary: "Build classical Semantic OKF knowledge directly inside a deterministic standalone expert skill while preserving exact parity with the separate builder and consultant stack."
status: "Accepted"
date: "2026-08-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Expert Skills"
tags: [knowledge, semantic-okf, classical-retrieval, skills, evaluation]
---

# ADR 0102: Generate Integrated Classical Knowledge Skills

## Status

Accepted.

## Context

The existing specialized-expert workflow intentionally separates knowledge
construction from expert packaging. A caller first materializes a validated
Semantic OKF snapshot and then gives that snapshot and reviewed guidance to
`build-specialized-skill`. This remains the appropriate generic path when the
snapshot is independently retained or shared by multiple consultants.

Some delivery workflows instead need one ready-to-install artifact and should
not have to coordinate an external knowledge directory, a builder skill, a
packager, and a consultation skill. Merely documenting those separate commands
inside a wrapper would leave the wrapper dependent on sibling packages and
would not satisfy the repository portability contract. Building knowledge on
first consultation would make the final expert write-capable and would prevent
its knowledge binding from being immutable before use.

The source-packed physical layout adds a further concern. Authoritative ledger
records retain stable logical `concept_path` values, but repeated structured
records may share one physical collection document. A generated expert must
therefore expose physical citations and exact anchors rather than handing the
caller a logical path that may not exist as a file.

## Decision

- Add the standalone write-capable
  `skills/build-classical-knowledge-skill/` package.
- Accept only a closed Semantic OKF manifest, a closed classical retrieval
  plan, reviewed guidance, generated skill metadata, and a new output path.
- Materialize the authoritative Semantic OKF core and classical retrieval
  projection directly into the candidate expert's `references/knowledge/`
  directory. Do not stage or require a prebuilt external snapshot.
- Bundle package-local construction code, the accepted read-only classical
  snapshot runtime, validation code, a generated-skill query helper, dependency
  locks, metadata, and reviewed guidance. Neither the generator nor its output
  may depend on sibling skills or repository-relative helpers.
- Publish the generated artifact under the closed
  `classical-knowledge-skill/1.0` manifest only after deep validation of the
  authoritative core, classical projection, complete tree, artifact bindings,
  every ledger record, and every physical evidence locator.
- Default generated consultation to `fusion` while preserving the explicit
  `bm25`, `topic`, `association`, and `fusion` routes and exact record lookup.
- Under `source-packed-v1`, translate logical record paths to
  `references/knowledge/concepts/<source_id>.md#record-<hash-prefix>`. Require a
  unique anchor and require the authoritative body to occur before the next
  record anchor. A body found elsewhere in the document is not a valid citation.
- Refuse output overwrites and symlinks, publish atomically, omit timestamps and
  absolute paths, and provide deterministic validation and `--check` commands.
- Keep the final expert read-only. It may verify, inspect, search, and retrieve
  exact records, but it may not construct, refresh, repair, or mutate knowledge.
- Retain the separate generic and specialized workflows. The integrated
  generator is an explicit direct-delivery variant and does not change Harbor's
  canonical `build-consult` or `consult-only` resource boundaries.

## Promotion gate

An integrated generator release is acceptable only when the same closed inputs
also build through the separate classical builder and consultant and the two
paths satisfy all of these checks:

- exact byte equality for every embedded knowledge file;
- exact byte equality for the classical consultation runtime;
- exact complete query-payload equality, including rankings, scores,
  expansions, filters, text, locators, and hashes, for all canonical questions
  across all four classical routes;
- zero ranking and payload mismatches;
- successful public generated-skill queries and deterministic rebuild checks;
- exact physical evidence resolution for every authoritative record and every
  retained evaluation hit.

This gate establishes deterministic build and retrieval equivalence. It does
not substitute for or claim a new model-judged Harbor answer-quality result.

## Validation evidence

The accepted implementation was rebuilt from the current closed classical
inputs for `graphrag-papers-40`, `astro-40`, and
`quantum-error-correction-papers-40`. Each generated expert passed deep
validation and an exact non-mutating rebuild check.

| Dataset | Records | Questions | Query-route cells | Exact payloads | Ranking mismatches | Verified hit citations |
|---|---:|---:|---:|---:|---:|---:|
| graphrag-papers-40 | 874 | 40 | 160 | 160/160 | 0 | 1,600/1,600 |
| astro-40 | 416 | 40 | 160 | 160/160 | 0 | 1,600/1,600 |
| quantum-error-correction-papers-40 | 15 | 40 | 160 | 160/160 | 0 | 1,527/1,527 |

Across the three datasets, all 480 complete payloads and rankings matched the
separate stack exactly. Validation covered all 1,305 authoritative records and
all 4,727 retained hits. Physical citations resolved every hit. They also made
183 GraphRAG hits directly openable whose stable logical `concept_path` did not
name a physical file under source packing. The knowledge trees contained 510
files in total and were byte-identical to their separate classical baselines.

The deterministic commands and complete machine-readable evidence are retained
in
[`20260813-parity-verification.md`](../../evaluations/integrated-classical-knowledge-skill/reports/20260813-parity-verification.md)
and its adjacent JSON report.

## Alternatives considered

### Keep only the separate multi-stage pipeline

Retained as a supported generic workflow but rejected as the only delivery
option. It requires the caller to coordinate and preserve several external
artifacts when one immutable expert is the desired result.

### Create a thin orchestrator over sibling skills

Rejected. The package and its generated output would cease to be standalone,
and behavior could drift when separately installed sibling versions differ.

### Build or repair knowledge on first consultation

Rejected. The expert would be write-capable, its evidence would not be frozen
before activation, and reproducible consultation would depend on source access.

### Copy a prebuilt snapshot and add guidance

Retained as `build-specialized-skill`. It does not satisfy the requested direct
construction workflow because it still requires an independently built input
snapshot.

## Consequences

Positive:

- one command produces one installable expert with immutable local knowledge;
- the generated artifact has no runtime dependency on the repository or sibling
  skills;
- consultation behavior is exactly equivalent to the accepted classical stack;
- packed records expose exact openable evidence rather than unresolved logical
  paths;
- deep, deterministic, and tamper-resistant validation happens before use.

Negative:

- the construction package deliberately carries copies of the accepted core and
  classical implementation, so release maintenance must keep parity tests in
  place;
- a generated expert includes its full knowledge tree and is larger than a
  guidance-only skill;
- deterministic retrieval parity does not itself measure how a future language
  model applies the packaged guidance in a complete answer.
