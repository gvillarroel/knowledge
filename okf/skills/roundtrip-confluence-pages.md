---
type: Agent Skill
title: Confluence Page Round-Trip
description: Download, edit, upload, and verify Confluence Cloud pages without flattening
  macros, Smart Links, statuses, images, attachments, labels, or unknown extension
  content. Use when Codex needs a loss-aware page round-trip, must add or replace
  page images/files, preserve dynamic Confluence elements, apply complex local edits
  with PI, detect concurrent page changes, or prove through API and visual checks
  that an uploaded page still works.
tags:
- codex
- skill
skill_name: roundtrip-confluence-pages
source_path: skills/roundtrip-confluence-pages/SKILL.md
---

# Confluence Page Round-Trip

Preserve Confluence storage XML as the editable source, capture ADF and rendered HTML as evidence, and refuse uploads that cannot be verified.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared Python requirements.
- Do not import scripts, instructions, validators, or conventions from sibling skills, evaluation fixtures, or repository files.
- Keep the page workspace as the only page-specific input and run every deterministic gate through `scripts/confluence_roundtrip.py`.
- Copying this skill directory outside the repository must preserve download, validation, upload, API verification, and final browser-ground-truth verification behavior.

## Prepare the environment

1. Work from this skill directory or use absolute paths to its scripts.
2. Use Python 3.11 or newer. Install `scripts/requirements.txt` in an isolated environment before running the skill.
3. Read `references/capability-matrix.md` before designing a page that uses dynamic elements or Marketplace macros.
4. Read `references/storage-editing.md` before changing storage XML or adding attachments.
5. Read `references/batch-workflows.md` before scanning a space or changing more than one page.
6. Resolve credentials from `CONFLUENCE_BASE_URL`, `CONFLUENCE_USERNAME`, and `CONFLUENCE_TOKEN`. The base URL must be the site root, without `/wiki`.
7. Never print, serialize, or pass an API token on the command line. Prefer `.env` or the process environment.

`CONFLUENCE_USERNAME` is the email address of the Atlassian account that created
the token; it is not an Atlassian display name. Create a standard API token at
<https://id.atlassian.com/manage-profile/security/api-tokens>, give it a
purpose-specific name and expiration, copy it once, and save it in a password
manager. This client currently calls the tenant URL directly and therefore does
not support scoped-token gateway URLs of the form
`https://api.atlassian.com/ex/confluence/{cloudId}`. Select **Create API token**,
not **Create API token with scopes**, until gateway URL support is implemented.
The token can do only what its Atlassian account is permitted to do in the target
Confluence site.

For a repository-local setup, create an ignored `.env` file in the directory
from which the command will run. Use the exact variable names below; the similar
names `CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN` are not accepted:

```dotenv
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=you@example.com
CONFLUENCE_TOKEN=paste-the-standard-api-token-here
```

This repository ignores `.env`, but verify that any other destination does too
before creating the file. Restrict the file to the current user where the host
supports file ACLs. Do not commit, paste into chat, place in a page workspace,
include in screenshots, or persist the token in shell history. Do not use a
Confluence password.

Alternatively, set the three values only for the current PowerShell process:

```powershell
$env:CONFLUENCE_BASE_URL = "https://your-domain.atlassian.net"
$env:CONFLUENCE_USERNAME = "you@example.com"
$env:CONFLUENCE_TOKEN = "paste-the-standard-api-token-here"
```

The aliases `ATLASSIAN_BASE_URL`, `ATLASSIAN_USERNAME`, and
`ATLASSIAN_API_TOKEN` are accepted for compatibility, but the `CONFLUENCE_*`
names take precedence. Command options can set only `--base-url` and
`--username`; there is deliberately no token option.

An implicit `./.env` fills missing process variables without replacing them.
Use `--env-file /absolute/path/to/.env` to select a different credential file
and explicitly override stale process values. The client refuses to combine a
site URL found only in an implicit `.env` with a token already present in the
process. Put a global option before the subcommand:

```bash
python scripts/confluence_roundtrip.py --env-file /absolute/path/to/.env doctor
```

Run the read-only preflight:

```bash
python scripts/confluence_roundtrip.py doctor
```

