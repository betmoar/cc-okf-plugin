#!/usr/bin/env python3
"""OKF concept rename — link-aware and recoverable.

All KNOWLEDGE writes (body [[old]]->[[new]] rewrites, the id: change, links:
regeneration) happen while concepts/<old>.md still exists, so an interruption
there is completable by simply re-running the command (every step is idempotent
and pre-flight tolerates the id-already-new resume state). The file rename
(os.rename, a single atomic POSIX syscall) is the last hard mutation; the only
step after it is rebuilding index.md, which is regenerable — if that is
interrupted, `/cc-okf:reindex` repairs it.

Usage:
    python3 rename.py <old-id> <new-id> [bundle-path]
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okf_common as oc  # noqa: E402
import reindex  # noqa: E402


def _concept_path(bundle: str, cid: str) -> str:
    return os.path.join(bundle, "concepts", f"{cid}.md")


def rewrite_bodies(bundle: str, old_id: str, new_id: str) -> None:
    """Step 2: literal [[old]] -> [[new]] across every concept file. Idempotent
    (already-rewritten files are no-ops). Token-exact: the bracketed form means
    [[old-v2]] is untouched."""
    cdir = os.path.join(bundle, "concepts")
    if not os.path.isdir(cdir):
        return
    needle, repl = f"[[{old_id}]]", f"[[{new_id}]]"
    for fname in sorted(f for f in os.listdir(cdir) if f.endswith(".md")):
        path = os.path.join(cdir, fname)
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        if needle in text:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text.replace(needle, repl))


def rename(bundle: str, old_id: str, new_id: str) -> int:
    bundle = os.path.abspath(os.path.expanduser(bundle))
    old_path, new_path = _concept_path(bundle, old_id), _concept_path(bundle, new_id)

    # 1. Pre-flight (no writes until all pass)
    if old_id == new_id:
        print("OKF rename: old-id and new-id are identical; nothing to do.", file=sys.stderr)
        return 2
    if not oc.ID_RE.match(new_id):
        print(f"OKF rename: new-id '{new_id}' is not kebab-case.", file=sys.stderr)
        return 2
    if not os.path.isfile(old_path):
        print(f"OKF rename: source concept '{old_id}' not found.", file=sys.stderr)
        return 2
    if os.path.isfile(new_path):
        print(f"OKF rename: target '{new_id}' already exists (collision).", file=sys.stderr)
        return 2
    with open(old_path, "r", encoding="utf-8") as fh:
        old_fm = oc.parse_frontmatter(fh.read()) or {}
    fid = str(old_fm.get("id") or old_id)
    # Tolerate the resume state: a partially-completed rename has already set
    # id to new_id while the file is still named <old_id>.md. Refuse only a
    # genuine mismatch (id is neither the old nor the new id).
    if fid not in (old_id, new_id):
        print(f"OKF rename: {old_id}.md has id '{fid}' (filename/id mismatch); "
              f"fix it before renaming.", file=sys.stderr)
        return 2

    # 2. Rewrite bodies [[old]] -> [[new]] everywhere (incl. old file). Idempotent.
    rewrite_bodies(bundle, old_id, new_id)

    # 3. Rewrite the id: field inside the still-old-named file. Idempotent.
    with open(old_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    with open(old_path, "w", encoding="utf-8") as fh:
        fh.write(oc.set_id(text, new_id))

    # 4. Regenerate links: in every concept (a KNOWLEDGE write) while <old>.md
    #    still exists, so an interruption here is completable by re-running.
    reindex.regenerate_links(bundle, dry_run=False)

    # 5. LAST hard mutation, atomic: rename the file.
    os.rename(old_path, new_path)

    # 6. Rebuild index.md AFTER the rename so its rows point at <new>.md. This is
    #    regenerable: if it is interrupted, `/cc-okf:reindex` repairs the index.
    reindex.rebuild_index(bundle, dry_run=False)

    print(f"OKF rename — '{old_id}' -> '{new_id}'. Run /cc-okf:log to record it.")
    return 0


def main(argv: list) -> int:
    args = [a for a in argv[1:] if a.strip()]
    if len(args) < 2:
        print("Usage: rename.py <old-id> <new-id> [bundle-path]", file=sys.stderr)
        return 2
    old_id, new_id = args[0], args[1]
    bundle = args[2] if len(args) > 2 else "."
    return rename(bundle, old_id, new_id)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
