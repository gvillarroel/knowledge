---
adr: "0013"
title: "ADR 0013: Use Confluence Storage XML as the Page Round-Trip Contract"
summary: "Edit Confluence pages through storage XML and require operation-bound API and browser evidence for every page, including sequential batches."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Confluence Interoperability"
tags:
  - confluence
  - skills
  - round-trip
  - storage
  - verification
---

# ADR 0013: Use Confluence Storage XML as the Page Round-Trip Contract

## Status

Accepted.

## Context

The existing Confluence source adapter normalizes storage-format page bodies to Markdown for read-oriented knowledge export. Markdown is intentionally lossy for Confluence editor extensions: macros, Smart Link appearances, mentions, status parameters, media identifiers, layouts, synced blocks, and Marketplace extension data cannot all be reconstructed from the normalized text.

Confluence exposes multiple page-body representations. ADF describes modern editor structure, but product-specific extension bodies and media services can require server-owned identifiers. Rendered view HTML shows current output but replacing a macro with that output would destroy its dynamic behavior. Storage format is accepted by the page update API and retains the `ac:*`, `ri:*`, macro, link, and attachment references needed for a page round-trip.

Live tenant testing also showed that REST acceptance is weaker than functional acceptance. Historical or guessed macro keys can be stored successfully while the authenticated page renders a macro error, and some current parameters require nested `ri:*` resources rather than plain text. Multi-page work adds another integrity problem: a batch-level success flag cannot safely replace the independently versioned evidence for each page, attachment set, and browser observation.

A dedicated native-editor fixture on page `34373703`, remote version 4, verified H1 through H6, current inline formatting and alignment, nested lists, assigned/due and completed tasks, merged tables, mentions/dates/emoji/status, and eight one-through-five-column layout sections. Regenerated ADF contained 8 layout sections and 22 layout columns, while authenticated screenshots verified their geometry. The same fixture exposed a representation boundary: remote storage and rendered view retained line-through styling, `<small>`, and `<big>`, but regenerated ADF omitted dedicated marks for those legacy-looking forms.

A current-editor fixture on page `34472058` established tenant-native storage keys and parameter shapes for `pagetreesearch`, `blog-posts`, `content-report-table`, `include`, `userlister`, `decisionreport`, `create-from-template`, `iframe`, `roadmap`, and `toc-zone`. It also exposed two additional boundaries. Operation-bound probes found the localized Cards and Carousel options, but both stopped at a Premium-trial gate before insertion, so the evidence established plan gating rather than authoring support. Synced-block storage and regenerated ADF retained resource IDs and embedded source content, while REST `body.view` returned only `Sync Block` placeholders; rendered-view text alone is therefore incomplete evidence for that feature.

A current-editor fixture on page `34897923`, remote version 4, established exact `viewpdf` and `viewxls` storage shapes backed by verified PDF and XLSX attachments. Its operation-bound API evidence passed 20 checks, and authenticated rendering showed the PDF document plus the named Excel worksheet with expected calculated values. Fresh editor probes also showed tenant-specific boundaries: Jira Activities had no accessible Jira site, Jira Chart required an administrator-managed connection, and Assets content was inaccessible. Searches in the `es-ES` editor catalog returned no exact option match for the queried English labels Activity Stream, Team Calendars, Jira Timeline, Word, and PowerPoint; this was not an exhaustive localized catalog inventory.

## Decision

Package `roundtrip-confluence-pages` as a standalone skill whose editable page-body contract is Confluence storage XML.

Each download captures:

- editable storage XML;
- ADF and rendered view as read-only observations;
- page identity, title, parent, status, version, global labels, and page-level content state;
- attachment bytes and SHA-256 hashes;
- restrictions, permitted operations, and content properties as read-only evidence; and
- deterministic structural and visual ground-truth assertions.

Uploads use independent page and attachment optimistic version locks, validate storage XML and attachment references before mutation, create or version attachments before the page body, synchronize global labels and content status, and then re-fetch storage, ADF, view, metadata, media types, and attachment bytes. Page parent and space are immutable in this workflow. Completion requires both deterministic API checks and an authenticated browser comparison recorded in `verification/browser-ground-truth.json`.

For every changed storage body, the uploader acquires its atomic local operation
lock and then requires Confluence's official asynchronous content-body service
to convert the candidate from `storage` to `view` with the target page as
`contentIdContext`, before any attachment or page mutation. Poll count and wall
time are bounded, and any queue, HTTP, conversion, status, schema, or timeout
failure blocks mutation. The async identifier is transient and may encode
account identity; it is escaped only in memory and is excluded from persisted
plans, journals, reports, and error messages. The journal stores only the
rendered digest, byte count, representation, and poll count. This preflight does
not replace post-upload representation checks or authenticated browser evidence
for dynamic and installed-app behavior.

