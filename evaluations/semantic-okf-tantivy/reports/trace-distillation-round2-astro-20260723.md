# Tantivy Astro Trace-Distillation Round 2

## Outcome

The prospective query mutation was rejected by the existing canonical
regression gate. The long-record overview builder was promoted after passing
candidate development, disjoint holdout, deterministic rebuild, exact evidence,
and the complete canonical replay.

## Query stage

Harbor evaluated six Astro `train` tasks and two disjoint `dev` holdout tasks.
The lexicon-backed inflection candidate passed all mechanical and exact-evidence
gates. Its holdout reward rose from `0.787847` to `0.807445`, with no regressed
Astro cell.

The additional frozen GraphRAG gate rejected it. All-40 metrics were close to
the baseline, but the hard cohort regressed:

| Query | All-40 Recall@10 | MRR@10 | nDCG@10 | Hard-10 Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Retained baseline | 80.74% | 93.75% | 81.05% | 92.17% | 90.00% | 80.54% |
| Inflection candidate | 80.80% | 93.75% | 81.22% | 90.17% | 85.00% | 78.03% |

The live consultant was restored exactly to baseline digest
`sha256:896d038b16dd974411ef50bf91e5efead5e2589262058114b4bed4d8993f0c84`
before builder evolution.

## Builder stage

The frozen consultant was embedded in every task. Harbor discovery covered six
independent Astro `train` tasks. Four evidence-cited proposals added one exact
overview passage before the first level-two heading only when a non-paper
record is at least 10,000 characters; the complete record remains present.

The sealed candidate digest is
`sha256:5223046d8c1fcc4d4d7cc4cf138e9182a67ac92f970d4bf05bcf39ba50c9e1a8`.

| Gate | Baseline | Candidate | Gain | Result |
| --- | ---: | ---: | ---: | --- |
| Astro development, 24 questions | 0.832638 | 0.853740 | +0.021102 | 6/6 pass |
| Astro holdout, 8 questions | 0.927071 | 0.927305 | +0.000234 | promote |

Holdout part 01 was unchanged at `1.0`; part 02 improved by `0.000468`.
There were zero regressed cells, errors, retries, missing rewards, or evidence
gate failures.

## Canonical replay

Two raw-input canonical builds produced 890 files each and were byte-identical.
The Top-10 run, exact replay, and pool-100 sensitivity run completed 120 queries
with zero errors. All 400 Top-10 and 527 pool-100 evidence rows were valid, all
ranked Top-10 results reproduced, and the pool-100 Top-10 prefix was identical.

| Route | All-40 Recall@10 | MRR@10 | nDCG@10 | Hard-10 Recall@10 | MRR@10 | nDCG@10 | P95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `tantivy_bm25` | 80.74% | 93.75% | 81.05% | 92.17% | 90.00% | 80.54% | 90.92 |

The quality columns in the general canonical table remain unchanged. The P95
diagnostic is refreshed from the latest replay.
