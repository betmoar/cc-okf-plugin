---
description: Regenerate index.md for an OKF bundle.
argument-hint: [bundle-path]
allowed-tools: Bash(python3:*), Read
---

Regenerate the catalog table in `index.md` for the OKF bundle at `$ARGUMENTS`
(default: the project root `.`).

1. Run the bundled reindexer with the Bash tool:

   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reindex.py" "$ARGUMENTS"
   ```

   Pass `--dry-run` to preview changes without writing (recommended on first v0.2
   reindex). If `${CLAUDE_PLUGIN_ROOT}` is not set, locate `scripts/reindex.py`
   inside the installed `okf` plugin directory (commonly under `~/.claude/plugins/`)
   and run that path instead. The script needs only the Python 3 standard library.

2. The script rewrites only the content between the
   `<!-- OKF:INDEX:BEGIN ... -->` and `<!-- OKF:INDEX:END -->` markers in
   `index.md`, preserving any surrounding prose. It reads every concept's
   frontmatter from `concepts/`, sorts rows by `(type, id)`, and reports how many
   concepts were indexed.

3. Report the count to the user. Suggest `/okf:validate` to confirm the bundle is
   conformant and `/okf:log` to record the change. Do not hand-edit the generated
   table — edit concept files and reindex instead.
