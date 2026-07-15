# Definitive Ensemble Answer-Output Evaluation

This pipeline evaluates actual answers from a tool-capable, three-arm Skill Arena run without
changing older evaluations. It separates mechanically verifiable properties from blinded semantic
judgment and binds every evidence check to the exact read-only `20260715-ensemble-final-03` bundle.
Raw runs, preparations, and reviewer attempts are append-only and ignored; only compact validated
reports are eligible for publication.

## Frozen inputs

The checked contract is `answer-output-evaluation-contract.json`. It requires:

- benchmark `semantic-okf-ensemble-hard10-three-arm`;
- profiles `knowledge-only-control`, `adaptive-consult-control`, and
  `ensemble-consult-treatment`;
- variant `codex-luna-tools`;
- questions `q031` through `q040` with their complete frozen IDs;
- three responses per profile-question cell, for exactly 90 Promptfoo rows;
- final-03 bundle tree SHA-256
  `ed9386b63e4e087eea0fe62cd53eeb22e8f9cc4d5973b45eae7d736d9b77f868`;
- ensemble index SHA-256
  `9ce8bac88df8621fd870d718d1166e706516f4c4d56497eecc080d454453e939`;
- canonical ensemble plan SHA-256
  `cbbc28d140667670621260513d08998a740227f2bdf93f4dce754f4c996dd8eb`;
- authoritative 874-record ledger SHA-256
  `df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc`;
- reviewed answer benchmark `semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1`
  at manifest SHA-256
  `257997cc2da3d9afae596ac8b46551a1b1fa73480f15861a25f262bb85a91f62`;
- reviewed hard-ground-truth SHA-256
  `c656fc575b0c7e06cd386093d975cd74ef9c9aead743312e3aadec1cbdc08451`.

The reviewed benchmark preserves all parent question bytes, qrels, statements, required papers and
sources, derivations, variants, important negatives, and evidence options. It appends only reviewed
claim IDs that independently support a complete existing OR group. The resulting 44 atomic groups
and 13 important-negative groups contain 113 option links, 68 unique reviewed claim IDs, and 71
authoritative evidence objects. Thirty-eight close but insufficient alternatives are explicitly
rejected. This versions acceptable evidence without changing the semantic answer key.

Preparation runs the standalone ensemble bundle validator, hashes all 904 bundle files, validates
the authoritative ledger, and checks every ground-truth claim identity before reading answers.

## Tool-capable generation runtime

The generation variant uses the Codex command adapter with `gpt-5.6-luna`, an ephemeral
`workspace-write` sandbox, approval policy `never`, web search disabled, and network access
disabled. The workspace permission belongs to the isolated agent adapter; consultation itself is
available only through the profile-gated MCP server version 1.5.0, whose tools are annotated
read-only, non-destructive, and closed-world. Inspect, coverage, and preparation are idempotent;
bootstrap and confirmation are deliberately non-idempotent. The published bundle remains read-only by contract,
and the independent mechanical scorer accepts evidence only when it matches the frozen repository
bundle.

The host must expose the exact offline embedding runtime through two declared passthrough
variables: `SEMANTIC_OKF_PYTHON` and `SEMANTIC_OKF_HF_HUB_CACHE`. The checked config manifest binds Python 3.12.13,
`sentence-transformers` 5.6.0, `huggingface-hub` 1.23.0, and the executable and build-lock hashes.
Use the repository environment and validate the config before every live run:

```powershell
$env:SEMANTIC_OKF_PYTHON = (Resolve-Path '.venv/Scripts/python.exe').Path
$env:SEMANTIC_OKF_HF_HUB_CACHE = (& $env:SEMANTIC_OKF_PYTHON -c `
  "from huggingface_hub.constants import HF_HUB_CACHE; print(HF_HUB_CACHE)").Trim()

& $env:SEMANTIC_OKF_PYTHON -c `
  "import platform, sentence_transformers, huggingface_hub; print(platform.python_version(), sentence_transformers.__version__, huggingface_hub.__version__)"

skill-arena val-conf evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml
skill-arena evaluate evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml --dry-run
```

