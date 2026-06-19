#!/usr/bin/env python3
"""OKF conformance validator.

Checks an Open Knowledge Format (OKF) bundle against the OKF v0.1 conformance
rules (see skills/okf/references/conformance.md). Prints a report grouped by
concept and exits non-zero if any ERROR-level violations are found.

Usage:
    python3 validate.py [bundle-path]      # default: current directory

Dependencies: Python 3.8+ standard library only. PyYAML is used for frontmatter
parsing when available, with a built-in fallback parser for the OKF subset.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okf_common as oc  # noqa: E402

ALLOWED_TYPES = {"concept", "decision", "reference", "glossary"}
ALLOWED_STATUS = {"draft", "review", "stable", "deprecated"}
REQUIRED_FIELDS = ("id", "title", "type", "created", "updated")
# Matches the first cell of a generated index row, tolerating the markdown-link
# form `| [`id`](concepts/id.md) |`, a bare `| `id` |`, or a plain `| id |`.
INDEX_ROW_RE = re.compile(r"^\|\s*\[?`?([a-z0-9][a-z0-9-]*)`?", re.MULTILINE)


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def _is_iso_date(value) -> bool:
    if not isinstance(value, str):
        value = str(value)
    try:
        _dt.date.fromisoformat(value.strip())
        return True
    except ValueError:
        return False


def validate_bundle(bundle: str):
    errors: list[str] = []
    warnings: list[str] = []

    def err(scope, msg):
        errors.append(f"[ERROR] {scope}: {msg}")

    def warn(scope, msg):
        warnings.append(f"[WARN]  {scope}: {msg}")

    index_path = os.path.join(bundle, "index.md")
    log_path = os.path.join(bundle, "log.md")
    concepts_dir = os.path.join(bundle, "concepts")

    if not os.path.isfile(index_path):
        err("bundle", "missing index.md at bundle root (run /okf:reindex)")
    if not os.path.isfile(log_path):
        err("bundle", "missing log.md at bundle root (run /okf:log)")

    if not os.path.isdir(concepts_dir):
        warn("bundle", "no concepts/ directory found; bundle has no concepts yet")
        concept_files: list[str] = []
    else:
        concept_files = sorted(
            f for f in os.listdir(concepts_dir) if f.endswith(".md")
        )
        if not concept_files:
            warn("concepts/", "directory is empty; bundle has no concepts yet")

    ids: dict[str, str] = {}
    parsed: dict[str, dict] = {}

    for fname in concept_files:
        scope = f"concepts/{fname}"
        path = os.path.join(concepts_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            err(scope, f"cannot read file: {exc}")
            continue

        fm = oc.parse_frontmatter(text)
        if fm is None:
            err(scope, "missing YAML frontmatter block (--- ... ---)")
            continue

        for field in REQUIRED_FIELDS:
            if not fm.get(field):
                err(scope, f"missing required frontmatter field: {field}")

        cid = fm.get("id")
        stem = fname[:-3]
        if cid:
            if cid != stem:
                err(scope, f"id '{cid}' does not match filename stem '{stem}'")
            if cid in ids:
                err(scope, f"duplicate id '{cid}' (also in {ids[cid]})")
            else:
                ids[cid] = scope
            parsed[cid] = {"fm": fm, "body": oc.body_of(text), "scope": scope}

        ctype = fm.get("type")
        if ctype and ctype not in ALLOWED_TYPES:
            err(scope, f"type '{ctype}' not in {sorted(ALLOWED_TYPES)}")

        status = fm.get("status")
        if status and status not in ALLOWED_STATUS:
            err(scope, f"status '{status}' not in {sorted(ALLOWED_STATUS)}")

        created, updated = fm.get("created"), fm.get("updated")
        if created and not _is_iso_date(created):
            err(scope, f"created '{created}' is not an ISO date (YYYY-MM-DD)")
        if updated and not _is_iso_date(updated):
            err(scope, f"updated '{updated}' is not an ISO date (YYYY-MM-DD)")
        if created and updated and _is_iso_date(created) and _is_iso_date(updated):
            if str(updated).strip() < str(created).strip():
                err(scope, f"updated ({updated}) is before created ({created})")

        for src in oc._as_list(fm.get("sources")):
            if isinstance(src, dict):
                if not src.get("title"):
                    warn(scope, "a source is missing a 'title'")
                url = src.get("url")
                if url and not re.match(r"^https?://", str(url)):
                    warn(scope, f"source url '{url}' is not http(s)")
            elif isinstance(src, str):
                if not src.strip():
                    warn(scope, "empty source entry")

    # Cross-link integrity. Body [[id]] is the source of truth (ERROR on
    # dangling). Frontmatter links: is generated — flag it only as stale (WARN).
    for cid, info in parsed.items():
        fm, body, scope = info["fm"], info["body"], info["scope"]
        body_links = oc.extract_wikilinks(body)
        for tid in body_links:
            if tid not in ids:
                err(scope, f"wiki-link [[{tid}]] does not resolve to a concept")
        fm_links = [str(x) for x in oc._as_list(fm.get("links"))]
        if fm_links != body_links:
            warn(scope, "links: is out of date with the body (run /okf:reindex)")

    # index.md freshness (advisory only — /okf:reindex is the source of truth).
    if os.path.isfile(index_path) and ids:
        try:
            with open(index_path, "r", encoding="utf-8") as fh:
                index_text = fh.read()
        except OSError:
            index_text = ""
        indexed = {m.group(1) for m in INDEX_ROW_RE.finditer(index_text)}
        missing = set(ids) - indexed
        stale = indexed - set(ids)
        if missing:
            warn("index.md", f"missing concepts {sorted(missing)} (run /okf:reindex)")
        if stale:
            warn("index.md", f"lists unknown ids {sorted(stale)} (run /okf:reindex)")

    return errors, warnings, len(concept_files)


def main(argv: list[str]) -> int:
    bundle = (argv[1] if len(argv) > 1 and argv[1].strip() else ".").strip()
    bundle = os.path.abspath(os.path.expanduser(bundle))
    if not os.path.isdir(bundle):
        print(f"OKF: bundle path is not a directory: {bundle}", file=sys.stderr)
        return 2

    errors, warnings, n = validate_bundle(bundle)

    print(f"OKF validation — bundle: {bundle}")
    print(f"Concepts examined: {n}")
    print("-" * 60)
    for line in warnings:
        print(line)
    for line in errors:
        print(line)
    print("-" * 60)
    print(f"Result: {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        print("FAIL: bundle is not OKF-conformant.")
        return 1
    print("PASS: bundle is OKF-conformant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
