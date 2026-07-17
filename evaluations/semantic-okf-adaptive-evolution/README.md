# Frozen Semantic OKF Adaptive Evolution

This directory records fixed-benchmark evolution of the standalone
`build-semantic-okf-adaptive` and `consult-semantic-okf-adaptive` packages. The original 30 retrieval
questions, 10 hard questions, ground truth, evaluator assertions, corpus inventory, and incumbent
reports are immutable under `semantic-okf-adaptive-frozen-40-plus-hard10-v1`.

Large bundles, candidate populations, and Skill Arena runs remain append-only and ignored. Compact
machine-readable summaries, configs, scripts, and English documentation are checked in.

## Outcome

Generation 0 evaluated ten answer-evidence ranking policies. Candidate 02 survived for paper coverage
and efficiency; candidate 07 survived for exact answer-claim and important-negative retrieval.
Candidate 07 became the canonical implementation base.

Generation 1 added deterministic facet-separated candidate discovery and authoritative response
finalization. It fixed most response-contract failures but an unrestricted evidence-selection policy
regressed answer quality, so the policy was discarded while both mechanisms were retained.

Generation 2 added minimal direct support: discovery may expand, but final evidence must directly
entail a stated claim; unused and merely topical records are removed; broad claims are split; and an
unresolved facet is qualified instead of forcing a full null answer. Its isolated treatment achieved
100% response-contract compliance, 98.0% correctness, 94.4% evidence validity, 93.7% grounding, and
100% important-negative coverage. It is the default adaptive consult policy; generation 0 remains the
high-grounding/exact-ID Pareto survivor.

Read [the conclusions and comparison tables](EVALUATION-CONCLUSIONS.md) for interpretation.

## Frozen boundary

Validate all 17 bound files, exact 30+10 composition, question/ground-truth alignment, and prompt
isolation:

```powershell
python evaluations/semantic-okf-adaptive-evolution/scripts/validate_frozen_benchmark.py
```

The expected-ID audit additionally checks the authoritative claim lines, paper-page hashes, adaptive
answer bindings, semantic relationship of every atomic statement, and exact assertions in four Skill
Arena configs:

```powershell
python evaluations/semantic-okf-adaptive-evolution/scripts/audit_expected_ids.py `
  --output evaluations/semantic-okf-adaptive-evolution/expected-id-audit.json
```

A legitimate benchmark correction must create a new benchmark ID and manifest. Do not edit a bound
question, ground-truth row, assertion, or evaluator in place.

## Real rebuild

Build twice into previously absent destinations and validate both:

```powershell
python -B skills/build-semantic-okf-adaptive/scripts/build_semantic_okf_adaptive.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-adaptive/adaptive-plan.json `
  tmp/adaptive-evolution-a --output-format json

python -B skills/build-semantic-okf-adaptive/scripts/validate_semantic_okf_adaptive.py `
  tmp/adaptive-evolution-a --output-format json

python -B skills/build-semantic-okf-adaptive/scripts/build_semantic_okf_adaptive.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-adaptive/adaptive-plan.json `
  tmp/adaptive-evolution-b --output-format json

python -B skills/build-semantic-okf-adaptive/scripts/validate_semantic_okf_adaptive.py `
  tmp/adaptive-evolution-b --output-format json
```

Compare sorted relative paths and byte hashes. The authoritative core must retain tree SHA-256
`331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`. The schema-1.2 derived
projection contains 831 reviewed answer bindings; every retrieval or answer artifact remains
non-authoritative.

## Read-only query verification

Use a validated bundle such as `BUNDLE` below. None of these commands writes to it.

```powershell
python skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py BUNDLE inspect

python skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py `
  BUNDLE search --mode adaptive `
  --query "How should graph and non-graph routes handle noisy evidence?" --top-k 10

python skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py `
  BUNDLE evidence-pack `
  --query "How should graph and non-graph routes handle noisy evidence?" --top-k 30

python skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py `
  BUNDLE coverage-pack `
  --query "How should graph and non-graph routes handle noisy evidence?" `
  --top-k 30 --per-facet 12 --maximum-facets 12
```

