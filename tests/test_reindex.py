# tests/test_reindex.py
import contextlib
import io
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "scripts"))
sys.path.insert(0, _HERE)  # tests/ — so `import okf_test_util` resolves
import reindex  # noqa: E402
from okf_test_util import make_bundle, concept  # noqa: E402


def read(bundle, stem):
    with open(os.path.join(bundle, "concepts", f"{stem}.md"), encoding="utf-8") as fh:
        return fh.read()


class TestReindex(unittest.TestCase):
    def test_reindex_strips_links_field(self):
        # §4: reindex must remove any existing links: line (not regenerate it).
        b = make_bundle({
            "a": concept("a", "links to [[b]]"),
            "b": concept("b", "leaf node"),
        })
        reindex.run(b)
        self.assertNotIn("links:", read(b, "a"))
        self.assertNotIn("links:", read(b, "b"))

    def test_idempotent_no_rewrite(self):
        b = make_bundle({"a": concept("a", "[[b]]"), "b": concept("b", "x")})
        reindex.run(b)
        first = read(b, "a")
        reindex.run(b)
        self.assertEqual(first, read(b, "a"))  # byte-identical second run

    def test_dry_run_writes_nothing(self):
        b = make_bundle({"a": concept("a", "[[b]]"), "b": concept("b", "x")})
        before = read(b, "a")
        with open(os.path.join(b, "index.md"), encoding="utf-8") as fh:
            index_before = fh.read()
        reindex.run(b, dry_run=True)
        self.assertEqual(before, read(b, "a"))
        with open(os.path.join(b, "index.md"), encoding="utf-8") as fh:
            index_after = fh.read()
        self.assertEqual(index_before, index_after)

    def test_links_field_strip_notice(self):
        # §4: when reindex strips an existing links: field, it prints the migration notice.
        b = make_bundle({"a": concept("a", "body links [[b]]", links_line="links: [x, y]"),
                         "b": concept("b", "leaf")})
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            reindex.run(b)
        output = buf.getvalue()
        self.assertIn("removed deprecated", output.lower())
        self.assertNotIn("links:", read(b, "a"))

    def test_reindex_strips_links_idempotent(self):
        # §4: second reindex run on already-stripped bundle is a no-op (no notice printed,
        # file content identical).
        b = make_bundle({"a": concept("a", "body with [[b]]", links_line="links: [b]"),
                         "b": concept("b", "leaf")})
        reindex.run(b)
        after_first = read(b, "a")
        self.assertNotIn("links:", after_first)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            reindex.run(b)
        after_second = read(b, "a")
        self.assertEqual(after_first, after_second, "second run should be a no-op")
        # The migration notice should NOT appear on the second run (no links: to strip)
        self.assertNotIn("removed deprecated", buf.getvalue().lower())

    def test_rebuilds_index(self):
        # Spec §A: reindex's second responsibility is the index.md table.
        b = make_bundle({"a": concept("a", "[[b]]"), "b": concept("b", "leaf")})
        reindex.run(b)
        with open(os.path.join(b, "index.md"), encoding="utf-8") as fh:
            idx = fh.read()
        self.assertIn("[`a`](concepts/a.md)", idx)
        self.assertIn("[`b`](concepts/b.md)", idx)
        self.assertIn("OKF:INDEX:BEGIN", idx)

    def test_title_fallback_to_stem(self):
        # §2: when title: is absent, index row should show the stem, not blank.
        b = make_bundle({"my-concept": concept("my-concept", "body", title=False)})
        reindex.run(b)
        rows = reindex.collect_concepts(os.path.join(b, "concepts"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "my-concept")


if __name__ == "__main__":
    unittest.main()
