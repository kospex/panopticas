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
└── constants.py      # File type mappings, metadata definitions, extension lookups
```

### Key Components

- **File Type Detection**: Uses extension mappings (`EXT_FILETYPES`) and shebang parsing to identify programming languages
- **Metadata Extraction**: Identifies build files, dependency manifests, CI configurations, and other special file types
- **URL Extraction**: Finds HTTP/HTTPS URLs within files using regex patterns
- **Git Integration**: Respects `.gitignore` patterns when scanning directories
- **Binary Detection**: Identifies binary file types (images, executables, archives)

## Development Commands

### Installation (Development)
```bash
pip install -e .
```

### Running Tests
```bash
pytest -v
```

Test fixture files are in `src/tests/` (sample files for analysis, not pytest tests). Automated tests should be added to a `tests/` directory in the project root.

### Build and Distribution
```bash
python -m build
python -m twine upload dist/*
```

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
- `docs/` — Website and documentation

## Dependencies

- **Click** (>=8.3.1) — CLI framework
- **prettytable** (>=3.17.0) — Table formatting for CLI output
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

## Release Process

1. Bump version in `pyproject.toml`
2. Update `CHANGELOG.md` with the new version and changes
3. Run tests: `pytest -v`
4. Build: `python -m build`
5. Upload to PyPI: `twine upload dist/*`
6. Tag the release:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
7. Create GitHub release:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG.md
   ```
8. If kospex pins this version, update `panopticas==X.Y.Z` in kospex's `pyproject.toml`

## Relationship to kospex

Panopticas is used by kospex for file type detection and metadata extraction. Key integration points:
- `kospex_core.py` uses panopticas for file metadata during sync
- `kospex_git.py` uses panopticas for repo file analysis
- kospex declares `panopticas>=0.0.14` in its `pyproject.toml`

When making breaking changes to panopticas, check kospex integration points first.
