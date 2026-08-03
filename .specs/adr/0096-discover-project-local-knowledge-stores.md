---
adr: "0096"
title: "ADR 0096: Discover Project-Local Knowledge Stores"
summary: "Initialize knowledge in a project's .know directory and resolve commands against the nearest project store before using the global fallback."
status: "Accepted"
date: "2026-08-02"
product: "knowledge"
owner: "Platform Architecture"
area: "CLI Storage"
tags:
  - cli
  - knowledge
  - local-first
  - storage
---

# ADR 0096: Discover Project-Local Knowledge Stores

## Status

Accepted.

## Context

The CLI previously selected `~/.knowledge` unless every invocation supplied
`--store`. That made unrelated projects share one implicit knowledge context
and made saved commands fragile because their intended store depended on an
extra flag.

Project work needs a durable local boundary: initialize knowledge once at the
project root, then let commands issued from any project subdirectory operate
on that same knowledge without repeating configuration.

## Decision

- `know init` without `--store` initializes `<current-directory>/.know`.
- Ordinary commands select stores in this precedence order:
  1. the explicit `--store <PATH>` value;
  2. the nearest `.know` directory at or above the working directory;
  3. the existing `~/.knowledge` user store.
- Discovery accepts an initialized or partially initialized `.know` directory;
  normal command initialization repairs its required configuration files.
- Running `know init` inside a parent project's subtree creates a new nested
  `.know` boundary rather than silently reusing the parent store.
- Store contents and key/source layouts remain unchanged. This decision only
  changes store placement and resolution.

## Consequences

Positive:

- knowledge context travels with a project;
- commands and generated metadata remain short because `--store` is optional;
- nested working directories resolve consistently to the project root;
- existing global workflows continue to work outside initialized projects.

Negative:

- command results can differ after changing the working directory;
- nested `.know` directories intentionally shadow parent project stores;
- users must use `--store` when they want to bypass a discovered local store.
