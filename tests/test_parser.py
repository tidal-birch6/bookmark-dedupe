import io
import unittest
from pathlib import Path

from bookmark_dedupe.parser import BookmarkParser, iter_bookmarks

FIXTURE = Path(__file__).parent / "fixtures" / "bookmarks.html"


class IterBookmarksTests(unittest.TestCase):
    def test_reads_every_anchor_in_document_order(self):
        with open(FIXTURE, encoding="utf-8") as f:
            bookmarks = list(iter_bookmarks(f))

        self.assertEqual(
            [b.url for b in bookmarks],
            [
                "https://example.com/one",
                "https://example.com/two",
                "https://example.com/one",
                "https://example.com/three",
                "https://example.com/two",
            ],
        )

    def test_decodes_entities_in_titles(self):
        with open(FIXTURE, encoding="utf-8") as f:
            bookmarks = list(iter_bookmarks(f))

        two = next(b for b in bookmarks if b.title.startswith("Example &"))
        self.assertEqual(two.title, "Example & Two")

    def test_captures_add_date(self):
        with open(FIXTURE, encoding="utf-8") as f:
            bookmarks = list(iter_bookmarks(f))

        self.assertEqual(bookmarks[0].add_date, "1600000001")

    def test_result_independent_of_chunk_size(self):
        # A folder tag or attribute can straddle a chunk boundary depending
        # on chunk_size. Small chunk sizes exercise that split without
        # needing a multi-megabyte fixture.
        with open(FIXTURE, encoding="utf-8") as f:
            whole = list(iter_bookmarks(f, chunk_size=65536))
        with open(FIXTURE, encoding="utf-8") as f:
            chunked = list(iter_bookmarks(f, chunk_size=7))

        self.assertEqual([b.url for b in whole], [b.url for b in chunked])
        self.assertEqual([b.title for b in whole], [b.title for b in chunked])

    def test_anchor_without_href_is_skipped(self):
        html = "<DT><A>no href here</A>"
        found = []
        parser = BookmarkParser(found.append)
        parser.feed(html)
        parser.close()
        self.assertEqual(found, [])

    def test_empty_input_yields_nothing(self):
        bookmarks = list(iter_bookmarks(io.StringIO("")))
        self.assertEqual(bookmarks, [])


if __name__ == "__main__":
    unittest.main()
