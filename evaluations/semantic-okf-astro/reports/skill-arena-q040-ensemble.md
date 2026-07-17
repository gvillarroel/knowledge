# Accepted Skill Arena q040 Paired Results

This report contains 1 explicitly selected final compare run(s). Every family remains an independent paired control/treatment diagnostic.

| Family | Control | Treatment | Delta | Treatment evidence | Harness | Accepted run |
|---|---:|---:|---:|---|---|---|
| ensemble | 0% | 100% | +100 pp | pass | FAILED | `2026-07-16T11-38-31-783Z-compare` |

An overall harness status of `FAILED` is compatible with an accepted pair because the all-cells rule includes the intentionally failing control. Each result covers one frozen q040 prompt, not the aggregate 40-question benchmark.
Promptfoo contract pass and authoritative evidence validity are separate gates. Evidence validity below is reconstructed independently from the frozen source-record crosswalk and authoritative ledger; response fields are never normalized.

## ensemble

Accepted run: `2026-07-16T11-38-31-783Z-compare` (`eval-EG6-2026-07-16T11:38:39`), benchmark `semantic-okf-astro-q040-ensemble-paired`. The metrics and responses in this section bind only that directory.

### Source bindings

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| promptfoo_results | 56732 | `5c4de2563c728916edcf0ee9224d5459fb9aafc26d01bc0c16388d23c1bbbc46` |
| promptfoo_config | 10795 | `c025b17a2a3f11a2affe7b2f4f94741bc360f38b1123f04367313150451fe7dc` |
| skill_arena_summary | 39693 | `34e0a85ef781b1904de3ef4df2b02cea318f182a37f9d0a5a51a6b7a905e1bd7` |
| authoritative_records | 3455749 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| source_combination | 438819 | `c09e952254e5f2a4673ec0864bb09be333d8e914a1d0c46284e33953296cb783` |

### Profile outcomes

| Profile | Role | Pass | Score | Assertions | Time | Strict JSON | Evidence valid |
|---|---|---:|---:|---:|---:|---:|---:|
| knowledge-only-control | passive-control | no | 0 | 0/3 | 114571 ms | no | 4/4 (pass) |
| ensemble-consult-treatment | treatment | yes | 1 | 3/3 | 271042 ms | yes | 5/5 (pass) |

The ensemble control's leading JSON object is recoverable, but its raw output has one extra closing brace. Therefore it fails strict JSON parsing and all three assertions. The treatment is strict JSON and passes `response-format`, `response-contract`, and `grounded-answer`.

### Exact parsed responses

The objects below are parsed directly from each raw response without changing any answer, claim, evidence identity, locator, or hash. Raw environment metadata and temporary workspace paths are excluded.

