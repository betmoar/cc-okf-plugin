import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import okf_common as oc  # noqa: E402


class TestParse(unittest.TestCase):
    def test_parse_and_body(self):
        text = "---\nid: a\ntitle: A\n---\nhello [[b]]\n"
        fm = oc.parse_frontmatter(text)
        self.assertEqual(fm["id"], "a")
        self.assertEqual(oc.body_of(text), "hello [[b]]\n")

    def test_no_frontmatter(self):
        self.assertIsNone(oc.parse_frontmatter("no fm here"))


class TestWikilinks(unittest.TestCase):
    def test_ordered_dedup(self):
        self.assertEqual(
            oc.extract_wikilinks("see [[b]] and [[a]] and [[b]] again"),
            ["b", "a"],
        )

    def test_token_exact(self):
        # [[a-v2]] must not be matched when looking for [[a]]
        self.assertEqual(oc.extract_wikilinks("[[a-v2]] [[a]]"), ["a-v2", "a"])


class TestExtractLinks(unittest.TestCase):
    """§5: extract_links recognises both [[wiki]] and markdown [text](target) forms."""

    # --- markdown link resolution ---

    def test_bare_md_link(self):
        self.assertEqual(oc.extract_links("[x](foo.md)"), ["foo"])

    def test_dotslash_md_link(self):
        self.assertEqual(oc.extract_links("[x](./foo.md)"), ["foo"])

    def test_concepts_prefix(self):
        self.assertEqual(oc.extract_links("[x](concepts/foo.md)"), ["foo"])

    def test_slash_concepts_prefix(self):
        self.assertEqual(oc.extract_links("[x](/concepts/foo.md)"), ["foo"])

    def test_fragment_stripped(self):
        self.assertEqual(oc.extract_links("[x](foo.md#section)"), ["foo"])

    def test_query_stripped(self):
        self.assertEqual(oc.extract_links("[x](foo.md?v=2)"), ["foo"])

    # --- flat-model non-resolvers (residual /  or ..) ---

    def test_subdir_does_not_resolve(self):
        # a/b.md has a residual / after normalization → not a flat concept
        self.assertEqual(oc.extract_links("[x](a/b.md)"), [])

    def test_dotdot_does_not_resolve(self):
        self.assertEqual(oc.extract_links("[x](../bar.md)"), [])

    def test_absolute_host_does_not_resolve(self):
        self.assertEqual(oc.extract_links("[x](https://host/x.md)"), [])

    # --- mixed wiki + markdown ---

    def test_mixed_dedup(self):
        body = "see [[foo]] and [bar text](bar.md) and [foo again](foo.md)"
        result = oc.extract_links(body)
        self.assertEqual(result, ["foo", "bar"])  # ordered, deduped

    # --- backwards-compat alias ---

    def test_alias_callable(self):
        self.assertTrue(callable(oc.extract_wikilinks))

    def test_alias_same_result(self):
        body = "[[foo]] and [bar](bar.md)"
        self.assertEqual(oc.extract_links(body), oc.extract_wikilinks(body))


class TestSplice(unittest.TestCase):
    def base(self, links_line):
        fm = ["id: a", "title: A", "type: concept",
              "created: 2026-06-01", "updated: 2026-06-01"]
        if links_line is not None:
            fm.append(links_line)
        return "---\n" + "\n".join(fm) + "\n---\n\nbody [[b]] [[c]]\n"

    def test_insert_when_absent(self):
        out = oc.splice_links(self.base(None), ["b", "c"])
        self.assertIn("links: [b, c]", out)
        self.assertTrue(out.endswith("body [[b]] [[c]]\n"))

    def test_replace_inline(self):
        out = oc.splice_links(self.base("links: [old]"), ["b", "c"])
        self.assertIn("links: [b, c]", out)
        self.assertNotIn("[old]", out)

    def test_replace_block(self):
        text = ("---\nid: a\ntitle: A\ntype: concept\ncreated: 2026-06-01\n"
                "updated: 2026-06-01\nlinks:\n  - old1\n  - old2\n---\n\nb [[b]]\n")
        out = oc.splice_links(text, ["b"])
        self.assertIn("links: [b]", out)
        self.assertNotIn("old1", out)

    def test_empty_removes_field(self):
        out = oc.splice_links(self.base("links: [old]"), [])
        self.assertNotIn("links:", out)

    def test_empty_removes_inline_empty_form(self):
        # the `links: []` form is also removed when the body has no links
        out = oc.splice_links(self.base("links: []"), [])
        self.assertNotIn("links:", out)

    def test_comment_in_links_block_is_swallowed(self):
        # Spec §A contract: comments inside a links: block are NOT preserved;
        # the field is regenerated wholesale. Critically, the comment and stray
        # list items must NOT leak into the frontmatter as garbage.
        text = ("---\nid: a\ntitle: A\ntype: concept\ncreated: 2026-06-01\n"
                "updated: 2026-06-01\nlinks:\n  # do not reorder\n  - old\n"
                "---\n\nbody [[b]]\n")
        out = oc.splice_links(text, ["b"])
        self.assertIn("links: [b]", out)
        self.assertNotIn("do not reorder", out)
        self.assertNotIn("- old", out)
        self.assertEqual(out.count("links:"), 1)  # no duplicate field

    def test_blank_line_after_links_block_preserved(self):
        # A separator blank line between links: and the next field must survive
        # (the consume loop stops at blanks, not just at top-level keys).
        text = ("---\nid: a\ntitle: A\ntype: concept\ncreated: 2026-06-01\n"
                "updated: 2026-06-01\nlinks:\n  - old\n\ntags: [x]\n"
                "---\n\nbody [[b]]\n")
        out = oc.splice_links(text, ["b"])
        self.assertIn("links: [b]", out)
        self.assertIn("\n\ntags: [x]", out)  # blank line + tags intact

    def test_placement_preserved_when_field_mid_frontmatter(self):
        # links: defined between title and created stays in that position.
        text = ("---\nid: a\ntitle: A\nlinks: [old]\ntype: concept\n"
                "created: 2026-06-01\nupdated: 2026-06-01\n---\n\nbody [[b]]\n")
        out = oc.splice_links(text, ["b"])
        lines = out.split("\n")
        self.assertEqual(lines.index("links: [b]"), lines.index("title: A") + 1)

    def test_idempotent(self):
        once = oc.splice_links(self.base(None), ["b", "c"])
        twice = oc.splice_links(once, ["b", "c"])
        self.assertEqual(once, twice)

    def test_preserves_other_bytes(self):
        text = self.base("links: [old]")
        out = oc.splice_links(text, ["b", "c"])
        # title/created/body untouched
        self.assertIn("title: A", out)
        self.assertIn("created: 2026-06-01", out)
        self.assertTrue(out.endswith("body [[b]] [[c]]\n"))


class TestSetId(unittest.TestCase):
    def test_set_id(self):
        text = "---\nid: old\ntitle: T\n---\nbody\n"
        self.assertIn("id: new", oc.set_id(text, "new"))


if __name__ == "__main__":
    unittest.main()
