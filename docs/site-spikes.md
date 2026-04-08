# Site Capture Spikes

This repository includes a focused benchmark for documentation-heavy sites that do not behave well under plain HTTP crawling.

## Goal

Compare multiple capture strategies against one documentation subtree and persist:

- a machine-readable JSON report;
- a Markdown summary;
- sampled page Markdown per strategy.

The current target that motivated this work is:

`https://docs.cloud.google.com/bigquery/docs`

## Runner

Use the standalone runner:

```bash
uv run python scripts/run_site_spikes.py https://docs.cloud.google.com/bigquery/docs --max-pages 12 --max-depth 1 --cdp-url http://127.0.0.1:9222 --output-dir evaluation/site_spikes/bigquery_docs
```

## Strategies

- `crawl4ai_deep` uses the current deep-crawl baseline when the dependency is installed.
- `http_plain_bfs` uses plain `requests` breadth-first crawling with no browser state.
- `http_cdp_bfs` uses `requests` plus cookies copied from a live Chrome session through CDP.
- `browser_cdp_bfs` loads every page in the live browser through CDP.
- `browser_seeded_http_cdp` discovers links in the browser and downloads the candidate pages through HTTP with the same Chrome cookies.

## Interpreting the report

The benchmark ranks strategies by:

1. successful execution;
2. useful pages captured;
3. low blocked-page count;
4. runtime;
5. average Markdown size.

For Google-hosted docs, the expected pattern is:

- plain HTTP gets blocked quickly;
- CDP cookies make HTTP viable again;
- full browser crawling is accurate but slower;
- browser-seeded HTTP is often the best efficiency tradeoff.

## Production choice

The production `site` adapter now prefers the CDP BFS HTTP path for `docs.cloud.google.com` whenever `KNOW_SITE_CDP_URL` is set.

That path:

- reuses cookies from the live Chrome session;
- keeps traversal inside the documentation subtree;
- extracts `main` or `article` content before HTML-to-text conversion;
- keeps `crawl4ai` available for other hosts or when `KNOW_SITE_FORCE_CRAWL4AI=1` is set.
