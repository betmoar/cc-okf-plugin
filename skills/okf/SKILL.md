---
name: okf
description: Conventions for reading, writing, validating, and maintaining Open Knowledge Format (OKF) knowledge bundles — directories of markdown concept files with YAML frontmatter, a generated index.md, an append-only log.md, [[wiki-style]] cross-links, and source citations. This skill should be used whenever the user reads, writes, edits, reorganizes, or validates an OKF bundle; encounters an index.md/log.md pair, a concepts/ directory, or .okf markers; or mentions OKF, knowledge bundles, concept notes, or conformance. Apply it even when the user does not say "OKF" explicitly but is clearly working inside a bundle whose project is OKF-activated.
---

# Open Knowledge Format (OKF)

OKF is a lightweight convention for storing durable knowledge as a directory of
markdown "concept" files with YAML frontmatter, tied together by a generated
`index.md`, an append-only `log.md`, cross-links between concepts, and citations
to sources. This skill is the knowledge layer: it describes how to read and
write bundles correctly. State-changing actions live in the OKF commands, not
here (see "Lifecycle actions are commands" below).

## When these conventions apply

Apply OKF conventions only when the current project is OKF-activated — that is,
when a `.okf/active` sentinel exists at the project root, or the session context
already indicates OKF is active for this project. In a non-activated project,
treat markdown as ordinary markdown and do not impose OKF structure unasked.
When unsure whether a project is activated, check for `.okf/active` or an
`index.md`/`log.md` pair before applying these rules.

## Bundle anatomy

An OKF bundle is a directory containing:

- `concepts/` — one markdown file per concept, named `<id>.md`. Each file has
  YAML frontmatter plus a markdown body.
- `index.md` — a generated catalog of all concepts. The table between the
  `<!-- OKF:INDEX:BEGIN ... -->` and `<!-- OKF:INDEX:END -->` markers is owned by
  `/cc-okf:reindex`; do not hand-edit it. Prose outside the markers is preserved.
- `log.md` — an append-only history of changes, managed by `/cc-okf:log`. Never
  rewrite or reorder existing entries.
- `.okf/active` — the per-project activation sentinel, written by `/cc-okf:activate`.

## Concept frontmatter

Every concept file begins with a YAML frontmatter block. Required fields:
`id`, `type`. Recommended fields: `title`, `created`, `updated`. Common
optional fields: `status`, `tags`, `sources`.

`type` and `status` are **free-form** — any value is accepted; the conventional
values are documented for grouping and filtering but not enforced.

```yaml
---
id: spaced-repetition          # required; kebab-case; MUST equal the filename stem
type: concept                  # required; free-form — conventional: concept | decision | reference | glossary
title: Spaced Repetition       # recommended; when absent, consumers derive from filename stem
status: stable                 # optional; free-form — conventional: draft | review | stable | deprecated
created: 2026-06-01            # recommended; ISO date YYYY-MM-DD
updated: 2026-06-19            # recommended; ISO date; must be >= created when both present
tags: [learning, memory]       # optional; list of kebab-case tags
sources:                       # optional; list of citations
  - title: Title of the source
    url: https://example.com/article
---
```

There is **no generated `links:` field**. Body links (`[[wiki]]` or
`[text](target.md)`) are the single source of truth and are read directly by
the toolchain. `/cc-okf:reindex` strips any legacy `links:` from v0.2 bundles.

Keep `id` stable once created — other concepts reference it. To rename, use
`/cc-okf:rename <old-id> <new-id>` — it updates the file, the `id`, and all
referencing body `[[wiki-link]]` occurrences, and reindexes automatically.

## Reading a bundle

To understand a bundle quickly:

1. Read `index.md` first for the catalog of concepts, their types, and status.
2. Read `log.md` for recent changes and intent.
3. Open individual `concepts/<id>.md` files as needed; follow `[[wiki-links]]`
   and `[text](md-links)` to related concepts.

Prefer the index and log as the map; do not read every concept file unless the
task requires breadth.

## Writing and extending a bundle

To add a concept:

1. Choose a unique, kebab-case `id`. Create `concepts/<id>.md` (the filename
   stem MUST equal `id`).
2. Fill required frontmatter (`id`, `type`). Add `title`, `created`, `updated`
   when convenient.
3. Write the body. Link related concepts inline with `[[other-id]]` wiki-links
   or `[text](other-id.md)` markdown links. Body links are the source of truth
   for the link graph — no `links:` field needed.
4. Cite sources in the `sources` list (each with at least a `title`).
5. Suggest the user run `/cc-okf:reindex` to refresh `index.md`, then
   `/cc-okf:log` to record the change.

To edit an existing concept: change the body/frontmatter, bump `updated` to
today, preserve `id`, and keep cross-links consistent. When removing a concept,
also remove or repoint every `[[wiki-link]]` that targeted it, or validation
will report a WARN for dangling links.

Cross-link and citation conventions are detailed in `references/spec.md`; worked
examples are in `references/examples.md`.

## Conformance, in brief

A bundle is conformant when: `index.md` and `log.md` exist at the bundle root;
every concept has parseable frontmatter with `id` and `type`; each `id` is
unique and matches its filename; dates (when present) are valid ISO dates with
`updated >= created`; and every body link resolves to an existing concept (WARN
if not — tolerant for incremental authoring). An out-of-date `index.md` is
advisory (WARN). The full rule list with severities is in
`references/conformance.md`, and `/cc-okf:validate` enforces it programmatically.

## Lifecycle actions are commands, not this skill

This skill is pure knowledge and performs no side effects. To change bundle
state, suggest the user run the OKF commands, which execute the bundled scripts:

- `/cc-okf:activate [bundle-path]` — opt this project into OKF (writes `.okf/active`).
- `/cc-okf:validate [bundle-path]` — check conformance (`scripts/validate.py`).
- `/cc-okf:reindex [bundle-path]` — strip any legacy `links:` and rebuild `index.md` (`scripts/reindex.py`).
- `/cc-okf:log [message]` — append a `log.md` entry (`scripts/append-log.py`).
- `/cc-okf:rename <old-id> <new-id>` — link-aware, recoverable concept rename (updates all referencing concepts and reindexes).
- `/cc-okf:query` — filter concepts by `--tag`, `--type`, `--status`, or `--text` (all filters AND-combined).

A skill cannot invoke a slash command directly. When an action is needed,
perform the editing work that is in scope, then tell the user the exact command
to run.

## Additional resources

- **`references/spec.md`** — the full OKF v0.1 specification (directory layout,
  frontmatter schema, index/log formats, cross-link and citation rules).
- **`references/conformance.md`** — every conformance rule with its severity,
  mirroring what `/cc-okf:validate` checks.
- **`references/examples.md`** — a complete example bundle: concept files,
  cross-links, citations, and generated `index.md`/`log.md`.
