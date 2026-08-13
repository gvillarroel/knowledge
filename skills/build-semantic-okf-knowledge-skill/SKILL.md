---
name: build-semantic-okf-knowledge-skill
description: Build a ready-to-use, standalone knowledge skill directly from a closed Semantic OKF source manifest, reviewed application guidance, and one exact canonical retrieval family. Use when Codex must generate both the embedded knowledge folder and its read-only consultation skill atomically for legacy, embeddings, classical, adaptive, entity-graph, ensemble, Graphify, or Turso; preserve the matched native builder and consultant behavior; add exact physical citations; validate every artifact; and avoid sibling-skill runtime dependencies.
---

# Build Semantic OKF Knowledge Skill

Generate one portable expert whose `references/knowledge/` is built with the
selected canonical Semantic OKF family and whose matched native consultant is
already bound to that immutable snapshot.

## Standalone family boundary

- Use only this package and explicit user-supplied manifest, plan, guidance,
  sources, model cache, and destination.
- Never import or execute a sibling skill. Exact builder and consultant
  packages are vendored under `assets/families/` and digest-tested against
  their canonical sources.
- Keep construction and consultation distinct. This skill may build and
  package; every generated expert is read-only.
- Never answer a domain question during generation, and never treat retrieval
  or graph scores as domain facts.
- Reject links, unknown files, incomplete bindings, silent model fallback,
  mutable consultation, or a destination that already exists.

## Reference routing

Read [family-contracts.md](references/family-contracts.md) before choosing a
family. Read [expert-contract.md](references/expert-contract.md) before every
build, validation, comparison, or release.

For family-specific plan or consultation details, read only the relevant
vendored references under:

```text
assets/families/FAMILY/builder/references/
assets/families/FAMILY/consultant/references/
```

## Workflow

1. Freeze intended questions, authority boundaries, evidence identities,
   runtime constraints, and acceptance gates.
2. Select one family from the matrix in `family-contracts.md`. Use its exact
   source manifest and, when required, its closed plan.
3. Author UTF-8 reviewed guidance with exactly one H1 and these headings:

   - `## Scope`
   - `## Application workflow`
   - `## Decision rules`
   - `## Evidence and limits`

4. Install the selected builder lock from
   `assets/families/FAMILY/builder/scripts/requirements.txt`. For an embedding
   or ensemble plan that declares `sentence-transformers` or LlamaIndex, also
   install the matching optional builder locks and provide the pinned model
   revision in a local cache.
5. Run `scripts/runtime_smoke.py --family FAMILY`, then build into a new
   directory whose basename equals `--name`.
6. Run the independent validator, deterministic `--check` rebuild, generated
   runtime smoke, deep generated verification, and representative search/get
   operations.
7. On every claimed dataset, compare the generated expert against the exact
   separate builder/consultant pair with identical input, plan, question,
   route, filters, and cutoff. Require byte-identical knowledge, identical
   native payloads and ranks before citation enrichment, 100% resolvable
   physical evidence, and zero query errors.

## Build

Planless family:

```bash
python -B scripts/build_semantic_okf_knowledge_skill.py \
  MANIFEST.json OUTPUT_SKILL \
  --family legacy \
  --name domain-knowledge-expert \
  --description "Apply the bundled domain knowledge with exact evidence." \
  --guidance REVIEWED_GUIDANCE.md \
  --concept-layout source-packed-v1 \
  --output-format json
```

Plan-based family:

```bash
python -B scripts/build_semantic_okf_knowledge_skill.py \
  MANIFEST.json OUTPUT_SKILL \
  --family adaptive --plan ADAPTIVE_PLAN.json \
  --name domain-knowledge-expert \
  --description "Apply the bundled domain knowledge with exact evidence." \
  --guidance REVIEWED_GUIDANCE.md \
  --concept-layout source-packed-v1 \
  --output-format json
```

The supported family IDs are `legacy`, `embeddings`, `classical`, `adaptive`,
`entity-graph`, `ensemble`, `graphify`, and `turso`. The default physical
layout is `source-packed-v1`.

## Validate and reproduce

```bash
python -B scripts/validate_semantic_okf_knowledge_skill.py \
  OUTPUT_SKILL --deep-validation

python -B scripts/build_semantic_okf_knowledge_skill.py \
  MANIFEST.json OUTPUT_SKILL \
  --family FAMILY [--plan FAMILY_PLAN.json] \
  --name domain-knowledge-expert \
  --description "Apply the bundled domain knowledge with exact evidence." \
  --guidance REVIEWED_GUIDANCE.md \
  --concept-layout source-packed-v1 \
  --output-format json --check

python -B OUTPUT_SKILL/scripts/runtime_smoke.py
python -B OUTPUT_SKILL/scripts/query_expert_knowledge.py \
  verify --deep-validation
```

## Generated consultation

The generated stable helper exposes `verify`, `inspect`, `search`, and `get`.
Its search mode defaults to the selected family's native default and may be
overridden with `--mode`. It preserves the native JSON payload and adds exact
physical evidence fields to authoritative hits:

- `logical_concept_path`;
- `physical_concept_path`;
- `evidence_path`;
- `evidence_anchor` for packed structured records; and
- `citation`.

Advanced matched-family commands remain available in `scripts/native/` and
their exact instructions remain under `references/consultation/`. Generated
experts contain no builder implementation and never reach back into this
generator.

## Completion gate

- The package and selected-family runtime smokes pass from declared locks.
- Manifest, optional plan, reviewed guidance, family, and model/cache policy
  are explicit and closed.
- The exact family builder and independent validator pass.
- The generated expert contains no link, special file, timestamp, unknown
  artifact, builder code, absolute source dependency, or writable cache.
- Every non-knowledge artifact and the complete knowledge tree are digest-bound.
- Every ledger record resolves to exact physical Markdown evidence and, when
  packed, to one unique record anchor.
- Native verification and a deterministic rebuild pass without changing one
  knowledge byte.
- Dataset comparison equals or exceeds the matched separate pair on every
  declared mechanical gate. Retrieval parity is never relabeled as grounded
  answer correctness.
