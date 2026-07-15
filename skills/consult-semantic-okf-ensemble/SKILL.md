---
name: consult-semantic-okf-ensemble
description: Consult a published definitive Semantic OKF ensemble read-only. Use for evidence-grounded retrieval or multi-paper synthesis when the bundle contains adaptive lexical, entity-graph, embedding, and ensemble projections and the answer must preserve exact claim IDs, paths, locators, citations, hashes, exclusions, and response contracts.
---

# Consult Semantic OKF Ensemble

Treat `semantic/`, `concepts/`, and accepted RDF as authoritative. Treat `adaptive/`,
`entity-graph/`, `retrieval/`, and `ensemble/` only as hash-bound discovery indexes.
Never edit, repair, or cache inside the supplied bundle.

## MCP-first execution rule

If `semantic_okf_bootstrap_skill` is visible, governed MCP runtime version 1.5.0 is
available. Do not run shell commands, scan for launchers, invoke Python, or inspect the
workspace first. Call `semantic_okf_bootstrap_skill` exactly once and before every
other tool. It accepts no arguments and returns the exact installed skill body in the
closed `semantic-okf-skill-bootstrap/1.0` envelope, bound to the expected skill ID,
SHA-256, and UTF-8 byte count. Follow that body, then use only
`semantic_okf_inspect`, every required `semantic_okf_coverage_brief` page,
`semantic_okf_prepare_answer`, and the terminal `semantic_okf_confirm_answer` for the
structured-answer workflow. The MCP annotations, one-shot bootstrap, server gate, and
treatment-only host shell restriction make this sequence read-only, profile-bound,
deterministic, and byte-confirmed. If another `semantic_okf_*` tool is visible without
`semantic_okf_bootstrap_skill`, fail closed. Continue to the CLI sections only when no
Semantic OKF MCP tool is available.

For hosts that execute Codex non-interactively, use the packaged
`publication-runtime\run_codex.cmd` as the Windows Codex command path. It delegates to the
real Codex executable, parses and verifies the canonical prepared-answer envelope,
verifies the successful digest-only confirmation suffix in Codex's JSONL events, and
atomically replaces `--output-last-message` with the exact confirmed UTF-8 candidate.
For the exact ensemble treatment profile it also disables the general shell tool before
Codex starts; controls retain the shared baseline runtime unchanged. It is transparent
when no Semantic OKF confirmation occurs and fails closed on any
envelope, canonicality, receipt, hash, byte-count, or ordering inconsistency. This host gate is
the only mechanism in the package that can prevent a free-form final agent message
from corrupting already-confirmed IDs or paths after the last tool call; it does not
retrieve evidence and never changes the canonical candidate.

Any failed answer-protocol call—prepare or confirm—publishes nothing and abandons
the active transaction. Recovery begins only with a fresh successful prepare. The
accepted final clean suffix contains one or more successful prepares followed by
exactly one successful terminal confirm.

## Enforce the structured-answer publication gate

When the task requests the `question_id`, `answer`, `evidence` JSON contract, this
gate is mandatory for every non-null answer:

1. When the `semantic_okf_*` MCP tools are available, use them instead of shell
   execution. Call `semantic_okf_bootstrap_skill` once with no arguments, require its
   exact `semantic-okf-skill-bootstrap/1.0` response, follow the returned frozen skill
   body, call `semantic_okf_inspect`, then read every
   `semantic_okf_coverage_brief` page in ascending numeric order, and finish through
   `semantic_okf_prepare_answer` and `semantic_okf_confirm_answer`. The profile-bound MCP server exposes
   no query tools when this skill is not mounted and obtains the bundle only from the
   absolute `SEMANTIC_OKF_BUNDLE` boundary.
2. Otherwise, use the packaged read-only CLI described below. Deep-validate the
   bundle and read every `coverage-brief` page for the exact question.
3. Account for every derived facet and draft only statements supported by reviewed
   claim IDs exposed across those pages.
4. Make one clean initial call to `semantic_okf_prepare_answer` only after coverage
   is complete and the draft has passed
   semantic review, or use `finalize-answer --draft -` in memory when MCP is unavailable.
   Do not depend on a writable workspace or create a draft inside the bundle.
