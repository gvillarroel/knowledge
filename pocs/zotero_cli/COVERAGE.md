# Zotero CLI replacement coverage

Verified on Windows with Zotero 9.0.6, local API v3, schema 42, and
`zotero-mcp-server` 0.6.1.

## What is covered

| Capability | Result | Evidence |
|---|---|---|
| Bibliographic metadata | Covered | `search` and `get metadata` return title, authors, DOI, URL, abstract, tags, and item key. |
| BibTeX | Covered | `get bibtex` emits a usable `@article` record. |
| PDF attachments | Covered | `get children` resolves the stored PDF and attachment key. |
| PDF full text | Covered | The POC retrieved 100,000+ characters from all 25 indexed pages. |
| Literal grep | Covered with constraints | `get fulltext ... | rg` works with UTF-8 configured; direct `rg` over `.zotero-ft-cache` also works. |
| Tags and recent items | Covered | Dedicated CLI commands exist and tags were verified live. |
| Notes and annotations | CLI surface present | Commands are exposed, but creation needs write-capable mode and annotation fidelity was not exercised by this POC. |
| Agent protocol | Covered | The package exposes both `zotero-cli` and an MCP server. |
| Bibliographic organization | Better than `know` | Zotero adds citation formats, duplicate handling, annotations, feeds, and a mature PDF reader. |

## Partial or conditional coverage

| Capability | Result | Consequence |
|---|---|---|
| Collections | Local reads work; writes require Zotero Web API credentials | A completely local unsynced library cannot be organized through this CLI. |
| Add by arXiv URL or DOI | Implemented, but treated as a write | It requires hybrid/Web API mode; it is not available with only the local API. |
| arXiv refresh | Import only | Zotero stores the item and PDF but does not preserve a declarative command that periodically refetches arXiv metadata. |
| Corpus-wide PDF keyword search | CLI gap with semantic fallback | `search --qmode everything` reported that the literal search returned no results, then substituted semantically related papers. The official local API returned the exact attachment, and direct cache `rg` worked. |
| Semantic search | Optional extra, verified | `zotero-mcp-server[semantic]` built a two-document full-text Chroma index and returned the paper as the top result. The index is separate and manual by default. |
| Windows stdout | Workaround required | Full-text output failed on a Unicode math character under the default code page; `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` fixed it. |
| Remote agents | Conditional | Local API access requires Zotero to be running on the same host. Remote agents need a scoped Web API key, MCP bridge, or generated filesystem mirror. |

## Not covered

| `know` capability | Zotero CLI status |
|---|---|
| Recursive site crawling, depth/page limits, anti-bot detection, and browser-cookie CDP capture | Not supported |
| YouTube or local video transcription, languages, timestamps, and segments | Not supported |
| Git repository clone/synchronization, branch selection, and source-tree export | Not supported |
| Confluence space/CQL synchronization | Not supported |
| Jira JQL/project synchronization | Not supported |
| Aha workspace synchronization | Not supported |
| Google release-feed normalization | Not supported |
| Declarative source manifests with update and delete commands | Not supported |
| Scheduled multi-source refresh and stale/unsynced status | Not supported |
| Normalized Markdown library with provenance frontmatter | Not supported |
| OKF concept export, zip export/import, and cross-key merge | Not supported |
| Television row/preview formats and drill-down browsing | Not supported |
| Deterministic Semantic OKF snapshots, RDF graphs, SHACL, and local SPARQL | Not supported |
| Lossless Confluence Storage XML and attachment round trips | Not supported |

## Replacement conclusion

Zotero CLI is a strong replacement for the actual arXiv-heavy library and for
agent retrieval after an item key is known. It is not a replacement for the
multi-source synchronization framework or the OKF/Confluence-specialized
skills.

The remaining agent-access problem is narrower than `know`: build a read-only,
incremental Zotero-to-Markdown mirror so agents can run corpus-wide `rg` against
stable, metadata-rich filenames. That mirror should use the official local API
and `/fulltext` endpoint rather than reading `zotero.sqlite` or treating
`.zotero-ft-cache` as a public format.
