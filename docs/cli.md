# know CLI

`know` manages a local knowledge store in `~/.knowledge`.

## Core commands

```bash
know --help
know add key research
know set credential jira_token secret-token
know add confluence --space ENG --key research
know add arxiv https://arxiv.org/abs/1706.03762 --key research
know add site https://openai.com/index/harness-engineering/ --key research
know add github-repo https://github.com/example/repo.git --key research --branch main --branch develop
know list keys
know list credentials
know list sources --key research
know search confluence "incident postmortem"
know search arxiv "all:transformer" --max-results 10 --sort-by relevance
know sync --key research
know export --key research
know import ~/.knowledge/exports/knowledge-export-20260322T180000Z.zip
```

## Store shape

```text
~/.knowledge/
  config.yaml
  keys.yaml
  exports/
  <key>/
    metadata.yaml
    confluence/
    arxiv/
    site/
    github/
    jira/
    aha/
    raw/
    library/
    cache/
```
