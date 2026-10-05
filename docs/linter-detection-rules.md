---
layout: default
title: Linter Detection Rules
description: Every linter, formatter and type checker config file panopticas detects, the source confirming each convention, and the candidates that were investigated and rejected.
---

# Linter, Formatter and Type Checker Detection — Rules Reference

**Rules verified:** 2026-10-05 (panopticas 0.0.20)
**Inventory below generated from:** `LINTER_RULES` in `src/panopticas/constants.py`

Panopticas detects the configuration and exclusion files of code-quality
tooling and tags each with the languages the tool targets, its role, the tool
name, and whether the file configures or excludes.

```
.eslintrc.json   -> ['JavaScript', 'TypeScript', 'linter', 'ESLint', 'config']
.eslintignore    -> ['JavaScript', 'TypeScript', 'linter', 'ESLint', 'ignore']
.rubocop.yml     -> ['Ruby', 'linter', 'formatter', 'RuboCop', 'config']
mypy.ini         -> ['Python', 'typechecker', 'mypy', 'config']
.editorconfig    -> ['formatter', 'EditorConfig', 'config']
```

This document is the **reference and evidence base**: what is detected, the
source that confirms each convention, and — equally important — what was
rejected and why.

## How matching works

`LINTER_RULES` maps a tool to its languages, its roles, and the files that
identify it. A single expansion step writes those entries into the same
`METADATA_RULES` tables every other rule uses, so the tags are produced by one
code path and the shape cannot drift between tools.

| Key | Expands into | Matched against |
|---|---|---|
| `config` | `exact_filename_rules` | the lowercased basename |
| `ignore` | `exact_filename_rules` | the lowercased basename |
| `path_contains` | `path_contains_rules` | a substring of the path |
| `extensions` | `extension_rules` | the file extension |

Tags are `languages + roles + [tool] + ["config"` or `"ignore"]`. The three
roles are `linter`, `formatter` and `typechecker`; a tool may hold more than
one, and several do — Ruff, Biome, RuboCop, Standard and SQLFluff all lint and
format.

Unlike AI artifact detection, these rules **add** tags rather than resolving to
a single winner, so `eslint.config.js` is both JavaScript and an ESLint config.

## Detection is path-based only

No rule opens a file. This is the same constraint AI detection works under, and
it is what makes the per-language shared config files undetectable:

| File | Really can hold | Why it is not tagged |
|---|---|---|
| `pyproject.toml` | Ruff, Black, mypy, isort, yapf, Pylint, Pyright | which tool is inside is not knowable from the path |
| `setup.cfg` | Flake8, isort, yapf, mypy | same |
| `tox.ini` | Flake8, Pylint | same |
| `package.json` | Prettier, ESLint, Stylelint, StandardJS | same |

Tagging any of these as a linter config would mislabel every repository that
has one, which is most of them. They keep their existing build and dependency
tags only.

## The rejected list

Each of these was investigated against the tool's current documentation and
**deliberately not added**. Re-adding one would mislabel repositories.

| Candidate | Why rejected |
|---|---|
| **revive** (`revive.toml`) | Auto-discovers only `$HOME/revive.toml`. A user-level path, not a repository artifact — the same trap AI detection warns about. A project-level config exists but must be passed with `-config`, under any name. |
| **SpotBugs** (`spotbugs-exclude.xml`) | Filter files are arbitrarily named and passed with `-exclude`/`-include`. The documentation's `myExcludeFilter.xml` is illustrative, not a convention. |
| **PMD** (`ruleset.xml`) | Ruleset files are arbitrarily named and passed explicitly. No discovered filename. |
| **CodeNarc** (`codenarc.xml`) | Rulesets are arbitrary `.xml` or `.groovy` files. Detected indirectly through npm-groovy-lint, which does have a fixed config name. |
| **Black** | Configured only in `pyproject.toml`. No dedicated file exists to match. |
| **StandardJS** | Configured only in `package.json`. |
| **Spotless** | Configured only in `build.gradle` / `pom.xml`. |
| **gofmt**, **gofumpt**, **go vet** | No configuration file at all. |
| **pycodestyle** | Project-level config lives in `setup.cfg` or `tox.ini`; the dedicated file is the user-level `~/.config/pycodestyle`. |
| **dprint** | Plausible (`dprint.json`), but the filename list could not be confirmed from the official docs. Left out pending verification — a missing rule is better than a wrong one. |
| **Sonar**, **Bandit**, **Brakeman**, **GitLeaks** | Security scanners, out of scope. GitLeaks is already detected separately via `.gitleaksignore`. |

### Two judgement calls worth knowing

**`checkstyle.xml`** is not a documented Checkstyle convention — Checkstyle
discovers nothing and takes its config as an argument. It is included because
the name is unambiguous in practice, and alongside it sit two names that *are*
documented: `google_checks.xml` and `sun_checks.xml` ship with the
distribution, and `config/checkstyle/` is the Gradle Checkstyle plugin's
documented default directory.

