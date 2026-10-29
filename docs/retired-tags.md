---
layout: default
title: Retired Tags
description: Tags earlier panopticas releases emitted and the current release does not, what replaced each, and how to recognise them in stored data.
---

# Retired and Changed Tags

**Reconstructed:** 2026-10-30, from every commit that changed tag output
(panopticas 0.0.1 to 0.0.21 and unreleased changes)

`get_tags()` lists the tags the installed version can assign. Data stored by
an older version can hold tags that are no longer on that list, because a tag
was renamed, recased or dropped. This page lists every such tag, and the API
that lets a consumer recognise one.

## The retired tags

Oldest first.

| Retired tag | Emitted by | Replaced by | Kind | Assigned to |
|---|---|---|---|---|
| `Github` | 0.0.1 – 0.0.10 | `GitHub` (0.0.11) | recase | every file under `.github/` |
| `eslint` | 0.0.5 – 0.0.19 | `ESLint` (0.0.20) | recase | `eslint.config.js` |
| `Claude Code` | 0.0.11 – 0.0.16 | `Claude` (0.0.17) | rename | `CLAUDE.md` |
| `Gemini CLI` | 0.0.11 – 0.0.16 | `Gemini` (0.0.17) | rename | `GEMINI.md` |

- **The renames** made AI products brand-level. `Claude` covers Claude Code
  and Claude Desktop alike, and `Gemini` covers Gemini CLI. A file that used
  to read `Claude, AI, Claude Code` now reads `AI, Claude, instructions`.
- **The recases** brought tool names into the vendor's own casing. The tag
  still means the same thing; only its spelling changed.

No tag has been dropped without a replacement.

## Why a change of case is listed

A recased tag is a different string, and whether a database treats it as the
same tag depends on how that database compares text:

| Database | Does `LIKE '%eslint%'` match a stored `ESLint`? |
|---|---|
| SQLite | matches: `LIKE` ignores case for ASCII letters |
| MySQL / MariaDB | matches under the default case-insensitive collations |
| PostgreSQL | no match: `LIKE` is case-sensitive; `ILIKE` is not |
| DuckDB | no match: `LIKE` is case-sensitive; `ILIKE` is not |

kospex stores tags in SQLite, so a query for `eslint` and one for `ESLint`
return the same rows there. Anyone using panopticas tags in another context,
whether a case-sensitive database, a Python `in` check or a dictionary key,
would see two different tags. Listing recases means the retired spelling is
recognised without having to ignore case.

## API

### get_deprecated_tags

```python
from panopticas import get_deprecated_tags

get_deprecated_tags()
# Returns: {'Github': 'GitHub', 'eslint': 'ESLint',
#           'Claude Code': 'Claude', 'Gemini CLI': 'Gemini'}
```

**Returns:** A `dict` mapping each retired tag to the current tag that
replaced it, oldest first. A tag dropped outright maps to `None`; none has
been so far. The dict is a copy, so changing it does not affect panopticas.

Use it to rewrite a stored tag to its current spelling for display, or to
show a retired tag as retired, with its replacement, instead of letting it
disappear from a tag listing while its rows remain.

### is_known_tag

```python
from panopticas import is_known_tag

is_known_tag("ESLint")                               # True
is_known_tag("eslint")                               # False
is_known_tag("eslint", check_deprecated=True)        # True
is_known_tag("Claude Code", check_deprecated=True)   # True
is_known_tag("esLint", check_deprecated=True)        # False
```

**Arguments:**
- `value` — the tag to check
- `check_deprecated` — keyword-only, default `False`. When `True`, a retired
  tag also counts as known.

**Returns:** `True` if `value` is a tag this version can assign, or, with
`check_deprecated=True`, one an earlier version assigned.

By default only the current vocabulary counts, which is what a tag picker or
a check on newly scanned data wants. Pass `check_deprecated=True` to validate
a search against stored data, where rejecting `Claude Code` would turn away a
tag that real files carry.

The match is exact, including case. `eslint` is known with
`check_deprecated=True` because it is a retired tag, not because case is
ignored, so `esLint`, which no release ever emitted, is not known.

### On the command line

```console
$ panopticas tags --retired

┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Retired tag ┃ Replaced by ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Github      │ GitHub      │
│ eslint      │ ESLint      │
│ Claude Code │ Claude      │
│ Gemini CLI  │ Gemini      │
└─────────────┴─────────────┘

4 retired tags
```

`panopticas tags --retired --json` returns `{"retired": {...}, "count": 4}`.

## Refreshing stored data

A retired tag stays in stored data until the file is scanned again. kospex
records the panopticas version each repository was synced with, and re-syncs
when it changes, so upgrading panopticas re-tags repositories synced
afterwards.

## Keeping this list complete

`DEPRECATED_TAGS` in `src/panopticas/constants.py` holds the table above.
`tests/test_retired_tags.py` compares the current vocabulary with a snapshot
of every tag panopticas has shipped, and fails if a tag disappears without
being added there. `Github` went unrecorded for a year before that test
existed.
