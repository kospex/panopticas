# Tag Vocabulary, JSON Output and Rich Migration — Design

**Date:** 2026-08-10
**Status:** Designed. Targets 0.0.19.

## Problem

Panopticas emits tags (`get_filename_metatypes()`) and file types
(`get_language()`), but there is no way to ask what the complete vocabulary
*is*. A consumer — kospex building a filter UI, a person writing a
`tech_type LIKE '%|tag|%'` query, an AI agent reasoning about a repo — has to
read `constants.py` and union the values by hand, and has no way to tell what
a new release added.

Two adjacent problems surfaced while designing that:

- Every CLI command prints a `prettytable`. kospex and foundationx have both
  moved to `rich`; panopticas is the odd one out.
- Every CLI command prints only human-formatted tables. An AI tool invoking
  `panopticas assess` has to parse ASCII box drawing to recover the data.

## Goal

Three library functions returning the vocabularies, three CLI commands
exposing them, `--json` on every command, and the `prettytable` → `rich`
migration. Shipped as one release.

## Decisions

| Decision | Choice |
|---|---|
| Derivation | Traversal of the existing constants — never a hand-maintained list |
| Functions | `get_tags()`, `get_filetypes()`, `get_languages()` |
| Return type | Sorted `list[str]`, deduplicated, `key=str.lower` |
| `directory` kind | **Excluded** from `get_tags()` |
| Language classification | Explicit set in `constants.py` + completeness test |
| CLI commands | `tags`, `languages`, `filetypes` — one per function |
| Vocabulary display | `rich.columns.Columns` grid; `--json` serves machines |
| JSON flag | Both `--json` and `-json` accepted |
| JSON top level | Always an object, never a bare array |
| Table library | `rich`, replacing `prettytable` in all four existing commands |
| Release | One version, three phased commits |

## Part 1 — Vocabulary derivation

### Why traversal, not a list

`METADATA_RULES` and `AI_RULES` are already dicts whose *values* are the tags.
The vocabulary is a set union over them. This is not Python reflection
(`inspect`/`dir()`) — just iterating data structures that already exist.

A hardcoded array is the wrong answer here specifically because adding rules
is the main way this repository changes. A list would drift on the first new
rule; a traversal cannot drift, because a new rule is in the vocabulary the
instant it is added.

```python
def get_tags():
    """Return every tag get_filename_metatypes() can emit, sorted."""
    tags = set(IMPLICIT_TAGS)
    for rules in ("extension_rules", "exact_filename_rules", "path_contains_rules"):
        for tag_list in METADATA_RULES[rules].values():
            tags.update(tag_list)
    for _, tag_list in METADATA_RULES["function_rules"]:
        tags.update(tag_list)
    for match_mode in AI_RULES.values():
        for product, kind in match_mode.values():
            tags.update((product, kind))
    return sorted(tags, key=str.lower)
```

Current result: **85 tags**.

### `IMPLICIT_TAGS`

Two tags are string literals inside `get_filename_metatypes()` rather than
entries in a rule table — `"AI"` at `core.py:109` and `"license"` at
`core.py:102`. `"license"` cannot become an `exact_filename_rule` because it
matches on the basename *minus* extension, covering `LICENSE`, `license.md`
and `license.txt`.

Add to `constants.py`:

```python
# Tags emitted directly by get_filename_metatypes() rather than by a rule
# table: "AI" prefixes every AI artifact's tags, and "license" is matched on
# the basename-without-extension so it cannot be an exact_filename rule.
IMPLICIT_TAGS = ("AI", "license")
```

and change `core.py` to reference it instead of the literals. This is the only
modification to existing detection code in Part 1 — it keeps one source of
truth rather than restating the two tags in `get_tags()`.

### Why `directory` is excluded

`AI_ARTIFACT_KINDS` declares 14 kinds; `AI_RULES` uses 13. The fourteenth,
`directory`, is synthesised inside `find_ai_files(all_files=True)` and never
returned by `get_filename_metatypes()`.

It is therefore unreachable from a tag search. Git does not track empty
directories, so a bare `.claude/skills/` never becomes a file row in kospex
and `tech_type` can never contain `|directory|`. Asked about the same path
directly, `get_filename_metatypes(".claude/skills/")` returns
`["AI", "Claude", "skill"]`.

`get_tags()` therefore derives AI kinds from the values present in `AI_RULES`,
not from `AI_ARTIFACT_KINDS`, so every tag it returns is one a consumer can
actually search for. A test asserts `"directory" not in get_tags()` so the
exclusion is deliberate rather than incidental.

