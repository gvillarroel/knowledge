# Astro Semantic OKF Evaluation Conclusions

## Executive conclusion

All six build/consult families passed their double-build, validation, deterministic
rebuild, authoritative-core parity, read-only consultation, and evidence-validity
gates on the same frozen Astro corpus. The benchmark does **not** show one retrieval
route dominating every objective:

- embedding hybrid has the highest overall Recall@10 (90.4%);
- embedding lexical and hybrid tie for the highest hard-question Recall@10 (80.8%);
- classical/adaptive BM25 has the highest Recall@1 (59.6%) and MRR@10 (0.921);
- classical/adaptive association has the highest nDCG@10 (0.835); and
- ensemble `quality` is a strong governed compromise, with 89.6% Recall@10, 0.890
  MRR@10, 0.819 nDCG@10, 94.4% Recall@20, and 100% valid evidence.

The definitive operational recommendation is therefore the ensemble `quality`
policy with explicit validation and answer-completeness gates. This recommendation
is based on its protected candidate set, cross-route consensus, exact evidence
identity, and fail-closed behavior. It is not a claim that `quality` has the highest
number in every column. For latency-sensitive work, use the explicitly named `fast`
or `robust` policy and preserve the same evidence gates.

## Frozen source and integrity bindings

| Item | Accepted value |
| --- | --- |
| Official upstream | `https://github.com/withastro/docs.git` |
| Pinned commit | `5c37be52c5038e1174be1e838d3dd5852db26a21` |
| Selected root | `src/content/docs/en` |
| Selected content | 416 English `.mdx` files |
| Authoritative source bytes | 2,944,859 |
| Authoritative tree SHA-256 | `f287ff3b67b568db7fa90e871ce6c06d272f4e94ed0ec71d2eb365de261ae9bd` |
| Accepted ignored Know export | `tmp/astro-docs-know/exports/knowledge-export-20260716T085103Z.zip` |
| Know export bytes | 22,663,290 |
| Know export SHA-256 | `5a49689fb5775c5f03717cbc11af0389d1014082b9f4c44fd21e4a03ffe71bec` |
| Generated manifest SHA-256 | `eddee30248eceb76fec85ea0ff9f9e0666dd8801d6a5fead2125fbdaaf1141bd` |
| Common logical core SHA-256 | `b40abef5887a598063ca2979bb406dfc203c2fbef7c44ab30ec43544c17063e9` |
| Common semantic records SHA-256 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| Benchmark | 40 questions: 20 direct, 10 cross-document, 10 hard |
| Hard-answer ground truth | 50 atomic claims, 20 important negatives, 46 exact evidence sections across 21 pages |

The [acquisition manifest](corpus/acquisition-manifest.json) and
[input inventory](corpus/input-inventory.json) bind the acquisition. The pinned MDX
bytes are authoritative. Every index, embedding, graph, route score, qrel, and answer
score is derived and non-authoritative.

## Expected-ID and crosswalk audit

The expected IDs are meaningful, but they represent different namespaces:

- `document_id` is the canonical Astro English route, such as
  `/en/guides/endpoints/`;
- `source_id` is an opaque `astro-doc-<16 hex>` identity derived from the canonical
  route; and
- `record_id` is the source-scoped MDX record identity, such as
  `sources/mdx/guides/endpoints`.

The evaluator resolves hits only through the closed
[source crosswalk](corpus/source-combination.json). It first joins the exact
`(source_id, record_id)` pair to one `document_id`; its separately published
`source_id -> document_id` map is also checked for total one-to-one coverage.
It never infers identity from a filename, heading, title, or shared prefix.

The `required_document_ids` and `required_source_ids` arrays in hard ground truth are
independently sorted sets. They must not be zipped by position. Question `q040`
demonstrates why:

