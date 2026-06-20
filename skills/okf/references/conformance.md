# OKF Conformance Rules

These are the rules enforced by `/cc-okf:validate` (`scripts/validate.py`). Each
rule has a severity:

- **ERROR** — a violation; the bundle is non-conformant and `validate.py` exits
  non-zero.
- **WARN** — advisory; does not fail validation but SHOULD be addressed.

`validate.py` ignores unknown frontmatter fields (forward compatibility) and
treats files under `.okf/` and the `index.md`/`log.md` files as non-concepts.

## Bundle-level

| # | Severity | Rule |
| - | -------- | ---- |
| B1 | ERROR | `index.md` exists at the bundle root. |
| B2 | ERROR | `log.md` exists at the bundle root. |
| B3 | WARN  | A `concepts/` directory exists. (Absent ⇒ the bundle has no concepts yet.) |
| B4 | WARN  | `concepts/` is non-empty. |

## Concept-level

| # | Severity | Rule |
| - | -------- | ---- |
| C1 | ERROR | The file has a YAML frontmatter block. |
| C2 | ERROR | Required fields present and non-empty: `id`, `type`. (`title`, `created`, `updated` are recommended but not required.) |
| C3 | ERROR | `id` equals the filename stem (`concepts/<id>.md`). |
| C4 | ERROR | `id` is unique within the bundle. |
| C7 | ERROR | `created` and `updated`, when present, are valid ISO dates (`YYYY-MM-DD`). |
| C8 | ERROR | `updated`, when present, is not earlier than `created`. |
| C9 | WARN  | Each `sources` entry has a `title`; any `url` starts with `http(s)://`. |

`type` and `status` are **free-form strings** — any value is accepted. The
conventional values (`concept`, `decision`, `reference`, `glossary` for type;
`draft`, `review`, `stable`, `deprecated` for status) are documented in
`spec.md` and used for ordering and filtering, but the validator does not
enforce them. This lets producers use domain-specific types without ceremony.

## Cross-bundle integrity

| # | Severity | Rule |
| - | -------- | ---- |
| X1 | WARN | A body link (`[[wiki-link]]` or `[text](md-link)`) does not resolve to an existing concept id. |

Body links are the single source of truth for the link graph. Dangling links
are tolerated (WARN only) to support the "reference now, create later" authoring
pattern and incremental agent writes. There is no generated `links:` field;
`/cc-okf:reindex` strips any leftover `links:` from v0.2 bundles.

## Index freshness (advisory)

| # | Severity | Rule |
| - | -------- | ---- |
| I1 | WARN | `index.md` lists every existing concept (none missing). |
| I2 | WARN | `index.md` lists no ids that no longer exist (none stale). |

`/cc-okf:reindex` is the source of truth for `index.md`. After adding, renaming, or
removing concepts, run `/cc-okf:reindex`, then re-run `/cc-okf:validate` — I1/I2 should
clear.

## Interpreting results

`validate.py` prints warnings first, then errors, then a summary line:

```
Result: <n> error(s), <m> warning(s)
```

Exit code `0` = conformant (errors == 0); `1` = non-conformant; `2` = usage
error (e.g. the bundle path is not a directory). Fix ERRORs first; they are the
ones that break the format's guarantees.
