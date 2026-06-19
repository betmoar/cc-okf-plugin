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
| Command `/okf:reindex` | `commands/reindex.md` | Regenerate `index.md` from concept frontmatter and regenerate each concept's `links:` from its body `[[id]]` wiki-links. Supports `--dry-run`. |
| Command `/okf:log` | `commands/log.md` | Append a timestamped entry to `log.md`. |
| Command `/okf:rename` | `commands/rename.md` | Rename a concept, rewriting its filename, `id:`, and every cross-link `[[old]]` → `[[new]]` across the bundle. |
| Command `/okf:query` | `commands/query.md` | Find concepts by `--tag`, `--type`, `--status`, or `--text` (AND-combined). |
| Hook | `hooks/hooks.json` | SessionStart gate — emits a short OKF pointer only when `.okf/active` exists. |
| Scripts | `scripts/` | `okf-gate.sh`, `okf_common.py`, `validate.py`, `reindex.py`, `rename.py`, `query.py`, `append-log.py`. |

Architecture: the **skill is knowledge** (no side effects); the **commands are
actions** that run the shared **scripts**. A skill cannot invoke a slash command,
so knowledge and lifecycle actions are kept separate but share `scripts/` via
`${CLAUDE_PLUGIN_ROOT}`.

## When to reach for OKF

OKF sits between two things you may already use:

- **vs. a personal vault (Obsidian/Foam/Dendron):** OKF lives *in the project's
  own git repo* and is maintained through explicit commands (`/okf:reindex`,
  `/okf:rename`, …) that Claude runs as it works — it's team-visible project
  knowledge, not a personal note store. (The plugin stays dormant until you
  `/okf:activate` a project.)
- **vs. Claude Code's built-in memory:** memory is cross-session assistant
  memory scoped to you; an OKF bundle is durable, reviewable knowledge committed
  alongside the code it describes, shared by everyone who clones the repo.

Reach for OKF when the knowledge belongs to the *project* and should live in its
history. Use a vault or memory when it belongs to *you*.

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
needs `Bash(python3:*)`, `Read`). On first run, choose
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
