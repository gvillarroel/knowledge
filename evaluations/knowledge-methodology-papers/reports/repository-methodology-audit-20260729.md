# Paper-Grounded Audit of Repository Knowledge Methodology

## Review identity

- Dataset: `knowledge-methodology-papers-47`
- Snapshot: `evaluations/knowledge-methodology-papers/bundle`
- Expert: `skills/review-knowledge-methodology`
- Expert tree SHA-256:
  `912e0af9b512cac273c70db3c7d583f5541b11f7218f28cb0310abf9b046d428`
- Review date: 2026-07-29
- Scope: knowledge acquisition, extraction, representation, retrieval,
  evaluation, evolution, and publication

## Executive finding

The repository is unusually strong on artifact integrity and experimental
boundaries. Its immutable source/build/consult stages, digest binding,
deterministic regeneration, append-only evidence, retrospective labels, and
one-way holdout policy should remain.

The largest weakness is not missing retrieval machinery. It is that the
repository has accumulated many sophisticated retrieval and evolution
treatments faster than it has accumulated cross-domain, claim-level, blinded,
and uncertainty-aware evidence for choosing among them. The next improvement
cycle should therefore prioritize evaluation validity, controlled chunking and
retrieval ablations, judge calibration, and a living research-review layer
before adding another retrieval family.

## Current strengths to preserve

1. **Build and consultation are isolated.** The evolution playbook freezes one
   layer while mutating another, and the canonical datasets keep raw build
   input separate from processed consult-only knowledge.
2. **Artifact identity is explicit.** Semantic OKF manifests, record ledgers,
   source digests, exact concept paths, SHACL reports, and deterministic
   reconstruction provide a strong reproducibility substrate.
3. **Evaluation evidence is classified honestly.** Exposed qrels are labeled
   retrospective and promotion-ineligible; mechanical retrieval is not
   presented as grounded answer quality.
4. **Holdout release is one-way.** Candidate selection is frozen before a
   holdout is opened, and later tuning requires a new untouched cohort.
5. **Failures remain evidence.** Provider failures, invalid comparisons, and
   superseding audits are preserved rather than rewritten.
6. **Semantic roles are separated.** Ontology meaning, SHACL acceptance,
   readable OKF concepts, normalized RDF, and build plans have distinct
   authority boundaries.

These controls align with the risks described by the corpus: adaptive reuse can
overfit a holdout
(`concepts/paper-1506-02629v2/sources-new-markdown-1506.02629v2-dd671258ed.md`,
PDF pages 1–3), and reproducible knowledge graphs require accessible code,
data, environment, instructions, and stable resources
(`concepts/paper-2309-08754v1/sources-new-markdown-2309.08754v1-647c5a4d37.md`,
PDF pages 1 and 4).

## Prioritized challenges and proposals

### P0. Make answer-quality diagnosis a promotion gate

**Current practice.** The repository correctly separates retrieval metrics
from semantic quality, but most family comparisons are still much denser on
Recall@10, MRR, nDCG, latency, and exact evidence validity than on blinded
claim-level answer analysis.

**Paper evidence.** RAGChecker decomposes overall quality into diagnostic
retriever and generator metrics, validates them against human judgments, and
reports a remaining gap between model predictions and human annotators
(`concepts/paper-2408-08067v2/sources-new-markdown-2408.08067v2-8e1f666a65.md`,
PDF pages 1–2 and 8). This is direct evidence that end-to-end and component
diagnostics reveal different failure modes.

**Challenge.** A candidate can retrieve the right paper yet omit, distort, or
hallucinate the claim. Exact evidence-path validity is necessary but does not
show that the cited span entails the answer.

**Proposal.** Add a claim ledger to grounded evaluations. For every required
answer claim, score retrieval coverage, entailment by cited evidence,
unsupported claims, contradiction, context utilization, and final
completeness. Keep deterministic retrieval columns, but block promotion until
a blinded semantic sample passes a registered threshold.

**Validation plan.** Freeze 24 development, 8 validation, and 8 untouched
holdout questions in at least two domains. Double-review the validation and
holdout answer claims; adjudicate disagreements. Compare the new diagnostic
scores with existing retrieval metrics and report where ranks change.

**Claim label:** synthesis. **Confidence:** high.

### P0. Calibrate every model judge against blinded humans

**Current practice.** Semantic review exists, but the methodology does not yet
define one repository-wide calibration contract for LLM judges, judge drift,
or acceptance thresholds.

