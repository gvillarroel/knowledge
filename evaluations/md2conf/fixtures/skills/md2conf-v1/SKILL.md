---
name: md2conf
description: Convert, preview, publish, and troubleshoot Markdown files or directory trees with the active hunyadi/md2conf Confluence CLI distributed as `markdown-to-confluence`. Use when Codex needs to install or verify the correct md2conf tool, generate local Confluence Storage Format, synchronize Markdown-owned pages, map page IDs and hierarchies, upload images or diagrams, manage labels or content properties, configure Cloud or Data Center authentication, diagnose conversion failures, or verify a publication. Do not use this workflow to claim lossless preservation of manually authored or macro-rich native Confluence pages.
---

# Publish Markdown with md2conf

Treat Markdown as the authoritative source, stage the conversion locally, and make every remote mutation explicit before publishing.

## Standalone boundary

- Use only this `SKILL.md` and its package-local `references/` files.
- Treat the `md2conf` executable, Confluence service, credentials, optional diagram renderers, Marketplace apps, and user-supplied Markdown as explicit external inputs.
- Diagnose missing prerequisites directly; do not require another skill, checkout, helper script, or hidden configuration.
- Keep conversion and planning offline unless the user explicitly authorizes a Confluence publication or another remote mutation.

## Complete every response

Do not let an unavailable executable, read-only sandbox, or offline constraint reduce the answer to "could not run." Distinguish observed evidence from proposed work, then give the complete safe next-step plan.

- For any local preview, name the maintained `markdown-to-confluence` distribution, require version/help/distribution preflight in an isolated environment, stage a disposable copy, and provide a `--local` command with the intended domain, space, and `--skip-update`. State that local mode makes no Confluence request but writes `.csf` and generated assets. Review titles, links, attachments, XML, and rendered assets.
- For a directory plan, apply the source inventory to the actual files: selected directory mode, root and space, `index.md` or `README.md`, `.mdignore`, relative links, attachments, labels, properties, source-ID policy, page creation or reordering, and conflicts. Include later authenticated-browser verification even when publication is not yet authorized.
- For raw `csf` or diagrams, require one well-formed, tenant-compatible storage XML node, disposable local validation of the revised source, and authenticated-browser rendering verification after any later publication. An accepted API write is not rendering evidence.
- For every `[Name](mailto:EMAIL)` candidate, state the full live-only chain: user lookup by name, exact-email match, conversion to `ri:user`, and possible first-mention notification. State that local mode cannot preview the lookup, stable 0.6.1 has no disabling user-mention flag, and `--no-notify` is insufficient; remove or rewrite the link when mentions are forbidden.
- For metadata preservation, distinguish absent, empty, and populated `tags` and `properties`. Supplied `tags` make stable 0.6.1 compare desired global tags with the full label API result and remove every unmatched label by name, including returned team or personal labels; `tags: []` therefore requests removal of all returned labels. Supplied properties remove unspecified properties, so `properties: {}` removes every non-synchronization property. For a preservation decision, explain both the version-scoped reconciliation rule and the case-specific impact. Omit `tags` to leave labels untouched; omit `properties` to preserve unrelated properties while md2conf still manages its own synchronization property.
- For every explicit page mapping, compare the mapped page with the requested space and root. State that the page ID bypasses those ancestry constraints, block any mismatch, and do not treat command flags, guessed replacement IDs, or creating a duplicate as an automatic repair. Require an explicit ownership and retargeting decision plus a verified destination before changing the mapping.
- For an authority conflict, explicitly say that md2conf regenerates the complete body and cannot preserve unmodeled native features losslessly. Recommend keeping the existing page Confluence-authored or publishing to a separate, explicitly Markdown-owned page.
- For any proposed live publication, close with browser checks for body rendering, hierarchy, links, attachments and bytes, labels, properties, diagrams, and intended mentions. Never imply that a zero exit code completes verification.

## Establish the authority model

Use md2conf only when the selected Markdown file or tree is intended to own the complete generated page body and its referenced attachments.

