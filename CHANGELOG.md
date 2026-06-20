# Changelog

All notable changes to the OKF plugin are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## 0.2.1

Permissive & interoperable — every change makes the format MORE permissive; no
v0.2-conformant bundle becomes non-conformant.

- **§1 X1 ERROR→WARN:** dangling body `[[id]]` links are now advisory (WARN),
  not failures. Supports "reference now, create later" authoring. Exit 0.
- **§2 Relaxed required fields:** only `id` and `type` are required (C2).
  `title`, `created`, `updated` are recommended. When `title` is absent,
  `index.md` and query output show the filename stem.
- **§3 Open type/status enums (C5/C6 removed):** `type` and `status` are
  free-form strings. Known values remain documented conventions but are no longer
  enforced by the validator.
- **§4 Drop `links:` mirror:** the generated `links:` frontmatter field is
  removed. Body links are now the single source of truth — no generated mirror,
  no drift. `/cc-okf:reindex` strips any existing `links:` field idempotently (with a
  migration notice on the first run that removes it). Rule X2 (stale `links:`)
  is removed.
- **§5 Markdown links in the link graph:** `[text](target.md)` links alongside
  `[[wiki]]` links are recognized by the extractor. Flat-model resolution: strip
  `./`, `concepts/`, `.md`, `#fragment`, `?query`. Dangling markdown links follow
  the same §1 WARN rule as wiki links.
- Backward compatible: all v0.2-conformant bundles remain conformant under
  v0.2.1. First `reindex` run on a v0.2 bundle strips the `links:` field with a
  migration notice.

## 0.2.0

- Link graph deduplicated: body `[[id]]` is now the single source of truth;
  `/cc-okf:reindex` generates the `links:` frontmatter field from it.
- `/cc-okf:reindex --dry-run`: preview concept-file changes without writing.
  First-run migration notice when hand-authored `links:` are dropped.
- New `/cc-okf:rename <old> <new>`: link-aware, recoverable concept rename.
- New `/cc-okf:query`: filter concepts by `--tag/--type/--status/--text` (AND).
- Validation: dangling body `[[id]]` is now an ERROR; stale `links:` is a WARN.
- Commands declare `python3`-only in `allowed-tools` (dropped the `python` alias).
- Known limitation: a concept file's CRLF line endings are normalized to LF when reindex rewrites its `links:` field.

## [0.1.0] - 2026-06-19

Initial release.

### Added
- `okf` skill (`skills/okf/`) — knowledge layer for reading and writing OKF
  bundles, with `references/spec.md` (OKF v0.1 specification),
  `references/conformance.md` (conformance rules and severities), and
  `references/examples.md` (a worked example bundle).
- Commands: `/cc-okf:activate`, `/cc-okf:validate`, `/cc-okf:reindex`, `/cc-okf:log`.
- SessionStart activation gate (`hooks/hooks.json` + `scripts/okf-gate.sh`) that
  emits a short OKF pointer only when a project has an `.okf/active` sentinel.
- Scripts: `validate.py` (conformance validator), `reindex.py` (regenerates
  `index.md`), `append-log.py` (appends to `log.md`). Standard-library only;
  PyYAML used when available with a built-in fallback parser.
- Marketplace catalog (`.claude-plugin/marketplace.json`) co-located with the
  plugin (`source: "./"`).