#### knowledge-only-control

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use hybrid rendering: configure `output: 'static'` (the default behavior), install an adapter for the deployment runtime, and opt only the account page and API endpoint out of prerendering with `export const prerender = false`. The account page can then read request-time cookies through `Astro.cookies` and personalize its response. The API route should be a server endpoint exporting its HTTP method function, such as `GET`, and return a `Response`; in on-demand mode it is built when requested and can inspect the full incoming `Request`. Every other route remains prerendered at build time. If server output becomes the default, change configuration to `output: 'server'` with the same adapter: routes become on-demand by default, so retain request-time behavior for the account page and API route without `prerender = false`, and explicitly add `export const prerender = true` to every route that must remain static, including the rest of the site and any static endpoint.",
    "claims": [
      {
        "statement": "The primarily static design is `output: 'static'` with a server-capable adapter, using `prerender = false` only on the account page and request-time API route; all other routes stay static.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "The account page can read, set, get, and delete cookies at request time through `Astro.cookies` once it is on-demand rendered.",
        "evidence_indices": [
          1
        ]
      },
      {
        "statement": "The API route should export an HTTP method handler such as `GET` and return a `Response`; on-demand endpoints are built when requested and can use the full request object.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "With `output: 'server'`, all routes are on-demand by default; routes that should remain static must explicitly export `prerender = true`.",
        "evidence_indices": [
          3
        ]
      }
    ]
  },
  "evidence": [
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": {
        "end": 3921,
        "kind": "character-range",
        "start": 1272
      },
      "text_sha256": "b465cc2f85513f3f99eede0264ec7468587abde4659584c529590c143c8016be"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": {
        "end": 7714,
        "kind": "character-range",
        "start": 5628
      },
      "text_sha256": "589f4fc0d0d9792678ff92e2dc057187fd42a2fe9d81d0f9e7b2f0328b1ebd4c"
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": {
        "end": 4956,
        "kind": "character-range",
        "start": 3534
      },
      "text_sha256": "39a45f987a3d5b4b0247a95d5d8a270af49b7db72637c15b3f4c0e1c404db51b"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": {
        "end": 5626,
        "kind": "character-range",
        "start": 3922
      },
      "text_sha256": "dadff917854661ded6a3491bff9307a5965a12909f162393d06696aa92f741c0"
    }
  ]
}
```

#### ensemble-consult-treatment

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "For a predominantly static Astro site, configure `output: 'static'` in `astro.config.mjs`; this is the static default and keeps pages and endpoints prerendered at build time. Because two routes need server behavior, add a server-capable adapter, for example `@astrojs/node`, and configure its standalone mode. In `src/pages/account.astro`, export `const prerender = false`; this opts that page out of prerendering so it is generated on demand. Apply the same export in the request-time API endpoint, such as `src/pages/api/account.ts`, so the endpoint runs per request rather than becoming a build artifact. The account page and endpoint can then use request-time features: `Astro.cookies` can check, get, set, or delete cookies, and request headers are available through `Astro.request.headers` (including the cookie header). Leave every other page and endpoint without that opt-out, preserving static generation. The inverse design starts with a server default: set `output: 'server'` and use the server adapter; routes are then generated on request by default. Mark routes that should remain static with `export const prerender = true`, including the otherwise-static pages and any static endpoint. In server mode, do not add `prerender = false` to dynamic routes because it is already the default; use `true` only for the static exceptions.",
    "claims": [
      {
        "statement": "Use `output: 'static'` and keep ordinary pages and endpoints prerendered; static output supports opting individual routes into on-demand rendering.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "Install a server adapter such as `@astrojs/node` and configure its Node adapter in standalone mode for the on-demand routes.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "Export `const prerender = false` in the cookie-aware account page and request-time API endpoint; the remaining site stays statically generated.",
        "evidence_indices": [
          3,
          4
        ]
      },
      {
        "statement": "On-demand pages and API endpoints can use `Astro.cookies`, while request headers such as the cookie are available through `Astro.request.headers`.",
        "evidence_indices": [
          3
        ]
      },
      {
        "statement": "For the inverse server-default design, set `output: 'server'`; use `export const prerender = true` on static exceptions, leaving other routes on-demand by default.",
        "evidence_indices": [
          3,
          1
        ]
      }
    ]
  },
  "evidence": [
    {
      "source_id": "astro-doc-3c50462cdbdb7a32",
      "record_id": "sources/mdx/reference/configuration-reference",
      "concept_path": "concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md",
      "source_path": "sources/mdx/reference/configuration-reference.mdx",
      "record_sha256": "09aeb7984eb813a284eb3ed10e6378a0ce05380a9e9c1e8985e3e812a2e823a0",
      "locator": {
        "end": 77315,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "c69c4ecedb148c9c163e730641e0711829bc1166ef65a559b6c6592542b7e865"
    },
    {
      "source_id": "astro-doc-ed7b0d0a27542ceb",
      "record_id": "sources/mdx/reference/routing-reference",
      "concept_path": "concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md",
      "source_path": "sources/mdx/reference/routing-reference.mdx",
      "record_sha256": "a2c19f8c3c653f3d3e5457adbc855842ca1ad1f7cdcebafe0ccbda63852cecb8",
      "locator": {
        "end": 12656,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "e9c7951303b435bed3bb9d9964091ea4aef87db13643b05f6e4016f948ec46c1"
    },
    {
      "source_id": "astro-doc-8aa98ab02807f857",
      "record_id": "sources/mdx/guides/integrations-guide/node",
      "concept_path": "concepts/astro-doc-8aa98ab02807f857/sources-mdx-guides-integrations-guide-node-49b507ef1d.md",
      "source_path": "sources/mdx/guides/integrations-guide/node.mdx",
      "record_sha256": "5af13752fc7aea5fa9b4c3b2eea5cdce9ece6a6f4f92c5194683ead8cdd43b81",
      "locator": {
        "end": 10697,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "1dfbdfe58f8174d9d93bd899d96092fd663277e77079a5182dcebb0739c0aa9d"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": {
        "end": 11578,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002"
    },
    {
      "source_id": "astro-doc-60e7507194bf5ea2",
      "record_id": "sources/mdx/guides/upgrade-to/v5",
      "concept_path": "concepts/astro-doc-60e7507194bf5ea2/sources-mdx-guides-upgrade-to-v5-b791353c5f.md",
      "source_path": "sources/mdx/guides/upgrade-to/v5.mdx",
      "record_sha256": "e509c1c555389d67a2808cb269633f34de2a2472fc060e0c3f6589728336227f",
      "locator": {
        "end": 58389,
        "fragment": null,
        "kind": "character-range",
        "start": 0,
        "target": "record-body"
      },
      "text_sha256": "be03c6bc217eebb084efea3a0af8c7f8d989a90b086ca8d8429d3cec5340deb3"
    }
  ]
}
```

### Non-accepted developmental traces

Earlier append-only directories below are audit traces only. They are excluded from accepted metrics and responses.

| Run | Summary | Successes | Failures | Errors |
|---|---:|---:|---:|---:|
| 2026-07-16T09-54-39-228Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T10-58-21-214Z-compare | yes | 0 | 2 | 0 |
| 2026-07-16T11-12-46-713Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T11-13-07-640Z-compare | yes | 1 | 1 | 0 |
| 2026-07-16T11-30-25-441Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T11-30-35-958Z-compare | yes | 0 | 2 | 0 |


No MCP runtime participates in this comparison or summary.