`finalize-answer` accepts a compact draft from an external file or stdin, rejects unknown claim IDs
and in-bundle draft paths, and reconstructs paper IDs, citations, evidence paths, and locators from the
validated binding artifact.

## Offline candidate evaluation

The predeclared [fitness contract](FITNESS.md) uses three sequential executions per hard question,
exact Recall@30 of atomic and negative claim identities, required-paper recall, evidence-contract
validity, all-40 no-regression gates, determinism, read-only consultation, and diagnostic latency.

```powershell
python evaluations/semantic-okf-adaptive-evolution/scripts/evaluate_candidate.py `
  --candidate candidate-11-minimal-direct-support `
  --bundle BUNDLE `
  --runtime skills/consult-semantic-okf-adaptive/scripts/_adaptive_snapshot.py `
  --questions evaluations/semantic-okf-adaptive/hard-questions.jsonl `
  --ground-truth evaluations/semantic-okf-adaptive/hard-ground-truth.jsonl `
  --retrieval-report RAW_RETRIEVAL_REPORT.json `
  --incumbent-summary evaluations/semantic-okf-adaptive/retrieval-summary.json `
  --top-k 30 --repetitions 3 `
  --output-json tmp/candidate-11-fitness.json `
  --output-markdown tmp/candidate-11-fitness.md
```

Reproduce the separately budgeted facet candidate analysis with:

```powershell
python evaluations/semantic-okf-adaptive-evolution/scripts/evaluate_coverage_pack.py `
  --candidate candidate-11-minimal-direct-support `
  --bundle BUNDLE `
  --runtime skills/consult-semantic-okf-adaptive/scripts/_adaptive_snapshot.py `
  --questions evaluations/semantic-okf-adaptive/hard-questions.jsonl `
  --ground-truth evaluations/semantic-okf-adaptive/hard-ground-truth.jsonl `
  --top-k 30 --per-facet 12 --maximum-facets 12 --repetitions 3 `
  --output-json tmp/coverage-pack-summary.json `
  --output-markdown tmp/COVERAGE-PACK.md
```

The facet union averages 81 unique claims and is explicitly not Recall@30.

## Skill Arena comparison

Each config has exactly two isolated profiles over the same bundle and model:

- a knowledge-only control with no declared consult skill; and
- a treatment with only `consult-semantic-okf-adaptive`.

The canonical task object is identical across generations, SHA-256
`da2fffaf3ea60976802ed6782633e9b2f079a6ddf65510d98a8c426c854d4a4b`. Validate and dry-run before
execution:

```powershell
skill-arena val-conf evaluations/semantic-okf-adaptive-evolution/skill-arena/g002-candidate11-hard10.yaml
skill-arena evaluate `
  evaluations/semantic-okf-adaptive-evolution/skill-arena/g002-candidate11-hard10.yaml --dry-run
skill-arena evaluate `
  evaluations/semantic-okf-adaptive-evolution/skill-arena/g002-candidate11-hard10.yaml
```

All three live runs completed 20 of 20 cells with zero execution errors. No generation achieved a
strict conjunctive pass, so the conclusion uses independently validated component metrics rather than
treating strict failure as zero answer quality.

## Checked-in evidence map

- `frozen-benchmark.json`: immutable benchmark boundary
- `expected-id-audit.json`: complete claim/config audit
- `generation-000-summary.json`: ten-candidate offline population
- `generation-001-summary.json`: rejected generation-1 policy and retained mechanisms
- `generation-002-summary.json`: accepted generation-2 Pareto survivor
- `coverage-pack-summary.json`: larger-budget facet discovery analysis
- `final-validation-summary.json`: final rebuild, manual-query, test, coverage, and package gates
- `skill-arena/*.yaml`: isolated causal comparison configs
- `scripts/*.py`: frozen validation and offline evaluation workflows
- `.specs/adr/0022-frozen-adaptive-semantic-okf-evolution.md`: durable architectural decision
