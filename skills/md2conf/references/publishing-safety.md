# Publishing Safety

Use this reference before any live md2conf command. The behavior below is verified against `markdown-to-confluence` 0.6.1; inspect `md2conf --help` and the installed version before applying it elsewhere.

## Mutation matrix

| Surface | Stable 0.6.1 behavior | Required guard |
| --- | --- | --- |
| Package identity | The active project is distributed as `markdown-to-confluence`; a different, obsolete package is named `md2conf` on PyPI. | Verify distribution, version, and modern help flags. |
| Remote preview | No documented API dry-run exists. | Use `--local` first and treat the first non-local command as a mutation. |
| Local preview | `--local` makes no API calls but writes `.csf` and generated embedded files next to the input; it still requires a domain. With `--keep-hierarchy`, it can also create missing `index.md` source files. | Convert a disposable copy and use the real non-secret domain for accurate links. |
| Page body | Publishing regenerates the complete page body from Markdown. | Use only on Markdown-owned pages; inventory any existing native content. |
| Conflict policy | `--overwrite` is the default. `--no-overwrite` skips a changed page only when a valid prior md2conf synchronization property exists and the current page version differs from its recorded version. It provides no baseline for an unmanaged page. | Pass `--no-overwrite` explicitly, but still verify page ownership, synchronization metadata, recorded/current versions, and current state. |
| Source mutation | `--keep-update` is the default and can inject page and space IDs into Markdown. | Decide between `--keep-update` and `--skip-update`; inspect the source diff. |
| Attachments | All existing page attachments not referenced by the generated document are deleted, even when the body itself is already current. | Inventory names and bytes; publish only when the source owns the complete attachment set. |
| Attachment comparison | Existing attachment equality is based on byte length rather than a content hash. | Verify bytes or a digest after publication; do not trust a same-size replacement to upload. |
| Labels | If `tags` exists, md2conf compares desired global labels with every label returned by the page-label API and removes unmatched labels by name. The set difference includes prefixes, but deletion omits the prefix, making same-name global/team/personal labels collision-prone. If `tags` is absent, it leaves labels alone. | Inventory the full returned label set; omit `tags` when any existing label must remain unmanaged or a name exists under multiple prefixes. |
| Content properties | Document properties recursively coalesce over `--global-properties`: non-null document values win and defaults fill missing or null paths. The merged object is reconciled as a complete set, removing unspecified existing properties apart from md2conf's synchronization tag. | Derive the merged object, inventory every remote property, and include the complete intended set; omit both inputs to leave properties unmanaged. |
| User mentions | A live run scans `[Name](mailto:EMAIL)` links, queries Confluence users by name, and converts exact email matches to `ri:user` mentions. Local mode has no user lookup and cannot preview the conversion. | Approve every candidate recipient or rewrite the source. Treat first-page mentions as notification-capable even with `--no-notify`. |
| Page tree | Directory mode can create pages and move or reorder children. | Pin the space/root and review the intended hierarchy and sibling order. |
| Document space routing | Inline `confluence-space-key` or frontmatter `space_key` / `confluence_space_key` can override the site-level space for a document. Inline comments take precedence over duplicate frontmatter values in stable 0.6.1. | Inventory effective page and space identity from every syntax and keep one mapping that matches the approved destination. |
| Explicit page IDs | A mapped page ID authorizes that page directly and is not constrained by the requested space or root ancestry. Duplicate explicit IDs are not rejected reliably by the release. | Check every mapping against the target and reject duplicate IDs before publishing. |
| Inline comments | Stable 0.6.1 has no comment-policy flag; regenerated storage does not preserve inline-comment markers as an editable contract. | Stop on pages with comments that must survive. Do not use development-only flags absent from help. |
| Raw CSF | A fenced `csf` block is passed as a single storage-format XML node without semantic validation. | Review XML, tenant compatibility, and browser rendering. |
| Failure | Page, attachment, label, property, hierarchy, and source writes are not one transaction. | Assume partial completion and reconcile before retrying. |

## Authentication selection

| Target | Required shape | Notes |
| --- | --- | --- |
| Confluence Cloud, standard token | `CONFLUENCE_DOMAIN`, `/wiki/` path, username, API key, space, API v2 | Username plus key selects Basic authentication. |
| Confluence Cloud, scoped token | `CONFLUENCE_API_URL`, API key, space, API v2; omit username | Omitting username selects Bearer authentication. Use the Atlassian gateway URL for the cloud ID. |
| Data Center or Server | Reviewed domain/path, credentials, space, API v1 | Treat v1 as deployment-specific and test it in the actual environment. |

Keep token values out of command arguments. md2conf does not automatically load a generic `.env` file in the stable CLI; inject variables through the selected shell, CI secret store, or container environment mechanism.

## Pre-publication evidence

Capture enough information to make the mutation reviewable:

- installed md2conf version and relevant help output;
- immutable source revision or working-tree diff;
- exact source file or directory;
- target domain, API version, space, root page, and explicit page mappings;
- existing page titles, versions, hierarchy, attachments, labels, properties, and inline comments;
- `.mdignore` rules, `[Name](mailto:EMAIL)` mention candidates, and excluded or `synchronized: false` documents;
- selected diagram renderers or confirmed Marketplace integrations;
- local `.csf` review result;
- explicit choice for overwrite, source update, and hierarchy behavior.

## Recovery

Classify failures before retrying:

- **Conversion failure:** fix Markdown, XML, link, or renderer input; no remote call should have occurred in `--local` mode.
- **Authentication or permission failure:** verify token type, auth mode, API URL/domain, space, and app permissions without creating a test page.
- **Known partial mutation:** inventory page IDs, source mappings, attachments, labels, properties, and order; resume only after matching each observed change to the reviewed plan.
- **Unknown remote outcome:** stop. Re-fetch the target and compare it with both the preflight inventory and local source before issuing another mutation.
- **Browser mismatch:** treat API acceptance as incomplete; fix the conversion or tenant-specific app/configuration and verify again.

## Primary references

- [md2conf 0.6.1 source and documentation](https://github.com/hunyadi/md2conf/tree/0.6.1)
- [markdown-to-confluence on PyPI](https://pypi.org/project/markdown-to-confluence/)
- [stable publisher mutation implementation](https://github.com/hunyadi/md2conf/blob/0.6.1/md2conf/publisher.py)
- [stable local converter implementation](https://github.com/hunyadi/md2conf/blob/0.6.1/md2conf/local.py)
- [Atlassian guidance on mention notifications](https://support.atlassian.com/confluence-cloud/docs/add-action-items-and-mentions/)
