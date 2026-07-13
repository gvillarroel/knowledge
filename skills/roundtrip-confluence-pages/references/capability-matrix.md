# Confluence Cloud page capability matrix

## Contents

- Scope and evidence boundary
- Representation contract
- Native body capabilities
- Links, Smart Links, and media
- Current built-in macros and dynamic elements
- Official legacy macro catalog
- Page-level and collaboration surfaces
- Marketplace and tenant-installed apps
- Verification requirements
- Official sources

## Scope and evidence boundary

This skill targets published Confluence Cloud pages returned by REST API v2. It does not treat live docs, blog posts, whiteboards, databases, content-tree Smart Link items, or slides as interchangeable with pages. Content-tree Smart Link items are a separate content type from the in-page Smart Link appearances covered below.

Use these support states when planning edits:

- **Author and verify**: use only the exact tenant-native shape that has passed storage validation, API verification, and authenticated-browser verification. Do not generalize a tested shape to untested options.
- **Preserve and verify**: keep an existing node opaquely and verify it after upload; do not invent a new instance.
- **Conditional**: require the relevant plan, rollout, installed app, license, external authentication, tenant policy, permissions, or server-owned identifier before authoring or executing the feature.
- **Out of contract**: do not mutate the surface through this skill. “Untouched” does not mean “verified preserved.”

The July 12–13, 2026 live campaign and its subsequent dedicated image-alt-text and native-editor workspaces passed their configured storage, API, regenerated ADF/view, and authenticated-browser checks. The evaluator inventory is still evolving, so this standalone reference deliberately does not publish an aggregate group or workspace count. When a count is required, derive it from the specific evaluation evidence bundle supplied for that run. These results prove only their configured fixtures and assertions. They are not exhaustive coverage of every Confluence editor option, parameter combination, plan-dependent feature, integration, viewer permission, or installed app. Browser records bind named checks and screenshots; they do not by themselves prove an unasserted interaction.

## Representation contract

Use three representations together:

| Representation | Role | Mutation rule |
|---|---|---|
| `storage` | Canonical editable body; retains `ac:*`, `ri:*`, macro parameters, link attributes, and attachment references | Edit and upload |
| `atlas_doc_format` (ADF) | Structured observation of modern editor nodes, marks, extensions, cards, and media IDs | Preserve as evidence; Confluence regenerates it after storage upload |
| `view` | Server-rendered HTML used for text assertions and browser ground truth | Preserve as evidence; never upload it |

Confluence accepts `storage` for page creation and update. Its content-body conversion API supports conversions among storage, ADF, editor, and rendered formats, but conversion is not the editable contract because it can normalize or omit product-specific details.

Live tenant testing on July 13, 2026 also proved the official asynchronous
`storage`-to-`view` conversion when `contentIdContext` identifies the target
page. Every actual body-changing upload therefore queues that conversion only
after acquiring the local operation lock and before any attachment or page
mutation. It polls for at most 30 seconds and 40 results, and treats failure,
timeout, malformed output, or an unknown status as blocking. Async IDs are
transient and may include account identity, so they are never persisted or
included in errors; the journal binds only a rendered hash, size,
representation, and poll count. A successful conversion is a server-render
preflight, not proof that installed-app, viewer-specific, or interactive output
works, so it never replaces post-upload API and authenticated-browser evidence.
The service can report `COMPLETED` while rendering an unknown-macro image, so
the preflight structurally parses HTML attributes and blocks either the exact
`wysiwyg-unknown-macro` class token or a URL whose path contains adjacent
`placeholder/unknown-macro` segments. The journal records only the count and
signal kinds, never the macro name or async identifier. Generic error-like CSS
names are not rejected because valid warning panels can use
`aui-iconfont-error`.

ADF documents nodes and marks that can appear across Atlassian products. Schema membership does not prove that a node is authorable in Confluence, enabled in a tenant, or functional for a viewer. Require a tenant-created fixture and live verification before promoting an untested surface from preserve-and-verify to author-and-verify.

## Native body capabilities

### Live author-and-verify forms

