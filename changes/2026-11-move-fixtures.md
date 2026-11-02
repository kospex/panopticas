# Move the Fixture Files from src/tests/ to tests/fixtures/

Closes [#99](https://github.com/kospex/panopticas/issues/99).

**Status:** implemented, 2026-11-02.

## Why

`src/tests/` held 187 sample files for panopticas to analyse. It contained no
test code; the pytest suite has always been in `tests/`.

- **PyPA.** The [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
  means "moving the code that is intended to be importable" into `src/`.
  Other project files stay at the root.
- **pytest.** [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
  describes two layouts: a root-level `tests/` beside `src/mypkg/`, and tests
  inside the package (`src/mypkg/tests/`). `src/tests/` was neither. The page
  "strongly" suggests a src layout either way.
- **#95.** setuptools treated `src/tests/` as a package candidate, so the
  0.0.22 wheel shipped `src/tests/typedpkg/` as a top-level `tests` package.
  #96 limited discovery to `panopticas`; this move removes the cause.

Neither guide says where fixture files go. They now sit beside the tests that
use them, as `tests/data/tag_snapshot.txt` already did.

## What changed

- `git mv src/tests tests/fixtures`, so history follows the files.
- `FIXTURES_DIR` in `tests/test_panopticas.py` and `tests/test_cli_json.py`
  now points to `tests/fixtures/`.
- **`TestFixtureFiles` fails instead of skipping** when the directory is
  missing. With the old path still in place after the move, 30 tests
  skipped and the suite passed apart from 5 CLI tests. That would have hidden
  a wrong path.
- `.gitignore`: the `.warp/` exception is now `!tests/fixtures/.warp/`.
- `CLAUDE.md`: the fixture location in Development Commands, File Structure
  and Testing, and a note that fixture directories avoid `lib/`.
- `pyproject.toml`: the comment from #96. The `include = ["panopticas*"]`
  restriction stays.

## Verification

| Check | Before | After |
|---|---|---|
| Tests | 1,399 passed, 0 skipped | 1,399 passed, 0 skipped |
| `assess --json` of the fixture tree | 187 files | 187 files, identical language and tags for every file |
| Tags with the repo-relative prefix (`src/tests/…` against `tests/fixtures/…`) | — | identical for all 187, for `get_filename_metatypes`, `get_ai_metadata` and `get_language` |
| pytest collection from `tests/fixtures/` | — | 0 items (no fixture is a `.py` file or named `test_*`) |
| Wheel | `panopticas` only | `panopticas` only |
| sdist | `tests/test_*.py`, plus `src/tests/typedpkg/` | `tests/test_*.py` only |

No `path_contains` or `AI_RULES` fragment matches `tests/` or `fixtures/`, so
the new prefix adds no tags. Path-sensitive fixtures (`.github/workflows/`,
`.warp/`, `.cargo/config.toml`, `gradle/libs.versions.toml`, `.nuke/`, `.vs/`)
kept their relative structure.

The sdist never carried the rest of the fixtures, so running the suite from
an sdist was already incomplete. This change doesn't make it worse; it drops
the one fixture the sdist did pick up.

## Not changed

Dated records keep the old path: the `changes/` notes and design plans that
name `src/tests/`, and `CHANGELOG.md` entries, including the #95 fix under
`[Unreleased]`. They describe where the files were at the time.

No effect on kospex: tags and vocabulary are unchanged.
