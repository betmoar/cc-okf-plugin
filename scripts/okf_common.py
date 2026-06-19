#!/usr/bin/env python3
"""Shared OKF helpers: frontmatter parsing, wiki-link extraction, and the
surgical `links:` splicer. Imported by validate/reindex/rename/query.

Python 3.8+ stdlib only. PyYAML used when present (and OKF_NO_YAML unset);
built-in fallback parser otherwise.
"""
from __future__ import annotations

import os
import re

WIKILINK_RE = re.compile(r"\[\[([a-z0-9][a-z0-9-]*)\]\]")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _coerce(val: str):
    val = val.strip()
    if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
        return val[1:-1]
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        return [_coerce(x) for x in inner.split(",")] if inner else []
    return val


def _fallback_parse(block: str) -> dict:
    data: dict = {}
    lines = block.split("\n")
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if not line[0].isspace() and ":" in line:
            key, _, rest = line.partition(":")
            key, rest = key.strip(), rest.strip()
            if rest:
                data[key] = _coerce(rest)
                i += 1
                continue
            items: list = []
            i += 1
            while i < n and (not lines[i].strip() or lines[i][0].isspace()):
                cur = lines[i]
                if not cur.strip():
                    i += 1
                    continue
                stripped = cur.strip()
                if stripped.startswith("- "):
                    item = stripped[2:].strip()
                    if ":" in item and not item.startswith("["):
                        k2, _, v2 = item.partition(":")
                        items.append({k2.strip(): _coerce(v2)})
                    else:
                        items.append(_coerce(item))
                i += 1
            data[key] = items
        else:
            i += 1
    return data


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip("\n")
    if not os.environ.get("OKF_NO_YAML"):
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(block)
            return data if isinstance(data, dict) else {}
        except Exception:
            pass
    return _fallback_parse(block)


def body_of(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 1)
            return text[nl + 1 :] if nl != -1 else ""
    return text


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def extract_wikilinks(body: str) -> list:
    seen: list = []
    for m in WIKILINK_RE.finditer(body):
        wid = m.group(1)
        if wid not in seen:
            seen.append(wid)
    return seen


def _fm_lines(text: str):
    """Split a file into (head, fm_lines, tail) where head is '---' (the open
    delimiter), fm_lines are the inner frontmatter lines, and tail is the list
    of lines from the closing '---' onward. Returns None if no frontmatter."""
    if not text.startswith("---"):
        return None
    lines = text.split("\n")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[0], lines[1:i], lines[i:]
    return None


def splice_links(text: str, links: list) -> str:
    """Replace ONLY the `links:` field in the frontmatter. Every other byte is
    preserved (split/join on '\\n' is a lossless round-trip). Empty links -> the
    field is removed."""
    parts = _fm_lines(text)
    if parts is None:
        return text
    head, fm, tail = parts
    new_fm: list = []
    insert_at = None
    i = 0
    while i < len(fm):
        line = fm[i]
        if not line[:1].isspace() and re.match(r"^links\s*:", line):
            insert_at = len(new_fm)
            i += 1
            # Consume EVERY indented continuation line belonging to links:
            # — block items (`  - x`) AND comments (`  # ...`). Stop at the next
            # top-level key (column 0) or a blank line, so separator blanks and
            # following fields are preserved. (Spec §A: comments are not kept;
            # the field is regenerated wholesale.)
            while i < len(fm) and fm[i][:1].isspace():
                i += 1
            continue
        new_fm.append(line)
        i += 1
    if links:
        link_line = "links: [" + ", ".join(links) + "]"
        if insert_at is None:
            new_fm.append(link_line)
        else:
            new_fm.insert(insert_at, link_line)
    return "\n".join([head] + new_fm + tail)


def set_id(text: str, new_id: str) -> str:
    """Rewrite the top-level `id:` field in the frontmatter."""
    parts = _fm_lines(text)
    if parts is None:
        return text
    head, fm, tail = parts
    out = []
    for line in fm:
        if not line[:1].isspace() and re.match(r"^id\s*:", line):
            out.append(f"id: {new_id}")
        else:
            out.append(line)
    return "\n".join([head] + out + tail)
