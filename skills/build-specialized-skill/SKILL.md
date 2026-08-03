---
name: build-specialized-skill
description: Build a standalone expert skill from one validated Semantic OKF knowledge folder and reviewed domain-application guidance. Use when Codex needs to add a distinct specialization stage after knowledge construction, bind the exact knowledge bytes into a portable skill, or validate and reproduce a generated expert skill before read-only consultation. This skill packages knowledge; it does not acquire sources, rebuild Semantic OKF, answer the final domain question, or mutate an existing expert skill.
---

# Build Specialized Skill

Package one immutable Semantic OKF snapshot with concise, reviewed instructions
for applying that knowledge. The output is a standalone expert skill that can be
installed and consulted without a separate knowledge mount or consultation skill.

## Standalone boundary

- Use only this skill's instructions, references, scripts, assets, and explicit
  user-supplied inputs.
- Accept one passing Semantic OKF folder and one UTF-8 Markdown guidance file.
- Never acquire sources, build or repair Semantic OKF, or import another skill.
- Never mutate the source knowledge folder or overwrite an output directory.
- Treat model-assisted guidance authoring as reviewable work. The deterministic
  builder only packages and binds the accepted guidance.

## Three-stage workflow

1. Finish knowledge construction and validate the complete Semantic OKF snapshot.
2. Inspect the snapshot and author guidance specialized for the intended domain
   tasks. Follow [expert-skill-contract.md](references/expert-skill-contract.md).
3. Build the expert skill into a new directory, validate it, reproduce it with
   `--check`, and then install or mount that generated skill for consultation.

Use `--query-template PATH` only when an evaluation has selected a reviewed,
self-contained retrieval adapter. Keep the default helper for ordinary experts.
The selected template becomes the generated `scripts/query_expert_knowledge.py`
and is digest-bound like every other expert artifact.
When that adapter has local modules or a requirements file, pass every regular
file separately with repeatable `--query-support PATH`. The builder copies each
file directly below `scripts/`, binds it in the manifest, and rejects basename
collisions. Query support requires an explicit custom template.

For a fixed workload whose questions and qrels are all exposed, the builder can
instead create its own retrospective supervised n-gram routing profile. Use
`--retrieval-profile retrospective-supervised-ngram` only after freezing and
measuring the default expert. This mode owns its query helper and routing index,
so it cannot be combined with `--query-template` or `--query-support`.

The integrated profile mode is not a promotion path. It requires
`--acknowledge-exposed-qrels`, records that every supplied qrel is development
evidence, sets `promotion_eligible: false`, and declares that no holdout exists.
Register a genuinely untouched cohort before making any generalization or
promotion claim.

The existing two-stage Build and Consult path remains valid when a reusable
generic consultant plus an external snapshot is preferred. Use this skill only
when the desired artifact is a self-contained expert that combines the snapshot
with instructions for applying it.

## Author the guidance

Read the ledger and representative concepts before writing guidance. Capture the
decisions that are specific to applying this knowledge: scope, task decomposition,
decision rules, evidence requirements, known negatives, and limits. Do not copy
the corpus into the guidance or state unsupported facts from memory.

The guidance file must contain exactly useful content, no TODOs, and these
second-level headings:

- `## Scope`
- `## Application workflow`
- `## Decision rules`
- `## Evidence and limits`

## Build and validate

Run commands from this skill directory, or prefix them with the skill root.

```bash
python scripts/build_specialized_skill.py KNOWLEDGE OUTPUT \
  --name domain-expert \
  --description "Apply the bundled domain knowledge to ..." \
  --guidance PATH_TO_GUIDANCE.md

python scripts/validate_specialized_skill.py OUTPUT

python scripts/build_specialized_skill.py KNOWLEDGE OUTPUT \
  --name domain-expert \
  --description "Apply the bundled domain knowledge to ..." \
  --guidance PATH_TO_GUIDANCE.md \
  --check
```

`OUTPUT` must be a new directory whose basename exactly matches `--name`.
`--check` builds a temporary candidate and compares complete regular-file bytes;
it never updates the accepted output. When using a selected custom adapter, add
`--query-template PATH_TO_FROZEN_QUERY_TEMPLATE.py` and the identical
`--query-support PATH` arguments to both build and check commands.

For an explicitly retrospective fixed workload, build a separate treatment:

```bash
python scripts/build_specialized_skill.py KNOWLEDGE PROFILE_OUTPUT \
  --name domain-expert-retrospective \
  --description "Apply bundled knowledge with retrospective routing." \
  --guidance PATH_TO_GUIDANCE.md \
  --retrieval-profile retrospective-supervised-ngram \
  --profile-dataset-id FROZEN_DATASET_ID \
  --profile-questions FROZEN_QUESTIONS.jsonl \
  --profile-qrel-key source_ids \
  --profile-identity-mode source-id \
  --acknowledge-exposed-qrels
```

Use `source-id` when qrels name exact ledger `source_id` values. Use `arxiv-id`
only when qrels and every authoritative record expose exactly one consistent
versioned arXiv identity. Repeat the identical arguments with `--check`.

## Generated expert contract

The generated skill contains:

- `SKILL.md` with the read-only expert workflow;
- `references/guidance.md` with the accepted application guidance;
- `references/knowledge/` with the complete immutable Semantic OKF snapshot;
- `scripts/query_expert_knowledge.py` for verified local ledger search;
- optional manifest-bound files beside the query helper for a selected
  multi-file adapter and its declared runtime dependencies;
- for integrated retrospective profiles,
  `scripts/expert_routing_index.json`, schema
  `semantic-okf-supervised-profile-index/2.0`, with question and ledger
  digests, one-to-five-token features, identity grouping, and an explicit
  no-holdout state;
- `expert-manifest.json` with knowledge tree, record, guidance, and runtime
  bindings; and
- `agents/openai.yaml` with portable interface metadata.

The generated query helper verifies the manifest and embedded knowledge tree
before every search or exact-record lookup. It does not perform network requests,
write indexes, cache data, or modify the skill.

The ordinary and custom-adapter packages retain manifest schema
`semantic-okf-expert-skill/1.0`. An integrated profile package uses
`semantic-okf-expert-skill/1.1` and binds the profile artifact and its
development-evidence disclosure. The routing profile is discovery metadata;
only the embedded ledger and concept files are authoritative answer evidence.

## Completion gate

Before returning the expert skill:

- the input build report says `status: pass` and `valid: true`;
- every ledger concept path is safe, exact, and present;
- guidance satisfies the required structure and contains no placeholders;
- any non-default query template and support set are self-contained, read-only,
  reviewed, dependency-declared, and selected without using the final
  evaluation cohort;
- any integrated supervised profile is a separate treatment, binds the exact
  question bytes and qrel identity contract, contains no exact-question lookup,
  and remains explicitly retrospective and promotion-ineligible;
- the generated skill passes its package-local validator;
- a repeated build passes `--check`;
- a representative query returns an exact record identity and concept path; and
- the source knowledge folder has the same tree digest as before the build.