`doctor` performs an authenticated, read-only request and reports the account
and site without printing the token. A missing value is reported by name. For
HTTP 401, confirm the account email, token value, expiration, and token type;
for HTTP 403, confirm the account's Confluence product and space permissions;
for a wrong site, correct the root URL and do not use `/wiki`. Revoke a token
immediately in Atlassian account security if it is exposed, then replace the
stored value and rerun `doctor`.

For a plan-only request, keep the response compact: use 6–10 ordered decisions, group immutable evidence once, name each applicable verification gate once, and list no more than five stop conditions. Prefer executable bundled command forms such as `upload --dry-run` and `completion-gate` over paraphrased command names. Include only boundaries triggered by the request and omit unrelated workflows.

For an attachment replacement plan, explicitly name the intended Confluence filename, state that attachments upload before storage XML, verify the uploaded attachment's SHA-256 digest and media type, and preserve old remote attachments unless deletion is separately authorized.

If no token exists, create one through the Atlassian account security UI only when the user authorized that account change. Store it in a protected secret store or `.env`, then rerun `doctor`. Do not create a replacement token merely because a site is temporarily unavailable.

## Download and establish ground truth

Download a published page by numeric ID:

```bash
python scripts/confluence_roundtrip.py download PAGE_ID ./page-workspace
```

Page IDs must be positive ASCII integers. The client retries only read-only GET
requests for bounded 429/502/503/504 responses; it never automatically retries a
mutation. A download target, workspace file, or attachment entry may not be a
symbolic link. `download --skip-attachments` is accepted only when the page has
no remote attachments; use `scan-space` for lightweight inventory or perform a
full download when attachments exist.

The workspace contains:

- `page.storage.xml`: the only body representation intended for editing.
- `page.meta.json`: editable title plus immutable page identity and location evidence.
- `page.labels.json`: editable global labels.
- `page.content-state.json`: page-level content status, editable only when the space enables the requested status behavior.
- `attachments/`: downloaded files; add or replace files here by filename.
- `page.adf.json`, `page.view.html`, `page.restrictions.json`, `page.properties.json`, and `page.operations.json`: read-only evidence. New downloads pin all five files in the manifest; older workspaces that predate the properties/operations sidecars remain supported without silently upgrading their evidence contract.
- `manifest.json`: read-only page/attachment version locks, hashes, page identity, and downloaded label/content-state baselines; never edit it by hand.
- `ground-truth.json`: structural and visual assertions.

Before editing, open the live page in the authenticated browser and record:

- one full-page screenshot or a set of scoped screenshots for dynamic regions;
- the visible title, content status, macro output, links, images, and attachment behavior;
- stable text or UI states that must remain visible after upload.

Store screenshot paths and notes in `ground-truth.json.visual_baseline`. Do not treat HTML source alone as visual ground truth.

## Edit without flattening

Edit `page.storage.xml` directly. Preserve every unknown `ac:*`, `ri:*`, `data-*`, macro parameter, extension key, local identifier, and link appearance attribute unless the requested change explicitly targets it.

For images or files:

1. Put the file in `attachments/` using its intended Confluence filename.
2. Reference that exact filename from storage XML.
3. Do not embed local absolute paths or base64 data in the page body.

Keep ADF and rendered HTML unchanged; Confluence regenerates them after storage upload. Use existing downloaded markup as the template for Smart Link cards, synced blocks, modern extensions, and Marketplace macros because installed apps can use tenant-specific keys. For synced blocks, preserve the complete storage subtree and resource IDs: a live fixture retained two editor-created nodes, including one populated source body, in storage and regenerated ADF, while REST `body.view` emitted only `Sync Block` placeholders. Prove preserved source text with ADF plus authenticated-browser evidence, not a rendered-view text assertion alone. Treat cross-instance synchronization and permission behavior as unverified until a paired source/destination fixture exercises both.

Use the native body forms and limits in `references/capability-matrix.md` and `references/storage-editing.md`. A live fixture verified H1–H6, current formatting, assigned/due and completed tasks, merged tables, and one-through-five-column layouts. It also showed that storage/view can preserve line-through styling, `<small>`, and `<big>` while regenerated ADF omits dedicated marks, so never claim lossless later re-editing of those legacy-looking forms in the Cloud editor.