| Surface | Exact tested scope | Important limit |
|---|---|---|
| Paragraphs and headings | Paragraphs plus H1 through H6 | All six heading levels regenerated in ADF and were verified by authenticated heading-role queries |
| Current text marks and alignment | Bold, italic, underline, inline code, subscript, superscript, text color, background highlight, indentation, and left/center/right alignment | Nondefault alignment regenerated as ADF marks; the full color palette and every indentation level were not tested |
| Legacy-looking inline forms | Storage and rendered view preserved line-through styling plus `<small>` and `<big>` | Regenerated ADF retained their text but emitted no dedicated strike/small/big marks. Do not claim lossless re-editing in the Confluence Cloud editor; preserve these forms opaquely when that workflow matters |
| Lists | Nested ordered and unordered lists | List start values and every nesting/indent interaction were not tested |
| Action items | One incomplete task with a server-owned assignee and due date, plus one completed task | Preserve account IDs, task IDs, due dates, and state; viewer-specific task/report behavior remains conditional |
| Decision | A live storage/ADF decision-list and decision-item round-trip | Copy a current editor-created instance for item text, state, and local IDs; do not invent a universal constructor from the single fixture |
| Quote, preformatted text, soft line break, and divider | One block quote, `<pre>` block, `<br />` soft line break, and horizontal rule | ADF normalized the `<pre>` text to a code-marked paragraph and the line break to `hardBreak`; storage/view and browser output were also checked |
| Date, emoji, mention, and inline status | One instance of each; mention used a server-owned account ID | Account visibility and status color/title combinations remain tenant- or viewer-dependent |
| Panels | Existing `info`, `note`, `warning`, and `tip` storage forms regenerated as panel nodes | This does not prove every current panel preset, custom color, icon, or no-icon form |
| Expand | Expand plus one nested expand | Deeper nesting and mixed extension children were not tested |
| Code block | Python and JavaScript storage forms with a title or language parameter | Auto-detection, formatting, line numbers, wrapping, and other languages were not tested |
| Table | A wide three-column table with a three-column spanning header and a two-row spanning body cell | Header-column option, numbered column, colors, resizing, distribution, and other merge/split cases were not tested |
| Layout | `single`, `two_equal`, left/right two-column sidebars, `three_equal`, `three_with_sidebars`, `four_equal`, and `five_equal` | Regenerated ADF contained 8 `layoutSection` and 22 `layoutColumn` nodes; authenticated screenshots verified geometry. Manual resizing and other width modes were not tested |

### Preserve-and-verify until a dedicated fixture passes

| Surface | Current treatment |
|---|---|
| Full color palette, full indentation/list option matrix, and list start values | Preserve existing markup; do not claim new authoring support |
| Strike, `<small>`, and `<big>` through a later Cloud-editor re-edit | Preserve storage opaquely; regenerated ADF omitted dedicated marks, so this workflow is not proven lossless |
| Untested task interactions and viewer-specific task reports | Preserve IDs, account IDs, dates, and state; do not invent server-owned values |
| Current error/success panels, custom panel colors, custom/no emoji | Preserve the downloaded form and validate the regenerated ADF panel type |
| Code language auto-detection, formatting, line numbers, wrapping, and untested languages | Preserve the downloaded parameters |
| Untested table controls, manual layout resizing, and unobserved width modes | Preserve exact nodes and attributes |
| Synced blocks | Preserve every `bodied-sync-block` identifier and body; treat permissions-dependent behavior as conditional. A live fixture retained two editor-created nodes, including one populated source body, in storage and ADF, while REST `body.view` emitted only `Sync Block` placeholders. It did not prove cross-instance propagation or permission behavior; those require a paired source/destination fixture. Verify preserved structure in ADF and rendered source content in the authenticated browser |
| Multi-bodied extensions and unknown ADF extension frames | Preserve the complete subtree and identifiers |
| Native table-linked bar, line, and pie charts | Preserve existing chart nodes and data linkage; do not confuse these current charts with the removed legacy Chart macro |

## Links, Smart Links, and media

### Links and Smart Links

