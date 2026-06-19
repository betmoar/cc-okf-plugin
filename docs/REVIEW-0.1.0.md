# OKF v0.1.0 — Honest Review

Internal critique of the shipped v0.1.0 plugin, recorded so v0.2 is driven by
evidence rather than momentum. Reviewer: Claude (Opus 4.8), grounded in a read of
`scripts/validate.py`, `scripts/reindex.py`, `scripts/okf-gate.sh`,
`hooks/hooks.json`, `skills/okf/SKILL.md`, and `README.md`. Confidence levels are
explicit; nothing here is verified against real-user telemetry.

Bottom line: **the engineering is clean and the architecture is right; the
product premise is the weak part.** This is a solid v0.1 with sound bones. The
work before v0.2 is mostly about *justifying the format's existence* and
*building the read path*, not about code quality.

---

## 1. The premise is thin (confidence: high)

Stripped to essentials, OKF is "a folder of markdown files with frontmatter, a
generated index, a changelog, and `[[wiki-links]]`." That is a Zettelkasten.
Obsidian, Foam, and Dendron already do this, parse `[[id]]` natively, and ship
mature retrieval/graph UIs.

The only defensible differentiator is **"an agent maintains it for you"** —
agent-native knowledge curation. But v0.1 doesn't lean into that. It invests
almost entirely in *conformance plumbing* (validate / reindex / log). And that
plumbing exists to automate bookkeeping **the format itself creates**: the
`id == filename` rule, the dual link representation, the hand-maintained index.
A format that needs a validator to stay internally consistent is generating the
very work its tooling then automates away. That is a design smell, not a feature.

**v0.2 ask:** Write the one-sentence answer to *"why not just Obsidian + git?"*
and make the plugin earn it. Likely answer: Claude curates, links, and dedupes
concepts as a side effect of normal work — so build *that*, not more linters.

## 2. The retrieval path is underbuilt (confidence: high)

The point of durable knowledge is **recall**. v0.1 ships `activate` / `validate`
/ `reindex` / `log` — all write/maintain operations — and **nothing for
querying**. No search, no "concepts tagged X," no graph traversal. `index.md` is
an alphabetized flat table; at 100+ concepts that is a phone book, not a map. The
skill says "prefer the index and log as the map," but in practice the read story
collapses to "Claude greps the folder."

**v0.2 ask:** Add a query/recall command (search by tag/type/text, follow the
link graph). The read path is the reason the write path exists.

## 3. The link graph is stored twice (confidence: high)

The same relationship lives in two places — inline `[[other-id]]` in the body
**and** `links: [other-id]` in frontmatter — and they can drift. The validator
treats them with **different severities**:

- dangling frontmatter `links:` target → **ERROR** (`validate.py:239`)
- dangling `[[wiki-link]]` → **WARN** (`validate.py:242`)

Same broken relationship, two verdicts. The validator already regexes wiki-links
(`WIKILINK_RE`), so the body is just as machine-readable as the frontmatter.

**v0.2 ask:** One source of truth. Either derive `links:` from the body at
reindex time, or drop `links:` and parse `[[…]]` everywhere. Align the severity.

## 4. Renames are a landmine with no tool (confidence: high)

`id` must equal the filename stem (`validate.py:198`). Renaming a concept
therefore means: rename the file → change `id` → update every referencing
`links:` → update every referencing `[[wiki-link]]` → reindex. For a store
that's meant to *evolve*, renames are routine, and there is no `/okf:rename` to
do this atomically.

**v0.2 ask:** Add `/okf:rename <old-id> <new-id>`. This is exactly the command
that would *justify* the format's "machine-readable link graph" claim — its
absence undercuts the pitch.

## 5. The activation gate is marketed as a feature but documented as flaky (confidence: moderate)

Dormant-by-default via the `.okf/active` sentinel + SessionStart gate is the
plugin's central value prop for global install. The README admits it can fail to
fire on fresh conversations ("start a fresh session or `/clear`"). If the gate is
unreliable, the dormancy story is shaky. This is the claim most likely to bite a
user. Not reproduced here — flagged from the README's own caveat.

**v0.2 ask:** Nail down gate-firing reliability across versions, or stop
marketing dormancy as a headline feature until it's deterministic.

## 6. Overlap with Claude Code's own memory system (confidence: moderate)

OKF is structurally near-identical to Claude Code's built-in memory store
(`~/.claude/.../memory/`): frontmatter, typed entries, `[[name]]` links, a
`MEMORY.md` index. The distinction — OKF is project-scoped knowledge committed to
the repo's git; memory is cross-session assistant memory — is real but narrow,
and the README never draws it.

**v0.2 ask:** State the distinction explicitly in the README so a user knows
when to reach for OKF vs. memory vs. Obsidian.

---

## What is genuinely good (keep these)

- **skill = knowledge / command = action / shared scripts** is the correct
  response to Claude Code's constraint that a skill cannot invoke a command.
- **Dormant-by-default** (sentinel + gate) is the right pattern for a global
  plugin — no token cost where unused. (Pending the reliability fix in §5.)
- The **validator is careful**: no hard PyYAML dependency (built-in fallback
  parser), and index freshness is advisory (WARN, not ERROR) because reindex is
  the source of truth. Good judgment.
- Code is **defensive and readable**. Note: the `updated < created` string
  compare (`validate.py:219`) is correct *only because* ISO format is validated
  immediately above — works, but fragile-looking; a future edit that reorders
  those checks would silently break it.

---

## Prioritized v0.2 backlog

1. **Kill the duplicate link representation** (§3) — one source of truth, aligned
   severity. Low effort, removes a whole class of drift bugs.
2. **Add `/okf:rename`** (§4) — makes the format's central claim true.
3. **Add a retrieval/query command** (§2) — build the read path.
4. **Fix or de-market the activation gate** (§5) — protect the core value prop.
5. **Write the "why not Obsidian / why not memory" paragraph** (§1, §6) — the
   positioning the whole thing currently lacks.

Items 1, 2, 5 are cheap and high-leverage. Item 3 is the real product work.
