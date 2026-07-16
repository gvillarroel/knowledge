# Astro Semantic OKF Evaluation

This evaluation transfers every Semantic OKF retrieval family to a frozen technical-documentation corpus. It uses the official English Astro documentation at commit `5c37be52c5038e1174be1e838d3dd5852db26a21`: 416 MDX pages, 2,944,859 checked bytes, 40 retrieval questions, and 10 evidence-first hard questions. Acquisition and all local generation, validation, building, and deterministic consultation can run without MCP.

## Frozen contract

| Item | Contract |
| --- | --- |
| Repository | `https://github.com/withastro/docs.git` |
| Commit | `5c37be52c5038e1174be1e838d3dd5852db26a21` |
| Authoritative content root | `src/content/docs/en` |
| Authoritative files | 416 English `.mdx` files |
| Checked source bytes | 2,944,859, preserved byte for byte from the accepted Know store |
| Questions | 40: 20 direct, 10 cross-document, and 10 hard |
| Hard ground truth | 50 atomic answer claims and 20 important negatives |
| Hard evidence | 46 exact heading-section bindings across 21 distinct pages |
| Source identity | Opaque `astro-doc-<16 hex>` derived from the canonical English route |
| Bundle-hit join | Exact `(source_id, record_id)` mapping to canonical route in `corpus/source-combination.json` |
| Build families | Legacy, classical, adaptive, embeddings, entity graph, and source-generic ensemble |

The MDX pages are authoritative. A validated Semantic OKF core is their authoritative projection. Plans, sectioning, graph edges, embeddings, lexical statistics, query expansion, rankings, qrels, answer packs, and scores are derived and non-authoritative.

## Layout

- `corpus/acquisition-manifest.json` binds the official repository commit, accepted ignored Know export, byte total, section counts, and authoritative tree digest.
- `corpus/input-inventory.json` binds all 416 source paths, routes, record IDs, source IDs, lengths, and SHA-256 digests.
- `corpus/manifest.json` is the minimal closed Semantic OKF manifest.
- `corpus/source-combination.json` is the only allowed evaluator join from bundle hits to route qrels.
- `benchmark/question-specs.json` is the reviewed evidence-first source for all 40 questions.
- `benchmark/retrieval-questions.jsonl` contains only prompts, types, and evaluator-side qrels.
- `benchmark/hard-ground-truth.jsonl` contains evaluator-only claims, negatives, joins, acceptable variants, failure conditions, and exact evidence bindings.
- `plans/` contains complete-corpus plans for every plan-driven builder.
- `results/runs/` is reserved for ignored, append-only bundles and detailed executions.
- Compact build, retrieval, and answer reports are published separately after an accepted run.

## Reproduce acquisition without MCP

Use an isolated Know store and pin the Git commit as the GitHub adapter branch. A commit SHA is accepted here deliberately: it prevents documentation changes from silently altering the benchmark.

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
$store = "tmp/astro-docs-know"
$key = "astro-technical-docs-2026-07"
$commit = "5c37be52c5038e1174be1e838d3dd5852db26a21"

python -m knowledge.cli --store $store add key $key
python -m knowledge.cli --store $store add github-repo https://github.com/withastro/docs.git --key $key --branch $commit
python -m knowledge.cli --store $store --verbose --json sync --key $key
python -m knowledge.cli --store $store --verbose --json export --key $key
```

If the key already exists, inspect and synchronize it instead of recreating it. The accepted ignored export is `tmp/astro-docs-know/exports/knowledge-export-20260716T085103Z.zip`, with 22,663,290 bytes and SHA-256 `5a49689fb5775c5f03717cbc11af0389d1014082b9f4c44fd21e4a03ffe71bec`. A different export is not silently accepted as the same corpus.

The official sitemap audit found exactly the same 416 English routes as the pinned English MDX tree. Other locales were excluded because they have uneven coverage and would add translations or fallback copies of the same documentation rather than independent evidence.

## Generate and validate

The generator copies accepted MDX bytes, publishes the corpus directory atomically, derives benchmark files and plans, and refuses any missing or ambiguous hard-evidence heading. `--check` is non-writing and detects stale, missing, extra, or byte-different corpus artifacts.

```powershell
$python = (Resolve-Path .venv/Scripts/python.exe).Path

& $python evaluations/semantic-okf-astro/scripts/prepare_corpus.py --json
& $python evaluations/semantic-okf-astro/scripts/prepare_corpus.py --check --json
& $python evaluations/semantic-okf-astro/scripts/validate_evaluation.py --json
& $python -m pytest tests/test_semantic_okf_astro_evaluation.py -q
```

The independent validator does not read the ignored Know store. It re-derives routes, opaque source IDs, builder Markdown record IDs, total source-record mapping, corpus hashes, qrel joins, hard-question subsets, character intervals, heading paths, selected-text hashes, claim bindings, derivation coverage, plan parity, and compact manifest digests from the checked files.

## Evaluation boundaries

Only each question string is supplied to a consultant. Qrels, source IDs, document routes, evidence paths, locators, hashes, claims, negatives, and derivation logic remain evaluator-only. Retrieval metrics and answer metrics must be reported separately: retrieving a relevant page does not prove that an answer used the required evidence or satisfied every atomic claim.

The checked plans are benchmark-independent and select all 416 sources. No plan contains question IDs or labels. The source-generic ensemble uses an empty identity override list, so distinct records are never merged by filename or title heuristics.
