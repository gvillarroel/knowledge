# Expert skill contract

## Contents

1. Input boundary
2. Guidance contract
3. Generated artifact
4. Consultation boundary
5. Reproducibility and evaluation

## Input boundary

The builder accepts one validated Semantic OKF folder. It requires:

- `index.md`;
- `semantic/build-report.json` with `status` equal to `pass` and `valid` equal
  to `true`;
- `semantic/records.jsonl`; and
- every exact `concept_path` named by the ledger.

The input is read-only. The builder rejects symlinks and path traversal so the
generated skill cannot depend on bytes outside its own directory.

## Guidance contract

Guidance is the procedural half of the expert. It explains how to apply the
bundled knowledge, not how the knowledge was acquired or materialized.

Use one H1 and these required H2 sections:

1. `Scope`: supported questions, intended users, and exclusions.
2. `Application workflow`: the ordered reasoning and evidence workflow.
3. `Decision rules`: domain-specific branches, thresholds, priorities, and
   important negatives that are grounded in the snapshot.
4. `Evidence and limits`: authoritative layers, citation form, uncertainty,
   missingness, and stop conditions.

Keep guidance concise. Prefer exact decision rules and small examples over a
second copy of the corpus. Remove TODOs, placeholders, speculative claims, and
instructions to use external knowledge when the bundled snapshot is authoritative.

## Generated artifact

`expert-manifest.json` uses schema `semantic-okf-expert-skill/1.0` for the
default helper and reviewed custom adapters. It binds:

- the complete regular-file tree digest and file count of
  `references/knowledge/`;
- the Semantic OKF record count and source build-report digest;
- the exact `SKILL.md`, guidance, query helper, and interface metadata bytes; and
- the skill name and description.

The manifest deliberately omits timestamps and absolute source paths. Identical
inputs therefore produce byte-identical expert skills across output locations.

The optional `--query-template` input is copied to the same bound query-helper
path. It must be a self-contained, read-only Python program that verifies the
manifest before retrieval. Repeatable `--query-support` inputs may supply its
direct local modules and dependency declaration. Every support input is copied
as a direct `scripts/` child and bound by path and SHA-256; symlinks,
directories, reserved names, and basename collisions are rejected. A custom
adapter is an evaluated artifact choice, not permission to acquire data, write
an index, or depend on undeclared host-local modules. Reproduction must pass the
identical template and support set to `--check`.

An integrated `retrospective-supervised-ngram` package uses manifest schema
`semantic-okf-expert-skill/1.1`. It additionally binds:

- `scripts/expert_routing_index.json` by path and SHA-256;
- profile schema `semantic-okf-supervised-profile-index/2.0`;
- the frozen dataset ID, exact question-file digest, question count, qrel key,
  and identity mode;
- the complete authoritative ledger digest and record count;
- `candidate_state: retrospective-all-exposed-supervised-profile`;
- `promotion_eligible: false`;
- a no-holdout declaration; and
- `exact_question_lookup: false`.

The builder learns only one-to-five-token features from the supplied
question/qrel pairs. The runtime combines those features with an authoritative
ledger-token fallback, deduplicates the selected primary identity, and returns
exact immutable records. It does not store question text, answers, or an exact
question lookup table.

Profile construction requires an explicit `--acknowledge-exposed-qrels` flag.
`source-id` mode requires qrels that are exact ledger source IDs. `arxiv-id`
mode requires every qrel and every record to resolve to one consistent
versioned arXiv identity. Missing, ambiguous, or unbound identities fail the
build.

## Consultation boundary

The generated expert skill is the only skill required for the new consultation
stage. It contains both the knowledge and the instructions for applying it.

Consultation is read-only:

- verify the embedded binding before answering;
- discover exact record identities before opening large concepts;
- use the accepted guidance to plan the domain task;
- cite exact bundled `concept_path` values;
- distinguish snapshot facts from inferences; and
- stop when the snapshot does not support the requested conclusion.

The existing generic Build and Consult architecture remains compatible. It is
still appropriate when knowledge should remain an external immutable mount used
by a reusable consultation skill.

## Reproducibility and evaluation

Evaluate the new flow as three distinct stages:

1. Build Knowledge: raw input to a passing immutable snapshot.
2. Build Specialized Skill: the exact snapshot plus reviewed guidance to a
   validated expert skill.
3. Consult: a query plus only that expert skill to a grounded answer.

Freeze every stage boundary by digest. A comparison must keep the dataset,
cohort, candidate budget, identity grouping, and metric contract identical.
Report alternatives as rows and aggregate dataset metrics as columns. Do not
mix status decisions or unavailable values into the primary metric table.

An all-exposed profile may be ranked only as a retrospective fixed-workload
treatment. It cannot be promoted, relabeled as holdout evidence, or used to
claim unseen-query performance. A future promotion study must register new
untouched cases, preserve the one-way holdout boundary, and evaluate the
selected artifact without exposing those qrels.
