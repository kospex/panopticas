# Retired Tags: `get_deprecated_tags()` and `is_known_tag()`

Closes [#54](https://github.com/kospex/panopticas/issues/54).

## Summary

`get_tags()` lists the tags the installed version assigns. Stored data
outlives that list: kospex keeps the tags from whichever version last synced a
repository. A consumer validating a stored tag against `get_tags()` could not
tell a retired tag from a typo.

This change adds:

- `DEPRECATED_TAGS` in `constants.py`, mapping each retired tag to its
  replacement (or `None`);
- `get_deprecated_tags()`, returning a copy of that table;
- `is_known_tag(value, *, check_deprecated=False)`;
- `panopticas tags --retired`, with `--json` support;
- `docs/retired-tags.md`, the public table and API description;
- a snapshot test that fails when a tag leaves the vocabulary unrecorded.

## How the list was established

The issue named two retired tags, `Claude Code` and `eslint`. To find the
rest, the tag vocabulary was rebuilt at every commit that touched the
detection source (23 commits, `src/panopticas.py` up to 0.0.10, then
`core.py` and `constants.py`). Each commit was compared with the one before,
and each disappearance was matched to the PyPI release that shipped it:

| Retired tag | Emitted by | Replaced by | Commit | Recorded in CHANGELOG |
|---|---|---|---|---|
| `Github` | 0.0.1 – 0.0.10 | `GitHub` | `6c89a97` (0.0.11) | no |
| `eslint` | 0.0.5 – 0.0.19 | `ESLint` | `952467f` (0.0.20) | 0.0.20 |
| `Claude Code` | 0.0.11 – 0.0.16 | `Claude` | `3389694` (0.0.17) | 0.0.17 |
| `Gemini CLI` | 0.0.11 – 0.0.16 | `Gemini` | `3389694` (0.0.17) | 0.0.17 |

How the rebuild worked:

- **Before `METADATA_RULES`:** the tags were the string literals appended
  inside `get_filename_metatypes()`.
- **After:** the rule tables were evaluated directly, together with
  `AI_RULES` and `IMPLICIT_TAGS`.

At the current commit the rebuild agrees with `get_tags()`, apart from two
dictionary-key literals that are not tags. Those never disappear, so they
cannot mask a retirement.

`Gemini CLI` was retired in the same commit as `Claude Code` but was missing
from the issue. That is presumably because the database it measured had no
`GEMINI.md` files.

`Github` was retired with no record anywhere. A kospex database synced with
0.0.10 or earlier, and not re-synced since, holds `|Github|Git|` on
everything under `.github/`.

No other tag has ever been removed, and no tag has been dropped without a
replacement.

## Design decisions

**Recases are listed.** The issue suggested leaving them out and relying on
case-insensitive matching, since SQLite's `LIKE` ignores ASCII case. That
holds for kospex, but not for a case-sensitive database (PostgreSQL, DuckDB),
a Python `in` check or a dictionary key. Listing both recases costs two
entries, and it means no consumer has to know to ignore case.

**`is_known_tag()` is exact, and current-only by default.** Matching is
case-sensitive, so `esLint` (never emitted) is unknown. `eslint` is known
with `check_deprecated=True`, but because it is on the retired list, not
because case is ignored.

The default is the current vocabulary only. That is what a tag picker or a
check on freshly scanned data wants. A search over stored data opts in with
`check_deprecated=True`.

**The flag is keyword-only and defaults to `False`.** A `None` default
protects against *mutable* defaults, which are shared between calls. A bool
cannot be mutated, so the protection does not apply here. The `*` keeps a
bare positional `True` out of call sites, where it would be unreadable.

**`panopticas tags` is unchanged.** Retired tags are behind `--retired`, so
the default output and its JSON shape (`{"tags", "count"}`) stay the same for
anything that already parses them.

## Keeping the list complete

`tests/data/tag_snapshot.txt` holds every tag shipped that is not retired.
`tests/test_retired_tags.py` asserts:

- every snapshot tag is either current or in `DEPRECATED_TAGS`, so a removal
  must be recorded;
- every current tag is in the snapshot, so a new tag is captured and its later
  removal is caught.

A tag added to the rules must therefore be added to the snapshot too. That is
one line, and the test's failure message says so.

## Docs

- `docs/retired-tags.md`: a new page, with nav entries in
  `docs/_layouts/default.html`.
- `docs/api.md` and `docs/cli.md`: the new functions, the `--retired` flag
  and `DEPRECATED_TAGS`. The stale vocabulary counts were corrected: 129 tags,
  96 filetypes, 62 non-languages, and the `languages --json` example now
  shows 34 rather than 32.
