#!/usr/bin/env bash
# OKF SessionStart gate.
#
# Emits a short OKF pointer as SessionStart additionalContext ONLY when this
# project has been activated (an `.okf/active` sentinel exists). Otherwise it
# emits nothing and exits 0, leaving the `okf` skill effectively dormant for
# non-OKF projects and avoiding per-session token bloat.
#
# Environment:
#   CLAUDE_PROJECT_DIR  - project root (provided by Claude Code); falls back to $PWD.
set -euo pipefail

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
sentinel="${project_dir}/.okf/active"

if [ -f "$sentinel" ]; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"OKF is active for this project (an .okf/active sentinel is present). Follow the okf skill's conventions when reading, writing, or editing knowledge bundles in this project. Lifecycle commands: /cc-okf:validate (check conformance), /cc-okf:reindex (regenerate index.md), /cc-okf:log (append a log entry), /cc-okf:activate (re-run activation)."}}
JSON
fi

exit 0
