# EnterpriseRAG: isolated finite evolution

The runner in `evaluations/enterprise_isolated_evolution/` implements the
remaining finite Entity Graph and Ensemble search, all-family replay, exact
selection, all-500 comparison and one independent private acceptance. The six
completed family catalogs remain closed. Its architecture is recorded in
[ADR 0165](../.specs/adr/0165-isolate-the-frozen-enterprise-evolution-planner.md).

## Evidence boundaries

The deterministic planner is the sole component that can propose, retain,
rank or stop candidates. Its input consists of the precommitted public plan
and qualified native development observations. The trusted host broker
executes fixed operations; it does not introduce new candidate choices.

The optimizer runs with a read-only root and exact code mount, no network,
unprivileged UID/GID, no capabilities, private namespaces, bounded temporary
storage, no Docker log archive, and irreversible process restrictions. The
launcher checks the actual created container before starting it. No model
session, credentials, task registry, corpus, prior transcript, evaluation cache
or private validation content is mounted into that process.

The host can still control Docker and access its own workspace. Host-side
adaptive changes after the policy freeze would violate this architecture.
Independent review binds the complete runtime, source packages, data locks,
executor controls, mutation catalog, budgets and downstream acceptance recipe.

Native task containers also disable network and privileges, use a read-only
root and allocate a fresh anonymous disk volume for the generated knowledge.
The volume is removed with its container. A source-pinned wrapper isolates the
agent's `/logs/verifier` mount while preserving the separate verifier's own
results bind. Both public and private workers install the same policy before
loading Harbor's owner. This fixes a shared feedback mount in the inspected
Harbor 0.18.0 source without changing its installed files, scorer, CPU, memory
or timeout limits. Synthetic probes must verify real uploads and artifact
transfer, subprocess execution, denied access and volume cleanup.

The planner exits before all-500 comparison. Private acceptance follows a
successful complete comparison, unless the selected bundle is unchanged, in
which case private data stays unopened. The broker accepts only fixed boolean,
digest and decision fields from the private authority; it never copies arbitrary
private diagnostic text into aggregate reports.

## Fixed execution stages

1. Qualify each exact corrected implementation once. A first measurement
   establishes a reference and does not claim improvement over a failed run.
2. Visit the inherited finite catalog with three consecutive evaluable misses
   per mechanism. Reset that counter on a strict improvement, skip duplicate
   profiles, preserve nontransferable cumulative caps and stop after a complete
   round without improvement or the five-round limit.
3. Run the reference and selected compositions on eight public development
   tasks each. Require exact reproduction of the individually retained scores.
4. Emit one archive-bound selection and terminate the optimizer permanently.
5. Recalculate reference and frozen bundles on all 500 public questions,
   with eight tasks per arm. Require qualification before admitting the next arm.
6. For a changed candidate, run the registered private comparison once:
   two arms, eight families, two independent groups per family. Require native
   qualification, strict aggregate gain and nonnegative paired family means.
7. Draft source-linked aggregates for independent publication review. Installing
   a canonical skill remains a separate action gated by the accepted evidence.

There are at most two native jobs in flight during family development. Joint,
recalculation and private arms are sequential, each with two concurrent trials.
All attempts are single-shot; original errors remain recorded. The durable
journal refuses an implicit restart or a repeated native identity.

## Preparation and execution

Read [the knowledge skill evolution playbook](knowledge-skill-evolution-playbook.md)
and the maintained organizer and owning evolution contracts before preparing a
new study. Windows hosts the broker and organizer; Linux/WSL runs Harbor 0.18.0
against already available, pinned Docker images and the existing local model
snapshot. No benchmark model calls or network downloads are part of this run.

Public preparation creates an exclusive destination and never grants admission:

```powershell
python -B -m evaluations.enterprise_isolated_evolution.prepare tmp/e16 --curator-source evaluations/enterprise_isolated_evolution/curator_authority.py
```

Preparation imports only terminal development evidence, constructs the exact
reference composition, versions the eighteen public task roles and records
complete source commitments, including the future installed authority's exact
bytes. Omitting `--curator-source` supports public rehearsal only and cannot
pass admission. Within the one public registry, qualification,
joint replay and all-500 roles intentionally overlap; they are not independent
validation datasets. The optimizer receives no all-500 payloads or feedback.

The independent curator must review the final sources, verify the actual
optimizer and task-executor denial probes, create fresh sealed validation,
register disjoint datasets, declare ordered stages, seal the design, and open
development. Only then may the complete runner start:

```powershell
python -B -m evaluations.enterprise_isolated_evolution.launcher tmp/e16
```

Do not run this command against a rehearsal folder, a stopped study, or an
existing journal. Do not edit a frozen runtime to resume a failed study.
Preserve its original results and follow the organizer's new-study boundary.

## Verification and artifacts

```powershell
python -B -m unittest tests.test_enterprise_isolated_evolution -v
python scripts/check_coverage.py --threshold 80
```

The behavioral tests exercise strict retention, duplicate accounting, complete
rounds, misses and caps, two-arm reproduction, full qualification, an exclusive
cross-process lease, irreversible selection, private release ordering and
agent/verifier mount isolation.
Synthetic native-realizer and actual-container rehearsals provide additional
interface evidence; their simulated rewards are never benchmark scores.

Generated inputs, optimizer packets, native records, task payloads and private
evidence stay under ignored `tmp/`. `aggregate-draft/` is still private working
output until reviewed. Publish only approved aggregate reports under
`evaluations/reports/`, including strategy rankings, dataset scope, cost/time
accounting and the evidence limitations. Keep the main report index linked.

Results from 6,000 documents must not be described as the full 511,962-document
EnterpriseRAG benchmark. Retrieval nDCG@10 and model answer-quality Overall
are different metrics; neither an internal Luna run nor a subset comparison
establishes an official public rank.

[Back to the documentation index](README.md).
