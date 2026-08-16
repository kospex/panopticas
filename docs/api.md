---
layout: default
title: API Reference
---

# API Reference

Panopticas provides constants and functions for file type detection and metadata extraction.

Everything listed here is exported from the top-level package:

```python
import panopticas

panopticas.get_language("app.py")   # "Python"
panopticas.VERSION                  # "0.0.19"
```

The examples below import from `panopticas.core` and `panopticas.constants`, which
is equivalent and makes the origin of each name explicit.

## Constants

### EXT_FILETYPES

A dictionary mapping file extensions to file type names. 81 entries covering
programming languages, data formats, configuration files and binary formats.

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

### LANGUAGE_FILETYPES and NON_LANGUAGE_FILETYPES

`EXT_FILETYPES` mixes two kinds of value: things that are programming languages
(`Python`, `Go`) and things that are file types but not languages (`PNG`,
`Gitignore`, `Lock`). These two collections classify every value in the table —
32 languages and 44 non-languages. `get_languages()` and `get_filetypes()` read
from them.

```python
from panopticas.constants import LANGUAGE_FILETYPES, NON_LANGUAGE_FILETYPES

"Python" in LANGUAGE_FILETYPES       # True
"PNG" in NON_LANGUAGE_FILETYPES      # True
```

A test asserts that every `EXT_FILETYPES` value appears in exactly one of the
two, so adding an extension without classifying it fails the suite.

### LANGUAGE_BY_BASENAME

A dictionary for special filenames that identify a file type by their exact name,
used where a file has no meaningful extension, or where the extension is too
ambiguous to map globally.

```python
from panopticas.constants import LANGUAGE_BY_BASENAME

LANGUAGE_BY_BASENAME["go.mod"]     # "go.mod"
LANGUAGE_BY_BASENAME["go.sum"]     # "go.sum"
LANGUAGE_BY_BASENAME["setup.cfg"]  # "INI"
```

`setup.cfg` is the illustrative case: it is read by `configparser`, so it is INI —
but `.cfg` is used for arbitrary formats elsewhere, so the mapping is by basename
rather than by extension.

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
| `setup.py` | build, dependencies, Python, setuptools |
| `package.json` | npm, dependencies |
| `.github/workflows/ci.yml` | workflow, pipeline, GitHub, Git |
| `Dockerfile` | IaC, Docker, dependencies |
| `go.mod` | Go, module, dependencies |

### AI_RULES

The AI coding agent detection table. Maps an indicator to a `(product, kind)`
pair across three match modes:

| Mode | Entries | Matched against |
|------|---------|-----------------|
| `exact_filename` | 25 | the basename, lowercased |
| `path_contains` | 31 | a fragment of the path, ending in `/` |
| `filename_suffix` | 4 | the end of the basename |

Precedence is exact filename, then the longest matching path fragment, then the
longest matching suffix. First hit wins, so exactly one `(product, kind)` is
returned for any path.

```python
from panopticas.constants import AI_RULES

AI_RULES["exact_filename"]["claude.md"]   # ("Claude", "instructions")
AI_RULES["path_contains"][".cursor/rules/"]  # ("Cursor", "rules")
```

Products are brand-level — `Claude` covers both Claude Code and Claude Desktop.
Artifacts owned by no single brand use a pseudo-product (`Agents`, `MCP`,
`llms.txt`).

See the [AI detection rules reference](/ai-detection-rules) for the full
inventory, the source that confirms each convention, and the candidates that were
investigated and rejected.

### AI_ARTIFACT_KINDS

The closed set of 14 artifact kinds an `AI_RULES` entry may use:

`agent`, `chatmode`, `command`, `config`, `directory`, `docs`, `history`,
`hook`, `ignore`, `instructions`, `plugin`, `prompt`, `rules`, `skill`

### IMPLICIT_TAGS

Tags that are assigned by detection logic rather than by a `METADATA_RULES`
entry — currently `("AI", "license")`. `get_tags()` unions these with the tags
derived from the rule tables so the published vocabulary stays complete.

### VERSION

The installed package version, read from package metadata via
`importlib.metadata`. `pyproject.toml` is the single source of truth.

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

**Returns:** List of paths relative to `directory`

Paths are relative to the scanned directory, not to the current working
directory. Join them back onto `directory` before opening them.

### get_language

Get the file type of a file based on extension, basename, or shebang.

```python
from panopticas.core import get_language

get_language("app.py")           # "Python"
get_language("server.js")        # "JavaScript"
get_language("go.mod")           # "go.mod"
get_language("unknown_script")   # May detect via shebang, or "Unknown"
```

**Parameters:**
- `file_path` (str): Path to the file
- `skip_shebang` (bool, optional): If set, skip shebang detection — filename-only
  detection, which does not open the file

**Returns:** File type name as a string, or `"Unknown"` (also available as
`panopticas.core.UNKNOWN`)

### get_fileext

Get the extension of a path, falling back to the basename when there is none.

```python
from panopticas.core import get_fileext

get_fileext("app.py")          # ".py"
get_fileext("Dockerfile")      # "Dockerfile"
get_fileext("src/.gitignore")  # ".gitignore"
```

**Returns:** The extension including the leading dot, or the basename if the path
has no extension.

### get_extension_filetype

Look up a single extension in `EXT_FILETYPES`. Case-insensitive.

```python
from panopticas.core import get_extension_filetype

get_extension_filetype(".PY")     # "Python"
get_extension_filetype(".nope")   # None
```

**Returns:** File type name, or `None` if the extension is not known.

### get_language_edge_cases

Look up a basename in `LANGUAGE_BY_BASENAME`.