Before authoring a built-in macro, consult the live-tested canonical forms in `references/storage-editing.md`. Treat a successful REST update as acceptance of storage, not proof that the macro works: the authenticated browser must render the configured result without an error. Do not substitute historical internal keys for current editor forms. The obsolete `tasks-report` key is a verified example that produces Confluence's unknown-macro placeholder markers, while the tested current `tasks-report-macro` key renders successfully.

A tenant-native fixture also established the exact current keys and parameter forms for Page Tree Search, Blog Posts, Content Report Table, Include Content, User List, Decision Report, Create from Template, iFrame, and Table of Contents Zone. Copy only the tested forms documented in `references/storage-editing.md`, retain server-owned IDs, and reverify conditional output. Keep the UI-created `roadmap` instance preserve-only: its encoded `source` and `hash` payloads are opaque. Operation-bound editor probes found the localized `Tarjetas` and `Carrusel` options, but each stopped at a Premium-trial gate before insertion. This proves plan gating, not a storage constructor or authoring support.

A current-editor Office fixture established author-and-verify support only for these exact forms: `viewpdf` with a resource-valued `name` parameter pointing to a PDF attachment, and `viewxls` with a resource-valued `name` plus a scalar `sheet` parameter. Put the exact referenced file in `attachments/`, upload and byte/MIME-verify it before the page body, preserve editor- and server-owned identifiers plus `ri:version-at-save`, and then prove the rendered PDF page and intended worksheet values in the authenticated browser. Treat every untested Office option as preserve-and-verify.

In the tested tenant, Jira Activities, Jira Chart, and Assets stopped at access or connection gates. In its `es-ES` editor catalog, searches returned no exact option match for the queried English labels Activity Stream, Team Calendars, Jira Timeline, Word, and PowerPoint. Treat these as dated query results, not exhaustive catalog or universal availability claims, and never synthesize storage from a UI label.

For a complex model-assisted edit, work on a copy and use the Luna route:

```bash
pi --model openai-codex/gpt-5.6-luna --skill /absolute/path/to/roundtrip-confluence-pages \
  --tools "read,edit,write,grep,find,ls" --no-session --approve -p \
  "Modify this Confluence page workspace as requested. Preserve unknown storage nodes and update ground truth."
```

Do not add a model fallback. If the installed PI/provider combination does not expose
filesystem tools, attach only `page.storage.xml` and `page.meta.json`, disable tools,
and require a strict JSON object containing replacement `title` and `storage` values.
Apply that response as a reviewable patch; never attach credentials, the manifest, or
read-only evidence. If the request names another PI skill, resolve and pass its real
path with a second `--skill`; do not invent or silently substitute a missing skill.
Validate every resulting workspace deterministically.

Quote the comma-separated `--tools` value, especially in PowerShell; an
unquoted comma list can be split before PI receives it. If `--skill` itself
suppresses tools in a provider/runtime combination, have PI read this `SKILL.md`
with its `read` tool first, then edit only the allowed workspace files. Record
the provider/model route in evidence because tool behavior can differ by route.

```bash
pi --model openai-codex/gpt-5.6-luna --skill /absolute/path/to/roundtrip-confluence-pages \
  --no-tools --no-session --approve -p \
  @/absolute/path/to/page-workspace/page.storage.xml \
  @/absolute/path/to/page-workspace/page.meta.json \
  "Return only JSON with title and storage. Preserve unknown storage nodes."
```

## Validate and review the mutation plan

Capture assertions after the local edit. Repeat `--visible-text` for stable strings that must appear in Confluence view mode:

```bash
python scripts/confluence_roundtrip.py capture-gt ./page-workspace \
  --visible-text "Architecture approved" \
  --visible-text "Release status"
python scripts/confluence_roundtrip.py validate ./page-workspace
python scripts/confluence_roundtrip.py upload ./page-workspace --dry-run \
  --output ./page-workspace/verification/noop-dry-run.json
```

Review the planned page update and every attachment create/update. If the remote version changed after download, stop and download again. Use `--force` only after reviewing a same-page version divergence. Do not use this skill to move a page between parents or spaces.

