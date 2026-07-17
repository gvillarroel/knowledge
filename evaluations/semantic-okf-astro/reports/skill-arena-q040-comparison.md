# Accepted Skill Arena q040 Paired Results

This report contains 6 explicitly selected final compare run(s). Every family remains an independent paired control/treatment diagnostic.

| Family | Control | Treatment | Delta | Treatment evidence | Harness | Accepted run |
|---|---:|---:|---:|---|---|---|
| legacy | 0% | 0% | +0 pp | fail | FAILED | `2026-07-16T11-50-44-330Z-compare` |
| embeddings | 100% | 100% | +0 pp | fail | PASSED | `2026-07-16T11-50-43-971Z-compare` |
| classical | 100% | 100% | +0 pp | pass | PASSED | `2026-07-16T11-55-25-736Z-compare` |
| adaptive | 0% | 100% | +100 pp | pass | FAILED | `2026-07-16T11-55-26-061Z-compare` |
| entity-graph | 0% | 0% | +0 pp | pass | FAILED | `2026-07-16T11-59-19-741Z-compare` |
| ensemble | 0% | 100% | +100 pp | pass | FAILED | `2026-07-16T11-38-31-783Z-compare` |

An overall harness status of `FAILED` is compatible with an accepted pair because the all-cells rule includes the intentionally failing control. Each result covers one frozen q040 prompt, not the aggregate 40-question benchmark.
Promptfoo contract pass and authoritative evidence validity are separate gates. Evidence validity below is reconstructed independently from the frozen source-record crosswalk and authoritative ledger; response fields are never normalized.

## legacy

Accepted run: `2026-07-16T11-50-44-330Z-compare` (`eval-DIs-2026-07-16T11:50:51`), benchmark `semantic-okf-astro-q040-legacy-paired`. The metrics and responses in this section bind only that directory.

### Source bindings

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| promptfoo_results | 64477 | `48b38bb1df8ee3a11d08f6023ae8367ff168801b24ee2f0e4783366dd275025f` |
| promptfoo_config | 10754 | `c5e37231343e2ebcd1ec8d64aaec2a59d1e3540ffb91d15b953fc31ee9ec3790` |
| skill_arena_summary | 46372 | `808e6ab9fcc6ab7ed340ab11f4af384cc4c6ca3fd0944af97c65d660d0cce567` |
| authoritative_records | 3455749 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| source_combination | 438819 | `c09e952254e5f2a4673ec0864bb09be333d8e914a1d0c46284e33953296cb783` |

### Profile outcomes

| Profile | Role | Pass | Score | Assertions | Time | Strict JSON | Evidence valid |
|---|---|---:|---:|---:|---:|---:|---:|
| knowledge-only-control | passive-control | no | 0.6666666666666666 | 2/3 | 87240 ms | yes | 0/7 (fail) |
| legacy-consult-treatment | treatment | no | 0.6666666666666666 | 2/3 | 97552 ms | yes | 0/6 (fail) |

Authoritative evidence failures:

- `knowledge-only-control` evidence 0: locator is not an object
- `knowledge-only-control` evidence 1: locator is not an object
- `knowledge-only-control` evidence 2: locator is not an object
- `knowledge-only-control` evidence 3: locator is not an object
- `knowledge-only-control` evidence 4: locator is not an object
- `knowledge-only-control` evidence 5: locator is not an object
- `knowledge-only-control` evidence 6: locator is not an object
- `legacy-consult-treatment` evidence 0: evidence keys/order differ from the closed response contract; locator is not an object
- `legacy-consult-treatment` evidence 1: evidence keys/order differ from the closed response contract; locator is not an object
- `legacy-consult-treatment` evidence 2: evidence keys/order differ from the closed response contract; locator is not an object
- `legacy-consult-treatment` evidence 3: evidence keys/order differ from the closed response contract; locator is not an object
- `legacy-consult-treatment` evidence 4: evidence keys/order differ from the closed response contract; locator is not an object
- `legacy-consult-treatment` evidence 5: evidence keys/order differ from the closed response contract; locator is not an object

### Exact parsed responses

The objects below are parsed directly from each raw response without changing any answer, claim, evidence identity, locator, or hash. Raw environment metadata and temporary workspace paths are excluded.

