---
name: consult-semantic-okf-ensemble
description: Consult a published definitive Semantic OKF ensemble read-only. Use for evidence-grounded retrieval or multi-paper synthesis when the bundle contains adaptive lexical, entity-graph, embedding, and ensemble projections and the answer must preserve exact claim IDs, paths, locators, citations, hashes, exclusions, and response contracts.
---

# Consult Semantic OKF Ensemble

Treat `semantic/`, `concepts/`, and accepted RDF as authoritative. Treat `adaptive/`,
`entity-graph/`, `retrieval/`, and `ensemble/` only as hash-bound discovery indexes.
Never edit, repair, or cache inside the supplied bundle.

## Enforce the CLI-only structured-answer gate

Use only the packaged read-only CLI. This package deliberately exposes no server,
host publication wrapper, or alternate answer transport. When the task requests the
`question_id`, `answer`, `evidence` JSON contract, apply this gate to every non-null
answer:

1. Resolve the package-local launcher through the bounded workspace paths below.
2. Deep-validate the bundle before retrieval and stop on any validation failure.
3. Read every `coverage-brief` page for the exact question once, in ascending page
   order, with identical parameters. Require the full-coverage and priority-order
   hashes, facets, route counts, and claim totals to agree across pages.
4. Account for every derived facet and draft only statements supported by reviewed
   claim IDs exposed across those pages. Keep the draft in memory and never write it
   into the bundle.
5. Pipe the draft to `finalize-answer --draft -`. Let the deterministic finalizer,
   not the model, construct `paper_ids`, `citations`, `evidence`, paths, locator order,
   and field order from verified bindings.
6. Keep stdout and stderr separate, never merge stderr with `2>&1`, stop on a nonzero
   exit, and accept only stdout that parses as the exact requested contract. Return
   the last successful finalizer JSON verbatim without parsing and reserializing it.

If validation, coverage, drafting, or CLI finalization
cannot complete, return the task's exact null-answer object instead. Never return a
diagnostic or the finalizer's exit-2 error object as an answer.
Do not hand-author a non-null contracted response as a fallback.

## Resolve the packaged CLI without broad scans

Resolve the packaged launcher from the current workspace before running any command.
A direct package invocation has `scripts/run_query.ps1`; a Skill Arena or
workspace-overlay installation has
`skills/consult-semantic-okf-ensemble/scripts/run_query.ps1`. The launcher uses the
absolute executable in `SEMANTIC_OKF_PYTHON` when declared, otherwise `python`.
When `SEMANTIC_OKF_HF_HUB_CACHE` is declared, it must be an absolute directory and
the launcher exposes only that governed model cache as `HF_HUB_CACHE`; do not pass
`HF_HOME` or a credential directory. The CLI rejects a missing or mismatched pinned
semantic runtime or model revision instead of silently changing retrieval policy.

```powershell
$QueryCommand = @(
  'scripts/run_query.ps1',
  'skills/consult-semantic-okf-ensemble/scripts/run_query.ps1'
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $QueryCommand) { throw 'consult-semantic-okf-ensemble CLI is not installed in this workspace' }
$Bundle = if (Test-Path -LiteralPath 'knowledge/semantic/records.jsonl') { 'knowledge' } else { 'BUNDLE' }
```

Use those resolved values in every command below. Do not run `find /`, recursive
drive scans, home-directory scans, or searches outside the current workspace to
locate the script, bundle, or query output. Stop with the explicit installation error
when neither package-relative path exists.

## Validate first

Run deep validation once for every new, release, or benchmark snapshot:

```powershell
& $QueryCommand $Bundle --deep-validation inspect
```

Stop on any closed-schema, component-hash, core-parity, claim-binding, model-revision,
or build-report failure. Do not fall back to an unvalidated scan.

## Choose a retrieval policy explicitly

Use `quality` for the strongest direct ordering. It preserves the adaptive paper set,
combines adaptive, BM25, graph, and exact pinned embedding ranks, and applies a
consensus promotion gate. It fails closed when the pinned offline embedding runtime is
unavailable.

```powershell
& $QueryCommand $Bundle search `
  --policy quality --query "QUESTION" --top-k 10
```

Use `fast` when latency or a missing embedding runtime matters; it retains protected
adaptive candidates and graph confirmation. Use `robust` to reproduce the protected
adaptive ordering. Never describe either as the quality policy.

Review `candidate_set_gate`, `promotion_gate`, and `route_rankings`. A high score or
graph path is not evidence. Open returned `concept_path` and `source_path`, then verify
the exact authoritative record, locator, and text hash before using a statement.

## Close answer coverage before drafting

For synthesis, comparisons, conditions, exclusions, mechanisms, or important
negatives, request the first compact page:

```powershell
$BriefJson = & $QueryCommand $Bundle coverage-brief `
  --query "QUESTION" --top-k 30 --per-facet 12 --maximum-facets 12 `
  --page 1 --page-size 48
