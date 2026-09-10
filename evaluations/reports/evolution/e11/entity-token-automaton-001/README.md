# Entity Graph token automaton: verified construction candidate

The new Entity Graph builder candidate passes exact software correctness and
the public fixture in the pinned native runtime. **Its EnterpriseRAG score is
still unavailable.** The full 6,000-document qualification has not run for this
candidate, and no canonical skill has been installed.

## What changed

Only `derive_mentions` in the Entity Graph builder changed. A sparse token trie
uses failure links to continue matching after a mismatch and output links to
report suffix matches. Each terminal retains its own original bindings; suffix
bindings are linked instead of copied. Duplicate aliases, overlapping matches,
original alias strings, integer counts, stable identities and final ordering
remain exact. All 251 other files, including every consultant and Ensemble's
separate copy, are unchanged.

The candidate is `sha256:6414475543ea62006f6cc2ea7bb330577279b90bf775154fe0596854143119f4`; its parent is
`sha256:886840868c7e47d2d7f35d5ecdf677100dfffc49d8750f8a890c273efc0c1f9d`. The [decision record](../../../../../.specs/adr/0141-use-token-automaton-for-exact-entity-mentions.md)
describes the scope and remaining gates.

## Correctness evidence

All seven declared realization checks and subsequent digest verification passed:

- 1,120 ordered matching comparisons across generic and scientific schemas,
  four token thresholds and adversarial/randomized public cases; 1,066 were nonempty.
- Two independent count oracles check duplicates/overlaps and suffix outputs.
- Four schema/layout integration cells execute 152 Python commands: 16 builds,
  16 standalone validations, 32 nonempty paired queries, 40 corruption
  rejections and eight protected-overwrite refusals, plus consultation checks.
- One separate public runtime fixture builds and independently validates 128
  records with Python 3.12.13, RDFLib 7.6.0 and pySHACL 0.40.0. All **145 output
  files match the preserved parent byte for byte**.

In the shared-first-token stress case, tuple construction falls from
**3,996,464 to 128**, with the same 32 output mentions. This is a counted
operation reduction on a synthetic input, not an Enterprise speed multiplier.

## Public runtime observations

| Operation | Frozen parent | Token automaton |
| --- | ---: | ---: |
| Complete build | 9.608 s | 9.507 s |
| Mention matching within build | 0.835 s | 0.748 s |
| Standalone validation | 3.178 s | 3.076 s |
| Mention matching within validate | 0.274 s | 0.245 s |

These are single `cProfile`-instrumented observations on the same 128 public
records, pinned image, 2 CPUs, 6 GiB and container-local workspace. Matching time
is nested inside each complete operation and must not be added to it. The
parent's completed measurement was preserved rather than repeated. Timing
variation and profiler overhead prevent a general performance claim.

Earlier profiling used host-backed storage and recorded 27.980/6.050 seconds
for build/validation. The storage control recorded 9.608/3.178 seconds with
identical outputs and unchanged skills. That difference belongs to the storage
treatment, not the automaton or the original Enterprise timeout. The first
expanded public fixture was correctly rejected for missing title metadata;
its evidence is preserved and excluded from successful-profile comparisons.

## EnterpriseRAG status and opportunities

The [retained eight-family comparison](../ensemble-semantic-return-native-001/README.md#eight-family-comparison)
still applies to its exact previously measured packages. Legacy is 72.38,
Turso 72.08, Adaptive 66.21, Embeddings 63.51, Classical 62.10 and Graphify 8.12
on the internal nDCG@10 ×100 scale. Entity Graph and Ensemble remain unavailable.
Application/category results remain linked from the [family index](../../../../../docs/enterprise-family-report-index.md).

This proposal increases cumulative claims from 84 to **85 of 585**. Entity Graph
has used two of 80, leaving 78. All closed catalogs, the two already charged
pending historical measurements, unavailable originals, five-round ceiling and
three-consecutive-evaluable-miss policy remain intact. This software validation
adds no quality miss. Five family searches remain open.

The new first measurement is reserved but unassigned. Full construction
qualification, the exact composed reference and fresh starting roles, remaining
searches, joint replay, paired all-500 comparison and independent acceptance
remain required before installing an accepted bundle. No private data was released.

[Cost/time and validation scope](cta.md) · [Source-bound aggregate](aggregate.json) · [E11 overview](../README.md)