#### knowledge-only-control

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use Astro’s default static output and add the adapter for the deployment runtime that will execute the dynamic routes. Keep the account page and API endpoint on demand with per-route prerender flags; all unspecified routes remain build-time static. The account page can read request cookies through Astro.cookies (or the request Cookie header), while the endpoint becomes a live API route when opted out of prerendering. If the application later becomes predominantly dynamic, switch to server output and invert the route flags so only explicitly static pages and endpoints are prerendered.",
    "claims": [
      {
        "statement": "Configure the primarily static design with the default static output, install the adapter matching the deployment runtime, and set `export const prerender = false` in both the cookie-aware account page and request-time API endpoint; other routes remain prerendered.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "In static output, an endpoint is generated at build time unless it opts out; with `prerender = false`, it is called on each request and functions as a live server API route.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "The account page may use `Astro.cookies` to check, set, get, or delete cookies, and request-time code can read the incoming cookie through `Astro.request.headers`; these features require the route not to be statically generated.",
        "evidence_indices": [
          3,
          4
        ]
      },
      {
        "statement": "For the inverse server-default design, configure `output: 'server'` with the adapter, omit `prerender = false` from dynamic routes, and add `export const prerender = true` to every page or endpoint that should remain static.",
        "evidence_indices": [
          5,
          6
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
      "locator": "Rendering mode > On-demand rendering",
      "text_sha256": "b1bf5f6607d41ae50f8c9a32371bff14628d0a7fc5963aa413f29fe283752de1"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "Enabling on-demand rendering",
      "text_sha256": "ccea10e4cbbbcf50a3d933613dc40f594577a034a21f344ea089412d999314b4"
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": "Server Endpoints (API Routes)",
      "text_sha256": "85eba164a3d64155fd8c5c7afb5f5fda972cb52a46d85065e23150957001ae4c"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "On-demand rendering features > Cookies",
      "text_sha256": "a0115cad76024f7bb30a80aaae8bd1041e80fa14b519763cefbae95fac72ceb6"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "On-demand rendering features > Request > Astro.request.headers",
      "text_sha256": "3e536fce5e025a9017ce1d34ba67f3f2bb7e2a390f01975b1ac7ecbd43845e19"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "Server mode",
      "text_sha256": "b216fa63434efd2c0d6bcb39eb4b50bcb50ee5415c4a04a772144f7b5e396bfc"
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": "Server Endpoints (API Routes)",
      "text_sha256": "dbd3c3f1d53a5e7c9f50b81f51e84380593f77e81dcb382fdae0fa29f8a62dee"
    }
  ]
}
```

#### legacy-consult-treatment

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use `output: 'static'` (the default) and configure an adapter for the deployment runtime, such as Node, Netlify, Vercel, or Cloudflare. The adapter enables request-time rendering while allowing the site to retain static output. In `src/pages/account.astro`, export `const prerender = false`; the page can then read, set, or delete request cookies through `Astro.cookies` and render account content per visit. Likewise, in `src/pages/api/account.ts` (or another endpoint file), export `const prerender = false` and implement `GET` (and any other needed HTTP methods). In static output, endpoints otherwise execute at build time, but this endpoint becomes a live server endpoint invoked for each request. All other pages and endpoints should omit a prerender override, so they remain prerendered. The inverse design is appropriate when most routes are dynamic: set `output: 'server'` with the adapter. Pages and endpoints then render on demand by default, so the account page and API route no longer need `prerender = false`; explicitly mark static exceptions, such as public or informational pages and static endpoints, with `export const prerender = true`. Server output changes the default rendering behavior rather than adding separate functionality.",
    "claims": [
      {
        "statement": "Configure `output: 'static'` and a deployment-matching adapter; static routes remain prerendered unless they opt out.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "Set `export const prerender = false` on the cookie-aware account page, where on-demand rendering permits cookie operations through `Astro.cookies`.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "Set `export const prerender = false` on the API endpoint so it is called live on requests rather than executed at build time.",
        "evidence_indices": [
          3
        ]
      },
      {
        "statement": "With `output: 'server'`, server rendering becomes the default; use `export const prerender = true` for static exceptions.",
        "evidence_indices": [
          4,
          5
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
      "locator": "sources/mdx/reference/configuration-reference.mdx",
      "text_sha256": "5c3fb16a3f7310024fe00a3a76083f9beda2a8e2b8ddd82c934ff6729efaddf1",
      "text": "**Type:** `'static' | 'server'`\n**Default:** `'static'`\n\nSpecifies the output target for builds.\n\n- `'static'` - Prerender all your pages by default, outputting a completely static site if none of your pages opt out of prerendering.\n- `'server'` - Use server-side rendering (SSR) for all pages by default, always outputting a server-rendered site."
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "sources/mdx/guides/on-demand-rendering.mdx",
      "text_sha256": "0735fd5cef79225fd6426ed55fcaec759f13be08435b6f3bebb836cdb59b75fb",
      "text": "To render any page on demand, you need to add an **adapter**."
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "sources/mdx/guides/on-demand-rendering.mdx",
      "text_sha256": "a0115cad76024f7bb30a80aaae8bd1041e80fa14b519763cefbae95fac72ceb6",
      "text": "A page or API endpoint rendered on demand can check, set, get, and delete cookies."
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": "sources/mdx/guides/endpoints.mdx",
      "text_sha256": "85eba164a3d64155fd8c5c7afb5f5fda972cb52a46d85065e23150957001ae4c",
      "text": "In statically-generated sites, your custom endpoints are called at build time to produce static files. If you opt in to [SSR](/en/guides/on-demand-rendering/) mode, custom endpoints turn into live server endpoints that are called on request."
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "sources/mdx/guides/on-demand-rendering.mdx",
      "text_sha256": "b216fa63434efd2c0d6bcb39eb4b50bcb50ee5415c4a04a772144f7b5e396bfc",
      "text": "For a **highly dynamic app**, after adding an adapter, you can [set your build output configuration to `output: 'server'`](/en/reference/configuration-reference/#output) to **server-render all your pages by default**."
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "sources/mdx/guides/on-demand-rendering.mdx",
      "text_sha256": "7901d49146dd336825050851c010faa528b6d8c4cb9ed35058c2c9fa76c7010e",
      "text": "Add `export const prerender = true` to any page or route to prerender a static page or endpoint:"
    }
  ]
}
```