Conversion task status alone is insufficient: live testing proved that
Confluence can return `COMPLETED` and `error: null` while the view body contains
its unknown-macro placeholder image. The preflight therefore parses rendered
HTML attributes and rejects the exact `wysiwyg-unknown-macro` class token or a
canonical URL path with adjacent `placeholder/unknown-macro` segments. It
persists only sanitized signal kinds and a placeholder count. It deliberately
does not scan for a generic `error` substring because valid warning markup can
contain `aui-iconfont-error`. A non-null service error is terminal even when a
task also claims `COMPLETED` and supplies a view value. Post-upload API
verification applies the same structural detector to the page's actual
re-fetched `view`, and the completion gate re-scans its digest-bound remote-view
artifact so legacy reports cannot bypass this check.

Legacy preflight journals created before sanitized render-safety evidence may
close only through a read-only reconciliation: the current page identity,
version, title, and storage must still match the verified operation; a fresh
safe conversion must exactly match the historical rendered digest and byte
count; and a separate hash-bound reconciliation artifact records that proof.
The historical journal is never rewritten. New-contract journals require their
inline safety record and reject a legacy reconciliation artifact.

Treat storage/view round-trip fidelity and subsequent Cloud-editor re-edit fidelity as separate claims. Preserve line-through styling, `<small>`, and `<big>` when they exist in storage and verify their rendered output, but do not claim that a later editor save is lossless when regenerated ADF has omitted their dedicated semantics.

Canonical storage comparison permits only narrowly observed formatting normalization. It may discard indentation-only text and tails in structural macro containers and inside `ac:parameter` or `ac:link` only when those elements contain child XML values such as `ri:page` or `ri:url`. A scalar parameter's whitespace remains part of its value, and whitespace in mixed content remains significant. This prevents server formatting from causing a false conflict without hiding a user-visible or parameter-value change.

The manifest also pins the downloaded global-label set and page content state. Preflight compares those editable baselines with the remote page before any mutation, and the client rechecks them immediately before their writes; a mismatch stops unless a reviewed `--force` operation explicitly accepts the concurrent state. ADF evidence must be a parseable top-level document with a positive version and content array. Attachment evidence binds filename, remote ID, version, bytes, and media type, and manifest refresh re-downloads bytes so a change inside the verify-to-refresh window cannot become a trusted lock.

Unknown built-in, Forge, Connect, or Marketplace macros and extension nodes remain opaque and are preserved byte-structurally unless explicitly edited. The skill does not mutate restrictions, permitted operations, permissions, comments, watchers, likes, analytics, classifications, owners, content properties, folders, or page-tree position. It does not claim a lossless contract for live docs, blog posts, databases, whiteboards, content-tree Smart Link items, or slides; in-page Smart Links remain part of the published-page body contract.

Authoring a known built-in macro uses a current editor-created storage instance from the target tenant as the preferred template. Canonical patterns proven in live tests are documented inside the standalone skill, including the modern `tasks-report-macro` key, CQL-backed `contentbylabel`, resource-valued space/user/URL parameters, the linked page wrapper required by Excerpt Include, and the exact page-`34472058` forms for Page Tree Search, Blog Posts, Content Report Table, Include Content, User List, Decision Report, Create from Template, iFrame, and Table of Contents Zone. Those patterns remain exact-fixture and tenant-conditional and require browser-rendered output; API acceptance alone never proves macro execution.

Promote only the exact current-editor `viewpdf` and `viewxls` shapes from page `34897923` to author-and-verify. Their attachments upload before the page body and must match the reviewed filename, SHA-256 bytes, and media type. Preserve server-owned macro and attachment-version identifiers, and require authenticated-browser proof of recognizable PDF content and the intended worksheet values. This promotion covers the tested PDF and XLSX forms only; it does not generalize to other Office formats, parameters, sheets, or viewer controls.

Jira Activities, Jira Chart, Assets, and the unmatched queried integration or legacy labels remain conditional preserve-and-verify. An access gate proves no executable macro, and a missing exact match for an English label in one `es-ES` catalog search proves neither exhaustive absence nor global removal. Do not infer storage keys from UI labels; promotion requires a tenant-native instance to pass the same operation-bound storage, attachment, API, and browser gates.

Roadmap Planner is deliberately excluded from that authoring promotion. Its UI-created `roadmap` instance is preserve-and-verify only: encoded `source` and `title`, the `hash`, link maps, identifiers, and parameter payload remain opaque even though the instance survived the round trip. Cards and Carousel likewise remain conditional preserve-only surfaces: their operation-bound Premium gates prove no insertion or storage shape, and promotion still requires a permitted authoring fixture.

Synced blocks require representation-aware ground truth. Preserve the complete `bodied-sync-block` subtree, resource/local identifiers, embedded content, and marks. The current fixture proves preservation and authenticated rendering for two editor-created nodes, including one populated source body; it does not prove propagation to a paired destination or permission behavior. Bind expected source structure and text to regenerated ADF and its rendered output to the authenticated browser. Require a dedicated paired source/destination fixture before claiming synchronization or permission semantics. Do not require REST `body.view` to contain the dynamic text when it supplies only the product placeholder, and never invent or transplant a resource ID.

