# Semantic OKF Definitive Ensemble Evaluation

> **Current operational boundary:** `consult-semantic-okf-ensemble` is now
> CLI-only. It requires no MCP server, MCP session, digest confirmation, or
> confirmed-output host wrapper. The MCP v1.5.0 material in this directory records
> the completed historical experiment at commit
> `3a5df66baf99c6c34ef6ff96d35aa44740b906c6`; its reports, hashes, and metrics are
> preserved and must not be attributed to the current CLI-only runtime. ADR 0027
> supersedes ADR 0026 for current operation while retaining ADRs 0023–0026 as
> historical design evidence.

Status: **complete for build, deterministic retrieval, population selection, reviewed answer-evidence coverage, and accepted answer-output evaluation**. The paper-diversified coverage union reaches 44/44 atomic groups, 13/13 important-negative groups, all required papers, and 713/713 valid bindings. The isolated v1.5.0 Skill Arena comparison completed 90/90 answers, 90 blinded reviews, compact aggregation, and an independent passing 90-trace attestation.

This directory evaluates the standalone `build-semantic-okf-ensemble` and `consult-semantic-okf-ensemble` skill pair. The pair combines adaptive lexical retrieval, entity-section graph retrieval, BM25, and a pinned offline embedding route behind closed quality gates. It does not modify the legacy, embedding, classical, entity-graph, or adaptive packages.

The concise interpretation and complete cross-family metric table are in [EVALUATION-CONCLUSIONS.md](EVALUATION-CONCLUSIONS.md).

## Current CLI-only verification

The active consultant invokes its packaged deterministic Python runner directly and
retains deep bundle validation, the `quality`/`fast`/`robust` policies, bounded
coverage, authoritative evidence paths and locators, text-hash checks, and read-only
operation. It does not discover or call MCP tools and has no automatic MCP fallback.

The hard `q031-graph-routing-boundary` trial exercised this path end to end. Deep
validation passed; `quality` used adaptive, BM25, embedding, and entity-graph
signals; five pages contained `[48, 48, 48, 48, 14]` claims; and deduplication
produced 206 unique reviewed claims. The run recorded coverage SHA-256
`881dec7d573003631c7ee5bb6c55ba4568393df1f911c26dbaa7bfa5c0619ac7`
and priority-order SHA-256
`9ec21df4d02d0e1fba2a9dac3555c68e424968d347ff4d48d8df768351e1b25b`.
It covered 4/4 atomic groups, 1/1 important-negative group, 3/3 required papers, and
four authoritative evidence bindings with zero MCP calls. The complete trial took
approximately 66.23 seconds in its measured environment, and its captured final
output SHA-256 was
`e052575835024481527ed7f07c80242a2ab414370f8868323861945931e43d50`.

This is a manual operational verification of one difficult question, not a new
40-question retrieval benchmark or aggregate answer-output evaluation. The direct
retrieval tables below remain valid measurements of the deterministic algorithms.
The 90-answer response-contract, grounding, correctness, and completeness results
remain historical MCP-treatment evidence until a fresh CLI-only answer experiment
is completed.

The checked [q031 cross-family report](cli-q031-comparison.md) contains every exact
answer and its full machine-readable response. The current deterministic CLI output
passes all five retained q031 mechanical gates. A separate fresh
[MCP-free Skill Arena diagnostic](cli-q031-skill-arena-diagnostic.md) distinguishes
that core result from agent publication behavior: after rejecting one 240-second
adapter timeout, the retry scored `0.6` for the knowledge-only control and `0.8` for
the CLI-skill treatment. The treatment missed only evidence validity because its
final message changed two dot-preserving authoritative filenames to hyphenated,
nonexistent paths. The CLI finalizer had emitted the correct paths. This one-pair
diagnostic is not an aggregate or causal quality estimate; it documents the exact
publication-integrity limitation that remains after removing MCP.

## Authority and frozen boundary

The authoritative knowledge remains the Semantic OKF core under `semantic/` and `concepts/`. The `adaptive/`, `entity-graph/`, `retrieval/`, and `ensemble/` trees are derived, hash-bound discovery artifacts. They cannot establish answer authority by score, graph path, or model similarity alone. Consultation is read-only and final evidence must resolve to a validated authoritative record, source path, locator, and text hash.