### Non-accepted developmental traces

Earlier append-only directories below are audit traces only. They are excluded from accepted metrics and responses.

| Run | Summary | Successes | Failures | Errors |
|---|---:|---:|---:|---:|
| 2026-07-16T09-54-48-338Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T11-12-55-752Z-compare | no | N/A | N/A | N/A |

## embeddings

Accepted run: `2026-07-16T11-50-43-971Z-compare` (`eval-PyJ-2026-07-16T11:50:51`), benchmark `semantic-okf-astro-q040-embeddings-paired`. The metrics and responses in this section bind only that directory.

### Source bindings

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| promptfoo_results | 55247 | `2db5417f5127d9d38b8c02f14b3f6773286ee83c12dab828c1619d0601ed8767` |
| promptfoo_config | 10815 | `b97e597ab959ee9bc8787625f0d677e7413749fe52106bae7efe647e6d1386bf` |
| skill_arena_summary | 41890 | `b820f790a7368807586045a9568d3ac022eb8a8545ad734d2760b2b78ce83740` |
| authoritative_records | 3455749 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| source_combination | 438819 | `c09e952254e5f2a4673ec0864bb09be333d8e914a1d0c46284e33953296cb783` |

### Profile outcomes

| Profile | Role | Pass | Score | Assertions | Time | Strict JSON | Evidence valid |
|---|---|---:|---:|---:|---:|---:|---:|
| knowledge-only-control | passive-control | yes | 1 | 3/3 | 96649 ms | yes | 7/7 (pass) |
| embeddings-consult-treatment | treatment | yes | 1 | 3/3 | 79565 ms | yes | 3/5 (fail) |

Authoritative evidence failures:

- `embeddings-consult-treatment` evidence 0: source_id + record_id is absent from the frozen identity crosswalk/ledger
- `embeddings-consult-treatment` evidence 2: source_id + record_id is absent from the frozen identity crosswalk/ledger

### Exact parsed responses

The objects below are parsed directly from each raw response without changing any answer, claim, evidence identity, locator, or hash. Raw environment metadata and temporary workspace paths are excluded.

#### knowledge-only-control

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use Astro’s default static output (`output: 'static'`) and install an adapter for the deployment runtime. Mark only the account page and API route with `export const prerender = false`; every other route remains prerendered at build time. The account page can then use `Astro.cookies` to read, set, or delete the account/session cookie for each request. Implement the API route as a server endpoint exporting `GET` (or another required HTTP method) and return a `Response`; in static mode it also needs `prerender = false`, so it is built when requested and can use request data and server-only behavior. The adapter is required for these on-demand routes and should correspond to the hosting runtime. If server output becomes the default, switch configuration to `output: 'server'` with the same adapter: routes are then server-rendered by default, so explicitly mark the account page and request-time API route as server routes only by leaving them unprerendered, while adding `export const prerender = true` to every otherwise-static page and endpoint. In that inverse design, the cookie-aware page and API remain request-time, and the explicitly opted-in static routes remain build-time artifacts.",
    "claims": [
      {
        "statement": "Configure `output: 'static'` and install an adapter matching the deployment runtime; Astro otherwise prerenders the site, while on-demand rendering requires an adapter.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "Set `export const prerender = false` only on the account page and API route; all other routes remain statically generated.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "Use `Astro.cookies` on the account page for request-time cookie checks and updates; on-demand pages and endpoints can check, set, get, and delete cookies.",
        "evidence_indices": [
          3
        ]
      },
      {
        "statement": "Implement the API as a server endpoint with an exported HTTP-method handler such as `GET` returning a `Response`; in static mode, opt out with `prerender = false`.",
        "evidence_indices": [
          4,
          5
        ]
      },
      {
        "statement": "For the inverse, configure `output: 'server'` with the adapter and add `export const prerender = true` to every route that should remain static; server rendering is then the default.",
        "evidence_indices": [
          6
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
        "end": 613,
        "kind": "character-range",
        "start": 0
      },
      "text_sha256": "51df641659c120649f20e9f54fc626930ca38481a789b16db1cf46009f42cdc6"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": {
        "end": 1270,
        "kind": "character-range",
        "start": 615
      },
      "text_sha256": "7a4c647183189cf496b750f94446b3fd3c84c6037eb5b4e4d1bc3feda6fe122d"
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
        "end": 7329,
        "kind": "character-range",
        "start": 4957
      },
      "text_sha256": "d033726d491d0d9e4b021870e77fc77884f3765192f8eb4078aee107a9468b08"
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