The Task Report fixture demonstrates this boundary concretely: the obsolete `tasks-report` key exhibits the rejected unknown-macro placeholder semantics, while the tested editor-emitted `tasks-report-macro` key renders successfully.

Multi-page operations use a content-derived dependency order and are sequential, non-atomic, and non-rollback. The batch manifest pins the inventory, tenant, space, page set, workspace paths, and dependencies. Its upload report is persisted before mutation and after every page attempt, binds the manifest hash, records partial/resume history, and references per-page results without replacing them.

The batch loader cross-checks every existing workspace page ID, tenant, and space against that manifest and rejects link-like workspace paths. Inventory requests current `subtype=page` items, validates that contract again before fetching ADF or rendered content, and requires every page-list continuation to stay on the tenant endpoint while preserving `space-id`, `status=current`, and `subtype=page`. It rejects malformed listing or pagination objects, altered or unexpected continuation filters, repeated cursors/pages, and cross-space results, and never silently drops an explicitly requested page ID. An unexpected live doc or other unsupported subtype therefore makes the inventory partial instead of entering a published-page batch. Batch report outputs are isolated from page workspaces and reserved evidence files. A batch preflight binds the manifest, dependency graph, and per-page desired-state digests; those bindings are rechecked before mutation, and a resumed verified row receives a fresh remote no-op check immediately before it can be skipped.

Inventory `visible_text` represents rendered content rather than embedded code.
The scanner suppresses style, script, template, and noscript containers. For
Confluence's escaped Excel-viewer fragment, it reparses only the exact viewer
container so workbook labels and calculated values remain searchable without
indexing Office-generated CSS. Literal markup text outside that product-owned
container remains literal content and is not interpreted as HTML.

Every verified page operation has one operation ID and desired-state digest spanning its mutation journal, API report, refreshed version lock, and immutable remote storage, ADF, view, and restriction evidence. Authenticated browser ground truth additionally binds the API report hash, remote version, tenant/page URL, required checks, and screenshot hashes. A batch completion report is only an aggregation of page completion gates whose current local state, API operation, and browser evidence all agree.

New workspaces additionally pin immutable local permitted-operation and content-property sidecars and re-fetch both as operation-bound remote verification evidence. They are inventory only, never editable inputs. Legacy workspaces that declare neither sidecar retain the prior evidence contract; declaring only one is invalid so the contract cannot be partially upgraded.

A mutation journal records each write as started before contact with Confluence. An exception after that point is unknown-partial, not proof of failure. A retry may reconcile an attachment update or page update only when the same operation and desired digest bind the exact remote identity, version, bytes, storage, and title; otherwise it stops for review. Batch resume similarly skips a verified page only when its desired digest, API operation, version, report hash, refreshed manifest locks, and a fresh no-op preflight all remain current.

An atomic workspace operation lock is acquired before prior verification evidence is invalidated or a new journal is written. It prevents concurrent local upload processes from overwriting each other's journal and evidence and is released only for a terminal journal. A lock left by a hard crash requires manual recovery only after the journal and remote state have been inspected; never overwrite or remove a live lock merely to bypass the conflict.

Upload CLI receipts are JSON-only. When stored inside a page workspace they are
confined to `verification/` and cannot replace the mutation journal, API or
browser reports, remote evidence, operation lock, reconciliation proof,
attachments, or editable/read-only page sidecars.

The skill directory contains its complete runtime, requirements, instructions, and references so it remains usable when copied outside the repository. Active PI-based forward tests use `openai-codex/gpt-5.6-luna` directly with no model fallback.

## Consequences

Positive:

- existing macros, Smart Links, images, layouts, statuses, and tenant-specific extensions survive edits that do not target them;
- attachment changes and concurrent remote edits have explicit safety checks;
- the exact current-editor PDF and Excel viewer shapes can be authored and verified without generalizing untested Office forms;
- failures can be attributed separately to local validation, REST acceptance, representation fidelity, attachment bytes, or browser rendering;
- partial multi-page mutations remain resumable and auditable without claiming atomicity or rollback;
- inventories can search rendered Excel worksheet values without CSS or JavaScript noise;
- REST-accepted but browser-broken macro configurations cannot satisfy completion;
- the read-oriented Markdown export remains unchanged and does not gain write authority.

Negative:

- storage XML is less friendly to edit than Markdown;
- Confluence may normalize storage after upload, so verification compares canonical XML and explicit invariants rather than raw bytes alone;
- REST rendered view can be intentionally incomplete for synced blocks, so ADF and authenticated-browser evidence are required for their content;
- storage and rendered-view fidelity do not imply lossless later Cloud-editor re-editing when regenerated ADF omits a legacy mark or element semantic;
- Marketplace macro execution still depends on tenant installation, licensing, permissions, and data-security policy;
- built-in integration discovery remains tenant-, plan-, rollout-, and permission-specific; a catalog result or gate dialog cannot establish a storage constructor;
- content-status synchronization can create an additional page version after the body update;
- multi-page updates can leave earlier pages committed when a later page fails;
- browser ground-truth checks remain necessary for dynamic and visual behavior.
