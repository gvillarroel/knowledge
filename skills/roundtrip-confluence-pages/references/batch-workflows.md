# Safe multi-page workflows

## Contents

- Inventory and local exploration
- Batch download and deterministic edits
- Dependency-aware ordering
- Preflight, upload, and resume
- Evidence architecture
- Verification and completion
- Failure semantics

## Inventory and local exploration

Scan a numeric space ID into a persisted JSON inventory:

```bash
python scripts/confluence_batch.py scan-space SPACE_ID ./space-inventory.json
```

The scan asks the page-list endpoint explicitly for current `subtype=page`
items and records searchable visible text,
storage macro names, ADF node types, global labels, linked domains, and
attachment filenames. Visible-text extraction suppresses CSS, JavaScript,
templates, and other non-rendered containers. When Confluence's Excel viewer
returns an escaped workbook fragment, the scanner reparses only that exact
viewer container so worksheet labels and calculated cell values stay
searchable without indexing embedded styles. A returned item is rechecked
before its ADF or rendered body is fetched, so an API response that unexpectedly
contains a live doc or another unsupported page subtype makes the inventory
partial rather than silently mixing content contracts. Blog posts, databases,
whiteboards, content-tree Smart Link items, and slides use separate inventory
workflows and are not included. Every pagination link must remain on the configured
tenant's `/wiki/api/v2/pages` endpoint and preserve the exact `space-id`,
`status=current`, and `subtype=page` invariants. Malformed listing rows or
pagination objects, unexpected query fields, duplicate filter values, invalid
limits, repeated cursors, repeated page IDs, non-numeric IDs, and pages returned
from another space make the inventory
partial instead of complete. A throttled or interrupted scan is likewise saved
with `status: partial`, its collected pages, the error stage, and an explicit
`rate_limited` flag. Do not use a partial inventory to define a complete batch.

Explore the inventory locally without credentials or network requests. Filters
within and across content categories are combined with AND semantics. Repeated
`--page-id` values are the explicit selection union and are then combined with
the other categories using AND. Text and attachment filters are
case-insensitive substrings; macro, ADF node, label, and domain filters are
case-insensitive exact matches.

```bash
python scripts/confluence_batch.py explore ./space-inventory.json \
  --text "release" --macro status --adf-node table \
  --label reviewed --domain developer.atlassian.com --attachment .png \
  --page-id 123456 --page-id 789012 \
  --output ./space-selection.json
```

`--output` writes the exact local query result atomically, so a selection can
be reviewed, hashed, or consumed by later automation without rescanning the
tenant. Every explicit `--page-id` must exist in the inventory; the command
does not silently reduce an explicit page set when one ID is absent.

## Batch download and deterministic edits

Download every selected page into `workspaces/PAGE_ID` and persist
`batch-manifest.json`:

```bash
python scripts/confluence_batch.py batch-download ./space-inventory.json ./release-batch \
  --page-id 123456 --page-id 789012
```

The manifest pins the inventory hash, tenant, space, page set, and workspace
paths. Existing workspace page IDs, tenant roots, and numeric space IDs are
cross-checked against those batch fields. Workspace paths may not traverse a
symbolic link or Windows junction. Use `--resume` only with that same inventory
and filter result. Invalid existing workspaces are not overwritten
automatically.

Apply deterministic sidecar and storage edits only after every workspace
validates and every candidate parses:

```bash
python scripts/confluence_batch.py batch-edit ./release-batch/batch-manifest.json \
  --append-storage-file ./approved-fragment.xml \
  --add-label roundtrip-reviewed --remove-label needs-review \
  --title-prefix "[Reviewed] " --title-suffix " — 2026"
```

`--append-storage` appends the supplied XML fragment verbatim. The command
rejects malformed storage, empty titles, invalid labels, and attempts to add and
remove the same label before writing any workspace. It then refreshes each local
ground-truth record. This is prevalidated local sequencing, not transactional
filesystem rollback.

## Dependency-aware ordering

The batch commands infer dependencies from actual `ri:page` elements in every
local `page.storage.xml`. A `ri:content-id` that matches a batch page ID or a
`ri:content-title` that uniquely matches a manifest or desired local page title
adds a source-to-consumer edge. References in comments and CDATA are ignored,
and references to pages outside the batch do not constrain the batch. A
concrete non-batch `ri:content-id` is authoritative and is never reinterpreted
through a coincidentally matching title. A title-only reference with a
non-`@self` `ri:space-key` is also treated as external because the numeric batch
space ID cannot prove that key is local.

Add an explicit dependency when the relationship is dynamic or otherwise not
represented by an `ri:page` element:

```json
{
  "page_id": "456",
  "title": "Consumer page",
  "workspace": "workspaces/456",
  "depends_on": ["123"]
}
```

Each `depends_on` value must identify another page in the same manifest. The
workflow rejects unknown IDs, duplicates, self-dependencies, ambiguous title
references, conflicting ID/title references, and dependency cycles. Edit
dependencies before the first upload; changing the manifest invalidates resume
evidence by design.