| `source_id` | Correct joined `document_id` | Meaning in `q040` |
| --- | --- | --- |
| `astro-doc-67458ae49afefc50` | `/en/guides/on-demand-rendering/` | Adapter, rendering mode, and cookies |
| `astro-doc-db7b41aee88b9016` | `/en/guides/endpoints/` | Request-time API endpoint |
| `astro-doc-ed7b0d0a27542ceb` | `/en/reference/routing-reference/` | Per-route `prerender` switch |

In the sorted document array, `/en/guides/endpoints/` comes first; in the sorted
source array, `astro-doc-67458ae49afefc50` comes first. Positional zipping would
therefore swap the first two identities. The independent validator re-derives all
416 identities, exact joins, locators, selected-text hashes, and hard-question
bindings. The accepted evaluation passes that audit.

## Build comparison

Each family was built twice from the same manifest. `Mean build ms` is the arithmetic
mean of the two measured builder subprocess wall times. It is not query latency.

| Family | Build | Validation | Deterministic bundle | Deterministic core | Core parity | Mean build ms |
| --- | --- | --- | --- | --- | --- | ---: |
| legacy | pass | pass | pass | pass | pass | 13,386.8 |
| embeddings | pass | pass | pass | pass | pass | 232,249.1 |
| classical | pass | pass | pass | pass | pass | 24,183.9 |
| adaptive | pass | pass | pass | pass | pass | 24,698.2 |
| entity-graph | pass | pass | pass | pass | pass | 42,479.9 |
| ensemble | pass | pass | pass | pass | pass | 334,528.9 |

The ensemble is the most expensive build because it materializes and hash-binds its
adaptive, lexical, graph, embedding, and identity-crosswalk components. That cost is
paid at publication time; it does not weaken the common authoritative core.

Machine-readable detail: [build comparison JSON](reports/build-comparison.json).
Readable compact report: [build comparison Markdown](reports/build-comparison.md).

## Retrieval comparison

The following table reports the selected representative route for each family over
all 40 questions. Recall is macro-averaged over the evaluator-owned relevant-document
sets. MRR measures how early the first relevant document appears, while nDCG rewards
ordering all relevant documents near the top. `Hard Recall@10` uses only the 10 hard
questions. Evidence validity independently reconstructs every returned authoritative
record and verifies its locator/hash binding.

| Family | Representative route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Standalone mean ms | Standalone p95 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | `legacy_tfidf` | 82.3% | 71.7% | 0.706 | 0.685 | 100.0% | 1.9 | 3.6 |
| embeddings | `lexical` | 89.8% | 80.8% | 0.812 | 0.783 | 100.0% | 99.1 | 107.8 |
| classical | `association` | 88.8% | 74.2% | 0.915 | 0.835 | 100.0% | 1,327.6 | 1,430.1 |
| adaptive | `association` | 88.8% | 74.2% | 0.915 | 0.835 | 100.0% | 1,341.0 | 1,443.6 |
| entity-graph | `entity` | 88.1% | 78.3% | 0.729 | 0.706 | 100.0% | 1,152.2 | 1,626.6 |
| ensemble | `quality` | 89.6% | 77.5% | 0.890 | 0.819 | 100.0% | 6,770.2 | 10,938.4 |

No route dominates the full metric vector. Important complementary results from the
20 executed routes are:

| Objective | Best observed route(s) | Result |
| --- | --- | ---: |
| Overall Recall@10 | embeddings `hybrid` | 90.4% |
| Hard Recall@10 | embeddings `lexical` and `hybrid` | 80.8% |
| Recall@1 | classical/adaptive `bm25` | 59.6% |
| MRR@10 | classical/adaptive `bm25` | 0.921 |
| nDCG@10 | classical/adaptive `association` | 0.835 |
| Recall@20 | embeddings `hybrid` | 94.6% |
| Evidence validity | every executed route | 100.0% |

