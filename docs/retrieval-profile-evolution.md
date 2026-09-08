# Evolving retrieval construction profiles

Use the [evaluation workspace](../evaluations/skill-evolution/README.md) to compare
explicit construction changes while keeping the source content, query workload,
authoritative evidence identities, and consultation implementations fixed.
The workflow uses native Harbor and the maintained authoring, organizing,
realization, reflective Pareto, and result-reporting skills.

## Scope and isolation

The baseline is a clean complete copy of
`skills/build-semantic-okf-knowledge-skill/`. It vendors the eight canonical
builder/consultant pairs. The experiment executes those builders and validators
directly. It imports the staged native consultants for most retrieval routes;
Legacy lexical and Turso SQL ranking retain the existing frozen comparators.
The public expert generator is verified separately with synthetic inputs.

Only four exact candidate paths may change: `SKILL.md`,
`scripts/apply_retrieval_profile.py`, `assets/retrieval-profile.json`, and
`references/retrieval-profile.md`. The profile transformation changes supported
retrieval parameters in a copy of the supplied plan. It preserves source
selection, chunking, authoritative records, identity grouping, and evidence
policies. The matched builder remains responsible for closed-plan validation.

The initial operations have the following actual plan scope, checked by applying
the fixed helper to source-generic plans. A family outside the listed scope is
an unchanged control within that profile, not an unsuccessful transformation.

| Profile | Plan change | Affected families |
|---|---|---|
| `neural-record` | Hashing to the pinned local MiniLM model, keeping record chunks | Embeddings, Ensemble |
| `quarter-expansion` | Multiply existing association and topic weights by 0.25 | Classical, Adaptive, Ensemble |
| `bm25-low-b` | Set existing BM25 length normalization to 0.25 | Classical, Adaptive, Entity Graph, Ensemble |
| `stronger-titles` | Set an existing separate title weight to 4.0 | Classical, Adaptive, Ensemble |

Legacy, Graphify and Turso are unchanged controls in all four profiles. They
remain in the predeclared 32-cell score and complete native execution matrix.

Historical EnterpriseRAG, Astro, architecture-book, and data-science workloads
are development-only. Never reuse protected GraphRAG or contradiction cohorts
for tuning. The current independent gate uses two newly selected BEIR-derived
source families. Their small reference-enriched slices support a bounded transfer
check, with unresolved public/pretraining exposure and no significance claim.

The host curator/controller is trusted; ignored directories are not an access
control mechanism. Candidate execution receives only its current evaluator-free
corpus, queries, exact staged skill, and read-only local model cache. Both native
Docker environments have `network_mode: none`. The separate verifier alone
mounts its task-local `/tests` read-only. Agent setup and verifier startup reject
any interface beyond loopback. On the current Docker kernel, the standard Harbor
dynamic egress sidecar lacks required nftables FIB support, so independently
verified native Compose definitions enforce this fixed physical boundary.

## Prepare a new campaign

The current scripts bind one explicit campaign directory through the reviewed
constants in `prepare_experiment.py`. Existing outputs are not restart targets.
A changed sampling rule, task contract, environment, hypothesis budget, or
acceptance rule requires a new reviewed campaign identity. Preserve failed
preparation versions and all first-evaluable execution evidence.

The current Windows/WSL preparation uses the short ignored `tmp/e5/` namespace.
Preserve both earlier campaigns: `20260906-r2` failed during native mounted
artifact collection, and `e3` exposed a CRLF verifier entrypoint and a genuine
Graphify repeated-build defect. Neither produced a valid retrieval score or
released private validation. Their incomplete jobs and stop receipts remain
separate evidence with their original failures.

Preserve e4 as well: all 32 native baseline trials completed with integrity,
but the owning controller rejected the null configured agent name against the
observed `skill-retrieval` identity. Its scores are retrospective diagnostics,
not an accepted evolution archive. No candidate or private gate ran.
[ADR 0119](../.specs/adr/0119-declare-native-agent-identity-and-qualify-the-owning-controller.md)
requires explicit truthful agent identity in both JobConfigs and an independent
native smoke that completes the owning controller's baseline, candidate and
archive path before the next design seal. Keep the implementation and predeclared
experiment unchanged; never repair the earlier native artifacts in place.

[ADR 0118](../.specs/adr/0118-normalize-empty-graphify-heading-identities-before-profile-evolution.md)
qualifies a source-generic empty-heading identity repair before freezing the new
Graphify baseline. All profile candidates share that correction, so it cannot
be credited to one retrieval profile. Task generation now writes explicit LF
shell bytes. Require an independent native smoke using the actual generated
tasks without rewriting their files, concurrent trials, and production cleanup.
Keep native output paths short. Reuse the exact unconsumed source portfolio and
seeds, with fresh task contracts and an independent review of the corrected
baseline. This is a new study, not a selective recovery of the failed jobs.

