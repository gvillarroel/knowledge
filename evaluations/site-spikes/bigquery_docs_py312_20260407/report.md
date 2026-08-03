# Site Capture Spike Report

- Target URL: `https://docs.cloud.google.com/bigquery/docs`
- Generated at: `2026-04-08T01:51:58Z`
- Max pages: `12`
- Max depth: `1`
- CDP URL: `http://127.0.0.1:9222`
- Python: `3.12.13`
- Platform: `Windows-11-10.0.26200-SP0`

## Ranking

| Rank | Strategy | Status | Pages | Useful | Blocked | Avg chars | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | crawl4ai_deep | ok | 11 | 11 | 0 | 203894 | 9.24 |
| 2 | http_plain_bfs | ok | 1 | 0 | 1 | 1089 | 0.68 |
| 3 | browser_seeded_http_cdp | failed | 0 | 0 | 0 | 0 | 0.38 |
| 4 | browser_cdp_bfs | failed | 0 | 0 | 0 | 0 | 0.42 |
| 5 | http_cdp_bfs | failed | 0 | 0 | 0 | 0 | 0.46 |

## Notes

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
- Error: `Error: BrowserType.connect_over_cdp: connect ECONNREFUSED 127.0.0.1:9222
Call log:
  - <ws preparing> retrieving websocket url from http://127.0.0.1:9222
`
- The browser seeds high-signal documentation links, then requests + Chrome cookies download pages faster.
- This is the main candidate if you want a production replacement for full browser crawling.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

### browser_cdp_bfs

- Status: `failed`
- Error: `Error: BrowserType.connect_over_cdp: connect ECONNREFUSED 127.0.0.1:9222
Call log:
  - <ws preparing> retrieving websocket url from http://127.0.0.1:9222
`
- Every page is navigated inside the live Chrome session.
- No pages were captured for https://docs.cloud.google.com/bigquery/docs.

### http_cdp_bfs

- Status: `failed`
- Error: `Error: BrowserType.connect_over_cdp: connect ECONNREFUSED 127.0.0.1:9222
Call log:
  - <ws preparing> retrieving websocket url from http://127.0.0.1:9222
`
- Requests-based breadth-first crawl.
- Chrome cookies are loaded through CDP before issuing HTTP requests.

## Recommendation

`crawl4ai_deep` ranked first in this run. Prefer it when you need the highest mix of useful page count, low block rate, and runtime efficiency.
