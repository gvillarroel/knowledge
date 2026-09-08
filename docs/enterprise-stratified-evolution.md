# Stratified EnterpriseRAG evolution

E7 evolves eight native retrieval strategies on 120 stratified questions and
recalculates the frozen selections on all 500 public questions. Every arm uses
the same 6,000 complete-document, reference-enriched corpus. This is an internal
retrieval comparison, distinct from the
[511,962-document Classical/Luna evaluation](enterprise-classical-full-corpus.md).
The study decision is [ADR 0129](../.specs/adr/0129-stratified-enterprise-family-evolution-and-joint-gate.md).

[Campaign status and reports](../evaluations/reports/evolution/e7/README.md)

## Sampling and score interpretation

| Question category | Development questions |
| --- | ---: |
| Basic | 24 |
| Semantic | 32 |
| Completeness | 12 |
| Project related | 12 |
| Intra-document reasoning | 12 |
| Constrained | 8 |
| Conflicting information | 4 |
| Miscellaneous | 8 |
| Information not found | 4 |
| High level | 4 |
| Total | 120 |

Sampling is uniform without replacement within each category. The seed is
frozen before scoring, and four 30-question blocks have identical category
counts. Application coverage and evidence-count bands are reported as overlapping
audit groups. They do not alter inclusion probabilities. All nine applications
are represented: Confluence, Fireflies, GitHub, Gmail, Google Drive, HubSpot,
Jira, Linear and Slack.

Selection uses weighted nDCG@10 over 112 questions with reference documents.
Each question receives its category population/sample weight; eligible weights
sum to 470. The eight sampled high-level or information-not-found questions have
no qrels and remain in execution and latency statistics. Final retrieval means
use 470 eligible questions out of all 500. The four blocks belong to one exposed
Enterprise source family and do not constitute independent validation.

The corpus includes all 722 gold reference identities and the contexts from the
previously frozen full-corpus Classical BM25 run, plus deterministic distractors.
It contains 37,183,736 rendered body characters. Only three Unicode newline
characters are normalized to LF at ingestion; this affects two characters in
two documents. Original and rendered body hashes are retained locally. Scores
on this reference-enriched corpus cannot be compared directly with the public
leaderboard or the existing full-corpus result.

## Evolution and acceptance

| Family | Treatment | Mechanisms |
| --- | --- | --- |
| Legacy | Consultation | BM25 saturation, length normalization, title weight |
| Embeddings | Construction | Semantic segmentation, sentence context |
| Classical | Construction | Length normalization, saturation, title weight, expansion, diversity |
| Adaptive | Construction | Classical mechanisms and aspect allocation |
| Entity Graph | Construction | BM25 settings, graph reach, edge weight, section granularity |
| Ensemble | Construction | Learned embeddings, classical mechanisms, component allocation |
| Graphify | Consultation | Traversal depth, lexical fusion, reciprocal-rank decay |
| Turso | Consultation | BM25 saturation, length normalization, title weight |

Each mechanism changes after three consecutive new evaluable candidates fail
to improve the incumbent. A gain resets that counter. Duplicate profiles do not
consume another trial. An improving complete catalog round triggers another
round, up to five; a complete round without improvement ends that family. The
117 variants per round define a finite search space, with at most 585 new
candidate trials across five rounds. A resource-limit stop is reported explicitly.

The native Harbor Pareto owner stages candidates, evaluates jobs and verifies
locked provenance. The scheduler only proposes the next frozen mutation. Each
trial executes a matched native builder and consultant with exact full-text
evidence, separate verification, offline models and deterministic reconstruction.
Five families mutate construction settings; three mutate consultation settings.
E7 makes no language-model calls and does not measure autonomous skill selection.

After every family finishes, the exact eight retained configurations are merged
and replayed jointly. Their development scores must reproduce before the entire
package is frozen. The all-500 comparison follows, without changing selection.
Finally, one independent transfer pilot tests all families on two reserved source
groups, with 12 questions and 985 documents per group. Every family's mean paired
gain must be nonnegative, and all native evidence/provenance gates must pass.
The package is accepted or rejected as a whole. No further evolution is allowed
after private release in this study.

## Execution and preservation

The implementation is in
[`evaluations/enterprise-stratified-evolution/`](../evaluations/enterprise-stratified-evolution/).
Native execution uses Harbor 0.18.0 under WSL Ubuntu and a pinned Docker runtime.
Each agent receives two CPU threads, 6 GiB RAM and a 3,600-second ceiling; at most
two trials run concurrently. Separate verifiers have two threads, 2 GiB RAM and
180 seconds. Network access is disabled and the pinned MiniLM cache is read-only.
There is one attempt and zero automatic retries per native trial.

All input and execution artifacts remain under ignored `tmp/e7/`. Preparation
commands create new paths and refuse replacement. The current materialization
depends on retained full-corpus inputs, UUID identity bindings and the local
pinned model cache; a clean clone must reacquire and requalify those inputs.
The independent curator owns private task preparation and access review. Never
reuse a consumed private cohort or copy raw artifacts into Git to simplify setup.

After preparation, native zero-query qualification, independent task review and
initial registration, the final command sequence is:

```powershell
python -B evaluations/enterprise-stratified-evolution/seal.py contract
python -B evaluations/enterprise-stratified-evolution/seal.py seal --review <qualified-review-directory>
python -B evaluations/enterprise-stratified-evolution/pipeline.py
```

The supervisor executes evolution, joint replay, freeze, final recalculation,
one release, native validation and terminal closure in order. It stops on the
first error and preserves all artifacts. Inspect `pipeline/`, `logs/`,
`family-results/` and the organizer ledger for actual progress; a started job
is not a completed metric. An unchanged selection leaves validation unopened.

The final publication must include baseline and frozen candidate metrics, all
eight primary routes, all eighteen diagnostic routes, category/application
views, CTA and exact source bindings. LLM usage is zero for E7; provider cost
is unavailable, and local CPU time must not be presented as a provider invoice.

Before publishing, replay every family's stopping and selection history using
the frozen scheduler and its existing native rewards. Reject missing attempts,
changed incumbents, false stop reasons or disagreement with native archives.
Category and application summaries identify the highest frozen primary route
using unrounded scores, preserving ties within 1e-12. Groups without references
have no winner, and comparisons require matching question denominators. These
descriptive summaries never change the jointly frozen selection.

Final collection requires both comparison arms and eight settled, error-free
native trials in each. Verify the exact declared route names for every family
in both aggregates and case arrays; a total of 36 routes alone cannot establish
coverage. The publication contract tests cover full 16-trial collection and
reject substituted routes, unfinished jobs and a missing comparison arm.

Development reports distinguish the scheduler's native objective from measured
retrieval quality. Unqualified candidates have no published nDCG observation,
even when the owner records a zero objective for a native execution error.
Keep these rejected attempts, their miss counts and source hashes in the
aggregate. The CTA report includes failed work in the sum of original native
job durations; that sum is neither campaign wall time nor a provider charge.

The native Pareto owner's diagnostic reward threshold is 0.8; its mandatory
qualification reward is exact evidence integrity of 1.0. Strict qualified
nDCG gains select development incumbents even when both arms are below the
diagnostic threshold. When separately normalizing completed jobs with
`report_harbor_jobs.py`, pass `--pass-threshold 0.8` explicitly: that reporting
tool otherwise defaults to 1.0. This display threshold does not change case
scores, selection, or the preregistered joint gate.
