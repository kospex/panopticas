---
layout: default
title: API Reference
---

# API Reference

Panopticas provides constants and functions for file type detection and metadata extraction.

## Constants

### EXT_FILETYPES

A dictionary mapping file extensions to language names. Contains 50+ entries covering common programming languages, data formats, and configuration files.

```python
from panopticas.constants import EXT_FILETYPES

EXT_FILETYPES[".py"]      # "Python"
EXT_FILETYPES[".js"]      # "JavaScript"
EXT_FILETYPES[".yaml"]    # "YAML"
EXT_FILETYPES["dockerfile"]  # "Dockerfile" (special case)
```

**Sample entries:**
- `.py` -> `Python`
- `.js` -> `JavaScript`
- `.ts` -> `TypeScript`
- `.go` -> `Go`
- `.rs` -> `Rust`
- `.java` -> `Java`
- `.rb` -> `Ruby`
- `.yaml`, `.yml` -> `YAML`
- `.json` -> `JSON`
- `dockerfile` -> `Dockerfile`

### LANGUAGE_BY_BASENAME

A dictionary for special filenames that identify a language by their exact name.

```python
from panopticas.constants import LANGUAGE_BY_BASENAME

LANGUAGE_BY_BASENAME["go.mod"]  # "go.mod"
LANGUAGE_BY_BASENAME["go.sum"]  # "go.sum"
```

### METADATA_RULES

A dictionary containing rules for tagging files with metadata. Rules are organized by:

- **extension_rules**: Tags based on file extension (e.g., `.jar` -> `["binary"]`)
- **exact_filename_rules**: Tags for specific filenames (e.g., `pyproject.toml` -> `["build", "dependencies", "Python"]`)
- **path_contains_rules**: Tags based on path patterns (e.g., `.github/workflows` -> `["workflow", "pipeline", "GitHub"]`)
- **function_rules**: Tags determined by custom functions

**Example tags:**

| File | Tags |
|------|------|
| `pyproject.toml` | build, dependencies, Python |
| `package.json` | npm, dependencies |
| `.github/workflows/ci.yml` | workflow, pipeline, GitHub, Git |
| `Dockerfile` | IaC, Docker, dependencies |
| `go.mod` | Go, module, dependencies |

## Functions

### find_files

Find all files in a directory, respecting `.gitignore` patterns.

```python
from panopticas.core import find_files

files = find_files("/path/to/project")
# Returns: ["src/main.py", "README.md", "pyproject.toml", ...]
```

**Parameters:**
- `directory` (str): Path to the directory to scan
- `all_files` (bool, optional): If `True`, ignore `.gitignore` patterns

**Returns:** List of relative file paths

### get_language

Get the programming language of a file based on extension, basename, or shebang.

```python
from panopticas.core import get_language

get_language("app.py")           # "Python"
get_language("server.js")        # "JavaScript"
get_language("go.mod")           # "go.mod"
get_language("unknown_script")   # May detect via shebang, or "Unknown"
```

**Parameters:**
- `file_path` (str): Path to the file
- `skip_shebang` (bool, optional): If set, skip shebang detection

**Returns:** Language name as a string, or `"Unknown"`

### get_filename_metatypes

Get metadata tags for a file based on its name and path.

```python
from panopticas.core import get_filename_metatypes

get_filename_metatypes("pyproject.toml")
# Returns: ["build", "dependencies", "Python"]

get_filename_metatypes(".github/workflows/ci.yml")
# Returns: ["workflow", "pipeline", "GitHub", "Git"]

get_filename_metatypes("requirements.txt")
# Returns: ["pip", "Python", "PyPi", "dependencies"]
```

**Parameters:**
- `file_path` (str): Path to the file (relative or absolute)

**Returns:** List of metadata tag strings

### identify_files

Scan a directory and identify the language/type of all files.

```python
from panopticas.core import identify_files

results = identify_files("/path/to/project")
# Returns: {
#   "src/main.py": "Python",
#   "package.json": "JSON",
#   "Dockerfile": "Dockerfile",
#   ...
# }
```

**Parameters:**
- `directory` (str): Path to the directory to scan

**Returns:** Dictionary mapping relative file paths to their language/type

### extract_urls_from_file

Extract all HTTP/HTTPS URLs from a file.

```python
from panopticas.core import extract_urls_from_file

urls = extract_urls_from_file("README.md")
# Returns: ["https://github.com/example/repo", "https://docs.example.com"]
```

**Parameters:**
- `file_path` (str): Path to the file

**Returns:** List of URL strings

**Raises:**
- `FileNotFoundError`: If the file does not exist
- `UnicodeDecodeError`: If the file cannot be decoded as UTF-8
