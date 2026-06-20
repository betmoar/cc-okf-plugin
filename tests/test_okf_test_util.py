"""Tests for the okf_test_util.concept() helper."""
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "scripts"))
sys.path.insert(0, _HERE)
import okf_common as oc  # noqa: E402
from okf_test_util import concept  # noqa: E402


class TestConceptHelper(unittest.TestCase):
    def test_default_title_present(self):
        text = concept("foo", "body text")
        self.assertIn("title: Foo", text)

    def test_title_false_omits_title(self):
        text = concept("foo", "body text", title=False)
        self.assertNotIn("title:", text)

    def test_title_false_still_parseable(self):
        text = concept("foo", "body text", title=False)
        fm = oc.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm["id"], "foo")
        self.assertEqual(fm["type"], "concept")
        self.assertNotIn("title", fm)

    def test_title_true_still_parseable(self):
        text = concept("bar", "body", title=True)
        fm = oc.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm["title"], "Bar")


if __name__ == "__main__":
    unittest.main()
