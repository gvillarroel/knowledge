# Endocrine-Hygiene Semantic OKF Evaluation

This evaluation measures how the existing Semantic OKF builder/consult alternatives
transfer to a new PubMed Central corpus about hygiene and personal-care products and
endocrine disruption. The accepted run uses Know for acquisition, honest PMCID
identity, a frozen evidence-first benchmark, and unchanged skill packages. The
deterministic direct builds and consultations run locally and offline after the
accepted corpus and pinned embedding model are present. The separate Skill Arena
diagnostic uses a remote PI model with network access. Neither path uses MCP.

## Frozen contract

| Item | Contract |
| --- | --- |
| Papers | 15 NCBI PubMed Central BioC full-text records |
| BioC passages | 2,010 passages; 604,905 passage-text characters |
| Reviewed claims | 93 claims in 15 JSONL files |
| Semantic OKF sources | 30 authoritative paper/claim sources plus 1 auxiliary vocabulary |
| Questions | 30: 15 direct, 10 cross-paper, and 5 hard |
| Hard ground truth | 5 records; 27 atomic answers; 15 important negatives |
| Hard evidence | 60 question-specific bindings across 34 distinct passages |
| Exact hard claims | 128 requirement occurrences across 37 distinct reviewed claim IDs |
| Paper identity | Canonical uppercase PMCID, for example `PMC6504186` |
| Manifest source identity | Lowercase, for example `paper-pmc6504186` and `claims-pmc6504186` |
| Passage locator | One-based `BioC-passage-NNNN`; never represented as a PDF page |
| Accepted build run | `20260715-endocrine-builds-05` |
| Authoritative core SHA-256 | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| Semantic records SHA-256 | `5bb09f5b4a7eb86c9f9e69c2e78c77d04a9530c5b305f3725c7ec3ef859913f5` |

The hard-question prompts do not contain PMCIDs, source IDs, paths, locators, hashes,
or complete answer claims. Qrels and ground truth are evaluator-only.

## Authority and artifact layout

Normalized BioC passage text and reviewed claim rows are authoritative evidence.
The Semantic OKF core is their validated authoritative projection. Every retrieval
index, vocabulary statistic, ranking, qrel, aggregate, and extractive answer pack is
derived and non-authoritative.

- `corpus/acquisition-selection.json` records why each paper was included and its
  interpretation caution.
- `corpus/acquisition-manifest.json` binds every Know response, raw BioC digest,
  normalized paper, passage count, and reviewed-claim count.
- `corpus/input-inventory.json` freezes the 30 authoritative inputs and one auxiliary
  vocabulary.
- `corpus/manifest.json` is the closed Semantic OKF build manifest.
- `corpus/source-combination.json` maps lower-case source IDs to real uppercase
  PMCIDs for evaluator-side paper deduplication.
- `benchmark/` contains the frozen question battery, evaluator-only hard ground
  truth, exact reviewed-claim requirements, and their hashes.
- `plans/` contains one closed input plan per builder family.
- `reports/` contains compact checked-in build, retrieval, determinism, and hard-answer
  results.
- `results/runs/` contains ignored append-only bundles, commands, logs, and detailed
  per-query results.

Large Know state, its export archive, generated bundles, and detailed run files stay
ignored and append-only. They are bound by checked-in hashes rather than committed.

## Lossless Know acquisition

The selected sources are the NCBI BioC JSON endpoints listed in
`corpus/acquisition-selection.json`. The Know site adapter must preserve an
`application/json` or `+json` response as UTF-8 JSON text; it must not pass the body
through HTML extraction. It validates JSON and records the raw byte count and
SHA-256 before writing the page.

The accepted ignored export is:

| Field | Value |
| --- | --- |
| Know key | `endocrine-hygiene-bioc-2026-07` |
| Store-relative archive | `exports/knowledge-export-20260715T220149Z.zip` |
| Bytes | `1952464` |
| SHA-256 | `73ae75e7cf024bb338ab1c7580e4766c0eb05b12ccd33a8e564f917da35d575f` |

Use the current worktree implementation explicitly so another editable installation
cannot shadow it:

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
$store = "tmp/endocrine-hygiene-know"
$key = "endocrine-hygiene-bioc-2026-07"

