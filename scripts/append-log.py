#!/usr/bin/env python3
"""OKF log appender.

Appends a structured, timestamped entry to an OKF bundle's log.md. The log is
append-only: entries are added in chronological order and existing content is
never rewritten. Creates log.md with a header if it does not yet exist.

Usage:
    python3 append-log.py [--bundle PATH] [--action ACTION] MESSAGE...

    --bundle PATH    Bundle root (default: current directory).
    --action ACTION  Short verb categorizing the entry, e.g. add, update,
                     remove, reindex, note (default: note).
    MESSAGE          The log message (remaining args are joined with spaces).

Entry format:
    ## 2026-06-19T13:58:00Z — <action>
    <message>

Dependencies: Python 3.8+ standard library only.
"""
from __future__ import annotations

import datetime as _dt
import os
import sys

HEADER = "# Log\n\n<!-- OKF:LOG (append-only; managed by /okf:log) -->\n"


def parse_args(argv: list[str]):
    bundle = "."
    action = "note"
    message_parts: list[str] = []
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--bundle" and i + 1 < len(argv):
            bundle = argv[i + 1]
            i += 2
        elif arg == "--action" and i + 1 < len(argv):
            action = argv[i + 1]
            i += 2
        else:
            message_parts.append(arg)
            i += 1
    return bundle, action, " ".join(message_parts).strip()


def main(argv: list[str]) -> int:
    bundle, action, message = parse_args(argv)
    if not message:
        print(
            'OKF: no log message given.\n'
            'Usage: append-log.py [--bundle PATH] [--action ACTION] MESSAGE...',
            file=sys.stderr,
        )
        return 2

    bundle = os.path.abspath(os.path.expanduser(bundle.strip() or "."))
    if not os.path.isdir(bundle):
        print(f"OKF: bundle path is not a directory: {bundle}", file=sys.stderr)
        return 2

    log_path = os.path.join(bundle, "log.md")
    timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"\n## {timestamp} — {action}\n{message}\n"

    if not os.path.isfile(log_path):
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(HEADER)

    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(entry)

    print(f"OKF log — appended to {log_path}")
    print(f"  {timestamp} — {action}: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