Stop before publication when any of these is true:

- the existing page contains manual content, open inline comments, unknown macros, Smart Links, extensions, or attachments that must survive but are absent from Markdown;
- page ownership or the target page ID, space, or root page is uncertain;
- the user expects a reversible, transactional, or lossless round trip;
- the target is a live doc, blog post, database, whiteboard, or other unsupported content type.

Return a source-of-truth diagnostic in those cases. Explain that md2conf regenerates the complete page body, and recommend either keeping the existing page Confluence-authored or using a separate Markdown-owned page. Do not flatten native Confluence content into Markdown or imply that md2conf preserves data it does not model.

## Verify the active tool

Run these checks before relying on any option:

```bash
md2conf --version
md2conf --help
python -m pip show markdown-to-confluence
```

Install the active project from the `markdown-to-confluence` distribution in an isolated Python 3.10+ environment. For a reproducible run against the version reviewed by this skill:

```bash
python -m pip install "markdown-to-confluence==0.6.1"
```

Never install the obsolete PyPI distribution named `md2conf`. Confirm that help includes `--local`, `--api-version`, `--root-page`, `--skip-update`, and `--no-overwrite`. Treat the installed help as authoritative; do not use flags copied from the upstream development branch when they are absent locally. In particular, stable 0.6.1 does not expose the development-only `--comments` or `--user-mentions` policy flags, so it cannot disable implicit user-mention conversion through a CLI option.

## Inspect the source and target

1. Decide whether to publish one standalone Markdown file or an entire directory tree.
2. Identify every explicit `page_id` or `confluence-page-id` mapping, reject duplicate page IDs or titles, and confirm that each mapped page actually belongs to the intended space and root subtree.
3. Inventory relative links, `[Name](mailto:EMAIL)` links, images, downloadable files, diagram sources, `.mdignore` rules, `tags`, `properties`, embedded HTML, raw `csf` blocks, and `synchronized: false` documents. Require embedded HTML to be well-formed XML; for example, write `<br />`, not `<br>`.
4. Inspect the target page or subtree for manual content, attachments, labels, content properties, inline comments, approved mention recipients, and sibling order before any live run.
5. Record whether md2conf may edit the Markdown source to inject page and space identifiers.

Read [markdown-contract.md](references/markdown-contract.md) for page mapping, hierarchy, links, metadata, attachments, and extension syntax. Read [publishing-safety.md](references/publishing-safety.md) before designing or executing any live publication.

## Convert locally first

Run `--local` on a disposable copy because it writes `.csf` files and generated embedded assets beside the input. It does not call Confluence, but stable 0.6.1 still requires a domain; use the real non-secret domain and space for accurate generated links:

```bash
md2conf --local --domain example.atlassian.net --space SPACE --skip-update ./docs
```

Use `offline.invalid` and a placeholder space only for a syntax-focused conversion. Inspect every `.csf` result for missing sections, invalid or local-only links, unexpected raw storage XML, diagram placeholders, and page-title duplication. If conversion reports an XML tag mismatch, inspect inline HTML for non-self-closing void elements such as `<br>` before debugging Confluence. Local mode performs no Confluence user lookup, so it cannot preview which `mailto:` links a live run will convert into user mentions. Keep strict URL validation enabled. If execution is unavailable, still provide the exact proposed local command and this inspection checklist; do not substitute the sandbox limitation for a plan.

Choose diagram behavior deliberately. The render modes require their external converters. Use a `--no-render-*` mode only after confirming that the matching Marketplace app is installed and permitted in the target tenant.

## Configure credentials safely

Pass secrets through the process environment or an approved secret manager, never through `-a`, `--api-key`, command history, logs, chat, screenshots, or a committed file.

For a standard Cloud token with Basic authentication, set:

```text
CONFLUENCE_DOMAIN
CONFLUENCE_PATH
CONFLUENCE_USER_NAME
CONFLUENCE_API_KEY
CONFLUENCE_SPACE_KEY
CONFLUENCE_API_VERSION=v2
```

