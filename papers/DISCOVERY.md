# Paper Discovery Workflow

This workflow supplies a repeatable recall layer for the repository's
knowledge-methodology research. The query profile is intentionally broader
than the final corpus: search retrieves candidates, and a semantic review of
the title and abstract decides whether each candidate is relevant.

## Weekly discovery

Use a fourteen-day overlap from the most recent successful run. The overlap
protects against delayed arXiv indexing, a skipped weekly run, and transient
API failures. `--published-after` is a strict UTC boundary, while
`--max-results` applies to each query lane.

```powershell
know --store C:\Users\villa\.knowledge search arxiv `
  --query-file papers\arxiv-discovery-queries.txt `
  --published-after 2026-07-20T00:00:00Z `
  --registered-key papers-self-improvement-km `
  --only-unregistered `
  --max-results 200 `
  --sort-by submittedDate `
  --sort-order descending `
  --request-delay 3
```

The command places the time boundary inside every arXiv query, searches lanes
sequentially, observes a delay between API requests, deduplicates exact paper
versions, and reports both exact-version and other-version registration state.
Inspect `truncated_queries` before review. If it is non-empty, repeat the run
with a larger `--max-results` value until it is empty; otherwise the candidate
set is not complete for the declared window.

## Selection boundary

Select a candidate when its title and abstract materially inform at least one
of these research areas:

- agent self-improvement, self-evolution, or continual adaptation;
- long-horizon execution, runtime harnesses, state management, or auditing;
- durable agent memory, context management, or knowledge management;
- knowledge graphs, retrieval, RAG, GraphRAG, or ontology engineering;
- agent skills, tool use, evaluation harnesses, or reliable benchmarks.

Reject generic application papers that merely use an agent or an LLM without
contributing a reusable method, evaluation, architecture, or failure analysis.
Title-screen the complete candidate set, then inspect the abstract of every
plausible finalist. Record each abstract-reviewed finalist in
`papers/discovery-log.md` with a short selection or rejection reason, and
record aggregate counts and reasons for the remaining title-screened rejects.
This prevents silent omissions without turning the durable ledger into a copy
of the complete API response.

## Registration

Pin selected papers to the exact arXiv version returned by the API. Register
and synchronize a reviewed batch idempotently:

```powershell
know --store C:\Users\villa\.knowledge add arxiv `
  https://arxiv.org/abs/2608.01964v1 `
  https://arxiv.org/abs/2608.05013v1 `
  --key papers-self-improvement-km `
  --if-missing `
  --sync `
  --request-delay 3 `
  --batch-size 50
```

Official arXiv abstract, HTML, and PDF URLs and alphaXiv overview URLs are
normalized to `https://arxiv.org/abs/<exact-id>`. Synchronization enriches the
source record with the paper title, authors, categories, dates, abstract, and
PDF URL. When API retries are exhausted, synchronization can recover through
official arXiv abstract-page citation metadata and records
`metadata_source: arxiv-abs-html`. Export the key after registration and verify
that every selected exact version appears in the store and archive.