The same MCP server configuration is present in all three isolated profiles, but it exposes tools
only when `SKILL_ARENA_ALLOWED_SKILLS` identifies exactly `consult-semantic-okf-ensemble`. The
knowledge-only and adaptive controls therefore receive an empty tool list. The ensemble treatment
receives exactly `semantic_okf_inspect`, `semantic_okf_coverage_brief`,
`semantic_okf_prepare_answer`, and `semantic_okf_confirm_answer`, preceded by the no-argument
`semantic_okf_bootstrap_skill`. Their closed input schemas accept
no bundle path, model-cache path, command, or URL. Preparation has no `mode` argument and returns
the canonical closed `semantic-okf-prepared-answer/1.0` envelope with exactly `schema`,
`candidate_json`, `response_sha256`, and `byte_count`. Confirmation accepts only the required
`response_sha256` string and constrains it to 64 lowercase hexadecimal characters. The server
resolves the bundle and offline
runtime only from its bound environment, requires absolute `SEMANTIC_OKF_PYTHON` and
`SEMANTIC_OKF_HF_HUB_CACHE` values, maps only the latter to `HF_HUB_CACHE`, and fails closed on a
missing or mismatched provider.

Bootstrap must be the first Semantic OKF call and may succeed exactly once. It resolves only the
installed `consult-semantic-okf-ensemble/SKILL.md` below the isolated `CODEX_HOME`, rejects links or
path escape, verifies the frozen raw-byte SHA-256 and byte count, and returns the exact strict-UTF-8
body through the closed `semantic-okf-skill-bootstrap/1.0` envelope. Every later tool is gated on
that success. The shared host wrapper disables Codex's general shell tool only for the exact
ensemble treatment identity; both controls retain the baseline command behavior.

For a non-null contracted answer, the treatment must first call `semantic_okf_bootstrap_skill`,
follow the returned frozen body, call `semantic_okf_inspect`, read every
`semantic_okf_coverage_brief` page for identical query parameters, and draft only from those
reviewed bindings. `semantic_okf_prepare_answer` independently recomputes the full pack, stores the
exact canonical JSON candidate, and returns its strict envelope. The treatment reviews the exact
`candidate_json` string inside that envelope without reserializing it, then sends only the short
`response_sha256` to `semantic_okf_confirm_answer`; it never copies the candidate or envelope into
the confirm call. The server verifies the outstanding digest, consumes that candidate, and returns
a closed receipt binding its hash and UTF-8 byte count. Confirmation is non-idempotent, must succeed
exactly once, and must be the terminal tool call. A failed prepare or failed confirm publishes
nothing and abandons that transaction. Recovery requires a fresh successful prepare and its new
digest before another confirm; no envelope from the abandoned transaction remains eligible.

Confirmation is not the publication boundary. The Skill Arena treatment invokes Codex through the
packaged confirmed-output host wrapper. It parses every strict prepared-answer envelope; verifies
the closed schema and exact keys, candidate canonicality, UTF-8 digest, and byte count; validates one
or more successful prepare calls followed by exactly one successful terminal digest confirmation
in the final clean transaction; checks that the receipt binds the same candidate; then atomically
writes the exact `candidate_json` bytes to the single absolute output-last-message path. A failed
protocol call clears the transaction for publication; only a fresh successful prepare may begin its
replacement. Any earlier successful confirm, confirm without a fresh prepare after failure, stale
or mismatched digest, repeated confirm, non-canonical candidate, any tool call after successful
confirmation, or another envelope, receipt, length, hash, or ordering mismatch fails closed instead
of publishing the agent's later free-form message. Control outputs pass through unchanged. The
accepted trace attestation must independently prove that every published treatment output equals
the candidate bound by its final confirmed envelope and receipt.

Accordingly, the causal estimand is the full definitive consultation capability—skill instructions,
digest-bound bootstrap, profile-gated MCP workflow, treatment runtime policy, and confirmed-output
host publication—not the effect of skill text in isolation.