For a changed storage body, the dry-run plan marks
`remote_render_preflight_required: true` but does not queue a server task. The
actual upload acquires the atomic workspace operation lock and then asks
Confluence to convert the candidate from `storage` to `view` with the page ID as
`contentIdContext`, before any attachment or page mutation. Polling is bounded;
an HTTP error, conversion failure, unknown status, malformed result, or timeout
blocks the upload. The async task ID can contain account identity, so it is
URL-escaped in memory and never written to plans, journals, reports, or error
messages. Only the rendered digest, byte count, representation, and poll count
are journaled, together with sanitized render-safety diagnostics. A
`COMPLETED` conversion is still rejected when parsed HTML attributes contain
Confluence's `wysiwyg-unknown-macro` class token or the canonical
`/placeholder/unknown-macro` URL path. Do not use a generic `error` substring:
valid Confluence output can contain names such as `aui-iconfont-error`.

Before a planned body/title page update, inspect the captured authenticated draft observation and recheck it before mutation. Drafts are outside the workspace contract, and REST v2 can reconcile the update into a draft or entirely override a substantially diverged draft. Abort the body/title update when a divergent draft exists or draft state cannot be established reliably; `--force` must not bypass this guard. Attachment-, label-, and content-status-only operations may proceed under their independent locks because they do not replace draft body/title content. Never claim that this skill preserved a draft.

The preflight also compares remote global labels and page content state with the
downloaded editable baselines, then rechecks immediately before either write.
A concurrent label/state change is a conflict unless the reviewed operation
explicitly uses `--force`. Valid ADF evidence must remain a parseable top-level
`doc` object with a positive version and content array; malformed conversion
output cannot satisfy download or verification.

Treat page content status as conditional. A space administrator can disable
statuses or restrict custom statuses; do not plan a status mutation until the
target space accepts the requested state.

## Upload and verify

Upload attachments first, then storage XML, labels, and content status:

```bash
python scripts/confluence_roundtrip.py upload ./page-workspace \
  --message "Explain the reviewed change"
```

The command performs post-upload API verification and writes `verification/report.json`, plus the remote storage, ADF, and rendered view representations. Treat any failed check as an incomplete upload.

The async storage-to-view preflight proves that Confluence's conversion service
accepted and rendered the candidate in the page context. It does not prove that
Forge, Connect, Marketplace, viewer-specific, or interactive content works;
post-upload API evidence and authenticated-browser ground truth remain required.

For new workspaces, API verification also writes immutable
`verification/remote.properties.json` and
`verification/remote.operations.json` evidence and binds their hashes into the
completion gate. These inventories are never editable inputs and the skill does
not mutate content properties or permission-derived operations.

Attachment verification binds filename, remote ID, version, SHA-256 bytes, and
MIME type. Manifest refresh downloads and hashes the attachment again; any
change between verification and refresh is rejected instead of becoming a new
trusted lock.

Every mutating step is journaled before it starts. If an attachment update or
page PUT committed but a later step failed, rerun the same reviewed workspace:
the uploader reconciles only an exact journaled remote ID, version, desired
digest, storage/title, and attachment-byte match, then skips the duplicate
write. A step that was merely `started` is reported as unknown-partial and
retains its resume lineage; inspect that journal instead of assuming no write
occurred or reaching for `--force`.

Only one local mutation operation may own a workspace. The uploader acquires
`verification/active-operation.lock` atomically before invalidating prior
evidence or writing a new journal and releases it only when the journal becomes
terminal. After a hard process crash, inspect the lock and mutation journal plus
the current remote page before manually removing a genuinely stale lock; never
delete an active lock merely to bypass the conflict.

Avoid `--no-verify` in normal use. When explicitly selected, the command returns `status: unverified` with a non-zero process exit code, does not advance the manifest version lock, and cannot support a success claim.

Then revisit the live page in the authenticated browser and compare it with the baseline:

1. Confirm the title and page-level content status.
2. Check every changed section at normal desktop width.
3. Open dynamic macros or expansions and follow internal, external, anchor, attachment, and Smart Links.
4. Confirm images load, captions/links are correct, and replaced attachment bytes are current.
5. Confirm dynamic macros render current data rather than an error or placeholder.
6. Capture post-upload screenshots and add their paths to the verification record.

