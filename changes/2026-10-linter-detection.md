# Linter, formatter and type checker detection

**Version:** 0.0.20
**Date:** 2026-10-05

## What changed

Panopticas now detects the configuration and exclusion files of code-quality
tooling — 30 tools, 96 exact filenames — across JavaScript, TypeScript, CSS,
Python, Go, Ruby, Java, Groovy, C#/.NET and SQL.

Before this change the only linters detected were ESLint's flat config and
SQLFluff, and the two rules disagreed on tag shape: `eslint.config.js` tagged
`["JavaScript", "linter", "eslint", "config"]` while `.sqlfluff` tagged
`["SQLFluff", "SQL", "linter"]` — lowercase versus brand-cased tool name, with
and without a `config` role.

## Design

### One table, not ninety-six literal rules

`LINTER_RULES` in `constants.py` describes each tool once:

```python
"ESLint": {
    "languages": ["JavaScript", "TypeScript"],
    "roles": ["linter"],
    "config": ["eslint.config.js", ..., ".eslintrc.json"],
    "ignore": [".eslintignore"],
},
```

`_expand_linter_rules()` writes those into the existing `METADATA_RULES`
tables at import: `config` and `ignore` into `exact_filename_rules`,
`path_contains` into `path_contains_rules`, `extensions` into
`extension_rules`. Tags are `languages + roles + [tool] + ["config"|"ignore"]`.

This was chosen over literal dict entries for three reasons. Prettier alone
accepts 18 config filenames that all carry identical tags, so the literal form
is 18 near-duplicate lines. The tag shape becomes structurally guaranteed
rather than a convention each entry has to remember — which is precisely what
went wrong between the `eslint` and `SQLFluff` rules. And the table reads as
the tool inventory, mirroring how `AI_RULES` already works.

Nothing downstream changed: `get_tags()` traverses `METADATA_RULES` after
expansion, so the new tags joined the vocabulary with no change to `core.py`
or `cli.py`. The existing vocabulary drift test in `tests/test_vocabulary.py`
picked up all 96 rules for free.

### Language tags name what a tool targets

ESLint gets `JavaScript` and `TypeScript`; Stylelint gets `CSS` and
deliberately not `JavaScript`; `.editorconfig` is language-neutral and carries
no language tag at all. Prettier is capped at its three main targets rather
than the seven parsers it ships, to keep one config file from carrying seven
language tags.

### Three roles

`linter`, `formatter` and `typechecker`, constrained by `LINTER_ROLES`. A tool
may hold several, and Ruff, Biome, RuboCop, Standard and SQLFluff all lint and
format. `.rubocop_todo.yml` and `.standard_todo.yml` are classified `ignore`
rather than `config` — both are generated to exclude existing offences, which
makes them the exclusion file rather than a second config.

## Research

Every convention was verified against the tool's current official
documentation before being added. The full evidence base, the sources, and the
rejected candidates are in `docs/linter-detection-rules.md`.

Eleven candidates were investigated and **rejected**, each of which would have
been a wrong rule:

- **revive** auto-discovers only `$HOME/revive.toml` — a user-level path, not
  a repository artifact.
- **SpotBugs**, **PMD** and **CodeNarc** take arbitrarily-named filter and
  ruleset files passed explicitly on the command line.
- **Black**, **StandardJS** and **Spotless** have no dedicated config file.
- **gofmt**, **gofumpt** and **go vet** have no configuration at all.
- **pycodestyle**'s dedicated file is user-level.
- **dprint** is plausible but its filename list could not be confirmed.
- Security scanners (Sonar, Bandit, Brakeman) are out of scope.

`pyproject.toml`, `setup.cfg`, `tox.ini` and `package.json` genuinely hold
linter configuration, but which tool is inside is not knowable from the path,
and detection here is path-based only. Tagging them would mislabel nearly
every repository that has one, so they keep only their existing build and
dependency tags.

## Side-effect: four missing extensions

The work surfaced a gap unrelated to linters. `.mjs`, `.cjs`, `.mts` and
`.cts` were absent from `EXT_FILETYPES` entirely, so every file using them
reported `Unknown` and `get_languages()` missed them. They are now JavaScript
and TypeScript respectively, matching GitHub Linguist, which types all four as
`programming`. They surfaced here because config authors use them to escape
the `"type"` field in `package.json`, which is why `eslint.config.mjs` and
`.prettierrc.cjs` are common.