## Part 2 — Filetypes and languages

`get_filetypes()` is a traversal like `get_tags()`:
`set(EXT_FILETYPES.values()) | set(LANGUAGE_BY_BASENAME.values())` — **76
values**. It is the full vocabulary `get_language()` can return from the
lookup tables.

Two documented caveats:

- Shebang detection can return an interpreter name outside the list
  (`bash`, `awk`, `ruby`), since it derives from file contents rather than
  a table.
- `UNKNOWN` (`"Unknown"`) is a sentinel for unrecognised files, not a member
  of the vocabulary.

### The language subset

`get_languages()` cannot be derived — nothing in the data says whether `PNG`
is a language. Most of the 76 values are not: `PNG`, `ZIP`, `Gitignore`,
`go.sum`, `nvmrc`, `Mailmap`, `CNAME`, `JSON`, `YAML`.

Classification principle: **a language expresses behaviour or presentation.**
Excluded are data and prose formats, binaries, named single-purpose files that
are a filename convention rather than a format, and framework or tool
artifacts whose actual language is something else.

The 44 excluded values:

| Group | Values |
|---|---|
| Binary / media | `DLL` `Excel` `Executable` `GIF` `ICO` `JPEG` `Java Archive` `Java Class` `PDF` `PNG` `ZIP` |
| Data & config formats | `CSV` `INI` `JSON` `Properties` `TOML` `TSV` `XML` `YAML` |
| Prose formats | `Markdown` `ReStructuredText` `Text` |
| Named files, not formats | `CNAME` `CODEOWNERS` `Dockerignore` `GitAttributes` `Gitignore` `GitLeaksIgnore` `Lock` `Mailmap` `nvmrc` `python-version` `go.mod` `go.sum` `SQLFluff` `SQLFluffIgnore` |
| Framework & tool file types | `ASP.NET` `ASP.NET Global` `ASP.NET User Control` `Apache JMeter` `C# Project` `SARIF` `SVG` `Visual Studio Solution` |

Leaving **32 languages**:

```
C, C Header, C#, C++, CSS, Dockerfile, Go, Groovy, Groovy Server Pages, HTML,
Java, JavaScript, JSX, Jupyter Notebook, Kotlin, Makefile, Objective-C, Perl,
PHP, PowerShell, Python, R, Ruby, Rust, Scala, Shell, SQL, Swift, Terraform,
TSX, TypeScript, Vue
```

Three judgement calls worth recording, since each will be questioned later:

- **Data and prose formats are excluded.** `JSON`, `XML`, `YAML`, `TOML`,
  `INI`, `Properties`, `Markdown` and `ReStructuredText` carry data or text,
  not behaviour. This also matches what GitHub displays — see below.
- **`HTML` and `CSS` are included.** They express presentation and are
  authored as the source of a page, which puts them on the behaviour side of
  the line rather than the data side.
- **`JSX` and `TSX` are both included.** They are syntax variants of
  JavaScript and TypeScript, not separate languages by every reading — but a
  `.tsx` file will not parse as plain TypeScript, and whichever way the call
  goes the pair must be treated identically.

The `ASP.NET` values are excluded because they name a framework, not a
language: the code in a `.aspx` or `.ascx` file is C# or Visual Basic. `SVG`
is an XML vocabulary for graphics.

### Alignment with GitHub Linguist

Most developers calibrate on the coloured language bar GitHub shows on a
repository, so it is the benchmark worth checking against.

Every entry in Linguist's `languages.yml` is nominally a "language", but the
`type` field decides what GitHub actually counts
(`lib/linguist/blob_helper.rb`):

```ruby
DETECTABLE_TYPES = [:programming, :markup].freeze

# Internal: Should this blob be included in repository language statistics?
def include_in_language_stats?
  ... language && DETECTABLE_TYPES.include?(language.type)
end
```

`data` and `prose` languages are therefore excluded from the bar. `JSON`,
`XML`, `YAML`, `TOML`, `INI`, `CSV`, `TSV` and `SVG` are `data`; `Markdown`,
`reStructuredText` and `Text` are `prose`. Excluding them from
`get_languages()` moves panopticas *towards* GitHub's behaviour, not away
from it — the opposite of the intuition that Linguist "counts Markdown as a
language".

The 32-value list agrees with GitHub's bar on 29 of 32. The three
disagreements are deliberate:

