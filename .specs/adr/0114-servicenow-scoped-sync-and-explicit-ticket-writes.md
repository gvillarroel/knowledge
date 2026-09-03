---
adr: "0114"
title: "ADR 0114: Add ServiceNow Table API Sources with Explicit Incident Writes"
summary: "Use scoped Table API reads for local knowledge and isolate incident creation behind an explicit command."
status: "Accepted"
date: "2026-08-28"
product: "knowledge"
owner: "Platform Architecture"
area: "Source Integrations"
tags: [servicenow, tickets, knowledge, synchronization, security]
---

# ADR 0114: Add ServiceNow Table API Sources with Explicit Incident Writes

## Context

The CLI already synchronizes ticket and documentation sources but has no
ServiceNow adapter. The requested capabilities are ticket creation, ticket
reading, and synchronization with a native ServiceNow collection.

The Table API covers incident and knowledge tables without a new runtime
dependency. A ServiceNow developer portal account is not itself an instance
or an authenticated REST integration.

## Decision

- Add ServiceNow to registration, search, synchronization, local browsing, and
  normalized Markdown export.
- Treat knowledge bases as the supported documentation collection. Discover
  bases through kb_knowledge_base and scope article reads by the exact
  kb_knowledge_base reference on kb_knowledge.
- Keep incident creation explicit under the ServiceNow command group. It sends
  one POST and verifies the returned identity with a separate GET. Normal sync
  never creates, updates, or deletes remote records.
- Support existing bearer tokens and instance Basic credentials through the
  store's credential references. Reject literal password/token registration
  values, require HTTPS origins, refuse redirects, and omit remote error bodies.
- Bind source identity to instance, table, and effective filter. Require exact
  source selection when multiple registered connections could match.
- Fetch and validate selected pages before replacing any record file. Use
  stable sys_id filenames, preserve unreturned records, and report truncation.
  Do not infer deletion from a limited or ACL-filtered result set.
- Validate typed knowledge-base and assignment-group scopes against returned
  raw values. Arbitrary encoded filters remain subject to ServiceNow's query
  handling and are not security controls.
- Keep live tenant verification separate from mocked API tests. A missing
  instance, email verification, unavailable credentials, or instance policy
  remains an explicit prerequisite, not a passing live test.

## Consequences

Existing library and OKF contracts remain intact. ServiceNow does not require
an additional SDK or a production subscription merely to run local tests.

The first integration is a pull/upsert workflow with an explicit incident
creation operation. It is not a bidirectional editor, catalog-ordering client,
deletion-aware mirror, OAuth token manager, or lossless article round trip.
Per-file atomic replacements are not a multi-file filesystem transaction.

The workflow and acceptance steps are documented in
[ServiceNow integration](../../docs/servicenow.md).