The direct retrieval evaluation binds the unchanged parent benchmark `semantic-okf-adaptive-frozen-40-plus-hard10-v1` at SHA-256 `2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414`. It contains the original 30 questions plus the 10 evidence-first hard questions. Answer-evidence coverage and answer-output scoring bind the append-only reviewed superset `semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1`, whose [manifest](reviewed-benchmark/frozen-answer-benchmark.json) has SHA-256 `257997cc2da3d9afae596ac8b46551a1b1fa73480f15861a25f262bb85a91f62`. The reviewed benchmark preserves question bytes, qrels, statements, required papers/sources, derivations, variants, and all parent evidence options; it adds only independently sufficient reviewed claim-ID alternatives.

The [parent frozen benchmark](../semantic-okf-adaptive-evolution/frozen-benchmark.json), [reviewed answer benchmark](reviewed-benchmark/frozen-answer-benchmark.json), [ensemble plan](ensemble-plan.json), [evaluation contract](evaluation-contract.json), and [answer-output evaluation contract](answer-output-evaluation-contract.json) have distinct roles:

- the parent frozen benchmark defines retrieval questions and qrels and remains read-only;
- the reviewed answer benchmark versions acceptable evidence alternatives without changing questions or qrels;
- the ensemble plan is the closed builder input;
- the evaluation contract binds routes, ranking rules, hard gates, metrics, and the causal-claim boundary; and
- the answer-output contract defines the generated-answer review without leaking expected evidence into the consultation skill.

Question IDs and answer keys are excluded from the bundle and runtime plan. Correcting benchmark truth requires a new benchmark identity rather than editing either frozen file.

## Final build

The accepted release evidence is run `20260715-ensemble-final-03`. Its compact [JSON report](build-validation-final.json) and [English report](build-validation-final.md) record:

| Property | Accepted value |
| --- | --- |
| Inputs | 15 paper Markdown files, 15 reviewed claim JSONL files, and 1 separately declared vocabulary |
| Manifest SHA-256 | `a4e83ce7d9630bf57ce4b3c2bf2cb445e34032c3ec46673b4bbed585885b0c37` |
| Ensemble plan file / canonical SHA-256 | `0f30f15f4156223a72200544ec07ffab33ee3d2a92aac09424f8444ad38339f5` / `cbbc28d140667670621260513d08998a740227f2bdf93f4dce754f4c996dd8eb` |
| Authoritative records | 874 |
| Authoritative core tree SHA-256 | `331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424` |
| Ensemble index SHA-256 | `9ce8bac88df8621fd870d718d1166e706516f4c4d56497eecc080d454453e939` |
| Publication | independently validated private candidate followed by one atomic rename |
| Rebuild result | 904 files versus 904 files, zero path or digest differences |

Both independent builds passed closed-schema, component-plan parity, authoritative-core parity, exact-source selection, question-isolation, pinned-model, validation, and reproducibility gates. Their authoritative core matches the pre-existing alternatives.

## Accepted policies

The completed four-generation population search selected the current `quality` policy. The three runtime policies serve different operational needs:

| Policy | Active routes and weights | RRF `k` | Gate behavior |
| --- | --- | ---: | --- |
| `quality` | adaptive `4`, graph fusion `1`, BM25 `5`, embedding hybrid `1` | 7 | Protect the adaptive set; promote the graph-lexical rank-one candidate to final rank one only when it is already within adaptive rank 10 and at least three of five declared voters place it within depth 3. |
| `fast` | adaptive `4`, graph lexical `1` | 5 | Promote the graph-lexical rank-one candidate only when both routes place it within depth 3 and it is already within adaptive rank 3. This avoids the embedding route but is not guaranteed to beat `robust` in wall-clock latency. |
| `robust` | adaptive only | 0 | Preserve the validated adaptive ordering with no effective promotion. |

Graph lexical is a consensus voter for `quality`, not an additional fusion weight. Stable ties use fused score, best active-component rank, active-component rank sum, active-route presence, and canonical paper ID, in that order. `quality` and `fast` fail closed when a required component is unavailable; `robust` remains available only when adaptive validation succeeds.

