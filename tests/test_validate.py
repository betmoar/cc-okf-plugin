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
    def test_minimal_concept_passes(self):
        # §2 C2: only id and type required; no title/created/updated needed.
        text = "---\nid: minimal\ntype: concept\n---\n\nbody\n"
        b = make_bundle({"minimal": text})
        errors, _, _ = validate.validate_bundle(b)
        self.assertEqual(errors, [], f"expected no errors, got: {errors}")

    def test_free_form_type_passes(self):
        # §3 C5/C6 removed: arbitrary type and status values must not produce errors.
        text = ("---\nid: thing\ntype: BigQuery Table\nstatus: experimental\n"
                "title: T\ncreated: 2026-06-01\nupdated: 2026-06-01\n---\n\nbody\n")
        b = make_bundle({"thing": text})
        errors, _, _ = validate.validate_bundle(b)
        self.assertEqual(errors, [], f"expected no errors, got: {errors}")

    def test_dangling_body_wikilink_is_warning(self):
        # §1: dangling [[id]] is now WARN not ERROR; bundle passes (exit 0).
        b = make_bundle({"a": concept("a", "points to [[ghost]]")})
        errors, warnings, _ = validate.validate_bundle(b)
        self.assertEqual(errors, [], f"expected no errors, got: {errors}")
        self.assertTrue(any("ghost" in w for w in warnings),
                        f"expected ghost WARN, got warnings={warnings}")
        # Confirm exit code is 0 via main()
        rc = validate.main(["validate.py", b])
        self.assertEqual(rc, 0)

    def test_stale_links_no_x2_warning(self):
        # §4 X2 removed: out-of-sync links: is ignored by validate (rule is gone).
        b = make_bundle({
            "a": concept("a", "see [[b]]", links_line="links: [ghost-stale]"),
            "b": concept("b", "leaf"),
        })
        errors, warnings, _ = validate.validate_bundle(b)
        self.assertFalse(any("a.md" in e for e in errors))
        # No X2 warning about stale links:
        self.assertFalse(
            any("links" in w.lower() and "out of date" in w.lower() for w in warnings),
            f"unexpected stale-links X2 warning in: {warnings}",
        )

    def test_clean_bundle_passes(self):
        b = make_bundle({
            "a": concept("a", "see [[b]]"),
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

    def test_dangling_markdown_link_is_warning(self):
        # §5+§1: markdown link to a missing concept → WARN not ERROR, exit 0.
        b = make_bundle({"a": concept("a", "see [ghost](ghost.md)")})
        errors, warnings, _ = validate.validate_bundle(b)
        self.assertEqual(errors, [], f"expected no errors, got: {errors}")
        self.assertTrue(any("ghost" in w for w in warnings),
                        f"expected ghost WARN, got warnings={warnings}")
        rc = validate.main(["validate.py", b])
        self.assertEqual(rc, 0)

    def test_markdown_link_resolves_to_existing_concept(self):
        # §5: markdown [text](foo.md) to an existing concept produces no warning.
        b = make_bundle({
            "a": concept("a", "see [b text](b.md)"),
            "b": concept("b", "leaf"),
        })
        errors, warnings, _ = validate.validate_bundle(b)
        self.assertEqual(errors, [])
        # No warning about 'b' being dangling
        self.assertFalse(any("b" in w and "resolv" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