**Paper evidence.** A controlled study finds both human and LLM judges
vulnerable to misinformation, gender, authority, and presentation
perturbations, with significant but different biases
(`concepts/paper-2402-10669v5/sources-new-markdown-2402.10669v5-d5684b7a2f.md`,
PDF pages 1 and 9). RAGChecker also finds a measurable gap between automated
metrics and human annotation (paper above, PDF page 8).

**Challenge.** A single uncalibrated judge can turn stylistic preference or
authority cues into a promotion decision.

**Proposal.** Version every judge prompt and model, blind candidate identity,
randomize answer order, include perturbation sentinels, sample at least two
human reviewers, record agreement, and prohibit judge-only promotion when
calibration drops below its registered bound.

**Validation plan.** Build a 60-answer calibration set containing clean,
factual-error, citation-authority, and verbosity perturbations. Measure
pairwise agreement, class-specific false acceptance, and rank stability for
each judge version.

**Claim label:** synthesis. **Confidence:** high.

### P0. Replace adaptive reuse with rolling untouched cohorts

**Current practice.** The playbook's one-way holdout boundary is strong.
However, GraphRAG has a fully exposed all-40 retrospective track, and repeated
family evolution can learn from the same corpus and query distribution.

**Paper evidence.** Adaptive reuse can overfit the holdout even when individual
procedures would generalize on fresh data
(`concepts/paper-1506-02629v2/sources-new-markdown-1506.02629v2-dd671258ed.md`,
PDF pages 1–3). Benchmark-contamination research describes how exposure
undermines evaluation trust
(`concepts/paper-2406-04244v1/sources-new-markdown-2406.04244v1-93e8f36aa4.md`,
PDF pages 1–2).

**Challenge.** Honest retrospective labels prevent a false claim, but they do
not create new evidence of generalization.

**Proposal.** Register rolling temporal cohorts from newly pinned source bytes
and unseen question authors. Reveal only pass/fail plus bounded diagnostics for
the qualification cohort; move opened cases permanently into development.
Maintain a contamination ledger covering prompts, qrels, traces, and training
inputs.

**Validation plan.** Transfer the frozen winner to a new paper domain and one
new version of an existing domain without modifying its bytes. Compare
pre-registered retrieval and claim-level metrics across both cohorts.

**Claim label:** repository-inference. **Confidence:** high.

### P1. Treat chunking as an experimental factor, not a fixed preprocessing choice

**Current practice.** Builder families encode different extraction,
segmentation, and hierarchy choices, but the main comparisons often change
more than chunking alone.

**Paper evidence.** Late chunking improves average retrieval over naive
chunking in its reported experiments
(`concepts/paper-2409-04701v3/sources-new-markdown-2409.04701v3-1ea0a39253.md`,
PDF page 7), while HiChunk introduces component-level evaluation and reports
hierarchical-chunking gains in- and out-of-domain
(`concepts/paper-2509-11552v3/sources-new-markdown-2509.11552v3-1013952b40.md`,
PDF pages 2 and 8). These are treatment-specific results, not a universal
winner.

**Challenge.** When extraction, chunking, index, ranking, and consultation
instructions change together, the repository cannot attribute the gain.

**Proposal.** Add a chunking matrix with whole-record, fixed-size, structural,
late, and hierarchical treatments. Freeze raw input, extractor, retriever,
consultant, and questions. Stratify by source format and question type.

**Validation plan.** Measure boundary accuracy, evidence-span coverage,
Recall@10, nDCG, context utilization, answer completeness, index size, and P95.
Promote no global default; select per documented source/question regime.

**Claim label:** synthesis. **Confidence:** medium-high.

### P1. Require simple and cross-domain retrieval baselines

**Current practice.** The repository compares many families, including
classical, embeddings, adaptive, graph, ensemble, Tantivy, and Tika/MALLET
treatments. Some current rankings are tied to one 40-question paper workload.

**Paper evidence.** BEIR shows that in-domain performance does not predict
zero-shot behavior, that BM25 remains a strong baseline, and that quality,
latency, index size, and annotation-pool bias interact
(`concepts/paper-2104-08663v4/sources-new-markdown-2104.08663v4-bdf7d9a00b.md`,
PDF pages 2 and 7–9). GraphRAG evidence also shows graph construction and prompt
costs vary sharply with task complexity
(`concepts/paper-2506-05690v3/sources-reused-markdown-2506.05690v3-206550caf8.md`,
PDF pages 3, 8–9).

