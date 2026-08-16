# Changelog

The format of this changelog is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed
 - `panopticas file` labelled its first table row `File extenion`. Cosmetic, and the only change to shipped code since 0.0.19 — no library function, tag or JSON field changes, so kospex is unaffected and its pin does not need bumping for this

## 0.0.19 - 2026-08-15

### Added
 - `get_tags()`, `get_filetypes()` and `get_languages()` return the vocabularies panopticas uses. The tag vocabulary is derived from the detection rules, so it cannot drift.
 - `panopticas tags`, `panopticas languages` and `panopticas filetypes` commands.
 - `--json` (also accepted as `-json`) on every command. In JSON mode stdout carries only the document; progress messages go to stderr.

### Changed
 - Table output now uses `rich` instead of `prettytable`, matching kospex and foundationx.
 - Path arguments are validated at the CLI boundary: `assess` and `urls` require a directory, `file` requires a file. Previously a wrong path type produced empty output or an unhandled error.
 - `assess -unknown` now reports totals for the rows it shows. Previously it filtered the rows but the footer still counted every scanned file.

### Fixed
 - `panopticas urls DIRECTORY` failed with `FileNotFoundError` whenever the target was not the current working directory, and silently read the wrong file when a same-named file existed in the current directory. `find_files()` returns paths relative to the scanned directory; they are now resolved against it before being opened.
 - `extract_urls_from_file()` crashed with `TypeError` instead of raising `UnicodeDecodeError` on undecodable input, because the error handler re-raised `UnicodeDecodeError` with only a message argument when its constructor requires five. This crashed `panopticas urls` and `panopticas file` on any binary file. The handler now preserves the original exception's fields, and `panopticas urls` treats an undecodable file as having no URLs instead of aborting the whole scan.
 - `assess -unknown` never matched anything, because `get_language()` returns the string `"Unknown"` and the filter compared against `None`. It now also matches `core.UNKNOWN`.

### Removed
 - The `prettytable` dependency.

## 0.0.18 - 2026-08-09

### Added
 - `setup.py` and `setup.cfg` detected as Python dependency manifests, tagged `build, dependencies, Python, setuptools` ([#21](https://github.com/kospex/panopticas/issues/21)). Both previously returned no metatypes, so a setuptools project without a `pyproject.toml` looked like it declared no dependencies at all
 - `setup.cfg` now reports its language as `INI` — it is read by `configparser`. Mapped by basename rather than adding `.cfg` to the extension table, since that extension is used for arbitrary formats elsewhere; no other `.cfg` file changes

### Notes
 - Tags are **added only** — no existing tag is renamed or removed, so this release is not breaking for kospex. However, kospex caches `tech_type` at sync time, so `setup.py` / `setup.cfg` only appear in an existing kospex database after a **re-sync**. `kospex_core.py` tracks `last_panopticas_version` and re-syncs when it changes, so bumping the kospex pin triggers re-tagging for repos synced afterwards

## 0.0.17 - 2026-08-04

### Added
 - AI coding agent detection — 20 products detected via a new `AI_RULES` table (60 detection rules), tagging artifacts with `AI`, the product brand, and the artifact kind (e.g. `AI, Claude, instructions`)
 - `panopticas ai [DIRECTORY]` command listing AI files with their product and kind, plus a summary of which AI products the repo uses; `--all-files` additionally reports gitignored files and bare AI directories
 - `get_ai_metadata(file_path)` returning `{"product", "kind"}` or `None` for a path
 - `find_ai_files(directory, all_files=False)` returning path -> AI metadata for a directory tree
 - Test coverage for AI detection, precedence, tag output and rules-table integrity (235 tests at release)

### Changed
 - (breaking) `CLAUDE.md` now tags as `AI, Claude, instructions` (was `Claude, AI, Claude Code`) and `GEMINI.md` as `AI, Gemini, instructions` (was `Gemini, AI, Gemini CLI`) — product tags are now brand-level and consistent across all AI entries
 - AI detection rules moved out of `METADATA_RULES` into the dedicated `AI_RULES` table

## 0.0.16 - 2026-05-21

### Fixed
 - [Replaced hardcoded VERSION with importlib.metadata](https://github.com/kospex/panopticas/issues/16) — pyproject.toml is now the single source of truth for the version

### Added
 - Detect `pnpm-lock.yaml` as a JavaScript dependency file (tags: `dependencies, JavaScript, pnpm, npm`) — unblocks pnpm project SCA in kospex `krunner osi`
 - Add `npm` tag to `yarn.lock` detection (now `dependencies, JavaScript, yarn, npm`) — surfaces that yarn fetches from the npm registry, mirroring the new pnpm-lock entry's tag list
 - [Add dependabot.yml to detections](https://github.com/kospex/panopticas/issues/6) — detects both .yml and .yaml variants with Dependabot, GitHub, dependencies, security tags
 - [Add Windows and .NET development file types](https://github.com/kospex/panopticas/issues/10) — .dll, .aspx, .ascx, .sln, .csproj, .config, global.asax, packages.config, nuget.config, web.config, app.config
 - pytest test suite covering file type detection, metadata extraction, shebang parsing, URL extraction, and constants integrity (~130 tests at release)
 - pytest as a test optional dependency (`pip install panopticas[test]`)

### Changed
 - Updated CLAUDE.md with correct package structure, release process, and relationship to kospex
 - Updated README.md with additional CLI examples and development instructions

## 0.0.15 - 2025-12-13

### Changed
 - [Remove package build and twine from dependencies](https://github.com/kospex/panopticas/issues/14)
 - [Version pin direct dependencies in pyproject.toml](https://github.com/kospex/panopticas/issues/13)

## 0.0.14 - 2025-11-24

### Added
 - [Added bare LICENSE filename detection](https://github.com/kospex/panopticas/issues/12)
 - [added groovy types and .properties files](https://github.com/kospex/panopticas/issues/11)

## 0.0.13 - 2025-10-01

### Added
 - [Added binary types](https://github.com/kospex/panopticas/issues/7)
 - [added a switch to skip shebang detection for filenname only tests](https://github.com/kospex/panopticas/issues/8)


## 0.0.12 - 2025-09-17

### Added
 - [Added more CI pipeline configuration files](https://github.com/kospex/panopticas/issues/5)

## 0.0.11 - 2025-09-05

### Added
  - added PowerShell .ps1 as a type
  - Added .exe, .jar and .zip as types (also tagged as binary)
### Changed
 - [Return 'Unknown' instead None type for unknown file types](https://github.com/kospex/panopticas/issues/4)

## 0.0.10 - 2025-05-09

  - added uv.lock as a type (from [Astral uv](https://docs.astral.sh/uv/))
  - added CNAME as github pages and other tools use this for domain mapping
  - added .sarif extension
  - added .python-version (for detecting pinned dependencies)

### Changed
  - moved the version function to use the click implementation


### Added
 - Added .gitleaksignore file
 - Added yarn.lock
 - Added optional line counting feature with `--lines` flag for assess command

### Changed
 - Restructured package layout to follow Python best practices with proper src/panopticas/ structure

## 0.0.9 - 2025-01-12

### Added
  - new function extract_urls_from_file

### Changed
  - changed panopticas file to use extract_urls_from_file

## 0.0.8 - 2025-01-12

### Added
  - .travis.yml identification for [Travis CI](https://www.travis-ci.com/)

### Changed
  - improved pip requirements detection to be regular expression based


## VERSION - DATE

### Added

### Changed