python -m knowledge.cli --store $store add key $key
$selection = Get-Content evaluations/semantic-okf-endocrine-hygiene/corpus/acquisition-selection.json -Raw | ConvertFrom-Json
foreach ($paper in $selection.papers) {
  $sourceId = $paper.pmcid.ToLowerInvariant()
  $url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/$($paper.pmcid)/unicode"
  python -m knowledge.cli --store $store add site $url --key $key --source-id $sourceId --max-depth 0 --max-pages 1
}
python -m knowledge.cli --store $store --json list sources --key $key
python -m knowledge.cli --store $store --verbose --json sync --key $key
python -m knowledge.cli --store $store --verbose --json export --key $key
```

If the key and sources already exist, do not recreate them; inspect and synchronize
the existing isolated key. Re-downloading a BioC endpoint does not silently replace
the accepted corpus. The new response must satisfy every raw hash in the acquisition
manifest, or the corpus requires a new version and manifest.

Verify the accepted archive before normalization:

```powershell
Get-Item tmp/endocrine-hygiene-know/exports/knowledge-export-20260715T220149Z.zip
Get-FileHash tmp/endocrine-hygiene-know/exports/knowledge-export-20260715T220149Z.zip -Algorithm SHA256
```

## Generate and validate the checked corpus

The generator consumes the lossless Know store and the manually reviewed,
hash-bound `corpus/claims-seed.json`. It writes normalized paper Markdown, reviewed
claim JSONL, vocabulary, manifests, acquisition bindings, and source identity maps.

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
python evaluations/semantic-okf-endocrine-hygiene/scripts/prepare_corpus.py --know-store tmp/endocrine-hygiene-know
python evaluations/semantic-okf-endocrine-hygiene/scripts/prepare_corpus.py --know-store tmp/endocrine-hygiene-know --check
python evaluations/semantic-okf-endocrine-hygiene/scripts/validate_ground_truth.py --json
```

The `--check` invocation is the non-writing CI/review gate. It rejects a stale,
missing, extra, or hash-mismatched generated artifact. Publication is staged and
atomically replaces the complete generated set only after every file is valid. The
ground-truth validator checks closed schemas, question counts and subset
relationships, direct-paper coverage, identity and answer leakage, qrels, every
evidence locator, and every passage-text hash.

The validator also joins each exact claim requirement to its declared ground-truth
evidence through `(paper_id, evidence_text_sha256)`. This evidence-digest join checks
128 requirement occurrences across 37 distinct reviewed claim IDs and confirms that
all 60 evidence bindings have reviewed-claim projections. Exact claim identity is
kept because several independently reviewed interpretations can share one passage.

## Reproduce builds and retrieval without replacing accepted raw runs

Use the repository virtual environment because the embedding plan is pinned to an
offline local model revision. The runner forces offline model settings and builds
all six unchanged families twice. Choose a new run ID: publication is append-only
and refuses an existing directory.

```powershell
$python = (Resolve-Path .venv/Scripts/python.exe).Path
$runId = "endocrine-repro-$((Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ'))"
$runDir = "evaluations/semantic-okf-endocrine-hygiene/results/runs/$runId"
$buildJson = "tmp/$runId-build.json"
$buildMarkdown = "tmp/$runId-build.md"
$retrievalJson = "tmp/$runId-retrieval.json"
$retrievalMarkdown = "tmp/$runId-retrieval.md"

& $python evaluations/semantic-okf-endocrine-hygiene/scripts/run_builds.py --preflight-only
& $python evaluations/semantic-okf-endocrine-hygiene/scripts/run_builds.py --run-id $runId --json-report $buildJson --markdown-report $buildMarkdown

& $python evaluations/semantic-okf-endocrine-hygiene/scripts/evaluate_retrieval.py --run-dir $runDir --build-report $buildJson --compact-json $retrievalJson --compact-markdown $retrievalMarkdown --raw-output "$runDir/retrieval/detailed-report.json" --python $python
& $python evaluations/semantic-okf-endocrine-hygiene/scripts/evaluate_retrieval.py --run-dir $runDir --build-report $buildJson --compact-json $retrievalJson --compact-markdown $retrievalMarkdown --raw-output "$runDir/retrieval/detailed-report-v2.json" --python $python

& $python evaluations/semantic-okf-endocrine-hygiene/scripts/verify_retrieval_determinism.py "$runDir/retrieval/detailed-report.json" "$runDir/retrieval/detailed-report-v2.json" --output "tmp/$runId-retrieval-determinism.json"

& $python evaluations/semantic-okf-endocrine-hygiene/scripts/compare_hard_answers.py --run-dir $runDir --retrieval-report "$runDir/retrieval/detailed-report.json" --output-json "tmp/$runId-hard-answers.json" --output-markdown "tmp/$runId-hard-answers.md"
```

Retrieval determinism compares routes, rankings, evidence bindings, errors, and
metrics after excluding timing and floating runtime scores. The accepted non-runtime
projection digest is
`5d210c8c5ee49fdb5943032bcab66b8723bee47dacbf1d75267367cbc68f5d1e`
for both detailed executions `v2` and `v3`.

