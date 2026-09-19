"""Command line entry point for bookmark-dedupe."""

import argparse
import sys

from .parser import iter_bookmarks


def build_parser():
    parser = argparse.ArgumentParser(
        prog="bookmark-dedupe",
        description="Find or remove duplicate URLs in a Netscape-format bookmarks export.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="bookmarks HTML file to read (default: stdin)",
    )
    parser.add_argument(
        "-d",
        "--duplicates-only",
        action="store_true",
        help="print only the entries that repeat an earlier URL, instead of the deduplicated list",
    )
    return parser


def run(argv):
    opts = build_parser().parse_args(argv)
    infile = (
        sys.stdin
        if opts.input == "-"
        else open(opts.input, "r", encoding="utf-8", errors="replace")
    )

    seen = set()
    try:
        for bookmark in iter_bookmarks(infile):
            is_duplicate = bookmark.url in seen
            seen.add(bookmark.url)
            if is_duplicate == opts.duplicates_only:
                print(f"{bookmark.title}\t{bookmark.url}")
    finally:
        if infile is not sys.stdin:
            infile.close()

    return 0


def main():
    sys.exit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
