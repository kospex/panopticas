# Replace the Deprecated pathspec `gitwildmatch` Factory

Closes [#25](https://github.com/kospex/panopticas/issues/25).

## Summary

`load_gitignore_patterns()` built its `.gitignore` matcher with a pattern
factory that pathspec deprecated in 1.0.0:

    pathspec.PathSpec.from_lines('gitwildmatch', patterns)

Every call raised a `DeprecationWarning` — 168 in the test suite — and the
call would fail outright once pathspec removes the name.

## Changes

    from pathspec.patterns.gitignore.spec import GitIgnoreSpecPattern
    ...
    pathspec.PathSpec.from_lines(GitIgnoreSpecPattern, patterns)

The pathspec floor in `pyproject.toml` moves from `>=0.12.1` to `>=1.0.0`.

## Why not the obvious fix

The deprecation message says to use `'gitignore'` instead, and the issue
proposed exactly that swap. It is the wrong one: it changes which files are
ignored.

pathspec offers three replacements. They were compared against the current
matcher on this repository's files and on a set of awkward patterns:

| Replacement | Warning gone | Same results as before |
|---|---|---|
| `'gitignore'` (registered name → `GitIgnoreBasicPattern`) | Yes | **No** — differs on two patterns |
| `GitIgnoreSpecPattern` passed directly | Yes | Yes |
| `pathspec.GitIgnoreSpec.from_lines(...)` | Yes | Yes, in every case tested |

The two differences with `'gitignore'`:

| Pattern | Before, and Git | With `'gitignore'` |
|---|---|---|
| `foo/*` | Ignores everything under `foo/`, including `foo/bar/baz.txt` | Ignores only direct children; `foo/bar/baz.txt` is scanned |
| a bare `/` | Ignores nothing | Ignores every file |

The cause is in pathspec's source. In 1.x the deprecated `GitWildMatchPattern`
is declared as `class GitWildMatchPattern(GitIgnoreSpecPattern)` and adds only
the warning. `GitIgnoreSpecPattern` replicates Git's actual behaviour;
`GitIgnoreBasicPattern` implements the gitignore documentation literally, and
pathspec's own docstring says it "differs from how Git actually behaves".

`foo/*` is a common shape in real `.gitignore` files, so the obvious fix would
have made panopticas scan and tag files a repository meant to exclude, with no
test failing.

Passing `GitIgnoreSpecPattern` directly is therefore identical to the old
behaviour by construction, not merely by testing. `GitIgnoreSpec.from_lines`
was the alternative; it needs no floor change but is a different class, so its
equivalence rests only on the cases tried.

## The floor change

`GitIgnoreSpecPattern` does not exist before pathspec 1.0.0 — importing it
under 0.12.1 raises `ModuleNotFoundError` — so the floor had to move.

- A fresh install already resolved to 1.x; `requirements.txt` pins `1.1.1`.
- kospex pins `pathspec==1.1.1` in its `requirements.txt`, so it is unaffected.
- Only an environment that pins pathspec below 1.0 would now fail to resolve.

The old `>=0.12.1` floor is how the deprecation arrived unannounced: the
resolver crossed the 0.x → 1.x boundary on its own.

## Verification

- The full suite passes with `-W error::DeprecationWarning`, on pathspec 1.1.1
  and on 1.0.0, the new floor. The warning count went from 168 to 0.
- `identify_files()` over this repository returns the same 113 files and
  filetypes before and after.
- Across 167 cloned repositories (237,318 files), the matcher's verdict was
  compared with `git check-ignore`. There was no case where a root
  `.gitignore` pattern was interpreted differently. The structural differences
  that comparison did find — tracked-but-ignored files, nested `.gitignore`
  files — are unrelated to this change and are recorded in #46.
- New tests in `tests/test_panopticas.py` (`TestLoadGitignorePatterns`) pin
  the two patterns above, negation, directory patterns and the four literals
  panopticas appends (`.git`, `.jekyll-cache`, `.ruff_cache`, `.DS_Store`).
  With `'gitignore'` swapped in, the `foo/*` and bare `/` tests fail.

## Not covered

Two malformed patterns raise from pathspec with every matcher, old and new: an
invalid range such as `a[b-a]c`, and a lone backslash. A `.gitignore`
containing one makes the scan fail. That is existing behaviour and is not
changed here.