The checked [population-search report](population-search-results.md) and its [machine-readable companion](population-search-results.json), SHA-256 `cf684b0fb097bcca13a79d64241eee9979e688999abd8b51e4a4524b8d42fb14`, cover 4 generations, 40 candidate evaluations, 3 deterministic replays per candidate, and 4,800 question rankings. The winner is `generation-001/candidate-02` with weights `4:1:5:1`, RRF `k=7`, fitness `91.8891506056`, and the consensus tie order. Thirty-seven candidate evaluations passed and three failed. Two later generations did not improve the best fitness, satisfying the declared plateau rule. Final-03 adds a reviewed semantic-claim coverage gate after paper ranking; it does not change routes, weights, ranking, or the replayed metrics, so this selection evidence remains applicable. The population result is evidence on this frozen optimization target; it is not generated-answer or causal evidence.

## Current retrieval reports

The runner deep-validates the bundle, executes the frozen 40-question top-10 protocol, and independently revalidates every retained hit under the evidence-valid schema 1.2 contract. The compact reports recompute metrics from the retained hits rather than trusting raw aggregate fields.

| Policy | Checked machine report | Report SHA-256 | Ranking SHA-256 |
| --- | --- | --- | --- |
| `robust` | [ensemble-robust-current-direct.json](baselines/ensemble-robust-current-direct.json) | `da205a3cc10cfaa95b1d72edd93239848f78b4c4539dea0708b49764d2089ca0` | `1cd400efd0d3b936cacb7a8bbc98b7d3053265256c0b58b4ce7c8ee2e8a3c90c` |
| `fast` | [ensemble-fast-current-direct.json](baselines/ensemble-fast-current-direct.json) | `ba83c8292eefccdf3a20dfe373f11b72afddcc3d469b7c720b60c3e1410148a0` | `58ffec9f7ec18413e3cd397f874be81014976b850f8f9b168637d038b8e3d835` |
| `quality` | [ensemble-quality-winner-direct.json](baselines/ensemble-quality-winner-direct.json) | `c487fd4ec828bb1164860bd55f3e1794290cfbbb842d23a2898691dd316e57ce` | `a8c94ecbe6967993a7920edd06e62c4cbefad27513b9445740294684329c3346` |

All three policies returned 100% independently valid evidence with no query errors. `quality` achieved 83.82% Recall@10, 100.00% MRR@10, and 85.20% nDCG@10 over all 40 questions; on the hard 10 it achieved 95.50%, 100.00%, and 88.27%. See [ensemble-determinism.json](baselines/ensemble-determinism.json) for the repeated-ranking bindings: `fast` and `robust` matched across three repetitions, while `quality` matched across three same-process repetitions and a fourth repetition in a second fresh process.

The raw append-only reports are retained under:

```text
evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/retrieval/robust-three-repetitions.json
evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/retrieval/fast-three-repetitions.json
evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/retrieval/quality-three-repetitions.json
evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/retrieval/quality-fresh-process.json
```

These large raw artifacts remain ignored and append-only. Checked reports, plans, hashes, and English documentation are the compact reproducibility layer.

## Answer-evidence gates

Direct top-10 paper ranking is not the whole answer workflow. The `coverage-pack` operation decomposes a synthesis question into facets, runs adaptive retrieval, reviewed-claim graph expansion, and pinned semantic claim retrieval, then produces a gated union of exact authoritative bindings. Candidate graph edges and embedding similarity have zero answer authority: every retained claim must intersect a reviewed exact answer binding.

The accepted [paper-diversified hard-10 report](hard10-coverage-pack-multisignal-diversified-publication-gate-final.md) and its [machine-readable companion](hard10-coverage-pack-multisignal-diversified-publication-gate-final.json) have SHA-256 values `25720899f87efedf4f9c901d91df19dbe97d2ffba53fec7c61e8dff0576ad0a1` and `f96ab9356a99ca5b3798e4de6912e0a6b5fc010c3abb5711360b85257374deec`, respectively. They bind the reviewed answer benchmark and pass plan, provider/index, determinism, read-only, reviewed-claim, question-isolation, and exact evidence-identity gates.

