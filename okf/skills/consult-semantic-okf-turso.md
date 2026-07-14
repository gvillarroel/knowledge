---
type: Agent Skill
title: Turso Semantic OKF Consultant
description: Give an agent read-only local tools and context to inspect, filter, query,
  compare, and cite an existing Turso-backed Semantic OKF knowledge database. Use
  when Codex needs exact record discovery, concept reading, attribute filters, SQL
  joins or aggregation, RDF statement traversal, provenance tracing, cross-source
  synthesis, schema inspection, or grounded answers from semantic/knowledge.db. This
  skill never builds, repairs, refreshes, synchronizes, or modifies knowledge.
tags:
- codex
- skill
skill_name: consult-semantic-okf-turso
source_path: skills/consult-semantic-okf-turso/SKILL.md
---

# Consult Semantic OKF with Turso

Answer from one published `knowledge.db` using local Turso Database queries while preserving revision, source, graph, and evidence boundaries.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared Python requirements.
- Treat the supplied database as the only domain input; this package contains no domain corpus.
- Do not import scripts, validators, or instructions from another skill or repository checkout.
- Require the local database file. Do not infer missing knowledge from sibling Markdown, RDF, a remote service, prior knowledge, or the web.

## Read-only boundary

- Reject published databases with active sidecars, copy the quiescent database into an isolated temporary directory, open that copy through `pyturso`, and require `PRAGMA query_only=1` before any consultation query.
- Accept only one bounded `SELECT`, `WITH`, or `EXPLAIN` statement in raw SQL mode. Reject mutation, transaction, attachment, extension, and file-access surfaces.
- Hash the published database before and after consultation; fail if bytes change. Let engine-created sidecars exist only beside the disposable working copy.
- Never build, migrate, repair, refresh, push, pull, or synchronize the database.
- If the database is absent, corrupt, stale, logically invalid, or uses an unsupported contract, report the condition and stop.

## Workflow

1. Parse the question and exact output contract: facts, operations, sources, graph scope, keys, types, ordering, limits, and evidence requirements.
2. Run the full `verify` command once for the database revision used as evidence.
3. Inspect `stats` or `schema` only when the source or column surface is not yet known.
4. Use `records` for exact identifiers, source filters, types, typed attributes, lexical discovery, and concept content.
5. Use `triples --graph data` or read-only SQL over `rdf_statements` for traversal and semantic joins. Select ontology or provenance explicitly when required.
6. Use `artifact` for the stored semantic plan, source manifest, ontology, shapes, or validation report.
7. For multi-source questions, establish breadth before depth and retain exact `concept_id`, `concept_path`, `source_id`, and `source_path` evidence.
8. Verify every returned scalar, relationship, citation, locator, and path in the database before answering.

## Required references

- Read [querying.md](references/querying.md) before choosing a table or writing SQL.
- Read [source-boundaries.md](references/source-boundaries.md) when authorities, partitions, permissions, or bundle boundaries matter.
- Read [cross-source-synthesis.md](references/cross-source-synthesis.md) before comparing or citing multiple sources.

## Environment

Run from this skill directory, or prefix every path with the skill root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1`. If `pyturso` is unavailable, return the runtime diagnostic. Do not fall back to `sqlite3` or legacy `libsql`, because that would bypass the declared engine contract.

## Verify and discover

Place the global `--validate` flag before the subcommand.

```bash
python scripts/query_turso_knowledge.py semantic/knowledge.db verify --format json

python scripts/query_turso_knowledge.py semantic/knowledge.db stats --format json

python scripts/query_turso_knowledge.py semantic/knowledge.db records \
  --source-id papers --type "Research Paper" --all --format json

python scripts/query_turso_knowledge.py semantic/knowledge.db records \
  --contains "retrieval strategy" --show-content --limit 10 --format json

python scripts/query_turso_knowledge.py semantic/knowledge.db records \
  --attribute status '"active"' --format paths
```

`--show-body` returns normalized record body text. `--show-content` returns the complete stored concept Markdown. Prefer the latter when evidence depends on frontmatter or exact concept text.

## Query RDF statements

```bash
python scripts/query_turso_knowledge.py semantic/knowledge.db triples \
  --graph data --predicate https://example.org/ontology/status \
  --object active --format json

python scripts/query_turso_knowledge.py semantic/knowledge.db triples \
  --graph provenance --subject SUBJECT_IRI --all --format json
```

Do not union graph names by default. `data` contains accepted domain statements, `ontology` contains reviewed schema, and `provenance` contains lineage. Shapes and validation reports are stored as artifacts and are never ordinary domain facts.

## Run read-only SQL

Write complex queries in a file outside the immutable database directory and bind values as JSON parameters:

```bash
python scripts/query_turso_knowledge.py semantic/knowledge.db sql \
  --query-file query.sql \
  --param source='"papers"' \
  --param minimum=3 \
  --format json
```

Inline example:

```bash
python scripts/query_turso_knowledge.py semantic/knowledge.db sql \
  --query "SELECT concept_type, COUNT(*) AS records FROM records GROUP BY concept_type ORDER BY records DESC" \
  --format json
```

Use explicit aliases so every result column name is unique. The helper caps output unless `--all` is intentional. It enforces both SQL screening and Turso's connection-level query-only mode.

## Completion gate

Before returning an answer, confirm:

- full logical verification passed for the cited database revision;
- the database and sidecar hashes were unchanged by consultation;
- the selected tables and graph names match the question;
- no shapes, validation results, ontology declarations, or provenance statements were presented as ordinary domain facts;
- every requested operation, clause, source minimum, key, type, order, uniqueness rule, and limit is satisfied;
- every cited `concept_id`, `concept_path`, source, locator, and supporting value exists in the returned database rows;
- every cross-source conclusion has direct evidence from the required independent sources;
- no claim depends on unmounted files, remote services, the web, or guesses when the database is authoritative.
