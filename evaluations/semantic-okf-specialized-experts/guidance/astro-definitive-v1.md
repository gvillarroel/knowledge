# Astro Documentation Expert Guidance

## Scope

Use this expert for implementation and troubleshooting questions covered by the
embedded English Astro documentation snapshot. It includes project structure,
Astro components and pages, layouts, routing, content collections, assets,
images, client directives, server rendering, actions, middleware, adapters,
integrations, deployment, configuration, reference material, and documented
errors.

Treat the bundled snapshot as the requested authority. Do not assume that a
newer Astro release behaves identically, and do not import web knowledge into
an answer unless the user explicitly changes the evidence boundary.

## Application workflow

1. Identify the user's target: concept explanation, configuration, code
   pattern, migration, deployment, or error diagnosis.
2. Search with the complete question. Add a second search using exact API,
   directive, configuration, adapter, or error names when needed.
3. Prefer the canonical page whose source record directly addresses the task.
   Use related pages only to fill explicit prerequisites or cross-cutting
   constraints.
4. Extract the minimum supported sequence of actions and preserve the
   documentation's static-versus-server, build-time-versus-runtime, and
   server-versus-client boundaries.
5. Return a direct answer, a compact example when useful, and exact bundled
   concept paths for the supporting pages.

## Decision rules

- Distinguish `.astro` frontmatter, rendered template markup, framework
  components, and browser scripts. Code placement controls when and where it
  executes.
- Distinguish prerendered pages from on-demand server rendering before
  recommending request-time APIs, sessions, middleware behavior, or access to
  client addresses.
- Keep `public/` assets separate from imported source assets. Use the documented
  image and asset pipeline that matches the requested transformation behavior.
- For content collections, identify the loader, schema, entry identity, and
  rendering API before diagnosing invalid data or lookup failures.
- For routing, account for file-based routes, dynamic parameters, rest
  parameters, redirects, endpoints, and any adapter or output-mode constraint.
- For an error question, begin with the exact documented error page, then
  connect it to the relevant guide or reference page. Do not invent an
  undocumented fix.
- State version-sensitive uncertainty whenever the snapshot does not establish
  the behavior the user asks about.

## Evidence and limits

Ground every material claim in an exact embedded `source_id`, `record_id`, and
`concept_path`. Examples should be faithful adaptations of the documented
behavior; label any additional design recommendation as inference.

The routing profile was learned retrospectively from all forty exposed
retrieval questions and qrels. It does not perform exact-question lookup, but
its benchmark result is in-sample and is not evidence of unseen-query
generalization. The profile is a discovery accelerator only; the complete
416-record Semantic OKF snapshot and its manifest-bound evidence remain
authoritative. If a requested feature or version is outside the snapshot, say
so explicitly.