```python
from panopticas.core import get_language_edge_cases

get_language_edge_cases("setup.cfg")  # "INI"
get_language_edge_cases("app.py")     # None
```

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

get_filename_metatypes("CLAUDE.md")
# Returns: ["AI", "Claude", "instructions"]
```

**Parameters:**
- `file_path` (str): Path to the file (relative or absolute)

**Returns:** List of metadata tag strings

AI tags are derived from `get_ai_metadata()`, so any product added to `AI_RULES`
appears here without further changes.

### get_ai_metadata

Return AI coding agent metadata for a path.

```python
from panopticas.core import get_ai_metadata

get_ai_metadata("CLAUDE.md")
# Returns: {"product": "Claude", "kind": "instructions"}

get_ai_metadata(".cursor/rules/style.mdc")
# Returns: {"product": "Cursor", "kind": "rules"}

get_ai_metadata("README.md")
# Returns: None
```

**Parameters:**
- `file_path` (str): Path to inspect

**Returns:** `{"product": str, "kind": str}`, or `None` if the path is not a
recognised AI agent artifact

This is pure path inspection — the file is never opened, and it does not need to
exist. It is the single source of truth for AI detection; `get_filename_metatypes()`
and the `panopticas ai` command both derive from it.

### find_ai_files

Find the AI coding agent artifacts in a directory tree.

```python
from panopticas.core import find_ai_files

find_ai_files("/path/to/project")
# Returns: {
#   "CLAUDE.md": {"product": "Claude", "kind": "instructions"},
#   ".claude/settings.local.json": {"product": "Claude", "kind": "config"},
# }
```

**Parameters:**
- `directory` (str): Path to the directory to scan
- `all_files` (bool, optional): If `True`, include gitignored files and bare AI
  directories

**Returns:** Dictionary mapping relative path to its AI metadata

### identify_files

Scan a directory and identify the file type of all files.

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

**Returns:** Dictionary mapping relative file paths to their file type

### identify_files_with_metrics

As `identify_files`, but also counts lines.

```python
from panopticas.core import identify_files_with_metrics

identify_files_with_metrics("/path/to/project")
# Returns: {
#   "src/main.py": {"type": "Python", "lines": 240},
#   "logo.png":    {"type": "PNG", "lines": "N/A"},
# }
```

**Returns:** Dictionary mapping relative file path to `{"type": ..., "lines": ...}`

### count_lines

Count the lines in a file.

```python
from panopticas.core import count_lines

count_lines("src/main.py")   # 240
count_lines("logo.png")      # "N/A"
```

**Returns:** `int`, or the string `"N/A"` for binary files, missing files, and
other read errors. This function does not raise.

### get_tags

Return every tag panopticas can assign to a file.

```python
from panopticas.core import get_tags

get_tags()
# Returns: ['.NET', 'agent', 'Agents', 'AI', 'Aider', ..., 'yarn']  (85 tags)
```

**Returns:** Sorted list of tag strings, case-insensitively ordered

The vocabulary is derived from the detection rules themselves — `METADATA_RULES`,
`AI_RULES` and `IMPLICIT_TAGS` — rather than maintained as a separate list, so it
cannot drift from what the tool actually assigns.

### get_filetypes

Return every file type panopticas recognises, languages or not.

```python
from panopticas.core import get_filetypes

get_filetypes()
# Returns: ['Apache JMeter', 'ASP.NET', ..., 'ZIP']  (76 file types)
```

**Returns:** Sorted list of file type strings

### get_languages

Return every file type that is a programming language.

```python
from panopticas.core import get_languages

get_languages()
# Returns: ['C', 'C Header', 'C#', 'C++', 'CSS', ..., 'Vue']  (32 languages)
```

**Returns:** Sorted list of language names — the subset of `get_filetypes()`
classified as `LANGUAGE_FILETYPES`

### check_shebang

Read the first line of a file and return it if it is a shebang.

```python
from panopticas.core import check_shebang

check_shebang("script")   # "#!/usr/bin/env python3"
check_shebang("app.py")   # None
```

**Returns:** The stripped shebang line, or `None` if there is none, the file is
missing, or it cannot be decoded. This function does not raise.

### extract_shebang_language / get_shebang_language

Map a shebang line to a language name. `get_shebang_language` is a thin wrapper
over `extract_shebang_language`.

```python
from panopticas.core import extract_shebang_language

extract_shebang_language("#!/usr/bin/env python3")  # "Python"
extract_shebang_language("#!/bin/bash")             # "bash"
extract_shebang_language("#!/usr/local/bin/perl")   # "perl"
```

**Returns:** Language or interpreter name as a string, or `None`

### extract_urls

Extract HTTP/HTTPS URLs from a string.

```python
from panopticas.core import extract_urls

extract_urls("see https://a.com and http://b.org/x")
# Returns: ["https://a.com", "http://b.org/x"]
```

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
- `UnicodeDecodeError`: If the file cannot be decoded as UTF-8 — binary files
  raise this, so callers scanning a whole tree should catch it

### is_pip_requirements

Test whether a filename looks like a pip requirements file.

```python
from panopticas.core import is_pip_requirements

is_pip_requirements("requirements.txt")       # True
is_pip_requirements("requirements-dev.txt")   # True
is_pip_requirements("reqs.txt")               # False
```

**Returns:** `bool`. Used as a `function_rule` in `METADATA_RULES`.

### load_gitignore_patterns

Load the `.gitignore` patterns for a directory.

```python
from panopticas.core import load_gitignore_patterns

spec = load_gitignore_patterns("/path/to/project")
spec.match_file("build/output.o")   # True
```

**Returns:** A `pathspec.PathSpec`, or `None` if the directory has no
`.gitignore`. Used internally by `find_files`, `identify_files` and
`find_ai_files`.
