# Preregistration: Knowledge Methodology Offline Ablation 01

## Question

Do the audit's recommendations to treat chunking as an experimental factor,
retain simple cross-domain baselines, and report uncertainty change conclusions
on the repository's existing paper-retrieval workloads?

## Evidence boundary

This is an exploratory retrospective study. All 80 qrels are already visible to
the repository. No result is promotion-eligible, no cohort is called a holdout,
and the experiment cannot establish unseen-query generalization.

The study applies one frozen implementation to:

- the 40-question, 15-paper GraphRAG corpus; and
- the 40-question, 15-paper quantum-error-correction corpus.

Only page-grounded paper text beginning at `## PDF page 1` is indexed. Dataset
selection prose, reviewed claims, semantic rubrics, answers, and hard-ground-
truth spans are excluded from retrieval input.

## Frozen treatments

Chunking treatments are complete paper, PDF page, fixed 128, 256, and 512
tokens, fixed 256 tokens with 32-token overlap, and a hierarchical combination
of complete-paper and best-page scores.

Retrievers are word BM25, character-trigram TF-IDF, and reciprocal-rank fusion
of those two rankings. These are deliberately simple offline baselines. This
phase does not represent a neural semantic retriever, late chunking, or learned
hierarchical chunking.

## Metrics and uncertainty

The primary metric is document Recall@10 over the declared non-exhaustive
paper focus set. MRR@10 and nDCG@10 are secondary. Query time, P95 time, and
index-unit count are diagnostics. Every aggregate metric receives a
deterministic 2,000-sample query-bootstrap 95% interval. Candidate-versus-
document comparisons use a paired query bootstrap.

The exact decision rules are machine-readable in `experiment.json`. They were
written before the first experiment execution:

- KM-004 receives directional support if a non-document chunker changes
  Recall@10 by at least 0.02 in either domain, and strong support if its paired
  interval excludes zero.
- KM-005 receives partial support if domain winners differ or the cross-domain
  quality-latency Pareto frontier retains multiple treatments.
- KM-006 receives support if any Recall@10 interval is at least 0.05 wide.

## Interpretation limits

Document-level qrels cannot measure whether a retrieved chunk contains the
required claim. Runtime is descriptive and machine-specific. The experiment
does not test grounded answer quality, judge bias, contamination controls,
ontology validity, skill modularization, or extraction fidelity. Those
proposals remain explicitly deferred rather than receiving synthetic evidence.
