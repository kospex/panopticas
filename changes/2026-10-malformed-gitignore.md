# A Malformed `.gitignore` No Longer Aborts the Scan

Closes [#50](https://github.com/kospex/panopticas/issues/50).

## Summary

If a repository's `.gitignore` contained a line panopticas could not process,
the whole scan failed with a traceback. Git accepts the same file, skips the
bad line and applies the rest.

| `.gitignore` content | Before | Git |
|---|---|---|
| `a[b-a]c` — a character range written backwards | `re.error: bad character range` | Skips the line |
| `\` — a lone backslash | `GitIgnorePatternError: Invalid git pattern` | Skips the line |
| Bytes that are not valid UTF-8 | `UnicodeDecodeError` | Reads the file as bytes |

Every command that walks a directory was affected (`assess`, `urls`, `ai`),
and so was any caller of `identify_files()`, `identify_files_with_metrics()`,
`find_files()` or `find_ai_files()` — including kospex during sync.

It was first noticed while replacing the pathspec matcher in #25. It is not a
regression: the previous matcher failed the same way.

## Cause

`load_gitignore_patterns()` opened the file as strict UTF-8 and handed every
line to pathspec in a single call, catching nothing. One bad line, or one bad
byte, took down the scan.

## Changes

In `core.py`:

- `_ignore_spec()` compiles patterns one line at a time and skips any line
  that raises `ValueError` (pathspec's `GitIgnorePatternError` is a subclass)
  or `re.error`. Order is preserved, because a later negation overrides an
  earlier match.
- `load_gitignore_patterns()` opens the file with `errors='replace'`, so
  undecodable bytes become replacement characters instead of raising. A line
  containing them simply matches nothing.

Skipping is silent, as it is in Git.

## Verification

- `TestMalformedGitignore` in `tests/test_panopticas.py` covers all three
  cases, checks that the valid lines around a bad one still apply — including
  a negation after it — and that the built-in exclusions survive. All six
  tests failed before the change.
- The full suite passes on pathspec 1.1.1 and on 1.0.0, the floor.
- Across 167 cloned repositories, `find_files()` selects exactly the same
  files before and after. None of them has a malformed line, so this confirms
  that compiling line by line changes nothing for a well-formed `.gitignore`.

## Not changed

- A `.gitignore` that cannot be opened at all (a permissions error, or a
  directory with that name) still raises.
- The other differences from Git's file selection are tracked in #46.
