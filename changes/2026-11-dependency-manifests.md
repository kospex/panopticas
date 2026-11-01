# Dependency Manifests: Python, Rust, Ruby, PHP, Elixir, Dart

For [#74](https://github.com/kospex/panopticas/issues/74).

**Status:** research done 2026-11-02. All ten decisions below were taken as
recommended. Python is implemented; Rust, Ruby, and PHP/Elixir/Dart follow
in their own PRs. Each convention below was checked against the tool's
current official docs, or its source code where the docs don't settle the
point (marked **[source]**).

## Current state

Counts are from a local kospex database (376 repositories), current files
only. "Today" is panopticas `main` after #86.

| File | Files / repos | Filetype today | Tags today |
|---|---|---|---|
| `requirements*.txt` | 99 / 43 | Text | `pip, Python, PyPI, dependencies` |
| `uv.lock` | 24 / 23 | Lock | `dependencies, Python, uv` |
| `pyproject.toml` | 131 / 82 | TOML | `build, dependencies, Python` |
| `setup.py` / `setup.cfg` | 46 / 32, 19 / 16 | Python / INI | `build, dependencies, Python, setuptools` |
| `py.typed` | 65 / 61 | Unknown | none |
| `MANIFEST.in` | 39 / 37 | Unknown | none |
| `*.pyi` | 169 / 16 | Unknown | none |
| `Pipfile`, `Pipfile.lock`, `poetry.lock`, `pylock.toml` | 1 / 1 each | Unknown, Lock, Lock, TOML | none |
| `pdm.lock`, `pdm.toml`, `uv.toml` | 0 | Lock, TOML, TOML | none |
| `Cargo.toml` | 125 / 14 | TOML | none |
| `Cargo.lock` | 14 / 10 | Lock | none |
| `build.rs` | 13 / 7 | Rust | none |
| `rust-toolchain.toml` | 4 / 2 | TOML | none |
| `*.rs` | 1,618 / 14 | Rust | none |
| `Gemfile` | 14 / 5 | Unknown | none |
| `Gemfile.lock` | 2 / 2 | Lock | none |
| `Rakefile` | 22 / 3 | Unknown | none |
| `*.gemspec` | 8 / 1 | Unknown | none |
| `*.rb` | 860 / 10 | Ruby | none |
| `composer.json` | 4 / 4 | JSON | none |
| `*.php` | 30 / 7 | PHP | none |
| `*.ex` / `*.exs` | 2 / 2, 0 | **Unknown** | none |
| `mix.exs`, `mix.lock`, `.formatter.exs` | 0 | Unknown, Lock, Unknown | none |
| `*.dart` | 5 / 2 | **Unknown** | none |
| `pubspec.yaml`, `pubspec.lock`, `analysis_options.yaml` | 0 | YAML, Lock, YAML | none |

Two findings beyond the issue:

- **Elixir and Dart aren't languages in panopticas at all.** `.ex`, `.exs` and
  `.dart` report `Unknown`. `Rust`, `PHP` and `Ruby` are filetypes, but
  `Rust` and `PHP` aren't tags yet.
- **`.pyi` stubs are Unknown**, although they're Python syntax.

## Precedents in the rules

- `Podfile` maps to the `Ruby` filetype because CocoaPods loads it as Ruby.
  `Gemfile`, `Rakefile`, `*.gemspec` and `*.rake` are Ruby code in the same way.
- `Makefile` is tagged `build` alone.
- `.python-version` is `Python, dependencies` and `.nvmrc` is
  `Node, dependencies`; neither names a tool.
- `go.sum` is `Go, dependencies, checksum`.
- Function rules (`is_pip_requirements`) already handle names that need a
  pattern, so `pylock.<name>.toml` needs no new match mode.
- Ecosystem tags use OSV names; the tool gets its own tag
  ([Ecosystem tags](https://panopticas.io/cli#ecosystem-tags)).

## Verified conventions

### Python

| File | Facts | Source |
|---|---|---|
| `Pipfile`, `Pipfile.lock` | Pipenv manifest (TOML) and lock (JSON), project root. "Both files should be committed." No user-level copy | pipenv.pypa.io |
| `poetry.lock` | Poetry's lock. "Application developers commit `poetry.lock`"; libraries may omit it. `poetry self` also writes one into Poetry's own config dir, outside any repository | python-poetry.org |
| `poetry.toml` | Project-local Poetry config from `poetry config --local`. "Be mindful when checking in this file… it may contain user-specific or sensitive information." User config is a different name (`config.toml`) | python-poetry.org |
| `pdm.lock`, `pdm.toml` | "You **should** commit the `pdm.lock` and `pdm.toml` file." The global project's `pdm.toml` lives under PDM's config root, outside any repository | pdm-project.org |
| `.pdm-python` | Local interpreter path. "**Do not** commit the `.pdm-python` file." | pdm-project.org |
| `uv.lock` | Next to `pyproject.toml`; "should be checked into version control" | docs.astral.sh/uv |
| `uv.toml` | Project config, found in the current or a parent directory. The same name is user-level at `~/.config/uv/uv.toml` and system-level at `/etc/uv/uv.toml`; only a copy inside a repository is a project file | docs.astral.sh/uv |
| `pylock.toml` | PEP 751, Final. "MUST be named `pylock.toml` or match… `^pylock\.([^.]+)\.toml$`"; prefix and suffix "MUST be lowercase when possible". pip, uv and PDM read or write it | packaging.python.org (verified) |
| `MANIFEST.in` | setuptools sdist contents, project root. Bare `MANIFEST` "is likely outdated" | setuptools.pypa.io |
| `py.typed` | PEP 561 marker: a package "MUST add a marker file named `py.typed`" to support typing. Inside the package directory | typing.python.org |
| `*.pyi` | Type stubs, "preferred… alongside the corresponding `*.py` files" | typing.python.org |
| `constraints.txt` | Name is arbitrary; `-c` picks the file and the name appears only in examples | pip.pypa.io |
| `environment.yml` / `.yaml` | conda's default for `conda env create -f`. conda is **not** an OSV ecosystem | docs.conda.io, OSV |

### Rust

| File | Facts | Source |
|---|---|---|
| `Cargo.toml` | Manifest, in every package and at the workspace root. Case-sensitive: Cargo errors on `cargo.toml` and asks for a rename **[source]** | doc.rust-lang.org/cargo |
| `Cargo.lock` | One per workspace, at the root. "When in doubt, check `Cargo.lock` into the version control system"; since 2023 `cargo new` no longer ignores it for libraries | doc.rust-lang.org/cargo, blog.rust-lang.org |
| `.cargo/config.toml`, `.cargo/config` | Read in the current and every parent directory, then `$CARGO_HOME/config.toml` (`~/.cargo/config.toml`). The extensionless name is still read and wins if both exist. Can be checked in, but "not usually" | doc.rust-lang.org/cargo (verified) |
| `rust-toolchain.toml`, `rust-toolchain` | rustup override; "suitable to check in to source control". Extensionless name kept for backwards compatibility and wins if both exist; it can be TOML or a bare channel name | rust-lang.github.io/rustup |
| `build.rs` | Default build script name in the package root; `package.build` renames it, `build = false` disables it | doc.rust-lang.org/cargo |

### Ruby

| File | Facts | Source |
|---|---|---|
| `Gemfile`, `Gemfile.lock` | Bundler manifest at the project root; the lock is the Gemfile name plus `.lock` | guides.rubygems.org, ruby/rubygems **[source]** |
| `gems.rb`, `gems.locked` | Current alternative names, opt-in through `init_gems_rb`. If both exist, Bundler uses `gems.rb` and warns | guides.rubygems.org, ruby/rubygems **[source]** |
| `*.gemspec` | Gem metadata and runtime dependencies; Ruby code. Bundler's `gemspec` globs `{,*,*/*}.gemspec` | guides.rubygems.org, Bundler `gemfile.5` |
| `.bundle/config` | Project-local Bundler settings; the same relative path is user-level at `~/.bundle/config`. Machine-local, and Rails' generated `.gitignore` excludes `/.bundle` | guides.rubygems.org, rails/rails |
| `Rakefile` | Exactly four names: `rakefile`, `Rakefile`, `rakefile.rb`, `Rakefile.rb`. Rake calls itself "a Make-like program"; Rakefiles are "rake's version of Makefiles" | ruby/rake **[source]** (verified), ruby.github.io/rake |
| `*.rake` | Auto-imported from `rakelib/`; Rails uses `lib/tasks/`. Global rakefiles live in `~/.rake/*.rake`, so `.rake/` is not a repository path | ruby/rake (verified) |
| `.ruby-version` | Cross-tool convention (rbenv, chruby, Bundler's `ruby file:`). chruby also reads `~/.ruby-version` | rbenv, chruby READMEs, Bundler `gemfile.5` |

### PHP, Elixir, Dart

| File | Facts | Source |
|---|---|---|
| `composer.json`, `composer.lock` | Manifest and lock at the project root. "For your library it is recommended to commit the `composer.lock` file", a change from older advice | getcomposer.org (verified) |
| `auth.json` | Composer credentials; "Make sure the `auth.json` file is in `.gitignore`". The name is generic | getcomposer.org |
| `mix.exs`, `mix.lock` | Mix project and lock; umbrella apps have `apps/*/mix.exs`. Hex: "always commit `mix.lock` to version control" | mix.hexdocs.pm, hex.pm (verified) |
| `.formatter.exs` | Read by `mix format`; nested copies are normal | mix.hexdocs.pm |
| `.ex`, `.exs` | "`.ex` files are meant to be compiled while `.exs` files are used for scripting" | elixir.hexdocs.pm |
| `pubspec.yaml`, `pubspec.lock` | Package manifest and lock. "For application packages, we recommend that you commit the pubspec.lock file"; "For regular packages, don't". Workspaces have one lock at the root | dart.dev (verified) |
| `pubspec_overrides.yaml` | Next to `pubspec.yaml`; overrides it, typically for local work | dart.dev |
| `analysis_options.yaml` | Analyzer and linter config at the package root; the analyzer walks up if it's missing | dart.dev |
| `.dart` | Dart source | dart.dev |

The pub tool is written lowercase, `pub`; the OSV ecosystem is `Pub`.

### OSV ecosystem names

`PyPI`, `crates.io`, `RubyGems`, `Packagist`, `Hex`, `Pub`, exactly as cased.
OSV describes `Hex` as the Erlang ecosystem, which Elixir shares.

## Rejected

| Candidate | Why |
|---|---|
| `auth.json` | Composer's credentials file, but the name is generic: nothing in the path says it is Composer's. Composer itself says to gitignore it |
| `constraints.txt` | The name is arbitrary in pip's docs |
| `environment.yml` / `.yaml` | conda isn't an OSV ecosystem, and the name is generic (1 repo) |
| `.rake/` | User-level global rakefiles |
| `.cargo/credentials.toml` | User-level only, under `$CARGO_HOME` |
| Bare `MANIFEST`, `config.toml`, `config` | Outdated or generic |

## Proposed rules

Shape: `[Language, tool, ecosystem, role]`. Tags new to the vocabulary are in
**bold**.

### Python

| File | Tags |
|---|---|
| `uv.lock` | `dependencies, Python, uv`, + `PyPI` |
| `pyproject.toml`, `setup.py`, `setup.cfg` | existing, + `PyPI` (decision 3) |
| `Pipfile` | `Python, **Pipenv**, PyPI, dependencies` |
| `Pipfile.lock` | `Python, Pipenv, PyPI, dependencies` |
| `poetry.lock` | `Python, **Poetry**, PyPI, dependencies` |
| `poetry.toml` | `Python, Poetry, config` |
| `pdm.lock` | `Python, **PDM**, PyPI, dependencies` |
| `pdm.toml`, `.pdm-python` | `Python, PDM, config` |
| `uv.toml` | `Python, uv, config` |
| `pylock.toml`, `pylock.<name>.toml` (function rule) | `Python, PyPI, dependencies` (no tool tag: pip, uv and PDM all write it) |
| `MANIFEST.in` | `Python, setuptools, build` |
| `py.typed` | `Python, **typing**` (decision 6) |
| `*.pyi` | filetype `Python`; tags `Python, typing` |

### Rust

| File | Tags |
|---|---|
| `Cargo.toml` | `**Rust**, **Cargo**, **crates.io**, build, dependencies` |
| `Cargo.lock` | `Rust, Cargo, crates.io, dependencies` |
| `.cargo/config.toml`, `.cargo/config` | `Rust, Cargo, config` |
| `rust-toolchain.toml`, `rust-toolchain` | `Rust, **rustup**, config`; extensionless one gets its own filetype |
| `build.rs` | `Rust, Cargo, build` (decision 7) |

### Ruby

| File | Tags |
|---|---|
| `Gemfile`, `gems.rb` | `Ruby, **Bundler**, **RubyGems**, dependencies`; filetype `Ruby` |
| `Gemfile.lock`, `gems.locked` | `Ruby, Bundler, RubyGems, dependencies`; `gems.locked` filetype `Lock` |
| `*.gemspec` | `Ruby, RubyGems, dependencies`; filetype `Ruby` |
| `.bundle/config` | `Ruby, Bundler, config` |
| `Rakefile` (all four names) | `Ruby, **Rake**, build`; filetype `Ruby` |
| `*.rake` | `Ruby, Rake, build`; filetype `Ruby` |
| `.ruby-version` | `Ruby, dependencies` (as `.python-version`); own filetype |

### PHP, Elixir, Dart

| File | Tags |
|---|---|
| `composer.json` | `**PHP**, **Composer**, **Packagist**, dependencies` |
| `composer.lock` | same |
| `.ex`, `.exs` | new language **`Elixir`** |
| `mix.exs` | `**Elixir**, **Mix**, **Hex**, build, dependencies` |
| `mix.lock` | `Elixir, Mix, Hex, dependencies` |
| `.formatter.exs` | `LINTER_RULES`: `Elixir, formatter, **mix format**, config` (decision 9) |
| `.dart` | new language **`Dart`** |
| `pubspec.yaml`, `pubspec.lock` | `**Dart**, **Pub**, dependencies` (decision 8) |
| `pubspec_overrides.yaml` | `Dart, Pub, dependencies, config` |
| `analysis_options.yaml` | `LINTER_RULES`: `Dart, linter, typechecker, **Dart analyzer**, config` (decision 9) |

## Decisions

1. **One PR per ecosystem?** *Recommendation:* four PRs (Python; Rust; Ruby;
   PHP, Elixir and Dart together, since Elixir and Dart have almost no files
   in the database). This note lands with the first.
2. **Tag shape `[Language, tool, ecosystem, role]`.** *Recommendation:* yes.
   Where the tool and the ecosystem share a name, use the tag once
   (`*.gemspec` is `RubyGems` only).
3. **`PyPI` on `pyproject.toml`, `setup.py` and `setup.cfg`?** These declare
   PyPI dependencies whichever tool reads them, so it says nothing about the
   tool. *Recommendation:* yes, so every Python manifest carries the ecosystem.
4. **New languages `Elixir` and `Dart`.** This grows the language vocabulary
   from 34 to 36 and starts counting `.ex`, `.exs` and `.dart` as code in
   kospex. *Recommendation:* yes.
5. **Ruby DSL files as `Ruby`** (`Gemfile`, `Rakefile`, `*.gemspec`, `*.rake`),
   following `Podfile`. These would count as Ruby code in kospex.
   *Recommendation:* yes.
6. **`py.typed` and `.pyi`.** `typechecker` is a linter role, so it would blur
   that meaning. *Recommendation:* a new tag `typing` on both, and `.pyi` as
   filetype `Python`.
7. **`build.rs`.** It's the default build-script name, but a path can't show
   that it's at a package root. *Recommendation:* tag it; `build.rs` anywhere
   else is rare.
8. **Dart's tool tag.** The tool is `pub` and the ecosystem `Pub`. Two tags
   differing only in case would collide under SQLite's `LIKE`.
   *Recommendation:* `Pub` only, as with `RubyGems`.
9. **`.formatter.exs` and `analysis_options.yaml`** are formatter and linter
   configs, so they belong in `LINTER_RULES`, which wants a tool name.
   Neither vendor brands one. *Recommendation:* `mix format` and
   `Dart analyzer`, and add them in the same PR as their language.
10. **Local-state files** (`.pdm-python`, `.bundle/config`, `poetry.toml`):
    the docs say not to commit them, or to be careful. *Recommendation:* tag
    them anyway as `config`. Panopticas is a detector; whether they belong in
    the repository is kospex's call.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://pipenv.pypa.io/en/latest/pipfile.html> | Pipfile and Pipfile.lock; commit both | 2026-11-02 |
| <https://pipenv.pypa.io/en/latest/configuration.html> | Pipfile location | 2026-11-02 |
| <https://python-poetry.org/docs/basic-usage/> | Committing `poetry.lock` | 2026-11-02 |
| <https://python-poetry.org/docs/cli/> | `poetry self` writes a lock into Poetry's config dir | 2026-11-02 |
| <https://python-poetry.org/docs/configuration/> | `poetry.toml`; user config is `config.toml` | 2026-11-02 |
| <https://pdm-project.org/en/latest/usage/project/> | Commit `pdm.lock`/`pdm.toml`; don't commit `.pdm-python` | 2026-11-02 |
| <https://pdm-project.org/en/latest/usage/config/> | `pdm.toml` locations | 2026-11-02 |
| <https://pdm-project.org/en/latest/usage/lockfile/> | Lock file naming, `pylock.toml` support | 2026-11-02 |
| <https://docs.astral.sh/uv/concepts/projects/layout/> | `uv.lock` location and commit | 2026-11-02 |
| <https://docs.astral.sh/uv/concepts/configuration-files/> | `uv.toml` project, user and system locations | 2026-11-02 |
| <https://docs.astral.sh/uv/concepts/python-versions/> | `.python-version` and the global pin | 2026-11-02 |
| <https://github.com/pyenv/pyenv/blob/master/README.md> | pyenv reads `.python-version` | 2026-11-02 |
| <https://packaging.python.org/en/latest/specifications/pylock-toml/> | `pylock.toml` naming rule | 2026-11-02 |
| <https://peps.python.org/pep-0751/> | PEP 751 status | 2026-11-02 |
| <https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html> | `MANIFEST.in` | 2026-11-02 |
| <https://typing.python.org/en/latest/spec/distributing.html> | `py.typed`, `.pyi` | 2026-11-02 |
| <https://pip.pypa.io/en/stable/user_guide/> | Constraints file name is arbitrary | 2026-11-02 |
| <https://docs.conda.io/projects/conda/en/latest/commands/env/create.html> | `environment.yml` default | 2026-11-02 |
| <https://ossf.github.io/osv-schema/> | Ecosystem names | 2026-11-02 |
| <https://doc.rust-lang.org/cargo/reference/manifest.html> | `Cargo.toml`; the `build` field | 2026-11-02 |
| <https://doc.rust-lang.org/cargo/reference/workspaces.html> | One `Cargo.lock` per workspace | 2026-11-02 |
| <https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html> | Committing `Cargo.lock` | 2026-11-02 |
| <https://doc.rust-lang.org/cargo/faq.html> | `cargo new` tracks `Cargo.lock` | 2026-11-02 |
| <https://blog.rust-lang.org/2023/08/29/committing-lockfiles/> | 2023 change to lockfile guidance | 2026-11-02 |
| <https://github.com/rust-lang/cargo/blob/master/src/cargo/util/important_paths.rs> | `Cargo.toml` is case-sensitive | 2026-11-02 |
| <https://doc.rust-lang.org/cargo/reference/config.html> | `.cargo/config(.toml)` lookup | 2026-11-02 |
| <https://doc.rust-lang.org/cargo/reference/build-scripts.html> | `build.rs` | 2026-11-02 |
| <https://rust-lang.github.io/rustup/overrides.html> | `rust-toolchain(.toml)` | 2026-11-02 |
| <https://guides.rubygems.org/gemfile/> | Gemfile location; lockfile name | 2026-11-02 |
| <https://guides.rubygems.org/command-reference/bundle-config/> | `.bundle/config` levels; `init_gems_rb` | 2026-11-02 |
| <https://github.com/ruby/rubygems/blob/master/lib/bundler/shared_helpers.rb> | `gems.rb`/`gems.locked` lookup and lockfile names | 2026-11-02 |
| <https://github.com/ruby/rubygems/blob/master/lib/bundler/man/gemfile.5.ronn> | gemspec glob; `ruby file:` | 2026-11-02 |
| <https://guides.rubygems.org/specification-reference/> | `.gemspec` | 2026-11-02 |
| <https://github.com/rails/rails/blob/main/railties/lib/rails/generators/rails/app/templates/gitignore.tt> | Rails ignores `/.bundle` | 2026-11-02 |
| <https://ruby.github.io/rake/doc/rakefile_rdoc.html> | Rakefile lookup; `rakelib/` | 2026-11-02 |
| <https://github.com/ruby/rake/blob/master/lib/rake/application.rb> | `DEFAULT_RAKEFILES`; `~/.rake` | 2026-11-02 |
| <https://github.com/ruby/rake/blob/master/README.rdoc> | "Make-like" | 2026-11-02 |
| <https://github.com/rbenv/rbenv> | `.ruby-version` | 2026-11-02 |
| <https://github.com/postmodern/chruby> | `.ruby-version`, `~/.ruby-version` | 2026-11-02 |
| <https://getcomposer.org/doc/01-basic-usage.md> | `composer.json`, committing the lock | 2026-11-02 |
| <https://getcomposer.org/doc/02-libraries.md> | Libraries commit the lock | 2026-11-02 |
| <https://getcomposer.org/doc/03-cli.md> | `COMPOSER_HOME`, `COMPOSER` | 2026-11-02 |
| <https://getcomposer.org/doc/articles/authentication-for-private-packages.md> | `auth.json` | 2026-11-02 |
| <https://elixir.hexdocs.pm/introduction-to-mix.html> | `mix.exs` | 2026-11-02 |
| <https://mix.hexdocs.pm/Mix.Tasks.Deps.html> | Dependencies in `mix.exs`; `mix.lock` | 2026-11-02 |
| <https://hex.pm/docs/usage> | Commit `mix.lock` | 2026-11-02 |
| <https://mix.hexdocs.pm/Mix.Tasks.Format.html> | `.formatter.exs` | 2026-11-02 |
| <https://elixir.hexdocs.pm/modules-and-functions.html> | `.ex` vs `.exs` | 2026-11-02 |
| <https://dart.dev/tools/pub/glossary> | Package, lockfile | 2026-11-02 |
| <https://dart.dev/tools/pub/private-files> | Committing `pubspec.lock` | 2026-11-02 |
| <https://dart.dev/tools/pub/workspaces> | One lock per workspace | 2026-11-02 |
| <https://dart.dev/tools/pub/dependencies> | `pubspec_overrides.yaml` | 2026-11-02 |
| <https://dart.dev/tools/analysis> | `analysis_options.yaml` | 2026-11-02 |
| <https://dart.dev/tools/pub/cmd> | "pub" casing | 2026-11-02 |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html> | `environment.yml` only in examples; `.condarc` without a path | Not needed: conda rejected |
| <https://mix.hexdocs.pm/Mix.Tasks.Deps.html> | `mix.lock` is "usually" the name; ignored when used as a dependency | Match the default name only |
| <https://hex.pm/docs/faq> | Accounts, billing, ownership | Nothing on lock files |
| <https://dart.dev/tools/pub/pubspec> | Names `pubspec.yaml`, not its location | Location came from the glossary |
| <https://elixir.hexdocs.pm/introduction.html> | `.exs` scripts only | `.ex` came from modules-and-functions |
| <https://doc.rust-lang.org/cargo/commands/cargo-locate-project.html> | Searches upward for `Cargo.toml`; nothing on case | Case came from Cargo's source |
| `bundler.io/guides/gemfile.html`, `bundler.io/man/gemfile.5.html`, `bundler.io/man/bundle-config.1.html` | Redirect stubs to guides.rubygems.org | Cited the targets |
| `doc/CHANGELOG-bundler-2.x.md` in ruby/rubygems | `gems.rb` and `gems.locked` are maintained | Corroborates; not deprecated |
| <https://devcenter.heroku.com/changelog-items/3501>, <https://github.com/ruby/rubygems/releases/tag/v4.1.0.beta3> | Bundler 4 announcements | Nothing on `gems.rb` defaults |
| <https://www.jetbrains.com/help/ruby/ruby-version-managers.html> | RubyMine reads `.ruby-version`, `.ruby-gemset`, `.rvmrc`, `.tool-versions` and others | Third party; candidates only |
| <https://gist.github.com/1912050> | chruby's list of tools that read `.ruby-version` | Not fetched |
| <https://mise.jdx.dev/configuration.html> | mise reads other tools' version files once enabled | Not followed up |
