# Tantivy Builder Forward-Four Trace-Distillation Result

## Outcome

Retain the stable dedicated builder. The `forward-four` candidate improved all
six development tasks, but its untouched holdout mean fell from 0.852793 to
0.831703 and two of four tasks regressed. Harbor therefore returned
`keep-baseline`; no candidate file was copied into
`build-semantic-okf-tantivy`.

The consultant remained byte-for-byte frozen at realizer digest
`sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7`
throughout builder discovery, development, and holdout.

## Candidate

The candidate retained every selected paper and semantic-claim record. It
changed only deterministic paper passage construction: each page start opened
an exact, overlapping forward window covering up to four page regions, with
shorter windows at the record tail. Every locator remained an exact substring
of its authoritative record.

Its sealed Harbor skill digest was
`sha256:0fccf4555edea1fadbe0530262030b15f183f6e696acd6e32dba17225b848a5d`.

## Development gate

| Task | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| part 01 | 0.813344 | 0.831600 | +0.018256 |
| part 02 | 0.877903 | 0.902885 | +0.024982 |
| part 03 | 0.805715 | 0.809467 | +0.003753 |
| part 04 | 0.839049 | 0.872281 | +0.033233 |
| part 05 | 0.899072 | 0.900329 | +0.001257 |
| part 06 | 0.871885 | 0.882390 | +0.010505 |
| **Mean** | **0.851161** | **0.866492** | **+0.015331** |

All six tasks were evaluable, error-free, and satisfied the exact-evidence and
mechanical qualification gates.

## Holdout gate

| Task | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| part 01 | 0.813455 | 0.910511 | +0.097055 |
| part 02 | 0.817969 | 0.865667 | +0.047698 |
| part 03 | 0.825374 | 0.602545 | -0.222829 |
| part 04 | 0.954375 | 0.948088 | -0.006287 |
| **Mean** | **0.852793** | **0.831703** | **-0.021091** |

The large part-03 loss and the smaller part-04 loss independently block
promotion. Positive development evidence and the first two holdout gains do
not compensate for either regression.

## Canonical replay

The retained live builder produced two new 890-file bundles that were
byte-identical to each other and to the frozen baseline. A fresh complete
Top-10 run, exact Top-10 replay, and pool-100 sensitivity run executed 120
queries with zero errors and 100% exact evidence validity.

The canonical table remains unchanged:

| Route | All-40 Recall@10 | MRR@10 | nDCG@10 | Hard-10 Recall@10 | Hard-10 MRR@10 | Hard-10 nDCG@10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `tantivy_bm25` | 80.74% | 93.75% | 81.05% | 92.17% | 90.00% | 80.54% |

All 400 Top-10 evidence rows and all 527 pool-100 rows were valid. The ranked
Top-10 replay and pool-100 Top-10 prefix were identical. Because neither live
skill changed, these metrics exactly match the checked canonical summary.
