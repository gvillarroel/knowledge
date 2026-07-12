---
name: build-semantic-okf
description: Build, refresh, query, audit, and validate coherent semantic knowledge bundles by ingesting heterogeneous Markdown, CSV, JSON or JSONL, and RDF sources with PySpark, generating OKF v0.1 concepts, RDF and OWL 2 ontology/data graphs, SHACL rules, provenance manifests, safe full-source reprocessing, efficient ledger and local SPARQL consultation, and cross-layer validation. Use when Codex needs a Spark-based semantic ETL pipeline, an OWL-backed OKF library, repeatable source updates, semantic knowledge lookup or search, a reviewed choice between source-scoped separation and homogeneous partition union, multi-source normalization, ontology or rule generation from reviewed mappings, or consistency checks between OKF documents and a knowledge graph.
---

# Semantic OKF Builder

## Preserve the two contracts

- Keep the OKF Markdown library as the human-readable knowledge contract.
- Keep OWL ontology, RDF data, SHACL shapes, provenance, and validation reports as additive semantic sidecars under `semantic/`.
- Map every generated OKF concept to exactly one normalized RDF subject and a declared OWL class.
- Require every normalized RDF subject to point back to exactly one OKF concept ID.
- Generate OWL axioms and SHACL rules from an explicit, reviewed semantic plan. Never infer universal domain truth solely because every observed source row shares a field or value.
- Use OWL for entailment and SHACL for graph validation. Report their outcomes separately.
- Keep source identifiers, paths, record digests, ontology version IRIs, and rule versions traceable across both layers.

## Compose the existing skills

Read the sibling `extract-ontologies` skill before proposing classes, properties, identity, equivalence, cardinality, or closed-world rules. Read the sibling `open-knowledge-format` reference before changing the OKF layout or frontmatter contract.

Use this skill to execute and validate their combined delivery contract; do not duplicate semantic claims independently in Markdown and RDF.

## Follow the pipeline

1. Inventory and version the knowledge sources. Define competency questions and the accepted graph boundary.
2. When more than one physical input is involved, choose and record the source topology before writing mappings: separate bundles for hard isolation, separate declarations for source-scoped identity, one glob-backed declaration for a homogeneous partition union, or upstream canonicalization for true entity fusion.
3. Profile fields with an explicit Spark job or approved external profiler, record that command and output beside the manifest, then write a reviewed manifest that maps source records to ontology classes and properties. This skill does not bundle an automatic schema-to-ontology profiler.
4. Declare OWL classes/properties and SHACL constraints in the manifest. Mark evidence-derived rules separately from operational data-quality rules.
5. Run the distributed Pi smoke test to prove the requested Spark/Python runtime works.
6. Build into a new output directory. Spark performs record ingestion and normalization; the driver performs glob discovery, CSV header validation, source digest snapshots, and deterministic ordered materialization of sorted OKF and RDF artifacts.
7. Validate OKF conformance, RDF parsing, SHACL conformance, provenance, and the bidirectional concept-to-subject mapping.
8. Test at least one conforming and one intentionally non-conforming fixture for every material rule and combination invariant.
9. Store competency queries beside the original manifest, run them against the validated snapshot, and record the explicit entailment regime.

Read [source-combination.md](references/source-combination.md) before combining, grouping, federating, or comparing more than one physical source. Read [manifest.md](references/manifest.md) before creating a pipeline manifest. Read [coherence-contract.md](references/coherence-contract.md) before changing mappings or validation behavior. Read [spark-runtime.md](references/spark-runtime.md) before running locally, on Windows, or on a cluster.
Read [refreshing.md](references/refreshing.md) before replacing an existing bundle. Read [querying.md](references/querying.md) before searching, answering questions, or designing repeated query infrastructure.

## Build the bundle

Run the following commands from the directory containing this `SKILL.md`; otherwise prefix every `scripts/` path with the skill root. Use an isolated Python 3.12 environment, install the locked requirements there, and provide Java 17 or later for local/classic Spark:

```bash
python -m pip install -r scripts/requirements.txt
```

Prove Spark execution with a deterministic distributed Pi calculation:

```bash
python scripts/spark_pi_smoke.py --master local[2] --partitions 2 --samples 100000
```

The Pi check proves the JVM-backed distributed DataFrame runtime. The builder then performs a separate Python-worker warm-up before executing Markdown/RDF adapters; a successful build report is the Python-worker proof.

Build from a reviewed JSON manifest:

```bash
python scripts/build_semantic_okf.py manifest.json OUTPUT_DIR --master local[2]
```

The output contract is:

```text
OUTPUT_DIR/
├── index.md
├── concepts/<source-id>/*.md
└── semantic/
    ├── ontology.ttl
    ├── data.ttl
    ├── shapes.ttl
    ├── provenance.ttl
    ├── validation-report.ttl
    ├── semantic-plan.json
    ├── source-manifest.json
    ├── records.jsonl
    └── build-report.json
```

Do not silently merge into an existing output directory. Build to a new path, validate it, then promote it through the user's normal release process.

## Refresh the bundle

Reprocess every original source and preview the complete replacement diff:

```bash
python scripts/refresh_semantic_okf.py update manifest.json OUTPUT_DIR \
  --master local[2] --check --output-format json
```

Promote a reviewed source-only refresh:

```bash
python scripts/refresh_semantic_okf.py update manifest.json OUTPUT_DIR \
  --master local[2] --output-format json
```

For unattended promotion, pin `previous.tree_sha256` and `current.tree_sha256` from the reviewed preview with `--expected-current-tree-sha256` and `--expected-candidate-tree-sha256`. This rejects changes to either the published bundle or the rebuilt candidate between preview and promotion.