#### embeddings-consult-treatment

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use `output: 'static'` and configure a server-capable adapter, such as `@astrojs/node` (for example, `adapter: node({ mode: 'standalone' })`). Keep the site’s normal behavior by leaving ordinary pages prerendered. In `src/pages/account.astro`, export `const prerender = false`; this makes only the account page render per request, allowing it to read request cookies through `Astro.cookies` (or the request cookie header). Likewise, in the API route file, export `const prerender = false` and export its `GET`, `POST`, or other `APIRoute` handler. The endpoint then runs on demand, receives the endpoint context—including `request`—and returns a `Response`; it can securely process request-time data and cookies. All routes without an override remain statically generated. An adapter is required because the build contains server-rendered routes. Conversely, if server output becomes the default, set `output: 'server'` with the same server adapter. Pages and endpoints then render on demand by default, so the account page and API route need no `prerender = false` declarations. Add `export const prerender = true` to every route that should remain static, such as the otherwise-static pages, thereby making the inverse arrangement explicit.",
    "claims": [
      {
        "statement": "Use static output with a server-capable adapter, and opt individual routes out with `prerender = false`.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "An on-demand page can read, set, get, and delete cookies, while request headers expose the incoming cookie.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "A server endpoint is an API route whose handler receives request context and returns a `Response`; it is built when requested.",
        "evidence_indices": [
          3
        ]
      },
      {
        "statement": "With `output: 'server'`, routes are on-demand by default and individual static routes use `prerender = true`.",
        "evidence_indices": [
          4
        ]
      }
    ]
  },
  "evidence": [
    {
      "source_id": "astro-doc-67458ae49efafc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49efafc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
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
      "source_id": "astro-doc-8aa98ab02807f857",
      "record_id": "sources/mdx/guides/integrations-guide/node",
      "concept_path": "concepts/astro-doc-8aa98ab02807f857/sources-mdx-guides-integrations-guide-node-49b507ef1d.md",
      "source_path": "sources/mdx/guides/integrations-guide/node.mdx",
      "record_sha256": "5af13752fc7aea5fa9b4c3b2eea5cdce9ece6a6f4f92c5194683ead8cdd43b81",
      "locator": {
        "end": 4275,
        "kind": "character-range",
        "start": 0
      },
      "text_sha256": "a8f8c2c536920cd0f32e5bce1c9ee2f13705bfe4a98b39d745b29eb74c5c362b"
    },
    {
      "source_id": "astro-doc-67458ae49efafc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49efafc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
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
      "source_id": "astro-doc-ed7b0d0a27542ceb",
      "record_id": "sources/mdx/reference/routing-reference",
      "concept_path": "concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md",
      "source_path": "sources/mdx/reference/routing-reference.mdx",
      "record_sha256": "a2c19f8c3c653f3d3e5457adbc855842ca1ad1f7cdcebafe0ccbda63852cecb8",
      "locator": {
        "end": 3825,
        "kind": "character-range",
        "start": 0
      },
      "text_sha256": "e961e628506f38198060853a90b9087c6a28a80bb868de6ae442cd664b5974f9"
    }
  ]
}
```

### Non-accepted developmental traces

Earlier append-only directories below are audit traces only. They are excluded from accepted metrics and responses.

| Run | Summary | Successes | Failures | Errors |
|---|---:|---:|---:|---:|
| 2026-07-16T09-54-34-794Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T11-12-42-534Z-compare | no | N/A | N/A | N/A |

## classical

Accepted run: `2026-07-16T11-55-25-736Z-compare` (`eval-tNp-2026-07-16T11:55:33`), benchmark `semantic-okf-astro-q040-classical-paired`. The metrics and responses in this section bind only that directory.

### Source bindings

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| promptfoo_results | 52347 | `56817c1e3d4acf92f0f9d7c603c2897d6efba240046fbe839f0751ec57ee0a2c` |
| promptfoo_config | 10805 | `cc31e751a280bedc43206230c2ef8eb6c4377a494233def7bbeb82188c9e92f1` |
| skill_arena_summary | 36085 | `c616b9f5ddeb18ab0bcec78b1cf2658d57758f2fcb5a164c579636e7cdd808a3` |
| authoritative_records | 3455749 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| source_combination | 438819 | `c09e952254e5f2a4673ec0864bb09be333d8e914a1d0c46284e33953296cb783` |

### Profile outcomes

| Profile | Role | Pass | Score | Assertions | Time | Strict JSON | Evidence valid |
|---|---|---:|---:|---:|---:|---:|---:|
| knowledge-only-control | passive-control | yes | 1 | 3/3 | 66976 ms | yes | 4/4 (pass) |
| classical-consult-treatment | treatment | yes | 1 | 3/3 | 125721 ms | yes | 3/3 (pass) |

### Exact parsed responses

The objects below are parsed directly from each raw response without changing any answer, claim, evidence identity, locator, or hash. Raw environment metadata and temporary workspace paths are excluded.

#### knowledge-only-control

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use static output by default and add an adapter for the deployment runtime, such as `@astrojs/node`. Configure the adapter in `astro.config.mjs`; the adapter is required for any on-demand route. Keep the account page and API endpoint request-time by exporting `const prerender = false` from each route. Leave every other route without an override, so it remains prerendered. The account page can use `Astro.cookies` to check, read, set, or delete cookies, while the API route should export a server endpoint handler such as `GET` and return a `Response`. In static mode, endpoints otherwise run at build time and become files; with `prerender = false`, this endpoint becomes a live server endpoint invoked per request and can use the fully usable request context. If server output later becomes the default, set `output: 'server'` alongside the adapter. Then routes are server-rendered on request by default, so the account page and API endpoint no longer need `prerender = false`; instead, add `export const prerender = true` only to routes that should remain static. This inverse design preserves the same mixed deployment while reversing the per-route opt-in direction.",
    "claims": [
      {
        "statement": "Static output is the appropriate default for a primarily static site; add a deployment-runtime adapter, and configure `@astrojs/node` when Node is the target.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "In static mode, export `prerender = false` on the account page and API route; routes without that override remain prerendered.",
        "evidence_indices": [
          0,
          3
        ]
      },
      {
        "statement": "An on-demand page can use `Astro.cookies` to check, get, set, and delete cookies.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "A static endpoint is built at build time, but an endpoint opted into SSR becomes a live request-time API route with a usable request context and `Response` return.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "With `output: 'server'`, routes are request-rendered by default; use `prerender = true` on individual routes that should remain static.",
        "evidence_indices": [
          0,
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
        "kind": "record"
      },
      "text_sha256": "64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002"
    },
    {
      "source_id": "astro-doc-8aa98ab02807f857",
      "record_id": "sources/mdx/guides/integrations-guide/node",
      "concept_path": "concepts/astro-doc-8aa98ab02807f857/sources-mdx-guides-integrations-guide-node-49b507ef1d.md",
      "source_path": "sources/mdx/guides/integrations-guide/node.mdx",
      "record_sha256": "5af13752fc7aea5fa9b4c3b2eea5cdce9ece6a6f4f92c5194683ead8cdd43b81",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "1dfbdfe58f8174d9d93bd899d96092fd663277e77079a5182dcebb0739c0aa9d"
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "b0dd4ef1c69101827474807a4544ebd1ea1fcd424e3735b7f6700f529b47c8f4"
    },
    {
      "source_id": "astro-doc-ed7b0d0a27542ceb",
      "record_id": "sources/mdx/reference/routing-reference",
      "concept_path": "concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md",
      "source_path": "sources/mdx/reference/routing-reference.mdx",
      "record_sha256": "a2c19f8c3c653f3d3e5457adbc855842ca1ad1f7cdcebafe0ccbda63852cecb8",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "e9c7951303b435bed3bb9d9964091ea4aef87db13643b05f6e4016f948ec46c1"
    }
  ]
}
```