The accepted evidence-coverage preflight is bound by
`hard10-coverage-pack-multisignal-diversified-publication-gate-final.json` at SHA-256
`f96ab9356a99ca5b3798e4de6912e0a6b5fc010c3abb5711360b85257374deec` and its English companion at
SHA-256 `25720899f87efedf4f9c901d91df19dbe97d2ffba53fec7c61e8dff0576ad0a1`.
It covers 44/44 reviewed atomic groups, 13/13 important-negative groups, all required papers, and
713/713 independently valid bindings. The paper-conditioned semantic reranker retains the existing
per-facet and global caps and receives no question ID or evaluator label. This report establishes
candidate availability and exact evidence identity; it does not supply any accepted generated-answer
metric.

After preflight, start a fresh live comparison. Do not reuse a smoke or diagnostic directory:

```powershell
$env:SEMANTIC_OKF_PYTHON = (Resolve-Path '.venv/Scripts/python.exe').Path
$env:SEMANTIC_OKF_HF_HUB_CACHE = (& $env:SEMANTIC_OKF_PYTHON -c `
  "from huggingface_hub.constants import HF_HUB_CACHE; print(HF_HUB_CACHE)").Trim()
skill-arena evaluate evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml
```

## Required live result

Use `promptfoo-results.json` only from a newly completed `codex-luna-tools` live run. The file must
contain the complete profile × question × repetition product. Every row must have consistent
benchmark, profile, question, variant, scenario, provider, and row identities; a unique Promptfoo
row ID; no adapter or runtime error; and a nonempty model output.

An answer that is invalid JSON remains a real answer outcome and receives a zero response-contract
score. A row with no model output is not an answer outcome: preparation rejects the entire run. This
prevents a terminal adapter failure or partial run from being reported as model quality. The pinned
Codex adapter maps a nonzero CLI exit to `response.error`; it may also preserve recoverable
tool-router diagnostics in `response.metadata.stderr` after a successful turn. Preparation accepts
those diagnostics only with a null adapter error and a nonempty output, so failed search attempts
remain observable answer behavior instead of being mistaken for a transport failure.

After preparation, blinded review, and compact aggregation, run the independent MCP/runtime attestor
over the same complete Promptfoo result, the bound schema-1.2 answer report, and raw traces. The
attestor deliberately runs last because it rejects an answer report that is missing or does not bind
the same 90 outputs. Controls must publish their raw final messages unchanged. Every treatment must have
exactly one successful first `semantic_okf_bootstrap_skill` call whose envelope matches the frozen
skill bytes, zero command-execution events, one successful inspect, every required coverage page,
and one or more successful `semantic_okf_prepare_answer` calls with no `mode`, each returning a strict
`semantic-okf-prepared-answer/1.0` envelope, followed by exactly one successful
`semantic_okf_confirm_answer` call containing only that final envelope's `response_sha256` as the
terminal tool call, and a host-published output byte-identical to that envelope's canonical
`candidate_json`. If an earlier protocol call failed, the accepted suffix must start with a fresh
successful prepare; the failed transaction publishes nothing. A missing trace, stale receipt,
earlier successful confirm, confirm without a fresh prepare after failure, stale or mismatched
digest, changed or non-canonical final candidate, repeated confirm, extra prepare or any other tool
after successful confirmation, envelope, length, or hash mismatch, or host mutation rejects the
complete run.

## Prepare, review, aggregate, and attest

Choose a new append-only preparation directory under the ignored results tree. Replace every
uppercase placeholder below with a new identifier. Never point the accepted workflow at `live-01`,
`live-02`, or any smoke directory.

```powershell
$live = "results/semantic-okf-ensemble-hard10-three-arm/NEW_COMPLETED_COMPARE_RUN/promptfoo-results.json"
$prepared = "evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/answer-output/NEW_LIVE_DIRECTORY"

python evaluations/semantic-okf-ensemble/scripts/prepare_answer_output_evaluation.py `
  --promptfoo-results $live `
  --output-dir $prepared
