---
type: Agent Skill
title: Brave Search
description: Use when Codex needs to research the web through the Brave Search CLI
  (`bx`) and return useful sources quickly. Trigger for web lookups, current news
  checks, image/video discovery, place lookups, query refinement, domain filtering,
  or when the user asks to use Brave Search specifically. Prefer this skill when `bx
  web`, `bx news`, `bx images`, `bx videos`, or `bx places` can answer the request
  efficiently from the terminal.
tags:
- codex
- skill
skill_name: brave-search-effective
source_path: skills/brave-search-effective/SKILL.md
---

# Brave Search Effective

Use `bx` as a fast search front-end. Optimize for useful queries, narrow result sets, and explicit fallback when a command is unavailable in the current plan.

## Standalone boundary

- Treat the `bx` executable, Brave API access, and its configured credentials as explicit external prerequisites.
- Use only this `SKILL.md` and package-local references for the workflow; do not require repository files or another skill.
- Run `bx --help` and `bx config --help` before the first search in an unfamiliar installation. If either the executable or authentication is unavailable, return that diagnostic instead of inferring repository-specific setup.

## Workflow

1. Choose the narrowest working subcommand first.
2. Start with a query that includes the target entity, task, and one disambiguator.
3. Add site constraints only after a broad query is noisy.
4. Inspect the JSON output and extract the relevant fields instead of dumping raw results.
5. If a subcommand returns `OPTION_NOT_IN_PLAN`, switch to a working alternative and say so briefly.

## Plan-only and offline requests

When the user asks only for a plan, state that no CLI command, network call, or
search was executed, no results were found, and every command is an example.
For a broad multi-part request, present five to eight relevant examples in the
order they would run. A seven-command template is:

1. `bx --help`
2. `bx config --help`
3. `bx news "<entity> <event> <date context>"`
4. `bx images "<entity> <visual need>"`
5. `bx videos "<entity> <tutorial need>"`
6. `bx places --location "<city region country>" -q "<place type>"`
7. `bx web "site:<authoritative-domain> <entity> <verification need>"`

Omit search commands unrelated to the request. Include a fallback only for a
command in the plan or a failure named by the user; do not pad the plan with
unsupported-feature fallbacks. Never present example links, dates, venues, or
media as found results.

## Choose The Command

- Use `bx web` for general web research, documentation, discussions, and mixed result sets.
- Use `bx news` for recent coverage and current-event style queries.
- Use `bx images` when the user explicitly wants images or visual references.
- Use `bx videos` when the user wants tutorials, talks, or walkthroughs.
- Use `bx places` for local search. Pass `-q` plus either `--location` or coordinates.
- Do not assume `bx context`, `bx answers`, `bx suggest`, or `bx spellcheck` are available. Probe only if needed and fall back immediately if the plan rejects them.

## Query Construction

- Start with plain language, not Boolean-heavy syntax.
- Include one context token that reduces ambiguity.
  Example: `ripgrep windows install`
  Example: `openai codex plugins March 2026`
- Prefer `site:` only when you want one source family.
  Example: `site:developers.openai.com codex skills`
- Prefer quoted phrases only for exact names or error text.
  Example: `"OPTION_NOT_IN_PLAN" brave search cli`
- For local search, keep the query short and push geography into `--location`.
  Example: `bx places --location "New York NY US" -q "coffee"`

## Result Handling

- Summarize the top relevant hits and include links.
- For `bx web`, inspect titles, URLs, descriptions, and special sections such as infobox, discussions, or videos.
- For `bx news`, mention absolute dates when recency matters.
- For `bx images` and `bx videos`, return only a few strong candidates unless the user asked for breadth.
- If the results are noisy, rerun with one refinement:
  site restriction, exact phrase, better entity name, or a narrower topic word.

## Current Plan Notes

These behaviors were verified in this environment with the configured key:

- Working: `bx web`
- Working: `bx news`
- Working: `bx images`
- Working: `bx videos`
- Working: `bx places` when invoked with `-q` and `--location`
- Not available in this plan: `bx context`
- Not available in this plan: `bx answers`
- Not available in this plan: `bx suggest`
- Not available in this plan: `bx spellcheck`

Treat these as environment-specific, not universal truths. Re-check if the key or plan changes.
Inspect `bx config --help` for the configuration subcommands supported by the installed CLI.

## Fallback Rules

- If `bx context` is unavailable, use `bx web` and synthesize manually.
- If `bx answers` is unavailable, use `bx web` or `bx news` plus direct source summaries.
- If `bx suggest` or `bx spellcheck` is unavailable, refine the query yourself.
- If `bx places` errors on positional input, switch to `-q` and `--location`.

## Reference

Read [recipes.md](./references/recipes.md) for tested command patterns and example queries before doing multi-step research.
