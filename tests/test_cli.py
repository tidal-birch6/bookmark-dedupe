import contextlib
import io
import sys
import unittest
from pathlib import Path

from bookmark_dedupe.cli import run

FIXTURE = Path(__file__).parent / "fixtures" / "bookmarks.html"


class RunTests(unittest.TestCase):
    def _run(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = run(argv)
        return status, out.getvalue().splitlines()

    def test_dedup_keeps_first_occurrence_of_each_url(self):
        status, lines = self._run([str(FIXTURE)])

        self.assertEqual(status, 0)
        self.assertEqual(
            lines,
            [
                "Example One\thttps://example.com/one",
                "Example & Two\thttps://example.com/two",
                "Example Three\thttps://example.com/three",
            ],
        )

    def test_duplicates_only_reports_repeats(self):
        status, lines = self._run(["--duplicates-only", str(FIXTURE)])

        self.assertEqual(status, 0)
        self.assertEqual(
            lines,
            [
                "Example One Again\thttps://example.com/one",
                "Duplicate Two\thttps://example.com/two",
            ],
        )

    def test_reads_from_stdin_by_default(self):
        stdin = io.StringIO(
            '<DT><A HREF="https://example.com/a">A</A>'
            '<DT><A HREF="https://example.com/a">A again</A>'
        )
        out = io.StringIO()
        real_stdin = sys.stdin
        sys.stdin = stdin
        try:
            with contextlib.redirect_stdout(out):
                status = run([])
        finally:
            sys.stdin = real_stdin

        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue().splitlines(), ["A\thttps://example.com/a"])


if __name__ == "__main__":
    unittest.main()