```

Preparation writes three raw, ignored artifacts:

- `review-tasks.jsonl`: deterministically ordered blinded review tasks;
- `review-manifest.json`: private profile/question/repetition mapping and input hashes;
- `mechanical-results.json`: per-answer mechanical scores without candidate answer text.

Run the fixed blinded reviewer in batches of three. The reviewer receives no profile, skill, or
repetition label and has tools, extensions, skills, prompt templates, context files, and session
reuse disabled.

```powershell
$PiCommand = (Get-Command pi.ps1 -ErrorAction Stop).Source
python evaluations/semantic-okf-ensemble/scripts/run_blinded_answer_reviews.py `
  --input-dir $prepared `
  --pi-command $PiCommand `
  --batch-size 3 --max-concurrency 2 `
  --batch-dir-name NEW_REVIEW_BATCH_DIRECTORY `
  --timeout-seconds 600 --max-attempts 3
```

The fixed reviewer is `openai-codex/gpt-5.6-luna`. PI is used only as the deliberately tool-disabled
review transport; it is not the generation variant. Batch prompts, attempts, standard output,
standard error, and `reviews.json` remain in the ignored preparation directory. On Windows, use the
PowerShell shim as shown; the extensionless npm shim is a POSIX shell script. The resolver also
prefers `.ps1`, `.cmd`, and `.exe` shims before an extensionless file. On POSIX, pass the resolved
`pi` executable instead. A failed reviewer attempt leaves its append-only batch directory intact;
retry the complete review with another new `--batch-dir-name`.

After all 90 reviews pass their closed schema, create new compact checked reports. Use fresh names
until the reports have passed repository validation; the release workflow may then bind the chosen
files as the final accepted summaries.

```powershell
python evaluations/semantic-okf-ensemble/scripts/aggregate_answer_output_evaluation.py `
  --input-dir $prepared `
  --output-json evaluations/semantic-okf-ensemble/NEW_COMPACT_SUMMARY.json `
  --output-markdown evaluations/semantic-okf-ensemble/NEW_COMPACT_SUMMARY.md
```

Only after aggregation succeeds, attest the complete runtime against that exact compact answer
report. The accepted run's original hook paths were beneath ephemeral Skill Arena workspaces and no
longer exist. Skill Arena copied each profile workspace, including its execution-event traces, into
the append-only ignored run tree. The explicit archive fallback below preserves each hook's exact
`.skill-arena/hooks/execution-events/...` relative identity and independently checks the retained
file hash, event count, and tool-event count against the Promptfoo row; it is not a filename-only
substitution.

```powershell
$live = "results/semantic-okf-ensemble-hard10-three-arm/2026-07-15T15-24-19-159Z-compare/promptfoo-results.json"
$answerReport = "evaluations/semantic-okf-ensemble/answer-output-comparison-final.json"
$knowledgeArchive = "results/semantic-okf-ensemble-hard10-three-arm/2026-07-15T15-24-19-165Z-4e2a14bd-6e27-47e8-a732-0471e27bf44e-codex-luna-tools-knowledge-only-control/workspace"
$adaptiveArchive = "results/semantic-okf-ensemble-hard10-three-arm/2026-07-15T15-24-19-166Z-ab783bc5-c47f-4d1b-a190-ec5ed5a00ddc-codex-luna-tools-adaptive-consult-control/workspace"
$ensembleArchive = "results/semantic-okf-ensemble-hard10-three-arm/2026-07-15T15-24-21-144Z-d142f872-8e8a-4e73-b87f-701962e3b391-codex-luna-tools-ensemble-consult-treatment/workspace"

