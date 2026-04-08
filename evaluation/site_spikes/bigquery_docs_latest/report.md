# Site Capture Spike Report

- Target URL: `https://docs.cloud.google.com/bigquery/docs`
- Generated at: `2026-04-08T03:06:59Z`
- Max pages: `24`
- Max depth: `1`
- CDP URL: `http://127.0.0.1:9222`
- Python: `3.14.3`
- Platform: `Windows-11-10.0.26200-SP0`

## Ranking

| Rank | Strategy | Status | Pages | Useful | Blocked | Avg chars | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | http_plain_bfs | ok | 1 | 0 | 1 | 1089 | 0.88 |
| 2 | http_cdp_bfs | failed | 0 | 0 | 0 | 0 | 0.00 |
| 3 | crawl4ai_deep | unavailable | 0 | 0 | 0 | 0 | 0.00 |
| 4 | browser_cdp_bfs | unavailable | 0 | 0 | 0 | 0 | 0.00 |
| 5 | browser_seeded_http_cdp | unavailable | 0 | 0 | 0 | 0 | 0.00 |

## Notes

### http_plain_bfs

- Status: `ok`
- Requests-based breadth-first crawl.
- No browser state is used, so anti-bot pages are expected on Google-hosted docs.
- Start URL: https://docs.cloud.google.com/bigquery/docs
- Sample capture count stored on disk: `1`

### http_cdp_bfs

- Status: `failed`
- Error: `RuntimeError: CDP-assisted site crawling requires the `playwright` Python package. Install it before using KNOW_SITE_CDP_URL.`
- Requests-based breadth-first crawl.
- Chrome cookies are loaded through CDP before issuing HTTP requests.

### crawl4ai_deep

- Status: `unavailable`
- Error: `No module named 'crawl4ai'`
- Deep crawl baseline used by the current site adapter.
- Connected to the live Chrome session through CDP.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

### browser_cdp_bfs

- Status: `unavailable`
- Error: `No module named 'playwright'`
- Every page is navigated inside the live Chrome session.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

### browser_seeded_http_cdp

- Status: `unavailable`
- Error: `No module named 'playwright'`
- The browser seeds high-signal documentation links, then requests + Chrome cookies download pages faster.
- This is the main candidate if you want a production replacement for full browser crawling.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

## Recommendation

`http_plain_bfs` ranked first in this run. Prefer it when you need the highest mix of useful page count, low block rate, and runtime efficiency.
