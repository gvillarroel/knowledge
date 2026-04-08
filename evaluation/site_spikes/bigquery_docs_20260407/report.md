# Site Capture Spike Report

- Target URL: `https://docs.cloud.google.com/bigquery/docs`
- Generated at: `2026-04-08T01:40:34Z`
- Max pages: `12`
- Max depth: `1`
- CDP URL: `http://127.0.0.1:9222`
- Python: `3.14.3`
- Platform: `Windows-11-10.0.26200-SP0`

## Ranking

| Rank | Strategy | Status | Pages | Useful | Blocked | Avg chars | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | http_cdp_bfs | ok | 12 | 12 | 0 | 48502 | 9.78 |
| 2 | browser_cdp_bfs | ok | 12 | 12 | 0 | 19314 | 13.27 |
| 3 | browser_seeded_http_cdp | ok | 10 | 10 | 0 | 53907 | 10.23 |
| 4 | http_plain_bfs | ok | 1 | 0 | 1 | 1089 | 0.85 |
| 5 | crawl4ai_deep | unavailable | 0 | 0 | 0 | 0 | 0.00 |

## Notes

### http_cdp_bfs

- Status: `ok`
- Requests-based breadth-first crawl.
- Chrome cookies are loaded through CDP before issuing HTTP requests.
- Start URL: https://docs.cloud.google.com/bigquery/docs
- Sample capture count stored on disk: `12`

### browser_cdp_bfs

- Status: `ok`
- Every page is navigated inside the live Chrome session.
- This is the highest-fidelity browser simulation in the benchmark.
- Sample capture count stored on disk: `12`

### browser_seeded_http_cdp

- Status: `ok`
- The browser seeds high-signal documentation links, then requests + Chrome cookies download pages faster.
- This is the main candidate if you want a production replacement for full browser crawling.
- Sample capture count stored on disk: `10`

### http_plain_bfs

- Status: `ok`
- Requests-based breadth-first crawl.
- No browser state is used, so anti-bot pages are expected on Google-hosted docs.
- Start URL: https://docs.cloud.google.com/bigquery/docs
- Sample capture count stored on disk: `1`

### crawl4ai_deep

- Status: `unavailable`
- Error: `No module named 'crawl4ai'`
- Deep crawl baseline used by the current site adapter.
- Connected to the live Chrome session through CDP.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

## Recommendation

`http_cdp_bfs` ranked first in this run. Prefer it when you need the highest mix of useful page count, low block rate, and runtime efficiency.
