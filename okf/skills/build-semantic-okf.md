---
type: Agent Skill
title: Semantic OKF Builder
description: Build and maintain a Semantic OKF source definition and its generated
  knowledge folder with deterministic Python adapters for Markdown, CSV, JSON or JSONL,
  and RDF. Use when Codex needs to create or change a manifest, source topology, mapping,
  ontology, validation rule, generated snapshot, refresh, promotion, rollback, or
  recovery. This skill owns construction and maintenance only; it does not answer
  questions from the generated knowledge.
tags:
- codex
- skill
skill_name: build-semantic-okf
source_path: skills/build-semantic-okf/SKILL.md
---

# Build Semantic OKF

Create and maintain one deterministic, validated knowledge folder from reviewed local sources. Keep the complete construction contract inside this skill.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared Python requirements.
- Do not import scripts, instructions, validators, or conventions from sibling skills or repository files.
- Own source inspection, manifest authoring, materialization, validation, refresh, promotion, rollback, and recovery here.
- Do not search, answer, compare, cite, or synthesize from a published knowledge folder.

## Workflow

1. Write the scope and competency questions before defining the ontology.
2. Choose a source-combination topology. Preserve independent authorities as separate declarations; use a glob only for a homogeneous partition union; perform true entity reconciliation upstream.
3. Inspect the physical fields, identifiers, encodings, and data quality. Record any profiling command and result beside the manifest.
4. Write a reviewed manifest with explicit classes, properties, source mappings, schemas, and evidence-backed SHACL rules.
5. Verify the locked Python runtime.
6. Build into a new output directory. The adapters parse every declared source strictly, normalize records, detect source changes, sort canonical records, and materialize the complete snapshot atomically.
7. Validate the generated bundle independently.
8. Run deterministic acceptance fixtures against the generated artifacts without modifying the candidate.
9. Refresh by rebuilding all declared sources and promoting only a validated replacement snapshot.

Do not infer classes, relations, rules, identity matches, or source precedence from field names alone. Ask for review when the mapping would change domain meaning.

## Required references

- Read [source-combination.md](references/source-combination.md) before combining more than one physical source.
- Read [manifest.md](references/manifest.md) before writing or changing a manifest.
- Read [coherence-contract.md](references/coherence-contract.md) before changing mappings, materialization, or validation behavior.
- Read [python-runtime.md](references/python-runtime.md) before installing or running the scripts.
- Read [refreshing.md](references/refreshing.md) before updating an existing snapshot.

## Environment

Run commands from the directory containing this `SKILL.md`, or prefix paths with the skill root.

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate the same environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install and verify with the activated interpreter:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
```

Keep the environment activated for every command below. CPython 3.12 is the compatibility baseline used to compile the lock; a newer CPython is supported only when `runtime_smoke.py` passes with the exact locked dependencies. No external data-processing engine is required.

## Build and validate

```bash
python scripts/build_semantic_okf.py manifest.json semantic-okf-output
python scripts/validate_okf_bundle.py semantic-okf-output
python scripts/validate_semantic_okf.py semantic-okf-output --output-format json
```

The output directory must not already exist. A successful build contains:

```text
semantic-okf-output/
  index.md
  concepts/
  semantic/
    ontology.ttl
    data.ttl
    shapes.ttl
    provenance.ttl
    records.jsonl
    semantic-plan.json
    source-manifest.json
    validation-report.ttl
    build-report.json
```

These artifacts are one release unit. The builder keeps asserted data, ontology, provenance, constraints, and validation results in separate files and validates their cross-layer coherence before publication.

## Refresh all sources

Preview a complete reprocessing pass:

```bash
python scripts/refresh_semantic_okf.py update manifest.json semantic-okf-output --check --output-format json
```

Promote an approved candidate:

```bash
python scripts/refresh_semantic_okf.py update manifest.json semantic-okf-output \
  --expected-current-tree-sha256 <current-tree-sha256> \
  --expected-candidate-tree-sha256 <candidate-tree-sha256> \
  --allow-plan-change \
  --allow-record-removals
```

Omit an approval flag when that change class is not intended. Refresh never merges generated trees in place. If promotion is interrupted, run:

```bash
python scripts/refresh_semantic_okf.py recover semantic-okf-output
```

## Source rules

- `markdown`: one concept per file; mapped YAML values must be scalars; the body is preserved for reading.
- `csv`: exact, case-sensitive headers; header order is irrelevant; duplicate, missing, and extra columns fail; scalar conversion is strict.
- `json`: one object per line unless `multiLine=true`; missing declared fields become null; unknown fields are ignored; malformed or non-object records fail.
- `rdf`: one concept per absolute URI subject; blank nodes must be skolemized; repeated mapped predicate values remain repeated values.
- Non-RDF identity is `(source_id, record_id)`. RDF subjects are global and must not collide.
- Every generated concept keeps a single explicit origin. Multi-origin fusion belongs in an upstream canonicalization stage with an external identity map and merge ledger.

## Completion gate

Before delivery, confirm all of the following:

- the runtime smoke test passes;
- every declared source was read by a real adapter;
- the build and independent validator pass with no retained staging directory;
- paper or document text remains readable in the generated concepts;
- the source manifest reports stable content and record digests;
- OKF concepts, ledger subjects, data subjects, provenance origins, ontology classes, and SHACL targets agree;
- all construction acceptance fixtures pass without changing the candidate snapshot;
- a second build from unchanged inputs produces the same logical artifacts;
- refresh preview reports additions, changes, and removals before promotion.