**`tsconfig.json`** is a *compiler* configuration, and the TypeScript handbook
is explicit that it does not handle linting. It is tagged `typechecker` because
it is nonetheless where a project's type checking is actually configured
(`strict`, `noImplicitAny`), which is the thing worth finding. `jsconfig.json`
is the same file applied to a JavaScript project.

## Filetypes, not just tags

Extensionless config dotfiles used to report `Unknown`. They now resolve on one
principle: **where a tool documents a single content format, map to that
format; where several are accepted, the file gets its own name.**

| Resolves to its documented format | Gets its own name |
|---|---|
| `.editorconfig`, `.flake8`, `.globalconfig`, `.pylintrc`, `pylintrc`, `.isort.cfg`, `.style.yapf` → `INI` | `.eslintrc` → `ESLintRC` (JSON, YAML or JS) |
| `.jshintrc` → `JSON` | `.prettierrc` → `Prettierrc` (JSON or YAML) |
| `staticcheck.conf` → `TOML` | `.stylelintrc` → `StylelintRC` (JSON or YAML) |
| `.rufo`, `Steepfile` → `Ruby` (both are evaluated as Ruby) | `.eslintignore`, `.prettierignore`, `.stylelintignore`, `.jshintignore`, `.yapfignore` — gitignore-style pattern files |
| `*.ruleset` → `XML` | |

`.cfg` and `.conf` are mapped by basename rather than by extension, because
both are used for arbitrary formats elsewhere — the same reasoning that already
applied to `setup.cfg`.

### Module extensions

Closing this gap also meant adding four extensions that were missing from
`EXT_FILETYPES` altogether, and which are not linter-specific at all:

| Extension | Language | Meaning |
|---|---|---|
| `.mjs` | JavaScript | always an ES module |
| `.cjs` | JavaScript | always CommonJS |
| `.mts` | TypeScript | TypeScript emitting an ES module |
| `.cts` | TypeScript | TypeScript emitting CommonJS |

These exist because Node needs to know a file's module system before parsing
it, and `.js` alone does not say. Config authors reach for them to escape the
`"type"` field in `package.json`, which is why `eslint.config.mjs` and
`.prettierrc.cjs` are so common. Both pairs match GitHub Linguist, which types
all four as `programming`.

## Sources

Every convention above was checked against the tool's own current
documentation:

| Tool | Source |
|---|---|
| ESLint | [Configuration files](https://eslint.org/docs/latest/use/configure/configuration-files) (flat), [v8 configuration files](https://eslint.org/docs/v8.x/use/configure/configuration-files) (eslintrc) |
| Prettier | [Configuration file](https://prettier.io/docs/configuration) |
| Stylelint | [Configure](https://stylelint.io/user-guide/configure/) |
| Biome | [Configure Biome](https://biomejs.dev/guides/configure-biome/) |
| oxlint | [Linter config](https://oxc.rs/docs/guide/usage/linter/config.html) |
| TypeScript | [tsconfig.json](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html) |
| EditorConfig | [editorconfig.org](https://editorconfig.org/) |
| Ruff | [Configuration](https://docs.astral.sh/ruff/configuration/) |
| Flake8 | [Configuring flake8](https://flake8.pycqa.org/en/latest/user/configuration.html) |
| Pylint | [Running pylint](https://pylint.readthedocs.io/en/stable/user_guide/usage/run.html) |
| mypy | [The mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html) |
| Pyright | [Configuration](https://github.com/microsoft/pyright/blob/main/docs/configuration.md) |
| isort | [Config files](https://pycqa.github.io/isort/docs/configuration/config_files.html) |
| yapf | [README](https://github.com/google/yapf) |
| Prospector | [Profiles](https://prospector.landscape.io/en/master/profiles.html) |
| golangci-lint | [Configuration file](https://golangci-lint.run/docs/configuration/file/) |
| staticcheck | [Configuration](https://staticcheck.dev/docs/configuration/) |
| RuboCop | [Configuration](https://docs.rubocop.org/rubocop/configuration.html) |
| Standard | [README](https://github.com/standardrb/standard) |
| Reek | [README](https://github.com/troessner/reek) |
| Rufo | [README](https://github.com/ruby-formatter/rufo) |
| erb_lint | [README](https://github.com/Shopify/erb_lint) |
| Steep | [README](https://github.com/soutaro/steep) |
| Sorbet | [CLI](https://sorbet.org/docs/cli) |
| Checkstyle | [Gradle Checkstyle plugin](https://docs.gradle.org/current/userguide/checkstyle_plugin.html) |
| npm-groovy-lint | [Documentation](https://nvuillam.github.io/npm-groovy-lint/) |
| Roslyn | [Configuration files for code analysis rules](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/configuration-files) |
| StyleCop | [Configuration](https://github.com/DotNetAnalyzers/StyleCopAnalyzers/blob/master/documentation/Configuration.md) |

## Re-verifying

Config filenames change. ESLint replaced `.eslintrc` with flat config and
dropped `.eslintignore`; Stylelint's docs warn its legacy locations "may be
removed in the future". Legacy names are kept deliberately — a repository that
still has `.eslintrc.json` is still a repository using ESLint.

When re-verifying, check each source above for new accepted extensions, and
re-read the rejected list before adding anything in it.

## Inventory

`*` marks a path fragment rather than a filename.

### JavaScript, TypeScript and CSS

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **ESLint** | linter | `JavaScript`, `TypeScript` | `eslint.config.js`, `eslint.config.mjs`, `eslint.config.cjs`, `eslint.config.ts`, `eslint.config.mts`, `eslint.config.cts`, `.eslintrc`, `.eslintrc.js`, `.eslintrc.cjs`, `.eslintrc.yaml`, `.eslintrc.yml`, `.eslintrc.json` | `.eslintignore` |
| **Prettier** | formatter | `JavaScript`, `TypeScript`, `CSS` | `.prettierrc`, `.prettierrc.json`, `.prettierrc.yml`, `.prettierrc.yaml`, `.prettierrc.json5`, `.prettierrc.js`, `.prettierrc.mjs`, `.prettierrc.cjs`, `.prettierrc.ts`, `.prettierrc.mts`, `.prettierrc.cts`, `.prettierrc.toml`, `prettier.config.js`, `prettier.config.mjs`, `prettier.config.cjs`, `prettier.config.ts`, `prettier.config.mts`, `prettier.config.cts` | `.prettierignore` |
| **Stylelint** | linter | `CSS` | `stylelint.config.js`, `stylelint.config.mjs`, `stylelint.config.cjs`, `stylelint.config.ts`, `.stylelintrc`, `.stylelintrc.js`, `.stylelintrc.mjs`, `.stylelintrc.cjs`, `.stylelintrc.yml`, `.stylelintrc.yaml`, `.stylelintrc.json` | `.stylelintignore` |
| **Biome** | linter, formatter | `JavaScript`, `TypeScript`, `CSS` | `biome.json`, `biome.jsonc`, `.biome.json`, `.biome.jsonc` | — |
| **oxlint** | linter | `JavaScript`, `TypeScript` | `.oxlintrc.json`, `.oxlintrc.jsonc`, `oxlint.config.ts`, `oxlint.config.mts` | — |
| **JSHint** | linter | `JavaScript` | `.jshintrc` | `.jshintignore` |
| **TypeScript** | typechecker | `TypeScript`, `JavaScript` | `tsconfig.json`, `jsconfig.json` | — |
| **EditorConfig** | formatter | *(none)* | `.editorconfig` | — |

### Python

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **Ruff** | linter, formatter | `Python` | `ruff.toml`, `.ruff.toml` | — |
| **Flake8** | linter | `Python` | `.flake8` | — |
| **Pylint** | linter | `Python` | `pylintrc`, `.pylintrc`, `pylintrc.toml`, `.pylintrc.toml` | — |
| **mypy** | typechecker | `Python` | `mypy.ini`, `.mypy.ini` | — |
| **Pyright** | typechecker | `Python` | `pyrightconfig.json` | — |
| **isort** | formatter | `Python` | `.isort.cfg` | — |
| **yapf** | formatter | `Python` | `.style.yapf` | `.yapfignore` |
| **Prospector** | linter | `Python` | `.prospector.yaml`, `.prospector.yml` | — |

### Go

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **golangci-lint** | linter | `Go` | `.golangci.yml`, `.golangci.yaml`, `.golangci.toml`, `.golangci.json` | — |
| **staticcheck** | linter | `Go` | `staticcheck.conf` | — |

### Ruby

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **RuboCop** | linter, formatter | `Ruby` | `.rubocop.yml` | `.rubocop_todo.yml` |
| **Standard** | linter, formatter | `Ruby` | `.standard.yml` | `.standard_todo.yml` |
| **Reek** | linter | `Ruby` | `.reek.yml` | — |
| **Rufo** | formatter | `Ruby` | `.rufo` | — |
| **erb_lint** | linter | `Ruby` | `.erb_lint.yml` | — |
| **Steep** | typechecker | `Ruby` | `steepfile` | — |
| **Sorbet** | typechecker | `Ruby` | `sorbet/`* | — |

### Java

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **Checkstyle** | linter | `Java` | `checkstyle.xml`, `google_checks.xml`, `sun_checks.xml`, `config/checkstyle/`* | — |

### Groovy

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **npm-groovy-lint** | linter | `Groovy` | `.groovylintrc.json`, `.groovylintrc.js`, `.groovylintrc.yml` | — |

### C# and .NET

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **Roslyn** | linter | `C#`, `.NET` | `.globalconfig`, `*.ruleset` | — |
| **StyleCop** | linter | `C#`, `.NET` | `stylecop.json`, `.stylecop.json` | — |

### SQL

| Tool | Role | Language tags | Config | Ignore |
|---|---|---|---|---|
| **SQLFluff** | linter, formatter | `SQL` | `.sqlfluff` | `.sqlfluffignore` |

<!-- 30 tools, 96 exact filenames -->
