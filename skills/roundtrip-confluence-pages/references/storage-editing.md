# Safe Confluence storage editing

## Contents

- Preservation rules
- Native editor fixture and representation limits
- Attachments and images
- Links and dynamic content
- Macros
- Mutation ownership and remote render preflight
- Draft-safe update boundary
- Ground truth

## Preservation rules

- Treat `page.storage.xml` as an XML fragment, not HTML to be reformatted.
- Preserve namespace-prefixed `ac:*` and `ri:*` elements, unknown attributes, macro IDs, local IDs, extension keys, and parameter order unless the change requires otherwise. Apply this rule to unknown Atlassian-built, Forge, Connect, and Marketplace extensions, not only Marketplace macros.
- Do not pass the fragment through a generic Markdown or HTML converter.
- Keep all filenames and Unicode text in UTF-8.
- Run `validate` after every model or manual edit.
- Treat `page.adf.json`, `page.view.html`, `page.restrictions.json`, `page.properties.json`, and `page.operations.json` as immutable evidence. Never edit permitted operations or content properties through this workflow.

The validator wraps the fragment with temporary `ac` and `ri` namespace declarations, canonicalizes it including XML comments, inventories macros and references, and rejects malformed XML before any network mutation.

Keep every attachment listed in `manifest.json` present in `attachments/`, even if the edited storage no longer references it. Attachment deletion and page moves are outside this workflow.

## Native editor fixture and representation limits

The verified native-editor fixture on page `34373703`, remote version 4, established these author-and-verify storage forms:

- paragraphs and H1 through H6;
- bold, italic, underline, inline code, superscript, subscript, foreground color, background highlight, indentation, and left/center/right alignment;
- block quote, preformatted text, a `<br />` soft line break, and a horizontal rule;
- nested ordered and unordered lists;
- one incomplete task with an `ri:user` assignee and due-date `time` element, plus one completed task;
- a wide table with `colspan` and `rowspan`, a mention, and a date;
- mention, date, emoji, and inline status; and
- `single`, `two_equal`, `two_left_sidebar`, `two_right_sidebar`, `three_equal`, `three_with_sidebars`, `four_equal`, and `five_equal` layouts.

Regenerated ADF contained 8 `layoutSection` and 22 `layoutColumn` nodes, and authenticated screenshots verified the resulting one-through-five-column geometry. Preserve the exact `ac:type` and child order; do not infer an untested layout type or manual resize value.

Representation fidelity is not the same as Cloud-editor re-edit fidelity. Remote storage and rendered view preserved line-through styling, `<small>`, and `<big>`, but regenerated ADF kept only their text and omitted dedicated strike/small/big marks. Do not promise that those legacy-looking forms will survive a later edit and save in the Confluence Cloud editor. Preserve them opaquely when that later workflow matters.

## Attachments and images

Use a full download whenever the page has remote attachments. The downloader
rejects `--skip-attachments` for such a page instead of producing a workspace
whose storage or manifest cannot be validated. Use the fleet inventory command
when only attachment names and page features are needed.

Reference an attachment by its exact local filename:

```xml
<ac:image ac:align="center" ac:alt="Architecture overview">
  <ri:attachment ri:filename="architecture.png" />
</ac:image>
```

Put `architecture.png` in `attachments/`. The uploader creates a new attachment or uploads a new version when bytes changed. It preserves or infers the MIME type and verifies both the remote bytes and media type. It never deletes remote attachments.

Page versions and attachment versions are independent optimistic locks. If an attachment is removed, replaced, versioned, or created with a colliding filename after the workspace download, the upload stops before mutation. Use `--force` only after explicitly reviewing that remote divergence.

Local attachment names must be portable on Windows: no reserved device names, invalid characters, trailing dots/spaces, overlong names, traversal, or case-insensitive collisions. The downloader fails safely when a remote title cannot be represented without loss; rename that attachment in Confluence before round-tripping it.

The dedicated live alt-text fixture proved that `ac:alt` regenerated the matching ADF media `alt` attribute and rendered HTML `<img alt>` value. Use meaningful alternative text rather than nearby visible prose as a substitute. For captions, dimensions, links, borders, or other modern media attributes, copy the pattern from a downloaded page created in the target tenant. ADF media IDs are server-owned and must not be invented.

## Links and dynamic content

Preserve normal links exactly:

```xml
<a href="https://example.com">External reference</a>
```

Internal links may use `ri:page`, anchors, content IDs, or absolute URLs. Preserve the downloaded form. Smart Link appearance can be encoded through data attributes or extension nodes that vary by editor version; copy an existing working link/card/embed from the same tenant and verify the live unfurl.

