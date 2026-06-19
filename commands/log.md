---
description: Append a timestamped entry to the OKF log.md.
argument-hint: [message]
allowed-tools: Bash(python3:*), Read
---

Append a structured, timestamped entry to the OKF bundle's append-only `log.md`.

The log message is `$ARGUMENTS`. If it is empty, ask the user what to record
before running anything.

1. Choose a short `action` verb that categorizes the change from context — one of
   `add`, `update`, `remove`, `reindex`, or `note` (default `note`).

2. Run the bundled appender with the Bash tool (bundle defaults to the project
   root `.`; add `--bundle <path>` if working in a subdirectory bundle):

   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/append-log.py" --action <verb> "$ARGUMENTS"
   ```

   If `${CLAUDE_PLUGIN_ROOT}` is not set, locate `scripts/append-log.py` inside
   the installed `okf` plugin directory (commonly under `~/.claude/plugins/`) and
   run that path instead. Use `python` if `python3` is unavailable. The script
   needs only the Python 3 standard library.

3. The script appends the entry in chronological order (creating `log.md` with a
   header if it does not exist) and never rewrites existing entries. Confirm the
   appended entry to the user.
