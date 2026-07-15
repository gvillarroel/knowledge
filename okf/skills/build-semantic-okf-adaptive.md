---
type: Agent Skill
title: Build Semantic OKF Adaptive
description: Build and independently validate an atomic Semantic OKF/RDF snapshot
  plus a deterministic adaptive retrieval projection for arbitrary declared sources.
  Use when Codex needs a standalone offline builder that combines Bag of Words, BM25,
  topic communities, a PPMI term graph, query-aspect routing, diversified reranking,
  and exact evidence bindings without changing authoritative records or requiring
  embeddings. This skill owns construction only and never answers from a published
  snapshot.
tags:
- codex
- skill
skill_name: build-semantic-okf-adaptive
source_path: skills/build-semantic-okf-adaptive/SKILL.md
---

# Build Semantic OKF Adaptive

Build an authoritative Semantic OKF core and a model-free adaptive discovery projection as one validated release. The manifest may declare any source formats supported by the bundled Semantic OKF runtime; the retrieval plan selects source IDs rather than relying on corpus-specific paper, claim, or entity schemas.

## Standalone authority boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the manifest, physical sources, adaptive plan, and absent destination as explicit user inputs.
- Do not import or execute sibling skills, repository helpers, fixtures, or root documentation.
- Own source processing, authoritative-core materialization, adaptive derivation, validation, and atomic publication.
- Never search, answer, compare claims, or cite from a published snapshot.
- Keep `adaptive/` non-authoritative. Only the ledger, concept files, and purpose-selected RDF graphs carry domain authority.

## Required references

- Read [source-combination.md](../../skills/build-semantic-okf-adaptive/references/source-combination.md) before combining physical sources.
- Read [manifest.md](../../skills/build-semantic-okf-adaptive/references/manifest.md) before writing or changing a manifest.
- Read [coherence-contract.md](../../skills/build-semantic-okf-adaptive/references/coherence-contract.md) before changing mappings or validation.
- Read [adaptive-plan.md](../../skills/build-semantic-okf-adaptive/references/adaptive-plan.md) before selecting sources or retrieval parameters.
- Read [adaptive-format.md](../../skills/build-semantic-okf-adaptive/references/adaptive-format.md) before reviewing derived artifacts.
- Read [python-runtime.md](../../skills/build-semantic-okf-adaptive/references/python-runtime.md) before installing or running the package.

## Workflow

1. Establish source authority, exact physical inputs, evidence identities, and competency questions.
2. Inspect schemas and encodings; write a closed Semantic OKF manifest with explicit mappings.
3. Write a closed adaptive plan. Select source IDs and pin tokenization, BM25, association, topic, expansion, diversification, and aspect-fusion parameters.
4. Install only `scripts/requirements.txt`. The retrieval projection itself uses the Python standard library and performs no model selection, download, or hosted request.
5. Build into an absent path. The command creates the authoritative core, exact record or page passages, verified reviewed-claim answer bindings, lexical/topic/term-graph artifacts, and one hash-bound adaptive policy before a single final rename.
6. Run the independent validator against the published release.
7. Rebuild identical inputs and plan into another absent path; require an identical sorted path-and-byte tree.
8. Open representative derived documents and their bound authoritative records; verify exact locators and hashes without running a consultation workflow.

Reject unknown plan members, implicit defaults, partial selection, unsafe paths, approximate locators, stale hashes, mutable publication, and statistical topics or associations presented as reviewed truth.

## Build and validate

```bash
python scripts/build_semantic_okf_adaptive.py manifest.json adaptive-plan.json semantic-okf-adaptive --output-format json
python scripts/validate_semantic_okf_adaptive.py semantic-okf-adaptive --output-format json
```

The destination contains the complete Semantic OKF core and exactly seven files under `adaptive/`: `index.json`, `documents.jsonl`, `answer-bindings.jsonl`, `lexicon.json`, `associations.jsonl`, `topics.json`, and `build-report.json`.

`answer-bindings.jsonl` is a derived response adapter, not authority. A row is emitted only for a reviewed record whose explicit evidence locator resolves to one or more declared paper records with matching paper identity and exact `## PDF page N` headings. It preserves the authoritative claim identity and text, canonical `PDF-page-N` locator tokens, integer citation pages, source paths, and hashes as separate typed fields. It never contains benchmark question IDs, expected answers, or evaluator labels.

The plan-bound adaptive policy does not learn benchmark labels. At consultation time it protects the strongest full-query results, deterministically decomposes synthesis queries into lexical aspects, and uses reciprocal-rank evidence-identity fusion to improve coverage. All chosen evidence still resolves to an exact authoritative record or character range.

## Completion gate

Confirm that:

- package-local runtime smoke passes;
- every requested source is selected or explicitly excluded;
- core and adaptive validation pass without warnings;
- the artifact tree is closed and contains no symlink;
- every passage binds to one source, record, concept, source path, locator, and text hash;
- every answer binding re-derives from a reviewed authoritative record and an existing exact paper-page heading;
- BM25 statistics, PPMI neighbors, topics, topic weights, plan hash, and report reproduce;
- failure leaves no destination or private candidate;
- two clean builds are byte-identical; and
- representative derived document locators resolve to the exact authoritative text.