#### classical-consult-treatment

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use static output as the default: configure `output: 'static'`, then add and configure a server adapter for the runtime hosting the on-demand routes. Export `prerender = false` from the cookie-aware account page and from the request-time API endpoint; every other route remains prerendered and is generated at build time. The account page can inspect and update request cookies through `Astro.cookies`, while the API endpoint should export its HTTP handler (such as `GET`) and return a `Response`. In static mode, custom endpoints otherwise execute at build time and become static files, so the endpoint’s `prerender = false` is essential for request-time behavior. If server output becomes the default, configure `output: 'server'` with the same kind of server adapter. That reverses the route defaults: pages and endpoints render on request unless they explicitly export `prerender = true`. Therefore, mark the account page and API route as server-rendered by default (explicit `false` is unnecessary), and add `prerender = true` to every route that should remain static. The adapter is required for on-demand rendering, whereas a purely static deployment would not need one; here it is needed because the two exceptional routes require server execution.",
    "claims": [
      {
        "statement": "Static output with a server adapter and per-route `prerender = false` preserves prerendering everywhere else while enabling the account page and API route at request time.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "An on-demand page or endpoint can check, set, get, and delete cookies through Astro’s cookie API.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "In static mode, custom endpoints run at build time and produce static files; opting out makes them live server endpoints called on request.",
        "evidence_indices": [
          1
        ]
      },
      {
        "statement": "With `output: 'server'`, routes render on demand by default, and individual static routes opt in with `prerender = true`.",
        "evidence_indices": [
          2
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
        "kind": "record"
      },
      "text_sha256": "64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002"
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "b0dd4ef1c69101827474807a4544ebd1ea1fcd424e3735b7f6700f529b47c8f4"
    },
    {
      "source_id": "astro-doc-ed7b0d0a27542ceb",
      "record_id": "sources/mdx/reference/routing-reference",
      "concept_path": "concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md",
      "source_path": "sources/mdx/reference/routing-reference.mdx",
      "record_sha256": "a2c19f8c3c653f3d3e5457adbc855842ca1ad1f7cdcebafe0ccbda63852cecb8",
      "locator": {
        "kind": "record"
      },
      "text_sha256": "e9c7951303b435bed3bb9d9964091ea4aef87db13643b05f6e4016f948ec46c1"
    }
  ]
}
```

### Non-accepted developmental traces

Earlier append-only directories below are audit traces only. They are excluded from accepted metrics and responses.

| Run | Summary | Successes | Failures | Errors |
|---|---:|---:|---:|---:|
| 2026-07-16T09-54-30-325Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T11-12-38-360Z-compare | no | N/A | N/A | N/A |

## adaptive

Accepted run: `2026-07-16T11-55-26-061Z-compare` (`eval-Fqk-2026-07-16T11:55:33`), benchmark `semantic-okf-astro-q040-adaptive-paired`. The metrics and responses in this section bind only that directory.

### Source bindings

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| promptfoo_results | 53843 | `384d50d1037942f7e831f596144ecc8151decf3557539d1490896a20320ba2a7` |
| promptfoo_config | 10795 | `4f98ab40a56d1e6d739b581436b08708f9a316722da47e90aaccee5b03fa68c7` |
| skill_arena_summary | 32094 | `d3969369eaaf30d40f0b384905fb23b78335b3f6db8348cad1985f63cba3b21c` |
| authoritative_records | 3455749 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| source_combination | 438819 | `c09e952254e5f2a4673ec0864bb09be333d8e914a1d0c46284e33953296cb783` |

### Profile outcomes

| Profile | Role | Pass | Score | Assertions | Time | Strict JSON | Evidence valid |
|---|---|---:|---:|---:|---:|---:|---:|
| knowledge-only-control | passive-control | no | 0.6666666666666666 | 2/3 | 131274 ms | yes | 0/1 (fail) |
| adaptive-consult-treatment | treatment | yes | 1 | 3/3 | 75037 ms | yes | 1/1 (pass) |

Authoritative evidence failures:

- `knowledge-only-control` evidence 0: locator is not an object

### Exact parsed responses

The objects below are parsed directly from each raw response without changing any answer, claim, evidence identity, locator, or hash. Raw environment metadata and temporary workspace paths are excluded.

#### knowledge-only-control

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use static output with a deployment adapter, then opt only the account page and API route into server rendering. In `astro.config.mjs`, keep `output: 'static'` and install the adapter matching the chosen runtime. In the account page, export `const prerender = false`; it is then generated per request and can read request-time cookies through `Astro.cookies` (or the request’s `cookie` header). Apply the same `prerender = false` export to the API endpoint so its handler runs on every request and returns a `Response`. All other pages and endpoints remain prerendered by default. For the inverse design, set `output: 'server'` after adding the adapter. That makes every page and route server-rendered by default, equivalent to opting out of prerendering everywhere. Add `export const prerender = true` to static exceptions such as otherwise-static pages or endpoints. Thus the two configurations differ only in their default: static output requires explicit opt-out for the account page and API route, whereas server output requires explicit opt-in for static exceptions. Cookies are available for on-demand pages and endpoints, not build-time prerendered routes.",
    "claims": [
      {
        "statement": "Keep `output: 'static'`, add a runtime-appropriate adapter, and export `prerender = false` on the account page and API endpoint.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "The endpoint remains request-time and returns a `Response`; other routes stay prerendered under static mode.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "An on-demand page or endpoint can check, set, get, and delete cookies, including through `Astro.cookies` or the request cookie header.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "With `output: 'server'`, routes are server-rendered by default; static exceptions export `prerender = true`.",
        "evidence_indices": [
          0
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
      "locator": "body",
      "text_sha256": "64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002"
    }
  ]
}
```