Run `20260715-endocrine-builds-04` is retained as rejected append-only history. Its
second embeddings attempt encountered a missing Windows staging path, which failed
the run-level core-parity gate; no retrieval result from that run was accepted. Run
`20260715-endocrine-builds-05` rebuilt the same frozen inputs and passed both build
attempts for every compatible family.

The legacy package has no ranked natural-language search command. Its accepted
read-surface smoke is explicit:

```powershell
& $python skills/consult-semantic-okf/scripts/query_semantic_okf.py "$runDir/bundles/legacy-a" ledger --all --validate --format json
```

The `legacy_lexical` benchmark row is instead a documented evaluator-side,
in-memory TF-IDF-like ledger baseline. See `LEGACY-CONSULT-NOTE.md`.

## Accepted reports

- `reports/build-comparison.md` and `.json`: two builds, independent validation,
  deterministic trees, authoritative-core parity, and exact incompatibility
  diagnostics.
- `reports/retrieval-comparison.md` and `.json`: every route over the same 30
  questions, with paper/source metrics, timing, and exact evidence validation.
- `reports/retrieval-determinism.json`: equality of the non-runtime retrieval
  projection across two executions.
- `reports/hard-answer-comparison.md` and `.json`: actual deterministic extractive
  packs for all five hard questions and every compatible family.
- [`reports/skill-arena-hard5-diagnostic.md`](reports/skill-arena-hard5-diagnostic.md)
  and [`reports/skill-arena-hard5-diagnostic.json`](reports/skill-arena-hard5-diagnostic.json):
  the bound accepted live paired hard5 diagnostic, component gates, per-cell
  results, and actual Q030 answers.
- `EVALUATION-CONCLUSIONS.md`: plain-language metric definitions, comparison tables,
  interpretation, and limitations.

The hard-answer packs use no MCP and no language model. They select at most 12
reviewed claims from one route, diversify once by paper, and copy reviewed
interpretations with exact bindings. Their atomic and negative metrics require exact
reviewed claim IDs from `benchmark/hard-claim-requirements.json`; they test evidence
selection and reviewed-claim fidelity, not prose quality, free-form semantic
correctness, or complete reasoning.

## Skill Arena hard5 paired diagnostic

`skill-arena/classical-hard4.yaml` retains its historical filename but declares the
five-prompt benchmark ID `semantic-okf-endocrine-hygiene-classical-hard5-paired`.
The isolated comparison has two profiles:

- `knowledge-only-control`, which receives the same published snapshot without the
  consultation skill; and
- `classical-cli-consult-treatment`, which adds only the classical consultation
  skill surface.

The accepted live result is `eval-v8v-2026-07-15T23:49:40`. All `10/10` cells
completed with `0` runtime errors. The raw result was bound to the exact config,
both profiles, all five prompt IDs, the `pi-luna-only` variant and model, the compiled
Promptfoo config, and the immutable bundle before aggregation.

| Profile | Compound pass | Mean score | Mean latency |
| --- | ---: | ---: | ---: |
| `knowledge-only-control` | 0/5 | 0.657 | 72.6 s |
| `classical-cli-consult-treatment` | 0/5 | 0.543 | 117.6 s |

| Component gate | Control | Treatment |
| --- | ---: | ---: |
| Response format | 100% | 100% |
| Response contract | 100% | 80% |
| Evidence validity | 40% | 20% |
| Exact reviewed-claim fidelity | 100% | 100% |
| Atomic answer completeness | 20% | 0% |
| Important-negative coverage | 20% | 0% |
| Required-paper coverage | 80% | 80% |

Treatment minus control was `-0.114` mean score and `+45.0 s` mean latency. This
single accepted run provides no evidence that the classical consultation treatment
improved outcomes. Both profiles passed zero compound cells, and the strict evidence,
atomic-completeness, and negative-coverage gates remain the bottleneck despite exact
claim fidelity passing in every cell.

The configuration uses one request per cell and a remote PI model with network
access, so these values are descriptive only and are not part of the offline
direct-execution claim above. No MCP participated. See the
[compact accepted report](reports/skill-arena-hard5-diagnostic.md) for per-question
cells and the actual Q030 control/treatment answers.

## Repository validation

Run tests against this worktree rather than any other editable installation:

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
python -m pytest -q
python scripts/check_coverage.py --threshold 80
git diff --check
```

The detailed run is tied to its recorded commit and runtime. Timing differences on
a later machine do not invalidate deterministic rankings, but they must not be
presented as the accepted latency measurement.