| Surface | Support state | Evidence boundary |
|---|---|---|
| External HTTPS and `mailto:` links | Author and verify | Tested with visible link text |
| Internal page link | Author and verify | Tested with `ri:page`; preserve content IDs and `ri:version-at-save` when Confluence supplies them |
| Same-page anchor and Anchor macro | Author and verify | Tested for one anchor shape |
| Undefined-page link | Author and verify | Tested as a stored link; page-creation behavior is not part of the contract |
| Attachment link/reference | Author and verify | API verifies the referenced attachment identity and bytes; browser download behavior requires a separate interaction check |
| URL, inline, and block-card Smart Link appearances | Author and verify | Tested only for the captured URL forms and authenticated viewer |
| Embed Smart Link | Preserve and verify | Not author-tested; copy a current tenant-created embed and verify live rendering |
| Heading/section, comment, cross-page anchor, and other untested internal targets | Preserve and verify | Keep the downloaded target, content ID, anchor, and display text |
| Third-party Smart Link unfurl | Conditional | Depends on provider access, app/auth state, tenant policy, and viewer permissions |

### Images, video, and files

| Surface | Support state | Evidence boundary |
|---|---|---|
| Attachment create/update | Author and verify | Verify filename, remote ID, version, SHA-256 bytes, and media type; deletion is unsupported |
| PNG, JPEG, and animated GIF attachment images | Author and verify | Tested with width/alignment, one border, and one caption |
| PDF, MP4, MP3, CSV, and text attachment references | Author and verify for storage/API identity | A plain PDF attachment reference is not the tested `viewpdf` macro below; do not claim preview, playback, or download success until the browser interaction and returned bytes are checked |
| Image alternative text | Author and verify for the dedicated fixture | A later fixture proved one `ac:alt` value survived in regenerated ADF and rendered `<img alt>` output; the original broad image group did not prove alt text, and visible nearby prose is not an alternative text value |
| Image height, inline/text-flow modes, image links, and untested border/alignment controls | Preserve and verify | Copy a current editor-created instance |
| Playable video, file preview, and explicit download controls | Preserve and verify | The exact fixture opened PDF, CSV, and text previews, played MP4, exposed an MP3 playback timeline, and showed Download controls. It did not fetch and verify returned download bytes, so explicit download success remains unproven |
| Media comments | Out of contract | Server-owned collaboration state; leave untouched and do not claim verification |
| Gallery macro | Preserve and verify | Legacy existing-only macro; manual image arrangement with tables/layouts is a separate body capability |

## Current built-in macros and dynamic elements

Preserve exact `ac:name`, parameters, macro IDs, bodies, resource elements, and extension data. Correlate storage with ADF before classifying an instance: modern panels, code blocks, statuses, tasks, decisions, and cards can retain old-looking storage keys while ADF identifies a current editor node.

Macro configuration, not its current query result, is normally serialized into the workspace; the authenticated live result must be verified after upload. Synced blocks are a representation exception: storage and ADF can retain their embedded content and resource IDs even when REST `body.view` exposes only a `Sync Block` placeholder. For that case, use ADF as structural/text evidence and the authenticated browser as dynamic rendering evidence.

### Live-tested forms

