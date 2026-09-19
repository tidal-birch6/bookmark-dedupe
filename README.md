# bookmark-dedupe

A command line tool that finds duplicate URLs in a browser bookmarks
export and prints a deduplicated list.

## the problem

Bookmark files accumulate duplicates for years: you save a page, forget
you saved it, save it again in a different folder six months later. None
of the major browsers dedupe on export, and once the file has a few
thousand entries spread across nested folders, eyeballing it stops being
an option.

Export formats (Chrome, Firefox, Safari) are all the same "Netscape
bookmark file" HTML format, dating back to Netscape Navigator. It's not
valid HTML by modern standards -- `<DT>` and `<P>` tags are never closed
-- which is why a generic HTML-to-tree parser tends to choke on it. This
tool only cares about `<A HREF="...">` tags, so it sidesteps the nesting
problem entirely.

## usage

Export your bookmarks (in Chrome: `chrome://bookmarks` -> the three-dot
menu -> Export bookmarks) and run:

```
bookmark-dedupe bookmarks.html > deduped.tsv
```

Output is `title<TAB>url`, one line per unique URL, first occurrence
wins. To see what would be *removed* instead:

```
bookmark-dedupe --duplicates-only bookmarks.html
```

It also reads from stdin, so it composes with anything else that emits
a Netscape bookmark file:

```
cat bookmarks.html | bookmark-dedupe
```

## install

No dependencies beyond the Python standard library.

```
python3 -m pip install -e .
```

That gives you the `bookmark-dedupe` command. Without installing, you
can also run it as a module:

```
python3 -m bookmark_dedupe.cli bookmarks.html
```

## why streaming matters here

Some people have bookmark files with tens of thousands of entries built
up over fifteen years of browser profile migrations. `iter_bookmarks()`
reads the input in fixed-size chunks and feeds them to the parser
incrementally, so the memory footprint doesn't grow with file size --
only the set of seen URLs does, which is unavoidable for dedup.

## license

MIT, see LICENSE.