1. Read the playbook, authoring contract, organizer contract, independent-validation
   ADR, owning evolver, and candidate-realization contract.
2. Freeze a clean baseline, local runtime image digest, model snapshot and
   source manifests. The learned profile uses the exact local MiniLM revision
   declared in `proposal-grid.json`; it cannot download or substitute a model.
3. Materialize evaluator-free inputs and keep references in the curator area.
   Reference construction normalizes source identities; it does not run a
   candidate. Run `neutralize_inputs.py` exactly once on the fresh campaign before
   building reference identities: it applies uniform collection metadata and
   opaque query IDs while preserving texts and relevance membership. It is not a
   restart command. Preserve upstream archive hashes and document pre-seal fixes.
4. Create the private authoring blueprint/seeds and replay it with the maintained
   task planner. Related historical annotation families stay on one side of the
   boundary. Seeded output names and directories vary independently of relevance.
5. Emit native tasks from the plan. Require exact source-tree and query-projection
   bindings, no undeclared input files, and stable runtime image resolution.
6. Run `audit_datasets.py`, the focused regression suites, and an actual native
   synthetic forward test. A successful command exit is insufficient: inspect
   native completion, reward coverage, errors, skill locks, and physical mounts.
7. Register actual task roots and downstream validation with the organizer.
   Have an independent curator inspect private validation and issue supported
   quality receipts. Seal only after protocol, job templates, complete input
   bindings, baseline, review evidence, and all dataset locks agree.

The preparers are deliberately separate from the optimizer. Do not display
private validation task names, questions, labels, detailed diagnostics or
trajectories to the candidate-generation role.

## Realize and compare candidates

After the design seal, `realize_profiles.py` invokes the maintained realizer to
prepare, validate, seal, and verify four complete isolated packages. Its trusted
validation commands inspect only synthetic plans and package structure. Their
receipts do not establish improved fitness.

`run_search.py prepare` writes an ordinary configuration for the maintained
reflective Pareto controller. Run its `dry-run` and `doctor` modes before the
`development` invocation. Every entry point verifies the native organizer's
ledger, source and seal commitments, task bytes, job templates, orchestration
files, offline model weights and baseline package. Every generation rejects
development after a private gate release. Validation requires the exact released
candidate and a still-planned gate, which is transitioned before dispatch.
It launches native Harbor under WSL, with two concurrent
trials, two numerical threads, fixed CPU/memory limits, one attempt, zero retries,
and local caches. The baseline runs first. Every trial builds twice, independently
validates both outputs, checks exact byte equality, searches every declared route,
and proves the skill/knowledge trees stayed unchanged.

The verifier binds every record's ID, digest, source, concept, and physical path
against independent authoritative identities. It checks the expected queries,
rank order, cutoff, unique hits, imported consultant hashes, frozen package files,
finite measurements, P95 consistency, and the declared zero-model execution
scope. Native Harbor locks and the owning controller establish the exact staged
candidate provenance; submitted file attestations alone are insufficient.

Only development evidence can drive complementary merges. Generation one is
optional and requires parents in the previous native Pareto archive, supported
non-conflicting operations, and unchanged budget/profile commitments. Keep
unqualified candidates and failed native trials visible in diagnostics.

[ADR 0120](../.specs/adr/0120-preflight-native-profile-and-complete-merge-lineage.md)
requires the complete native merge-plan order to match the sealed archive's
complementary pairs before applying the four-child limit. A native generation
seal does not cover `mergePlans`; package digests alone also do not establish
unchanged acceptance rules. Use the installed owner's exact profile and
previous-generation checks before native dispatch. Preserve the archived parent
digests and exact operation unions, and reject baseline-plus-candidate pairs
that would merely rerun an existing profile. These preparation checks neither
score new cases nor change the frozen protocol.

## Freeze, validate, and publish

The [campaign helper source archive](../evaluations/skill-evolution/campaign-tools/README.md)
contains exact copies of the four e5 workspace helpers and a SHA-256 manifest.
It makes native report normalization, supported merge preparation and completed
generation registration reviewable alongside the experiment code. The merge
preparer's archived bytes match its independent qualification and actual
generation-one execution.

These scripts derive imports and output locations from `tmp/e5`; use that
registered runtime placement. Restore a missing helper from the source archive
only after matching its manifest hash. Preserve an existing file and reject a
hash mismatch. The helpers retain their create-only outputs and stage guards:
restoring code does not authorize replaying a completed job, overwriting a
report, releasing a private gate or changing a frozen candidate. New experiments
still require a separately registered design and fresh private verification.

