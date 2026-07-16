# Astro Hard-Question Answer Comparison

These are actual deterministic extractive answers produced from each alternative's own ranked, independently valid passages. Generation does not read ground truth and uses no language model or MCP. The mechanical completeness metrics indicate evidence sufficiency, not prose fluency or a semantic judge score.

| Family | Answer-best route | Retrieval-best route | Atomic evidence | Required documents | Evidence completeness | Negative evidence | Grounding | Evidence valid |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy | legacy_tfidf | legacy_tfidf | 66.0% | 74.2% | 68.0% | 75.0% | 100.0% | 100.0% |
| embeddings | hybrid | lexical | 0.0% | 84.2% | 7.0% | 0.0% | 100.0% | 100.0% |
| classical | bm25 | association | 66.0% | 77.5% | 68.0% | 75.0% | 100.0% | 100.0% |
| adaptive | bm25 | association | 66.0% | 77.5% | 68.0% | 75.0% | 100.0% | 100.0% |
| entity-graph | entity | entity | 0.0% | 78.3% | 0.0% | 0.0% | 100.0% | 100.0% |
| ensemble | quality | quality | 66.0% | 77.5% | 68.0% | 75.0% | 100.0% | 100.0% |

## One difficult question: `q040`

### legacy — `legacy_tfidf`

A primarily static Astro site needs one cookie-aware account page and one request-time API route, while all other routes should stay prerendered. Derive the output, adapter, per-route, endpoint, and request-feature configuration, including the inverse design if server output becomes the default.

