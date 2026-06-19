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
  `/okf:reindex`; do not hand-edit it. Prose outside the markers is preserved.
- `log.md` — an append-only history of changes, managed by `/okf:log`. Never
  rewrite or reorder existing entries.
- `.okf/active` — the per-project activation sentinel, written by `/okf:activate`.

## Concept frontmatter

Every concept file begins with a YAML frontmatter block. Required fields:
`id`, `title`, `type`, `created`, `updated`. Common optional fields: `status`,
`tags`, `links`, `sources`.

```yaml
---
id: spaced-repetition          # required; kebab-case; MUST equal the filename stem
title: Spaced Repetition       # required; human-readable
type: concept                  # required; concept | decision | reference | glossary
status: stable                 # optional; draft | review | stable | deprecated
created: 2026-06-01            # required; ISO date YYYY-MM-DD
updated: 2026-06-19            # required; ISO date; must be >= created
tags: [learning, memory]       # optional; list of kebab-case tags
links: [forgetting-curve]      # optional; list of OTHER concept ids (the link graph)
sources:                       # optional; list of citations
  - title: Title of the source
    url: https://example.com/article
---
```

Keep `id` stable once created — other concepts reference it. To rename, update
the file, the `id`, and every referencing `links`/`[[wiki-link]]`, then reindex.

## Reading a bundle

To understand a bundle quickly:

1. Read `index.md` first for the catalog of concepts, their types, and status.
2. Read `log.md` for recent changes and intent.
3. Open individual `concepts/<id>.md` files as needed; follow `links` and
   `[[wiki-links]]` to related concepts.

Prefer the index and log as the map; do not read every concept file unless the
task requires breadth.

## Writing and extending a bundle

To add a concept:

1. Choose a unique, kebab-case `id`. Create `concepts/<id>.md` (the filename
   stem MUST equal `id`).
2. Fill required frontmatter. Set `created` and `updated` to today's date.
3. Write the body. Link related concepts inline with `[[other-id]]` wiki-links,
   and record the same relationships in the `links` frontmatter list so the link
   graph is machine-readable.
4. Cite sources in the `sources` list (each with at least a `title`).
5. Suggest the user run `/okf:reindex` to refresh `index.md`, and `/okf:log` to
   record the change.

To edit an existing concept: change the body/frontmatter, bump `updated` to
today, preserve `id`, and keep cross-links consistent. When removing a concept,
also remove or repoint every `links`/`[[wiki-link]]` that targeted it, or
validation will report dangling links.

Cross-link and citation conventions are detailed in `references/spec.md`; worked
examples are in `references/examples.md`.

## Conformance, in brief

A bundle is conformant when: `index.md` and `log.md` exist at the bundle root;
every concept has the required frontmatter; each `id` is unique and matches its
filename; `type`/`status` use allowed values; dates are valid ISO dates with
`updated >= created`; and every `links` target resolves to an existing concept.
Dangling cross-links and an out-of-date `index.md` are the most common failures.
The full rule list with severities is in `references/conformance.md`, and
`/okf:validate` enforces it programmatically.

## Lifecycle actions are commands, not this skill

This skill is pure knowledge and performs no side effects. To change bundle
state, suggest the user run the OKF commands, which execute the bundled scripts:

- `/okf:activate [bundle-path]` — opt this project into OKF (writes `.okf/active`).
- `/okf:validate [bundle-path]` — check conformance (`scripts/validate.py`).
- `/okf:reindex [bundle-path]` — regenerate `index.md` (`scripts/reindex.py`).
- `/okf:log [message]` — append a `log.md` entry (`scripts/append-log.py`).

A skill cannot invoke a slash command directly. When an action is needed,
perform the editing work that is in scope, then tell the user the exact command
to run.

## Additional resources

- **`references/spec.md`** — the full OKF v0.1 specification (directory layout,
  frontmatter schema, index/log formats, cross-link and citation rules).
- **`references/conformance.md`** — every conformance rule with its severity,
  mirroring what `/okf:validate` checks.
- **`references/examples.md`** — a complete example bundle: concept files,
  cross-links, citations, and generated `index.md`/`log.md`.