The family table uses a second standalone timing pass for only the representative
route, one question at a time and without sibling-route cache priming. Those numbers
are comparable within this machine/run. The all-route report also contains
query-major *marginal* timings. Later sibling routes can reuse bounded warm
computation, so marginal figures are diagnostic and must not be compared as cold or
standalone latency. One-time deep validation, model setup, and CLI inspection are
reported separately and excluded from both query timing columns.

Machine-readable detail: [retrieval comparison JSON](reports/retrieval-comparison.json).
All-route table and timing note: [retrieval comparison Markdown](reports/retrieval-comparison.md).

## Hard-question answer evidence

These results are deterministic, ground-truth-blind extractive answer packs over the
10 hard questions. They use each family's own valid ranked passages, no language
model, and no MCP. They measure whether the selected passages are sufficient to
support the curated answer; they are not semantic-judge scores and do not measure
prose fluency.

| Family | Answer route | Retrieval representative | Atomic evidence | Required documents | Exact evidence spans | Important negatives | Grounding | Evidence valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | `legacy_tfidf` | `legacy_tfidf` | 66.0% | 74.2% | 68.0% | 75.0% | 100.0% | 100.0% |
| embeddings | `hybrid` | `lexical` | 0.0% | 84.2% | 7.0% | 0.0% | 100.0% | 100.0% |
| classical | `bm25` | `association` | 66.0% | 77.5% | 68.0% | 75.0% | 100.0% | 100.0% |
| adaptive | `bm25` | `association` | 66.0% | 77.5% | 68.0% | 75.0% | 100.0% | 100.0% |
| entity-graph | `entity` | `entity` | 0.0% | 78.3% | 0.0% | 0.0% | 100.0% | 100.0% |
| ensemble | `quality` | `quality` | 66.0% | 77.5% | 68.0% | 75.0% | 100.0% | 100.0% |

Interpret these columns narrowly:

- `Required documents` asks whether the selected pack contains each required page.
- `Exact evidence spans` asks whether a selected passage fully contains each exact
  curated character range.
- `Atomic evidence` gives a claim credit only when every evidence ID required by
  that claim is covered.
- `Important negatives` applies the same all-required-evidence rule to exclusions or
  failure conditions.
- `Grounding = 100%` means each selected extract has a valid evidence binding.
- `Evidence valid = 100%` means those bindings reconstruct and hash correctly.

Consequently, 100% grounding and evidence validity do **not** mean that an answer is
complete or semantically correct. Conversely, an atomic score of 0% does not prove
that every sentence is false. It can mean the retriever reached the right page but
selected a narrower or different exact span. This is visible in `q040`: entity graph
retrieved all three required documents (100% document coverage) but none of its
selected passages fully enclosed the five curated evidence ranges, so its exact-span
and atomic scores were 0%.

The `q040` diagnostic reinforces the distinction:

| Family | Atomic evidence | Required documents | Exact evidence spans | Important negatives |
| --- | ---: | ---: | ---: | ---: |
| legacy | 60.0% | 66.7% | 80.0% | 100.0% |
| embeddings | 0.0% | 66.7% | 20.0% | 0.0% |
| classical | 60.0% | 66.7% | 80.0% | 100.0% |
| adaptive | 60.0% | 66.7% | 80.0% | 100.0% |
| entity-graph | 0.0% | 100.0% | 0.0% | 0.0% |
| ensemble | 60.0% | 66.7% | 80.0% | 100.0% |

For reference, the audited answer to `q040` is: keep Astro's static output default;
install the deployment adapter for the target host; export `prerender = false` only
from the cookie-aware account page and the request-time endpoint; read
`Astro.cookies` only at request time; export the required endpoint HTTP handlers and
use the incoming `Request`/`params`; and leave all other routes prerendered. If
`output: 'server'` becomes the default, invert the exception by exporting
`prerender = true` from routes that must remain build-time static. Installing an
adapter alone does not make every route dynamic, and request-specific cookies do not
exist during build-time prerendering.