| Value | Linguist | Panopticas | Why |
|---|---|---|---|
| `JSX` | not a language — `.jsx` is JavaScript | included | Kept paired with `TSX`, which Linguist does have as `programming` |
| `SQL` | `data` | included | Linguist's typing is an outlier; excluding SQL from a language list would read as a bug |
| `ASP.NET` | `programming` | excluded | Names a framework — the code in `.aspx`/`.ascx` is C# or Visual Basic |

Verified against `github-linguist/linguist` `main` on 2026-08-10. Linguist
changes; treat this table as a snapshot, and re-check before citing it as
current.

### Keeping the classification honest

Store the exclusions in `constants.py` as `NON_LANGUAGE_FILETYPES`, and
enforce a **completeness test**: every value in `EXT_FILETYPES` and
`LANGUAGE_BY_BASENAME` must be classified. Adding an extension without
deciding whether it is a language fails `pytest` with the unclassified value
named.

This is what makes an explicit list acceptable here where it was rejected in
Part 1 — the drift is caught by the build rather than trusted to reviewers.

## Part 3 — CLI commands

Three commands, one per function:

| Command | Output |
|---|---|
| `panopticas tags` | 85 tags |
| `panopticas languages` | 32 languages |
| `panopticas filetypes` | 76 file types |

Human output is a `rich.columns.Columns` grid — 85 values in a compact block
rather than an 85-line scroll — with a count line beneath. Machine consumers
use `--json`, so human mode is free to optimise for reading.

## Part 4 — JSON output

`--json` and `-json` are both accepted on all seven commands. The repository
is already mixed (`-unknown`, `-all-files` alongside `--lines`,
`--all-files`), so accepting both means nothing anyone types is wrong:

```python
@click.option('--json', '-json', 'as_json', is_flag=True, default=False,
              help="Output as JSON.")
```

### Tighten the path arguments while the decorators are open

This phase edits every command's decorator block, which is the moment to fix
inconsistent path validation. Three of the four commands accept a
`click.Path` that does not constrain what kind of path it is:

| Command | Current | Should be | Why |
|---|---|---|---|
| `assess` | `click.Path(exists=True)` | `click.Path(exists=True, file_okay=False, dir_okay=True)` | Walks a directory; a file argument silently yields an empty result |
| `urls` | `click.Path(exists=True)` | `click.Path(exists=True, file_okay=False, dir_okay=True)` | Same — `find_files()` walks a directory |
| `file` | `click.Path(exists=True)` | `click.Path(exists=True, dir_okay=False)` | Opens the path; a directory argument raises `IsADirectoryError` from inside the handler |
| `ai` | already constrained | unchanged | — |

Validating at the Click boundary means a wrong path type fails with a clear
message before any handler runs, instead of producing an empty table or an
unhandled exception. The behaviour change is small and strictly an
improvement: arguments that currently "succeed" with empty output become
explicit errors.

Every JSON output is an object at the top level, never a bare array, so fields
can be added later without breaking a parser.

```jsonc
// panopticas tags --json
{"tags": ["...", "..."], "count": 85}
// languages --json  -> {"languages": [...], "count": 32}
// filetypes --json  -> {"filetypes": [...], "count": 76}

// panopticas assess --json      (meta is a real array, not "a, b, c")
{"directory": ".", "count": 42, "files": [
  {"path": "src/panopticas/core.py", "language": "Python", "meta": []},
  {"path": "CLAUDE.md", "language": "Markdown",
   "meta": ["AI", "Claude", "instructions"]}]}

// panopticas ai --json
{"directory": ".", "count": 3, "products": {"Claude": 3}, "paths": [
  {"path": "CLAUDE.md", "product": "Claude", "kind": "instructions"}]}

// panopticas file x.py --json
{"file": "x.py", "extension": ".py", "filetype": "Python", "shebang": null,
 "shebang_language": null, "meta": [], "urls": []}

// panopticas urls . --json
{"directory": ".", "count": 2, "files": [{"path": "README.md", "urls": ["..."]}]}
```

`assess --json` adds `"lines"` per file and a top-level `"total_lines"` **only
when `--lines` is passed**, so the document states what was actually measured
rather than emitting nulls. Binary files whose count is `"N/A"` emit
`"lines": null`.

Two behaviours matter for piping:

- **stdout carries only the JSON document.** The `Assessing directory: …` and
  `Found N files.` chatter moves to stderr in JSON mode.
- **Paths are emitted raw**, not passed through `sanitise_for_display()`. JSON
  escaping already neutralises control characters, and a consumer needs the
  true path to open the file.

