# Changelog

All notable changes to the OKF plugin are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## 0.2.0

- Link graph deduplicated: body `[[id]]` is now the single source of truth;
  `/okf:reindex` generates the `links:` frontmatter field from it.
- `/okf:reindex --dry-run`: preview concept-file changes without writing.
  First-run migration notice when hand-authored `links:` are dropped.
- New `/okf:rename <old> <new>`: link-aware, recoverable concept rename.
- New `/okf:query`: filter concepts by `--tag/--type/--status/--text` (AND).
- Validation: dangling body `[[id]]` is now an ERROR; stale `links:` is a WARN.
- Commands declare `python3`-only in `allowed-tools` (dropped the `python` alias).

## [0.1.0] - 2026-06-19

Initial release.

### Added
- `okf` skill (`skills/okf/`) — knowledge layer for reading and writing OKF
  bundles, with `references/spec.md` (OKF v0.1 specification),
  `references/conformance.md` (conformance rules and severities), and
  `references/examples.md` (a worked example bundle).
- Commands: `/okf:activate`, `/okf:validate`, `/okf:reindex`, `/okf:log`.
- SessionStart activation gate (`hooks/hooks.json` + `scripts/okf-gate.sh`) that
  emits a short OKF pointer only when a project has an `.okf/active` sentinel.
- Scripts: `validate.py` (conformance validator), `reindex.py` (regenerates
  `index.md`), `append-log.py` (appends to `log.md`). Standard-library only;
  PyYAML used when available with a built-in fallback parser.
- Marketplace catalog (`.claude-plugin/marketplace.json`) co-located with the
  plugin (`source: "./"`).
