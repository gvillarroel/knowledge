# Brave CLI Recipes

Use these patterns as starting points and adapt them to the task.

## General Web Research

```powershell
bx web "ripgrep windows install"
bx web "site:developers.openai.com codex skills"
bx web "\"OPTION_NOT_IN_PLAN\" brave search cli"
```

Use for docs, official pages, forum threads, and mixed-result discovery.

## News Research

```powershell
bx news "OpenAI Codex"
bx news "Brave Search API"
```

Use when the request depends on what changed recently. Report dates explicitly.

## Image And Video Discovery

```powershell
bx images "ripgrep logo"
bx videos "ripgrep tutorial"
```

Use when the user wants visual references, screenshots, demos, or talks.

## Local Search

```powershell
bx places --location "New York NY US" -q "coffee" --count 3
bx places --location "San Francisco CA US" -q "bookstore"
```

Keep the search term short. Put geography in `--location`.

## Manual Refinement Moves

- Add one disambiguator: product name, date, platform, or file type.
- Add `site:` only when you want a known source family.
- Add quotes only for exact names or literal error messages.
- Replace vague verbs like `fix` or `help` with the concrete target: `install`, `pricing`, `release notes`, `API docs`.

## Unsupported Or Plan-Limited Commands

If any of these return `OPTION_NOT_IN_PLAN`, switch away immediately:

- `bx context`
- `bx answers`
- `bx suggest`
- `bx spellcheck`