#### adaptive-consult-treatment

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use Astro’s default static output and add an adapter for the deployment runtime. Keep the site prerendered by default, then opt the account page and API endpoint into request-time rendering with `export const prerender = false`. The account page can read request cookies through `Astro.cookies` and personalize its response; the endpoint likewise executes on each request and returns a dynamic `Response`. All unmodified routes remain static build artifacts. The adapter is required for any on-demand page or route, and should match the hosting runtime (for example, Node, Netlify, Vercel, or Cloudflare). If the application later becomes predominantly dynamic, invert the design: configure `output: 'server'` after installing the adapter, making every route request-rendered by default. Then add `export const prerender = true` to the routes that should remain static, including ordinary pages or a static endpoint. Thus, static-default mode minimizes server execution and uses per-route opt-outs, while server-default mode uses per-route opt-ins for prerendering; neither changes the need for an adapter when server rendering is involved.",
    "claims": [
      {
        "statement": "Use static output by default; install an adapter matching the deployment runtime, and opt individual dynamic routes out of prerendering with `export const prerender = false`.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "The cookie-aware account page should be a non-prerendered page and can inspect or mutate request cookies through `Astro.cookies`.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "The request-time API route should also export `prerender = false`, so its handler runs on demand and can return dynamic responses.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "With `output: 'server'`, server rendering becomes the default; reverse the per-route setting by exporting `prerender = true` for routes or endpoints that should remain static.",
        "evidence_indices": [
          0
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
        "kind": "record"
      },
      "text_sha256": "64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002"
    }
  ]
}
```

### Non-accepted developmental traces

Earlier append-only directories below are audit traces only. They are excluded from accepted metrics and responses.

| Run | Summary | Successes | Failures | Errors |
|---|---:|---:|---:|---:|
| 2026-07-16T09-54-26-203Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T11-12-34-193Z-compare | no | N/A | N/A | N/A |

## entity-graph

Accepted run: `2026-07-16T11-59-19-741Z-compare` (`eval-Vea-2026-07-16T11:59:27`), benchmark `semantic-okf-astro-q040-entity-graph-paired`. The metrics and responses in this section bind only that directory.

### Source bindings

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| promptfoo_results | 60136 | `d2508b90912a3382a208484d3511d9c613e747c2039ae61c43f9f0dc03a1753c` |
| promptfoo_config | 10835 | `1c065123f140f716ae04fac79824322b115c5cabe581223b93152d1f8c0ee281` |
| skill_arena_summary | 41366 | `3a51570f4b0a0b2ca3a0d0f82e31d9b0f048b9409f4a74c60b0b3ca6149f26f1` |
| authoritative_records | 3455749 | `ef87105fe99c64683f21848810e82166ff54633095a28ab1cfa681984262cf0b` |
| source_combination | 438819 | `c09e952254e5f2a4673ec0864bb09be333d8e914a1d0c46284e33953296cb783` |

### Profile outcomes

| Profile | Role | Pass | Score | Assertions | Time | Strict JSON | Evidence valid |
|---|---|---:|---:|---:|---:|---:|---:|
| knowledge-only-control | passive-control | no | 0 | 0/3 | 97737 ms | no | 0/5 (fail) |
| entity-graph-consult-treatment | treatment | no | 0 | 0/3 | 92072 ms | no | 5/5 (pass) |

Authoritative evidence failures:

- `knowledge-only-control` evidence 0: locator is not an object
- `knowledge-only-control` evidence 1: locator is not an object
- `knowledge-only-control` evidence 2: locator is not an object
- `knowledge-only-control` evidence 3: locator is not an object
- `knowledge-only-control` evidence 4: locator is not an object

### Exact parsed responses

The objects below are parsed directly from each raw response without changing any answer, claim, evidence identity, locator, or hash. Raw environment metadata and temporary workspace paths are excluded.

#### knowledge-only-control

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use static output with a server adapter installed for the deployment runtime. Static output prerenders the site by default, while the account page and API endpoint each opt into request-time rendering with `export const prerender = false`; every other route remains prerendered. The account page can read the incoming cookie through `Astro.cookies.get()` because cookie utilities are available on routes rendered on demand. The endpoint likewise becomes a live server endpoint invoked per request, rather than a build-time static file. In configuration, use `output: 'static'` (the default) and configure the selected adapter integration, for example `adapter: yourAdapter()`. For the inverse design, switch to `output: 'server'` after adding the adapter. That makes all pages and routes server-rendered by default—the equivalent of opting out of prerendering everywhere—so mark only genuinely static pages and endpoints with `export const prerender = true`. Thus, static-default is the minimal-exception design for a primarily static site; server-default is the inverse, exception-based design for a primarily dynamic site.",
    "claims": [
      {
        "statement": "Configure static output and a server adapter; keep the account page and API endpoint request-time with `export const prerender = false`, leaving other routes prerendered.",
        "evidence_indices": [
          0
        ]
      },
      {
        "statement": "Read request-time account cookies with `Astro.cookies.get()`; cookie utilities apply to routes rendered on demand.",
        "evidence_indices": [
          1
        ]
      },
      {
        "statement": "In static mode an endpoint is build-time/static unless opted out; with SSR it is a live endpoint called on request.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "The inverse is `output: 'server'`, with `export const prerender = true` on individual pages or endpoints that should remain static.",
        "evidence_indices": [
          3,
          4
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
      "locator": "sources/mdx/guides/on-demand-rendering.mdx",
      "text_sha256": "3dd7fc6e1e1d620f6fee24117db763905540c6c076d6c8a4ed31c68213d203ef"
    },
    {
      "source_id": "astro-doc-7205d6a01925b590",
      "record_id": "sources/mdx/reference/api-reference",
      "concept_path": "concepts/astro-doc-7205d6a01925b590/sources-mdx-reference-api-reference-f22ce22db7.md",
      "source_path": "sources/mdx/reference/api-reference.mdx",
      "record_sha256": "305583e864a611bcfb7bbad75bcf344dc5ffca5708fee107c4324e44128789c9",
      "locator": "sources/mdx/reference/api-reference.mdx",
      "text_sha256": "4833820a69d0cb8d11ef92fed23b95f665c4b5af8b5c4c52ea090db24da662a8"
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": "sources/mdx/guides/endpoints.mdx",
      "text_sha256": "319d74e52bce67b1be5329aacafb24afcfbf692a90d89f85e17498db299303e7"
    },
    {
      "source_id": "astro-doc-3c50462cdbdb7a32",
      "record_id": "sources/mdx/reference/configuration-reference",
      "concept_path": "concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md",
      "source_path": "sources/mdx/reference/configuration-reference.mdx",
      "record_sha256": "09aeb7984eb813a284eb3ed10e6378a0ce05380a9e9c1e8985e3e812a2e823a0",
      "locator": "sources/mdx/reference/configuration-reference.mdx",
      "text_sha256": "b64f57f041c19d42527c9c79116508e053e74b9331fbc70c9c8379b56b8f1fd5"
    },
    {
      "source_id": "astro-doc-67458ae49afefc50",
      "record_id": "sources/mdx/guides/on-demand-rendering",
      "concept_path": "concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md",
      "source_path": "sources/mdx/guides/on-demand-rendering.mdx",
      "record_sha256": "daafa8646f81d0b02c913c1e27d289b5f7f1ccdf892d8e2308a6f4dd58761ee3",
      "locator": "sources/mdx/guides/on-demand-rendering.mdx",
      "text_sha256": "c304a91e7393600dd29498e02d67fe6bebad60fc322ebf5d2822fdce2d9cd21a"
    }
  ]
}
```