python evaluations/semantic-okf-ensemble/scripts/attest_skill_arena_mcp_runtime.py `
  --input $live `
  --contract evaluations/semantic-okf-ensemble/answer-output-evaluation-contract.json `
  --config evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml `
  --config-manifest evaluations/semantic-okf-ensemble/skill-arena/config-manifest.json `
  --answer-report $answerReport `
  --publication-gate-script skills/consult-semantic-okf-ensemble/publication-runtime/confirmed_output_gate.py `
  --publication-gate-launcher skills/consult-semantic-okf-ensemble/publication-runtime/run_codex.cmd `
  --treatment-skill skills/consult-semantic-okf-ensemble/SKILL.md `
  --archived-workspace "knowledge-only-control=$knowledgeArchive" `
  --archived-workspace "adaptive-consult-control=$adaptiveArchive" `
  --archived-workspace "ensemble-consult-treatment=$ensembleArchive" `
  --output-json evaluations/semantic-okf-ensemble/skill-arena-mcp-runtime-attestation-final.json `
  --output-markdown evaluations/semantic-okf-ensemble/skill-arena-mcp-runtime-attestation-final.md
```

The adaptive-control q040 repetition at Promptfoo test index 28 contains one diagnostic
`command_execution` start for `rg --files knowledge` that has no matching completion because the
agent superseded it with a later, identical command that completed. The attestor preserves and
classifies this single control-side start rather than inventing a completion. It does not relax the
treatment contract: all 30 treatment traces contain zero shell or command calls and retain the exact
bootstrap, inspect, complete coverage paging, prepare, terminal digest-confirm, and byte-exact host
publication protocol.

Preparation, review, aggregation, and attestation refuse to overwrite their outputs. Do not check in
the raw preparation or archived workspace directories; check in compact JSON and English Markdown
only after a real 90-answer run, all real reviews, and the independent attestation complete.

## Diagnostic chronology and exclusion rules

The earlier artifacts remain useful diagnostics but are not accepted evidence for the final
`codex-luna-tools` comparison:

1. `2026-07-15T06-17-44-349Z-compare` completed 90 generations through the earlier
   `pi-luna-only` route. Its treatment outputs exposed hand-authored or post-edited evidence: 98 of
   203 locator entries violated the authoritative binding, and only 2 of 30 treatment answers bore
   an exact deterministic-constructor signature. It is retained to explain the mandatory answer
   construction gate, not as the definitive answer result.
2. The first blinded-review attempt used batches of five and left three failed batches. A separate
   batch-size-three replay under `live-02` proved the review pipeline could complete, but it still
   reviewed the superseded PI generation and therefore remains diagnostic.
3. `2026-07-15T07-58-56-975Z-compare` tested the hardened treatment instructions through PI. The PI
   generation backend exposed no file tools, so all ten treatment outputs abstained. Those nulls
   measure a runtime-capability mismatch, not retrieval or answer quality.
4. The first Codex smoke established that file tools were available, but a read-only sandbox blocked
   the Python query process. The next smoke enabled `workspace-write`; it was stopped because the
   default host Python did not match the pinned sentence-transformers runtime.
5. A subsequent launcher preflight showed that Skill Arena also isolates the default Hugging Face
   cache. `SEMANTIC_OKF_PYTHON`, `SEMANTIC_OKF_HF_HUB_CACHE`, and `run_query.ps1` closed those two
   diagnostic runtime gaps, but that shell-launcher route was not accepted and was superseded rather
   than repaired in place.
6. The profile-gated read-only MCP prototype completed inspect, all five q031 coverage pages, and
   its then-single `semantic_okf_finalize_answer` call with the then-current 198-claim union, while
   both controls exposed zero tools. This established bounded transport for that historical runtime,
   not the accepted split-tool or host-publication contract.
7. `2026-07-15T09-58-38-815Z-compare` was intentionally stopped after 46/90 rows. All 15 completed
   treatments called the historical single-tool constructor, but only 5/15 visible outputs were
   byte-identical to it and q031 was 0/3. The checked
   `finalizer-copy-integrity-diagnostic-20260715` report records why an instruction to copy verbatim
   is insufficient; it does not describe the accepted split tools.
