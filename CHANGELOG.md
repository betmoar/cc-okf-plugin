# Changelog

All notable changes to the OKF plugin are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

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
