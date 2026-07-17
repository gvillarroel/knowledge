# Semantic OKF Harbor Evolution Results

Campaign: `20260716-pi-spark-one-evolution-pilot`

Date: 2026-07-16

Status: complete

## Executive conclusion

There is no single winner on every measured axis. The evolved **classical** consultation skill is the strongest mechanical primary candidate: it scores `0.995`, `1.000`, and `1.000` on the live train, development, and holdout questions; passes every declared promotion gate; and retains the strongest selected deterministic ranking profile (`MRR@10 0.915`, `nDCG@10 0.835`) among the six families. It is not universally best, because its manually reviewed answer completeness falls on both `q031` and `q034`.

The evolved **embeddings** skill is the most consistently positive evolution across the live cases. Harbor reward improves on all three questions, holdout semantic correctness rises from `0.85` to `0.95`, and the selected lexical route has the best hard-question recall (`80.8%`). The evolved **entity-graph** skill is a useful complementary strategy: it turns the training timeout into a valid answer and produces the most complete development answer (`0.889`), but its deterministic rank quality and holdout evidence coverage remain weaker.

The mechanical campaign decisions are:

| Family | Mechanical decision | Practical interpretation |
|---|---|---|
| Legacy | Promoted | Passes the declared development gates, but the evolved training output is invalid JSON and deterministic retrieval is weakest; retain as a compatibility baseline rather than the preferred default. |
| Embeddings | Promoted | Most consistent live reward improvement and strongest selected hard recall; recommended as a complementary high-recall route. |
| Classical | Promoted | Strongest overall mechanical primary candidate; use semantic-completeness checks because concise answers omitted important conditions. |
| Adaptive | Rejected | Evolved development evidence is not fully valid, the quality gate fails, and reward regresses from `1.000` to `0.000`. |
| Entity graph | Promoted | Distinct and valuable for entity-oriented synthesis; development semantics are excellent, but holdout evidence coverage is incomplete. |
| Ensemble | Pending | Evolved development output repairs a baseline timeout, but the missing baseline hard-completeness value makes the declared non-regression gate unobservable. |

“Promoted” here means that the candidate passed the campaign's declared **mechanical development gates**. It does not mean that every answer was semantically better, and it does not override the separate training and holdout observations.

## What was evaluated

All six knowledge-builder/consultation families were compared on the same published Semantic OKF cores:

| Family | Retrieval methods in the existing alternative | One Harbor-guided evolution |
|---|---|---|
| Legacy | Validated ledger and read-only SPARQL; evaluator-side whole-record TF-IDF for ranked benchmarking | Standalone deterministic ledger TF-IDF plus a bounded, hash-bound answer compiler |
| Embeddings | Lexical, vector, and lexical-vector hybrid retrieval | Standalone bounded answer compiler over the unchanged embedding consultation implementation |
| Classical | BM25, topic, lexical-association, and fused retrieval | Standalone bounded answer compiler over the unchanged classical retrieval implementation |
| Adaptive | BM25, topic, association, fusion, and query-adaptive routing | Standalone bounded answer compiler over the unchanged adaptive retrieval implementation |
| Entity graph | Lexical, entity, graph traversal, and fused retrieval | Standalone bounded answer compiler over the unchanged graph retrieval implementation |
| Ensemble | Quality, fast, and robust policies over multiple derived indexes | Standalone bounded answer compiler over the unchanged ensemble retrieval implementation |

Each evolution is independently named and installable. The parent packages were not edited. The retrieval scripts in every evolved package are byte-identical to their parents; the change is the family-specific `prepare`/`finalize` answer path. `prepare` selects and projects bounded candidates onto exact authoritative parent records. `finalize` rebuilds that support set, rejects unknown or changed support IDs, enforces the closed response schema, and emits hash-valid evidence in first-use order. Ranks, vectors, topics, entity edges, excerpts, and support packs remain derived and non-authoritative.

## Source and benchmark provenance