After those authenticated observations, bind the check IDs and screenshots to
the current API operation. Paths are resolved from the workspace and must stay
inside `verification/`:

```bash
python scripts/confluence_roundtrip.py record-browser-gt ./page-workspace \
  "https://example.atlassian.net/wiki/spaces/SPACE/pages/PAGE_ID/Title" \
  --check rendered-page \
  --check changed-dynamic-macro \
  --baseline verification/browser-baseline.png \
  --final-screenshot verification/browser-final.png
```

The command writes and validates `verification/browser-ground-truth.json`. It
binds the exact API operation, report hash, desired-state digest, remote
version, tenant/page URL, required check IDs, and decodable screenshot hashes.
It rejects screenshots outside `verification/` and baseline/final byte reuse.

Run the local combined gate from the copied skill directory:

```bash
python scripts/confluence_roundtrip.py completion-gate ./page-workspace
```

This command reads only the workspace and local screenshot files. It rejects stale API evidence, mismatched page or tenant identity, failed browser checks, missing screenshots, and incorrect screenshot hashes. A successful round trip requires its output to contain `status: verified`.

Do not report success until the API report passes and the browser rendering matches the ground truth.

## Process multiple pages

Use the standalone batch companion for inventory, local exploration, and
prevalidated multi-page operations:

```bash
python scripts/confluence_batch.py scan-space SPACE_ID ./space-inventory.json
python scripts/confluence_batch.py explore ./space-inventory.json --macro status --label reviewed \
  --output ./space-selection.json
python scripts/confluence_batch.py batch-download ./space-inventory.json ./page-batch --label reviewed
python scripts/confluence_batch.py batch-validate ./page-batch/batch-manifest.json
python scripts/confluence_batch.py batch-plan ./page-batch/batch-manifest.json
python scripts/confluence_batch.py batch-upload ./page-batch/batch-manifest.json --message "Reviewed batch"
python scripts/confluence_batch.py batch-verify ./page-batch/batch-manifest.json
python scripts/confluence_batch.py batch-completion-gate ./page-batch/batch-manifest.json
```

Read `references/batch-workflows.md` for deterministic edit commands, local
filter semantics, partial and HTTP 429 handling, and resume rules. Batch upload
is sequential, never forceful or atomic, and never claims rollback. Keep custom
batch report outputs outside `workspaces/`; the batch companion rejects output
paths that would overwrite page sidecars or API/browser evidence.

Space inventories index rendered text, not embedded CSS or JavaScript. The
scanner also extracts the visible worksheet labels and values from Confluence's
escaped Excel-viewer fragment, so `explore --text` can find workbook content
without polluting results with Office-generated style declarations.

## Safety boundaries

- Never delete remote attachments automatically; unreferenced files remain available.
- Treat upload-time `--skip-attachments`, `--skip-labels`, and `--skip-content-state` as explicit partial-operation controls. Dry-run reports suppressed changes; verified upload rejects a skip that would omit desired state. Download-time `--skip-attachments` is a separate lightweight guard and refuses pages that actually have attachments.
- Never alter restrictions, permissions, comments, watchers, likes, analytics, owners, classifications, or content properties through this skill. Leave other collaboration state untouched, but do not claim it was preserved unless it was separately captured and verified.
- Never edit `page.properties.json` or `page.operations.json`. New manifests pin both as immutable inventory evidence and verification re-fetches both; legacy workspaces may omit both, but declaring only one is invalid.
- Never mutate or claim preservation of drafts. Detect a divergent draft and abort any planned body/title update even with `--force`; an indeterminate draft state is the same stop condition. Attachment-, label-, and content-status-only operations remain eligible under their independent locks.
- Never upload to a different site than `manifest.json.base_url` without a separately reviewed migration workflow.
- Never change `space_id` or `parent_id`; use a separately reviewed page-move workflow, then download a fresh workspace.
- Never claim that all Marketplace macros are executable: preserve their storage nodes losslessly, then verify the installed app, license, and tenant policy in the live page.
- Treat live docs, blog posts, databases, whiteboards, content-tree Smart Link items, and slides as different content types until a dedicated round-trip contract is implemented and tested. This does not change the tested support for Smart Links embedded inside a published page.
