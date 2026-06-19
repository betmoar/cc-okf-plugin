---
description: Find OKF concepts by tag, type, status, or text.
allowed-tools: Bash(python3:*), Read
---

Search the current OKF bundle's concepts. Filters combine with AND; `--text` is
a case-insensitive substring match over title and body.

Run (pass any of `--tag`, `--type`, `--status`, `--text`):

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/query.py" $ARGUMENTS
```
