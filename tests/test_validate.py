# tests/test_validate.py
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "scripts"))
sys.path.insert(0, _HERE)  # tests/ — so `import okf_test_util` resolves
import validate  # noqa: E402
from okf_test_util import make_bundle, concept  # noqa: E402


class TestValidate(unittest.TestCase):
    def test_dangling_body_wikilink_is_error(self):
        b = make_bundle({"a": concept("a", "points to [[ghost]]")})
        errors, warnings, _ = validate.validate_bundle(b)
        self.assertTrue(any("ghost" in e for e in errors))

    def test_stale_links_is_warning_not_error(self):
        # body links [b]; frontmatter links empty -> stale -> WARN, not ERROR
        b = make_bundle({
            "a": concept("a", "see [[b]]"),  # no links: line yet
            "b": concept("b", "leaf"),
        })
        errors, warnings, _ = validate.validate_bundle(b)
        self.assertFalse(any("a.md" in e for e in errors))
        self.assertTrue(any("links" in w.lower() for w in warnings))

    def test_clean_bundle_passes(self):
        b = make_bundle({
            "a": concept("a", "see [[b]]", links_line="links: [b]"),
            "b": concept("b", "leaf"),
        })
        errors, _, _ = validate.validate_bundle(b)
        self.assertEqual(errors, [])

    def test_required_field_check_survives_refactor(self):
        # id missing -> still an ERROR after the okf_common import swap.
        b = make_bundle({"a": "---\ntitle: A\ntype: concept\n"
                              "created: 2026-06-01\nupdated: 2026-06-01\n---\n\nx\n"})
        errors, _, _ = validate.validate_bundle(b)
        self.assertTrue(any("id" in e for e in errors))

    def test_index_staleness_still_warns(self):
        # concept present but not listed in index.md -> still a WARN.
        b = make_bundle({"a": concept("a", "leaf")})  # make_bundle writes a bare index
        _, warnings, _ = validate.validate_bundle(b)
        self.assertTrue(any("index" in w.lower() for w in warnings))

    def test_block_links_matching_body_triggers_stale_warn(self):
        # Block-form `links:\n  - b` matches the body [[b]] when parsed as a list,
        # but reindex would reformat it to inline `links: [b]`. Validate must now
        # use the byte predicate (splice_links != text) and therefore WARN here.
        block_links = "links:\n  - b"
        b = make_bundle({
            "a": concept("a", "see [[b]]", extra_fm=block_links),
            "b": concept("b", "leaf"),
        })
        _, warnings, _ = validate.validate_bundle(b)
        self.assertTrue(
            any("links" in w.lower() for w in warnings),
            f"expected stale-links WARN for block-form links:; got warnings={warnings}",
        )


if __name__ == "__main__":
    unittest.main()