5. Treat the prepare result as the canonical closed envelope
   `semantic-okf-prepared-answer/1.0`. It contains exactly `schema`, `candidate_json`,
   `response_sha256`, and `byte_count`. Semantically review the exact JSON string in
   `candidate_json` without editing, reformatting, reordering, or parsing and
   reserializing it. Verify that `response_sha256` is 64 lowercase hexadecimal
   characters and that `byte_count` describes the UTF-8 candidate. Retry preparation
   only after materially revising the draft; the new envelope replaces the outstanding
   candidate.
6. Submit only the envelope's short digest to `semantic_okf_confirm_answer` as
   `response_sha256`. Never copy `candidate_json`, the full envelope, or any long
   candidate text into the confirm call. Require a successful `confirmed` receipt
   whose SHA-256 and byte count bind the prepared candidate. A missing preparation,
   malformed digest, digest mismatch, or repeated successful confirmation fails closed. If a
   prepare or confirmation attempt fails, that transaction publishes nothing and no
   candidate from it remains eligible: call `semantic_okf_prepare_answer` again to
   establish a fresh envelope, then confirm only its new `response_sha256`. Never retry
   confirmation against a stale digest.
7. A successful confirmation is terminal. Do not call any tool again, do not send an
   empty or placeholder digest, and do not repeat confirmation. Immediately emit
   exactly the prepared envelope's `candidate_json` string as the final response.
   Never emit the envelope, digest, receipt, a parsed object, or a reserialized copy. When MCP is
   unavailable, accept only stdout that parses as the requested contract, never merge stderr with `2>&1`,
   and stop on a nonzero exit. Return the last successful finalizer JSON verbatim
   only when MCP is unavailable.
8. Let the finalizer, not the model, construct `paper_ids`, `citations`, `evidence`,
   paths, locator order, and field order.

If validation, coverage, drafting, preparation, confirmation, or CLI finalization
cannot complete, return the task's exact null-answer object instead. Never return a
confirmation receipt or the finalizer's exit-2 error object as an answer.
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
full query when that is the finalizer's only required facet. Keep the draft in memory,
and repeat the exact query and full-pack parameters, including `page_size`, used for
every brief page. With MCP, make one initial `semantic_okf_prepare_answer` call with
the existing `question_id`, `query`, `draft`, bounds, retrieval
parameters, and `page_size`. Do this only after drafting is complete; make another
prepare call only for a materially revised draft. Preserve the exact returned text
as the closed canonical `semantic-okf-prepared-answer/1.0` envelope. Review the exact
`candidate_json` string inside it without reserialization. After verifying the
envelope's 64-character lowercase `response_sha256` and positive `byte_count`, call
the terminal `semantic_okf_confirm_answer` tool with exactly this closed input:

```json
{"response_sha256":"64_LOWERCASE_HEX_FROM_PREPARE_ENVELOPE"}
```

The confirmation call accepts no candidate, `candidate_json`, envelope, mode, draft,
query, question ID, bounds, retrieval parameters, paths, or other fields. Only a
successful `confirmed` receipt whose SHA-256 and byte count match the envelope
authorizes publication. The response to publish is the exact unchanged UTF-8 string in
the envelope's `candidate_json`, never the envelope, digest, or receipt. Confirmation
is non-idempotent and terminal: after the receipt, make no further tool call. When MCP is
unavailable, pipe the draft to standard input and use the CLI:

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
replaces that gate. It
guarantees structural and identity integrity; you must still review semantic
entailment and completeness, revise and prepare again if needed, confirm the exact
envelope digest, and then return the envelope's candidate bytes without modification. Return the last
successful finalizer JSON verbatim only for the CLI fallback.

Read [references/querying.md](references/querying.md) for policy and failure semantics,
[references/adaptive-format.md](references/adaptive-format.md) for exact answer
bindings, [references/entity-graph-format.md](references/entity-graph-format.md) for
graph authority boundaries, and [references/retrieval-format.md](references/retrieval-format.md)
for the pinned semantic projection.
