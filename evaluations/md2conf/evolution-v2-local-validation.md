# md2conf v2 Local Validation

## Scope

This validation checks version-sensitive behavior used by the second skill-evolution pass. It uses only disposable copies and local Python calls. It does not authenticate to or contact Confluence.

Validation environment:

- date: 2026-07-13, America/New_York;
- isolated temporary virtual environment;
- distribution: `markdown-to-confluence`;
- executable version: `0.6.1`;
- package home page: `https://github.com/hunyadi/md2conf`;
- credentials: none.

## Results

| Case | Method | Result |
| --- | --- | --- |
| Hierarchy-preserving local conversion | Copied `missing-index/site/` to a fresh temporary directory and ran `md2conf --local --domain docs.corp.example --space OPS --skip-update --keep-hierarchy COPY`. | Exit `0`. The disposable copy gained root and nested `index.md` files plus four `.csf` files. SHA-256 comparison confirmed that the repository fixture remained unchanged. |
| Nested `.mdignore` rule | Copied `ignore-rules/` to a fresh temporary directory and ran local conversion against its root rule `drafts/*.md`. | Exit `1` with `ValueError: nested matching not supported: drafts/*.md`. This confirms that nested exclusions must be expressed in the nested directory's own `.mdignore`. |
| Comment/frontmatter mapping precedence | Parsed `mapping-precedence/conflicted.md` with the installed `md2conf.scanner.Scanner`. | Effective page ID was `111` and effective space was `HR`, while the frontmatter values were `222` and `ENG`. The title still parsed as `Deployment Runbook`. |
| Recursive global-property merge | Parsed document properties from `property-merge/page.md`, loaded `global-properties.yaml`, and called installed `md2conf.coalesce.coalesce_json`. | The result retained document `width: narrow` and `theme: document`, inherited nested `density: compact`, retained owner team `docs`, and added retention years `7`. |

The generated hierarchy-copy files were:

```text
index.csf
index.md
overview.csf
overview.md
teams/index.csf
teams/index.md
teams/oncall.csf
teams/oncall.md
```

## Installed-source corroboration

Read-only inspection of the installed stable source confirmed the remaining version-scoped rules:

- attachment inventory, upload/reconciliation, and deletion of unreferenced attachments happen before the conditional page-body update, so cleanup still runs when body content is current;
- label set comparison includes name and prefix, but removal calls the API with only the label name;
- `--no-overwrite` returns early only when a valid synchronization property exists and the current page version differs from its recorded version;
- `synchronized: false` documents remain indexed for metadata, hierarchy, and link resolution while body synchronization is skipped.

## Limits

This evidence validates local conversion, parsing, merge behavior, and inspected stable-source control flow. It does not exercise a mock or live Confluence API, tenant permissions, Marketplace apps, remote attachment endpoints, label deletion behavior in a specific tenant, or browser rendering.
