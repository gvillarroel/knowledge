# Evaluation datasets and reports

Start with the [report hub](../evaluations/reports/README.md) for the highest
observed retrieval result within each dataset's published contract. Use its
[skill pages](../evaluations/reports/skills/README.md) to inspect a skill across
datasets, and [CTA](../evaluations/reports/cta/README.md) for cost, time, and
quality. CTA is interpreted as cost, time, and accuracy/quality; retrieval
relevance and generated-answer correctness remain distinct measurements.

The [public EnterpriseRAG results reference](../evaluations/enterprise-rag-bench/reports/public-results-20260906.md)
records the official 25-system leaderboard and additional author-reported
experiments checked on 2026-09-06. Its answer-quality scores and full-corpus
scope remain separate from the local 40-question retrieval comparison.

The [2026-09-06 verification report](../evaluations/reports/validation/20260906-verification.md)
records the completed comparison, repository tests, storage migration, and
report-only reproduction check.

## Storage policy

Dataset bytes remain local at their existing paths. Git tracks acquisition
descriptors, generators, reviewed manifests, schemas, runtime definitions,
tests, and reviewed reports. The shared
[`evaluations/.gitignore`](../evaluations/.gitignore) excludes downloaded
sources, corpora, knowledge snapshots, question banks, qrels, reference answers,
generated tasks, execution results, caches, and local environments.

Adding an ignore rule does not remove already tracked data. The index migration
uses an exact path list and preserves every local file's SHA-256. Its aggregate
[receipt](../evaluations/reports/data-hygiene/20260906-index-migration.json)
records the affected evaluation directories and preserved-file check. The
staged deletions remove files from future Git snapshots; the files remain on
disk. Earlier commits still contain any previously committed data. This change
does not rewrite repository history.

Validate the boundary:

```powershell
python scripts/check_evaluation_data.py
```

For a separately reviewed future migration, `--untrack` removes only currently
ignored evaluation paths from the index. Authored runtime code and package
locks are explicitly retained. Keep sealed or generated study evidence at its
original location and under its existing access policy.

## Reproduce EnterpriseRAG-Bench