The `adaptive-paper-conditioned-claim-diversification-v1` reranker retains a six-claim global prefix, then reserves up to six semantic claims for each of the first three distinct papers selected by adaptive retrieval before filling from global semantic order. It does not receive evaluator IDs or labels, introduce a paper, change direct ranking, or exceed the existing 20-per-facet and 240-total semantic caps.

| Coverage candidate | Atomic groups | Important-negative groups | Required papers | Mean semantic candidates | Mean union candidates | Exact binding validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Global semantic order, retained diagnostic | 43/44 | 13/13 | 100.0% | 126.1 | 166.4 | 713/713 |
| Paper-conditioned diversity, accepted | **44/44** | **13/13** | **100.0%** | 104.4 | 162.4 | **713/713** |

The accepted semantic component alone covers 39/44 groups versus 42/44 before diversification, but it is less redundant with adaptive and graph candidates and raises union coverage to 100%. This variable-budget union must not be described as Recall@30. These are candidate-availability and exact-identity measurements, not generated-answer correctness, completeness, or entailment.

In the historical v1.5.0 treatment, the bounded `semantic_okf_coverage_brief` MCP tool exposed the complete deduplicated union without sending one unbounded result. The diversified q031 pack contained 206 claims and remained within the five-page protocol. The stateful treatment protocol required one first `semantic_okf_bootstrap_skill` call, `semantic_okf_inspect`, every coverage page for identical parameters, and a final clean transaction consisting of one or more successful `semantic_okf_prepare_answer` calls while the draft was still being reviewed followed by exactly one successful `semantic_okf_confirm_answer` call as the terminal tool call. Preparation independently recomputed the unpaged pack and constructed the contracted answer from reviewed bindings.

That isolated runtime was the profile-gated, read-only MCP server version 1.5.0. The knowledge-only and adaptive controls received an empty tool list; only the ensemble treatment received `semantic_okf_bootstrap_skill`, `semantic_okf_inspect`, `semantic_okf_coverage_brief`, `semantic_okf_prepare_answer`, and `semantic_okf_confirm_answer`. All five tools were read-only, non-destructive, and closed-world. Bootstrap and confirm were deliberately non-idempotent; inspect, coverage, and prepare were idempotent. Bootstrap accepted no arguments, resolved only the installed skill under `CODEX_HOME`, verified its frozen raw-byte identity, and returned its exact UTF-8 body through `semantic-okf-skill-bootstrap/1.0`. It had to succeed exactly once before every other Semantic OKF call. The treatment host disabled the general shell tool before Codex started, while both controls retained the shared baseline command behavior. The prepare schema had no `mode` and returned the canonical closed `semantic-okf-prepared-answer/1.0` envelope with exactly `schema`, `candidate_json`, `response_sha256`, and `byte_count`. Confirm accepted only `response_sha256`, which had to be 64 lowercase hexadecimal characters. `SEMANTIC_OKF_PYTHON` identified the exact absolute Python executable bound by the config manifest, while `SEMANTIC_OKF_HF_HUB_CACHE` identified an absolute directory containing the pinned model revision. Relative or missing paths failed closed. Skill Arena disabled network and web search and set the Hugging Face and Transformers offline controls, so an unavailable runtime or model cache was an error rather than a download or lexical substitution. No host-specific absolute path was checked into the evaluation.

Historical treatment outputs were published through a separate confirmed-output host gate. The agent reviewed the exact `candidate_json` string inside the prepared envelope, then sent only that envelope's short `response_sha256` to confirm; it never copied the candidate or envelope into the confirm call. The server verified the outstanding digest, consumed the candidate, and returned a closed receipt binding the exact candidate hash and UTF-8 byte count. Confirm had to succeed exactly once and be the terminal tool call. Any failed answer-protocol call—prepare or confirm—published nothing and abandoned the active transaction. Recovery required a fresh successful prepare and its new digest; a prior envelope was no longer eligible. The wrapper parsed the strict envelope, verified its schema and exact keys, candidate canonicality, digest, byte count, terminal receipt, and transaction order, then atomically published the exact `candidate_json` bytes. Any earlier successful confirm, confirm without a fresh prepare after failure, stale or mismatched digest, repeated confirm, trailing tool call, non-canonical candidate, or envelope, protocol, hash, length, receipt, or terminal-sequence mismatch failed closed. Controls remained transparent pass-throughs.

