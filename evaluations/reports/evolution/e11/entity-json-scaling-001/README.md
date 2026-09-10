# Entity Graph: public JSON scaling diagnosis

The frozen skill completed construction, independent validation and deep
consultation on a new **1,024-record synthetic JSON** input after asynchronous
traceback sampling was disabled. The original larger-cell `SIGSEGV` remains
preserved. **No new EnterpriseRAG score, candidate mutation or promotion follows.**

## Measured work

| Records | Operation | Elapsed seconds | Candidate extraction seconds | Mention matching seconds |
| ---: | --- | ---: | ---: | ---: |
| 256 | build | 11.019 | 3.091 | 0.717 |
| 256 | validate | 3.532 | 1.051 | 0.223 |
| 256 | consult-deep | 2.329 | 1.071 | 0.212 |
| 1024 | build | 42.700 | 13.645 | 3.086 |
| 1024 | validate | 13.167 | 4.504 | 0.994 |
| 1024 | consult-deep | 9.608 | 4.586 | 1.051 |

Function times are nested inside command times and must not be added. They
include profiler overhead. The 256-record cell had an armed asynchronous
watchdog; its operations finished before the first scheduled 30-second dump.
The 1,024-record control used cProfile without that watchdog. One observation
per cell and different instrumentation do not establish a scaling law or speedup.

Candidate extraction used **32.10%** of total profiled build time
and **48.39%** of profiled deep-consult time in the larger cell.
This makes its repeated token eligibility checks a concrete next investigation.
It does not identify the phase that timed out in the original Enterprise job.

## Original failure and separate control

The first fixture passed all three 256-record operations. Its 1,024-record build
exited with signal 11 after 31.853 seconds, without a completed cProfile file.
The partial traceback ends during the first asynchronous dump. The remaining
two operations were not attempted. The container's OOM flag was false; no
300-second command timeout occurred. Neither observation proves a crash cause.

The separate control preserved the exact 1,024-record input, complete skill,
image and per-command resources. It removed asynchronous traceback collection,
retained cProfile, and did not repeat the successful 256-record cell. All three
operations passed, and both exported snapshots retain their checked byte
inventories. The control is consistent with an instrumentation issue; one
successful control cannot establish the exact cause of the original crash.
Python documents that [delayed traceback collection uses a watchdog thread](https://docs.python.org/3.12/library/faulthandler.html#dumping-the-tracebacks-after-a-timeout).
Related [upstream traceback crash evidence](https://github.com/python/cpython/issues/116008)
motivates the control but does not prove this incident has the same defect.

## Workload scope

Earlier software profiles used Markdown and 160-character sections. The new
JSON fixture maps document bodies to RDF literals and preserves the public
Entity plan's 12,000-character section cap and 1,200-candidate cap. Each generated
body has 8,192 characters; two synthetic source IDs and deterministic record
seeds produce one source family. The larger input contains the smaller prefix.
These are software diagnostic cells, not independent benchmark datasets.

The bound [input-shape summary by application](groups.md) describes only the
existing exposed development corpus: 6,000 documents and 37,183,736 raw body
characters. No document text, title, record ID, question or answer is published.
The synthetic text does not reproduce the original corpus's vocabulary or
full workload. No 6,000-document feasibility result or all-500 result is added.

## Next bounded hypothesis

Investigate a prefix count of disallowed tokens inside the builder's
`_candidate_statistics` function. It could avoid checking the same token for
stopword or digit status in each overlapping n-gram window. Preserve every
valid window, excluded alias, count, score, tie order, complete build and
independent validation. Freeze the entire consultant in this treatment.

This is an unreserved source-only hypothesis. No candidate, new proposal charge
or native attempt exists. An explicit reservation within Entity's existing cap,
an exact isolated mutation contract and the declared correctness checks must
precede implementation. A later consultation change is a separate treatment.

The [eight-family Enterprise comparison](../entity-consultant-token-automaton-native-001/README.md#eight-family-comparison)
is unchanged, with 86 cumulative claims and five searches still open. The
composed reference, remaining searches, paired all-500 evaluation and one-way
whole-bundle acceptance remain unfinished.

[CTA](cta.md) · [Source-bound aggregate](aggregate.json) · [E11](../README.md)
