---
name: build-classical-chunked-knowledge-skill
description: Build a new standalone classical Semantic OKF expert that preserves the complete immutable knowledge and accepted BM25, topic, PPMI association, and fusion retrieval while adding exact structure-aware chunks, linked-neighbor metadata, and query-budgeted nonredundant context selection. Use when papers or other large files make a generated knowledge skill send excessive evidence tokens to an answering model and the original build-classical-knowledge-skill must remain unchanged.
---

# Build Classical Chunked Knowledge Skill

Generate a portable read-only expert with byte-preserved classical knowledge
and a separate deterministic context projection. Keep the original generator
and every authoritative record unchanged.

## Standalone authority boundary

- Use only this package and explicit manifest, plan, guidance, sources, context
  plan, and destination inputs.
- Own source processing, knowledge construction, context derivation, expert
  packaging, validation, and atomic publication.
- Never answer the domain question during generation.
- Keep the generated expert read-only and network-free.
- Do not import or execute sibling skills, repository helpers, fixtures, or
  root documents.

## Reference routing

Read [expert-skill-contract.md](references/expert-skill-contract.md) and
[context-projection.md](references/context-projection.md) before every build.
For changed inputs also read:

- [source-combination.md](references/source-combination.md) for source topology;
- [manifest.md](references/manifest.md) for mappings and schemas;
- [coherence-contract.md](references/coherence-contract.md) for semantic or
  provenance diagnosis; and
- [classical-plan.md](references/classical-plan.md) for retrieval parameters.

## Workflow

1. Define authority, competency questions, evidence identities, intended
   decisions, answer-quality gates, and the comparable token unit.
2. Review the closed Semantic OKF manifest and classical plan. Keep every
   inclusion and exclusion explicit.
3. Review the context plan. Prefer Markdown structure, exact non-overlapping
   ranges, explicit neighbor links, and a bounded adaptive fallback. Do not use
   lossy summaries as evidence.
4. Author one UTF-8 guidance document with exactly one H1 and these headings:

   - `## Scope`
   - `## Application workflow`
   - `## Decision rules`
   - `## Evidence and limits`

5. Use CPython 3.12 in an isolated environment. Install
   `scripts/requirements.txt` and run the package-local smoke test.
6. Build into a new directory whose basename equals `--name`. The command
   builds and deeply validates the complete classical snapshot, derives and
   rederives every exact chunk, binds all metadata, and publishes once.
7. Run the generated validator, deterministic `--check`, runtime smoke, deep
   verification, one full-search parity probe, and representative `context`
   and neighbor-hydration probes.
8. Compare identical questions against the unchanged classical baseline.
   Require rank and evidence parity plus lower provider-visible context. Keep
   grounded answer quality and retrieval mechanics as separate gates.

## Build

```bash
python -B scripts/build_classical_chunked_knowledge_skill.py \
  MANIFEST.json CLASSICAL_PLAN.json OUTPUT_SKILL \
  --name domain-chunked-knowledge-expert \
  --description "Apply bundled domain knowledge with bounded exact context." \
  --guidance REVIEWED_GUIDANCE.md \
  --concept-layout source-packed-v1 \
  --output-format json
```

The bundled `assets/default-context-plan.json` is the default. Supply
`--context-plan CONTEXT_PLAN.json` only for a reviewed closed override.

## Validate and reproduce

```bash
python -B scripts/validate_classical_chunked_knowledge_skill.py \
  OUTPUT_SKILL --deep-validation

python -B scripts/build_classical_chunked_knowledge_skill.py \
  MANIFEST.json CLASSICAL_PLAN.json OUTPUT_SKILL \
  --name domain-chunked-knowledge-expert \
  --description "Apply bundled domain knowledge with bounded exact context." \
  --guidance REVIEWED_GUIDANCE.md \
  --concept-layout source-packed-v1 \
  --output-format json --check

python -B OUTPUT_SKILL/scripts/runtime_smoke.py
python -B OUTPUT_SKILL/scripts/query_expert_knowledge.py \
  verify --deep-validation
python -B OUTPUT_SKILL/scripts/query_expert_knowledge.py \
  context --query "COMPLETE QUESTION" --mode fusion --format markdown
```

## Consultation acceptance

Keep `search` byte-compatible with the matched classical runtime before
additive citations. Make `context` the normal answer path. Require it to:

- start from unchanged classical candidate ranks;
- emit only exact ledger slices with verified hashes and physical citations;
- account for conservative metadata and text token estimates;
- preserve distinct evidence identities before optimizing additional chunks;
- repair uncovered retrievable query facets before the general MMR pass;
- report retrievable-query coverage and uncovered facets;
- use Jensen-Shannon similarity only as a bounded redundancy signal, not as a
  substitute for relevance; and
- fail visibly into one larger budget or targeted linked-neighbor hydration
  when its quality guard is incomplete.

Do not call a smaller payload a quality improvement. Before promotion require
fresh independent semantic non-regression in addition to deterministic rank,
evidence, robustness, and token gates.

## Evaluation status

Treat this additive builder as experimental. The latest frozen consultation
treatment reduced mean agent tokens by 82.30% and produced valid evidence in
all six independent validation cases, but blind review still found two of six
semantic regressions. It was rejected for promotion. Do not replace the
classical builder or describe this package as the default until a new study
passes a fresh zero-regression semantic gate. See ADR 0108 for the durable
decision and study boundary.

## Completion gate

- Package and generated runtime smokes pass with pinned dependencies.
- Manifest, source topology, guidance, classical plan, and context plan are
  closed and digest-bound.
- Generated knowledge bytes equal the separately built classical snapshot.
- Every chunk deterministically rederives from one exact authoritative range;
  all previous/next links and hashes validate.
- Full search rankings and evidence remain unchanged.
- Representative context bundles fit their budgets and reconstruct exact
  evidence without writes.
- Build and `--check` are byte-identical and the copied package is portable.
- Relevant tests and the repository coverage gate pass.