The test source is the official English Astro documentation from [`withastro/docs`](https://github.com/withastro/docs.git), pinned at commit:

```text
5c37be52c5038e1174be1e838d3dd5852db26a21
```

The accepted corpus contains 416 English MDX files under `src/content/docs/en`, totaling 2,944,859 checked bytes. Its tree SHA-256 is `f287ff3b67b568db7fa90e871ce6c06d272f4e94ed0ec71d2eb365de261ae9bd`. Those pinned MDX bytes are authoritative. Semantic OKF projections, qrels, graphs, indexes, rankings, ground truth, and scores are derived.

The benchmark retains 30 existing questions and adds 10 evidence-first hard questions, for 40 total:

| Question class | Count |
|---|---:|
| Direct | 20 |
| Cross-document | 10 |
| Hard, evidence-first | 10 |
| Total | 40 |

The full label split is 24 train, 8 development, and 8 holdout questions with no label overlap. The live pilot uses only one prospectively declared question from each cohort: `q031` for training, `q032` for development, and `q034` for holdout. The source pages are not split-disjoint and the checked ground truth is historically visible, so this is question-use isolation rather than a claim of an untouched secret population.

The agent prompt contains the question, expected response ID, and source-generic response contract. It does not contain qrels, required source identities, ground-truth claims, expected evidence, derivation logic, or failure conditions.

## Deterministic 40-question retrieval benchmark

The following table reports the selected route for each family. `Recall@10` is the fraction of relevant documents recovered in the first ten distinct results. `MRR@10` rewards putting the first relevant result early. `nDCG@10` rewards ordering all relevant results well. The latency is a standalone, one-route-at-a-time measurement, so it is comparable across these rows.

| Family | Selected route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms | p95 ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Legacy | `legacy_tfidf` | 82.3% | 71.7% | 0.706 | 0.685 | 100.0% | 2.3 | 3.3 |
| Embeddings | `lexical` | 89.8% | **80.8%** | 0.812 | 0.783 | 100.0% | 148.1 | 175.9 |
| Classical | `association` | 88.8% | 74.2% | **0.915** | **0.835** | 100.0% | 1,570.2 | 1,669.8 |
| Adaptive | `association` | 88.8% | 74.2% | **0.915** | **0.835** | 100.0% | 1,395.7 | 1,468.7 |
| Entity graph | `entity` | 88.1% | 78.3% | 0.729 | 0.706 | 100.0% | 1,148.0 | 1,545.9 |
| Ensemble | `quality` | 89.6% | 77.5% | 0.890 | 0.819 | 100.0% | 7,335.5 | 12,758.2 |

Important route-level details:

- The embeddings `hybrid` route has the highest raw `Recall@10` of any individual route (`90.4%`), but its `nDCG@10` (`0.767`) is below the selected embeddings lexical route.
- Classical and adaptive BM25 produce the best `MRR@10` among their individual routes (`0.921`) and require only about 55–67 ms, while their topic and association variants improve other rank characteristics at much higher cost.
- Entity traversal alone is weak (`58.8% Recall@10`), but direct entity retrieval reaches `78.3%` hard recall, showing that the graph strategy is genuinely distinct rather than a cosmetic lexical variant.
- Ensemble `fast` and `robust` are much cheaper diagnostic routes than `quality`; the selected quality policy is over 7 seconds per question and is not the latency winner.

Because all evolved retrieval scripts are byte-identical to their parent implementations, baseline and evolved deterministic retrieval results are identical by construction and verification. The Harbor evolution changes answer assembly and contract enforcement, not the underlying 40-question ranking result. The full 20-route table is in [`reports/deterministic-40.md`](reports/deterministic-40.md), with its machine-readable counterpart in [`reports/deterministic-40.json`](reports/deterministic-40.json).

## Live Harbor baseline-to-evolved results

Each cell below is `baseline → evolved` Harbor reward for one real Pi model run. Reward is in `[0, 1]`; zero can mean a failed non-compensating quality gate rather than a semantically empty answer.

| Family | Train `q031` | Development `q032` | Holdout `q034` | Direction across the three observations |
|---|---:|---:|---:|---|
| Legacy | 0.000 → 0.000 | 0.000 → **1.000** | 0.000 → **0.992** | Two operational repairs, but evolved train remains invalid JSON |
| Embeddings | 0.270 → **0.991** | 0.485 → **0.704** | 0.658 → **0.988** | Improves all three live rewards |
| Classical | 0.960 → **0.995** | 0.726 → **1.000** | 1.000 → 1.000 | Improves or ties all three |
| Adaptive | 0.000 → **0.995** | **1.000** → 0.000 | 1.000 → 1.000 | Training repair, development regression, holdout tie |
| Entity graph | 0.000 → **0.622** | 0.548 → **0.726** | 0.400 → **0.466** | Improves all three, from a lower evidence baseline |
| Ensemble | **0.767** → 0.603 | 0.000 → **0.992** | 0.992 → **1.000** | Training regression, development timeout repair, holdout gain |

The live campaign contains 36 accepted trials: six families × two generations × three questions. There is exactly one attempt per accepted family/generation/question observation.

### Declared promotion gates

The gates are non-compensating. A higher nDCG or reward cannot compensate for invalid JSON, an unknown evidence identity, a bad hash, or a runtime failure.

| Family | Runtime | Contract | Non-null | References | All evidence | Quality gate | Dev reward non-regression | Dev hard-completeness non-regression | Deterministic retrieval | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| Legacy | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Promoted |
| Embeddings | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Promoted |
| Classical | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Promoted |
| Adaptive | Pass | Pass | Pass | Pass | **Fail** | **Fail** | **Fail** | **Fail** | Pass | Rejected |
| Entity graph | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Promoted |
| Ensemble | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Unknown | Pass | Pending |

The ensemble baseline timed out on `q032`, so its baseline hard-completeness dimensions were not emitted. Missing is preserved as unknown; it is not silently converted to zero. The holdout was opened only after every evolved candidate had been frozen, and no candidate was edited afterward.

### Live resource use

These are descriptive totals across the three accepted live questions per generation. They include the 600-second entity-graph training and ensemble development baseline timeouts, so they are not steady-state service benchmarks.

| Family | Total latency seconds, B → E | Input tokens, B → E | Output tokens, B → E | Runtime errors, B → E |
|---|---:|---:|---:|---:|
| Legacy | 212.2 → 227.8 | 3,806,051 → 2,430,294 | 40,843 → 45,741 | 0 → 0 |
| Embeddings | 565.1 → 361.9 | 1,262,652 → 994,640 | 48,376 → 33,397 | 0 → 0 |
| Classical | 409.3 → 337.5 | 2,630,256 → 1,161,077 | 40,305 → 24,210 | 0 → 0 |
| Adaptive | 1,039.9 → 425.9 | 4,080,711 → 980,403 | 56,443 → 30,100 | 0 → 0 |
| Entity graph | 972.4 → 439.6 | 4,121,488 → 2,942,129 | 41,752 → 51,414 | 1 → 0 |
| Ensemble | 1,533.2 → 874.8 | 1,131,414 → 1,717,612 | 28,001 → 42,327 | 1 → 0 |

Most evolutions reduce latency and input tokens. The exceptions are useful: legacy becomes slightly slower in aggregate despite using fewer input tokens, while ensemble reduces latency by eliminating a timeout but consumes substantially more input and output tokens.

The complete cohort tables report all 16 Harbor dimensions and per-observation resource totals in [`reports/campaign-comparison.md`](reports/campaign-comparison.md). The hash-bound source is [`reports/campaign-comparison.json`](reports/campaign-comparison.json).

## Actual answer quality on the three hard questions

Harbor's deterministic grader measures response shape, retrieval, identity, locator, hash, and evidence sufficiency. It does **not** prove that the answer prose says every required thing correctly. The actual final answers were therefore reviewed separately against the evidence-first atomic ground truth.

The next table reports `semantic correctness / completeness / grounding`, again as `baseline → evolved`. Correctness and grounding are conservative manual judgments in `[0, 1]`. Completeness is the deterministic mean of nine question-specific items: five atomic claims, two important negatives, and two explicit derivation requirements.

| Family | Train `q031` C/K/G | Development `q032` C/K/G | Holdout `q034` C/K/G |
|---|---|---|---|
| Legacy | .90/.722/.00 → .80/.667/.00 | .95/.778/.00 → .95/.722/.95 | .90/.944/.00 → .90/.944/.85 |
| Embeddings | .90/.722/.90 → .85/.667/1.00 | .95/.722/1.00 → .95/.833/.95 | .85/.889/1.00 → .95/.889/1.00 |
| Classical | .90/.722/1.00 → .95/.611/1.00 | .95/.722/1.00 → .95/.722/1.00 | .90/.944/1.00 → .95/.722/1.00 |
| Adaptive | .85/.611/.90 → .75/.500/.90 | .90/.667/1.00 → .80/.611/.75 | .90/.944/1.00 → .95/.778/1.00 |
| Entity graph | .00/.000/.00 → .90/.611/.75 | .90/.667/.95 → .95/.889/1.00 | .90/.944/1.00 → .95/.722/1.00 |
| Ensemble | .90/.722/.90 → .85/.556/.95 | .00/.000/.00 → .90/.722/.95 | .85/.889/.90 → .85/.722/1.00 |

The separation between metrics is material:

- On `q032`, evolved entity graph has Harbor reward `0.726` but the best manual completeness (`0.889`) because its prose states all five atomic claims even though its cited evidence covers only one of two required document identities.
- On `q034`, entity-graph baseline has Harbor reward `0.400` but manual completeness `0.944`; classical evolved has Harbor reward `1.000` but completeness `0.722`. The first metric scores the declared evidence contract, while the second scores answer content.
- Evolved embeddings is the clearest holdout improvement: reward rises `0.658 → 0.988`, correctness rises `0.85 → 0.95`, completeness holds at `0.889`, and grounding remains `1.00`.
- Evolved classical is mechanically excellent and semantically correct, but brevity removes conditions. On `q034`, it omits the unauthorized-remote-image outcome and weakens the authorization-before-dimension-inference rule.
- Evolved adaptive demonstrates why a gate must be non-compensating. On development, one invalid evidence row reduces `all_evidence_valid` and the quality gate to zero; semantic correctness, completeness, and grounding also regress.
- Evolved ensemble repairs the development timeout and the holdout's incorrect `imageDomains` identifier, but it regresses on training and loses holdout detail about unauthorized remote images.

The recurring semantic gaps are also actionable. `q031` answers often omit rate limiting, adapter-specific session-driver defaults, and the precise difference between `context.rewrite` and `next(Request-or-path)`. `q032` answers often omit that `Astro.url` inside a server island identifies the island endpoint and that a stable encryption key is needed across rolling deployments. `q034` answers often fail to state that remote dimension inference is authorized only after the URL passes the configured allowlist, and none fully explains the display-without-optimization fallback for an unauthorized remote image.

The complete answer reviews and exact bound result hashes are in:

- [`reports/q031-semantic-review.md`](reports/q031-semantic-review.md)
- [`reports/q032-semantic-review.md`](reports/q032-semantic-review.md)
- [`reports/q034-semantic-review.md`](reports/q034-semantic-review.md)

Their JSON companions use closed schemas and validators that recompute completeness, check result bindings, and extract the retained final Pi answer from the append-only trace.

## Metric definitions

Harbor emits 16 independent dimensions for every observation when available:

- Contract and validity: `response_contract`, `non_null_answer`, `reference_validity`, `evidence_validity`, `all_evidence_valid`, and `quality_gate`.
- Retrieval: `evidence_recall`, `evidence_precision`, `complete_qrel_coverage`, `mrr`, and `ndcg`.
- Hard-question sufficiency: `required_document_coverage`, `authoritative_evidence_completeness`, `atomic_claim_evidence_completeness`, and `important_negative_evidence_completeness`.
- Aggregate: `reward`.

The quality gate equals one only when the response contract, non-null answer, reference closure, and all evidence rows are valid. For these hard questions, the aggregate is:

```text
reward = quality_gate × (
    0.15 × evidence_recall
  + 0.10 × nDCG
  + 0.15 × required_document_coverage
  + 0.15 × authoritative_evidence_completeness
  + 0.30 × atomic_claim_evidence_completeness
  + 0.15 × important_negative_evidence_completeness
)
```

This formula intentionally makes malformed or invalidly grounded answers score zero. It is an evidence-and-contract utility, not a prose correctness probability.

## Benchmark identity and evidence integrity

The independent ID audit passes:

| Integrity check | Result |
|---|---:|
| Ordered question IDs | 40/40, exactly `q001`–`q040` |
| Split membership | 24/8/8, no overlap |
| Generated tasks aligned with benchmark | 40/40 |
| Qrel assignments | 80 |
| Distinct source-to-ledger-to-crosswalk joins | 30/30 |
| Hard required ID sets equal qrels | 10/10 |
| Unique real-grader evidence mappings | 46/46 |
| Oracle rewards | `q031=1.0`, `q032=1.0`, `q034=1.0` |

Question IDs are stable scoped ordinals. Document IDs are canonical English Astro routes. Source IDs are `astro-doc-` plus the first 16 hexadecimal characters of SHA-256 over the document ID. Record IDs derive from the pinned upstream MDX path. Qrel source and document arrays are validated as sets through the crosswalk rather than paired by list position.

For every hard locator, the grader first checks the raw authoritative file hash and selected-byte hash, then normalizes CRLF/CR to LF for the derived record join. It trims terminal publication newlines only when a direct normalized join fails at end-of-file. All 46 locators map uniquely; eight require the EOF-only trim. See [`reports/benchmark-id-audit.md`](reports/benchmark-id-audit.md) and [`reports/benchmark-id-audit.json`](reports/benchmark-id-audit.json).

## Runtime, authentication, network, and MCP boundary

| Component | Frozen value |
|---|---|
| Harbor | `0.18.0` |
| Agent | Built-in Pi, `0.73.1` |
| Model | `openai-codex/gpt-5.3-codex-spark` |
| Thinking | `high` |
| Agent session | One `--no-session` request per question |
| Runtime image | `semantic-okf-harbor-runtime:1.0` |
| Image ID | `sha256:5a6e31885c495758c9c979df71ae09aced5bb8869f3d6a54eb5706ba071a297c` |
| Knowledge mount | One family bundle, read-only |
| Embedding cache | Read-only and only for embeddings/ensemble |
| MCP | **Not used** |

Pi authentication is copied into a private per-job directory, mounted with `auth.json` mode `0600`, and destroyed after the job. Credentials are not stored in the image, configuration, trace report, or repository. The runner rejects empty or malformed authentication before starting Harbor.

Network isolation could not be enforced on this WSL Docker host because Harbor 0.18.0's egress-control sidecar failed for both allowlist and no-network policies. Both phases therefore ran in `public` network mode. The verifier remained a separate container, received no knowledge bundle, model cache, or authentication mount, and its grader performs no network operations, but this is **not** a claim that egress was technically blocked. A future rerun may use agent allowlisting and a no-network verifier only after those modes pass a disposable smoke test on a compatible host.

## Append-only runs and exclusions

Raw jobs, model traces, generated tasks, bundle snapshots, image receipts, and model caches are large, append-only, and ignored. Compact manifests and reports are checked in. The accepted binding ledger names every job and trial explicitly and binds each with the job result hash, job lock hash, trial result hash, and trial lock hash. The campaign reporter does not glob for a convenient successful run.

Eleven retained runs are documented but excluded from every aggregate and promotion decision:

| Exclusion category | Count | Reason |
|---|---:|---|
| Pre-fix grader | 6 | The runs predate the EOF publication-newline repair; corresponding `grader-r1` runs are authoritative. |
| Pre-agent authentication failure | 4 | Pi exited before task execution because the ephemeral credential mount was unavailable; later explicitly authenticated runs are authoritative. |
| Delayed duplicate | 1 | A redundant retry never produced a terminal trial; the already completed accepted run is authoritative. |

No semantic, retrieval, contract, or grounding failure was retried. Infrastructure-only failures are retained for auditability rather than overwritten or silently relabeled as skill failures. The exact roots and reasons are listed in [`reports/campaign-comparison.md`](reports/campaign-comparison.md).

## Skill Arena causal structure

Six separate Skill Arena configurations compare one baseline and one evolved skill within the same family on the frozen `q031` prompt. Each comparison uses the same family bundle, Pi model, runtime intent, and assertions; only the frozen skill changes. No all-skills portfolio is treated as causal evidence. All configurations passed schema validation and two-cell dry-run planning with no unsupported cells or prompt leakage.

These Skill Arena dry runs establish configuration and source-materialization integrity only. They are not additional model-quality observations. Harbor supplies the live answer, evidence, latency, and token evidence. See [`skill-arena/README.md`](skill-arena/README.md) and [`skill-arena/last_report.md`](skill-arena/last_report.md).

## Grep versus the legacy evaluator

The user's observation about grep applies to an optional **manual navigation instruction**, not to the benchmark retrieval algorithm.

The legacy consultation reference includes a fixed-string `rg` command as a fallback for manually searching concept Markdown. It recommends fixed strings so user text is not interpreted as a regular expression. The primary legacy package otherwise exposes exact ledger filters and read-only SPARQL, and it has no native ranked natural-language-search command.

For a fair ranked benchmark, `evaluate_retrieval.py` constructs an in-process `LegacyIndex`. It tokenizes each authoritative record's title and body, computes document frequency and smoothed inverse document frequency, applies log-scaled term frequency, and sorts by score and exact concept path. It does not invoke `grep`, `rg`, or another search subprocess. The evolved Harbor legacy compiler likewise uses deterministic ledger TF-IDF for its primary preparation workflow; its reference explicitly says this replaces ad hoc `rg` discovery for that workflow.

Therefore the reported legacy row measures deterministic TF-IDF retrieval over the authoritative ledger, not grep performance. The optional `rg` instruction was not removed from the historical baseline merely to alter this note.

## Insights and next decision

1. **Use evolved classical as the current mechanical primary, not as an unquestioned semantic winner.** It passes all gates and is strongest on selected rank quality, but its compact answers need an explicit semantic-coverage checklist before finalization.
2. **Keep evolved embeddings as a high-recall companion.** It improves Harbor reward on all three live questions and has the clearest all-around holdout gain. Its lexical route is also much faster than classical association or ensemble quality.
3. **Retain entity graph as a distinct synthesis route.** Its strong `q032` semantics and `78.3%` hard recall show real complementary value. Improve document/evidence coverage without discarding its entity-centric answer behavior.
4. **Do not promote adaptive in its current evolved form.** A single invalid evidence row is enough to fail the development gate, and its development semantics regress as well.
5. **Keep ensemble pending.** The treatment is promising on development and holdout, but the training regression, high cost, and unobservable baseline development hard-completeness gate prevent a clean promotion claim.
6. **Treat legacy promotion as compatibility evidence.** Its development and holdout contract repairs are real, but one failed training output and weaker 40-question retrieval make it a poor default when stronger alternatives exist.
7. **Add semantic coverage to the next evolution gate.** Evidence validity and claim-evidence coverage are necessary, but the observed divergences show they cannot substitute for answer-level claims, exclusions, and conditional logic.

## Limitations

- There is one live question per cohort and one accepted attempt per baseline/treatment cell. These results are diagnostic case studies, not statistically powered estimates, confidence intervals, or proof of universal superiority.
- Source documents overlap cohorts. The split prevents reusing question labels after candidate freeze, but it is not source-disjoint and does not make the public ground truth secret.
- The manual semantic reviews are separately validated and hash-bound, but they are still judgments against three questions, not an automated population metric.
- Evolved retrieval parity is intentional: the single evolution changed answer assembly, not retrieval. A later retrieval evolution would require a newly frozen benchmark cycle rather than reusing holdout feedback.
- Latency and token totals include agent reasoning, tool use, cold setup effects, and two 600-second timeouts. They should not be read as production service-level benchmarks.
- Network egress was not technically blocked on this host, despite the verifier's separate mount boundary and offline implementation.

## Final validation

The completed tree passed the following closure gates after the OKF projections were regenerated:

| Gate | Result |
|---|---:|
| Full repository test suite | `1607 passed` |
| Harbor evaluation tests | `38 passed` |
| Generated Harbor tasks | `40/40`, deterministic and leak checks passed |
| Benchmark ID and locator audit | Passed, including `46/46` unique evidence mappings |
| Independent semantic-review artifact validation | Passed for `q031`, `q032`, and `q034` |
| Standalone skill validation | Passed for all six evolved packages |
| Standalone runtime smoke | Passed for all six evolved packages |
| Application coverage gate | `90.9%` (`7504/8256` executable lines), threshold `80%` |

The coverage result comes from the required `python scripts/check_coverage.py --threshold 80` run, which exited successfully. The exact percentage was recomputed from that run's generated `.cover` files because the command runner did not return the captured text summary.

## Reproducibility index

| Artifact | Purpose |
|---|---|
| [`benchmark-manifest.json`](benchmark-manifest.json) | Frozen question hashes, counts, authority, and prompt-isolation boundary |
| [`campaign.json`](campaign.json) | Runtime, live cases, attempts, evolution limit, gates, and interpretation limit |
| [`runtime-manifest.json`](runtime-manifest.json) | Image, verifier, mount, authentication, and network bindings |
| [`campaign-bindings.json`](campaign-bindings.json) | Explicit accepted and excluded append-only run identities and hashes |
| [`reports/campaign-comparison.json`](reports/campaign-comparison.json) | Complete 36-trial, 18-pair Harbor comparison |
| [`reports/deterministic-40.json`](reports/deterministic-40.json) | Complete deterministic retrieval comparison over 40 questions and 20 routes |
| [`reports/benchmark-id-audit.json`](reports/benchmark-id-audit.json) | ID, crosswalk, qrel, locator, and real-grader mapping receipts |
| [`reports/q031-semantic-review.json`](reports/q031-semantic-review.json) | Training answer review |
| [`reports/q032-semantic-review.json`](reports/q032-semantic-review.json) | Development answer review |
| [`reports/q034-semantic-review.json`](reports/q034-semantic-review.json) | Frozen holdout answer review |
| [`skill-arena/`](skill-arena/) | Six direct control/treatment configurations and validation receipts |
| [ADR 0030](../../.specs/adr/0030-harbor-guided-single-evolution-consultation.md) | Durable architecture and evaluation decision |
