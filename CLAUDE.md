# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Panopticas is a Python CLI tool for analyzing file types, languages, and metadata in codebases. It identifies programming languages by file extensions, shebangs, and filenames, and extracts metadata like dependencies, build configurations, and URLs from files.

## Architecture

The project consists of two main Python modules:

- `src/panopticas.py`: Core analysis engine containing file type detection, language identification, and metadata extraction functions
- `src/panopticas_cli.py`: Click-based CLI interface with commands for assessing directories and individual files

### Key Components

- **File Type Detection**: Uses extension mappings (`EXT_FILETYPES`) and shebang parsing to identify programming languages
- **Metadata Extraction**: Identifies build files, dependency manifests, CI configurations, and other special file types
- **URL Extraction**: Finds HTTP/HTTPS URLs within files using regex patterns
- **Git Integration**: Respects `.gitignore` patterns when scanning directories

## Development Commands

### Installation (Development)
```bash
pip install -e .
```

### Build and Distribution
```bash
# Build the package
python -m build

# Upload to PyPI (requires twine)
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

- `src/panopticas.py`: Main analysis functions and constants
- `src/panopticas_cli.py`: CLI interface using Click framework
- `pyproject.toml`: Build configuration and dependencies
- `requirements.txt`: Python dependencies
- `CHANGELOG.md`: Version history following Keep a Changelog format

## Dependencies

The project uses:
- Click: CLI framework
- prettytable: Table formatting for CLI output
- pathspec: Git-style path matching for `.gitignore` support
- twine: Package distribution
- build: Python package building

## Testing and Quality

The project does not currently have automated tests or linting configured. When making changes, manually test the CLI commands to ensure functionality.