# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Panopticas is a Python CLI tool and library for analyzing file types, languages, and metadata in codebases. It identifies programming languages by file extensions, shebangs, and filenames, and extracts metadata like dependencies, build configurations, and URLs from files.

Panopticas is a dependency of [kospex](https://github.com/kospex/kospex) — a broken panopticas release can break kospex installs.

## Architecture

The project is a Python package with the following modules:

```
src/panopticas/
├── __init__.py       # Module exports
├── core.py           # Core analysis engine — file type detection, language identification, metadata extraction
├── cli.py            # Click-based CLI interface
└── constants.py      # File type mappings, metadata definitions, extension lookups, AI agent rules
```

### Key Components

- **File Type Detection**: Uses extension mappings (`EXT_FILETYPES`) and shebang parsing to identify programming languages
- **Metadata Extraction**: Identifies build files, dependency manifests, CI configurations, and other special file types
- **AI Agent Detection**: Identifies AI coding agent artifacts (`AI_RULES`) — see below
- **URL Extraction**: Finds HTTP/HTTPS URLs within files using regex patterns
- **Git Integration**: Respects `.gitignore` patterns when scanning directories
- **Binary Detection**: Identifies binary file types (images, executables, archives)

### AI Agent Detection

> **Before adding or changing a rule, read [`docs/ai-detection-rules.md`](docs/ai-detection-rules.md)** — the full inventory, the source that confirms each convention, and the list of candidates already investigated and **rejected**. Four proposed rules were rejected as wrong; re-adding one would mislabel repositories.

`AI_RULES` in `constants.py` maps an indicator to `(product, kind)` across three match modes — `exact_filename`, `path_contains` and `filename_suffix`. Precedence is exact filename, then the longest matching path fragment, then the longest matching suffix; first hit wins.

`core.get_ai_metadata(path)` is the single source of truth, returning `{"product", "kind"}` or `None`. `get_filename_metatypes()` derives `["AI", product, kind]` from it, so `assess` and kospex pick up AI tags without calling anything new.

Rules to follow when adding a product:

- Detection is **path-based only** — never open a file to determine AI metadata.
- Products are **brand-level**: `Claude` covers both Claude Code and Claude Desktop. Files owned by no brand use a pseudo-product (`Agents`, `MCP`, `llms.txt`).
- `kind` must come from `AI_ARTIFACT_KINDS`. Do not invent a new one without adding it there.
- `exact_filename` and `path_contains` keys are lowercase; path fragments end with `/`.
- **Verify the convention against the product's current official docs before adding it.** A wrong rule mislabels a repository and the label flows into kospex. A missing rule is better than a wrong one. Watch for user-level paths (`~/.config/<tool>/`) — those are not repository artifacts and must not be added.

## Development Commands

### Installation (Development)
```bash
pip install -e .
```

### Running Tests
```bash
pytest -v
```

Test fixture files are in `src/tests/` (sample files for analysis, not pytest tests). Automated tests live in `tests/` in the project root.

### Build and Distribution
```bash
python -m build
python -m twine upload dist/panopticas-X.Y.Z*
```

`dist/` accumulates artifacts from every previous release. Uploading `dist/*`
makes twine re-send them all; PyPI rejects the duplicates and the upload
aborts. Always scope the glob to the version being released.

### Running the CLI
```bash
# Assess current directory
panopticas assess

# Assess specific directory
panopticas assess /path/to/directory

# Analyze single file
panopticas file filename.py

# Find URLs in directory
panopticas urls /path/to/directory

# Find AI coding agent files and directories
panopticas ai
panopticas ai /path/to/directory
panopticas ai --all-files          # include gitignored files and bare AI directories

# Show the vocabularies panopticas uses
panopticas tags
panopticas languages
panopticas filetypes

# Any command can emit JSON
panopticas assess --json
```

## File Structure

- `src/panopticas/` — Package source code
  - `core.py` — Main analysis functions
  - `cli.py` — CLI interface using Click
  - `constants.py` — File type and metadata mappings
  - `__init__.py` — Package exports
- `src/tests/` — Test fixture files (sample files for analysis)
- `pyproject.toml` — Build configuration and dependencies
- `requirements.txt` — Pinned Python dependencies
- `CHANGELOG.md` — Version history following Keep a Changelog format
- `docs/` — The panopticas.io website (see below)

## The docs site

`docs/` is the published GitHub Pages site for [panopticas.io](https://panopticas.io),
not a place for working documents. Pages is configured as `build_type: "legacy"`
serving `main:/docs`, which means GitHub builds it with its own `github-pages`
gem set (Jekyll 3.9.x) and **ignores `docs/Gemfile` and `docs/Gemfile.lock`
entirely**.

Those two files are therefore local-preview scaffolding only, and are
gitignored — tracking them produced Dependabot alerts for gems the published
site never uses. They still exist in a working checkout; recreate them with
`bundle init` and `gem "jekyll", "~> 4.3"` if they are missing.

To preview locally:

```bash
cd docs && bundle exec jekyll serve
```

Note the fidelity gap: local preview runs Jekyll 4.x while Pages publishes with
Jekyll 3.9.x. Fine for markdown pages and the existing layout; do not rely on it
for Jekyll-4-only features.

Adding a page means front matter (`layout: default` plus a `title`) — without it
Jekyll copies the file verbatim instead of rendering it — and a nav entry in
`docs/_layouts/default.html`.

## Dependencies

- **Click** (>=8.3.1) — CLI framework
- **rich** (>=14.0.0) — Table formatting for CLI output
- **pathspec** (>=0.12.1) — Git-style path matching for `.gitignore` support

## Code Style

- Python 3.12+ required
- Follow existing patterns in the codebase
- Constants and mappings go in `constants.py`
- Analysis logic goes in `core.py`
- CLI commands go in `cli.py`
- When adding new file types, update both the extension mapping and any relevant metadata detection

## Testing

When making changes:
1. Run any existing automated tests: `pytest -v`
2. Manually test CLI commands to ensure functionality
3. Test with the fixture files in `src/tests/`
4. If adding new file types, add corresponding test fixture files

## Change Documentation

Each feature or significant change should have a markdown file in `/changes/`. Naming convention: `YYYYMM-short-description.md`.

Design specs and implementation plans live under `/changes/design/specs/` and
`/changes/design/plans/`, named `YYYY-MM-DD-short-description[-design].md`.

**Do not put working documents in `docs/`.** `docs/` is the published GitHub Pages
site for [panopticas.io](https://panopticas.io) — anything added there is public
web content, not repository documentation.

## Release Process

1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md` with the new version and changes
3. Run tests: `pytest -v`
4. Build: `python -m build`
5. Upload to PyPI: `twine upload dist/panopticas-X.Y.Z*` — scope the glob to this release; `dist/*` re-sends every past artifact and the upload aborts on the duplicates
6. Tag the release:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
7. Create GitHub release:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG.md
   ```
8. Update `panopticas==X.Y.Z` in kospex's `pyproject.toml` — kospex uses an **exact pin**, so a new release does not reach it until this is bumped. This step is mandatory, not conditional.

## Relationship to kospex

Panopticas is used by kospex for file type detection and metadata extraction. Key integration points:
- `kospex_core.py` uses panopticas for file metadata during sync
- `kospex_git.py` calls `get_filename_metatypes()` and stores the result as `tech_type`
- `kospex_schema.py` encodes tags as `|tag1|tag2|`; `kospex_query.py` queries them with `tech_type LIKE '%|tag|%'`
- `kospex_core.py` tracks `last_panopticas_version` and re-syncs when it changes, so a version bump re-tags already-synced repos
- kospex pins `panopticas==X.Y.Z` in its `pyproject.toml` — an **exact** pin, so releases do not flow through until it is bumped. Read the current value from kospex's `pyproject.toml` rather than trusting a version quoted here; this line claimed `0.0.16` long after kospex had moved to `0.0.17`

When making breaking changes to panopticas, check kospex integration points first. Adding a tag is safe; renaming or removing one is not, since kospex stores tags in a database that is only refreshed on re-sync.