## Part 5 — prettytable → rich

All four existing commands migrate. Leaving a mix of both libraries would be
worse than either.

- `pyproject.toml`: drop `prettytable>=3.17.0`, add `rich>=14.0.0`
- `requirements.txt`: regenerate

Following the foundationx pattern (`foundationx/src/foundationx/cli.py`):
module-level `console = Console()`, `Table(title=…, caption=…,
caption_style="dim")`, `add_column(justify=…, style=…)`,
`console.print(table)`. The trailing `Found 42 files.` and
`Products: Claude (3)` prints become table captions.

### Escaping is not optional

`cli.py:116-128` already strips C0/C1 control characters from filenames,
because panopticas scans repositories it does not control and a crafted path
could otherwise rewrite the operator's terminal.

Rich adds a second injection surface: it interprets `[...]` in cell values as
markup by default, so a file named `[blink]evil.py` would be rendered as
markup rather than displayed. Both treatments are needed:

```python
def cell(value):
    """Render an untrusted value safely: strip terminal control sequences,
    then neutralise rich's [markup] so a crafted path cannot style output."""
    return escape(sanitise_for_display(value))
```

Applied to **every path and URL that reaches the terminal**, not only table
cells. That includes the `Assessing directory: {directory}` banner lines,
which currently pass an argv-supplied path straight to `click.echo()`
unsanitised, and any rich `title=`/`caption=` string built from a path — rich
parses markup in those too.

Tags, products, kinds and file types come from `constants.py` and are trusted.

The JSON path is the deliberate exception, covered in Part 4: paths are
emitted raw because JSON escaping already neutralises control characters and
the output is not bound for a terminal.

### kospex impact

None. kospex declares `prettytable==3.17.0` and `rich>=14.0.0` as direct
dependencies, so dropping prettytable from panopticas does not disturb it and
rich is already in its tree.

kospex also depends on `panopticas>=0.0.18`, not the exact pin that
`CLAUDE.md` describes, so this release reaches kospex without a manual bump.
`CLAUDE.md`'s release step 8 is stale on that point; correcting it is out of
scope here.

## Testing

New `tests/test_vocabulary.py`:

1. **Drift test (the important one).** Synthesise a path from every rule key
   in `METADATA_RULES` and `AI_RULES`, run each through
   `get_filename_metatypes()`, and assert every tag produced is in
   `get_tags()`. Any future rule whose tags escape the vocabulary fails the
   build. This makes the contract self-enforcing rather than documented.
2. **Classification completeness.** Every `EXT_FILETYPES` /
   `LANGUAGE_BY_BASENAME` value is classified as language or non-language.
3. `set(get_languages()) <= set(get_filetypes())`.
4. `"directory" not in get_tags()`.
5. Each function returns a sorted, deduplicated list.
6. Spot-checks: `Claude`, `build`, `license`, `AI` in tags; `Python`, `HTML`,
   `JSX`, `TSX` in languages; `PNG`, `JSON`, `YAML`, `Markdown`, `SVG` and
   `ASP.NET` in filetypes but **not** in languages — these are the
   classification calls most likely to be changed by accident.

Extend `tests/test_panopticas.py` (or add `tests/test_cli_json.py`) with
Click `CliRunner` tests asserting each command's `--json` output parses and
carries the documented keys, and that `-json` behaves identically to `--json`.
Add boundary cases: a file passed where a directory is required (and the
reverse) exits non-zero with a Click usage error rather than reaching the
handler, and a filename containing rich markup and control characters renders
escaped in table output but survives verbatim in `--json`.

## Implementation phases

One spec, one plan, three commits, one release (0.0.19).

| Phase | Scope |
|---|---|
| 1 | `IMPLICIT_TAGS`, `NON_LANGUAGE_FILETYPES`, three functions, `__init__.py` exports, three CLI commands, vocabulary tests |
| 2 | `--json`/`-json` on all seven commands, `click.Path` constraints tightened, stdout/stderr split, JSON tests |
| 3 | prettytable → rich across all commands, `cell()` escaping, dependency swap |

Each phase is independently revertible. Also required before release: a change
document at `changes/2026-08-tag-vocabulary-and-cli-refactor.md` per
`CLAUDE.md`, and a `CHANGELOG.md` entry.

## Out of scope

- Reclassifying any existing tag or file type mapping.
- Adding new detection rules.
- Changing `get_filename_metatypes()` output for any path.
- Fixing `CLAUDE.md`'s stale exact-pin claim in release step 8.
