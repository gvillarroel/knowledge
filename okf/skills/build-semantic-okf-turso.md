---
type: Agent Skill
title: Turso Semantic OKF Builder
description: Build and maintain a validated Semantic OKF snapshot whose required indexed
  consultation projection is stored in local Turso Database. Use when Codex needs
  to create, migrate, validate, refresh, promote, recover, or inspect the construction
  of Turso-backed semantic knowledge from reviewed Markdown, CSV, JSON or JSONL, and
  RDF sources. This skill owns mutation and lifecycle operations only; it does not
  answer domain questions from the database.
tags:
- codex
- skill
skill_name: build-semantic-okf-turso
source_path: skills/build-semantic-okf-turso/SKILL.md
---

# Build Semantic OKF with Turso

Build one complete Semantic OKF release and its local `semantic/knowledge.db` projection with the Rust-based Turso Database engine.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared Python requirements.
- Do not import instructions, scripts, validators, or conventions from another skill or repository checkout.
- Treat the reviewed manifest and its local sources as explicit user-supplied inputs.
- Own source inspection, manifest authoring, materialization, database indexing, validation, refresh, promotion, rollback, and recovery here.
- Do not search, answer, compare, cite, or synthesize domain knowledge from a published database.

## Storage authority

- Publish the folder, Markdown concepts, RDF graphs, reports, and `knowledge.db` as one release unit.
- Treat the reviewed source plan and normalized records as provenance authority. Treat `knowledge.db` as the required indexed consultation projection of that exact release.
- Store sources, normalized records, concept documents, flattened attributes, core artifacts, and indexed data/ontology/provenance RDF statements in Turso.
- Bind database rows to the bundle with artifact hashes, concept hashes, source hashes, record hashes, row counts, schema digest, and one logical database digest.
- Reject any database-to-bundle drift. Never repair one side in place.

Turso Database is the ground-up Rust rewrite of SQLite. `libSQL` is the older SQLite fork. This package intentionally uses the `pyturso` distribution and `turso` Python module, not `sqlite3` or the legacy `libsql` client. Read [turso-storage.md](references/turso-storage.md) before changing the schema, engine, database lifecycle, or cloud boundary.

## Workflow

1. Define scope and competency questions before ontology or storage design.
2. Choose and record the source-combination topology.
3. Inspect physical identifiers, fields, encodings, and quality.
4. Write a reviewed manifest with explicit mappings, classes, properties, schemas, and evidence-backed SHACL rules.
5. Verify the locked runtime, including the actual Turso engine.
6. Build into a new hidden candidate. Reprocess every declared source, materialize the Semantic OKF artifacts, build `knowledge.db`, and validate both surfaces.
7. Publish the candidate only after every check passes.
8. Run deterministic acceptance queries against the database without modifying it.
9. Refresh by rebuilding the complete folder and complete database; never merge generated rows or files in place.

Do not infer classes, identity matches, source precedence, mappings, or validation rules from names alone. Require review when a choice changes domain meaning.

## Required references

- Read [source-combination.md](references/source-combination.md) before combining physical sources.
- Read [manifest.md](references/manifest.md) before creating or changing a manifest.
- Read [coherence-contract.md](references/coherence-contract.md) before changing mapping or validation behavior.
- Read [turso-storage.md](references/turso-storage.md) before changing database materialization or schema.
- Read [python-runtime.md](references/python-runtime.md) before installing or executing scripts.
- Read [refreshing.md](references/refreshing.md) before updating a published release.

## Environment

Run from this skill directory, or prefix every path with the skill root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1`. A platform without a compatible `pyturso` wheel may compile the Rust extension and therefore needs a working Rust and native build toolchain. Stop with the runtime diagnostic if `runtime_smoke.py` fails; never substitute `sqlite3` silently.

## Build and validate

```bash
python scripts/build_semantic_okf.py manifest.json semantic-okf-turso-output
python scripts/validate_okf_bundle.py semantic-okf-turso-output
python scripts/validate_semantic_okf.py semantic-okf-turso-output --output-format json
python scripts/validate_turso_store.py \
  semantic-okf-turso-output/semantic/knowledge.db \
  --bundle semantic-okf-turso-output --output-format json
```

The output must not exist before the build. A passing release contains:

```text
semantic-okf-turso-output/
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
    knowledge.db
```

To add Turso Database to an already validated compatible Semantic OKF bundle, use the package-local migration entry point:

```bash
python scripts/materialize_turso_store.py EXISTING_BUNDLE --output-format json
python scripts/validate_turso_store.py \
  EXISTING_BUNDLE/semantic/knowledge.db --bundle EXISTING_BUNDLE
```

The migration command is create-only. It never overwrites an existing database.

## Refresh all sources

Preview a complete rebuild:

```bash
python scripts/refresh_semantic_okf.py update manifest.json semantic-okf-turso-output \
  --check --output-format json
```

Promote only the reviewed candidate:

```bash
python scripts/refresh_semantic_okf.py update manifest.json semantic-okf-turso-output \
  --expected-current-tree-sha256 CURRENT_SHA256 \
  --expected-candidate-tree-sha256 CANDIDATE_SHA256 \
  --allow-plan-change \
  --allow-record-removals
```

Omit approval flags for change classes that are not intended. Recover an interrupted journaled promotion with:

```bash
python scripts/refresh_semantic_okf.py recover semantic-okf-turso-output
```

## Source rules

- `markdown`: preserve one readable concept per file; mapped frontmatter values must be scalar.
- `csv`: require exact case-sensitive headers independently of order and strict scalar conversion.
- `json`: accept JSON Lines unless `multiLine=true`; reject malformed, duplicate, non-object, ambiguous, or lossy values.
- `rdf`: require stable URI subjects and explicit local formats; reject blank source nodes.
- Scope non-RDF identity by `(source_id, record_id)` and keep RDF subject IRIs global.
- Perform entity fusion upstream with a reviewed identity map and merge ledger.

## Completion gate

Before delivery, confirm:

- the runtime smoke test identifies `pyturso` and Turso Database;
- every declared source was read by its real adapter;
- the build remained invisible until the bundle and database both passed validation;
- `PRAGMA integrity_check`, schema, row counts, logical digest, artifact parity, and concept parity pass;
- all normalized records, concepts, sources, attributes, and indexed RDF statements are represented in Turso;
- paper or document text remains readable from the `concepts` table;
- construction fixtures query the generated database without changing its bytes;
- a second build from unchanged inputs has the same logical database digest;
- refresh preview reports additions, changes, and removals before promotion;
- no credentials, remote URL, network dependency, or cloud write was introduced into the local baseline.