#### entity-graph-consult-treatment

```json
{
  "question_id": "q040",
  "answer": {
    "summary": "Use `output: 'static'` with a server adapter, for example `@astrojs/node`. Static output prerenders the site by default while permitting selected routes to opt into on-demand rendering. Configure both the cookie-aware account page and request-time API endpoint with `export const prerender = false`; every other route remains prerendered. The endpoint should export its HTTP handler, such as `GET` or `POST`, and return a `Response` (or redirect), because an on-demand endpoint is built when requested and can execute server code at runtime. In the account page, read or modify request cookies through `Astro.cookies`; in an API route, use the context’s `cookies` utility. These cookie operations require on-demand rendering, not prerendering. The adapter is required for any server-rendered routes regardless of output mode. In the inverse design, set `output: 'server'` with the same adapter. Then pages and endpoints are server-rendered on request by default, so the account page and API route need no `prerender = false`. Mark only routes intended to remain static with `export const prerender = true`; thus the formerly static remainder is explicitly opted into prerendering.",
    "claims": [
      {
        "statement": "Configure `output: 'static'` and install a server adapter such as `@astrojs/node`; the adapter is required for server-rendered routes.",
        "evidence_indices": [
          0,
          1
        ]
      },
      {
        "statement": "In static output, export `prerender = false` from the account page and API endpoint; all other routes retain the prerendered default.",
        "evidence_indices": [
          0,
          2
        ]
      },
      {
        "statement": "The request-time endpoint exports an HTTP method handler and can return a `Response`; on-demand endpoints are built when requested and can run server code.",
        "evidence_indices": [
          2
        ]
      },
      {
        "statement": "Use `Astro.cookies` in the page or the endpoint context’s `cookies` utility to check, get, set, or delete cookies; this is available for on-demand routes.",
        "evidence_indices": [
          2,
          3
        ]
      },
      {
        "statement": "With `output: 'server'`, routes are on-demand by default; export `prerender = true` only on routes that should remain static.",
        "evidence_indices": [
          4
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
        "end": 4387,
        "fragment": "record-body-736d392f1b0a13adcc8b79c7",
        "kind": "character-range",
        "start": 3087,
        "target": "record-body"
      },
      "text_sha256": "488b068c0313e2723a299149265fe5a21bf8aed116621292a3be70212010f523"
    },
    {
      "source_id": "astro-doc-8aa98ab02807f857",
      "record_id": "sources/mdx/guides/integrations-guide/node",
      "concept_path": "concepts/astro-doc-8aa98ab02807f857/sources-mdx-guides-integrations-guide-node-49b507ef1d.md",
      "source_path": "sources/mdx/guides/integrations-guide/node.mdx",
      "record_sha256": "5af13752fc7aea5fa9b4c3b2eea5cdce9ece6a6f4f92c5194683ead8cdd43b81",
      "locator": {
        "end": 1692,
        "fragment": "record-body-208aa3527e37f0126d16fe9e",
        "kind": "character-range",
        "start": 760,
        "target": "record-body"
      },
      "text_sha256": "fb5381b36bdacff3206460655c784a4493c3a305ed5a6ad50acfa431f792abf6"
    },
    {
      "source_id": "astro-doc-db7b41aee88b9016",
      "record_id": "sources/mdx/guides/endpoints",
      "concept_path": "concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md",
      "source_path": "sources/mdx/guides/endpoints.mdx",
      "record_sha256": "e1a30889b018d330ddcc2d29d2dcb60a2886d6b2361d0af7180c21459e5a6140",
      "locator": {
        "end": 7064,
        "fragment": "record-body-0a07d92f82ede703c4be5006",
        "kind": "character-range",
        "start": 4318,
        "target": "record-body"
      },
      "text_sha256": "96ea1faaa3762ebf4ba056862fd22f70e593b5d34b802a0bcf6d41fe1c65302f"
    },
    {
      "source_id": "astro-doc-7205d6a01925b590",
      "record_id": "sources/mdx/reference/api-reference",
      "concept_path": "concepts/astro-doc-7205d6a01925b590/sources-mdx-reference-api-reference-f22ce22db7.md",
      "source_path": "sources/mdx/reference/api-reference.mdx",
      "record_sha256": "305583e864a611bcfb7bbad75bcf344dc5ffca5708fee107c4324e44128789c9",
      "locator": {
        "end": 21729,
        "fragment": "record-body-1170c919c2ddc0dc49458003",
        "kind": "character-range",
        "start": 21521,
        "target": "record-body"
      },
      "text_sha256": "75799b2389c5f0df2ea5e81365e4d8ae6c654eac7d4a5aa1e9cc11b678ba91f3"
    },
    {
      "source_id": "astro-doc-ed7b0d0a27542ceb",
      "record_id": "sources/mdx/reference/routing-reference",
      "concept_path": "concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md",
      "source_path": "sources/mdx/reference/routing-reference.mdx",
      "record_sha256": "a2c19f8c3c653f3d3e5457adbc855842ca1ad1f7cdcebafe0ccbda63852cecb8",
      "locator": {
        "end": 2232,
        "fragment": "record-body-e9458942fa7b457dd24ee7ec",
        "kind": "character-range",
        "start": 1599,
        "target": "record-body"
      },
      "text_sha256": "cbbc4457158df5ea0d53bcac01e3dd6ea0647028194fd00f227bcc8ecd75e82d"
    }
  ]
}
```

### Non-accepted developmental traces

Earlier append-only directories below are audit traces only. They are excluded from accepted metrics and responses.

| Run | Summary | Successes | Failures | Errors |
|---|---:|---:|---:|---:|
| 2026-07-16T09-54-43-864Z-compare | no | N/A | N/A | N/A |
| 2026-07-16T11-12-51-141Z-compare | no | N/A | N/A | N/A |

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
