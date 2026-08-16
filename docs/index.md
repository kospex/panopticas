---
layout: default
title: Panopticas
---

# panopticas

Panopticas helps understand file types with metadata tags, similar to tools like [enry](https://github.com/go-enry/go-enry) and [linguist](https://github.com/github-linguist/linguist)

The core functionality is a language detector and metadata identifier, based on the filename extension, filename details and the shebang line.

## Why another detector?

The metadata tagging is where panopticas differs from other tools.

Some files have a "language" like XML or YAML, but the filetype is actually a specific product file.

For example:
- pom.xml is a Maven project file, but the language is XML.
- package.json is a Node.js project file, but the language is JSON.
- requirements.txt is a pip project file, but the language is text.
- .github/workflows/python.yml is a GitHub Actions workflow file, but the language is YAML, but it's specific to GitHub Actions.

Panopticas helps provide more context for files that are not just a language, but a specific product file.

## Installation

```bash
pip install panopticas
```

Requires Python 3.12 or later.

## Usage

The examples below cover the common cases. For every command, every option and
the JSON shape each one emits, see the [CLI reference](/cli).

Change into the directory you want to check the file types of and then run:

```bash
panopticas assess
```

`assess` respects `.gitignore`. Two options change what it reports:

```bash
panopticas assess -unknown        # only files whose language could not be identified
panopticas assess --lines         # include a line count for each file
```

To check a single file and get some metadata:

```bash
panopticas file FILENAME
```

To find the URLs referenced across a directory:

```bash
panopticas urls /path/to/directory
panopticas urls /path/to/directory -all-files   # include gitignored files
```

### AI coding agent detection

Panopticas identifies the file and directory artifacts left by AI coding agents,
and tags each one with three tags: `AI`, the product brand, and the kind of
artifact.

```
CLAUDE.md                       -> AI, Claude, instructions
.cursor/rules/style.mdc         -> AI, Cursor, rules
.github/copilot-instructions.md -> GitHub, Git, AI, Copilot, instructions
```

Detection is path-based only — no file is opened to determine AI metadata.

```bash
panopticas ai
panopticas ai /path/to/directory
panopticas ai --all-files   # include gitignored files and bare AI directories
```

The command lists each artifact with its product and kind, then summarises which
AI products the repository uses.

The [AI detection rules reference](/ai-detection-rules) documents every rule, the
source that confirms each convention, and the candidates that were investigated
and rejected.

### Vocabularies

Three commands print the vocabularies panopticas works with. The tag list is
derived from the detection rules themselves, so it cannot drift from what the
tool actually assigns.

```bash
panopticas tags        # every tag panopticas can assign to a file
panopticas languages   # every language it recognises
panopticas filetypes   # every file type, languages or not
```

### JSON output

Every command accepts `--json` (also spelled `-json`). In JSON mode stdout
carries only the document — progress messages go to stderr — so output can be
piped safely:

```bash
panopticas assess --json | jq '.files[] | select(.language == "Python")'
panopticas ai --json | jq '.products'
```

### API reference

Check out the simple explanation of the [API reference](/api), and if you need more detail, check out the few python classes in /src/panopticas/