For a scoped Cloud token, set `CONFLUENCE_API_URL` to the Atlassian gateway URL, set `CONFLUENCE_API_KEY`, and omit `CONFLUENCE_USER_NAME` so md2conf uses Bearer authentication. Use API v1 only for a reviewed Data Center or Server target. Do not claim that an environment is publish-ready merely because variables exist; verify account, space, page, and app permissions without printing values.

## Review the mutation plan

md2conf has no documented remote dry-run. Before a live command, state and review all applicable effects:

- create or replace complete page bodies and titles;
- upload referenced assets and delete every existing page attachment that is not referenced by the generated document;
- compare desired global `tags` with the full label set returned by Confluence and remove unmatched labels by name; do not assume only global labels are affected;
- remove unspecified existing content properties when frontmatter or global properties are supplied;
- query Confluence users referenced as `[Name](mailto:EMAIL)` and convert exact matches to `ri:user` mentions; a first mention on a page can notify the person even when page-update notifications are disabled;
- inject page and space identifiers into Markdown under the default `--keep-update` behavior;
- miss an updated attachment when the replacement has the same byte length as the remote file, because stable 0.6.1 does not compare attachment hashes;
- create pages and move or reorder children during directory publication;
- leave a partial remote and local state if a later step fails.

Use `--no-overwrite` as a conflict guard for manual edits made after a prior md2conf synchronization, but do not treat it as universal protection for a newly associated or previously unmanaged page. Inventory the target and require explicit publication authority regardless.

Treat `--no-notify` only as a request to make page updates as minor edits without ordinary change notifications. It is not a guarantee that mention recipients will remain unnotified. Remove or rewrite `[Name](mailto:EMAIL)` links before publication when user mentions are not explicitly approved.

## Publish with explicit choices

For an already mapped page whose source must remain byte-stable, use a reviewed command shaped like:

```bash
md2conf --api-version v2 --domain example.atlassian.net --space SPACE \
  --no-overwrite --no-notify --skip-update ./guide.md
```

For a Markdown-owned tree that may persist newly created page mappings, choose the hierarchy and root explicitly:

```bash
md2conf --api-version v2 --domain example.atlassian.net --space SPACE \
  --root-page 123456 --keep-hierarchy --no-overwrite --no-notify \
  --keep-update ./docs
```

Use `--overwrite` only after reviewing the current remote page and explicitly accepting Markdown replacement of changes made since the last md2conf synchronization. After a `--keep-update` run, inspect and retain the intended Git diff containing generated page mappings.

## Verify and recover

Treat a zero exit code as necessary but insufficient. After publication:

1. Inspect the Markdown diff for identifier injection or other unexpected local changes.
2. Open representative created and updated pages in an authenticated browser.
3. Verify titles, parent-child placement, sibling order, relative and anchor links, intended mail links or user mentions, images, downloads, labels, properties, diagrams, status widgets, and generated-by notice.
4. Confirm that only the reviewed attachments remain and verify the intended attachment bytes or digest, especially for same-size replacements; also confirm that no manual content or comment was expected to survive.
5. Record the command shape without secrets, installed version, source revision, target space/root, observed page IDs, and verification result.

On failure, assume partial completion. Inspect both the source tree and Confluence before retrying; reconcile injected IDs, created pages, uploaded or deleted attachments, labels, properties, and page order. Never claim rollback or automatically repeat a mutation whose remote outcome is unknown.

## Safety boundaries

- Never publish merely to test credentials; use the least mutating authenticated check available outside md2conf or stop with a diagnostic.
- Never expose, persist, or echo API tokens.
- Never publish an ambiguous title match or unreviewed page ID.
- Never publish an unreviewed `[Name](mailto:EMAIL)` mention candidate; `--no-notify` does not neutralize mention notifications.
- Never use raw `csf` blocks or custom extensions without reviewing the emitted storage XML and verifying the rendered result.
- Never describe md2conf publication as a lossless Confluence round trip.