Machine-readable detail: [hard-answer comparison JSON](reports/hard-answer-comparison.json).
All actual extracts for `q040`: [hard-answer comparison Markdown](reports/hard-answer-comparison.md).

The independent manual rerun used the selected route from each family twice, validated
every returned locator and hash, and hashed each bundle before and after consultation.
All six rankings and evidence signatures were deterministic, every checked hit was
valid, and every bundle remained unchanged. At Recall@10 over the three required
`q040` documents, embeddings lexical and entity graph reached 100%; the other four
selected routes reached 66.7%. This larger candidate check does not contradict the
narrow exact-span answer-pack table above. See [manual query verification](reports/manual-query-verification.md).

## Actual q040 answers from every consultation family

Six final live Skill Arena runs asked the same model the same difficult `q040`
question over the corresponding frozen bundle. Each family remained an isolated
control/treatment pair; the rows below are descriptive across pairs and are not an
all-skills causal portfolio. The independent evidence audit reconstructs identities,
paths, locators, and hashes from the authoritative ledger instead of trusting a
Promptfoo shape assertion.

| Treatment | Promptfoo contract | Authoritative evidence | Manual answer audit | Important observation |
| --- | ---: | ---: | --- | --- |
| legacy | fail | fail | substantively complete | Correct prose, but legacy evidence added forbidden fields and encoded locators as strings. |
| embeddings | pass | fail | substantively complete | Two rows used the nonexistent source ID `astro-doc-67458ae49efafc50`; shape validation alone missed the typo. |
| classical | pass | pass | substantively complete | Strict JSON and all cited records reconstruct exactly. |
| adaptive | pass | pass | substantively complete | Strict JSON and all cited records reconstruct exactly. |
| entity graph | fail | pass | substantively complete | The recoverable answer had an extra trailing brace; its five evidence rows themselves are authoritative and exact. |
| ensemble | pass | pass | substantively complete | The source-generic finalizer produced strict contract-compliant output with exact evidence. |

The paired control/treatment pass rates were, respectively: legacy 0%/0%, embeddings
100%/100%, classical 100%/100%, adaptive 0%/100%, entity graph 0%/0%, and ensemble
0%/100%. Control outcomes vary because these are separate live model executions;
only the delta inside an individual pair has the intended isolation. A pass also does
not establish evidence validity: embeddings is the concrete counterexample.

All six treatment summaries reached the same audited technical conclusion: keep the
static default and install the target runtime adapter; set `prerender = false` only
on the account page and live API endpoint; use request-time cookies on the account
page; export endpoint HTTP handlers that return `Response`; and leave the remaining
routes prerendered. Under `output: 'server'`, dynamic rendering becomes the default,
so static exceptions use `prerender = true` and the two dynamic routes no longer need
an explicit `false`.

The exact parsed answers, per-assertion results, timings, artifact hashes, and every
evidence-validation failure are preserved in the
[six-family q040 report](reports/skill-arena-q040-comparison.md) and its
[machine-readable form](reports/skill-arena-q040-comparison.json).

## Isolated Skill Arena q040 diagnostic

The final isolated same-model, same-bundle run `eval-EG6-2026-07-16T11:38:39`
produced the intended causal contrast:

| Profile | Pass rate | Time | Interpretation |
| --- | ---: | ---: | --- |
| knowledge-only control | 0/1 (0%) | 114,571 ms | Failed the response/grounding contract |
| definitive ensemble treatment | 1/1 (100%) | 271,042 ms | Passed JSON, response-contract, and grounded-answer assertions |

The treatment used only `consult-semantic-okf-ensemble`, returned a 160-320 word
answer with five grounded claims, and let the deterministic finalizer construct five
exact evidence rows. Its answer covered static output, a server adapter, per-route
`prerender = false`, request-time cookies, a request-time endpoint, and the inverse
`output: 'server'`/`prerender = true` design. Skill Arena labels the overall two-cell
run `FAILED` because the control cell failed; that aggregate status does not mean the
treatment failed. The causal delta is +100 percentage points for this one question.

