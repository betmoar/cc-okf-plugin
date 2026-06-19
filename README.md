# OKF — Open Knowledge Format plugin for Claude Code

A Claude Code plugin for reading, writing, validating, and maintaining **Open
Knowledge Format (OKF)** knowledge bundles: git-friendly directories of markdown
concept files with YAML frontmatter, a generated `index.md`, an append-only
`log.md`, `[[wiki-style]]` cross-links, and source citations.

The plugin is **dormant by default**. It only nudges Claude toward OKF
conventions in projects you explicitly activate, via a per-project sentinel and a
SessionStart gate — so installing it globally costs nothing in projects that
don't use OKF.

## What's inside

| Component | Path | Purpose |
| --------- | ---- | ------- |
| Skill `okf` | `skills/okf/` | Pure knowledge: how to read/write OKF, the spec, conformance rules, examples. Loads on demand. |
| Command `/okf:activate` | `commands/activate.md` | Opt a project into OKF (writes `.okf/active`). |
| Command `/okf:validate` | `commands/validate.md` | Check a bundle against conformance rules. |
| Command `/okf:reindex` | `commands/reindex.md` | Regenerate `index.md` from concept frontmatter. |
| Command `/okf:log` | `commands/log.md` | Append a timestamped entry to `log.md`. |
| Hook | `hooks/hooks.json` | SessionStart gate — emits a short OKF pointer only when `.okf/active` exists. |
| Scripts | `scripts/` | `okf-gate.sh`, `validate.py`, `reindex.py`, `append-log.py`. |

Architecture: the **skill is knowledge** (no side effects); the **commands are
actions** that run the shared **scripts**. A skill cannot invoke a slash command,
so knowledge and lifecycle actions are kept separate but share `scripts/` via
`${CLAUDE_PLUGIN_ROOT}`.

## Install

This repo is the plugin itself. It's distributed through a separate marketplace
catalog repo that points here via a GitHub source
(`{ "source": "github", "repo": "betmoar/cc-okf-plugin" }`):

```
/plugin marketplace add betmoar/ccp-market
/plugin install okf@betmoar
```

(`betmoar` is the marketplace's `name`, not this repo.) For local development
without a marketplace, load the plugin straight from disk:

```
claude --plugin-dir /path/to/cc-okf-plugin
```

## Quick start

```
/okf:activate              # writes .okf/active for this project
# start a new session (or /clear) so the SessionStart gate fires
/okf:reindex               # create/refresh index.md
/okf:log "Initial bundle"  # create/append log.md
/okf:validate              # expect: 0 error(s)
```

Then create concepts under `concepts/<id>.md`. The `okf` skill documents the
frontmatter schema, cross-link and citation conventions, and conformance rules;
see `skills/okf/references/` for the full spec, rules, and examples.

## The activation gate (per-project opt-in)

Claude Code has no native per-project enable for a globally-installed plugin, and
plugin skills can't be gated on a sentinel file natively. This plugin uses the
established workaround:

1. `/okf:activate` writes `.okf/active` at the project root.
2. On session start, `scripts/okf-gate.sh` checks for that sentinel. If present,
   it emits a short factual pointer as `SessionStart` `additionalContext`
   telling Claude OKF is active here; if absent, it emits nothing.
3. The full OKF spec stays in the skill body / `references/` and loads only when
   relevant (progressive disclosure), so token cost is minimal even when active.

Hook and `hooks.json` changes require `/reload-plugins` or a restart to take
effect. If a brand-new conversation doesn't pick up the pointer, start a fresh
session or `/clear` (a known SessionStart timing quirk on some versions).

## Permissions

Each command declares a tightly scoped `allowed-tools` (e.g. `validate` only
needs `Bash(python3:*)`, `Bash(python:*)`, `Read`). On first run, choose
"Yes, and don't ask again" to persist the grant into `.claude/settings.local.json`
for that project. Prefer letting Claude Code write these permissions rather than
hand-editing the file.

## Requirements

- The Python scripts need only the **Python 3 standard library** (PyYAML is used
  if present, but is not required — there is a built-in frontmatter parser).
- `okf-gate.sh` is a POSIX `bash` script.

## Development & versioning

`version` in `.claude-plugin/plugin.json` drives updates: bump it (and the
CHANGELOG) for users to receive changes. During active iteration you may instead
leave `version` unset so each commit is treated as a new version (instant
propagation after `/plugin marketplace update` + `claude plugin update`).

Validate before publishing (from the repo root):

```
claude plugin validate . --strict
```

## License

MIT — see [LICENSE](LICENSE).
