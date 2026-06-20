---
description: Rename an OKF concept by id, rewriting every cross-link.
allowed-tools: Bash(python3:*), Read
---

Rename the concept `$1` to `$2` in the current OKF bundle, rewriting its
filename, `id:`, every `[[old]]` wiki-link across all concepts, and regenerating
`links:` and `index.md`.

Run:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rename.py" $ARGUMENTS
```

After it succeeds, suggest the user run `/cc-okf:log "renamed $1 to $2"`. Note that
`updated` is intentionally left unchanged (it is human-authored).
