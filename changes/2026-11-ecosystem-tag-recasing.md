# Ecosystem Tags: Recase `PyPi` and `maven`

Follows decisions 2 and 3 of [#73](https://github.com/kospex/panopticas/issues/73),
recorded in `changes/2026-11-js-package-managers.md`.

**Status:** implemented.

## The rule

A tag that names a package ecosystem uses the name the OSV schema gives it.
The tool that manages the dependencies gets its own tag alongside.
`requirements.txt` reads `pip, Python, PyPI, dependencies`: `pip` is the tool
and `PyPI` the ecosystem.

OSV is the format vulnerability databases and scanners share. If the tags
use its names, a tag matches an advisory's `ecosystem` field exactly, with no
mapping table and no case-folding.

## What changed

| Old tag | New tag | First emitted | Carried by |
|---|---|---|---|
| `maven` | `Maven` | 0.0.5 | `pom.xml` |
| `PyPi` | `PyPI` | 0.0.11 | pip requirements files (`is_pip_requirements`) |

`npm`, `NuGet` and `Go` already matched OSV, so they don't change.

First-emitted versions come from `git log -S` on each spelling, read against
`pyproject.toml` at that commit. The `maven` commit (2024-10-10) carries
version 0.0.5, the same release the retired-tags reconstruction gives for
`eslint`. The `PyPi` commit (2025-09-05) carries 0.0.11, released that day.

Both old spellings are in `DEPRECATED_TAGS` and on `docs/retired-tags.md`.
They're placed in order of first emission, which is the order "oldest first"
already meant: `maven` (0.0.5) sits after `eslint`, and `PyPi` (0.0.11) after
`Gemini CLI`. The snapshot replaces the old spellings with the new ones, so
the tag count stays at 139.

## Docs

- `docs/cli.md` has a new **Ecosystem tags** section. It covers the rule,
  a table of which files carry each ecosystem tag today, the coverage gaps,
  and the npm paragraph from #73, now one case of the general rule. It also
  carries the guidance on finding npm-the-command projects: the tags can't
  show it, because `package.json` is tagged the same whichever tool installs
  it, but `package-lock.json` and `npm-shrinkwrap.json` can, since only npm
  writes them.
- The `PyPi` examples in `docs/cli.md` (the `assess` table and JSON) and
  `docs/api.md` (`get_filename_metatypes`) now read `PyPI`.
- The retired-tag listings in `docs/cli.md`, `docs/api.md` and
  `docs/retired-tags.md` show six entries.

## Not changed here

- **Missing ecosystem tags.** `uv.lock`, `pyproject.toml` and the Gradle files
  carry their tool's tag but no ecosystem tag. crates.io, RubyGems, Packagist,
  Pub and Hex have no tags at all. That's
  [#74](https://github.com/kospex/panopticas/issues/74), which follows this
  rule.
- **`gradle`.** It's lower-case, unlike the vendor's own "Gradle", but it's
  a tool tag, not an ecosystem tag, and recasing it wasn't part of decisions 2
  and 3.
- **`Go` is also the language tag.** On `go.mod` and `go.sum` it means both;
  the docs say so.

## Effect on kospex

kospex matches tags with SQLite's `LIKE`, which ignores ASCII case, so
`tech_type LIKE '%|PyPi|%'` keeps matching rows re-synced with `PyPI`. A
case-sensitive consumer sees the new spelling after a re-sync, and can
recognise the old one through `get_deprecated_tags()` or
`is_known_tag(..., check_deprecated=True)`.

kospex has its own `"PyPi"` and `"maven"` ecosystem strings in
`kospex_dependencies.py` and its extractor registry. Those are kospex values,
not panopticas tags, and nothing here touches them.

## Tests

- `tests/test_retired_tags.py`: the full retirement list and its order now
  include `maven` and `PyPi`; a new test checks both new spellings are
  current and both old ones are known as retired.
- `tests/test_panopticas.py`: `pom.xml` carries `Maven`, `requirements.txt`
  carries `PyPI`.
- All five assertions failed before the change.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://ossf.github.io/osv-schema/> | Ecosystem names `npm`, `PyPI`, `Maven`, `NuGet`, `Go`, `crates.io`, `RubyGems`, `Packagist`, `Pub`, `Hex` (schema 1.9.2) | 2026-11-01 |
| <https://pypi.org/> | The spelling "PyPI" | 2026-11-01 |