The [bootstrap and shell-isolation technical preflight](bootstrap-isolation-technical-preflight-final.md) exercised the real provider once on q031. It observed zero command-execution events, the exact 15,699-byte skill bootstrap, five coverage pages, a clean digest confirmation, the canonical `shell_tool_disabled: true` receipt, and byte-identical host publication. The host corrected a differing raw agent message. All prompt assertions passed, but the treatment-only one-row smoke is explicitly non-causal and supplies no aggregate answer metric.

The need for these host and isolation gates is evidence-based. The [finalizer copy-integrity diagnostic](finalizer-copy-integrity-diagnostic-20260715.md) stopped after 46/90 rows because only 5/15 treatment outputs copied finalizer bytes exactly. The later [host-publication mutation diagnostic](host-publication-mutation-diagnostic-20260715.md) found that 0/3 q031 host outputs matched their valid confirmed candidates and six evidence fields changed. The [long-candidate confirmation diagnostic](long-candidate-confirmation-diagnostic-20260715.md) records the frozen v1.3.1 failure. Finally, the [skill-bootstrap isolation diagnostic](skill-bootstrap-isolation-diagnostic-20260715.md) records the partial v1.4.0 run that was stopped after a faithful but uncontracted shell read of the mounted skill. All four attempts are rejected diagnostics, not answer-quality evidence; no row or metric may be merged into the accepted comparison.

The historical [manual q031 verification](manual-query-verification-final.md), its [machine-readable companion](manual-query-verification-final.json), and [checked draft](manual-query-q031-draft.json) prove one pre-diversification finalizer path could cover all four q031 groups and reconstruct exact bindings without mutating the bundle. It does not establish the current host-publication contract or aggregate semantic quality.

The parent [expected-ID audit](EXPECTED-ID-AUDIT.md) found all 44 atomic mappings and 13 important-negative sets sensible. The new reviewed benchmark preserves those mappings and appends 41 independently sufficient option links, for 113 links, 68 unique reviewed IDs, and 71 authoritative evidence objects; 38 close but insufficient alternatives are explicitly rejected. Exact-ID coverage remains deliberately stricter than semantic correctness and must not replace blinded semantic review.

## Reproduction

Run from the repository root in the pinned Python 3.12 offline environment. The embedding model revision must already be in the local cache. Never rebuild over the recorded release; choose a new append-only run ID and two paths that do not exist.

### Build and independently validate two fresh snapshots

```powershell
$RunId = 'REPLACE-WITH-NEW-APPEND-ONLY-ID'
$RunRoot = "evaluations/semantic-okf-ensemble/results/runs/$RunId"
$BundleA = "$RunRoot/workspace-a/knowledge"
$BundleB = "$RunRoot/workspace-b/knowledge"

python skills/build-semantic-okf-ensemble/scripts/runtime_smoke.py
python skills/build-semantic-okf-ensemble/scripts/build_semantic_okf_ensemble.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-ensemble/ensemble-plan.json $BundleA --output-format json
python skills/build-semantic-okf-ensemble/scripts/validate_semantic_okf_ensemble.py `
  $BundleA --output-format json
python skills/build-semantic-okf-ensemble/scripts/build_semantic_okf_ensemble.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-ensemble/ensemble-plan.json $BundleB --output-format json
python skills/build-semantic-okf-ensemble/scripts/validate_semantic_okf_ensemble.py `
  $BundleB --output-format json
```

Compare complete relative-path inventories and SHA-256 values before accepting a rebuild. The checked final result of that comparison is [build-validation-final.json](build-validation-final.json).

### Validate and replay the recorded release

The recorded bundle is read-only at `evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/workspace-a/knowledge`. Write any new retrieval output beneath a new ignored run directory.

```powershell
$Bundle = 'evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/workspace-a/knowledge'
$Replay = 'evaluations/semantic-okf-ensemble/results/runs/REPLACE-WITH-NEW-ID/retrieval'

python skills/consult-semantic-okf-ensemble/scripts/query_semantic_okf_ensemble.py `
  $Bundle --deep-validation inspect
