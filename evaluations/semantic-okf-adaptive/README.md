# Semantic OKF Adaptive Evaluation

This evaluation adds an isolated, source-generic Semantic OKF generation without modifying the
legacy, embedding, classical, or entity-graph packages. It compares thirteen retrieval routes on the
same forty questions and evaluates the answer-level effect of adding the adaptive consult skill on the
ten hard questions.

This directory is the historical generation-0 baseline. Subsequent fixed-benchmark skill evolution,
the expected-ID audit, and the current generation-2 recommendation are documented in
`evaluations/semantic-okf-adaptive-evolution/README.md` and
`evaluations/semantic-okf-adaptive-evolution/EVALUATION-CONCLUSIONS.md`.

## Scope and authority

The authoritative input is exactly the previously pinned corpus:

- 15 paper Markdown files;
- 15 reviewed-claim JSONL files; and
- the separately declared analysis vocabulary used by the Semantic OKF core but excluded from the
  adaptive retrieval selection.

The resulting core contains 31 sources and 874 records. Its logical tree SHA-256 remains
`331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`, identical to all compared
alternatives. Everything below `adaptive/` is derived, non-authoritative, closed, hash-bound, and
reproducible offline.

## Standalone skill pair

The independently installable packages are:

- `skills/build-semantic-okf-adaptive`
- `skills/consult-semantic-okf-adaptive`

The builder persists 1,135 exact passages over 846 selected paper and claim records, 96,799 lexical
terms, 3,000 PPMI association rows, and 16 deterministic topic communities. Its generic defaults use
one full-record passage and a source-scoped evidence identity. The evaluation plan explicitly opts the
known Markdown papers into PDF-page segmentation and maps paper and claim sources to reviewed paper
identities.

The consultant exposes `bm25`, `topic`, `association`, `fusion`, and `adaptive`. Adaptive mode protects
the strongest full-query evidence, decomposes multi-part questions into bounded aspects, and permits a
new aspect-only identity only at the plan-pinned rank threshold. Every mode returns exact
`evidence_rows` copied from authoritative bindings. For structured answers, the skill treats synthesis
as a coverage checklist, runs focused follow-up queries for unsupported aspects, and losslessly adapts
authoritative claim and page fields to the user's declared response types.

## Question and ground-truth contract

`retrieval-questions.jsonl` contains the unchanged original thirty questions followed by the same ten
evidence-first hard questions, `q031` through `q040`. The checked hard ground truth records atomic
answer claims, required papers and sources, exact authoritative paths and locators or text hashes,
derivation logic, acceptable variants, and important negatives. Task prompts do not contain hidden
answers.

The hard-question artifacts are inherited byte-for-byte from the classical evaluation and rebound by
`hard-ground-truth-manifest.json`. Validate them with:

```powershell
python evaluations/semantic-okf-classical/scripts/generate_hard_questions.py --check
python evaluations/semantic-okf-classical/scripts/validate_hard_ground_truth.py `
  --repo-root . --evaluation-dir evaluations/semantic-okf-adaptive
```

## Rebuild and independent validation

Build into previously absent destinations:

```powershell
.venv\Scripts\python.exe -B skills\build-semantic-okf-adaptive\scripts\build_semantic_okf_adaptive.py `
  evaluations\graphrag-cross-paper\manifest.json `
  evaluations\semantic-okf-adaptive\adaptive-plan.json `
  tmp\adaptive-a --output-format json

.venv\Scripts\python.exe -B skills\build-semantic-okf-adaptive\scripts\validate_semantic_okf_adaptive.py `
  tmp\adaptive-a --output-format json

.venv\Scripts\python.exe -B skills\build-semantic-okf-adaptive\scripts\build_semantic_okf_adaptive.py `
  evaluations\graphrag-cross-paper\manifest.json `
  evaluations\semantic-okf-adaptive\adaptive-plan.json `
  tmp\adaptive-b --output-format json
```

The accepted run is `20260714-adaptive-final-05`. Its two 890-file builds have identical relative paths
and file hashes. The sorted path-and-file-hash manifest digest is
`bb864ddbf4e4e2815fe03fcc42f676586aafd8919e361d1a418d028ccf34f70d`. See
`determinism-report.json` and `evaluation-environment.json` for reproducibility bindings.

## Retrieval comparison

The final schema 1.5 comparator extends the evidence-valid schema 1.2 contract. It runs:

1. legacy lexical;
2. embedding lexical, vector, and hybrid;
3. entity-graph lexical, entity, traversal, and fusion;
4. classical BM25, topic, association, and fusion; and
5. adaptive fusion.

Every route receives the same forty questions, authoritative core, and direct top-10 budget. Each hit
is independently checked for exact record, concept, source path, locator, text hash, and core parity.
The compact checked outputs are `retrieval-summary.json` and `retrieval-summary.md`; the 6.9 MB raw
report remains under the ignored append-only final run.

The comparison command requires the five validated bundles and four consult entry points:

