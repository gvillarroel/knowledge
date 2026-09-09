# Entity Graph alias matching: a concrete construction hypothesis

Source inspection and a synthetic profile identify potentially unnecessary
work in the unchanged Entity Graph mention matcher. This is a construction
diagnosis, not a retrieval improvement or a proven explanation of the
[original 3,600-second timeout](../entity-graph-timeout-001/README.md).

The current algorithm constructs one global set of alias lengths. For every
section it scans every possible token window for every length, even when no
alias starts with that window's first token. All matches then contribute exact
integer counts to source-bound mentions.

The public 6,000-document image-source input contains **34 distinct token
lengths among titles and record IDs**, with a maximum of **569 tokens**.
This metadata summary spans all nine applications. It excludes generated
subject-IRI aliases and therefore does not claim to enumerate the complete
derived alias map. No document text, title, record ID or benchmark question is
published. The input path is the bound image-source copy, not a claimed host
mount at `/dataset/input`.

An unchanged-function profile on deterministic synthetic text gives:

| Distinct alias lengths | Entities | Sections | Section-token range | Profiled seconds |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 128 | 128 | 1,025–1,028 | 0.230 |
| 32 | 128 | 128 | 1,025–1,056 | 1.435 |
| 128 | 128 | 128 | 1,025–1,152 | 8.270 |

Each row is one `cProfile`-instrumented call, with successful matches and an
ordered-result digest preserved in the [aggregate](aggregate.json). Alias
lengths, section lengths and match counts differ across rows. These observations
are not an uninstrumented benchmark, a candidate speedup or a full-corpus run.

The proposed change is to index allowed alias lengths by the first normalized
token, then visit only compatible window sizes at each section position. The
existing alias map would still resolve every binding. Overlapping matches,
duplicate normalized aliases, original alias strings, integer counts, stable
identities and final ordering must stay exact. Tokenization, plans, selected
sources, graph rules, retrieval settings and every validator must remain intact.

No Entity Graph candidate has been materialized or charged at this checkpoint.
Before implementation, the proposal needs a prospective reservation within its
existing 80-claim family allowance and the unchanged global cap, together with
an exact mutation contract. Required software evidence includes adversarial
matcher parity and complete build/query/corruption parity against the frozen
parent. Native feasibility would still require the separately controlled
whole-corpus evaluation. Unchanged consultant validation remains part of that
workload and may retain substantial cost even if builder matching improves.

[Current E11 status](../README.md) ·
[Family evidence index](../../../../../docs/enterprise-family-report-index.md)
