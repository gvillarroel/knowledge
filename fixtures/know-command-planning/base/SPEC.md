# SPEC

## Primary CLI

The CLI binary is `know`.

The following commands must work:

```bash
know --help
know add key <KEY>
know list keys
know list sources --key <KEY>
know add confluence --space <SPACE> --key <KEY>
know search confluence "text search"
know add arxiv <URL> --key <KEY>
```

Examples:

```bash
know add github-repo <REPO_URL> --key <KEY> --branch <BRANCH> --branch <BRANCH_2>
know add jira-project <PROJECT> --key <KEY>
know add video <VIDEO_URL_OR_PATH> --key <KEY>
know list sources --key <KEY>
know sync --key <KEY>
know export --key <KEY>
```

## Key Metadata

Each key must store repeatable commands for inspection, sync, and export.

## Skill

Create `skills/know/SKILL.md` with information about how to use this CLI.
