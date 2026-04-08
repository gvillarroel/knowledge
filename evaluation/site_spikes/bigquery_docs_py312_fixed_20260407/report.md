# Site Capture Spike Report

- Target URL: `https://docs.cloud.google.com/bigquery/docs`
- Generated at: `2026-04-08T01:58:21Z`
- Max pages: `12`
- Max depth: `1`
- CDP URL: `http://127.0.0.1:9222`
- Python: `3.12.13`
- Platform: `Windows-11-10.0.26200-SP0`

## Ranking

| Rank | Strategy | Status | Pages | Useful | Blocked | Avg chars | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | http_cdp_bfs | ok | 12 | 12 | 0 | 48502 | 8.43 |
| 2 | crawl4ai_deep | ok | 11 | 11 | 0 | 205425 | 7.35 |
| 3 | http_plain_bfs | ok | 1 | 0 | 1 | 1089 | 0.71 |
| 4 | browser_seeded_http_cdp | failed | 0 | 0 | 0 | 0 | 60.52 |
| 5 | browser_cdp_bfs | failed | 0 | 0 | 0 | 0 | 62.76 |

## Notes

### http_cdp_bfs

- Status: `ok`
- Requests-based breadth-first crawl.
- Chrome cookies are loaded through CDP before issuing HTTP requests.
- Start URL: https://docs.cloud.google.com/bigquery/docs
- Sample capture count stored on disk: `12`

### crawl4ai_deep

- Status: `ok`
- Deep crawl baseline used by the current site adapter.
- Connected to the live Chrome session through CDP.
- Sample capture count stored on disk: `11`

### http_plain_bfs

- Status: `ok`
- Requests-based breadth-first crawl.
- No browser state is used, so anti-bot pages are expected on Google-hosted docs.
- Start URL: https://docs.cloud.google.com/bigquery/docs
- Sample capture count stored on disk: `1`

### browser_seeded_http_cdp

- Status: `failed`
- Error: `TimeoutError: Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://docs.cloud.google.com/bigquery/docs", waiting until "domcontentloaded"
`
- The browser seeds high-signal documentation links, then requests + Chrome cookies download pages faster.
- This is the main candidate if you want a production replacement for full browser crawling.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

### browser_cdp_bfs

- Status: `failed`
- Error: `TimeoutError: Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://docs.cloud.google.com/bigquery/docs/ai-introduction", waiting until "domcontentloaded"
`
- Every page is navigated inside the live Chrome session.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

## Recommendation

`http_cdp_bfs` ranked first in this run. Prefer it when you need the highest mix of useful page count, low block rate, and runtime efficiency.