Validation, planning, upload, API verification, and completion use the same
stable topological order. Independent pages retain their manifest order, while
every referenced source is processed before its consumers. Their reports expose
both `dependency_order` and the merged `dependencies` map for auditing.

## Preflight, upload, and resume

Validate all workspaces, then build all remote plans before any upload:

```bash
python scripts/confluence_batch.py batch-validate ./release-batch/batch-manifest.json
python scripts/confluence_batch.py batch-plan ./release-batch/batch-manifest.json
```

`batch-plan.json` includes page, attachment, label, and content-state changes.
The planner always uses the per-page optimistic locks with `force: false`. A
single local validation or remote planning failure prevents batch upload from
starting. The plan binds the exact batch-manifest SHA-256, per-page desired
state digests, and inferred dependency graph. Batch upload rechecks those local
bindings before the first mutation, before each later page, and inside the
per-page uploader.

Upload sequentially in the recorded dependency order:

```bash
python scripts/confluence_batch.py batch-upload ./release-batch/batch-manifest.json \
  --message "Reviewed multi-page release update"
```

The command writes `batch-upload-report.json` after every page. `status:
verified` means every page passed API verification; it does not replace browser
ground truth. A failure, including HTTP 429, stops new uploads and produces
`status: partial`. Earlier pages are not rolled back. A page that failed after
mutation began is marked `mutation_state: unknown-partial` and must be inspected
before resuming.

After resolving the error, resume only the same manifest:

```bash
python scripts/confluence_batch.py batch-upload ./release-batch/batch-manifest.json \
  --resume --message "Resume reviewed multi-page release update"
```

Resume verifies the batch-manifest hash, revalidates and replans the complete
batch, skips report entries already API-verified, and retries failed or pending
entries without force. Immediately before skipping a verified row, it performs
another live no-op preflight so a remote edit after the all-page plan cannot be
mistaken for a current success.

## Evidence architecture

Treat batch evidence as an index over independently verified page operations, not as a replacement for page-level evidence.

- `batch-manifest.json` pins the inventory hash, tenant, space, selected page set, workspace paths, explicit dependencies, and the stable dependency order used by every later stage.
- `batch-plan.json` records the complete preflight before mutation. A plan is invalid after the batch manifest or any desired workspace state changes.
- `batch-upload-report.json` is written before the first mutation and after every page attempt. It binds the exact batch-manifest SHA-256, dependency graph, ordered per-page results, resume history, partial failures, and the explicit facts that the operation is non-atomic and no rollback was attempted.
- Each page retains its own mutation journal, operation ID, desired-state SHA-256, immutable remote storage/ADF/view/restrictions snapshots, API report, current remote version, and manifest lock. A successful batch row must point to an API-verified page operation; it cannot make stale page evidence current.
- A resumed batch skips an earlier verified row only when its desired-state digest, API operation ID, remote version, API-report hash, and refreshed manifest locks still match and a fresh remote preflight is a no-op. A local edit or stale report makes that row pending again even when the batch-manifest file itself did not change.
- `verification/browser-ground-truth.json` binds authenticated observations to that page's exact API operation, report hash, desired-state digest, remote version, tenant/page URL, required check IDs, and screenshot hashes. Reusing a prior screenshot or recording observations before the API verification fails the page gate.
- `batch-verify-report.json` re-runs API verification for every page in dependency order. `batch-completion-report.json` aggregates page completion gates only after every current API report and browser record agree.

Keep failed and partial reports as audit evidence. Resume creates a new history entry and continues the same manifest; it does not erase an earlier unknown-partial mutation or claim transactionality.

Place custom batch report outputs outside `workspaces/`. Report commands reject
paths that would overwrite a page sidecar, API/browser evidence, the batch
manifest, or another reserved batch artifact.

## Verification and completion

Re-run deterministic API verification for every page:

```bash
python scripts/confluence_batch.py batch-verify ./release-batch/batch-manifest.json
```

Create each page's authenticated `verification/browser-ground-truth.json` as
described in the main workflow, then require every page-level completion gate:

```bash
python scripts/confluence_batch.py batch-completion-gate \
  ./release-batch/batch-manifest.json
```

The batch completion result is `verified` only when every page independently
has current API evidence, passing browser checks, and valid screenshot hashes.

## Failure semantics

- Batch operations are sequential and never atomic across Confluence pages.
- The workflow never claims or attempts rollback of earlier successful pages.
- HTTP 429 is surfaced as `rate_limited: true`; wait for the service window,
  inspect the partial report, and resume deliberately.
- `partial` is not success. Inspect every failed and pending page.
- There is no batch force option. Redownload any page whose version or
  attachment lock diverged.
- Page moves, attachment deletion, restrictions, comments, and other
  server-owned surfaces remain outside this workflow.
