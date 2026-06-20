"""Helpers to build a throwaway OKF bundle on disk for tests."""
import os
import tempfile


def write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def make_bundle(concepts: dict) -> str:
    """concepts maps filename-stem -> full file text. Returns bundle path."""
    bundle = tempfile.mkdtemp(prefix="okf_test_")
    cdir = os.path.join(bundle, "concepts")
    os.makedirs(cdir, exist_ok=True)
    for stem, text in concepts.items():
        write(os.path.join(cdir, f"{stem}.md"), text)
    write(os.path.join(bundle, "log.md"), "# Log\n")
    write(os.path.join(bundle, "index.md"), "# Index\n")
    return bundle


def concept(cid, body, links_line=None, ctype="concept", status=None,
            tags=None, extra_fm="", title=True):
    """Build concept text. Each field has a clean override so callers never emit
    duplicate keys. links_line is a raw frontmatter line (or None) for tests that
    need to seed a specific links: form. Pass title=False to omit the title: line
    entirely (produces a concept with only the required id/type fields plus dates)."""
    fm = [f"id: {cid}"]
    if title:
        fm.append(f"title: {cid.title()}")
    fm += [f"type: {ctype}", "created: 2026-06-01", "updated: 2026-06-01"]
    if status is not None:
        fm.append(f"status: {status}")
    if tags is not None:
        fm.append("tags: [" + ", ".join(tags) + "]")
    if extra_fm:
        fm.append(extra_fm)
    if links_line is not None:
        fm.append(links_line)
    return "---\n" + "\n".join(fm) + "\n---\n\n" + body + "\n"