8. `2026-07-15T11-08-27-398Z-compare` was intentionally stopped after 38/90 rows. All three examined
   q031 treatments had valid prepared candidates and confirmation receipts, but the plain host
   command published a different free-form message in 3/3 cases and changed six evidence fields.
   The checked `host-publication-mutation-diagnostic-20260715` report records why server confirmation
   is insufficient without the host wrapper.
9. Historical MCP v1.3.1 separated preparation from confirmation and added the hash-bound host
   wrapper, but confirmation still required the model to copy the complete `candidate_json` string.
   Its q031 preflight established the recoverable transaction shape over the current 206-claim,
   five-page diversified union; it did not establish that long-copy confirmation was reliable.
10. The checked [long-candidate confirmation diagnostic](long-candidate-confirmation-diagnostic-20260715.md) records the
    frozen full-run attempt `2026-07-15T13-50-35-550Z-compare`
    (`eval-d9Z-2026-07-15T13:50:43`) exercised that historical v1.3.1 protocol. Its first treatment
    prepared successfully, failed to copy the long candidate into confirmation, and did not recover.
    The runner stopped at that first treatment protocol failure. The attempt is rejected and supplies
    no benchmark row or answer-quality metric.
11. MCP v1.4.0 kept the four profile-gated tools but made preparation return the
    closed `semantic-okf-prepared-answer/1.0` envelope and confirmation accept only its 64-character
    lowercase `response_sha256`. The host verifies envelope keys, candidate canonicality, digest,
    UTF-8 byte count, terminal receipt binding, and transaction order before atomically publishing
    the exact `candidate_json` bytes. A failed prepare or confirm clears the transaction; recovery
    requires a fresh envelope and its new digest. Earlier successful confirms, stale or mismatched
    digests, confirmation without a fresh prepare, repeated confirmation, or anything after a
    successful confirmation are rejected. Its q031 digest-publication smoke passed the technical
    transport contract, but supplied no causal answer-quality metric.
12. The checked [skill-bootstrap isolation diagnostic](skill-bootstrap-isolation-diagnostic-20260715.md)
    records the partial v1.4.0 comparison `2026-07-15T14-29-07-959Z-compare`
    (`eval-T27-2026-07-15T14:29:15`). One treatment used the ordinary shell to read the exact mounted
    skill body before the governed MCP sequence. That is Skill Arena's normal activation mechanism,
    but it violated the frozen zero-command treatment gate. All 17 persisted rows were rejected.
    MCP v1.5.0 replaces that read with a pathless, one-shot, digest-bound bootstrap tool and disables
    the general shell for the treatment. The accepted complete 90-answer v1.5.0 run below uses that
    replacement contract and is kept separate from all 17 rejected rows.

Do not merge rows across these attempts, fill missing cells, reuse their evaluation IDs, or report a
smoke as an accepted result. The accepted metrics below come only from the fresh complete v1.5.0
comparison and its independently reviewed compact report.

## Metric separation

Mechanical metrics are recomputed from the answer rather than copied from Promptfoo:

- response-contract compliance;
- exact evidence validity against reviewed ledger records, concept files, sources, papers, and cited
  PDF pages;
- grounding of every supporting claim reference in independently valid evidence;
- exact atomic claim identity coverage;
- required paper and source coverage;
- exact important-negative identity coverage.

Blinded model-judged metrics are:

- claim correctness against the supplied authoritative support-record interpretations;
- semantic completeness against every atomic ground-truth claim;
- important-negative coverage.

The schema-1.2 compact report contains overall metrics for each profile, population standard
deviations, worst-question scores, all 30 profile-question means, strict full-pass deltas, and two
matched question-level contrasts: ensemble treatment minus knowledge-only control and ensemble
treatment minus adaptive active control. It binds the exact Skill Arena config and manifest,
consult-skill trees, source manifest, contract, mechanical evaluator, preparer, blinded reviewer,
and aggregator by SHA-256. It does not contain answer text, reviewer notes, or machine-specific
paths.

