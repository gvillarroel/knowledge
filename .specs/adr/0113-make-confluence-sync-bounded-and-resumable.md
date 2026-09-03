---
adr: "0113"
title: "ADR 0113: Make Confluence Sync Bounded and Resumable"
summary: "Separate scoped page discovery from bounded downloads, retry safe reads, and publish only complete snapshots."
status: "Accepted"
date: "2026-08-28"
product: "knowledge"
owner: "Platform Architecture"
area: "Confluence Interoperability"
tags:
  - confluence
  - synchronization
  - reliability
  - concurrency
---

# ADR 0113: Make Confluence Sync Bounded and Resumable

## Context

The Confluence reader used fixed 60-second HTTP timeouts without retries. Space
listing expanded all storage bodies into memory and sent an unsupported
space-key filter to the v2 pages endpoint. CQL downloads ran sequentially and
used an implicit 100-page cap. A failed request lost the opportunity to reuse
previously downloaded pages. Local publication cleared the source directory
before writing the replacement.

ADR 0013 and ADR 0016 establish separate authority for native page editing and
Markdown publication. Neither contract should acquire automatic concurrent
writes or generic write retries as a side effect of improving the read CLI.

## Decision

1. Resolve space keys through the v2 spaces API and list current published pages
   with the numeric space-id filter. Fetch metadata in small batches without
   body expansion. CQL discovery expands version metadata.
2. Download individual bodies with a bounded thread pool, a bounded pending
   queue, and a separate persistent HTTP session per thread. Default to four
   workers and 25 inventory items.
3. Share a read-only client across sync, search, and browsing. Retry transient
   GET failures with bounded exponential backoff and jitter. Honor Retry-After
   as a minimum delay, coordinate cooldowns across workers, and stop when the
   required wait exceeds the explicit budget. Never retry authentication,
   certificate, redirect, or other permanent failures as transient problems.
   Treat Atlassian's `SUSPENDED_INACTIVITY` 503 as a permanent site state and
   report the required administrative reactivation after one request. Treat an
   explicit `caller cannot access Confluence` 403 as a permanent account-access
   state, stop the request group, and direct the operator to grant app access or
   update the configured credentials without exposing the remote response body.
4. Keep pagination on the configured origin and endpoint. Carry forward missing
   scope filters and reject changed filters, malformed continuations, repeated
   cursors, and non-progressing inventories.
5. Checkpoint each downloaded page atomically, with a digest and isolation by
   local store, remote tenant, account, and selection. Re-enumerate before reuse;
   require matching current version and metadata. A corrupt or unverifiable
   checkpoint is a cache miss.
6. Publish only after all selected pages succeed. Preserve the prior corpus and
   successful sync timestamp on partial failure, report failures explicitly,
   exit unsuccessfully, and retain completed checkpoints. Continue other
   registered sources after a handled Confluence sync failure.
7. Preserve authored files during publication; remove only stale documents
   identified as this source's generated pages. Use a process lock, staged
   publication, rollback on a local commit failure, and recovery after an
   interrupted directory swap. Keep staging, backup, and lock files in a
   store-root control directory outside exported key directories.
8. Persist validated resource/retry controls at registration and support
   transient overrides on sync. Preserve explicit legacy limit behavior while
   providing distinct page-size and max-pages controls. No implicit CQL total
   cap remains when the user has not requested one.
9. Keep live fault injection off Atlassian infrastructure. Exercise failures
   through mocks and a local HTTP server. A live helper may create only an
   explicitly authorized isolated fixture, default to private, require a separate
   explicit flag for a site-visible Confluence Free fixture, journal each write
   before sending it, and never blindly retry a potentially committed POST.

## Consequences

Large bodies no longer accumulate for the whole space in memory. Healthy pages
can finish despite an isolated page failure, and the next attempt can reuse
their verified bodies. Repeated unchanged synchronizations still perform
inventory requests but avoid body downloads. Credential-bearing requests cannot
follow a hostile continuation or redirect.

The implementation uses additional disk space for checkpoints and staged
snapshots. A space-wide synchronization is not a transaction against concurrent
remote edits. Repeated permanent failures require user or service repair, and
long server cooldowns can intentionally stop the run. A failed live preflight
does not establish live download success.

The local HTTP test validates a 128-page corpus with throttling, transient
server failures, a truncated response, and resume after a permanent page error.
The configured tenant's 2026-08-28 preflight returned HTTP 503 on every attempt,
so no remote fixture was created in that run. On 2026-09-01, the same response
was diagnosed as `SUSPENDED_INACTIVITY` across the site root and both API
generations while Atlassian's public status was operational. Reactivation on
2026-09-02 removed that suspension response, after which the configured identity
received an explicit Confluence app-access denial. No remote fixture had been
created as of that access check; live verification requires granting that exact
identity Confluence app access first.

## References

- [Confluence pages API](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/)
- [Confluence rate limiting](https://developer.atlassian.com/cloud/confluence/rate-limiting/)
- [Synchronization guide](../../docs/confluence-sync.md)
- [ADR 0013](0013-confluence-storage-roundtrip-contract.md)
- [ADR 0016](0016-separate-md2conf-publishing-authority.md)