An Excerpt Include uses an `ac:link` wrapper around its page resource in the live-tested storage form:

```xml
<ac:structured-macro ac:name="excerpt-include">
  <ac:parameter ac:name="">
    <ac:link><ri:page ri:content-title="Source page" /></ac:link>
  </ac:parameter>
</ac:structured-macro>
```

Do not replace the wrapped link with a naked `ri:page`; that shape failed the tested Confluence Cloud update. Prefer `ri:content-id` when a downloaded instance supplies it, and retain any `ri:version-at-save` normalization Confluence adds.

For classic storage generated from a URL, Confluence Cloud accepts a block Smart Link in this form:

```xml
<p><a data-card-appearance="block" href="https://example.com/">Example</a></p>
```

Do not assume an `ac:link` plus `ri:url` form will hydrate as a card in every editor generation. Inspect the authenticated view after upload.

Confluence can add opaque `ac:macro-id`, default `ac:schema-version`, and `ri:version-at-save` attributes and reorder `ac:parameter` children when it saves storage. It can also remove indentation-only text and tails inside structural macro containers. In particular, formatting-only whitespace inside an `ac:parameter` or `ac:link` is equivalent only when that element contains child XML such as `ri:page` or `ri:url`. Whitespace in a scalar parameter is part of its value, and whitespace in mixed content remains significant. Verification treats only those server-owned normalizations as equivalent; comments, user-owned attributes, meaningful node order, parameter values, links, and attachment references still have to match.

## Macros

A status lozenge in storage commonly follows this structure:

```xml
<ac:structured-macro ac:name="status">
  <ac:parameter ac:name="title">READY</ac:parameter>
  <ac:parameter ac:name="colour">Green</ac:parameter>
</ac:structured-macro>
```

Macro names and parameter spellings are storage contracts, not UI labels. Prefer a downloaded working instance over a hand-authored guess. Keep rich-text or plain-text macro bodies and every parameter not targeted by the request.

Unknown Atlassian-built, Forge, Connect, and Marketplace macros or extension nodes are opaque. Never replace them with rendered HTML because doing so destroys dynamic behavior. Inventory their storage and ADF extension keys, preserve the complete subtree, and verify the installed module in the authenticated browser.

A live-tested Decision used modern ADF nodes carried inside storage rather than a named legacy macro:

```xml
<ac:adf-extension>
  <ac:adf-node type="decision-list">
    <ac:adf-attribute key="local-id">SERVER_OR_EDITOR_CREATED_LIST_ID</ac:adf-attribute>
    <ac:adf-node type="decision-item">
      <ac:adf-attribute key="local-id">SERVER_OR_EDITOR_CREATED_ITEM_ID</ac:adf-attribute>
      <ac:adf-attribute key="state">DECIDED</ac:adf-attribute>
    </ac:adf-node>
  </ac:adf-node>
</ac:adf-extension>
```

Copy a current editor-created Decision when item text, state, or identifiers must change. The single tested structural form is not a universal constructor, and local IDs must not collide.

For a current Task Report, use the internal key emitted by the editor rather than the historical UI-derived guess:

```xml
<ac:structured-macro ac:name="tasks-report-macro">
  <ac:parameter ac:name="spaces">~PERSONAL_SPACE_KEY</ac:parameter>
  <ac:parameter ac:name="pageSize">20</ac:parameter>
  <ac:parameter ac:name="status">incomplete</ac:parameter>
</ac:structured-macro>
```

Copy the exact `spaces` value from a working instance. The obsolete `tasks-report` key can pass storage/API acceptance but renders with Confluence's `wysiwyg-unknown-macro` class token and `/placeholder/unknown-macro` URL path. The tested current `tasks-report-macro` key renders successfully.

The current Confluence editor created these additional live-tested forms on page `34472058`. Treat the parameter names and nested resource shapes as exact; replace fixture values only with target-tenant values obtained through the UI or an existing downloaded instance.

| UI surface | Exact storage form and boundary |
|---|---|
| Page Tree Search | Empty `pagetreesearch` structured macro; output remains page-tree and viewer conditional |
| Blog Posts | `blog-posts` with scalar `max` |
| Content Report Table | `content-report-table` with scalar `maxResults` and `labels` |
| Include Content | `include` with an unnamed `ac:parameter` containing `ac:link` then `ri:page`; preserve `ri:version-at-save` when returned |
| User List | `userlister` with scalar `groups`; the group key is tenant-owned and an empty result is valid output |
| Decision Report | Empty `decisionreport` structured macro; rows depend on matching decisions and viewer access |
| Create from Template | Inline `create-from-template` with `blueprintModuleCompleteKey`, `contentBlueprintId`, `templateName`, `title`, and `buttonLabel`; blueprint and template IDs are server-owned |
| iFrame | `iframe` with `src` containing `ri:url`, plus scalar `width`, `title`, and `height`; browser framing policy remains conditional |
| Table of Contents Zone | `toc-zone` with an `ac:rich-text-body`; the fixture contained H2/H3 headings and generated links to both |
| Roadmap Planner | `roadmap` with `timeline`, URL-encoded `source`, `title`, `hash`, and empty `maplinks`/`pagelinks`; preserve the entire UI-created macro opaquely and do not construct, decode/re-encode, or recompute its payload/hash |

