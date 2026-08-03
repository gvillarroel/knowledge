# Tika/MALLET/Tantivy consult-to-builder trace distillation

Date: 2026-07-27

## Evaluation

The consultation stage used Harbor 0.18.0 `consult-only` tasks over an immutable
15-paper Semantic OKF snapshot. Each task required a JSON answer grounded in exact
ledger evidence from a declared minimum number of independent papers. The verifier
checked response shape, evidence identities, hashes, locators, document minimums,
focus-set coverage, reciprocal-rank metrics, and the aggregate reward. Development
required all three selected tasks to reach `0.70` and every required mechanical gate.
Holdout stayed physically closed unless development passed.

The builder stage is a separate `build-consult` treatment. It mounts only the
evaluator-free 32-file raw input at `/dataset`, builds
`/workspace/knowledge`, validates that new snapshot, and then consults it with one
fixed consult skill. The prebuilt reference bundle is available only inside the
separate verifier environment.

## Consult selection

| Candidate | q006 | q007 | q008 | Mean | Development passes | Decision |
|---|---:|---:|---:|---:|---:|---|
| v39 | 0.7174 | 0.6608 | 0.7819 | 0.7200 | 2/3 | Frozen experimental builder control |
| v42 | 0.6522 | 0.9674 | 0.6302 | 0.7499 | 1/3 | Rejected |

v42 eliminated evidence-contract failures and substantially improved q007, but it
regressed the number of tasks above the required threshold. The frozen control is
therefore v39, digest
`sha256:2f22698579835f1c024fefee1071554618d644f87141e6a49d813a5ce58153cd`.
This is a confound-control selection, not a promotion. Its development gate failed,
the consultation holdout remained closed and unread, and the source skill was not
modified.

## Builder runtime and task correction

The Harbor 1.0 runtime was extended reproducibly from preserved image
`sha256:1315195d...aded5` with Debian
`openjdk-17-jdk-headless:amd64 17.0.19+10-1~deb12u2`. The qualified active image is
`sha256:f1fe60c2...6ec66`. It exports the canonical, non-symlink Java path and stable
read-only mount targets for Tika and MALLET. The real builder smoke test passed in
the container with Tika jar-tree digest `314729d4...1d45` and MALLET jar-tree digest
`733877cc...c729`.

The first generated build instruction named the registry's generic
`manifest.json`/`plan.json` convention even though this builder has two closed plan
inputs. No model call was made with that instruction. The append-only v43 task tree
instead names `ingestion-plan.json` and `retrieval-plan.json`; deterministic
regeneration, leakage checks, and all 40 oracle qualification gates passed. Its tree
digest is `6c2b7a36...bfb3`.

Harbor 0.18 drops a replacement skill represented as `Path` when another installed
skill remains a string. A local adapter stringifies all skill paths after the trace
distiller's substitution. A no-model `Job.create()` rehearsal proved that both the
candidate builder and frozen consult skill remained installed. The incomplete v44
attempt that exposed this defect was stopped and excluded from evaluation.

## Builder development result

The baseline and candidate used q009, q011, and q012 with zero retries, the same
OpenRouter model, the same v43 task checksums, the same runtime, and frozen consult
v39. Both builder arms produced the same authoritative records digest
`b64917f4...0805`; this confirms that downstream answer variation is not an
artifact-content change.

| Arm | q009 | q011 | q012 | Mean | Trials >= 0.70 | Mechanical gates |
|---|---:|---:|---:|---:|---:|---:|
| Builder baseline | 0.7370 | 0.4837 | 0.0000 | 0.4069 | 1/3 | 2/3 |
| Builder candidate v45 | 0.8637 | 0.3942 | 0.6454 | 0.6344 | 1/3 | 3/3 |

The candidate removed the observed `/usr/bin/java` symlink failures and made all
required mechanical gates pass, but only one task reached the required reward
threshold. The trace-distillation gate therefore failed at a 33.3% pass rate versus
the required 100%. Replay signatures matched, attempt independence was verified,
and there were no candidate errors or missing rewards. Holdout remained closed and
unread. The source builder skill was not modified.

This result also bounds the causal claim: the builder creates an identical snapshot,
while the verifier reward measures the complete build-and-consult answer. The
candidate's mean gain cannot be credited solely to the builder. Future builder
promotion should add direct verifier metrics for runtime preflight, build success,
validation, reproducibility, and snapshot digest before using downstream semantic
reward as a promotion gate.

## Evidence

- Frozen control:
  `canonical/graphrag-papers-40/frozen-consult-v39.json`
- v39 development gate:
  `generated/trace-distillation/20260727-consult-v39-promotion-gate-01/development-gate.json`
- v42 development gate:
  `generated/trace-distillation/20260727-consult-v42-promotion-gate-01/development-gate.json`
- Builder task tree:
  `evaluations/semantic-okf-datasets/generated/tasks/graphrag-papers-40/build-consult/tika-mallet-tantivy-v43`
- Runtime receipt:
  `runtime/runtime-build.json`
- Builder baseline:
  `evaluations/semantic-okf-datasets/results/20260727-tika-mallet-tantivy-v43-builder-discovery-baseline-01`
- Candidate development gate:
  `generated/trace-distillation/20260727-builder-v45-promotion-gate-01/development-gate.json`
- Closed holdout receipt:
  `generated/trace-distillation/20260727-builder-v45-promotion-gate-01/holdout-gate.json`
