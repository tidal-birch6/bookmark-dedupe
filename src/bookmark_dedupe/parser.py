"""Streaming parser for Netscape-format bookmark exports -- the HTML file
Chrome, Firefox and Safari all produce from File > Export Bookmarks."""

from html.parser import HTMLParser


class Bookmark:
    __slots__ = ("title", "url", "add_date")

    def __init__(self, title, url, add_date):
        self.title = title
        self.url = url
        self.add_date = add_date

    def __repr__(self):
        return f"Bookmark(title={self.title!r}, url={self.url!r})"


class BookmarkParser(HTMLParser):
    """Emits one Bookmark per <A> tag as soon as its closing tag is seen.

    Netscape bookmark files never close their <DT> or <P> tags, which
    trips up parsers that try to build a proper tree. We don't need the
    tree -- only <A> elements matter -- so we just track whether we're
    currently inside one and ignore everything else about nesting.
    """

    def __init__(self, on_bookmark):
        super().__init__(convert_charrefs=True)
        self._on_bookmark = on_bookmark
        self._in_anchor = False
        self._url = None
        self._add_date = None
        self._title_parts = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attr_map = dict(attrs)
        self._in_anchor = True
        self._url = attr_map.get("href")
        self._add_date = attr_map.get("add_date")
        self._title_parts = []

    def handle_endtag(self, tag):
        if tag != "a" or not self._in_anchor:
            return
        self._in_anchor = False
        if self._url:
            title = "".join(self._title_parts).strip()
            self._on_bookmark(Bookmark(title, self._url, self._add_date))

    def handle_data(self, data):
        if self._in_anchor:
            self._title_parts.append(data)


def iter_bookmarks(fileobj, chunk_size=65536):
    """Yield Bookmark objects from fileobj without reading it all at once.

    fileobj must be opened in text mode. We read chunk_size characters at
    a time and feed them straight to the parser, so memory use stays
    proportional to chunk_size regardless of how large the export file
    is -- a multi-decade bookmark hoard is the whole reason this tool
    exists.
    """
    found = []

    parser = BookmarkParser(found.append)
    try:
        while True:
            chunk = fileobj.read(chunk_size)
            if not chunk:
                break
            parser.feed(chunk)
            yield from found
            found.clear()
        parser.close()
        yield from found
    finally:
        found.clear()