python evaluations/semantic-okf-ensemble/scripts/run_frozen_retrieval.py `
  --bundle $Bundle --policy robust --repetitions 3 `
  --output-json "$Replay/robust-three-repetitions.json" --output-markdown "$Replay/robust-three-repetitions.md"
python evaluations/semantic-okf-ensemble/scripts/run_frozen_retrieval.py `
  --bundle $Bundle --policy fast --repetitions 3 `
  --output-json "$Replay/fast-three-repetitions.json" --output-markdown "$Replay/fast-three-repetitions.md"
uv run --python 3.12 `
  --with-requirements skills/consult-semantic-okf-ensemble/scripts/requirements-embeddings.txt `
  python evaluations/semantic-okf-ensemble/scripts/run_frozen_retrieval.py `
  --bundle $Bundle --policy quality --repetitions 3 `
  --output-json "$Replay/quality-three-repetitions.json" --output-markdown "$Replay/quality-three-repetitions.md"
```

Recompute a compact direct report from each raw route with `scripts/compare_direct_retrieval.py`. For example:

```powershell
python evaluations/semantic-okf-ensemble/scripts/compare_direct_retrieval.py `
  --report "$Replay/quality-3x.json" --route ensemble_quality `
  --candidate-label definitive-ensemble-quality-winner `
  --output-json "$Replay/quality-direct.json" `
  --output-markdown "$Replay/quality-direct.md"
```

Use route `ensemble_fast` for `fast` and `ensemble_robust` for `robust`. Do not relabel a component replay as ensemble behavior.

### Recheck population selection and hard-question coverage

```powershell
python evaluations/semantic-okf-ensemble/scripts/summarize_population_search.py --check

python evaluations/semantic-okf-ensemble/scripts/evaluate_hard10_coverage_pack.py `
  --candidate definitive-ensemble-quality-paper-diversified-publication-gate-v1 --bundle $Bundle `
  --top-k 30 --per-facet 12 --maximum-facets 12 --repetitions 3 `
  --output-json "$Replay/hard10-coverage-pack.json" `
  --output-markdown "$Replay/hard10-coverage-pack.md"
```

### Repeat the manual finalization check

```powershell
$Question = 'A production router must choose among question-only or standalone-model answering, basic RAG, and GraphRAG before generation. Derive an evidence-based decision boundary for simple facts, interconnected synthesis, and noisy graph evidence, and explain why an always-use-the-graph policy is unsupported.'

python skills/consult-semantic-okf-ensemble/scripts/query_semantic_okf_ensemble.py `
  $Bundle search --policy quality --query $Question --top-k 10
python skills/consult-semantic-okf-ensemble/scripts/query_semantic_okf_ensemble.py `
  $Bundle coverage-pack --query $Question --top-k 30 --per-facet 12 --maximum-facets 12
Get-Content evaluations/semantic-okf-ensemble/manual-query-q031-draft.json -Raw | `
  python skills/consult-semantic-okf-ensemble/scripts/query_semantic_okf_ensemble.py `
  $Bundle finalize-answer --draft - --question-id q031-graph-routing-boundary `
  --query $Question --top-k 30 --per-facet 12 --maximum-facets 12
```

## Repository validation

```powershell
python evaluations/semantic-okf-adaptive-evolution/scripts/validate_frozen_benchmark.py
python evaluations/semantic-okf-ensemble/scripts/generate_reviewed_answer_benchmark.py --check
python evaluations/semantic-okf-ensemble/scripts/generate_skill_arena_config.py --check
python evaluations/semantic-okf-ensemble/scripts/summarize_population_search.py --check
python evaluations/semantic-okf-ensemble/scripts/validate_scaffold.py
skill-arena val-conf evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml
skill-arena evaluate evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml --dry-run
python -m compileall -q evaluations/semantic-okf-ensemble/scripts
$SkillValidator = "$env:USERPROFILE/.codex/skills/.system/skill-creator/scripts/quick_validate.py"
python $SkillValidator `
  skills/build-semantic-okf-ensemble
