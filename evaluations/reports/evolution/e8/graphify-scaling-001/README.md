# Graphify neighbor-selection scaling audit

Date: 2026-09-09. A host-only prototype removes repeated scans of all pair
scores while preserving the original mutual-neighbor graph on synthetic
fixtures. The largest measured fixture, 800 short records, took 0.371 seconds
versus 7.573 seconds for the original function, a 20.43-fold ratio. This is an
isolated function measurement, not a native builder or retrieval result.

## Mechanism

The current [Graphify projection](../../../../../skills/build-semantic-okf-knowledge-skill/assets/families/graphify/builder/scripts/_graphify_projection.py)
computes TF-IDF similarities for document pairs, stores positive scores and then
scans that complete score map once for every record to choose its neighbor.
With dense lexical overlap, the map has N(N-1)/2 entries and endpoint selection
performs N squared times (N-1)/2 checks. This additional selection work grows
cubically. The native function is used during both projection creation and
projection validation.

The isolated prototype retains each endpoint's best permitted neighbor while
visiting each pair. It preserves feature extraction, corpus-wide IDF, norms,
cosine arithmetic, cross-partition eligibility, score/path tie-breaking, mutual
edge selection, output order and twelve-decimal scores. The current builder uses
one neighbor. Retained neighbor state is bounded by N entries for that setting;
pair enumeration remains quadratic. Token extraction and pairwise lexical work
are still required. No approximate search or graph pruning is introduced.

## Measured synthetic timing

| Synthetic records | Original median | Prototype median | Original / prototype | Identical output edges |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 0.020680 s | 0.007148 s | 2.89 | 23 |
| 200 | 0.131212 s | 0.025199 s | 5.21 | 40 |
| 400 | 0.955150 s | 0.093079 s | 10.26 | 67 |
| 800 | 7.573302 s | 0.370646 s | 20.43 | 138 |

Each row uses three paired runs on the same Windows host with alternating
execution order and checks exact edge tuples before accepting its timing.
Fixtures use seed 60109, seven synthetic partitions and short generated text.
The host also had the original native Graphify job active, so these timings
are descriptive and do not estimate dedicated Harbor resource performance.

At 800 records the dense original stores 319,600 pair scores and performs
255,680,000 endpoint checks. The prototype retains at most 800 neighbor entries
after pair updates. These are algorithmic state/check counts, not measured peak
memory or an end-to-end speed estimate.

Four focused tests with 234 subtests also compare exact outputs across seeded
sparse/dense fixtures, one/two/seven partitions, neighbor limits 1/2/4, reversed
input order, empty or zero-norm records, disjoint terms and exact ties. The
prototype is extracted and run separately; no source skill is modified.

## Evidence and next evaluation

[Audit implementation](../../../../../evaluations/audit_graphify_neighbor_scaling.py)
loads only two source AST functions in isolation and has no corpus, model,
candidate, Harbor or private-release interface. Reproduce into a fresh path:

```powershell
python evaluations/audit_graphify_neighbor_scaling.py --output tmp/graphify-scaling-new.json
python -m pytest -q tests/test_graphify_neighbor_scaling_audit.py
```

The [aggregate](aggregate.json) preserves all paired durations, output hashes
and source/prototype commitments. Source SHA-256:
`f52b62934248497726e950308b2e99f2751d739522ac91ca901dd8401d19e987`.
Prototype function SHA-256:
`cdeac2f609d03e17111dde340a530278888e8a0016ef756c1b90f0be9a061864`.

The original E8 Graphify baseline was still in its first construction when this
audit began. Its eventual native outcome must be preserved independently; this
audit does not locate its active stack or prove that this function accounts for
all elapsed build time. No quality score or construction success is inferred.

The supported next hypothesis is a separate builder-efficiency treatment,
realized from a frozen parent under a prospectively reviewed study. Require
complete artifact and graph parity, deterministic rebuilds, native construction
feasibility, matched query outputs and unchanged evidence gates before any
quality claim or installation. E8's consultation treatments and sealed controls
remain unchanged. The current synthetic prototype is not a packaged skill.

[Campaign status](../README.md) · [Traversal and fusion audit](../../e7/graphify-opportunity-001/README.md) · [Family index](../../../../../docs/enterprise-family-report-index.md)