## Filetype resolution

Extensionless config dotfiles previously reported `Unknown`. They now resolve
on one principle, which reconciles the two precedents already in the codebase
(`.sqlfluff` got its own name; `setup.cfg` was mapped to `INI` "because it is
read by configparser"): **where a tool documents a single content format, map
to that format; where several are accepted, the file gets its own name.**

`.cfg` and `.conf` are mapped by basename, not extension, because both are
used for arbitrary formats elsewhere.

## kospex impact

All tag changes are additions or case-only:

- `eslint` became `ESLint`. kospex matches with `tech_type LIKE '%|tag|%'`,
  and SQLite `LIKE` is case-insensitive for ASCII, so stored queries still
  match.
- `.sqlfluff` kept every tag it had and gained `formatter` and `config`.

No tag was renamed in a way that changes matching, and none was removed. A
kospex pin bump is needed only to pick up the new tags, which requires a
re-sync — `last_panopticas_version` handles that automatically.

## Also fixed: `panopticas file` ignored basename mappings

`panopticas file` built its "File type" row from
`get_extension_filetype(extension)`, which consults only `EXT_FILETYPES` and
never `LANGUAGE_BY_BASENAME`. Files typed by basename therefore reported
nothing there while `panopticas assess` reported their type correctly — the two
commands disagreed about the same file.

This predates the linter work: `panopticas file go.mod` has shown a blank file
type since basename mapping was introduced, as has `setup.cfg`. Mapping
`.isort.cfg` and `staticcheck.conf` by basename (correct, because `.cfg` and
`.conf` hold arbitrary formats elsewhere) would have added two more.

The row now reads `core.get_language(file, skip_shebang=True)`, which checks
`LANGUAGE_BY_BASENAME` before the extension table. Two details matter:

- `skip_shebang=True` keeps the row distinct from the Shebang Language row.
  Without it a shebang-only script would report `bash` as its *file* type,
  conflating two rows that exist precisely to be compared.
- `get_language()` returns the string `"Unknown"` for unrecognised files,
  which is normalised to `None` so the JSON contract still emits null.

The row remains a pure table lookup, so the trust comment above it still
holds: the value is always a `constants.py` value, never raw input from the
path.

Across the 96 linter config filenames the row went from 55/96 resolved to
96/96, and `go.mod` and `setup.cfg` are fixed as a side-effect.

## Also fixed: unreadable paths aborted whole scans

`check_shebang()` caught `FileNotFoundError` and `UnicodeDecodeError`, which
covers a filename that does not exist on disk — the common case, and the
reason `get_language("no-such-file.py")` has always correctly returned
`Python`. But `open()` fails in other ways that are not `FileNotFoundError`:

| Path | Raised | Caught before? |
|---|---|---|
| missing file | `FileNotFoundError` | yes |
| a directory | `IsADirectoryError` | **no** |
| unreadable file | `PermissionError` | **no** |
| name too long | `OSError` | **no** |
| NUL byte in path | `ValueError` | **no** |

The handler is now `except (OSError, ValueError)`. `OSError` is the base class
of every filesystem refusal; `ValueError` covers a NUL byte in the path and
keeps undecodable content handled, since `UnicodeDecodeError` is a `ValueError`
subclass.

This mattered well beyond the type returned for one file. `identify_files()`
walks whole trees, so a single unreadable file aborted an entire
`panopticas assess` run with a `PermissionError` traceback. `count_lines()` in
the same module was already robust — it ends with a catch-all — which is what
made `check_shebang()` the last unguarded `open()` on the scanning path.

`panopticas urls` had the identical bug one layer up: its loop caught
`UnicodeDecodeError`, added in 0.0.19 so a binary file could not kill the run,
but not `OSError`. Fixed in the CLI loop rather than in
`extract_urls_from_file()`, whose raising behaviour is documented and
deliberate — the decision to keep scanning belongs to the caller walking the
tree.

`panopticas file` was never exposed: Click rejects an unreadable path at the
CLI boundary before the library sees it.

## Testing

`tests/test_linter_detection.py` — 141 tests covering table integrity,
expansion into each `METADATA_RULES` table, representative tags per language,
the config/ignore split, filetype resolution for every config filename, and
negative guards asserting each rejected convention stays undetected.

Fixture files for the novel filetype resolutions are in `src/tests/`.
