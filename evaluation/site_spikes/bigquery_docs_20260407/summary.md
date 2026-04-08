# BigQuery Docs Spike Summary

## Scope

Target: `https://docs.cloud.google.com/bigquery/docs`

Run date: `2026-04-08`

Runner:

```bash
uv run python scripts/run_site_spikes.py https://docs.cloud.google.com/bigquery/docs --max-pages 12 --max-depth 1 --cdp-url http://127.0.0.1:9222 --output-dir evaluation/site_spikes/bigquery_docs_20260407
```

## Observed results

| Strategy | Result |
|---|---|
| `http_plain_bfs` | Blocked immediately by Google's `sorry` flow. Not viable for this host. |
| `crawl4ai_deep` | Could not run in the local Python 3.14 environment because `crawl4ai` did not install cleanly due an `lxml` build failure. |
| `http_cdp_bfs` | Best raw throughput in this run. Captured 12/12 useful pages in 9.78 seconds. |
| `browser_cdp_bfs` | Best fidelity. Captured 12/12 useful pages in 13.27 seconds with much cleaner page bodies because the extraction is scoped to the rendered `main` content. |
| `browser_seeded_http_cdp` | Best architecture candidate. It captured 10 useful pages in 10.23 seconds and produced a focused set of pages while avoiding full browser cost on every page. |

## What matters

- Real Chrome cookies are enough to make direct HTTP crawling work again for `docs.cloud.google.com`.
- Plain HTTP without browser state is not workable here.
- Full browser crawling is reliable, but it is slower and more expensive than cookie-assisted HTTP.
- The current HTTP text extraction keeps global navigation, locale links, and footer content. That makes `http_cdp_bfs` look strong on page count and total text volume, but the Markdown is noisier than the browser-based extraction.
- The browser-based captures are materially cleaner because they read rendered `main` content instead of stripping the entire HTML document.

## Recommendation

If the next goal is the fastest production improvement with minimal operational cost, promote a CDP-cookie HTTP strategy first.

If the next goal is cleaner Markdown, implement a hybrid:

1. Use the live browser only to open the seed page and collect high-signal in-subtree links.
2. Reuse Chrome cookies for the actual HTTP downloads.
3. Replace full-document HTML stripping with `main` or `article` extraction before converting to Markdown.

That hybrid should preserve the efficiency of `http_cdp_bfs` while moving content quality closer to `browser_cdp_bfs`.