This is a development diagnostic, not an untouched holdout: three earlier q040 runs
exposed, respectively, an unavailable claimless finalizer, an overly difficult exact-
quote handoff, and a model-side field-placement error. Those failures drove the
source-generic `answer-brief`, hash-bound support IDs, and byte-for-byte final-output
gate. They are not counted as independent trials or hidden by averaging. The accepted
run is bound in [the compact Skill Arena report](reports/skill-arena-q040-ensemble.md).

## Frozen post-tuning q039 holdout

After the definitive ensemble skill and its q040 finalizer were frozen, one separate
q039 hard question was executed as a same-model, same-bundle control/treatment
holdout. The prompt covered processed module deduplication, `is:inline`,
`data-astro-rerun`, ClientRouter lifecycle events, and persistent listener guards,
without exposing qrels, expected source IDs, routes, or answer claims. No skill change
was made after reading the result.

| Profile | Contract | Evidence valid | Required docs | Exact spans | Atomic claims | Negatives | Time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| knowledge-only control | pass | 3/3 | 100% | 100% | 100% | 100% | 75,842 ms |
| ensemble treatment | pass | 3/3 | 66.7% | 75% | 80% | 100% | 162,166 ms |

Both cells passed, so the causal delta is 0 percentage points. This is useful
contract-level and evidence-validity no-regression evidence, but not exact benchmark
sufficiency parity and **not** evidence that the skill outperformed the already
successful control. The treatment manually covers every requested facet with valid
authoritative evidence; however, it cites the Astro transitions module instead of the
curated directives-reference span. The strict evidence-first scorer therefore gives
it 3/4 exact spans and 4/5 atomic claim groups, while preserving full important-
negative coverage. There was exactly one completed live evaluation; two preceding
compare directories were dry-runs and one was an incomplete preflight with no model
evaluation. The accepted result is
`eval-jIy-2026-07-16T11:59:52` in run
`2026-07-16T11-59-44-962Z-compare`.

See the [checked q039 holdout report](reports/skill-arena-q039-holdout.md), its
[machine-readable result](reports/skill-arena-q039-holdout.json), and the frozen
[holdout manifest](skill-arena/q039-ensemble-holdout-manifest.json).

## Definitive ensemble policy and quality gates

Use the ensemble `quality` policy as the default when the pinned offline embedding
runtime is available and its measured latency is acceptable. Apply these gates in
order:

1. Deep-validate the bundle. Reject core drift, component-hash drift, crosswalk gaps,
   stale model revisions, invalid paths, invalid locators, or text-hash mismatch.
2. Inspect the exact source-record identity crosswalk, `candidate_set_gate`,
   `promotion_gate`, and component route rankings. A consensus score remains derived
   discovery metadata, not evidence.
3. Decompose a multi-part question into explicit answer facets. Require at least one
   independently valid authoritative passage for every asserted facet, comparison,
   condition, and important negative.
4. Open the authoritative concept/source path and verify the exact locator and text
   hash before using a statement.
5. If a facet remains unsupported, retry with focused subqueries and a larger bounded
   `evidence-pack`. If the gap remains, mark it partial or unresolved; do not fill it
   from model memory.
6. For a claimless generic bundle such as this Astro snapshot, do not fabricate claim
   IDs or paper citations. Use the source-generic finalizer: the bounded full-query
   answer brief assigns hash-bound support IDs to exact facet-ranked passages, and each
   atomic claim names only those IDs. The CLI rebuilds the brief and constructs exact paths, locators, hashes,
   and evidence indices. Claim-only coverage remains available only with reviewed
   answer bindings.
7. Use `fast` when the embedding runtime or latency budget prevents `quality`, and
   `robust` when reproducing the protected adaptive order. Label the policy used.

