# tests/test_rename.py
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "scripts"))
sys.path.insert(0, _HERE)  # tests/ — so `import okf_test_util` resolves
import rename  # noqa: E402
from okf_test_util import make_bundle, concept  # noqa: E402


def read(bundle, stem):
    with open(os.path.join(bundle, "concepts", f"{stem}.md"), encoding="utf-8") as fh:
        return fh.read()


def exists(bundle, stem):
    return os.path.isfile(os.path.join(bundle, "concepts", f"{stem}.md"))


class TestRename(unittest.TestCase):
    def test_happy_path(self):
        b = make_bundle({
            "old": concept("old", "I am old"),
            "ref": concept("ref", "points to [[old]] here"),
        })
        rc = rename.rename(b, "old", "new")
        self.assertEqual(rc, 0)
        self.assertTrue(exists(b, "new"))
        self.assertFalse(exists(b, "old"))
        self.assertIn("id: new", read(b, "new"))
        self.assertIn("[[new]]", read(b, "ref"))
        self.assertNotIn("[[old]]", read(b, "ref"))

    def test_token_exact(self):
        b = make_bundle({
            "old": concept("old", "x"),
            "ref": concept("ref", "[[old-v2]] stays, [[old]] changes"),
        })
        rename.rename(b, "old", "new")
        self.assertIn("[[old-v2]]", read(b, "ref"))
        self.assertIn("[[new]]", read(b, "ref"))

    def test_collision_refused_no_write(self):
        b = make_bundle({"old": concept("old", "x"), "new": concept("new", "y")})
        before = read(b, "old")
        rc = rename.rename(b, "old", "new")
        self.assertNotEqual(rc, 0)
        self.assertEqual(before, read(b, "old"))  # untouched

    def test_missing_source_refused(self):
        b = make_bundle({"a": concept("a", "x")})
        self.assertNotEqual(rename.rename(b, "ghost", "new"), 0)

    def test_bad_new_id_refused(self):
        b = make_bundle({"old": concept("old", "x")})
        self.assertNotEqual(rename.rename(b, "old", "Bad ID"), 0)

    def test_recovery_after_crash_before_final_rename(self):
        # Simulate crash: run steps 2-4 (rewrite bodies, set id, reindex) but
        # NOT the final os.rename, then re-invoke rename and assert clean state.
        b = make_bundle({
            "old": concept("old", "self [[old]]"),
            "ref": concept("ref", "[[old]]"),
        })
        rename.rewrite_bodies(b, "old", "new")  # step 2 only
        # old file still present, bodies now say [[new]] -> partial state
        self.assertTrue(exists(b, "old"))
        rc = rename.rename(b, "old", "new")  # re-run completes
        self.assertEqual(rc, 0)
        self.assertTrue(exists(b, "new"))
        self.assertFalse(exists(b, "old"))
        self.assertIn("[[new]]", read(b, "ref"))
        self.assertNotIn("[[old]]", read(b, "ref"))

    def test_referrer_links_and_index_regenerated(self):
        # Spec §B step 4: rename runs reindex, so referrers' links: and index.md
        # reflect the new id.
        b = make_bundle({
            "old": concept("old", "x"),
            "ref": concept("ref", "points [[old]]"),
        })
        rename.rename(b, "old", "new")
        self.assertIn("links: [new]", read(b, "ref"))
        with open(os.path.join(b, "index.md"), encoding="utf-8") as fh:
            idx = fh.read()
        self.assertIn("`new`", idx)
        self.assertNotIn("`old`", idx)
        self.assertIn("concepts/new.md", idx)  # index path points at the new file
        self.assertNotIn("concepts/old.md", idx)

    def test_id_filename_mismatch_refused(self):
        # frontmatter id: must match the filename stem being renamed.
        b = make_bundle({"wrongname": concept("actual-id", "x")})
        rc = rename.rename(b, "wrongname", "new")
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
