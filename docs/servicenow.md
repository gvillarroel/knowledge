# ServiceNow integration

ServiceNow support adds explicit incident creation, ticket reads, remote search,
and a repeatable local Markdown collection. Synchronization reads from ServiceNow;
it does not publish local edits or create remote records.

## What is supported

| Operation | Command or table |
| --- | --- |
| Create one incident and read it back | `know servicenow create-ticket` |
| Read an exact ticket number or sys_id | `know servicenow read-ticket` |
| Search ticket summaries and saved filters | `know search servicenow` |
| Synchronize tickets | `incident`, `problem`, `change_request`, `sc_task`, `sc_req_item` |
| Discover knowledge bases | `know servicenow knowledge-bases` |
| Synchronize articles in a knowledge base | `kb_knowledge` with `--knowledge-base SYS_ID` |
| Read synchronized content locally | `know browse servicenow` and `know export` |

A ServiceNow knowledge base is the supported analogue of a documentation space.
The `kb_knowledge_base` table identifies bases, and `kb_knowledge`
contains their articles. See the official
[Knowledge Management component reference](https://www.servicenow.com/docs/r/servicenow-platform/knowledge-management/Installed-with-km-core.html).

Creating catalog requests, changing tickets, publishing articles, attachments,
journal history, and configuring Agent Workspaces are outside this integration.
The supported write creates an `incident`; it does not use the Table API
to bypass catalog ordering, change approvals, or instance business rules.

## Account and instance prerequisites

You need an actual instance origin such as `https://dev123456.service-now.com`
and an identity allowed to access the relevant tables and fields. The developer
portal login is separate from credentials for the instance REST API.

For development, ServiceNow offers free Personal Developer Instances. Register
on the [Developer Portal](https://developer.servicenow.com/), complete the
required account verification, and request a PDI. Availability and onboarding
steps are controlled by ServiceNow. PDIs are for learning and experiments, not
production. See the [official PDI guide](https://developer.servicenow.com/print_page.do?category=developer-program&identifier=obtaining-a-pdi&module=guide&release=yokohama).

Use a dedicated integration identity with only the required access. Table,
record, and field ACLs and REST access policies remain authoritative. Do not
make tables public or disable ACLs to get an integration test to pass.

## Configure credentials

Set these environment variables through your secret manager or local shell:

| Variable | Meaning |
| --- | --- |
| `SERVICENOW_BASE_URL` | HTTPS instance origin, without a path or query |
| `SERVICENOW_TOKEN` | Existing OAuth bearer access token |
| `SERVICENOW_USERNAME` | Instance username for Basic authentication |
| `SERVICENOW_PASSWORD` | Instance password for Basic authentication |

Use either bearer authentication or Basic authentication as allowed by your
instance. An environment bearer token takes precedence unless you explicitly
choose username/password flags. This integration does not mint or refresh
tokens; your credential provider must supply a current token.

Registration stores `$env:NAME` references, not resolved secrets. You can
also use an existing `$name` reference from the store's credential manager.
Literal `--token` and `--password` values are rejected. Keep references in
single quotes in both PowerShell and Bash so the shell does not expand them.

```sh
know add key itsm
know add servicenow --key itsm --table incident --query 'active=true'
know list sources --key itsm --type servicenow
```

The base URL and authentication flags can instead be provided explicitly:

```sh
know add servicenow --key itsm --table incident --query 'priority=1' --base-url https://dev123456.service-now.com --token '$env:SERVICENOW_TOKEN'
```

Each registration's identity includes the instance, table, and effective scope.
Different filters on the same table produce different sources. When several
sources share a key, remote operations require `--source-id` to avoid
guessing the intended connection. Do not mix `--key` with connection
overrides; use the registered connection or an explicit direct connection.

## Create and read a ticket

Preview an incident first. A dry run does not resolve credentials or contact
ServiceNow:

```sh
know servicenow create-ticket --key itsm --short-description "[Integration test] Verify know ServiceNow access" --description "Disposable development test of ticket creation, reading, and synchronization." --impact 3 --urgency 3 --correlation-id know-servicenow-smoke-001 --dry-run
```

After checking the target and payload, remove `--dry-run` to create the
incident. The command sends exactly one POST, then independently GETs the
returned `sys_id`. A successful result contains `created: true`,
`verified: true`, the ticket number, sys_id, native URL, and record.

Use `--caller-id SYS_ID` if your instance requires a caller.
`--description-file PATH` reads a UTF-8 description of up to 1 MiB.
A registered assignment group is inherited and cannot be silently replaced.
The instance may impose additional mandatory fields or business rules; an API
rejection is a failed creation, not permission to weaken those controls.

```sh
know servicenow read-ticket INC0010001 --key itsm
know search servicenow "VPN" --key itsm --limit 25
```

Replace the example number with the number returned by creation. An exact
ticket read uses the instance and table and enforces a registered assignment
group, but does not apply arbitrary saved query predicates such as active state.

POST requests are never retried automatically. If the request times out, inspect
the instance before trying again. If creation succeeds but read-back fails, the
error identifies the created sys_id and warns against repeating creation.
`--correlation-id` is a useful external reference, not a server-enforced
idempotency key.

Direct reads and writes without `--key` use the environment or explicit
connection options and do not require creating a local store.

## Synchronize tickets

```sh
know sync servicenow --key itsm
know browse servicenow --key itsm
know export --key itsm
```

`know sync --key itsm` includes ServiceNow alongside other source types.
Use the exact update command returned at registration to refresh just one
source.

To select a team's tickets, register an explicit group sys_id:

```sh
know add servicenow --key itsm --table incident --assignment-group 0123456789abcdef0123456789abcdef --query 'active=true' --limit 1000 --page-size 100
```

Replace the example group id with an authorized group on your instance.

## Synchronize a knowledge base

Discover accessible base identities first:

```sh
know servicenow knowledge-bases
know add key service-knowledge
know add servicenow --key service-knowledge --table kb_knowledge --knowledge-base 0123456789abcdef0123456789abcdef --query 'workflow_state=published'
know sync servicenow --key service-knowledge
know browse servicenow --key service-knowledge --format television
know export --key service-knowledge
```

Replace the example base id with one returned by discovery. Article HTML is
normalized to readable text; the requested source fields remain available in a
JSON section. This is not a lossless ServiceNow editor round trip.

## Synchronization guarantees and limits

- Pages use a stable sys_id tie-breaker, at most 100 records per request, and a
  default total cap of 1,000 records. `--limit` changes the total cap.
- Pagination advances by the requested window, not by the number of records
  remaining after ACL filtering. Link headers are used only as pagination
  signals; their URLs are never followed with credentials.
- `truncated` and `next_offset` expose a bounded result. Remote search
  accepts `--offset` for continuation. To cover more records during sync,
  increase the registered limit or use separately registered, narrower scopes.
- Sync upserts records by validated sys_id under
  `<store>/<key>/servicenow/<source-id>/records/<sys_id>.md`.
  Repeated sync does not duplicate records. Unreturned records are retained
  because omission may mean filtering, a cap, changed ACLs, or remote deletion.
  This is an accumulated local collection, not a deletion-aware mirror.
- All selected pages and documents are validated before publication starts.
  A fetch, identity, timestamp, or scope error preserves the previous files.
  Changed files are staged and replaced individually. Publication across
  multiple files is not a filesystem transaction.
- Authored files outside the managed records are preserved. The normal source
  metadata records the query, last sync time, record counts, changed and
  retained counts, and truncation status.
- Configured knowledge-base and assignment-group scopes are also checked
  against returned raw reference values. Missing scope fields fail closed.
- Encoded queries cannot contain JavaScript, newlines, `^NQ`, or `^EQ`.
  Register separate sources for separate disjunctive scopes. ServiceNow can
  ignore invalid query terms depending on instance configuration; have an
  administrator review `glide.invalid_query.returns_no_rows` and test custom
  filters with the intended integration identity.
- HTTPS certificate verification remains enabled; redirects to login pages or
  other hosts are refused. Error messages omit remote response bodies and
  authentication values.
- GET retries are limited to three attempts for HTTP 429/502/503/504, with at
  most five seconds of waiting per retry. Other errors are surfaced directly.

These API behaviors follow the official
[Table API reference](https://www.servicenow.com/docs/r/xanadu/api-reference/rest-apis/c_TableAPI.html).
Filters are not an authorization boundary; instance ACLs control access.

## Verification

The automated suite uses simulated API responses and checks command routing,
authentication, pagination, ACL-filtered pages, redacted failures, ticket
read-back, repeat sync, Markdown export, and preservation of previous content:

```sh
python -m pytest -q tests/test_servicenow.py
python scripts/check_coverage.py --threshold 80
```

Live acceptance requires a provisioned instance and usable API credentials:
create one clearly labeled development incident, read its returned number,
synchronize a query matching that incident, inspect its Markdown and exported
archive, then repeat the same sync and confirm no duplicate record file.
Discover one permitted knowledge base and verify an article's content against
its native ServiceNow page.

Automated API simulations do not establish that a particular tenant's account,
ACLs, plugins, or business rules have been verified. Do not report live
acceptance until those operations have actually succeeded.

[Back to the documentation index](README.md).
