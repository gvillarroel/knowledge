# Reliable Confluence synchronization

Use the normal CLI to synchronize a registered source:

```sh
know --verbose sync confluence --key research --space ENG
```

Omit `--space` to synchronize all registered Confluence sources for that key, including sources registered with only CQL. A per-run override does not change the saved source configuration:

```sh
know --verbose sync confluence --key research --space ENG \
  --workers 4 --page-size 25 --timeout 90 --max-retries 4
```

## What changes for large spaces

Space synchronization first resolves the space key to its numeric ID. It requests a small inventory of current published pages, then downloads their storage bodies concurrently. The inventory does not request page bodies. Each worker reuses its own HTTP session; the queue holds at most twice the worker count.

The distinction between a space key and ID matters: the v2 pages endpoint documents `space-id`, not `space-key`. Continuations must stay on the configured origin and endpoint. Missing filters are carried forward; changed filters, repeated cursors, invalid results, and pagination without progress fail the synchronization instead of silently producing an incomplete library. [Atlassian pages API](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/).

CQL synchronization also downloads bodies concurrently and requests content version metadata for cache validation. An explicit CQL expression defines the query scope; a saved space value does not add an implicit clause to that expression.

## Configuration

These options work on both `know add confluence` and `know sync confluence`. Registration saves them; sync arguments override them for that run only. Saved timeouts and retry controls also apply to Confluence search and browsing.

| Option | Default | Meaning |
| --- | --- | --- |
| `--workers` | 4 | Concurrent page downloads, from 1 to 16. |
| `--page-size` | 25 | Items per inventory request, from 1 to 250. |
| `--timeout` | 60 seconds | Read timeout for each request attempt. |
| `--connect-timeout` | 10 seconds | Connection timeout for each request attempt. |
| `--max-retries` | 4 | Retries after the initial GET; 0 disables retries. Maximum: 10. |
| `--max-retry-wait` | 120 seconds | Total retry and shared cooldown waiting budget per request; request execution time is separate. |
| `--max-pages` | 0 | Total selected pages; 0 means all matching pages. |
| `--refresh` | Off | Sync only: ignore cached bodies and fetch every selected page. |

For example, save conservative defaults for a new source:

```sh
know add confluence --space ENG --key research \
  --workers 4 --page-size 25 --timeout 90 --max-retries 4
```

The old `--limit` registration option remains compatible: for a space it controls inventory size, while for CQL it caps the total number of selected pages. Explicit `--page-size` or `--max-pages` takes precedence over the corresponding legacy value. Without an explicit total cap, CQL sync no longer stops implicitly at 100 pages.

A smaller page size reduces inventory response size but adds requests. More workers can help when individual pages are slow, but also consume API quota more quickly. Start with the defaults and use the recorded request/retry counts before increasing concurrency.

## Retry behavior

The shared read client retries timeouts, connection interruptions, truncated/invalid JSON responses, and HTTP 408, 429, 500, 502, 503, and 504. Retries use exponential backoff with jitter. Only GET is exposed by this client. A 503 carrying Atlassian's `SUSPENDED_INACTIVITY` code is permanent rather than transient: the client stops after one request and directs the operator to reactivate the Confluence subscription. A 403 whose Atlassian payload says the caller cannot access Confluence also stops immediately and directs the operator to grant the configured account Confluence app access or replace its credentials. Remote response bodies are not copied into either diagnostic.

`Retry-After` is a minimum delay, including when supplied as an HTTP date. Rate limiting and server-directed waits pause the other workers too. If the required wait exceeds the configured budget, the operation stops with a clear diagnostic; it never retries earlier by truncating the server delay. Authentication failures, other permanent HTTP errors, schema errors, TLS certificate failures, and redirects are not retried.

A failed page is recorded and other pages can finish. Exhausted rate limiting or invalid authentication stops the request group. No failed page is silently counted as synchronized. This follows Atlassian's guidance on bounded backoff and coordination between workers. [Atlassian rate limiting](https://developer.atlassian.com/cloud/confluence/rate-limiting/).

## Partial results and recovery

Each successful body is written atomically to a checkpoint with a content digest. Checkpoints are isolated by store, tenant, account, and source selection. A subsequent run inventories the remote source again and reuses a body only when its digest and freshly listed version/metadata still match. Missing version metadata or a corrupt checkpoint causes a fresh download.

