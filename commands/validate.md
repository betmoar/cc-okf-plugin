---
description: Validate an OKF bundle against conformance rules.
argument-hint: [bundle-path]
allowed-tools: Bash(python3:*), Bash(python:*), Read
---

Run OKF conformance validation on the bundle at `$ARGUMENTS` (default: the
project root `.`).

1. Run the bundled validator with the Bash tool:

   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" "$ARGUMENTS"
   ```

   If `${CLAUDE_PLUGIN_ROOT}` is not set in the shell (a known quirk in some
   Claude Code versions), locate `scripts/validate.py` inside the installed
   `okf` plugin directory (commonly under `~/.claude/plugins/`) and run that
   path instead. Use `python` if `python3` is unavailable. The script needs only
   the Python 3 standard library.

2. Read the script's output. It prints warnings, then errors, then a summary
   line `Result: <n> error(s), <m> warning(s)` and exits non-zero when there are
   errors.

3. Summarize the findings for the user, grouped by concept, naming the specific
   rule each violation breaks (see the `okf` skill's `references/conformance.md`
   for rule meanings). Distinguish ERRORs (must fix; bundle is non-conformant)
   from WARNs (advisory). When errors involve a stale `index.md`, recommend
   `/okf:reindex`. Do not edit any files as part of validation.
