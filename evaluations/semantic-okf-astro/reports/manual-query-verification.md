# Astro q040 Manual Query Verification

Question: A primarily static Astro site needs one cookie-aware account page and one request-time API route, while all other routes should stay prerendered. Derive the output, adapter, per-route, endpoint, and request-feature configuration, including the inverse design if server output becomes the default.

Each selected route was executed twice against the same published bundle. Ranking and evidence signatures cover the complete route result, up to the 100-hit candidate-pool limit. Every retained locator and text hash was independently checked against the authoritative ledger, and the bundle tree was hashed before and after consultation.

| Family | Route | Returned | Valid evidence | Rank deterministic | Evidence deterministic | Bundle unchanged | Required-doc R@10 |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy | legacy_tfidf | 100 | 100/100 | yes | yes | yes | 66.7% |
| embeddings | lexical | 100 | 100/100 | yes | yes | yes | 100.0% |
| classical | association | 100 | 100/100 | yes | yes | yes | 66.7% |
| adaptive | association | 100 | 100/100 | yes | yes | yes | 66.7% |
| entity-graph | entity | 72 | 72/72 | yes | yes | yes | 100.0% |
| ensemble | quality | 100 | 100/100 | yes | yes | yes | 66.7% |

The extracts below are deterministic, ground-truth-blind evidence packs. They demonstrate what each route exposes; they are not a semantic correctness judgment and may be incomplete even when every citation is valid.

## legacy / legacy_tfidf

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
    prefi… [/en/guides/upgrade-to/v5/] Astro v5.0 merges the `output: 'hybrid'` and `output: 'static'` configurations into one single configuration (now called `'static'`) that works the same way as the previous hybrid option. [/en/reference/integrations-reference/] ```ts
interface AstroIntegration {
  name: string;
  hooks: {
    'astro:config:setup'?: (options: {
      config: AstroConfig;
      command: 'dev' | 'build' | 'preview' | 'sync';
      isRestart: boolean;
      updateConfig: (newConfig: DeepPartial<AstroConfig>) => AstroConfig… [/en/guides/upgrade-to/v6/] Astro 6.0 uses Vite's new Environment API for build configuration and dev server interactions. [/en/guides/routing/] In static builds, you can customize the file output format using the [`build.format`](/en/reference/configuration-reference/#buildformat) configuration option.

## embeddings / lexical

[/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
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
`output: 'server'` is configured, but this page is static! [/en/guides/upgrade-to/v5/] Astro v5.0 merges the `output: 'hybrid'` and `output: 'static'` configurations into one single configuration (now called `'static'`) that works the same way as the previous hybrid option. [/en/guides/endpoints/] ## Server Endpoints (API Routes) [/en/reference/modules/astro-static-paths/] export function createHandler(app) {
  return async (request) => {
    const { pathname } = new URL(request.url);

    // Endpoint to collect static paths during build
    if (pathname === '/__astro_static_paths') {
      const staticPaths = new StaticPaths(app);
      const…

## classical / association

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
    prefi… [/en/reference/adapter-reference/] The following example creates an adapter with a server entrypoint and stable support for Astro static output:

## adaptive / association

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
    prefi… [/en/reference/adapter-reference/] The following example creates an adapter with a server entrypoint and stable support for Astro static output:

## entity-graph / entity

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
    prefi… [/en/reference/routing-reference/] ```astro title="src/pages/static-about-page.astro" {3}
---
// with `output: 'server'` configured
export const prerender = true
---
<!-- My static about page -->
<!-- All other pages are rendered on demand -->
``` [/en/guides/routing/] When running `astro build`, Astro will output HTML files with the [meta refresh](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#examples) tag by default.

## ensemble / quality

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
    prefi… [/en/reference/adapter-reference/] The following example creates an adapter with a server entrypoint and stable support for Astro static output:

All execution is local and offline. The active verification has no MCP dependency.