**Challenge.** A complex treatment that leads one retrospective table may be
dominated on a new domain or on cost.

**Proposal.** Every study must include lexical, semantic, and hybrid controls,
plus the simplest applicable non-graph baseline. Report a Pareto surface over
quality, grounded answer score, latency, memory, construction time, and tokens.
Define a retirement rule for treatments dominated on all registered domains.

**Validation plan.** Run the identical candidate digests on GraphRAG, Astro,
the paper-methodology corpus, and one non-paper corpus. Use per-domain and
worst-domain metrics; do not rank only by pooled mean.

**Claim label:** synthesis. **Confidence:** high.

### P1. Account for stochastic variance and practical significance

**Current practice.** Deterministic build and direct-retrieval replicates are
excellent. Model-generated answers and judge-based evaluations do not yet
share a universal repeated-run and uncertainty requirement.

**Paper evidence.** Benchmark comparisons can be distorted by
hyperparameter, data, initialization, and numerical variance; the paper
recommends sampling multiple sources of variation and statistical comparison
(`concepts/paper-2103-03098v1/sources-new-markdown-2103.03098v1-68b571fe84.md`,
PDF pages 1–2, 6–10, and 15–16).

**Challenge.** A one-run improvement can be smaller than evaluator or
generation variance.

**Proposal.** Require at least three independent generation replicates for
screening and enough samples for the registered promotion effect. Report
confidence intervals, probability of improvement, worst-case domain, and
paired effect size. Pin provider model snapshots and judge versions.

**Validation plan.** Replay the current top two consultants under identical
balanced schedules and estimate rank-switch probability. Set the minimum
meaningful effect before looking at holdout outcomes.

**Claim label:** repository-inference. **Confidence:** high.

### P1. Add a reviewed claim layer above full paper text

**Current practice.** The new corpus preserves complete page-grounded text and
excellent file identity. Only the reused GraphRAG partition has a mature
reviewed-claim layer; the 32 new papers currently expose metadata and full
text, not normalized reviewed findings.

**Paper evidence.** Knowledge-graph reproducibility depends on code, data,
versioning, environment, and executable instructions
(`concepts/paper-2309-08754v1/sources-new-markdown-2309.08754v1-647c5a4d37.md`,
PDF pages 1 and 4). This supports reproducible evidence records, but the exact
claim schema below is a repository design inference.

**Challenge.** Full text is traceable but expensive to compare, and retrieval
can surface an abstract without exposing conditions, baselines, or
limitations.

**Proposal.** Add two-reviewer evidence cards for material paper findings:
claim, task, dataset, intervention, comparator, metric, result, limitations,
page span, reviewer, and adjudication state. Keep cards non-authoritative until
adjudicated; never replace full text.

**Validation plan.** Annotate the papers used by the first six recommendations,
measure reviewer agreement and locator validity, then compare audit time and
claim error rate with full-text-only review.

**Claim label:** repository-inference. **Confidence:** medium-high.

### P1. Make corpus selection a living, auditable review

**Current practice.** `paper-selection.json` records exact versions, lanes, and
selection dimensions, but the initial corpus is purposive. It has no frozen
database query log, exclusion ledger, citation-snowball record, or duplicate
screening evidence.

**Paper evidence.** The corpus surveys repeatedly motivate structured
taxonomies, broad comparison, and explicit gaps; the knowledge-graph
reproducibility study additionally demonstrates the value of transparent
selection and executable acquisition
(`concepts/paper-2309-08754v1/sources-new-markdown-2309.08754v1-647c5a4d37.md`,
PDF pages 1–4). No paper in this snapshot establishes one mandatory systematic
review protocol.

**Challenge.** Relevance depends on curator judgment, so omissions may mirror
the repository's existing preferences.

**Proposal.** Version search strings, indexes, dates, inclusion/exclusion
decisions, duplicate handling, citation snowballing, reviewer assignments, and
an update cadence. Keep the current 47-paper snapshot immutable and publish
future corpus versions as superseding releases.

**Validation plan.** Have two reviewers independently screen the next search
delta. Report agreement, disputed exclusions, lane saturation, and newly
introduced methodological conclusions.

**Claim label:** repository-inference. **Confidence:** medium.

### P2. Bound ontology and SHACL claims

