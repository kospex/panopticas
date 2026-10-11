# Exclude `.git` When There Is No `.gitignore`

Closes [#1](https://github.com/kospex/panopticas/issues/1).

## Summary

panopticas has four built-in exclusions — `.git`, `.jekyll-cache`,
`.ruff_cache` and `.DS_Store` — but they were appended to the patterns read
from `.gitignore`. A directory with no `.gitignore` got no matcher at all, so
nothing was excluded and the contents of `.git` were scanned.

    $ git init demo && echo 'print(1)' > demo/app.py
    $ panopticas assess demo        # before: app.py plus every file under .git/

Affected:

- `panopticas assess` and `panopticas urls` listed Git's internal files.
- `panopticas ai` could report a file inside `.git` as an AI artifact.
- `identify_files()` returned those files to any caller. kospex calls it
  during sync but was already guarding against this — see below.

## Decision

Issue #1 asked for a decision between three options. Taken:

- **Exclude `.git` by default — yes.** It is never repository content.
- **A switch to turn filtering off — already exists.** `-all-files` (and
  `all_files=True`) disables all filtering and is unchanged, so it still shows
  `.git`.
- **Apply all four built-in exclusions, not just `.git`.** A directory with no
  `.gitignore` now behaves exactly like one with an empty `.gitignore`. Having
  the two differ was the bug.

## Changes

In `core.py`:

- `ALWAYS_IGNORED` holds the four built-in patterns.
- `_scan_spec(directory)` returns the `.gitignore` matcher, or a matcher of
  `ALWAYS_IGNORED` alone when there is no `.gitignore`.
- `identify_files()`, `identify_files_with_metrics()`, `find_files()` and
  `find_ai_files()` use `_scan_spec()`.

`load_gitignore_patterns()` is public and documented as returning `None` when
there is no `.gitignore`. That contract is kept; the fallback lives in the
private helper instead.

## Effect on a real corpus

Measured across 167 cloned repositories before and after:

| | Before | After |
|---|---|---|
| Repositories with no root `.gitignore` | 6 | 6 |
| Files under `.git/` scanned | 308 | 0 |

No other difference in the files selected.

## Effect on kospex

None on its file inventory. `get_repo_files()` in `kospex_git.py` builds the
inventory by iterating the result of `identify_files()`, and it already skips
any `.git` path itself, with a comment noting that panopticas "excludes .git
on most repos but not reliably". This fix makes that guard redundant rather
than changing what kospex stores.

Because kospex takes its file list from panopticas, anything panopticas
excludes is absent from the kospex inventory. That was already true of
`.jekyll-cache`, `.ruff_cache` and `.DS_Store` in every repository with a
`.gitignore`; it now also holds in repositories without one. A committed
`.DS_Store` in such a repository would previously have been inventoried and
no longer is. None of the six corpus repositories has one.

## Not changed

- `-all-files` still lists `.git`. Whether "all files" should ever include
  Git's internals is a separate question.
- The walk still descends into `.git` and discards each file, rather than
  pruning the directory. Correct, but slower than it needs to be on a large
  repository.
- The other differences from Git's own file selection — tracked-but-ignored
  files, nested `.gitignore` files — are recorded in #46.

## Tests

`TestScanWithoutGitignore` in `tests/test_panopticas.py` builds a repository
with a `.git` directory and no `.gitignore`, and covers all four walkers, the
unchanged `all_files` behaviour, and that the result matches a repository with
an empty `.gitignore`.
