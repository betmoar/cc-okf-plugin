#!/usr/bin/env python3
"""OKF concept query — filter by tag/type/status/text (AND-combined).

Usage:
    python3 query.py [--tag T] [--type Y] [--status S] [--text STR] [bundle-path]
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okf_common as oc  # noqa: E402


def query(bundle, tag=None, type=None, status=None, text=None) -> list:
    bundle = os.path.abspath(os.path.expanduser(bundle))
    cdir = os.path.join(bundle, "concepts")
    rows = []
    if not os.path.isdir(cdir):
        return rows
    needle = text.lower() if text else None
    for fname in sorted(f for f in os.listdir(cdir) if f.endswith(".md")):
        path = os.path.join(cdir, fname)
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
        fm = oc.parse_frontmatter(raw) or {}
        tags = [str(t) for t in oc._as_list(fm.get("tags"))]
        if tag and tag not in tags:
            continue
        if type and str(fm.get("type") or "") != type:
            continue
        if status and str(fm.get("status") or "") != status:
            continue
        if needle:
            hay = (str(fm.get("title") or "") + "\n" + oc.body_of(raw)).lower()
            if needle not in hay:
                continue
        rows.append({
            "id": str(fm.get("id") or fname[:-3]),
            "title": str(fm.get("title") or fname[:-3]),
            "type": str(fm.get("type") or ""),
            "status": str(fm.get("status") or ""),
            "tags": ", ".join(tags),
            "file": f"concepts/{fname}",
        })
    rows.sort(key=lambda r: (r["type"], r["id"]))
    return rows


def main(argv: list) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="query.py")
    p.add_argument("bundle", nargs="?", default=".")
    p.add_argument("--tag")
    p.add_argument("--type")
    p.add_argument("--status")
    p.add_argument("--text")
    ns = p.parse_args(argv[1:])
    rows = query(ns.bundle, tag=ns.tag, type=ns.type, status=ns.status, text=ns.text)
    print(f"OKF query — {len(rows)} match(es).")
    for r in rows:
        tags = f"  [{r['tags']}]" if r["tags"] else ""
        print(f"  {r['id']}  ({r['type']}/{r['status'] or '—'})  {r['title']}{tags}  {r['file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