```powershell
.venv\Scripts\python.exe evaluations\semantic-okf-adaptive\scripts\compare_retrieval.py `
  --inventory evaluations\semantic-okf-embeddings\input-inventory.json `
  --questions evaluations\semantic-okf-adaptive\retrieval-questions.jsonl `
  --legacy-bundle LEGACY_BUNDLE `
  --embedding-bundle EMBEDDING_BUNDLE `
  --classical-bundle CLASSICAL_BUNDLE `
  --entity-graph-bundle ENTITY_GRAPH_BUNDLE `
  --adaptive-bundle ADAPTIVE_BUNDLE `
  --embedding-consult-script skills\consult-semantic-okf-embeddings\scripts\query_semantic_okf_embeddings.py `
  --classical-consult-script skills\consult-semantic-okf-classical\scripts\query_semantic_okf_classical.py `
  --entity-graph-consult-script skills\consult-semantic-okf-entity-graph\scripts\query_semantic_okf_entity_graph.py `
  --adaptive-consult-script skills\consult-semantic-okf-adaptive\scripts\query_semantic_okf_adaptive.py `
  --top-k 10 --output-json RAW_COMPARISON.json --output-markdown RAW_COMPARISON.md
```

This adaptive run is direct top-10 only. The entity-graph evaluation retains the separate pool-100
embedding sensitivity experiment; it must not be confused with the direct table.

## Paired answer evaluation

`skill-arena/adaptive-hard10.yaml` defines an isolated two-profile comparison:

- `knowledge-only-control`: the pinned adaptive bundle with no declared skill;
- `adaptive-consult-treatment`: the same bundle plus exactly
  `consult-semantic-okf-adaptive`.

The model, question, workspace, timeout, concurrency, and network restrictions are otherwise identical.
This estimates the effect of adding the consult instructions; an all-skills portfolio is not used as
causal evidence.

```powershell
$ValidateDesign = Join-Path $HOME '.agents/skills/skill-arena-config-author/scripts/validate-evaluation-design.js'
node $ValidateDesign `
  evaluations\semantic-okf-adaptive\skill-arena\adaptive-hard10.yaml `
  --coverage evaluations\semantic-okf-adaptive\skill-arena\prompt-coverage.json

skill-arena val-conf evaluations\semantic-okf-adaptive\skill-arena\adaptive-hard10.yaml
skill-arena evaluate evaluations\semantic-okf-adaptive\skill-arena\adaptive-hard10.yaml --dry-run
skill-arena evaluate evaluations\semantic-okf-adaptive\skill-arena\adaptive-hard10.yaml
```

The accepted final run is
`results/semantic-okf-adaptive-hard10-paired/2026-07-14T17-50-14-025Z-compare`, evaluation ID
`eval-Iue-2026-07-14T17:50:18`. All 20 requested cells completed with zero transport errors. The
strict all-contract pass rate is 0%, so the result is interpreted through independently scored
components rather than as “all answers were wrong.”

The adaptive knowledge-only control achieved 97.50% correctness, 90.25% completeness, 93.23%
evidence validity, and 93.32% grounding. The adaptive consult treatment achieved 93.58%, 57.25%,
59.33%, and 60.00%, respectively. Adding the skill therefore had negative paired effects on this
fixed benchmark, despite the bundle's strong control and the retriever's leading observed recall.
Four treatment answers still used full source-locator strings where the output required integer PDF
pages, and several omitted required answer facets. The current design should use a deterministic
post-retrieval evidence serializer instead of relying on answer-model instruction following.

The first run is retained as a superseded diagnostic in `skill-arena/diagnostic-run-summary.json`.
Its output-contract failure prompted an instruction repair, but the same ten questions were reused;
the accepted run is a regression observation, not an untouched generalization or a causal estimate of
the repair. `grounded-answer-summary.md` compares 100 answers across all five alternatives, and
`skill-arena/final-run-summary.json` binds the accepted raw run, blinded reviews, skill hashes, and
compact reports. Raw outputs stay append-only and ignored; compact summaries are checked in.

## Interpretation and limitations

Read `EVALUATION-CONCLUSIONS.md` before choosing a package. The highest observed retrieval score is not
automatically the best end-to-end answer system. In particular, the adaptive improvement over
classical fusion is small, occurs on one of forty questions, ties on the hard ten, and costs about
three times the in-process query latency. Its isolated consult treatment also reduced completeness and
grounding relative to the same-bundle control. Classical fusion remains the simpler broad retrieval
default, embedding consultation has the strongest observed answer-level treatment effect, and a new
untouched benchmark is required before claiming broad adaptive superiority.

The tokenizer is English-oriented and ASCII-alphanumeric. Timing is diagnostic rather than a portable
hardware benchmark. The hard ten were used as a no-regression cohort and later as the paired answer
set, so they are not a fresh statistical holdout.

## Legacy `rg` and `grep` note

The separate investigation remains at
`evaluations/semantic-okf-classical/legacy-grep-investigation.md`. The legacy consultant instructions
recommend `rg` for one exact-text workflow; the frozen `legacy_lexical` evaluator is an in-memory
TF-IDF-like ranker and executes neither `rg` nor `grep`. The legacy baseline was not changed.
