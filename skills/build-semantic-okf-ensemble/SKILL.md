---
name: build-semantic-okf-ensemble
description: Build and independently validate a new Semantic OKF bundle with one authoritative Markdown/RDF/SHACL core plus deterministic adaptive lexical, source-generic entity-section graph, embedding, exact identity-crosswalk, and quality-gated ensemble projections. Use when Codex must publish a standalone, reproducible multi-signal knowledge snapshot from a closed local manifest and plan without modifying an existing bundle or treating retrieval artifacts as authoritative.
---

# Build Semantic OKF Ensemble

Create a new immutable bundle in one atomic publication. Preserve the Semantic OKF core as the only authority; use every ensemble component only for discovery and later evidence selection.

## Required references

- Read [manifest.md](references/manifest.md) before authoring or reviewing the core manifest.
- Read [source-combination.md](references/source-combination.md) before combining independently governed inputs.
- Read [ensemble-plan.md](references/ensemble-plan.md) before authoring the closed ensemble plan.
- Read [coherence-contract.md](references/coherence-contract.md) before changing ontology, mappings, or validation rules.
- Read [ensemble-format.md](references/ensemble-format.md) before validating or publishing a bundle.
- Read [python-runtime.md](references/python-runtime.md) before installing the base or optional runtime.
- Read the component plan references only when changing that component: [adaptive-plan.md](references/adaptive-plan.md), [entity-graph-plan.md](references/entity-graph-plan.md), and [retrieval-plan.md](references/retrieval-plan.md).

## Build workflow

1. Declare source governance and identity policy before writing the manifest. Do not infer authority, joins, equivalence, or precedence from observed text.
2. Create a closed Semantic OKF manifest. Pin every local input and keep the separately declared entity vocabulary explicit.
3. Create one closed ensemble plan containing complete `adaptive`, `entity_graph`, and `embedding` child plans plus the three policies and mandatory quality gates. Prefer schema `2.0` for arbitrary declared records. Use schema `1.0` only to reproduce the legacy paper/claim contract.
4. In schema `2.0`, keep all three child `source_ids` selections identical, use graph schema `2.0`, keep adaptive PDF-page sources empty, and declare intentional cross-source identity joins only through sorted `identity.overrides`. Empty adaptive paper mappings are valid. In schema `1.0`, retain the complete paper mappings, paper-plus-claim selection, auxiliary vocabulary, and PDF-page list.
5. Install `scripts/requirements.txt` in an isolated environment. Install an optional lock only when the embedding child plan declares its corresponding offline backend.
6. Run the runtime smoke test.
7. Build to a path that does not exist. Never build over, repair, or mutate a published bundle.
8. Run the independent ensemble validator. For a release candidate, repeat the build to a second fresh path and require identical file inventories and hashes.

```bash
python scripts/runtime_smoke.py
python scripts/build_semantic_okf_ensemble.py MANIFEST.json ENSEMBLE-PLAN.json OUTPUT --output-format json
python scripts/validate_semantic_okf_ensemble.py OUTPUT --output-format json
```

## Authority and quality gates

- Treat only `semantic/`, `concepts/`, and their exact authoritative bindings as knowledge authority.
- Treat `adaptive/`, `entity-graph/`, `retrieval/`, and `ensemble/` as closed, hash-bound, non-authoritative projections.
- Require all three component validators to pass and bind the identical pre-projection core tree.
- In schema `2.0`, require child-plan digest parity, a total canonical identity crosswalk, exact cross-component record-set parity, and record-body passage evidence. Never infer a join from a path, prefix, title, filename, or paper-like token.
- Keep candidate graph-edge weight at zero for answer-evidence expansion; candidate
  entities, traversal scores, and embedding scores remain discovery-only. Semantic
  claim candidates must intersect reviewed exact answer bindings.
- Reject evaluation question IDs in plans. Do not encode answer keys, expected sources, benchmark labels, or question-specific routing.
- Fail closed on duplicate JSON keys, unknown schema members, unsafe paths, symlinks or junctions, stale hashes, non-finite values, missing evidence pages, incomplete component selection, or component/core parity failure.
- Use only a pinned offline embedding provider. Never download a model during a build or silently change provider, revision, dimension, splitter, or fallback behavior.
- The package is a local CLI workflow and requires no MCP server.

## Atomic publication

The entrypoint validates the entire plan before building the core, creates every layer inside one private sibling candidate, independently rederives all component artifacts, writes the ensemble binding last, and publishes once with an atomic rename. A failure must leave neither the requested output nor a private candidate.

The output directory must be new. Updating a source, plan, dependency lock, model revision, or algorithm identity creates a new bundle generation; it never alters an existing one.

## Completion gate

Before handing off a bundle, confirm that:

- the base runtime and every declared optional backend passed their smoke checks;
- the build and independent validator returned `valid: true` and `status: pass`;
- the manifest, full ensemble plan, child plan hashes, algorithm identities, component index hashes, and common core hash are persisted;
- every schema `2.0` selected record appears exactly once in `identity-crosswalk.jsonl`, all component record sets match it, and every locator/text hash resolves to authoritative `record.body`;
- every derived directory contains exactly its declared regular files;
- the authoritative core validates independently and was not changed by adding projections;
- a second clean build is byte-identical for the same inputs and runtime; and
- generated outputs remain outside the skill package and are handled as append-only release artifacts.
