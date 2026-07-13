# Confluence eight-hour round-trip campaign

This directory defines and validates an immutable evidence package for an
eight-hour campaign that edits downloaded Confluence page workspaces locally,
uploads them, and verifies the result through both the Confluence API and an
authenticated browser.

The campaign tools are independent from the Confluence skill. The live
materializer snapshots already-produced evidence; it does not contact
Confluence or mutate a page. The validator reads only the immutable package and
does not accept an unbound success flag as proof.

## Run the live campaign

1. Record the timezone-aware campaign start when work actually begins. Capture
   every page's authenticated browser baseline inside the campaign and ensure
   the earliest baseline is captured within five minutes of the start. The
   materializer derives each baseline time from the source screenshot's
   filesystem modification time, so do not rewrite or replace the baseline
   later.
2. Exercise the four live fixtures and keep their workspaces under
   `campaign/workspaces/<page-id>/` in the live batch source. For every page,
   finish API verification, authenticated browser verification, and a final
   no-op dry-run. Keep the refreshed `manifest.json`; it is required evidence,
   not optional workspace metadata.
3. Persist the eight multi-page workflow sources at the paths expected by the
   materializer:

   | Milestone | Source path below the live batch root |
   |---|---|
   | `scan` | `space-inventory.json` |
   | `inventory` | `space-inventory.json` |
   | `explore` | `campaign/space-explore-final.json` |
   | `batch-download` | `campaign/batch-manifest.json` |
   | `batch-validate` | `campaign/batch-local-validation-v2.json` |
   | `batch-dry-run` | `campaign/batch-plan-final-noop.json` |
   | `batch-upload` | `campaign/batch-upload-report.json` |
   | `batch-verify` | `campaign/batch-verify-final.json` |

   Generate the filtered exploration receipt separately from the inventory:

   ```powershell
   python skills/roundtrip-confluence-pages/scripts/confluence_batch.py explore `
     evaluations/confluence-8h-live/batch/space-inventory.json `
     --text "Confluence 8h Lab" `
     --output evaluations/confluence-8h-live/batch/campaign/space-explore-final.json
   ```

   The explore receipt must have `status: "queried"`, refer to a verified
   inventory, retain a non-empty filter, and contain exactly the campaign
   pages. Every batch receipt must cover that same exact page set. The
   inventory may contain additional pages.
4. Continue real work until at least eight hours have elapsed from the earliest
   baseline capture. Set `ended_at` to the actual finish time, then materialize
   within 30 minutes into a new, nonexistent package directory:

   ```powershell
   python evaluations/confluence-8h-campaign/materialize_live_campaign.py `
     --source-root evaluations/confluence-8h-live/batch `
     --output evaluations/confluence-8h-campaign/final-live-2026-07-13-0602/campaign.json `
     --campaign-id confluence-8h-2026-07-13 `
     --started-at "2026-07-12T21:57:14-04:00" `
     --ended-at "2026-07-13T06:02:08-04:00"
   ```

   The output directory itself must not already exist. Source and output may
   not contain one another. The materializer reads each source once, stages a
   complete package in a sibling directory, rechecks every source byte before
   publication, and publishes only after all evidence passes.
5. Validate the resulting immutable package:

   ```powershell
   python evaluations/confluence-8h-campaign/validate_campaign.py `
     evaluations/confluence-8h-campaign/final-live-2026-07-13-0602/campaign.json
   ```

`campaign.template.json` documents the generated manifest shape. It is useful
for reviewing the contract, but copying it and filling timestamps is not proof
of a live campaign. Use the materializer for the final package.

## Manifest contract

The final manifest binds all of the following:

- `schema_version`, a non-empty campaign ID, timezone-aware start and end, and
  a minimum duration of at least eight hours;
- one `confluence` identity containing an origin-only HTTPS `base_url` and a
  non-empty `space_id` shared by every page and workflow artifact;
- a hash-bound `timeline.report` generated at
  `evidence/campaign-timeline.json`;
- the exact required coverage-category set;
- a hash-bound `multi_page_workflow.report`; and
- one or more non-overlapping phases that start and end with the campaign and
  leave no gap.

Every completed test case must use a unique ID and page ID, have
`status: "passed"`, declare at least one recognized coverage category, and
contain four distinct `{ "path": "...", "sha256": "..." }` evidence records:

- `api_report`;
- `browser_ground_truth`;
- `noop_dry_run`; and
- `workspace_manifest`.

All evidence paths are relative to the package root. Screenshot and workflow
artifact paths are relative to their owning report. Absolute paths, directory
escapes, symlink escapes, missing files, and incorrect lowercase SHA-256
digests are rejected.

## Per-page evidence binding

An API report must have `status: "verified"`, the case page ID, a non-empty
operation ID, a desired-state SHA-256, a positive remote version, a
timezone-aware `verified_at`, and at least one check with `passed: true`.

The browser report must bind the same page, operation, desired state, remote
version, tenant page URL, and exact API-report digest. Its verification time
must follow the API verification within the phase. It needs passing checks, one
decodable PNG or JPEG baseline, and at least one decodable final screenshot
whose digest differs from the baseline.

The no-op report must have `status: "dry-run"` and prove convergence for that
same page, desired state, and remote version. Page, body, metadata, labels,
content state, attachments, and every suppressed-change field must show no
change. Attachment, label, and content-state synchronization must be enabled.

The workspace manifest must identify the same tenant, space, page, canonical
page URL, remote version, operation, and desired-state digest. Its
`last_verified_at` must follow `downloaded_at` and fall between API and browser
verification. This prevents a detached report triad from being reused with a
different or stale downloaded workspace.

## Multi-page workflow receipt

The workflow report must contain these operations exactly once and in this
order:

1. `scan`
2. `inventory`
3. `explore`
4. `batch-download`
5. `batch-validate`
6. `batch-dry-run`
7. `batch-upload`
8. `batch-verify`

Each operation must have `status: "passed"`, the exact campaign page set, a
campaign-bounded `captured_at`, and a hash-bound artifact. The first operation
sets `previous_artifact_sha256` to `null`; every later operation sets it to the
digest of the preceding artifact. `artifact_chain_head_sha256` must equal the
last artifact digest. Non-inventory receipts must be distinct.

The artifacts are validated semantically as well as by hash. Scan and inventory
must be verified and include all campaign pages in the declared tenant and
space. Explore must be a distinct persisted filtered query. Batch download must
bind the exact inventory digest; batch upload must bind the exact batch-manifest
digest. Batch download, dry-run, and upload must share the batch ID, and
validate, dry-run, upload, and verify must share one complete dependency order.
All per-page statuses and no-op or verification payloads must pass their
operation-specific checks.

## Real-duration timeline

An eight-hour difference between user-entered manifest timestamps is necessary
but insufficient. The hash-bound timeline report additionally proves that:

- every page has one baseline receipt bound to its exact screenshot and page;
- the earliest baseline filesystem capture occurred no more than five minutes
  after campaign start;
- at least eight real hours elapsed from that baseline to materialization;
- the latest API and browser verification times are derived from the bound
  per-page reports;
- start, baseline, API verification, browser verification, end, and
  materialization occur in chronological order;
- `ended_at` is not in the future and materialization occurs no more than 30
  minutes later; and
- workflow receipt times and all nested `*_at` timestamps remain inside the
  campaign interval.

Those six milestones are canonical-JSON hashed and chained with
`previous_sha256`; the timeline stores the final
`milestone_chain_head_sha256`. The validator recomputes the complete chain and
cross-checks every timestamp and baseline against the rest of the package.
