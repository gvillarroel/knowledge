# Markdown Contract

Use these rules when preparing or diagnosing md2conf input. Treat the installed CLI and the official documentation for its exact version as authoritative.

## Page identity and title

Associate an existing page explicitly with either a Markdown comment:

```markdown
<!-- confluence-page-id: 20250001023 -->
```

or frontmatter:

```yaml
---
title: Installation guide
page_id: "20250001023"
---
```

Prefer an explicit page ID for an existing page. Verify that it belongs to the intended space and root because explicit mapping bypasses ancestry checks. Reject duplicate explicit IDs across the source set. Implicit title matching is allowed only within a trusted page ancestry, but a title match is not proof that the page is Markdown-owned.

Page identity can also include an inline `confluence-space-key` comment or frontmatter `space_key` / `confluence_space_key`. This document-level value participates in routing and can override the site-level `--space` or `CONFLUENCE_SPACE_KEY` for that document. Stable 0.6.1 extracts inline page and space comments before frontmatter and coalesces them with the comment values taking precedence. Never encode the same identity twice: keep one reviewed page/space mapping and block a source-level space that differs from the approved target.

Title precedence is frontmatter `title`, then the single highest unique heading, then a generated filename-based title. Use `--skip-title-heading` only after checking whether removing the first heading harms the document structure.

## Single file versus directory

- Publish a single file only when it is standalone; relative links to other Markdown pages are not supported in single-page mode.
- Publish a directory when relative page links and a page tree must be resolved together.
- Keep every relative Markdown target inside the synchronized directory hierarchy.
- Use `index.md` or `README.md` as the directory's parent page when that hierarchy is intended. Remember that `--keep-hierarchy` may create a missing `index.md`, even during local conversion.
- Choose `--keep-hierarchy` or `--skip-hierarchy` explicitly and pin `--root-page` for a controlled subtree.
- Use same-directory `.mdignore` rules for files or directories that must not participate. Stable 0.6.1 rejects a rule containing `/` or another path separator as unsupported nested matching; place a nested file's rule in that nested directory instead. Remove or rewrite links to an excluded Markdown page because strict relative-page resolution cannot target a page omitted from the synchronized tree. Hidden directories and non-`.md` files are not scanned as pages.
- Set `synchronized: false` only for a mapped placeholder that participates in navigation or link resolution while remaining Confluence-authored.

Directory publication may create pages and synchronize child order. Review the full tree, not only changed Markdown files.

## Frontmatter and metadata

A document may declare:

```yaml
---
title: Service operations
page_id: "20250001023"
tags:
  - operations
  - runbook
properties:
  content-appearance-published: fixed-width
  content-appearance-draft: full-width
synchronized: true
---
```

Treat `tags` and `properties` as remote replacement requests, not additive hints. When `tags` is present, stable 0.6.1 compares the desired global labels with the full label set returned by Confluence and removes unmatched labels by name; do not assume non-global returned labels are outside the mutation surface. Empty values are still supplied: `tags: []` requests removal of all returned labels, and `properties: {}` removes every non-synchronization property. Omit `tags` to leave labels untouched. Omit `properties` to preserve unrelated properties; md2conf still creates or updates its own synchronization property. Frontmatter may also use an HTML-comment envelope at the beginning of the file, but keep one unambiguous metadata block.

The label difference calculation preserves the `global`, `team`, or `personal` prefix, but stable 0.6.1 sends each deletion with only the label name. When the same name exists under multiple prefixes, removal is ambiguous and can affect a label that the desired global set appears to retain. Omit `tags` when those labels must remain unmanaged.

`--global-properties FILE` supplies defaults for every synchronized document. Stable 0.6.1 recursively coalesces document properties over those defaults: a non-null document value wins, a missing or null document path inherits the global value, and nested dictionaries merge instead of replacing wholesale. Derive and review that merged object first. If either source is supplied, the merged object becomes the complete desired property set and unspecified remote properties are deleted, apart from md2conf's synchronization property. To leave remote properties unmanaged, omit both document `properties` and `--global-properties`.

Use `<!-- confluence-skip-start -->` and `<!-- confluence-skip-end -->` only for content intentionally excluded from Confluence. Verify that excluded content does not contain a required definition, target, or context.

## Links and attachments

- Resolve local image and attachment paths from the Markdown document and keep them inside the synchronization root.
- Use directory mode for links between Markdown pages.
- Keep strict URL validation enabled so broken relative targets fail instead of silently degrading.
- Inventory every `[Name](mailto:EMAIL)` link. During a live run, stable 0.6.1 queries Confluence users by name and converts an exact email match into an `ri:user` mention. Local mode cannot preview this because it performs no user lookup. Remove or rewrite the link when a mention and its possible first-mention notification are not approved.
- Expect local images and downloadable files to become page attachments.
- Prefer raster output when Confluence rendering of SVG is unreliable, but preserve the source outside the generated attachment contract.
- Remember that an existing remote attachment absent from the generated document is deleted during publication.

## Embedded HTML and storage XML

md2conf parses generated Confluence Storage Format as XML. Embedded HTML must therefore be XML-compatible even when a Markdown renderer would accept looser HTML syntax. Close every element and use self-closing void elements such as `<br />` instead of `<br>`. A malformed inline element can fail local conversion with an XML opening/ending tag mismatch before any remote call.

Keep embedded HTML small and portable. Prefer ordinary Markdown when it expresses the same result, and distinguish Markdown HTML from fenced `csf`: the former still passes through Markdown conversion, while the latter is inserted as a storage-format XML node.

## Diagrams and formulas

Choose one representation per feature:

- pre-render draw.io, Mermaid, PlantUML, or LaTeX with the required local converter; or
- use the corresponding `--no-render-*` form only when the target Marketplace app is installed, licensed, permitted, and verified.

Inspect `MERMAID_CMD`, `PLANTUML_CMD`, and related external-tool configuration without exposing sensitive paths or arguments. Verify the rendered output in Confluence; successful storage upload does not prove that a Marketplace macro executes.

## Native Confluence constructs

md2conf recognizes selected widgets such as table of contents, child listing, statuses, and dates. It also accepts a fenced `csf` block containing one Confluence Storage Format XML node.

Use raw `csf` only when ordinary Markdown cannot express the required construct. Copy a tenant-compatible shape, keep namespaces and parameters intact, review it as executable page configuration, and verify it in an authenticated browser. Do not use raw storage fragments to imitate unknown content from an existing page.

## Local conversion

Use local mode to inspect generated storage without an API call:

```bash
md2conf --local --domain example.atlassian.net --space SPACE --skip-update ./docs
```

Run it on a disposable copy because output is written beside the input. Check all generated `.csf` documents and embedded assets, including title handling, relative page URLs, attachment filenames, macro parameters, and any raw XML.

## Primary reference

- [md2conf 0.6.1 documentation](https://github.com/hunyadi/md2conf/tree/0.6.1)
