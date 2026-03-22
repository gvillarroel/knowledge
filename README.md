# knowledge

A Python CLI that manages a local knowledge base stored in `~/.knowledge`.

It fetches content from multiple source types, converts it to Markdown with
YAML frontmatter, and organises it in a hierarchical folder structure ready
for use with static-site generators, note-taking tools, or AI pipelines.

---

## Installation

```bash
pip install -e .
```

> **Optional heavy dependencies** – `crawl4ai` for the `web` source type and
> `atlassian-python-api` for Confluence / Jira sources are declared as normal
> dependencies.  If you only need a subset of source types you can install just
> the packages you need.

---

## Quick start

```bash
# Add a website (crawled with crawl4ai)
knowledge add mysite https://docs.example.com --type web --max-pages 100

# Add a GitHub repo (two branches at once)
knowledge add myrepo https://github.com/org/repo --type github --branches main,dev

# Add a Confluence space
knowledge add cf-docs https://myco.atlassian.net/wiki \
  --type confluence --space DOCS \
  --username me@myco.com --token $CONFLUENCE_TOKEN

# Add a Jira project
knowledge add jira-proj https://myco.atlassian.net \
  --type jira --project PROJ \
  --username me@myco.com --token $JIRA_TOKEN

# Add an Aha! product
knowledge add aha-prod https://myco.aha.io \
  --type aha --subdomain myco --product-id PROD --token $AHA_TOKEN

# Fetch / refresh content
knowledge update             # all sources
knowledge update mysite      # single source

# List registered sources
knowledge list
knowledge list --json

# Show details of one source
knowledge show mysite

# Export Markdown to a directory
knowledge export --output ./docs
knowledge export mysite --output ./docs

# Remove a source
knowledge remove mysite
```

---

## Knowledge base layout

```
~/.knowledge/
├── sources.yaml          # registry of all sources
└── data/
    ├── mysite/           # one directory per key
    │   └── docs-example-com--getting-started.md
    ├── myrepo/
    │   ├── main/         # one sub-directory per branch
    │   │   └── README.md
    │   └── dev/
    │       └── README.md
    └── cf-docs/
        └── getting-started/
            └── installation.md
```

Each Markdown file has a YAML frontmatter block:

```markdown
---
fetched_at: '2024-06-01T12:00:00+00:00'
key: mysite
source: https://docs.example.com/getting-started
title: Getting Started
type: web
---

# Getting Started
…
```

---

## Source types

| Type | Description | Required options |
|------|-------------|-----------------|
| `web` | Crawls a website with [crawl4ai](https://github.com/unclecode/crawl4ai) | `url` |
| `github` | Clones a Git repo (one or more branches) | `url`, optionally `--branches`, `--token` |
| `confluence` | Fetches pages from a Confluence space | `url`, `--space`, `--username`, `--token` |
| `jira` | Fetches issues from a Jira project | `url`, `--project`, `--username`, `--token` |
| `aha` | Fetches features/ideas from an Aha! product | `--subdomain`, `--product-id`, `--token` |

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `KNOWLEDGE_HOME` | Override the knowledge base directory (default: `~/.knowledge`) |
| `KNOWLEDGE_USERNAME` | Default username for Confluence / Jira `add` commands |
| `KNOWLEDGE_TOKEN` | Default API token for `add` commands |

---

## Development

```bash
pip install -e ".[dev]"
pytest
```
