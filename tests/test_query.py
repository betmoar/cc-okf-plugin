# tests/test_query.py
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "scripts"))
sys.path.insert(0, _HERE)  # tests/ — so `import okf_test_util` resolves
import query  # noqa: E402
from okf_test_util import make_bundle, concept  # noqa: E402


class TestQuery(unittest.TestCase):
    def setUp(self):
        self.b = make_bundle({
            "a": concept("a", "alpha body", tags=["x", "y"]),
            "b": concept("b", "beta body", status="stable"),
            "c": concept("c", "gamma body", ctype="decision"),
        })

    def ids(self, rows):
        return sorted(r["id"] for r in rows)

    def test_tag_filter(self):
        self.assertEqual(self.ids(query.query(self.b, tag="x")), ["a"])

    def test_type_filter(self):
        self.assertEqual(self.ids(query.query(self.b, type="decision")), ["c"])

    def test_status_filter(self):
        self.assertEqual(self.ids(query.query(self.b, status="stable")), ["b"])

    def test_text_filter_case_insensitive(self):
        self.assertEqual(self.ids(query.query(self.b, text="BETA")), ["b"])

    def test_and_combination(self):
        # type=concept AND text=alpha -> only a
        self.assertEqual(self.ids(query.query(self.b, type="concept", text="alpha")), ["a"])

    def test_empty_result(self):
        self.assertEqual(query.query(self.b, tag="nope"), [])

    def test_title_fallback_to_stem(self):
        # §2: when title: is absent, query row should show the stem, not blank.
        b = make_bundle({"my-concept": concept("my-concept", "body", title=False)})
        rows = query.query(b)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "my-concept")


if __name__ == "__main__":
    unittest.main()
