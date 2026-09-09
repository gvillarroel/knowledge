# Embeddings: requested semantic-window workload

The six original semantic-chunking trials exceeded the fixed construction limit
before producing retrieval scores. A read-only audit now quantifies the work
requested by that splitter on the same 6,000 public documents. It does not run
an encoder, retry a failed trial or measure a new candidate.

All 6,000 normalized document bodies contain multiple sentence spans. Semantic
mode therefore requests **264,738 window vectors in a preliminary splitting
pass**, across 6,000 calls to the provider's Python `encode` method. Final chunk
vectors would be encoded afterward. Record mode skips that preliminary pass
and directly requests the 6,000 record vectors. The provider may batch each
request internally; these counts are neither tensor-forward counts nor a
runtime ratio. They describe the complete requested workload, not how much a
timed-out original execution actually completed.

| Neighbor buffer | Requested preliminary window vectors | Window characters in total | Repeated exact window texts | Ideal exact-text deduplication ceiling |
| --- | ---: | ---: | ---: | ---: |
| 1 | 264,738 | 114,598,838 | 527 | 0.199% |
| 2 | 264,738 | 187,908,168 | 424 | 0.160% |
| 3 | 264,738 | 259,049,110 | 463 | 0.175% |
| 4 | 264,738 | 327,927,121 | 584 | 0.221% |

The normalized document bodies contain 38,791,960 characters. Character totals
are input-size observations; they do not measure model tokens, truncation,
latency or memory. Duplicate counts use whole-window text SHA-256 across the
complete first pass and assume collision resistance. The ceiling assumes ideal
reuse with no cache overhead or numerical change, and says nothing about
sharing tokenizer output or other possible optimizations.

Two useful conclusions follow from the observed inputs and frozen code:

- The percentile threshold is applied after every window has been encoded.
  Changing only that threshold cannot reduce this preliminary vector count,
  although it can change final chunk boundaries and the later encoding work.
- Reusing identical whole-window texts could remove at most 584 of these
  requests, or 0.220595%, among the audited buffers. That offers little reduction
  in requested first-pass inputs. Reducing the segmentation workload would
  require a different construction mechanism, which remains untested.

| Source application | Documents | Requested preliminary window vectors |
| --- | ---: | ---: |
| Confluence | 543 | 33,971 |
| Fireflies | 139 | 20,697 |
| GitHub | 312 | 10,421 |
| Gmail | 1,336 | 55,877 |
| Google Drive | 647 | 28,182 |
| HubSpot | 321 | 7,609 |
| Jira | 584 | 24,850 |
| Linear | 991 | 35,891 |
| Slack | 1,127 | 47,240 |

The audit verifies the frozen nine input files and three builder modules. It
uses the exact structured-record body construction, string-only input contract,
whitespace/Unicode normalization and native sentence spans. An independent
reconstruction checks every normalized body and span, all 30,000 declared string
values, each buffer's window totals and both local/global duplicate measures.
Only aggregate observations are published; document text and identities stay
outside Git.

Embeddings still retains its original **63.51% weighted development nDCG@10**.
This audit neither establishes the cause of each timeout nor proves that a
changed splitter would finish or improve relevance. It creates no candidate,
new study, native score, acceptance or installation. A changed segmentation
mechanism must preserve source locators, complete input coverage and the pinned
embedding contract, then pass a separately declared construction treatment and
the applicable native gates. The six original failures, skipped options and
consumed runtime remain part of the history.

[Original native search and failures](../../e7/embeddings-complete-001/README.md) ·
[Cumulative native cost/time evidence](../development-cta-001/README.md) ·
[Aggregate observations and source commitments](aggregate.json) ·
[Family index](../../../../../docs/enterprise-family-report-index.md) · [Campaign](../README.md)