These are exact-fixture forms, not universal parameter matrices. Operation-bound editor probes found the localized `Tarjetas` and `Carrusel` options on the same tenant, but both stopped at a Premium-trial gate before insertion. Keep them conditional and preserve-only until the target plan permits a dedicated authoring fixture; the gate supplies no storage constructor.

### Office file viewers

A current-editor fixture on page `34897923` established author-and-verify support for these exact parameter shapes:

```xml
<ac:structured-macro ac:name="viewpdf">
  <ac:parameter ac:name="name">
    <ri:attachment ri:filename="report.pdf" />
  </ac:parameter>
</ac:structured-macro>

<ac:structured-macro ac:name="viewxls">
  <ac:parameter ac:name="name">
    <ri:attachment ri:filename="workbook.xlsx" />
  </ac:parameter>
  <ac:parameter ac:name="sheet">Verification</ac:parameter>
</ac:structured-macro>
```

These snippets show the tested parameter shape and intentionally omit editor-created macro attributes for readability. Do not remove `ac:macro-id`, `ac:local-id`, schema, layout, or other attributes from a downloaded instance, do not copy identifiers into a second instance where they could collide, and preserve `ri:version-at-save` when Confluence returns it.

Put the exact referenced filename in `attachments/` before upload. The fixture verified the PDF as `application/pdf` and the XLSX workbook as `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; attachment upload, SHA-256 bytes, and media type must pass before the page body changes. Only `.xlsx` and one named existing worksheet were tested for `viewxls`; do not infer `.xls`, range selection, hidden-sheet behavior, or other Office options.

REST storage and view acceptance do not prove either viewer works. In the authenticated browser, require recognizable PDF page content rather than an editor placeholder, and require the intended Excel worksheet tab plus stable cell or calculated values inside the rendered workbook. Do not claim PDF navigation, download, multi-page behavior, or other viewer controls unless the corresponding interaction was separately performed and recorded.

The same tenant exposed Jira Activities, Jira Chart, and Assets only through access or connection gates: the account had no accessible Jira sites, Jira Chart required an administrator-managed connection, and Assets content was inaccessible. In its `es-ES` editor catalog, searches returned no exact option match for the queried English labels Activity Stream, Team Calendars, Jira Timeline, Word, and PowerPoint. These dated query results are not an exhaustive localized catalog inventory and establish no storage constructor, global removal, or general availability. Preserve an existing instance opaquely, reinventory the target tenant, and require a dedicated passing fixture before promotion.

Content by Label keeps its query in CQL in the live-tested canonical form:

```xml
<ac:structured-macro ac:name="contentbylabel">
  <ac:parameter ac:name="labels">reviewed</ac:parameter>
  <ac:parameter ac:name="max">20</ac:parameter>
  <ac:parameter ac:name="cql">label = &quot;reviewed&quot;</ac:parameter>
</ac:structured-macro>
```

Live Search and Labels List use a nested resource element for the space selection:

```xml
<ac:structured-macro ac:name="livesearch">
  <ac:parameter ac:name="spaceKey"><ri:space ri:space-key="@self" /></ac:parameter>
</ac:structured-macro>
<ac:structured-macro ac:name="listlabels">
  <ac:parameter ac:name="spaceKey"><ri:space ri:space-key="@self" /></ac:parameter>
</ac:structured-macro>
```

Profile macros identify the user with a server-owned account ID. Preserve the parameter name casing emitted by the macro:

```xml
<ac:structured-macro ac:name="profile-picture">
  <ac:parameter ac:name="User"><ri:user ri:account-id="ACCOUNT_ID" /></ac:parameter>
</ac:structured-macro>
<ac:structured-macro ac:name="profile">
  <ac:parameter ac:name="user"><ri:user ri:account-id="ACCOUNT_ID" /></ac:parameter>