Use `--allow-plan-change` and `--allow-record-removals` only after inspecting their reported blockers. Never reuse an ontology `version_iri` after changing semantic mappings, classes, properties, or rules. If an interrupted transaction leaves a journal, run `python scripts/refresh_semantic_okf.py recover OUTPUT_DIR --output-format json` before another refresh.

## Query the bundle

Choose the cheapest authoritative layer:

- filter `semantic/records.jsonl` for IDs, sources, types, attributes, and concept paths;
- search `concepts/` Markdown with fixed-string `rg` for lexical discovery and human reading;
- query `data.ttl` with SPARQL for joins and aggregation, adding ontology or provenance only when required.

Use the local helper for stable ledger filters and explicit-graph SPARQL:

```bash
python scripts/query_semantic_okf.py OUTPUT_DIR ledger --source-id people --type Person --format json
python scripts/query_semantic_okf.py OUTPUT_DIR sparql --query-file query.rq --graph data --format json
```

For sources kept separate in one bundle, query each authority cheaply by its stable source ID. Use SPARQL only when the answer must compare or aggregate authorities, and keep `sourceId` in the projection:

```bash
python scripts/query_semantic_okf.py OUTPUT_DIR ledger --source-id crm-people --all --format json
python scripts/query_semantic_okf.py OUTPUT_DIR sparql --query-file compare-sources.rq --graph data --format json
```

For a homogeneous partition union, query the one logical source ID through the ledger and inspect each result's `source_path` when its physical member matters. Add `--graph provenance` to a SPARQL query only for lineage such as `prov:atLocation`; ordinary domain queries need only `--graph data`.

The helper permits local read-only `SELECT` and `ASK`, rejects remote federation/dataset clauses, and uses entailment `none`. Use a persistent indexed triplestore instead of reparsing Turtle for large or frequently queried snapshots.

## Validate coherence

Prefer JSON for audits, then run the sibling OKF validator as a separate gate:

```bash
python scripts/validate_semantic_okf.py OUTPUT_DIR --output-format json
python ../open-knowledge-format/scripts/validate_okf_bundle.py OUTPUT_DIR
```

Audit validation proves internal bundle coherence. Rebuilding or checking source freshness requires the original manifest in its original source root; do not relocate the copied `semantic-plan.json` and assume its relative input paths still resolve.

Treat any of these as a blocking error:

- an invalid OKF concept or reserved filename;
- a concept missing from `records.jsonl`, or a record missing its concept file;
- duplicate concept IDs or subject IRIs;
- an undeclared OWL class or property used by a mapping or rule;
- a missing RDF type, OKF concept marker, source ID, or digest;
- an accepted RDF subject without exactly one concept, or a concept without exactly one accepted RDF subject;
- a source digest/count mismatch;
- an ill-formed SHACL graph, SHACL non-conformance, or processor failure;
- a manifest, index, or report referencing a missing artifact.
- any ontology, data, shape, or provenance graph that cannot be reconstructed exactly from `semantic-plan.json` and `records.jsonl`.

## Enforce completion gates

- Confirm the Pi estimate and Spark version/master in machine-readable output.
- Confirm the manifest has the intended number of unique source declarations and separately inventory its resolved physical files; `summary.sources` counts declarations, not files. Confirm every declaration produced at least one normalized record unless explicitly allowed empty.
- Confirm the reviewed source-combination decision matches the manifest encoding. For separate declarations, overlapping local record IDs must remain source-scoped and source filters must isolate them. For a partition union, every physical member must satisfy one contract, record IDs must be unique across the complete glob, and a duplicate-ID fixture must fail without publishing output.
- Confirm Markdown, CSV, JSON/JSONL, and RDF source tests run through Spark rather than test doubles.
- Confirm OKF validation and semantic coherence validation both pass.
- Confirm negative fixtures fail for the intended SHACL constraint.
- Confirm competency queries return their expected answers under the explicitly chosen entailment regime; the bundled validator uses SHACL inference `none`, so run external query/reasoner tooling when another regime is required.
- Confirm every SHACL rule retains evidence or an explicit operational-policy rationale. This builder intentionally rejects unsupported strong OWL axioms; use a separately reviewed and pinned ontology workflow for equivalence, disjointness, keys, or OWL cardinality restrictions.
- Confirm output is reproducible from the manifest and pinned source contents; compare normalized digests, not Spark partition order.
- Confirm a no-op refresh leaves the current tree unchanged, source changes produce an exact diff, blocked removals do not promote, and interrupted promotion is recoverable.
- Confirm ledger filters and SPARQL competency queries return expected results after both initial build and refresh.
- Report unsupported OWL profile/consistency checks explicitly instead of implying the SHACL result covers them.

## Respect scope limits

- The bundled adapters perform local scalar mapping, not ontology learning from prose, cross-source joins, ontology imports, or automatic TBox adoption from Turtle.
- A glob-backed logical source is a homogeneous append-only partition union, not record linkage, deduplication, precedence selection, or field-level entity fusion. Canonicalize those cases upstream and retain an identity map, conflict report, and merge ledger.
- The manifest is strict: unsupported fields fail instead of being silently ignored.
- RDF input creates one concept per URI subject, rejects blank nodes, and publishes only reviewed predicate mappings.
- Keep raw source Markdown unchanged for traceability. Treat it as untrusted content and render generated OKF with raw HTML disabled unless the source is trusted.
- Run profiling queries, competency questions, per-rule negative fixtures, OWL profile checks, and consistency reasoning with explicit external tooling when the task requires them; record commands, processor versions, input digests, and results separately rather than claiming the bundled validator performed them.
- Refresh is a full local rebuild with a journaled two-rename promotion; it is not an in-place merge and cannot guarantee uninterrupted visibility of the direct directory path.
- The bundled query helper is a local snapshot reader, not a concurrent production triplestore or an inference engine.