This gate is the practical advantage of the definitive ensemble: it combines
complementary retrieval signals while making incomplete evidence visible and failing
closed on integrity errors. It cannot guarantee that one fixed ranking wins every
future corpus or every metric.

## No-MCP boundary and legacy `grep` finding

No MCP server, transport, or runtime participates in the accepted Astro acquisition,
build, validation, retrieval, or answer-pack experiment. Know acquired the pinned Git
repository through its local CLI adapter. The definitive ensemble consultant is also
CLI-only. The frozen Astro corpus contains a page describing Astro's own Docs MCP
service, but that text is authoritative benchmark content, not an enabled connector.

The legacy `grep` observation is correct only at the instruction layer. Legacy
consultation documentation includes an optional manual `rg` fixed-string discovery
example. The legacy builder and query CLI do not launch `grep` or `rg`. Because the
legacy CLI has no ranked natural-language-search command, the Astro direct benchmark
uses an evaluator-side deterministic in-memory TF-IDF implementation. Its
`legacy_tfidf` metrics therefore do not measure the documented manual `rg` workflow.
The legacy package was not modified to change this finding. See the separate
[legacy grep/rg investigation](LEGACY-GREP-INVESTIGATION.md).

## Reproduction

Run from the repository root in PowerShell. The following keeps the new large run
append-only and ignored; it writes candidate compact reports inside that run for
review rather than overwriting the checked accepted reports.

```powershell
$env:PYTHONPATH = (Resolve-Path src).Path
$python = (Resolve-Path .venv/Scripts/python.exe).Path
$runId = "astro-reproduction-$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))"
$runDir = "evaluations/semantic-okf-astro/results/runs/$runId"

& $python evaluations/semantic-okf-astro/scripts/prepare_corpus.py --check --json
& $python evaluations/semantic-okf-astro/scripts/validate_evaluation.py --json

& $python evaluations/semantic-okf-astro/scripts/run_builds.py `
  --run-id $runId --python $python `
  --report "$runDir/build-comparison.json" `
  --markdown "$runDir/build-comparison.md"

& $python evaluations/semantic-okf-astro/scripts/evaluate_retrieval.py `
  --run-dir $runDir --python $python --timeout 300 `
  --raw-output "$runDir/retrieval/detailed-report.json" `
  --compact-json "$runDir/retrieval/compact-report.json" `
  --compact-markdown "$runDir/retrieval/compact-report.md"

& $python evaluations/semantic-okf-astro/scripts/compare_hard_answers.py `
  --run-dir $runDir `
  --retrieval-report "$runDir/retrieval/detailed-report.json" `
  --output-json "$runDir/answers/hard-answer-comparison.json" `
  --output-markdown "$runDir/answers/hard-answer-comparison.md"
```

Validate the benchmark and focused implementation contracts:

```powershell
& $python -m pytest tests/test_semantic_okf_astro_evaluation.py -q
& $python evaluations/semantic-okf-astro/scripts/generate_skill_arena_configs.py
& $python evaluations/semantic-okf-astro/scripts/generate_q039_ensemble_holdout.py --check
skill-arena val-conf evaluations/semantic-okf-astro/skill-arena/q040-ensemble-paired.yaml
skill-arena val-conf evaluations/semantic-okf-astro/skill-arena/q039-ensemble-holdout.yaml
```

When the accepted append-only raw Skill Arena directories are retained locally,
`summarize_q040_skill_arena.py --check` and `summarize_q039_holdout.py --check`
byte-check the compact live-answer reports against those raw artifacts. The checked
repository retains the compact build, retrieval, answer, manual-query, all-family
q040, ensemble q040, and q039 holdout reports linked above. The accepted detailed
build/retrieval run is
`evaluations/semantic-okf-astro/results/runs/20260716-astro-generic-01`; it remains
ignored and append-only.