The source directory is replaced only after every selected page has been downloaded and converted successfully. On an incomplete run:

- the last complete Markdown corpus and `last_synced_at` remain unchanged;
- the command exits with code 1;
- structured output contains `failed` entries with page IDs, sanitized errors, and a `report` path;
- other registered sources can continue after a handled Confluence synchronization failure; and
- successful page checkpoints remain available for the next attempt.

Retry the same command after the underlying problem has cleared:

```sh
know --json sync confluence --key research --space ENG
```

The result reports `pages`, `downloaded`, `reused`, `requests`, `retries`, and `complete`. Inspect the report named in the output for per-page failures. Reports omit authentication values and response bodies.

Checkpoint bodies are private source content. They live below the store's configured temporary cache in `knowledge-cache/<key>/confluence/<source-id>/confluence-v1/<scope-digest>/`; keep that cache out of version control and sharing. Deleting it loses download reuse but does not delete the published corpus.

Publication preserves authored files and removes stale generated pages only when their frontmatter identifies this source. A generated filename that would collide with an authored file stops publication. A process lock prevents two syncs from writing the same source. Publication uses a staged directory with rollback on local failure and recovery of an interrupted directory swap. Staging, recovery files, and locks stay in the store-root `.confluence-sync/` control directory, outside the key directories that are exported. A hard process termination can leave control files behind, but the operating system releases the process lock. Confluence does not provide a transaction spanning all remote pages, so a running synchronization is not a globally consistent point-in-time snapshot of concurrent edits.

## Verification

Run the focused offline suite:

```sh
python -m pytest -q tests/test_source_helper_coverage.py tests/test_coverage_paths.py tests/test_cli.py tests/test_browse_coverage.py -k confluence
python scripts/check_coverage.py --threshold 80
```

The local HTTP integration test serves 128 substantial page bodies with real persistent connections. It injects HTTP 429/503 responses, a truncated transfer, and a permanent page failure, then verifies that the next attempt reuses 127 pages and downloads only the missing one. Unit cases cover timeouts, retry exhaustion, unsafe pagination, changed versions, corrupt caches, source locking, and failed publication.

For a live read-only access probe using configured `CONFLUENCE_*` credentials:

```sh
python scripts/confluence_sync_smoke.py
```

After explicitly authorizing remote fixture creation:

```sh
python scripts/confluence_sync_smoke.py --create-fixture --pages 40 --body-kib 32
```

The command above creates a private test space. Confluence Free does not support private spaces, so its site-visible form must be selected explicitly:

```sh
python scripts/confluence_sync_smoke.py --create-fixture --site-visible-fixture --pages 40 --body-kib 32
```

A site-visible fixture is accessible to signed-in users of that Confluence site; it does not enable anonymous access. Both forms use a clearly synthetic space name, journal each attempted write, never retry a POST, run the public CLI twice, and verify page identities and unchanged-version reuse. The helper does not modify or delete existing pages. It requires an available v2 space-creation API, and private mode also requires permission to create private spaces. Created fixtures are left in the isolated space named in the report.

On 2026-08-28, the configured tenant returned HTTP 503 for all three preflight attempts. A follow-up on 2026-09-01 established that the site root, v1 API, v2 API, and current-user endpoint all returned `SUSPENDED_INACTIVITY`: Atlassian had deactivated this Confluence Cloud subscription after inactivity. Atlassian's public Confluence and developer status pages were operational, so this was tenant-specific rather than a platform incident. On 2026-09-02, reactivation removed the suspension response, but the configured API identity received `403 FORBIDDEN` with `Request rejected because caller cannot access Confluence`. No remote writes were attempted in any of these runs. Live creation/download verification remains unavailable until the configured identity has Confluence app access; the local HTTP and unit verification must not be presented as a successful tenant test. Do not deliberately trigger Atlassian rate limits: inject those failures locally.

This remains a read-oriented Markdown export. Native page editing and storage-preserving round trips retain their separate [ADR 0013 contract](../.specs/adr/0013-confluence-storage-roundtrip-contract.md). See [ADR 0113](../.specs/adr/0113-make-confluence-sync-bounded-and-resumable.md) for the synchronization decision.

[Back to the documentation index](README.md).