python $SkillValidator `
  skills/consult-semantic-okf-ensemble
python -m pytest -q
python scripts/check_coverage.py --threshold 80
```

## Isolated answer-output evidence

The v1.5.0 Skill Arena control/treatment compare `2026-07-15T15-24-19-159Z-compare` (`eval-RTd-2026-07-15T15:24:26`) completed all 90 planned answers: three profiles, ten hard questions, and three repetitions per cell. Preparation `live-published-confirmed-01` produced 90 blinded review tasks and 90 completed reviews. The compact [JSON](answer-output-comparison-final.json), SHA-256 `6f48c963e8c1f85f9c1355a2d1d796ff8821239c05fb19ad72f78488a6acd5ae`, and [English report](answer-output-comparison-final.md), SHA-256 `2e37ec6602839d89ee27e1eb6fe6b8a8f1a8b3da24dbd5576ecaef08dad10178`, contain the complete aggregate and per-question results.

| Profile | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `knowledge-only-control` | 0.0% | 13.3% | 5.6% | 5.4% | 90.6% | 75.1% | 3.7% | 75.3% | 39.8% | 94.2% | 5.0% |
| `adaptive-consult-control` | 3.3% | 23.3% | 82.6% | 82.5% | 83.0% | 72.7% | 55.3% | 76.0% | 74.8% | 86.7% | 78.3% |
| `ensemble-consult-treatment` | **53.3%** | **100.0%** | **100.0%** | **100.0%** | **96.7%** | **91.1%** | **86.0%** | **98.5%** | **98.5%** | **99.2%** | **100.0%** |

| Matched ensemble minus adaptive delta | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ten matched questions | +50.0 pp | +76.7 pp | +17.4 pp | +17.5 pp | +13.7 pp | +18.4 pp | +30.7 pp | +22.5 pp | +23.8 pp | +12.5 pp | +21.7 pp |

Strict full pass requires every independent contract, evidence, and semantic gate to pass for one output. It is therefore deliberately harsher than any component mean: the ensemble passed all gates on 16/30 outputs, adaptive on 1/30, and knowledge-only on 0/30. The ensemble's worst-question means were still 100.0% for contract, evidence validity, and grounding, 87.5% for correctness, and 79.2% for completeness; its remaining worst-question bounds were 66.7% exact atomic IDs, 91.7% papers, 91.7% sources, 91.7% important negatives, and 100.0% exact negative IDs.

Correctness, completeness, and important-negative coverage are model-judged under a fixed blinded rubric. They are comparative evidence, not mechanical truth. Contract, evidence validity, grounding, exact identities, paper, and source metrics are mechanically recomputed against the frozen bundle. These answer metrics must also remain separate from Recall@10, MRR@10, and nDCG@10: retrieval measures which papers were found and ordered, while the answer report measures the generated synthesis.

The historical isolated estimand was the full then-definitive consultation capability: the skill, digest-bound bootstrap, profile-gated MCP transport, mandatory inspect/all-pages/prepare/digest-confirm workflow, treatment shell restriction, and exact confirmed-output host publication. It was not an estimate of the skill text alone. The passing attestation records 30/30 exact treatment bootstrap/terminal-confirm sequences, zero treatment shell execution, 16 host publication corrections, and three clean recoveries after failed protocol attempts. One adaptive-control q040 trace has a superseded command start followed by an exact successful retry; the closed attestor reports it as one bounded control-runtime diagnostic and forbids it in treatment traces. The four rejected diagnostics—including the partial v1.4.0 bootstrap run—remain excluded from every result above. The all-skills portfolio remains descriptive rather than causal.

The ensemble is the best observed candidate on this frozen benchmark, not a universal winner. The weights were selected on the same target, semantic metrics use a model judge, and only ten hard questions support the answer-output contrast. The checked conclusion document records the complete interpretation boundary and historical comparisons.

For the separate legacy implementation question, see the [legacy `grep` / `rg` investigation](../semantic-okf-classical/legacy-grep-investigation.md). It confirms that the optional reader instruction to use `rg` for an exact phrase is distinct from the evaluator's in-memory deterministic TF-IDF-like `legacy_lexical` algorithm; the legacy baseline was not modified.