Retrieval quality and answer quality remain distinct. A high retrieval score cannot establish that a
generated synthesis is correct, complete, grounded, or contract-compliant. Exact-ID coverage shows
identity availability, not semantic entailment. Semantic scores are explicitly model-judged even
though profile identities are blinded. Because GPT-5.6 Luna reviews GPT-5.6 Luna generations, the
review is profile-blinded but not model-family independent. Matched deltas summarize the ten frozen
questions and three repetitions; they are not evidence of universal superiority or an untouched
holdout.

## Accepted live result

Status: **accepted complete live comparison**.

Skill Arena compare run `2026-07-15T15-24-19-159Z-compare`, Promptfoo evaluation
`eval-RTd-2026-07-15T15:24:26`, completed the exact 90/90 profile × question × repetition product
without provider-response errors. Preparation `live-published-confirmed-01` produced 90 mechanical
records and blinded tasks; review batch `review-batches-001` produced 90 closed-schema reviews with
the fixed `openai-codex/gpt-5.6-luna` reviewer.

The accepted compact reports are
`answer-output-comparison-final.json` at SHA-256
`6f48c963e8c1f85f9c1355a2d1d796ff8821239c05fb19ad72f78488a6acd5ae` and
`answer-output-comparison-final.md` at SHA-256
`2e37ec6602839d89ee27e1eb6fe6b8a8f1a8b3da24dbd5576ecaef08dad10178`.
The independently rendered runtime reports are
`skill-arena-mcp-runtime-attestation-final.json` and
`skill-arena-mcp-runtime-attestation-final.md`; the compact JSON attestation has SHA-256
`8085e666cced0d8b6d5a0b32095c29d836756bf67d1a515412c3ce7d9df5d77d`.

| Profile | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `knowledge-only-control` | 0.0% | 13.3% | 5.6% | 5.4% | 90.6% | 75.1% | 3.7% | 75.3% | 39.8% | 94.2% | 5.0% |
| `adaptive-consult-control` | 3.3% | 23.3% | 82.6% | 82.5% | 83.0% | 72.7% | 55.3% | 76.0% | 74.8% | 86.7% | 78.3% |
| `ensemble-consult-treatment` | 53.3% | 100.0% | 100.0% | 100.0% | 96.7% | 91.1% | 86.0% | 98.5% | 98.5% | 99.2% | 100.0% |

Positive matched deltas favor the ensemble treatment. Each value is the mean of ten matched
question-level differences after averaging the three repetitions within a question.

| Contrast | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ensemble_vs_knowledge_only` | +53.3% | +86.7% | +94.4% | +94.6% | +6.2% | +16.0% | +82.3% | +23.2% | +58.8% | +5.0% | +95.0% |
| `ensemble_vs_adaptive` | +50.0% | +76.7% | +17.4% | +17.5% | +13.7% | +18.4% | +30.7% | +22.5% | +23.8% | +12.5% | +21.7% |

These answer metrics do not replace the separate retrieval benchmark. They establish strong quality
on the frozen ten-question answer task under the declared model-judged and mechanical contracts;
they do not prove universal superiority or performance on an untouched external holdout.

## Validation

```powershell
python -m compileall -q evaluations/semantic-okf-ensemble/scripts
python evaluations/semantic-okf-ensemble/scripts/generate_reviewed_answer_benchmark.py --check
python evaluations/semantic-okf-ensemble/scripts/generate_skill_arena_config.py --check
python evaluations/semantic-okf-ensemble/scripts/validate_scaffold.py
$tests = (Get-ChildItem tests/test_semantic_okf_ensemble_*.py | Sort-Object Name).FullName
python -m pytest -q $tests
python scripts/check_coverage.py --threshold 80
```

The full ensemble suite covers the exact 90-row Cartesian product, valid authoritative evidence,
blinded task contents, partial runs, duplicate rows, missing adapter output, recoverable tool
diagnostics, malformed execution metadata, review identity coverage, closed compact schemas, causal
contrasts, archived-trace fallback, bootstrap and shell-isolation gates, publication transactions,
reviewed benchmark regeneration, retrieval coverage, skill packaging, and omission of raw
answer/reviewer text.
