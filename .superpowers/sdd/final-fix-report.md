# Final Fix Report — OKF v0.2 Review Wave

## Fix 1 (Important): validate stale-links uses byte predicate

**File:** `scripts/validate.py`

**Before** (lines 104-105, cross-link loop):
```python
parsed[cid] = {"fm": fm, "body": oc.body_of(text), "scope": scope}
...
fm_links = [str(x) for x in oc._as_list(fm.get("links"))]
if fm_links != body_links:
    warn(scope, "links: is out of date with the body (run /okf:reindex)")
```

**After** (`parsed` dict now carries raw `text`; comparison uses `splice_links`):
```python
parsed[cid] = {"fm": fm, "body": oc.body_of(text), "scope": scope, "text": text}
...
if oc.splice_links(info["text"], body_links) != info["text"]:
    warn(scope, "links: is out of date with the body (run /okf:reindex)")
```

**New test** (`tests/test_validate.py`, `test_block_links_matching_body_triggers_stale_warn`):
```python
def test_block_links_matching_body_triggers_stale_warn(self):
    # Block-form `links:\n  - b` matches the body [[b]] when parsed as a list,
    # but reindex would reformat it to inline `links: [b]`. Validate must now
    # use the byte predicate (splice_links != text) and therefore WARN here.
    block_links = "links:\n  - b"
    b = make_bundle({
        "a": concept("a", "see [[b]]", extra_fm=block_links),
        "b": concept("b", "leaf"),
    })
    _, warnings, _ = validate.validate_bundle(b)
    self.assertTrue(
        any("links" in w.lower() for w in warnings),
        f"expected stale-links WARN for block-form links:; got warnings={warnings}",
    )
```

All existing validate tests pass unchanged. The new test catches the exact scenario where parsed-list equality would miss a reformat.

---

## Fix 2 (Important): document CRLF as a known limitation

**File:** `skills/okf/references/spec.md`

Added a "Known limitations" subsection (after the Migration notice in §5, adjacent to the code-fence limitation which was documented at the same time):

```markdown
### Known limitations

**Code fences are not parsed.** `WIKILINK_RE` matches `[[id]]` even inside
fenced code blocks. Under v0.2 such a token is treated as a real link (it
populates `links:`, and a dangling one is an ERROR). Avoid `[[…]]` inside code
samples or escape it. Proper fence-aware extraction is a v0.3 item.

**CRLF line endings are normalized on rewrite.** Concept files with CRLF
(`\r\n`) line endings are normalized to LF when `/okf:reindex` rewrites a
file's `links:` field (text-mode I/O + `split("\n")` join). Files whose `links:`
does not change are left byte-identical.
```

**File:** `CHANGELOG.md`

Added bullet under `0.2.0`:
```
- Known limitation: a concept file's CRLF line endings are normalized to LF when reindex rewrites its `links:` field.
```

No code changes; documentation only.

---

## Fix 3 (Minor): README "What's inside" table updated

**File:** `README.md`

Changes to the component table:
- `/okf:reindex` description updated: now notes it regenerates each concept's `links:` from body `[[id]]` wiki-links AND supports `--dry-run`.
- Added row: `/okf:rename` (`commands/rename.md`) — rename a concept, rewriting every cross-link.
- Added row: `/okf:query` (`commands/query.md`) — find concepts by tag/type/status/text.
- Scripts row updated: `okf_common.py`, `rename.py`, `query.py` added alongside existing scripts.

---

## Fix 4 (Minor): clean migration-notice output for dict-form links

**File:** `scripts/reindex.py`

**Before** (in `regenerate_links`):
```python
old_links = [str(x) for x in oc._as_list(old_fm.get("links"))]
```
Dict-form `{id: foo}` stringified as `{'id': 'foo'}` in the dropped notice AND in the subset check — so `{id: foo}` was never matched against body string `"foo"`, causing false "dropped" notices.

**After** (new helper + usage):
```python
def _link_id(entry) -> str:
    """Extract a clean string id from a links: entry (dict-form or plain string)."""
    if isinstance(entry, dict):
        return str(entry.get("id", entry))
    return str(entry)

...
old_links = [_link_id(x) for x in oc._as_list(old_fm.get("links"))]
```

Clean ids are now used for both the subset check and the printed notice. A dict-form `{id: foo}` whose body has `[[foo]]` is no longer reported as dropped.

---

## Fix 5 (doc record): correct plan design note

**File:** `docs/plans/2026-06-19-okf-v0.2.md`

**Before:**
> the stale-`links:` check (Task 3) uses **list** (order-sensitive) comparison, not set. Reindex generates `links:` in body first-appearance order, so order is canonical; list comparison makes validate WARN *exactly when* reindex would rewrite the file. Set comparison was rejected — it would call a file clean that reindex then mutates. // DECISION: keep list comparison.

**After:**
> the stale-`links:` check uses the **byte-level predicate** `splice_links(text, body_links) != text` — the same one reindex uses — which is what truly makes the two agree. The earlier list-comparison approach was wrong: parsed-list equality ignores formatting (block vs. inline, `links: []` vs. absent) that reindex would still rewrite, so validate would call a file "clean" that reindex then mutates. // DECISION: byte predicate via splice_links.

---

## Test Results

### PyYAML parser path
```
Ran 41 tests in 0.089s
OK
```

### Fallback parser path (OKF_NO_YAML=1)
```
Ran 41 tests in 0.051s
OK
```

New test `test_block_links_matching_body_triggers_stale_warn` present and passing in both runs. Baseline was 40 tests; now 41 (net +1). No warnings, pristine output (expected stderr from rename refusals is test-internal).