The [dataset descriptor](../evaluations/enterprise-rag-bench/descriptor.json)
pins the [Onyx repository](https://github.com/onyx-dot-app/EnterpriseRAG-Bench)
at commit `d36685e273713975ee20299bbf1ab64165575b3c`, the `v1.0.0`
document archive, question bytes, and MIT license by SHA-256.

The upstream archive contains 511,962 document files plus an embedded question
file. Acquisition retains that complete archive locally. Preparation excludes
the embedded questions from builder inputs and selects a **reduced dataset**:

- 40 questions: five each from basic, semantic, intra-document reasoning,
  project-related, constrained, conflicting-information, completeness, and
  miscellaneous categories.
- 85 unique reference documents required by those questions.
- 900 distractors: 100 per source type, selected by a domain-separated SHA-256
  order before strategy results exist.
- 985 documents across Confluence, Fireflies, GitHub, Gmail, Google Drive,
  HubSpot, Jira, Linear, and Slack.

The upstream question bank contains one repeated qrel entry. The adapter uses
set semantics while preserving original upstream bytes. Four document IDs
refer to different document bodies in the archive; all colliding IDs are
quarantined. A selected question referencing an ambiguous or missing ID fails
preparation. No selected reference is ambiguous in this dataset version.

This is a reference-enriched corpus with a balanced source-type distractor
sample, not a representative sample of upstream document volume. Its retrieval
scores are not official full-corpus Onyx leaderboard scores. The 10 high-level
and 20 information-not-found questions lack retrieval qrels and need a
separately frozen answer/abstention evaluation. The remaining 460 upstream
questions are retained locally but are not scored by this 40-question run.
All records belong to one synthetic organization; this descriptive comparison
does not claim independent development/validation families or promotion.

From the repository root:

```powershell
python evaluations/enterprise-rag-bench/dataset_tool.py acquire
python evaluations/enterprise-rag-bench/dataset_tool.py prepare
python evaluations/enterprise-rag-bench/dataset_tool.py prepare --check
```

Acquisition reuses only matching pinned bytes. Preparation publishes once;
`--check` regenerates into an isolated temporary directory and compares the
complete file inventory and hashes. To change sampling, source revision, or
questions, create a new descriptor version and output directory.

Install the unchanged skill dependencies in a local Python 3.12 environment:

```powershell
uv venv --python 3.12 evaluations/enterprise-rag-bench/.venv
uv pip install --python evaluations/enterprise-rag-bench/.venv/Scripts/python.exe `
  -r skills/build-semantic-okf-turso/scripts/requirements.txt `
  -r skills/build-semantic-okf-graphify/scripts/requirements.txt
```

Use that interpreter to build and evaluate with a new run ID:

```powershell
evaluations/enterprise-rag-bench/.venv/Scripts/python.exe `
  evaluations/enterprise-rag-bench/run_comparison.py build --run-id <new-run-id>
evaluations/enterprise-rag-bench/.venv/Scripts/python.exe `
  evaluations/enterprise-rag-bench/run_comparison.py evaluate --run-id <new-run-id>
```

On Linux or WSL, use the environment's `bin/python` path. Turso requires its
actual `pyturso` engine; a platform without a wheel needs a Rust/native build
toolchain. No SQLite substitution is permitted.

The builder receives only `processed/enterprise-rag-bench-40-v1/input/`.
Questions, expected document IDs, gold answers, and answer facts live in the
separate `evaluator/` tree. Each source type has its own manifest declaration,
and document bodies and upstream hashes are preserved. No qrel-derived
retrieval profile or skill mutation is made.

The runner reuses the existing eight-family build and 18-route measurement
helpers, builds each family twice, independently validates both builds, checks
core identity parity, and freezes code and data hashes. Every route runs in a
fresh process and receives the same 40 questions three times at Top-10. Warm
caches can persist within one route's repetitions. Initialization is excluded
from P95. Embeddings use the declared 384-dimensional deterministic hashing
backend. This test uses zero model calls; it does not generate or judge answers.

Raw per-question rankings and logs remain ignored. Only allowlisted aggregate
metrics, category breakdowns, runtime identity, and provenance commitments
enter `reports/<run-id>/comparison.json` and its Markdown companion. Existing
run IDs are never overwritten. A failure leaves local diagnostics and does
not publish a complete comparison.

## Maintain the report hub

[`report-sources.json`](../evaluations/report-sources.json) is the explicit
inventory of approved aggregate sources. Update it when adding a new completed
report, then regenerate all views:

```powershell
python evaluations/build_report_catalog.py
python evaluations/build_report_catalog.py --check
```

For a newly completed EnterpriseRAG run, first point its source entry at the
new aggregate and publish the canonical table and companion contract:

```powershell
python evaluations/publish_enterprise_report.py
python evaluations/publish_enterprise_report.py --check
```

Publication is create-only. Use only `--check` for an already published run,
then regenerate the report hub to reflect the selected source.

The generator reads only those reviewed sources, validates row counts and
numeric units, preserves missing metrics and ties, and derives every view from
one normalized aggregate catalog. It can regenerate on a clean checkout
without downloading datasets or opening ignored result files. Source report
hashes make drift visible. Older evidence stays in its original location.

An active study can be linked from the report hub, skill pages and CTA without
registering unfinished comparisons as dataset rows. The
[stratified Enterprise campaign E7](../evaluations/reports/evolution/e7/README.md)
publishes measured development snapshots through that navigation. Its final
catalog entry requires the completed paired all-500 aggregate, with eight
fixed primary routes in each arm, and must retain its separate 6,000-document
retrospective scope. Declared variants and queued families are not results.

No single cross-dataset average or universal skill winner is computed. A
dataset page compares rows only within its named contract. Historical
construction tokens, consultation tokens, deterministic latency, and semantic
answer audits retain their separate denominators and validity boundaries.

After checking out a fresh clone, historical private datasets and processed
snapshots must be restored locally before running dataset-dependent tests.
Follow their own acquisition descriptors and access policies; never copy raw
data into tracked source to satisfy a test. The report hub and the new small
unit fixtures require no private source data.

## Improve the evaluated skills

The [evolution roadmap](knowledge-skill-evolution-roadmap.md) distinguishes
retrieval implementation changes from agent instruction changes, identifies
bounded candidates for the current families, and audits which historical
datasets can support a new study. Its
[readiness inventory](../evaluations/reports/evolution/20260906-readiness.md)
records current skill fingerprints and the prerequisites for independent
validation. It contains no new scores or promotion claim.

[Back to the documentation index](README.md).