Choose one qualified development finalist using the frozen rule. If the required
development gain is absent, retain baseline and keep validation sealed. Otherwise
record its exact package as candidate evidence, complete evolution, and release
the whole validation portfolio once through the organizer. The owning controller's
`holdout` phase implements this study's mandatory independent validation.

### Compare both generations

E5 stopped after a runtime interruption at 319 / 320 native development results.
Its actual endpoint is the [interrupted observed-evidence catalog](../evaluations/reports/evolution/e5/interrupted-development-001/README.md).
The complete-generation command below remains a guarded path; do not run it for
e5's absent final native archive. See [ADR 0121](../.specs/adr/0121-preserve-interrupted-evolution-without-manufacturing-completion.md).

For e5, first complete native normalization, visual review and immutable report
registration for both generations. Then run:

```powershell
python -B evaluations/skill-evolution/aggregate_campaign.py
```

The combined `evaluations/reports/evolution/e5/comparison/` catalog preserves ten
measured runs of nine distinct profiles. It includes all routes and failed
denominators, views by dataset and skill, and per-cell CTA measurements. The two
baseline measurements keep their generation identities; no grand mean or pooled
P95 is invented. Unknown payload fields are excluded from the exported rows.
The reporter requires the same registered comparison profile, hardware snapshot,
route grid and quality scale, and stops after private release or terminal evolution.

Register the reviewed combined directory as public report evidence on the running
evolution stage before selection and validation. Its cross-generation maxima are
descriptive. They do not create a combined native archive, carry an earlier
candidate into the final archive, or replace the predeclared finalist rule.
See the [source and workflow overview](../evaluations/skill-evolution/README.md).

### Close an interrupted generation

Preserve the native controller log, every original job and the stopped runtime
observation. A missing TrialResult is unavailable evidence, not permission to
fill a reward, repeat a task, or mark the root complete. Use the exact installed
external-failure recovery contract only when its positive eligibility and
provenance predicates apply.

For the e5 interruption, the [archived normalization helper](../evaluations/skill-evolution/campaign-tools/normalize_interruption.py)
invokes the native reporter separately for four complete comparable jobs and one
partial diagnostic job. Its `--allow-incomplete` report does not compare that
partial mean with complete profiles. Then `aggregate_interruption.py` publishes
the observed cross-generation catalog while leaving the complete-generation
reporter and final-archive rule unchanged. Both steps are create-only and already
executed; preserve their outputs rather than replaying them.

Review and register the observed native sources, public catalog, independent
workflow review and interruption decision before stopping the active evolution
stage and its unused planned gates. Do not complete a stage that did not finish,
open private validation without the required finalist, or treat historical
secondary analysis as a prospectively registered successor study. Native
analysis-only support does not establish permission to change the frozen
selection population after results are known.

Evolution report Git attributes preserve the exact bytes used by SHA-256
commitments across checkouts. Do not normalize already registered reports or
place new metadata inside a sealed report directory.

### Apply the terminal selection rule

After the final development archive is complete, `report_selection.py
--generation N` publishes an audit of the predeclared rule: greatest native
aggregate mean, fewer cell regressions against baseline, fewer profile
operations, then lexical candidate ID. It checks complete qualification and
all 32 cells, and asks the installed owner to verify the archive seal and exact
finalist/profile binding. It does not compute task scores, run a job, create a
candidate, release validation or promote a package. Preserve its source-bound
decision before completing evolution; an earlier archive cannot replace an
already started later generation.

Do not tune, merge, reselect, retry semantic outcomes, or reopen the gate after
release. A failure is terminal for that study. Preserve experimental options
without describing them as promoted defaults.

Normalize completed jobs with `harbor-run-results` before publishing reviewed
aggregate comparisons. Report dataset-specific default-route and all-route
results, missing/error denominators, nDCG/recall/MRR, construction time, query P95,
storage, and actual model-call accounting. Keep local runtime costs distinct from
provider billing. Native trial token and billing totals exclude assistant-based
research, authoring, review and orchestration; do not present them as a complete
development-cost estimate. Do not combine these results with official EnterpriseRAG
answer-quality scores or historical runs under different protocols.

Run the repository coverage gate and inspect both the test summary and total:

```powershell
python scripts/check_coverage.py --threshold 80
```

Keep test temporary directories inside the workspace when configuring a fresh
test invocation. Before any authorized publication, check data-ignore policy,
links, generated report consistency, source bindings, and the explicit diff.

[Documentation index](README.md) · [Evolution roadmap](knowledge-skill-evolution-roadmap.md)