[/en/reference/configuration-reference/] ```js
//astro.config.mjs
export default defineConfig({
	 site: "https://example.com",
	 output: "server", // required, with no prerendered pages
	 adapter: node({
	   mode: 'standalone',
	 }),
	 i18n: {
    defaultLocale: "en",
    locales: ["en", "fr", "pt-br", "es"],
    prefixDefaultLocale: false,
    domains: {
      fr: "https://fr.example.com",
      es: "https://example.es"
    }
  },
})
``` [/en/guides/upgrade-to/v5/] Astro v5.0 merges the `output: 'hybrid'` and `output: 'static'` configurations into one single configuration (now called `'static'`) that works the same way as the previous hybrid option. [/en/reference/integrations-reference/] ```ts
interface AstroIntegration {
  name: string;
  hooks: {
    'astro:config:setup'?: (options: {
      config: AstroConfig;
      command: 'dev' | 'build' | 'preview' | 'sync';
      isRestart: boolean;
      updateConfig: (newConfig: DeepPartial<AstroConfig>) => AstroConfig;
      addRenderer: (renderer: AstroRenderer) => void;
      addWatchFile: (path: URL | string) => void;
      addClientDirective: (directi… [/en/guides/upgrade-to/v6/] Astro 6.0 uses Vite's new Environment API for build configuration and dev server interactions. [/en/guides/routing/] In static builds, you can customize the file output format using the [`build.format`](/en/reference/configuration-reference/#buildformat) configuration option. [/en/guides/content-collections/] Point Astro to the location of your content, define your data shape, and you're good to go with a blog or similarly content-heavy, mostly static site in no time! [/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
---
// with `output: 'server'` configured
export const prerender = true
---
<!-- My static about page -->
<!-- All other pages are rendered on demand -->
``` [/en/guides/on-demand-rendering/] ```astro title="src/pages/about-my-app.astro" ins={2}
---
export const prerender = true
---
<html>
<!--
`output: 'server'` is configured, but this page is static! [/en/guides/upgrade-to/v1/] ```css ins=":where(.astro-XXXXXX)"
div:where(.astro-XXXXXX) { color: red; } /* 0-0-1 specificity */
```
The previous specificity increase made it hard to combine scoped styles in Astro with other CSS files or styling libraries (e.g. [/en/guides/caching/] You can then use [`Astro.cache`](/en/reference/api-reference/#cache) in your `.astro` pages (or `context.cache` for API routes and middleware) to control caching per request. [/en/guides/integrations-guide/netlify/] This adapter allows Astro to deploy your [on-demand rendered routes and features](/en/guides/on-demand-rendering/) to [Netlify](https://www.netlify.com/), including [server islands](/en/guides/server-islands/), [actions](/en/guides/actions/), and [sessions](/en/guides/sessions/). [/en/guides/upgrade-to/v7/] If your project already has a `src/fetch.ts` file used for other purposes, Astro will attempt to process it as an advanced routing configuration, which may cause unexpected errors.

Evidence:

- `/en/reference/configuration-reference/` — `concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md` — `{"kind":"record"}` — `c69c4ecedb148c9c163e730641e0711829bc1166ef65a559b6c6592542b7e865`
- `/en/guides/upgrade-to/v5/` — `concepts/astro-doc-60e7507194bf5ea2/sources-mdx-guides-upgrade-to-v5-b791353c5f.md` — `{"kind":"record"}` — `be03c6bc217eebb084efea3a0af8c7f8d989a90b086ca8d8429d3cec5340deb3`
- `/en/reference/integrations-reference/` — `concepts/astro-doc-16b8feb4d7e2595e/sources-mdx-reference-integrations-reference-c343421f83.md` — `{"kind":"record"}` — `7d237457030f9c5bdc67aa4fa49b8457cec441ad38c910e41b3bca37f4c4f23f`
- `/en/guides/upgrade-to/v6/` — `concepts/astro-doc-c21bb94164385610/sources-mdx-guides-upgrade-to-v6-35acdcfc48.md` — `{"kind":"record"}` — `bfe97fb05d86f17c6bf73432a7bdd964983c84307e878b70f6b61efd27f36f65`
- `/en/guides/routing/` — `concepts/astro-doc-edee4d931bfbee3d/sources-mdx-guides-routing-3c3bf608b2.md` — `{"kind":"record"}` — `7e04a2569f02611cd11bbfa9fb4aae7a208712f472244bedb7f9ef402f4e1782`
- `/en/guides/content-collections/` — `concepts/astro-doc-0716837c2e1c20bb/sources-mdx-guides-content-collections-8ab872cbaf.md` — `{"kind":"record"}` — `d42e89e3d834cbdd430dd19a3fd7604a32a60c35d047d7e9e251ed3e6667bafa`
- `/en/reference/routing-reference/` — `concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md` — `{"kind":"record"}` — `e9c7951303b435bed3bb9d9964091ea4aef87db13643b05f6e4016f948ec46c1`
- `/en/guides/on-demand-rendering/` — `concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md` — `{"kind":"record"}` — `64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002`
- `/en/guides/upgrade-to/v1/` — `concepts/astro-doc-9931b08868d6ceca/sources-mdx-guides-upgrade-to-v1-c789b0b038.md` — `{"kind":"record"}` — `b72acfe95f52fb7e11a471d0ab87b89051c2435e6c5c8db892ffe72d780cc045`
- `/en/guides/caching/` — `concepts/astro-doc-6cdc77179daee9ce/sources-mdx-guides-caching-cc4b0fd2c1.md` — `{"kind":"record"}` — `d26040d4197ad1f982298b70eccacb0b30dbebe1c009deaefb90873195e0c498`
- `/en/guides/integrations-guide/netlify/` — `concepts/astro-doc-56e26b0f8027b154/sources-mdx-guides-integrations-guide-netlify-92d57058bf.md` — `{"kind":"record"}` — `149623634f72741afa932a2cc8a3b106fc957a624dcc884c4595c748fcda063f`
- `/en/guides/upgrade-to/v7/` — `concepts/astro-doc-4e7ca58cc34c6aa0/sources-mdx-guides-upgrade-to-v7-90c3fab370.md` — `{"kind":"record"}` — `8300b24bfb0547ce76df70a41b4b3d146330941ffb1921390171ae990f26355b`

Mechanical score for this answer: atomic evidence 60.0%; required documents 66.7%; important negatives 100.0%.

### embeddings — `hybrid`

A primarily static Astro site needs one cookie-aware account page and one request-time API route, while all other routes should stay prerendered. Derive the output, adapter, per-route, endpoint, and request-feature configuration, including the inverse design if server output becomes the default.

[/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
---
// with `output: 'server'` configured
export const prerender = true
---
<!-- My static about page -->
<!-- All other pages are rendered on demand -->
``` [/en/guides/on-demand-rendering/] Each adapter allows Astro to output a script that runs your project on a specific **runtime**: the environment that runs code on the server to generate pages when they are requested (e.g. [/en/guides/content-collections/] If you are building a static website (Astro's default behavior) with build-time collections, use the [`getStaticPaths()`](/en/reference/routing-reference/#getstaticpaths) function to create multiple pages from a single page component (e.g. [/en/reference/integrations-reference/] function setPrerender() {
  return {
    name: 'set-prerender',
    hooks: {
      'astro:route:setup': ({ route }) => {
        if (route.component.endsWith('/blog/[slug].astro')) {
          route.prerender = true;
        }
      },
    },
  };
}
```

If the final value after running all the hooks is `undefined`, the route will fall back to a prerender default based on the [`output` option](/en/reference/configu… [/en/reference/configuration-reference/] When using SSR or with a static adapter in `output: static`
mode, status codes are supported. [/en/guides/routing/] Astro needs to know which route should be used to build the page. [/en/guides/upgrade-to/v5/] ### Deprecated: `routes` on `astro:build:done` hook (Integration API) [/en/reference/modules/astro-app/] The client IP address that will be made available as [`Astro.clientAddress`](/en/reference/api-reference/#clientaddress) in pages, and as `ctx.clientAddress` in API routes and middleware. [/en/guides/caching/] The following example caches all API routes with stale-while-revalidate, product pages with a 1-hour freshness window, and blog posts for 5 minutes: [/en/guides/integrations-guide/vercel/] If enabled, the adapter will save [static headers in the Vercel `vercel.json` file](https://vercel.com/docs/project-configuration#headers) when provided by Astro features, such as Content Security Policy. [/en/reference/modules/astro-fetch/] `FetchState` tracks the matched route, cookies, session providers, and other per-request data. [/en/guides/integrations-guide/netlify/] The Netlify adapter automatically configures skew protection for Astro features like actions, server islands, view transitions, and prefetch requests by injecting the current deploy ID into internal requests.

Evidence:

- `/en/reference/routing-reference/` — `concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md` — `{"end":3825,"kind":"character-range","start":0}` — `e961e628506f38198060853a90b9087c6a28a80bb868de6ae442cd664b5974f9`
- `/en/guides/on-demand-rendering/` — `concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md` — `{"end":1270,"kind":"character-range","start":615}` — `7a4c647183189cf496b750f94446b3fd3c84c6037eb5b4e4d1bc3feda6fe122d`
- `/en/guides/content-collections/` — `concepts/astro-doc-0716837c2e1c20bb/sources-mdx-guides-content-collections-8ab872cbaf.md` — `{"end":35326,"kind":"character-range","start":31382}` — `ced5e1ff26fdaffb59d68880564bc8e0ad6d94359e800b0669348dc8fd0af387`
- `/en/reference/integrations-reference/` — `concepts/astro-doc-16b8feb4d7e2595e/sources-mdx-reference-integrations-reference-c343421f83.md` — `{"end":19591,"kind":"character-range","start":17398}` — `f2f97526225cc991e817758f8a58baaeb23c335fa415590973c21d3553302d79`
- `/en/reference/configuration-reference/` — `concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md` — `{"end":5520,"kind":"character-range","start":0}` — `7c740a9b3a8fde3863da3df79a25441724454e15aff679a3185a3eed9e5d4979`
- `/en/guides/routing/` — `concepts/astro-doc-edee4d931bfbee3d/sources-mdx-guides-routing-3c3bf608b2.md` — `{"end":15618,"kind":"character-range","start":14427}` — `437d65f43cc3d0f231f6f51cd49162ee57c0b0c37589952ece6f3947fe9fcf1c`
- `/en/guides/upgrade-to/v5/` — `concepts/astro-doc-60e7507194bf5ea2/sources-mdx-guides-upgrade-to-v5-b791353c5f.md` — `{"end":15701,"kind":"character-range","start":12593}` — `a113b3257199971f4f903f8ae5b3f4986613ae12812c055d85f6f4f3d820795c`
- `/en/reference/modules/astro-app/` — `concepts/astro-doc-352138ab4dd13cf7/sources-mdx-reference-modules-astro-app-5784865079.md` — `{"end":11977,"kind":"character-range","start":8735}` — `f93248591230164c6944f421b809627d0e201d7fe3bb4d81dd33a932f7a16483`
- `/en/guides/caching/` — `concepts/astro-doc-6cdc77179daee9ce/sources-mdx-guides-caching-cc4b0fd2c1.md` — `{"end":11209,"kind":"character-range","start":9691}` — `bc702fcad4993a901e73a9949dd0a745e631f4433c50cdac4a36fc5634bf6699`
- `/en/guides/integrations-guide/vercel/` — `concepts/astro-doc-d6e95079dcee5dde/sources-mdx-guides-integrations-guide-vercel-35650af39a.md` — `{"end":13920,"kind":"character-range","start":8344}` — `6a7568b04a5d60bccc41403eabd23c7e8098b7621fce60c1c152e5b3e0371587`
- `/en/reference/modules/astro-fetch/` — `concepts/astro-doc-77c25adf2ec80269/sources-mdx-reference-modules-astro-fetch-7a85f816ed.md` — `{"end":1590,"kind":"character-range","start":0}` — `efd85fc36e9fde3ae68d5022412dcca4d4210cefd8a5e6af9fc7ab7b46a2d232`
- `/en/guides/integrations-guide/netlify/` — `concepts/astro-doc-56e26b0f8027b154/sources-mdx-guides-integrations-guide-netlify-92d57058bf.md` — `{"end":10812,"kind":"character-range","start":8480}` — `fa81efe19ee23822d3b7be6f7f02d0b8042b776db370cf3582ae10541430e072`

Mechanical score for this answer: atomic evidence 0.0%; required documents 66.7%; important negatives 0.0%.

### classical — `bm25`

A primarily static Astro site needs one cookie-aware account page and one request-time API route, while all other routes should stay prerendered. Derive the output, adapter, per-route, endpoint, and request-feature configuration, including the inverse design if server output becomes the default.

[/en/guides/on-demand-rendering/] ```astro title="src/pages/about-my-app.astro" ins={2}
---
export const prerender = true
---
<html>
<!--
`output: 'server'` is configured, but this page is static! [/en/guides/caching/] You can then use [`Astro.cache`](/en/reference/api-reference/#cache) in your `.astro` pages (or `context.cache` for API routes and middleware) to control caching per request. [/en/guides/routing/] In static builds, you can customize the file output format using the [`build.format`](/en/reference/configuration-reference/#buildformat) configuration option. [/en/reference/configuration-reference/] ```js
//astro.config.mjs
export default defineConfig({
	 site: "https://example.com",
	 output: "server", // required, with no prerendered pages
	 adapter: node({
	   mode: 'standalone',
	 }),
	 i18n: {
    defaultLocale: "en",
    locales: ["en", "fr", "pt-br", "es"],
    prefixDefaultLocale: false,
    domains: {
      fr: "https://fr.example.com",
      es: "https://example.es"
    }
  },
})
``` [/en/reference/adapter-reference/] The following example creates an adapter with a server entrypoint and stable support for Astro static output: [/en/guides/upgrade-to/v5/] Astro v5.0 merges the `output: 'hybrid'` and `output: 'static'` configurations into one single configuration (now called `'static'`) that works the same way as the previous hybrid option. [/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
---
// with `output: 'server'` configured
export const prerender = true
---
<!-- My static about page -->
<!-- All other pages are rendered on demand -->
``` [/en/guides/integrations-guide/vercel/] This adapter allows Astro to deploy your [on-demand rendered routes and features](/en/guides/on-demand-rendering/) to [Vercel](https://www.vercel.com/), including [server islands](/en/guides/server-islands/), [actions](/en/guides/actions/), and [sessions](/en/guides/sessions/). [/en/reference/modules/astro-app/] This module helps adapter authors [build a server entrypoint](/en/reference/adapter-reference/#building-a-server-entrypoint) while supporting pages rendered in development mode or that have been prebuilt through `astro build`. [/en/reference/integrations-reference/] ```ts
interface AstroIntegration {
  name: string;
  hooks: {
    'astro:config:setup'?: (options: {
      config: AstroConfig;
      command: 'dev' | 'build' | 'preview' | 'sync';
      isRestart: boolean;
      updateConfig: (newConfig: DeepPartial<AstroConfig>) => AstroConfig;
      addRenderer: (renderer: AstroRenderer) => void;
      addWatchFile: (path: URL | string) => void;
      addClientDirective: (directi… [/en/reference/api-reference/] Use the `context` object in [endpoint functions](/en/guides/endpoints/) to serve static or live server endpoints and in [middleware](/en/guides/middleware/) to inject behavior when a page or endpoint is about to be rendered. [/en/guides/internationalization/] ```js title="astro.config.mjs" {3-7} ins={14-17}
import { defineConfig } from "astro/config"
export default defineConfig({
  site: "https://example.com",
  output: "server", // required, with no prerendered pages
  adapter: node({
    mode: 'standalone',
  }),
  i18n: {
    locales: ["es", "en", "fr", "ja"],
    defaultLocale: "en",
    routing: {
      prefixDefaultLocale: false
    },
    domains: {
      fr: "htt…

Evidence:

- `/en/guides/on-demand-rendering/` — `concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md` — `{"kind":"record"}` — `64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002`
- `/en/guides/caching/` — `concepts/astro-doc-6cdc77179daee9ce/sources-mdx-guides-caching-cc4b0fd2c1.md` — `{"kind":"record"}` — `d26040d4197ad1f982298b70eccacb0b30dbebe1c009deaefb90873195e0c498`
- `/en/guides/routing/` — `concepts/astro-doc-edee4d931bfbee3d/sources-mdx-guides-routing-3c3bf608b2.md` — `{"kind":"record"}` — `7e04a2569f02611cd11bbfa9fb4aae7a208712f472244bedb7f9ef402f4e1782`
- `/en/reference/configuration-reference/` — `concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md` — `{"kind":"record"}` — `c69c4ecedb148c9c163e730641e0711829bc1166ef65a559b6c6592542b7e865`
- `/en/reference/adapter-reference/` — `concepts/astro-doc-1269cfbb4f20a502/sources-mdx-reference-adapter-reference-0c0f5e5ae3.md` — `{"kind":"record"}` — `f6c8dc78c4a7d6352f891d6715265031f1268f842760b7d14e7e4e57ddf9562a`
- `/en/guides/upgrade-to/v5/` — `concepts/astro-doc-60e7507194bf5ea2/sources-mdx-guides-upgrade-to-v5-b791353c5f.md` — `{"kind":"record"}` — `be03c6bc217eebb084efea3a0af8c7f8d989a90b086ca8d8429d3cec5340deb3`
- `/en/reference/routing-reference/` — `concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md` — `{"kind":"record"}` — `e9c7951303b435bed3bb9d9964091ea4aef87db13643b05f6e4016f948ec46c1`
- `/en/guides/integrations-guide/vercel/` — `concepts/astro-doc-d6e95079dcee5dde/sources-mdx-guides-integrations-guide-vercel-35650af39a.md` — `{"kind":"record"}` — `40ee45e535106610af03b05e579d167fe2cec8b137ea42963191f8939cceccbd`
- `/en/reference/modules/astro-app/` — `concepts/astro-doc-352138ab4dd13cf7/sources-mdx-reference-modules-astro-app-5784865079.md` — `{"kind":"record"}` — `fb7da0f5d347794da299f94aaf92f7594d4ef55ee1ac6e407f9dce253056c741`
- `/en/reference/integrations-reference/` — `concepts/astro-doc-16b8feb4d7e2595e/sources-mdx-reference-integrations-reference-c343421f83.md` — `{"kind":"record"}` — `7d237457030f9c5bdc67aa4fa49b8457cec441ad38c910e41b3bca37f4c4f23f`
- `/en/reference/api-reference/` — `concepts/astro-doc-7205d6a01925b590/sources-mdx-reference-api-reference-f22ce22db7.md` — `{"kind":"record"}` — `0745b1e862cdce942f8bb257bf1a8791398413680bf7f03135df84d137e9c557`
- `/en/guides/internationalization/` — `concepts/astro-doc-7764e5b951c83eae/sources-mdx-guides-internationalization-09f9134f05.md` — `{"kind":"record"}` — `d1ab16c52c2b1eea0d87c2ce47c319af9115dd5d396f9eb48122d50ff510e774`

Mechanical score for this answer: atomic evidence 60.0%; required documents 66.7%; important negatives 100.0%.

### adaptive — `bm25`

A primarily static Astro site needs one cookie-aware account page and one request-time API route, while all other routes should stay prerendered. Derive the output, adapter, per-route, endpoint, and request-feature configuration, including the inverse design if server output becomes the default.

[/en/guides/on-demand-rendering/] ```astro title="src/pages/about-my-app.astro" ins={2}
---
export const prerender = true
---
<html>
<!--
`output: 'server'` is configured, but this page is static! [/en/guides/caching/] You can then use [`Astro.cache`](/en/reference/api-reference/#cache) in your `.astro` pages (or `context.cache` for API routes and middleware) to control caching per request. [/en/guides/routing/] In static builds, you can customize the file output format using the [`build.format`](/en/reference/configuration-reference/#buildformat) configuration option. [/en/reference/configuration-reference/] ```js
//astro.config.mjs
export default defineConfig({
	 site: "https://example.com",
	 output: "server", // required, with no prerendered pages
	 adapter: node({
	   mode: 'standalone',
	 }),
	 i18n: {
    defaultLocale: "en",
    locales: ["en", "fr", "pt-br", "es"],
    prefixDefaultLocale: false,
    domains: {
      fr: "https://fr.example.com",
      es: "https://example.es"
    }
  },
})
``` [/en/reference/adapter-reference/] The following example creates an adapter with a server entrypoint and stable support for Astro static output: [/en/guides/upgrade-to/v5/] Astro v5.0 merges the `output: 'hybrid'` and `output: 'static'` configurations into one single configuration (now called `'static'`) that works the same way as the previous hybrid option. [/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
---
// with `output: 'server'` configured
export const prerender = true
---
<!-- My static about page -->
<!-- All other pages are rendered on demand -->
``` [/en/guides/integrations-guide/vercel/] This adapter allows Astro to deploy your [on-demand rendered routes and features](/en/guides/on-demand-rendering/) to [Vercel](https://www.vercel.com/), including [server islands](/en/guides/server-islands/), [actions](/en/guides/actions/), and [sessions](/en/guides/sessions/). [/en/reference/modules/astro-app/] This module helps adapter authors [build a server entrypoint](/en/reference/adapter-reference/#building-a-server-entrypoint) while supporting pages rendered in development mode or that have been prebuilt through `astro build`. [/en/reference/integrations-reference/] ```ts
interface AstroIntegration {
  name: string;
  hooks: {
    'astro:config:setup'?: (options: {
      config: AstroConfig;
      command: 'dev' | 'build' | 'preview' | 'sync';
      isRestart: boolean;
      updateConfig: (newConfig: DeepPartial<AstroConfig>) => AstroConfig;
      addRenderer: (renderer: AstroRenderer) => void;
      addWatchFile: (path: URL | string) => void;
      addClientDirective: (directi… [/en/reference/api-reference/] Use the `context` object in [endpoint functions](/en/guides/endpoints/) to serve static or live server endpoints and in [middleware](/en/guides/middleware/) to inject behavior when a page or endpoint is about to be rendered. [/en/guides/internationalization/] ```js title="astro.config.mjs" {3-7} ins={14-17}
import { defineConfig } from "astro/config"
export default defineConfig({
  site: "https://example.com",
  output: "server", // required, with no prerendered pages
  adapter: node({
    mode: 'standalone',
  }),
  i18n: {
    locales: ["es", "en", "fr", "ja"],
    defaultLocale: "en",
    routing: {
      prefixDefaultLocale: false
    },
    domains: {
      fr: "htt…

Evidence:

- `/en/guides/on-demand-rendering/` — `concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md` — `{"kind":"record"}` — `64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002`
- `/en/guides/caching/` — `concepts/astro-doc-6cdc77179daee9ce/sources-mdx-guides-caching-cc4b0fd2c1.md` — `{"kind":"record"}` — `d26040d4197ad1f982298b70eccacb0b30dbebe1c009deaefb90873195e0c498`
- `/en/guides/routing/` — `concepts/astro-doc-edee4d931bfbee3d/sources-mdx-guides-routing-3c3bf608b2.md` — `{"kind":"record"}` — `7e04a2569f02611cd11bbfa9fb4aae7a208712f472244bedb7f9ef402f4e1782`
- `/en/reference/configuration-reference/` — `concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md` — `{"kind":"record"}` — `c69c4ecedb148c9c163e730641e0711829bc1166ef65a559b6c6592542b7e865`
- `/en/reference/adapter-reference/` — `concepts/astro-doc-1269cfbb4f20a502/sources-mdx-reference-adapter-reference-0c0f5e5ae3.md` — `{"kind":"record"}` — `f6c8dc78c4a7d6352f891d6715265031f1268f842760b7d14e7e4e57ddf9562a`
- `/en/guides/upgrade-to/v5/` — `concepts/astro-doc-60e7507194bf5ea2/sources-mdx-guides-upgrade-to-v5-b791353c5f.md` — `{"kind":"record"}` — `be03c6bc217eebb084efea3a0af8c7f8d989a90b086ca8d8429d3cec5340deb3`
- `/en/reference/routing-reference/` — `concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md` — `{"kind":"record"}` — `e9c7951303b435bed3bb9d9964091ea4aef87db13643b05f6e4016f948ec46c1`
- `/en/guides/integrations-guide/vercel/` — `concepts/astro-doc-d6e95079dcee5dde/sources-mdx-guides-integrations-guide-vercel-35650af39a.md` — `{"kind":"record"}` — `40ee45e535106610af03b05e579d167fe2cec8b137ea42963191f8939cceccbd`
- `/en/reference/modules/astro-app/` — `concepts/astro-doc-352138ab4dd13cf7/sources-mdx-reference-modules-astro-app-5784865079.md` — `{"kind":"record"}` — `fb7da0f5d347794da299f94aaf92f7594d4ef55ee1ac6e407f9dce253056c741`
- `/en/reference/integrations-reference/` — `concepts/astro-doc-16b8feb4d7e2595e/sources-mdx-reference-integrations-reference-c343421f83.md` — `{"kind":"record"}` — `7d237457030f9c5bdc67aa4fa49b8457cec441ad38c910e41b3bca37f4c4f23f`
- `/en/reference/api-reference/` — `concepts/astro-doc-7205d6a01925b590/sources-mdx-reference-api-reference-f22ce22db7.md` — `{"kind":"record"}` — `0745b1e862cdce942f8bb257bf1a8791398413680bf7f03135df84d137e9c557`
- `/en/guides/internationalization/` — `concepts/astro-doc-7764e5b951c83eae/sources-mdx-guides-internationalization-09f9134f05.md` — `{"kind":"record"}` — `d1ab16c52c2b1eea0d87c2ce47c319af9115dd5d396f9eb48122d50ff510e774`

Mechanical score for this answer: atomic evidence 60.0%; required documents 66.7%; important negatives 100.0%.

### entity-graph — `entity`

A primarily static Astro site needs one cookie-aware account page and one request-time API route, while all other routes should stay prerendered. Derive the output, adapter, per-route, endpoint, and request-feature configuration, including the inverse design if server output becomes the default.

[/en/guides/on-demand-rendering/] ```astro title="src/pages/about-my-app.astro" ins={2}
---
export const prerender = true
---
<html>
<!--
`output: 'server'` is configured, but this page is static! [/en/reference/error-reference/] - [**AdapterSupportOutputMismatch**](/en/reference/errors/adapter-support-output-mismatch/)<br/>Adapter does not support server output. [/en/reference/configuration-reference/] ```js
//astro.config.mjs
export default defineConfig({
	 site: "https://example.com",
	 output: "server", // required, with no prerendered pages
	 adapter: node({
	   mode: 'standalone',
	 }),
	 i18n: {
    defaultLocale: "en",
    locales: ["en", "fr", "pt-br", "es"],
    prefixDefaultLocale: false,
    domains: {
      fr: "https://fr.example.com",
      es: "https://example.es"
    }
  },
})
``` [/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
---
// with `output: 'server'` configured
export const prerender = true
---
<!-- My static about page -->
<!-- All other pages are rendered on demand -->
``` [/en/guides/routing/] When running `astro build`, Astro will output HTML files with the [meta refresh](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#examples) tag by default. [/en/guides/content-collections/] You can [generate page routes](#generating-routes-from-content) from your live collection entries on demand, fetching your data fresh at runtime upon each request without needing a rebuild of your site like [build-time collections](#defining-build-time-content-collections) do. [/en/guides/upgrade-to/v5/] Astro v5.0 merges the `output: 'hybrid'` and `output: 'static'` configurations into one single configuration (now called `'static'`) that works the same way as the previous hybrid option. [/en/reference/adapter-reference/] 'astro:build:ssr': ({ middlewareEntryPoint }) => {
        // remember to check if this property exits, it will be `undefined` if the adapter doesn't opt in to the feature
        if (middlewareEntryPoint) {
          createEdgeMiddleware(middlewareEntryPoint)
        }
      }
    },
  };
} [/en/guides/endpoints/] ## Server Endpoints (API Routes) [/en/reference/programmatic-reference/] mergeConfig(
  {
    output: "static",
    site: "https://example.com",
    integrations: [partytown()],
    server: ({command}) => ({
      port: command === "dev" ? [/en/guides/deploy/gitlab/] This setting instructs Astro to put the static build output in a folder called `public`, which is the folder required by GitLab Pages for exposed files. [/en/guides/deploy/github/] Astro maintains an [official Astro GitHub Action to deploy your project to a GitHub Pages](https://github.com/withastro/action) with very little configuration and is the recommended way to deploy to GitHub Pages.

Evidence:

- `/en/guides/on-demand-rendering/` — `concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md` — `{"end":5891,"fragment":"record-body-9f0a49f62846ce43e60cedc2","kind":"character-range","start":4388,"target":"record-body"}` — `5824627aa1d60f925fbed752a048308e9bed56dfc28f0717b1e94c2026ebe0bd`
- `/en/reference/error-reference/` — `concepts/astro-doc-d6bee6279a720694/sources-mdx-reference-error-reference-fbe90a9c1a.md` — `{"end":4297,"fragment":"record-body-bdfe14f718efba0e13503f42","kind":"character-range","start":310,"target":"record-body"}` — `cc6afc2308abda0e7c2a3009549369e4043f36f46abd334f3b1ee0fc92a9e609`
- `/en/reference/configuration-reference/` — `concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md` — `{"end":67441,"fragment":"record-body-57a0fd6d75a36f42ed05a0b3","kind":"character-range","start":66015,"target":"record-body"}` — `f39f03ee292d3ddafbb99691d4136a0e09d7eee233d07404ead4b6dd5cb43bf0`
- `/en/reference/routing-reference/` — `concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md` — `{"end":2232,"fragment":"record-body-e9458942fa7b457dd24ee7ec","kind":"character-range","start":1599,"target":"record-body"}` — `cbbc4457158df5ea0d53bcac01e3dd6ea0647028194fd00f227bcc8ecd75e82d`
- `/en/guides/routing/` — `concepts/astro-doc-edee4d931bfbee3d/sources-mdx-guides-routing-3c3bf608b2.md` — `{"end":10987,"fragment":"record-body-ace4c74e6c2b8b231ffdf5bd","kind":"character-range","start":8987,"target":"record-body"}` — `d46a29df01278ad23beb7064dd1ce2d1861c6a07164ea575265b04545c6c4e50`
- `/en/guides/content-collections/` — `concepts/astro-doc-0716837c2e1c20bb/sources-mdx-guides-content-collections-8ab872cbaf.md` — `{"end":38113,"fragment":"record-body-031b20efc59caa38c3061911","kind":"character-range","start":35144,"target":"record-body"}` — `28f73750d6fcf0c13c5555ba19413c3c589f4c42e9f849eb40a7f19c1268c9c6`
- `/en/guides/upgrade-to/v5/` — `concepts/astro-doc-60e7507194bf5ea2/sources-mdx-guides-upgrade-to-v5-b791353c5f.md` — `{"end":17719,"fragment":"record-body-bc67991829772b4b3076c87f","kind":"character-range","start":16843,"target":"record-body"}` — `79ac356b0f5edf4963abf3c712f92e0d2f83ae113bc9f004f8755c72d40e9f3c`
- `/en/reference/adapter-reference/` — `concepts/astro-doc-1269cfbb4f20a502/sources-mdx-reference-adapter-reference-0c0f5e5ae3.md` — `{"end":23856,"fragment":"record-body-ec03ca0aaf4ff4481f8fcfdf","kind":"character-range","start":21640,"target":"record-body"}` — `9c052a1b1ec65606e55719c1db595a74f7516619897c479853d29473dcc190b8`
- `/en/guides/endpoints/` — `concepts/astro-doc-db7b41aee88b9016/sources-mdx-guides-endpoints-526d039df3.md` — `{"end":7064,"fragment":"record-body-0a07d92f82ede703c4be5006","kind":"character-range","start":4318,"target":"record-body"}` — `96ea1faaa3762ebf4ba056862fd22f70e593b5d34b802a0bcf6d41fe1c65302f`
- `/en/reference/programmatic-reference/` — `concepts/astro-doc-2f72773430e2f30e/sources-mdx-reference-programmatic-reference-21abf1612e.md` — `{"end":6912,"fragment":"record-body-66b2472871003ddcd220261c","kind":"character-range","start":5163,"target":"record-body"}` — `1a05dba96353daf925ccfbc1c11cde8f9d8bdc46c92bb5dfc9c35a1a463c2c65`
- `/en/guides/deploy/gitlab/` — `concepts/astro-doc-67534e0b3afac4d4/sources-mdx-guides-deploy-gitlab-17c3986a63.md` — `{"end":4281,"fragment":"record-body-221a079485b82bb1c84fd529","kind":"character-range","start":364,"target":"record-body"}` — `df80608ccd316c7437506b092dac3edf0f78f8cb6f724007fd28a77ea6ca71f6`
- `/en/guides/deploy/github/` — `concepts/astro-doc-663ea81d7c2a1f67/sources-mdx-guides-deploy-github-2d84ac555c.md` — `{"end":4074,"fragment":"record-body-40426f88fe862e1e3ecab9db","kind":"character-range","start":280,"target":"record-body"}` — `f31719ea070c07e7314393461c369129d6933942f2f78d04f7bf6050f5e9fa31`

Mechanical score for this answer: atomic evidence 0.0%; required documents 100.0%; important negatives 0.0%.

### ensemble — `quality`

A primarily static Astro site needs one cookie-aware account page and one request-time API route, while all other routes should stay prerendered. Derive the output, adapter, per-route, endpoint, and request-feature configuration, including the inverse design if server output becomes the default.

[/en/guides/on-demand-rendering/] ```astro title="src/pages/about-my-app.astro" ins={2}
---
export const prerender = true
---
<html>
<!--
`output: 'server'` is configured, but this page is static! [/en/guides/routing/] In static builds, you can customize the file output format using the [`build.format`](/en/reference/configuration-reference/#buildformat) configuration option. [/en/guides/caching/] You can then use [`Astro.cache`](/en/reference/api-reference/#cache) in your `.astro` pages (or `context.cache` for API routes and middleware) to control caching per request. [/en/reference/configuration-reference/] ```js
//astro.config.mjs
export default defineConfig({
	 site: "https://example.com",
	 output: "server", // required, with no prerendered pages
	 adapter: node({
	   mode: 'standalone',
	 }),
	 i18n: {
    defaultLocale: "en",
    locales: ["en", "fr", "pt-br", "es"],
    prefixDefaultLocale: false,
    domains: {
      fr: "https://fr.example.com",
      es: "https://example.es"
    }
  },
})
``` [/en/reference/adapter-reference/] The following example creates an adapter with a server entrypoint and stable support for Astro static output: [/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
---
// with `output: 'server'` configured
export const prerender = true
---
<!-- My static about page -->
<!-- All other pages are rendered on demand -->
``` [/en/guides/upgrade-to/v5/] Astro v5.0 merges the `output: 'hybrid'` and `output: 'static'` configurations into one single configuration (now called `'static'`) that works the same way as the previous hybrid option. [/en/guides/integrations-guide/vercel/] This adapter allows Astro to deploy your [on-demand rendered routes and features](/en/guides/on-demand-rendering/) to [Vercel](https://www.vercel.com/), including [server islands](/en/guides/server-islands/), [actions](/en/guides/actions/), and [sessions](/en/guides/sessions/). [/en/reference/integrations-reference/] ```ts
interface AstroIntegration {
  name: string;
  hooks: {
    'astro:config:setup'?: (options: {
      config: AstroConfig;
      command: 'dev' | 'build' | 'preview' | 'sync';
      isRestart: boolean;
      updateConfig: (newConfig: DeepPartial<AstroConfig>) => AstroConfig;
      addRenderer: (renderer: AstroRenderer) => void;
      addWatchFile: (path: URL | string) => void;
      addClientDirective: (directi… [/en/reference/modules/astro-app/] This module helps adapter authors [build a server entrypoint](/en/reference/adapter-reference/#building-a-server-entrypoint) while supporting pages rendered in development mode or that have been prebuilt through `astro build`. [/en/reference/api-reference/] Use the `context` object in [endpoint functions](/en/guides/endpoints/) to serve static or live server endpoints and in [middleware](/en/guides/middleware/) to inject behavior when a page or endpoint is about to be rendered. [/en/guides/internationalization/] ```js title="astro.config.mjs" {3-7} ins={14-17}
import { defineConfig } from "astro/config"
export default defineConfig({
  site: "https://example.com",
  output: "server", // required, with no prerendered pages
  adapter: node({
    mode: 'standalone',
  }),
  i18n: {
    locales: ["es", "en", "fr", "ja"],
    defaultLocale: "en",
    routing: {
      prefixDefaultLocale: false
    },
    domains: {
      fr: "htt…

Evidence:

- `/en/guides/on-demand-rendering/` — `concepts/astro-doc-67458ae49afefc50/sources-mdx-guides-on-demand-rendering-821fb8d2c7.md` — `{"end":11578,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `64f3baf78b0b04488a1f7ae89d042371fd56028ecf5444776753cae8b0128002`
- `/en/guides/routing/` — `concepts/astro-doc-edee4d931bfbee3d/sources-mdx-guides-routing-3c3bf608b2.md` — `{"end":29204,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `7e04a2569f02611cd11bbfa9fb4aae7a208712f472244bedb7f9ef402f4e1782`
- `/en/guides/caching/` — `concepts/astro-doc-6cdc77179daee9ce/sources-mdx-guides-caching-cc4b0fd2c1.md` — `{"end":11209,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `d26040d4197ad1f982298b70eccacb0b30dbebe1c009deaefb90873195e0c498`
- `/en/reference/configuration-reference/` — `concepts/astro-doc-3c50462cdbdb7a32/sources-mdx-reference-configuration-reference-b734a501a7.md` — `{"end":77315,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `c69c4ecedb148c9c163e730641e0711829bc1166ef65a559b6c6592542b7e865`
- `/en/reference/adapter-reference/` — `concepts/astro-doc-1269cfbb4f20a502/sources-mdx-reference-adapter-reference-0c0f5e5ae3.md` — `{"end":36781,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `f6c8dc78c4a7d6352f891d6715265031f1268f842760b7d14e7e4e57ddf9562a`
- `/en/reference/routing-reference/` — `concepts/astro-doc-ed7b0d0a27542ceb/sources-mdx-reference-routing-reference-315c04b052.md` — `{"end":12656,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `e9c7951303b435bed3bb9d9964091ea4aef87db13643b05f6e4016f948ec46c1`
- `/en/guides/upgrade-to/v5/` — `concepts/astro-doc-60e7507194bf5ea2/sources-mdx-guides-upgrade-to-v5-b791353c5f.md` — `{"end":58389,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `be03c6bc217eebb084efea3a0af8c7f8d989a90b086ca8d8429d3cec5340deb3`
- `/en/guides/integrations-guide/vercel/` — `concepts/astro-doc-d6e95079dcee5dde/sources-mdx-guides-integrations-guide-vercel-35650af39a.md` — `{"end":17288,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `40ee45e535106610af03b05e579d167fe2cec8b137ea42963191f8939cceccbd`
- `/en/reference/integrations-reference/` — `concepts/astro-doc-16b8feb4d7e2595e/sources-mdx-reference-integrations-reference-c343421f83.md` — `{"end":74824,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `7d237457030f9c5bdc67aa4fa49b8457cec441ad38c910e41b3bca37f4c4f23f`
- `/en/reference/modules/astro-app/` — `concepts/astro-doc-352138ab4dd13cf7/sources-mdx-reference-modules-astro-app-5784865079.md` — `{"end":13156,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `fb7da0f5d347794da299f94aaf92f7594d4ef55ee1ac6e407f9dce253056c741`
- `/en/reference/api-reference/` — `concepts/astro-doc-7205d6a01925b590/sources-mdx-reference-api-reference-f22ce22db7.md` — `{"end":39096,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `0745b1e862cdce942f8bb257bf1a8791398413680bf7f03135df84d137e9c557`
- `/en/guides/internationalization/` — `concepts/astro-doc-7764e5b951c83eae/sources-mdx-guides-internationalization-09f9134f05.md` — `{"end":17749,"fragment":null,"kind":"character-range","start":0,"target":"record-body"}` — `d1ab16c52c2b1eea0d87c2ce47c319af9115dd5d396f9eb48122d50ff510e774`

Mechanical score for this answer: atomic evidence 60.0%; required documents 66.7%; important negatives 100.0%.
