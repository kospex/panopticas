# JavaScript Package-Manager Files

Closes [#73](https://github.com/kospex/panopticas/issues/73).

**Status:** implemented. Verified on 2026-11-01 against each tool's current
official docs. All eight decisions below were taken as recommended.

## Current state

Repository counts are from a local kospex database (376 repositories).

| File | Repos | Language / tags today |
|---|---|---|
| `.npmrc` | 52 | Unknown, no tags |
| `.npmignore` | 33 | Unknown, no tags |
| `pnpm-workspace.yaml` | 16 | YAML, no tags |
| `.yarnrc.yml` / `.yarnrc` | 8 / 5 | YAML / Unknown, no tags |
| `.yarn/releases/*.cjs` | 7 | JavaScript, no tags |
| `bun.lock` | 2 | Lock, no tags |
| `deno.json` / `deno.lock` | 2 / 1 | JSON / Lock, no tags |
| `npm-shrinkwrap.json`, `bun.lockb`, `bunfig.toml`, `.pnpmfile.cjs`, `.pnp.cjs` | 0 | No tags (`bun.lockb` Unknown) |

Already tagged, but inconsistent:

| File | Tags |
|---|---|
| `package.json` | `npm, dependencies` (no `JavaScript`) |
| `package-lock.json` | `npm, dependencies` (no `JavaScript`) |
| `yarn.lock` | `dependencies, JavaScript, yarn, npm` |
| `pnpm-lock.yaml` | `dependencies, JavaScript, pnpm, npm` |
| `.nvmrc` | `Node, dependencies` |

## Two findings that change the issue

### npm 12 no longer reads `npm-shrinkwrap.json`

The current npm docs are version 12.2.1 (Latest), and v11 is marked Legacy.
The v12 `package-lock.json` page says:

> As of npm v12, `npm-shrinkwrap.json` is no longer read or written by npm.

> Projects that previously committed `npm-shrinkwrap.json` should rename it
> to `package-lock.json`; the file format is identical.

The v12 `npm-shrinkwrap.json` page is gone (404). In v11 it was a publishable
lockfile "identical to `package-lock.json`", preferred when both exist.

So `npm-shrinkwrap.json` is a **legacy** npm lockfile. It's still worth
detecting, for older repositories, as chat modes are for Copilot.

### pnpm 11 moved its settings into `pnpm-workspace.yaml`

From the [pnpm 11 release post](https://pnpm.io/blog/releases/11.0):

> pnpm no longer reads non-auth settings from `.npmrc`.

> pnpm no longer reads the `pnpm` field in `package.json`.

> Other settings must live in `pnpm-workspace.yaml` or the new global
> `config.yaml`.

`pnpm-workspace.yaml` defines the workspace root and holds catalogs (shared
dependency versions, since pnpm 9.5.0). It's now also pnpm's project settings
file, including `overrides`. So it's `config` **and** `dependencies`.

pnpm's [`.npmrc` page](https://pnpm.io/npmrc) now treats the project
`.npmrc` as auth and certificate settings only, which "hold secrets. Keep them
out of your repository", and says "Add it to `.gitignore`."

## `.npmrc` is shared, not npm-only

npm, pnpm, Bun and Deno all read `.npmrc`, and Yarn Classic does too. Yarn 2+
ignores it ("Any other file is now ignored - this includes `.npmrc`"). It's the
npm-registry config and auth file for the whole ecosystem. That fits the
`npm` tag meaning the npm ecosystem or registry (decision 1) rather than the
npm CLI.

npm documents four levels: per-project (`/path/to/my/project/.npmrc`),
per-user (`~/.npmrc`), global and built-in. Only the project file is in a
repository. A repository scan only sees repository files, so an exact-filename
rule is safe. The user-level trap is a *path* outside the repository, not the
filename.

Auth tokens go in `.npmrc` as `//registry.npmjs.org/:_authToken=...`.
Whether a committed `.npmrc` holds one depends on its contents, so panopticas
tags the file and kospex decides what that means (detector, not policy).

## Verified conventions

| File | Tool | What it is | Source |
|---|---|---|---|
| `.npmrc` | npm (also pnpm, Bun, Deno, Yarn 1) | Per-project registry config and auth | npm `npmrc`; pnpm `npmrc`; Deno Node page |
| `npm-shrinkwrap.json` | npm ≤ 11 | Publishable lockfile, legacy as of v12 | npm v11 shrinkwrap; npm v12 package-lock |
| `.npmignore` | npm | Files excluded from the published package; also read in subdirectories; overrides the `.gitignore` fallback | npm `developers` |
| `.yarnrc.yml` | Yarn 2+ | Project config ("must be called `.yarnrc.yml`") | Yarn `yarnrc` |
| `.yarnrc` | Yarn 1 | Project config, merged up the file tree | Yarn Classic `yarnrc` |
| `.yarn/releases/`, `.yarn/plugins/`, `.yarn/sdks/`, `.yarn/patches/`, `.yarn/versions/` | Yarn 2+ | Committed, per Yarn's gitignore guidance | Yarn Q&A |
| `.yarn/cache/` | Yarn 2+ | Package archives, committed only with Zero-Installs | Yarn Q&A, Caching |
| `.yarn/install-state.gz`, `.yarn/unplugged/`, `.yarn/__virtual__/` | Yarn 2+ | Never committed (covered by `.yarn/*`) | Yarn Q&A, `yarnrc` defaults |
| `.pnp.cjs`, `.pnp.loader.mjs` | Yarn 2+ PnP | Generated loader with the dependency tree; committed only with Zero-Installs | Yarn PnP, Caching |
| `pnpm-workspace.yaml` | pnpm | Workspace root, catalogs and (pnpm 11+) settings | pnpm `pnpm-workspace.yaml`; pnpm 11 post |
| `.pnpmfile.mjs`, `.pnpmfile.cjs` | pnpm | Hooks; `.mjs` takes priority (pnpm 11) | pnpm `pnpmfile`; pnpm 11 post |
| `bun.lock` | Bun ≥ 1.2 | Text lockfile, the default since v1.2 | Bun lockfile |
| `bun.lockb` | Bun < 1.2 | Binary lockfile; Bun documents migrating off it | Bun lockfile |
| `bunfig.toml` | Bun | Project config, "in your project root, alongside your `package.json`" | Bun `bunfig` |
| `deno.json`, `deno.jsonc` | Deno | Config, found in the working directory or a parent | Deno configuration |
| `deno.lock` | Deno | Lockfile; the default path, on by default | Deno `deno.json` reference |

Default registries: npm and Bun use `https://registry.npmjs.org/` (both
stated). Yarn 2+ uses `npmRegistryServer: "https://registry.yarnpkg.com"`
(stated). pnpm's docs state no default URL (`registries` "Default:
undefined"), and Yarn Classic's docs don't state one either. Deno uses `jsr:`
and `npm:` specifiers and recommends JSR.

### Not added

| Candidate | Why not |
|---|---|
| `~/.npmrc`, `~/.yarnrc.yml`, `$HOME/.bunfig.toml`, `$XDG_CONFIG_HOME/.bunfig.toml`, pnpm's `config.yaml` and `auth.ini`, `~/.pnpm/global_pnpmfile.mjs`, Yarn's `${HOME}/.yarn/berry` | User-level. The Bun user file is `.bunfig.toml` (dotted), and the project file is `bunfig.toml`, so only the undotted name is a rule. |
| pnpm `include` files (v12.15+) | Arbitrary names, such as `./config/catalog.yaml`. Not knowable from the path. |
| `.yarn/install-state.gz`, `.yarn/unplugged/`, `.yarn/__virtual__/` | Never meant to be committed. A fallback `.yarn/` rule would still tag them if they are committed. |
| `lerna.json`, `nx.json`, `turbo.json` | Build orchestration, not package management. Possibly a separate issue. |

## Proposed rules

| File | Proposed tags | Filetype |
|---|---|---|
| `.npmrc` | `JavaScript, npm, config` | `npmrc` (INI-like; new) |
| `npm-shrinkwrap.json` | `JavaScript, npm, dependencies` | JSON (unchanged) |
| `.npmignore` | `JavaScript, npm, ignore` | `npmignore` (new) |
| `.yarnrc.yml` | `JavaScript, yarn, npm, config` | YAML (unchanged) |
| `.yarnrc` | `JavaScript, yarn, npm, config` | `yarnrc` (new) |
| path `.yarn/` | `JavaScript, yarn` (decision 5) | — |
| `.pnp.cjs`, `.pnp.loader.mjs` | `JavaScript, yarn, dependencies` (decision 5) | JavaScript (unchanged) |
| `pnpm-workspace.yaml` | `JavaScript, pnpm, npm, config, dependencies` | YAML (unchanged) |
| `.pnpmfile.cjs`, `.pnpmfile.mjs` | `JavaScript, pnpm, config` | JavaScript (unchanged) |
| `bun.lock` | `JavaScript, Bun, npm, dependencies` | Lock (unchanged) |
| `bun.lockb` | `JavaScript, Bun, npm, dependencies, binary` | `Bun Lockfile` (new, non-language) |
| `bunfig.toml` | `JavaScript, Bun, config` | TOML (unchanged) |
| `deno.json`, `deno.jsonc` | `Deno, config` | JSON / JSONC |
| `deno.lock` | `Deno, dependencies` | Lock (unchanged) |
| `package.json`, `package-lock.json` | add `JavaScript` | unchanged |

New tags: `Bun` and `Deno`. New filetypes are added to `NON_LANGUAGE_FILETYPES`.

`npm` is deliberately **not** on the Deno files. Deno can resolve from JSR as
well as npm, and which one a project uses isn't knowable from the path.

## Decisions (taken as recommended)

1. **What `npm` means.** *Recommendation:* the npm ecosystem/registry, with
   each tool tagged separately (`yarn`, `pnpm`, `Bun`). `package.json` and
   `package-lock.json` are both, which is fine. Document it in
   `docs/cli.md`'s tag notes. A path can't show a private registry or
   mirror, so `npm` means "this ecosystem", not "fetched from the public
   registry".
2. **A registry-tag convention across ecosystems.** *Recommendation:* adopt
   OSV's ecosystem names (OSV schema 1.9.2): `npm`, `PyPI`, `crates.io`,
   `RubyGems`, `Packagist`, `Pub`, `Hex`, `NuGet`, `Maven`, `Go`. `npm`,
   `NuGet` and `Go` already match exactly. `maven` would become `Maven`, and
   `PyPi` would become `PyPI`; those are recasings with `DEPRECATED_TAGS`
   entries, in a separate PR. #74 follows whatever is decided here.
3. **Recase `PyPi` to `PyPI`?** *Recommendation:* yes, in that separate PR.
   PyPI's own name is "PyPI", only `requirements.txt` carries the tag today,
   and it matches OSV.
4. **`pnpm-workspace.yaml`: `config` and `dependencies`?** *Recommendation:*
   yes, both. As of pnpm 11 it's the settings file as well as the catalogs.
5. **The `.yarn/` directory and PnP loaders.** Committed `.yarn/releases/*.cjs`
   is a vendored copy of Yarn, and `.pnp.cjs` is generated. Both count as
   JavaScript today and inflate it in kospex.
   *Recommendation:*
   - Tag a fallback `.yarn/` path as `JavaScript, yarn`, and `.pnp.*` as `JavaScript, yarn, dependencies`.
   - Raise `vendored` and `generated` tags as a separate issue. They'd apply
     well beyond Yarn (`dist/`, minified files), and are a vocabulary
     decision in their own right.
6. **`bun.lockb` filetype and `binary`.** *Recommendation:* a new
   non-language filetype `Bun Lockfile`, and add `binary`, so it's excluded
   wherever binaries are.
7. **Deno's language tag.** Deno runs TypeScript and JavaScript.
   *Recommendation:* no language tag, as with Gradle and Mill, which build
   several languages.
8. **New filetypes for `.npmrc`, `.npmignore` and `.yarnrc`.** They have no
   extension and report Unknown. *Recommendation:* give each its own name
   (`npmrc`, `npmignore`, `yarnrc`), following the extensionless-config rule
   for linters in CLAUDE.md.

## Follow-ups

- The registry-tag recasings (`PyPi` → `PyPI`, `maven` → `Maven`) are a
  separate PR, with `DEPRECATED_TAGS` entries (decisions 2 and 3).
- `vendored` and `generated` tags are [#83](https://github.com/kospex/panopticas/issues/83) (decision 5).

## Effect on kospex

Everything proposed adds tags to files that have none, or adds `JavaScript`
to `package.json` and `package-lock.json`. Nothing is removed. The recasings
in decisions 2 and 3 are the only retirements, and they'd be a separate PR.

## Tests

- `tests/test_js_package_managers.py`: every rule; the `.yarn/` directory,
  including a Zero-Installs cache zip that keeps `binary`; `JavaScript` on
  `package.json` and `package-lock.json`; `yarn.lock` and `pnpm-lock.yaml`
  unchanged; the filetypes; the user-level and lookalike names that must stay
  untagged; and `Bun` and `Deno` in the vocabulary. Before the rules were
  added, 29 tests failed and the 9 guards passed.
- Fixtures in `src/tests/`: `.npmrc` (no credentials), `.npmignore`,
  `.yarnrc.yml`, `.yarn/releases/yarn-fixture.cjs`, `pnpm-workspace.yaml`,
  `.pnpmfile.cjs`, `bun.lock`, `bunfig.toml`, `deno.json` and
  `npm-shrinkwrap.json`.
- `tests/data/tag_snapshot.txt`: `Bun` and `Deno`.
- Docs: `docs/cli.md` (the meaning of `npm`, and 139 tags and 100
  filetypes); `docs/api.md` (66 non-languages); `CHANGELOG.md`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://docs.npmjs.com/cli/v12/configuring-npm/npmrc> | Four `.npmrc` levels; scoped `_authToken` (v12.2.1, last edited 2026-02-19) | 2026-11-01 |
| <https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json> | npm 12 no longer reads `npm-shrinkwrap.json`; the format is identical | 2026-11-01 |
| <https://docs.npmjs.com/cli/v11/configuring-npm/npm-shrinkwrap-json> | v11 shrinkwrap: publishable, preferred over `package-lock.json` (last edited 2025-10-05) | 2026-11-01 |
| <https://docs.npmjs.com/cli/v12/using-npm/developers> | `.npmignore`, the `.gitignore` fallback, subdirectories, `files` (last edited 2026-06-29) | 2026-11-01 |
| <https://docs.npmjs.com/cli/v12/using-npm/config> | Default registry `https://registry.npmjs.org/` (last edited 2026-02-11) | 2026-11-01 |
| <https://yarnpkg.com/configuration/yarnrc> | `.yarnrc.yml` naming; `npmRegistryServer` default; `yarnPath`; `.yarn/` folder defaults | 2026-11-01 |
| <https://yarnpkg.com/cli/config/set> | `--home` configuration exists (a user-level `.yarnrc.yml`) | 2026-11-01 |
| <https://yarnpkg.com/migration/guide> | Yarn 2+ ignores `.npmrc` | 2026-11-01 |
| <https://classic.yarnpkg.com/en/docs/yarnrc> | Yarn 1 `.yarnrc`, merged up the file tree | 2026-11-01 |
| <https://yarnpkg.com/cli/set/version> | The release is stored in the project and referenced by `yarnPath`; `packageManager` by default | 2026-11-01 |
| <https://yarnpkg.com/features/pnp> | `.pnp.cjs` is the generated loader | 2026-11-01 |
| <https://yarnpkg.com/features/caching> | Zero-Installs: commit the cache and loader files | 2026-11-01 |
| <https://yarnpkg.com/getting-started/qa> | Which `.yarn/` paths to commit or ignore | 2026-11-01 |
| <https://pnpm.io/pnpm-workspace_yaml> | Workspace root, catalogs, settings | 2026-11-01 |
| <https://pnpm.io/blog/releases/11.0> | Settings moved out of `.npmrc` and `package.json`; `.pnpmfile.mjs` priority | 2026-11-01 |
| <https://pnpm.io/npmrc> | Project `.npmrc` is auth/certificates only; "Add it to `.gitignore`"; read order | 2026-11-01 |
| <https://pnpm.io/pnpmfile> | `.pnpmfile.mjs` and `.pnpmfile.cjs`; global pnpmfile is user-level | 2026-11-01 |
| <https://pnpm.io/settings/dependency-resolution> | `registries` "Default: undefined" | 2026-11-01 |
| <https://pnpm.io/10.x/settings> | `overrides` in `pnpm-workspace.yaml` | 2026-11-01 |
| <https://pnpm.io/config-includes> | `include` (v12.15+) uses arbitrary file names | 2026-11-01 |
| <https://github.com/pnpm/pnpm/releases/tag/v9.5.0> | Catalogs added in 9.5.0 | 2026-11-01 |
| <https://bun.com/docs/pm/lockfile> | `bun.lock` the default since v1.2; migrating from `bun.lockb` | 2026-11-01 |
| <https://bun.com/docs/runtime/bunfig> | `bunfig.toml` at the project root; user-level `.bunfig.toml`; default registry | 2026-11-01 |
| <https://docs.deno.com/runtime/fundamentals/configuration/> | `deno.json` / `deno.jsonc` discovery (updated 2026-06-17) | 2026-11-01 |
| <https://docs.deno.com/runtime/reference/deno_json/> | `deno.lock` default path, on by default (updated 2026-06-25) | 2026-11-01 |
| <https://docs.deno.com/runtime/fundamentals/modules/> | `jsr:` and `npm:` specifiers; JSR recommended (updated 2026-06-30) | 2026-11-01 |
| <https://docs.deno.com/runtime/fundamentals/node/> | Deno reads `.npmrc` (updated 2026-07-30) | 2026-11-01 |
| <https://ossf.github.io/osv-schema/> | Ecosystem names (schema 1.9.2, 2026-10-13) | 2026-11-01 |
| <https://pypi.org/> | The spelling "PyPI" | 2026-11-01 |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://newreleases.io/project/npm/pnpm/release/9.5.0> | Mirrors pnpm 9.5.0's "Added support for catalogs" | Corroborates the release page, and places 9.5.0 in 2024 |
| <https://docs.deno.com/examples/dependency_lockfile_tutorial/> | Search snippet: `deno.lock` is meant to be committed | Not opened. Consistent with tagging `deno.lock` as a repository file |
| <https://docs.deno.com/runtime/packages/supply_chain/> | Search snippet: commit `deno.lock` | Not opened. As above |
| <https://docs.deno.com/runtime/reference/cli/ci/> | Search snippet: commit `deno.lock` for CI | Not opened. As above |