</ac:structured-macro>
```

A Widget Connector carries a resource element inside its URL parameter and may retain provider-specific options:

```xml
<ac:structured-macro ac:name="widget">
  <ac:parameter ac:name="overlay">youtube</ac:parameter>
  <ac:parameter ac:name="_template">PROVIDER_TEMPLATE</ac:parameter>
  <ac:parameter ac:name="width">480px</ac:parameter>
  <ac:parameter ac:name="url"><ri:url ri:value="https://example.com/provider-item" /></ac:parameter>
  <ac:parameter ac:name="height">300px</ac:parameter>
</ac:structured-macro>
```

Do not invent account IDs, personal-space keys, provider templates, or app extension identifiers. Profile visibility, widget execution, Task Report data, search results, and label reports depend on the target tenant and authenticated viewer. Verify actual browser output, not only REST acceptance or the absence of a conversion error.

Do not author a Roadmap Planner by inserting wiki markup or editing storage directly. Atlassian documents that creation path as unsupported. The live UI-created instance survived storage, ADF, view, and browser checks, but that proves preservation only: its encoded `source`, `title`, `hash`, link maps, IDs, and parameter ordering remain opaque. Preserve the complete instance and verify it in the authenticated browser.

Synced blocks have a representation-specific verification boundary. The live fixture retained two editor-created `ac:adf-extension` nodes whose `ac:adf-node` type was `bodied-sync-block`; one node contained a populated source body with headings, prose, and a table, while the other contained an empty paragraph and used a different `resource-id`. Storage and regenerated ADF retained both server-owned `resource-id` and `local-id` values, `ac:adf-content`, and breakout metadata. REST `body.view`, however, emitted only two `Sync Block` placeholder paragraphs. Do not interpret the missing view text as flattening, and do not use `body.view` or `capture-gt --visible-text` alone to prove synced content. Bind the expected source structure and text to regenerated ADF, then verify its rendered output in the authenticated browser. This fixture did not prove propagation to a paired destination or permission behavior; require a dedicated paired fixture before claiming either. Never invent or transplant a resource ID.

## Mutation ownership and remote render preflight

Only one local writer may own a workspace. Before invalidating prior evidence or writing a new mutation journal, the uploader atomically creates `verification/active-operation.lock`. A second writer must stop. A terminal journal releases the lock. If a process dies while the journal remains running, inspect the lock contents, mutation journal, and current remote state before manually removing a genuinely stale lock; never overwrite or delete it merely to bypass the conflict.

For every changed storage body, the uploader uses Confluence's official asynchronous content-body conversion to render the candidate from `storage` to `view` with the page ID as `contentIdContext` and caching disabled. It performs this bounded preflight after acquiring the operation lock and before any attachment or page mutation. HTTP, queue, conversion, schema, unknown-status, and timeout failures block the upload. Persist only the completed representation, rendered SHA-256, byte count, poll count, and sanitized render-safety diagnostics in the mutation journal. Keep the async task ID transient because it can contain account identity.

Task completion is necessary but insufficient. Live testing returned `COMPLETED` with `error: null` for an invented macro while the HTML contained an image with the exact `wysiwyg-unknown-macro` class token and a URL path with adjacent `placeholder/unknown-macro` segments. Parse rendered HTML attributes and block the upload when either structural signal is present. Do not scan for a generic `error` substring: valid warning panels can contain the legitimate `aui-iconfont-error` class.

This preflight proves that Confluence's conversion service accepted and rendered the candidate in the page context. It does not prove dynamic macros, Forge/Connect/Marketplace apps, viewer-specific output, or interactions; post-upload API verification and authenticated-browser ground truth remain mandatory.

## Draft-safe update boundary

Drafts are not part of the editable workspace contract. Confluence REST v2 can reconcile an update into a draft and may entirely override a substantially diverged draft.

Snapshot the authenticated draft observation during download/planning and recheck it before mutation. Abort any planned body/title page update when a divergent draft exists or draft state cannot be established reliably; `--force` must not bypass this guard. Attachment-, label-, and content-status-only operations may proceed under their independent locks because they do not replace draft body/title content. Never infer draft preservation from a successful page update or an unchanged published version baseline.

## Ground truth

After editing, run:

```bash
python scripts/confluence_roundtrip.py capture-gt WORKSPACE \
  --visible-text "Stable visible assertion"
```

Use stable assertions only. Do not assert timestamps, recent-update lists, issue counts, user-specific macro output, or other values expected to change. Record dynamic expectations as browser checks instead, such as “macro renders without an error and contains at least one linked row.” A check name plus `passed: true` is only a signed-off observation; retain a screenshot and sufficiently specific notes, selectors, link targets, or interaction results to show what was actually checked. For file behavior, open the control and verify the returned filename, media type, and nonzero bytes before claiming that a download works.
