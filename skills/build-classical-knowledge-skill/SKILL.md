---
name: build-classical-knowledge-skill
description: Build a ready-to-use, standalone knowledge skill directly from a closed Semantic OKF source manifest, a classical retrieval plan, and reviewed application guidance. Use when Codex must generate both the embedded knowledge folder and its read-only expert consultation skill in one atomic operation, with deterministic BM25, topic, PPMI association, and fusion retrieval, exact physical citations, deep validation, and no model downloads or sibling-skill dependency.
---

# Build Classical Knowledge Skill

Generate one portable expert skill whose `references/knowledge/` contains a
deeply validated classical Semantic OKF snapshot and whose local query helper is
already bound to that exact snapshot.

## Standalone authority boundary

- Use only this package and explicit user-supplied manifest, plan, guidance,
  sources, and destination.
- Own source processing, knowledge materialization, retrieval projection,
  expert packaging, validation, and atomic publication.
- Never answer the user's domain question during generation.
- Keep the generated skill read-only. It may verify, inspect, search, hydrate,
  synthesize, and cite, but never build, repair, refresh, cache, or mutate.
- Do not import or execute a sibling skill, repository helper, fixture, or root
  document.

## Reference routing

For unchanged reviewed inputs, load only the expert contract. Otherwise read:

- [source-combination.md](references/source-combination.md) for multiple inputs
  or source topology;
- [manifest.md](references/manifest.md) for source mappings and schemas;
- [coherence-contract.md](references/coherence-contract.md) for semantic or
  provenance diagnosis;
- [classical-plan.md](references/classical-plan.md) for tokenizer, BM25, PPMI,
  topics, expansion, and reranking choices; and
- [expert-skill-contract.md](references/expert-skill-contract.md) before every
  generated-skill build or validation.

## Workflow

1. Define source authority, competency questions, evidence identities, intended
   users, and supported decisions.
2. Review the closed Semantic OKF manifest and classical plan. Select every
   intended source explicitly; keep exclusions explicit.
3. Author one UTF-8 guidance document with exactly one H1 and these headings:

   - `## Scope`
   - `## Application workflow`
   - `## Decision rules`
   - `## Evidence and limits`

4. Use CPython 3.12 in an isolated environment. Install
   `scripts/requirements.txt` and run the package-local smoke test.
5. Build into a new directory whose basename equals `--name`. The command
   constructs `references/knowledge/`, independently rederives the classical
   artifacts, verifies every physical concept and packed-record anchor, writes
   the consultation runtime, and publishes the complete skill with one rename.
6. Run the package validator, repeat the complete build with `--check`, run the
   generated runtime smoke, and perform one deep generated-skill verification.
7. Query representative exact, paraphrased, thematic, and synthesis requests.
   Require the generated rankings to match the same classical modes over the
   same snapshot and require every returned physical citation to resolve.

## Build

Run from this skill directory or prefix scripts with the copied skill root:

```bash
python -B scripts/build_classical_knowledge_skill.py \
  MANIFEST.json CLASSICAL_PLAN.json OUTPUT_SKILL \
  --name domain-knowledge-expert \
  --description "Apply the bundled domain knowledge with exact evidence." \
  --guidance REVIEWED_GUIDANCE.md \
  --concept-layout source-packed-v1 \
  --output-format json
```

The default physical layout is `source-packed-v1`. It preserves every logical
record while avoiding repeated small Markdown files for structured sources.

## Validate and reproduce

```bash
python -B scripts/validate_classical_knowledge_skill.py \
  OUTPUT_SKILL --deep-validation

python -B scripts/build_classical_knowledge_skill.py \
  MANIFEST.json CLASSICAL_PLAN.json OUTPUT_SKILL \
  --name domain-knowledge-expert \
  --description "Apply the bundled domain knowledge with exact evidence." \
  --guidance REVIEWED_GUIDANCE.md \
  --concept-layout source-packed-v1 \
  --output-format json --check

python -B OUTPUT_SKILL/scripts/runtime_smoke.py
python -B OUTPUT_SKILL/scripts/query_expert_knowledge.py \
  verify --deep-validation
```

## Consultation acceptance

The generated helper exposes `verify`, `inspect`, `search`, and `get`. Search
supports `bm25`, `topic`, `association`, and `fusion`; `fusion` is the default.
Every hit retains the classical identity and ranking fields and additionally
returns:

- `logical_concept_path` for stable record identity;
- `physical_concept_path` and `evidence_path` for the existing Markdown file;
- `evidence_anchor` for a record inside a packed collection; and
- `citation` for direct local use.

Do not accept a generated skill merely because it builds. On each claimed test
dataset, compare identical queries, modes, filters, and cutoffs against the
standalone classical consultation contract. Require identical ranked document
IDs, 100% exact physical evidence, no query errors, a passing deep validator,
and a deterministic rebuild. Keep grounded-answer quality separate from direct
retrieval parity.

## Completion gate

- Package-local runtime smoke passes with pinned dependencies.
- Manifest, source topology, guidance, and plan are reviewed and closed.
- The generated skill contains no symlink, unsafe path, unknown script, model,
  network dependency, timestamp, or absolute source path.
- Semantic core and classical projection pass deep independent validation.
- Every ledger record resolves to an exact physical Markdown file and anchor.
- A repeated build is byte-identical.
- Representative generated searches and exact hydration pass without writes.
- Dataset comparison meets or exceeds the matched standalone classical path on
  every declared hard gate; retrieval evidence is not mislabeled as answer
  correctness.
