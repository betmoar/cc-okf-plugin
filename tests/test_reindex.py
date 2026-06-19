# tests/test_reindex.py
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
    def test_generates_links_from_body(self):
        b = make_bundle({
            "a": concept("a", "links to [[b]]"),
            "b": concept("b", "leaf node"),
        })
        reindex.run(b)
        self.assertIn("links: [b]", read(b, "a"))
        self.assertNotIn("links:", read(b, "b"))  # no body links -> omitted

    def test_idempotent_no_rewrite(self):
        b = make_bundle({"a": concept("a", "[[b]]"), "b": concept("b", "x")})
        reindex.run(b)
        first = read(b, "a")
        reindex.run(b)
        self.assertEqual(first, read(b, "a"))  # byte-identical second run

    def test_dry_run_writes_nothing(self):
        b = make_bundle({"a": concept("a", "[[b]]"), "b": concept("b", "x")})
        before = read(b, "a")
        reindex.run(b, dry_run=True)
        self.assertEqual(before, read(b, "a"))

    def test_migration_notice_for_dropped_links(self):
        # hand-authored links: [ghost] with no body [[ghost]] -> dropped + notice
        b = make_bundle({"a": concept("a", "no links here", links_line="links: [ghost]")})
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            reindex.run(b)
        self.assertIn("ghost", buf.getvalue())
        self.assertNotIn("links:", read(b, "a"))

    def test_rebuilds_index(self):
        # Spec §A: reindex's second responsibility is the index.md table.
        b = make_bundle({"a": concept("a", "[[b]]"), "b": concept("b", "leaf")})
        reindex.run(b)
        with open(os.path.join(b, "index.md"), encoding="utf-8") as fh:
            idx = fh.read()
        self.assertIn("[`a`](concepts/a.md)", idx)
        self.assertIn("[`b`](concepts/b.md)", idx)
        self.assertIn("OKF:INDEX:BEGIN", idx)


if __name__ == "__main__":
    unittest.main()
