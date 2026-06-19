---
description: Opt this project into OKF; write the .okf/active sentinel.
argument-hint: [bundle-path]
allowed-tools: Bash(mkdir:*), Write, Read
---

Activate OKF for this project so the SessionStart gate begins pointing future
sessions at the `okf` skill.

The bundle path is `$ARGUMENTS` (default: the project root `.`).

Do the following:

1. Create the `.okf/` directory at the project root if it does not exist, then
   write the sentinel file `.okf/active`. Its contents should record the
   activation date (today) and the bundle path, for example:

   ```
   activated: <today's date, YYYY-MM-DD>
   bundle: <bundle-path or .>
   ```

2. If the bundle does not yet have `concepts/`, `index.md`, or `log.md`, tell the
   user they can initialize them with `/okf:reindex` (creates `index.md`) and
   `/okf:log` (creates `log.md`). Do not fabricate concepts.

3. Optionally, if a project `CLAUDE.md` exists, offer to append a single
   human-readable line noting that OKF is active and pointing at the bundle.
   Only do this with the user's agreement.

4. Confirm activation and remind the user that the gate runs at session start —
   they should start a new session (or `/clear`) for the OKF pointer to be
   injected automatically.

Writing `.okf/active` is the only state change required; keep the action minimal.