if ($LASTEXITCODE -ne 0) { throw 'coverage brief failed' }
$Brief = $BriefJson | ConvertFrom-Json -Depth 100
$Brief | ConvertTo-Json -Depth 100 -Compress
```

Read `pagination.total_pages`, then invoke the same command exactly once for each page
from 2 through that exact total, in ascending numeric order. Keep every retrieval
parameter, including `page_size`, and the exact query unchanged; change only `--page`.
Never skip, repeat, or reorder a page, concatenate all pages into one tool output, stop
early, or print `coverage-pack` for drafting. Each brief recomputes and hash-binds the
complete pack, then pages the entire deduplicated union by deterministic persisted-IDF,
facet-consensus, and weighted-RRF priority. It emits authoritative text only once per
page. Confirm every page has the same `full_coverage.sha256`, facets, route counts,
total claims, `priority_order`, and `priority_order_sha256`.

The semantic claim route uses deterministic paper-conditioned diversification after
its global prefix: it reserves bounded evidence depth for the first three distinct
papers already selected by the adaptive route, then fills the remaining per-facet
budget by global semantic rank. This prevents globally similar claims from crowding
out a complementary claim in an already relevant paper. It never adds a new paper,
changes authority, or exceeds the published semantic caps.

Use every row in `facets`, in order, exactly once in the draft. Inspect every page's
`claims`; each row is a reviewed exact answer binding with `claim_id`, `paper_id`,
`authoritative_text`, `citation_pages`, and all route/facet provenance. `routes` retains
the full bounded route counts while listing only claim IDs present on that page. The
graph route remains reviewed-claim discovery with zero candidate-edge authority. The
pinned hybrid route remains reviewed, exact-binding discovery with the deterministic
`adaptive-paper-conditioned-claim-diversification-v1` reranker. Coverage fails closed
when the offline semantic provider is unavailable. Prefer a qualified partial answer
over inventing support.

Record each exact derived facet as `supported`, `partial`, or `unresolved`. Use one
directly entailing reviewed claim per atomic statement when possible; add evidence only
for a real join or contrast. Preserve requested exclusions and important negatives.

## Finalize through the gate

Create the in-memory draft with this closed shape:

```json
{
  "summary": "A synthesis within the requested word bound.",
  "facets": [
    {
      "facet": "Exact facet text copied from the coverage brief",
      "status": "supported",
      "statement": "One atomic statement entailed by the cited reviewed claims.",
      "supporting_claim_ids": ["claim-example-001"]
    },
    {
      "facet": "Another exact facet",
      "status": "unresolved",
      "statement": "The authoritative corpus does not establish this requested point.",
      "supporting_claim_ids": []
    }
  ]
}
```

Use every exact `facets[*].facet` value from the coverage brief; it already includes the
full query when that is the finalizer's only required facet. Keep the draft in memory
and repeat the exact query and full-pack parameters used for every brief page. Pipe the
draft to standard input and use the CLI:

```powershell
$DraftJson = @'
{"summary":"...","facets":[...]}
'@
$FinalJson = $DraftJson | & $QueryCommand $Bundle `
  finalize-answer --draft - --question-id QUESTION_ID --query "QUESTION"
if ($LASTEXITCODE -ne 0) { throw 'answer finalization failed' }
$FinalJson | ConvertFrom-Json -Depth 100 | Out-Null
```

The finalizer defaults to 180-320 summary words; use `--summary-min-words` and
`--summary-max-words` when the task specifies different bounds. It rejects missing
facets, unsupported IDs, evidence outside the gated coverage union, all-unresolved
drafts, in-bundle drafts, and malformed response fields. It reconstructs paper IDs,
integer citation pages, claim paths, and locator strings from verified bindings. It
recomputes the full unpaged coverage pack independently; a brief page never weakens or
replaces that gate. It guarantees structural and identity integrity; you must still
review semantic entailment and completeness and revise the in-memory draft when
needed. Return the last successful finalizer JSON verbatim without modification.

Read [references/querying.md](references/querying.md) for policy and failure semantics,
[references/adaptive-format.md](references/adaptive-format.md) for exact answer
bindings, [references/entity-graph-format.md](references/entity-graph-format.md) for
graph authority boundaries, and [references/retrieval-format.md](references/retrieval-format.md)
for the pinned semantic projection.