**Current practice.** The repository already distinguishes OWL meaning from
SHACL operational acceptance and does not equate validation with universal
truth.

**Paper evidence.** SHACL validation operates against a specific graph and
shape document; expressive SPARQL constraints can be harder to understand and
can cause performance problems, while different fragments have different
complexity
(`concepts/paper-2112-01441v1/sources-new-markdown-2112.01441v1-269406ca95.md`,
PDF pages 3, 6, and 20).

**Challenge.** As shapes and ontology-learning assistance expand, constraint
coverage and maintainability can become implicit.

**Proposal.** Preserve the existing semantic boundary. Add competency-question
coverage for every shape, positive and negative fixtures, per-shape runtime,
and explicit human approval for LLM-suggested classes, properties, or rules.

**Validation plan.** Mutate each required constraint with one conforming and
one violating fixture; measure detection, false positives, and validation
cost. Reject rules without a reviewed evidence or policy basis.

**Claim label:** direct plus repository-inference. **Confidence:** high.

### P2. Evolve declarative components, not whole copied systems

**Current practice.** The playbook correctly selects one primary evolution
controller and separates builder from consultant mutation. The large family
surface still creates maintenance and attribution cost.

**Paper evidence.** GEPA combines natural-language reflection with
multi-objective Pareto selection
(`concepts/paper-2507-19457v2/sources-new-markdown-2507.19457v2-3121cb6102.md`,
PDF pages 1–4). DSPy argues for declarative, modular LM programs compiled
against data and metrics rather than ad hoc free-form prompt manipulation
(`concepts/paper-2310-03714v1/sources-new-markdown-2310.03714v1-356206937c.md`,
PDF pages 1–2).

**Challenge.** Copying an entire skill for each experiment obscures the exact
mutable component and makes downstream fixes expensive.

**Proposal.** Define explicit signatures for extraction, routing, retrieval,
evidence selection, synthesis, and citation. Let an evolution treatment mutate
one signature implementation or prompt at a time. Seal unchanged components
by digest and materialize a complete candidate only at evaluation boundaries.

**Validation plan.** Re-express one existing family mutation as a component
contract. Compare diff size, attribution, build reproducibility, quality, and
maintenance effort with the copied-skill workflow.

**Claim label:** synthesis. **Confidence:** medium-high.

### P2. Add extraction-fidelity gates

**Current practice.** New papers are extracted page by page with `pypdf`,
normalized to NFC, hashed, and bound to exact PDFs. This preserves identity,
but not necessarily table, formula, multi-column, or figure reading order.

**Paper evidence.** The current snapshot does not directly compare scientific
PDF extraction engines. This is an open evidence gap.

**Challenge.** A deterministic extraction error is still a deterministic
error, and it can silently degrade retrieval or invert a table interpretation.

**Proposal.** Keep `pypdf` as the deterministic baseline, add sampled visual
page checks, extraction-quality heuristics, and an independently implemented
extractor comparison for difficult pages. Quarantine papers that fail the
fidelity gate instead of silently ingesting them.

**Validation plan.** Build a stratified page set containing two-column text,
tables, equations, footnotes, and figures. Double-review reading order and
locator correctness, then publish error rates by extractor and page class.

**Claim label:** open-question plus repository-inference. **Confidence:** medium.

## Recommended implementation order

1. Register claim-level grounded-answer metrics and judge calibration.
2. Create a new untouched cross-domain cohort and contamination ledger.
3. Run controlled chunking and retrieval-baseline ablations with uncertainty.
4. Add reviewed paper evidence cards and the living-review update protocol.
5. Modularize one evolution path and introduce retirement criteria.
6. Add SHACL coverage and PDF extraction-fidelity gates.

Do not add a ninth canonical retrieval family before items 1–3 produce
selection evidence. A new family remains permissible for a concrete deployment
requirement, but it should not enter a quality leaderboard without the same
cross-domain, claim-level, cost, and uncertainty contract.

## Review limits

- The corpus is curated and arXiv-centered; it is not exhaustive.
- Paper results were applied only within their reported tasks and then labeled
  when the repository recommendation was an inference.
- Page text was extracted from PDFs and may degrade formulas, tables, figures,
  or multi-column order.
- The audit did not run new model-answer experiments. Every proposal includes a
  falsifiable validation plan precisely because the papers do not prove the
  outcome in this repository.
- Papers published after the pinned versions require a governed corpus update.
