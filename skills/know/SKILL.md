---
name: know
description: Use when needs to work with the `know` CLI in this repository to create knowledge keys, register sources, inspect configured sources, synchronize content into `~/.knowledge`, export normalized Markdown libraries, or import exported archives.
---

# Overview

Use the `know` CLI to build and maintain a local, reproducible knowledge base inside `~/.knowledge`.

## Follow the standard workflow

1. Create a key with `know add key <KEY>`.
2. Attach sources with commands such as:
   `know add confluence --space <SPACE> --key <KEY>`
   `know add arxiv <URL> --key <KEY>`
   `know add github-repo <REPO_URL> --key <KEY> --branch <BRANCH>`
   `know add jira-project <PROJECT> --key <KEY>`
   `know add video <VIDEO_URL_OR_PATH> --key <KEY>`
3. Inspect registered sources with `know list sources --key <KEY>`.


## Preserve repository expectations

- Keep documents in English.
- Prefer the command shape `know <verb> <object>` consistently and avoid noun-first top-level forms such as `know key ...`.
- Preserve raw synchronized content under `<key>/raw/`.
- Preserve exported Markdown under `<key>/library/`.
- Ensure exported Markdown includes YAML frontmatter with source provenance.
- Prefer the command shapes documented in `SPEC.md` and `docs/cli.md`.

## Use credentials and metadata consistently

- Read `~/.knowledge/keys.yaml` when integrations refer to credential aliases such as `$name`.
- Keep source registrations traceable through each key's `metadata.yaml`.
- Preserve update and delete command fields when modifying registered sources.

## Update sources
Synchronize content with `know sync --key <KEY>`.
## Export data
Export normalized Markdown and a zip archive with `know export --key <KEY>`.
## Import Data
Import an archive with `know import <ARCHIVE.zip>`.