| Surface | Support state | Tested storage key or node |
|---|---|---|
| Anchor | Author and verify | `anchor` |
| Attachments | Author and verify | `attachments` |
| PDF macro | Author and verify for exact fixture | `viewpdf`; resource-valued `name` contains `ri:attachment` for a `.pdf` verified as `application/pdf` |
| Office Excel | Author and verify for exact fixture | `viewxls`; resource-valued `name` contains `ri:attachment` for a tested `.xlsx`, and scalar `sheet` names an existing worksheet; verified as `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| Change History | Author and verify | `change-history` |
| Children/Child Items | Author and verify | `children` |
| Content by Label/Filter by Label | Author and verify, conditional output | `contentbylabel`; tested CQL and label parameters |
| Contributors | Author and verify, conditional output | `contributors` |
| Content Properties | Author and verify | `details` |
| Content Properties Report | Author and verify, conditional output | `detailssummary` |
| Excerpt | Author and verify | `excerpt` |
| Excerpt Include | Author and verify, conditional reference | `excerpt-include`; unnamed parameter contains an `ac:link`-wrapped `ri:page` |
| Include Content | Author and verify for exact fixture, conditional reference | `include`; unnamed parameter contains `ac:link` then `ri:page`, with server-added `ri:version-at-save` preserved |
| Labels List | Author and verify, conditional output | `listlabels`; `spaceKey` contains an `ri:space` resource |
| Live Search | Author and verify, conditional output | `livesearch`; `spaceKey` contains an `ri:space` resource |
| Page Tree | Author and verify, conditional output | `pagetree` |
| Page Tree Search | Author and verify for exact fixture, conditional output | `pagetreesearch`; the editor-created fixture had no parameters |
| Blog Posts | Author and verify for exact fixture, conditional output | `blog-posts`; scalar `max` |
| Content Report Table | Author and verify for exact fixture, conditional output | `content-report-table`; scalar `maxResults` and `labels` |
| Popular Labels | Author and verify, conditional output | `popular-labels` |
| Profile and Profile Picture | Author and verify, conditional output | `profile`, `profile-picture`; user parameter contains a server-owned `ri:user` account ID |
| Recently Updated | Author and verify, conditional output | `recently-updated` |
| Task Report | Author and verify, conditional output | Tested `tasks-report-macro` renders successfully; obsolete `tasks-report` can pass storage/API acceptance but produces the exact `wysiwyg-unknown-macro` and `/placeholder/unknown-macro` render markers |
| Table of Contents | Author and verify | `toc` |
| Table of Contents Zone | Author and verify for exact fixture | `toc-zone`; `ac:rich-text-body` generated entries for the tested H2/H3 headings |
| User List | Author and verify for exact fixture, conditional output | `userlister`; scalar tenant-owned `groups` key |
| Decision Report | Author and verify for exact fixture, conditional output | `decisionreport`; the editor-created fixture had no parameters |
| Create from Template | Author and verify for exact fixture, conditional action | Inline `create-from-template`; exact parameters were `blueprintModuleCompleteKey`, `contentBlueprintId`, `templateName`, `title`, and `buttonLabel`, with server-owned blueprint/template IDs |
| iFrame | Author and verify for exact fixture, conditional execution | `iframe`; `src` contains `ri:url`, with scalar `width`, `title`, and `height` |
| Roadmap Planner | Preserve and verify only for a UI-created fixture | `roadmap`; preserve the complete encoded `source`, `title`, `hash`, empty link maps, IDs, and parameters opaquely. The successful round-trip is not evidence for storage authoring |
| Widget Connector | Author and verify, conditional execution | `widget`; URL parameter contains an `ri:url` resource |
| Body elements represented by storage macros | Author and verify for exact fixtures | `code`, `expand`, `info`, `note`, `status`, `tip`, `warning` |
| Decision | Author and verify for exact fixture | Modern `decision-list`/`decision-item` ADF nodes carried in storage, not a legacy named macro |

### Current but not author-tested by this skill

| Surface | Support state | Reason or prerequisite |
|---|---|---|
| Native connected charts | Preserve and verify | Current chart feature is separate from the removed legacy Chart macro; no dedicated fixture passed |
| Cards and Carousel | Conditional; preserve and verify | Operation-bound editor probes found the localized `Tarjetas` and `Carrusel` options, but both stopped at a Premium-trial gate before insertion. This proves plan gating, not storage authoring; rollout and data visibility still apply |
| Activity Stream and Team Calendars | Conditional; preserve and verify | The tested `es-ES` editor catalog returned no exact option match for those queried English labels; this is not an exhaustive localized catalog inventory. Application links, plan, permissions, rollout, and product availability still apply |
| Jira work items/issues | Conditional; preserve and verify | Requires connected Jira, permissions, compatible project data, and its own passing fixture |
| Jira Activities | Conditional; preserve and verify | The editor exposed the option, but the tested account had no accessible Jira sites; no executable storage instance was created |
| Jira Chart | Conditional; preserve and verify | The editor exposed the option, but required an administrator-managed Confluence-to-Jira connection; no executable storage instance was created |
| Jira Timeline | Conditional; preserve and verify | The tested `es-ES` editor catalog returned no exact option match for the queried English label; this is not an exhaustive localized catalog inventory. Connected Jira, permissions, and compatible roadmap data still apply |
| Assets data | Conditional; preserve and verify | The editor exposed the option, but the tested account lacked access to its content; plan, Jira/Assets access, schema permissions, and license still apply |

The tested `es-ES` editor catalog also returned no exact option match for the queried English labels Word and PowerPoint. They remain existing-only legacy macros under the catalog below; this query result is not an exhaustive localized inventory or a universal product-availability claim.

## Official legacy macro catalog

Use Atlassian's current removal catalog as the authority. The lists below are exhaustive for that catalog as reviewed July 13, 2026. Preserve an existing legacy subtree opaquely; never treat successful preservation as proof that a new instance can be authored.

### Preservation-only legacy macros with an alternative or current editor replacement

| Display name | Legacy storage key(s) |
|---|---|
| Align | `align` |
| Background color | `bgcolor` |
| Center | `center` |
| Cheese | `cheese` |
| Code Block | `codeBlock` |
| Content by user | `content-by-user` |
| Copyright | `copyright` |
| Create space button | `create-space-button` |
| Fancy bullets | `fancy-bullets` |
| Global reports | `global-reports` |
| Highlight | `highlight` |
| Loremipsum | `loremipsum` |
| Multimedia | `multimedia` |
| Navigation map | `navmap` |
| Noformat | `noformat` |
| Legacy Panel family | `info`, `tip`, `note`, `warning`, `panel` |
| Privacy mark | `privacy-mark` |
| Privacy policy | `privacy-policy` |
| Recently used labels | `recently-used-labels` |
| Registered Trademark | `reg-tm` |
| Search results | `search` |
| Service Mark | `sm` |
| Space attachments | `space-attachments` |
| Space details | `space-details` |
| Strikethrough | `strike` |
| Trademark | `tm` |

The same storage key can represent different editor generations. For example, a current panel can regenerate from an old-looking `info` or `warning` key. Use ADF and the authenticated editor/view to distinguish a current element from a legacy macro instance.

### Preservation-only legacy macros without an alternative

| Display name | Legacy storage key |
|---|---|
| Div | `div` |
| Favorite Pages | `favpages` |
| HTML comment | `htmlcomment` |
| Style | `style` |

### Existing-only macros that remain visible but cannot be newly inserted or edited

| Display name | Legacy storage key |
|---|---|
| Chart | `chart` |
| Contributors Summary | `contributors-summary` |
| Gallery | `gallery` |
| Page Index | `index` |
| PowerPoint | `viewppt` |
| Recently Updated Dashboard | `recently-updated-dashboard` |
| Related Labels | `related-labels` |
| Spaces List | `spaces` |
| Word | `viewdoc` |

Treat Network and any PDF macro instance that cannot be matched to the exact current-editor `viewpdf` shape above as preserve-and-verify after the April 1, 2026 full legacy-editor deprecation. Atlassian began the phased retirement in January 2026; those dates are not interchangeable. A generic PDF attachment or Smart Link is not evidence for the PDF macro, and the storage key alone does not establish editor generation.

### Removed features: out of contract for authoring or execution

| Display name | Former key or migration behavior |
|---|---|
| Confluence News gadget | Removed gadget |
| Legacy Google Drive macros | `google-drive-docs`, `google-drive-sheets`, `google-drive-slides`; placeholders can convert to Smart Links |
| IM Presence | `im` |
| JUnit Report | `junitreport` |
| Legacy Microsoft OneDrive macro | Placeholder can convert to a Smart Link |
| Rollover | `rolloverwithoudbody` |
| Span | `span` |

Preserve an unknown inert subtree if it appears in downloaded storage, but do not claim the removed feature executes.

## Page-level and collaboration surfaces

| Surface | Support state | Skill behavior |
|---|---|---|
| Title | Author and verify | Editable in `page.meta.json`; verify after upload |
| Parent, page-tree position, folders, and space | Out of contract for mutation | Capture available identity/location evidence; moves or folder reorganization require a separate reviewed workflow and fresh download |
| Published version | Author and verify safety lock | Use optimistic locking and the current version plus one |
| Page content status | Conditional author and verify | A space admin can disable statuses or restrict custom statuses; verify availability before setting or clearing, which can publish another version |
| Inline status lozenge | Author and verify for tested form | Body content independent of page content status |
| Global labels | Author and verify | Edit global labels; preserve non-global prefixes |
| Attachments | Author and verify | Create/version and verify bytes/media type; deletion is unsupported |
| Restrictions and permissions | Out of contract | Download restrictions as read-only evidence; never mutate them |
| Drafts | Out of contract; detect and abort body/title updates | REST v2 can reconcile an update body into a draft and may entirely override a substantially diverged draft. Snapshot draft divergence at download/plan time and recheck it before mutation. Abort any planned body/title page update when a divergent draft exists or draft state cannot be established reliably; `--force` must not bypass this guard. Attachment-, label-, and content-status-only operations may proceed under their independent locks because they do not replace draft body/title content. Never claim draft preservation. |
| Owner, last owner, collaborators, page position, title emoji, and header image | Out of contract for mutation | Do not claim preservation unless each surface is separately captured and verified |
| Approvals and classifications | Conditional and out of contract for mutation | Plan, organization policy, admin configuration, and permissions apply |
| Space templates and block-template libraries | Out of contract for library mutation | Content inserted from a template can be treated as ordinary page body only after download; do not manage the template library through this page workflow |
| Other content types | Out of contract | Live docs, blog posts, whiteboards, databases, content-tree Smart Link items, and slides have distinct data models or publication lifecycles. Use a dedicated workflow; in-page Smart Links remain covered by the page-body contract above. |
| Comments, likes, watchers, analytics, app content properties, automation, reactions, and notification state | Out of contract | Leave untouched; current workspaces do not prove these states were preserved |
| Permitted operations and content properties | Read-only inventory evidence; out of contract for mutation | New downloads persist immutable `page.operations.json` and `page.properties.json` sidecars and API verification re-fetches them as operation-bound remote evidence. Legacy workspaces without both sidecars retain their older contract. Never edit or mutate either surface through this skill. |

## Marketplace and tenant-installed apps

An exhaustive static list of Marketplace, Forge, or Connect macros is impossible. Installed modules vary by tenant, app version, license, permissions, data-security policy, and dynamically registered app modules.

Use this dynamic inventory contract for every target tenant and page:

1. Inventory every `ac:structured-macro`, `ac:adf-extension`, `ac:adf-node`, extension key/type, macro ID, local ID, parameter, namespaced child, and corresponding ADF extension record.
2. Classify only a known, tenant-tested constructor as author-and-verify. Treat every unknown core, Forge, Connect, and Marketplace extension as preserve-and-verify.
3. Preserve the complete unknown subtree, attributes, parameter order, and server-owned identifiers. Never replace it with rendered HTML or infer an app payload from its visible output.
4. After upload, confirm the app is installed and licensed for the viewer, then verify that each preserved extension renders and behaves without an error or placeholder.
5. If installation, license, permission, or execution cannot be proved, report the surface as conditional or unverified. Do not claim that all Marketplace macros are executable.

## Verification requirements

Every completed round-trip requires all of the following:

1. A body-changing upload acquires the atomic workspace operation lock and completes Confluence's official asynchronous `storage`-to-`view` conversion in the target page context before any mutation. The journal binds the completed representation, rendered digest/size, and poll count without persisting the potentially identifying async task ID.
2. Storage XML returned by Confluence is equivalent to the local editable storage after allowing only documented server-owned save normalization.
3. Title, labels, and any enabled page-level content status match their editable sidecars.
4. Every local attachment exists remotely with the same SHA-256 bytes and media type.
5. Confluence returns regenerated ADF and view representations without an API error.
6. Every claimed surface has a narrow structural/API assertion; a broad group pass must not be reused as proof of an unasserted option.
7. Authenticated-browser ground truth records the observed result for each claimed layout, macro output, link target, image control, interactive container, file download/playback, and app-backed element.
8. Dynamic checks assert stable behavior, such as a macro rendering without an error and exposing an expected link, rather than unstable counts or timestamps.
9. Any untested option remains preserve-and-verify, conditional, or out of contract in the completion report.

## Official sources

Reviewed July 13, 2026:

- [Confluence REST API v2: Page](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/)
- [Confluence REST API v2: Attachment](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-attachment/)
- [Confluence REST API v2: Operation](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-operation/)
- [Confluence REST API v1: Content body conversion](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content-body/)
- [Confluence REST API v1: Content states](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content-states/)
- [Confluence REST API v1: Content restrictions](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content-restrictions/)
- [Atlassian Document Format structure](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [Add elements to a page or live doc](https://support.atlassian.com/confluence-cloud/docs/insert-elements-into-a-page/)
- [Create and edit content](https://support.atlassian.com/confluence-cloud/docs/create-and-edit-content/)
- [Format text](https://support.atlassian.com/confluence-cloud/docs/format-text/)
- [Simplify data with tables](https://support.atlassian.com/confluence-cloud/docs/simplify-data-with-tables/)
- [Create and manage layouts](https://support.atlassian.com/confluence-cloud/docs/create-and-manage-layouts/)
- [Charts and connected data](https://support.atlassian.com/confluence-cloud/docs/charts-and-connected-data/)
- [Create and use synced blocks](https://support.atlassian.com/confluence-cloud/docs/create-and-use-synced-blocks/)
- [Use macros to show Confluence content](https://support.atlassian.com/confluence-cloud/docs/use-macros-to-show-confluence-content-on-pages/)
- [What are macros?](https://support.atlassian.com/confluence-cloud/docs/what-are-macros/)
- [Learn which macros are being removed](https://support.atlassian.com/confluence-cloud/docs/learn-which-macros-are-being-removed/)
- [FAQ: Understanding legacy editor deprecation](https://support.atlassian.com/confluence-cloud/docs/faq-understanding-legacy-editor-deprecation/)
- [Insert the Network macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-network-macro/)
- [Insert the PDF macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-pdf-macro/)
- [Insert the Roadmap Planner macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-roadmap-planner-macro/)
- [Insert the iFrame macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-iframe-macro/)
- [Insert the User List macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-user-list-macro/)
- [Insert the Decision Report macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-decision-report-macro/)
- [Insert the Create from Template macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-create-from-template-macro/)
- [Insert Microsoft Office macros](https://support.atlassian.com/confluence-cloud/docs/insert-microsoft-office-macros/)
- [Insert the Jira issues macro](https://support.atlassian.com/confluence-cloud/docs/insert-the-jira-issues-macro/)
- [Add a Jira timeline to Confluence](https://support.atlassian.com/jira-software-cloud/docs/add-your-roadmap-to-a-confluence-cloud-page/)
- [Display Assets data](https://support.atlassian.com/confluence-cloud/docs/display-your-assets-data-on-a-confluence-page/)
- [Display dynamic content with Cards](https://support.atlassian.com/confluence-cloud/docs/display-beautiful-dynamic-content-on-your-page-with-cards/)
- [Add dynamic frames with Carousel](https://support.atlassian.com/confluence-cloud/docs/add-a-trio-of-dynamic-frames-to-your-page-with-carousel/)
- [Embed calendars](https://support.atlassian.com/confluence-cloud/docs/embed-calendars-on-confluence-pages/)
- [Add the Activity Stream gadget](https://support.atlassian.com/confluence-cloud/docs/add-the-activity-stream-gadget/)
- [Insert links and anchors](https://support.atlassian.com/confluence-cloud/docs/insert-links-and-anchors/)
- [Display files and images](https://support.atlassian.com/confluence-cloud/docs/display-files-and-images/)
- [Work with images, videos, and files](https://support.atlassian.com/confluence-cloud/docs/work-with-images-videos-and-files/)
- [Add a status to a page or blog](https://support.atlassian.com/confluence-cloud/docs/add-a-status-to-your-page-or-blog/)
- [Request and manage approvals](https://support.atlassian.com/confluence-cloud/docs/request-and-manage-approvals-in-confluence/)
- [Classify a page or blog post](https://support.atlassian.com/confluence-cloud/docs/classify-a-page-or-blogpost/)
- [Add an emoji and header image](https://support.atlassian.com/confluence-cloud/docs/make-your-page-and-its-title-more-memorable/)
- [Edit a template](https://support.atlassian.com/confluence-cloud/docs/edit-a-template/)
- [Create and manage block templates](https://support.atlassian.com/confluence-cloud/docs/create-and-manage-block-templates/)
- [Confluence Cloud permissions and restrictions](https://support.atlassian.com/confluence-cloud/docs/what-are-confluence-cloud-permissions-and-restrictions/)
- [Manage page-level permissions](https://support.atlassian.com/confluence-cloud/docs/manage-permissions-on-the-page-level/)
- [Forge macro module reference](https://developer.atlassian.com/platform/forge/manifest-reference/modules/macro/)
