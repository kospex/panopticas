# panopticas

Discover insights into the types of data and functions used in your code.

Inspired by tools like [enry](https://github.com/go-enry/go-enry) and [linguist](https://github.com/github-linguist/linguist)

Features: language detector and metadata identifiers, based on the filename extension, filename details and the shebang line. Detects build configurations, dependency manifests, CI pipeline files, AI coding agent artifacts, and binary file types.

The official documentation can be found at [panopticas.io](https://panopticas.io)

## Installation

```bash
pip install panopticas
```

Requires Python 3.12 or later.

## Usage

The examples below cover the common cases. For every command, every option and
the JSON shape each one emits, see the
[CLI reference](https://panopticas.io/cli).

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

To find URLs in files:

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
AI products the repository uses. See
[the AI detection rules reference](https://panopticas.io/ai-detection-rules) for
the full inventory, the source that confirms each convention, and the candidates
that were investigated and rejected.

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

## Development

If you want to check out the [panopticas repo](https://github.com/kospex/panopticas) and work on bug fixes, use the pip "editable" install:

```bash
pip install -e .
```

### Running Tests

```bash
pytest -v
```

## Relationship to kospex

Panopticas is a dependency of [kospex](https://github.com/kospex/kospex), which
uses it for file type detection and metadata extraction during repository sync.
Tags are stored in the kospex database, so adding a tag is safe but renaming or
removing one is a breaking change.

## Changelog

See [CHANGELOG.md](https://github.com/kospex/panopticas/blob/main/CHANGELOG.md) for version history.

## License

MIT
