# knowledge

`know` is a Python CLI for building a local knowledge base in `~/.knowledge`.

Each knowledge key is an independent local collection with declarative source registrations, raw synchronized content, exported Markdown, and repeatable commands stored in metadata.

## Install

```bash
uv tool install .
```

From GitHub:

```bash
uv tool install git+https://github.com/<owner>/<repo>.git
```

The installed executable is `know`.

## Quick Start

```bash
know add key research
know set credential jira_token secret-token
know add confluence --space ENG --key research
know add arxiv https://arxiv.org/abs/1706.03762 --key research
know add github-repo https://github.com/example/repo.git --key research --branch main --branch develop
know list credentials
know list sources --key research
know search confluence "incident postmortem"
know search arxiv "attention is all you need" --max-results 5 --sort-by submittedDate
know sync --key research
know export --key research
```

## Store Layout

```text
~/.knowledge/
  config.yaml
  keys.yaml
  exports/
  <key>/
    metadata.yaml
    confluence/
    arxiv/
    github/
    jira/
    aha/
    raw/
    library/
    cache/
```

## Supported Commands

```bash
know --help
know add key <KEY>
know set credential <NAME> <VALUE>
know list keys
know list credentials
know list sources --key <KEY>
know add confluence --space <SPACE> --key <KEY>
know search confluence "text search"
know search arxiv "all:transformer" --max-results 10
know add arxiv <URL> --key <KEY>
know add github-repo <REPO_URL> --key <KEY> --branch <BRANCH>
know add jira-project <PROJECT> --key <KEY>
know sync --key <KEY>
know export --key <KEY>
know import <ARCHIVE.zip>
```

## Notes

- `keys.yaml` stores named credentials that can be referenced as `$name`.
- Credential management also follows the `know <verb> <object>` pattern: `know set credential ...` and `know list credentials`.
- Exported Markdown always includes YAML frontmatter with source provenance.
- `know export` renders Markdown into each key library and also produces a zip archive for import or transfer.
- Human docs are in `docs/`.
- Coverage gate command: `python scripts/check_coverage.py --threshold 80`
