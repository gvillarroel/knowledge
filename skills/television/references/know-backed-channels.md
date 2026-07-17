# Native know-backed channels

Use `know` for sources it already exposes. Do not rebuild remote clients, caches, parsing, or preview selection in a custom script when an installed `know` command can emit Television rows and previews.

## Lifecycle

1. Inspect `know add tv --help`, `know sync television --help`, and the selected source command's `--help`.
2. Register the source and preview commands with `know add tv`.
3. Materialize the source with `know sync television`.
4. Inspect the cable, `commands.json`, `README.md`, and source metadata.
5. Use the platform install command from `commands.json` and verify with `tv list-channels`.

## Output contract

- Use `--format television` for source rows.
- Use `--format television-preview --entry '{}'` for the selected-row preview.
- Preserve the same query and filters in source and preview commands.
- Pass `{}` as data to the preview command; do not evaluate the selected row as program text.
- `know sync television` writes `<CHANNEL>.toml`, `commands.json`, `README.md`,
  and `source-metadata.yaml`. It does not write `manifest.json` or `source.json`.
- `commands.json` is the manifest for this simple path. Select
  `install_macos` or `install_windows` from it instead of reconstructing a
  destination.

## arXiv

Use the `search` family exactly as shown. `know browse arxiv` is a different
local-store workflow and does not accept the query/preview contract below;
`--preview` is not the selected-row option. The search-backed channel may need
network access when it runs.

```text
know add tv arxiv-rag --key research \
  --description "Browse arXiv results for retrieval-augmented generation" \
  --source-command "know search arxiv \"retrieval-augmented generation\" --format television --max-results 20 --sort-by submittedDate" \
  --preview-command "know search arxiv \"retrieval-augmented generation\" --format television-preview --max-results 20 --sort-by submittedDate --entry '{}'"
know sync television arxiv-rag --key research
```

## Registered sources

```text
know add tv knowledge-sources --key research \
  --description "Browse registered knowledge sources" \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"
know sync television knowledge-sources --key research
```

## Jira

```text
know add tv jira-incidents --key ops \
  --description "Browse severity 1 Jira incidents" \
  --source-command "know search jira \"severity 1\" --format television" \
  --preview-command "know search jira \"severity 1\" --format television-preview --entry '{}'"
know sync television jira-incidents --key ops
```

Apply the same row/preview pair to supported `know list`, `know search`, and `know browse` families. If the installed command lacks a required format or filter, report that boundary before designing a custom adapter.
