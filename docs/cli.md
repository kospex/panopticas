---
layout: default
title: CLI Reference
description: Every panopticas command, its options, and the JSON document each one emits.
---

# CLI Reference

Panopticas has seven commands. Every one of them accepts `--json`.

| Command | Purpose |
|---|---|
| [`assess`](#assess) | Identify the file type and tags of every file in a directory |
| [`file`](#file) | Everything panopticas knows about one file |
| [`urls`](#urls) | Every HTTP/HTTPS URL referenced across a directory |
| [`ai`](#ai) | AI coding agent artifacts, by product and kind |
| [`tags`](#vocabularies) | Every tag panopticas can assign |
| [`languages`](#vocabularies) | Every language it recognises |
| [`filetypes`](#vocabularies) | Every file type, languages or not |

Run `panopticas COMMAND --help` for the same options inline.

## Global behaviour

`panopticas --version` prints the installed version. `panopticas` with no
command prints help and exits `0` — not `2`, which is what Click does by
default for a group with no subcommand.

Directory-scanning commands (`assess`, `urls`, `ai`) honour `.gitignore`. Each
has a flag to override that; note the spelling differs between them, `--all-files`
on `ai` and `-all-files` on `urls`, because the repository has always mixed
single- and double-dash long options.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, including `--help` and the bare `panopticas` invocation |
| `2` | Bad arguments — missing, or the wrong kind of path |

Path arguments are type-checked at the CLI boundary, so a mistake fails loudly
instead of producing empty output:

```console
$ panopticas assess src/app.py
Usage: panopticas assess [OPTIONS] [DIRECTORY]
Try 'panopticas assess --help' for help.

Error: Invalid value for '[DIRECTORY]': Directory 'src/app.py' is a file.
```

```console
$ panopticas file src
Error: Invalid value for 'FILE': File 'src' is a directory.
```

## JSON output

Every command accepts `--json`, also spelled `-json`.

In JSON mode **stdout carries the document and nothing else** — the progress
banner is redirected to stderr — so output pipes cleanly into `jq` or any
parser without a stripping step:

```console
$ panopticas assess --json 2>/dev/null | jq '.files[] | select(.language == "Python") | .path'
"src/app.py"

$ panopticas assess --json 2>&1 >/dev/null
Assessing current directory.
```

Every document is a JSON object, never a bare array, so fields can be added
without breaking consumers.

---

## assess

Identify the file type and metadata tags of every file in a directory.

```
panopticas assess [OPTIONS] [DIRECTORY]
```

`DIRECTORY` defaults to the current directory. It must be a directory.

| Option | Effect |
|---|---|
| `-unknown` | Show only files whose type could not be identified |
| `--lines` | Add a line count column, and a total |
| `--json`, `-json` | Emit JSON |

```console
$ panopticas assess
                             Assessment of .
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File                      ┃ Language  ┃ Meta                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ requirements.txt          │ Text      │ pip, Python, PyPi,             │
│                           │           │ dependencies                   │
│ pyproject.toml            │ TOML      │ build, dependencies, Python    │
│ .gitignore                │ Gitignore │ Git, ignore                    │
│ CLAUDE.md                 │ Markdown  │ AI, Claude, instructions       │
│ .claude/commands/build.md │ Markdown  │ AI, Claude, command            │
│ src/app.py                │ Python    │                                │
└───────────────────────────┴───────────┴────────────────────────────────┘
                                 6 files
```

Long paths **fold** onto a second line rather than being truncated — an
ellipsis would cut the filename, which is the part identifying the row.

`-unknown` reports totals for the rows it shows, not for every file scanned.

### JSON

| Field | Type | Notes |
|---|---|---|
| `directory` | string | As given on the command line |
| `count` | number | Rows in `files`, after `-unknown` filtering |
| `files[].path` | string | Relative to `directory` |
| `files[].language` | string | `"Unknown"` when undetected — never `null` |
| `files[].meta` | array of string | Tags; empty array when none |
| `files[].lines` | number or null | `--lines` only; `null` for binary and unreadable files |
| `total_lines` | number | `--lines` only; excludes the `null` entries |

```json
{
  "directory": ".",
  "count": 6,
  "files": [
    {
      "path": "requirements.txt",
      "language": "Text",
      "meta": ["pip", "Python", "PyPi", "dependencies"]
    },
    {
      "path": "src/app.py",
      "language": "Python",
      "meta": []
    }
  ]
}
```

---

## file

Everything panopticas can determine about a single file.

```
panopticas file [OPTIONS] FILE
```

`FILE` is required and must be a file, not a directory.

| Option | Effect |
|---|---|
| `--json`, `-json` | Emit JSON |

```console
$ panopticas file src/app.py

Assessing filetype for file src/app.py

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Method           ┃ Result                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ File extension   │ .py                      │
│ File type        │ Python                   │
│ Shebang          │ #!/usr/bin/env python3   │
│ Shebang Language │ Python                   │
│ Meta             │                          │
│ URLs             │ https://example.com/docs │
└──────────────────┴──────────────────────────┘
```

This is the only command that reads file contents beyond the first line — it
extracts URLs from the whole file.

### JSON

| Field | Type | Notes |
|---|---|---|
| `file` | string | As given on the command line |
| `extension` | string | The basename when the file has no extension |
| `filetype` | string or null | `null` when the extension is not recognised |
| `shebang` | string or null | The raw first line, when it is a shebang |
| `shebang_language` | string or null | Derived from `shebang` |
| `meta` | array of string | Tags; empty array when none |
| `urls` | array of string | HTTP/HTTPS URLs found in the file |

```json
{
  "file": "src/app.py",
  "extension": ".py",
  "filetype": "Python",
  "shebang": "#!/usr/bin/env python3",
  "shebang_language": "Python",
  "meta": [],
  "urls": ["https://example.com/docs"]
}
```

Note that `filetype` here is the **extension lookup only**. It is `null` for a
file identified by basename or shebang alone, where `assess` would still report
a language.

---

## urls

Every HTTP/HTTPS URL referenced across a directory.

```
panopticas urls [OPTIONS] DIRECTORY
```

`DIRECTORY` is **required** for this command — unlike `assess` and `ai`, it does
not default to the current directory. It must be a directory.

| Option | Effect |
|---|---|
| `-all-files` | Include gitignored files (single dash) |
| `--json`, `-json` | Emit JSON |

```console
$ panopticas urls .
                       URLs in .
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Filename                  ┃ URLs                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ requirements.txt          │                          │
│ pyproject.toml            │                          │
│ .gitignore                │                          │
│ CLAUDE.md                 │                          │
│ .claude/commands/build.md │                          │
│ src/app.py                │ https://example.com/docs │
└───────────────────────────┴──────────────────────────┘
                        6 files
```

Every scanned file gets a row, including those with no URLs. Binary files are
reported as having no URLs rather than aborting the scan.

### JSON

| Field | Type | Notes |
|---|---|---|
| `directory` | string | As given on the command line |
| `count` | number | Files scanned, not URLs found |
| `files[].path` | string | Relative to `directory` |
| `files[].urls` | array of string | Empty array when none |

```json
{
  "directory": ".",
  "count": 6,
  "files": [
    { "path": "pyproject.toml", "urls": [] },
    { "path": "src/app.py", "urls": ["https://example.com/docs"] }
  ]
}
```

To get a flat, deduplicated list:

```console
$ panopticas urls . --json | jq -r '.files[].urls[]' | sort -u
```

---

## ai

Find the artifacts left by AI coding agents, with the product and the kind of
artifact each one is.

```
panopticas ai [OPTIONS] [DIRECTORY]
```

`DIRECTORY` defaults to the current directory. It must be a directory.

| Option | Effect |
|---|---|
| `--all-files` | Include gitignored files, and bare AI directories (double dash) |
| `--json`, `-json` | Emit JSON |

```console
$ panopticas ai

Assessing current directory.

                  AI artifacts in .
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Path                      ┃ Product ┃ Kind         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ .claude/commands/build.md │ Claude  │ command      │
│ CLAUDE.md                 │ Claude  │ instructions │
└───────────────────────────┴─────────┴──────────────┘
               2 AI paths • Claude (2)
```

Detection is **path-based only** — no file is opened to determine AI metadata.
See the [AI detection rules reference](/ai-detection-rules) for every rule and
the source that confirms it.

`--all-files` additionally emits the AI directories themselves, with
`kind: "directory"`:

```console
$ panopticas ai --all-files --json 2>/dev/null | jq -r '.paths[] | "\(.kind)\t\(.path)"'
directory       .claude/
directory       .claude/commands/
command .claude/commands/build.md
instructions    CLAUDE.md
```

### JSON

| Field | Type | Notes |
|---|---|---|
| `directory` | string | As given on the command line |
| `count` | number | Entries in `paths` |
| `products` | object | Product name to count, most-used first, then alphabetical |
| `paths[].path` | string | Relative to `directory`, sorted |
| `paths[].product` | string | Brand-level: `Claude`, not `Claude Code` |
| `paths[].kind` | string | One of the 14 artifact kinds |

```json
{
  "directory": ".",
  "count": 2,
  "products": { "Claude": 2 },
  "paths": [
    { "path": ".claude/commands/build.md", "product": "Claude", "kind": "command" },
    { "path": "CLAUDE.md", "product": "Claude", "kind": "instructions" }
  ]
}
```

`products` is the quickest answer to "which AI tools does this repo use?":

```console
$ panopticas ai --json 2>/dev/null | jq -r '.products | keys[]'
Claude
```

---

## Vocabularies

Three commands print what panopticas knows, taking no arguments beyond `--json`.

```
panopticas tags
panopticas languages
panopticas filetypes
```

| Command | Answers |
|---|---|
| `tags` | Every tag that can appear in an `assess` **Meta** column |
| `languages` | Every file type that is a programming language |
| `filetypes` | Every file type, languages and non-languages alike |

`languages` is a subset of `filetypes`; the remainder are things like `PNG`,
`Lock` and `Gitignore` that have a type but are not languages.

The tag vocabulary is **derived from the detection rules themselves** rather
than maintained as a separate list, so it cannot drift from what the tool
actually assigns.

```console
$ panopticas tags

.NET           agent      Agents      AI            Aider
Amazon Q       Apache     ASP.NET     Augment       Azure DevOps
binary         Bitbucket  build       Buildkite     C#
...

85 tags
```

Values are sorted case-insensitively, so `binary` sorts near `Bitbucket`
rather than after `ZIP`.

### JSON

Each command returns its values under a key named after the command, plus a
count.

| Command | Shape |
|---|---|
| `tags` | `{"tags": [...], "count": 85}` |
| `languages` | `{"languages": [...], "count": 32}` |
| `filetypes` | `{"filetypes": [...], "count": 76}` |

```console
$ panopticas languages --json | jq -r '.count'
32
```

These are useful for building a filter UI, or for diffing two releases to see
what a version bump added:

```console
$ panopticas tags --json | jq -r '.tags[]' > tags-new.txt
$ diff tags-old.txt tags-new.txt
```
