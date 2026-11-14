# Gradle: Tag Every Gradle Script, and `is_gradle_script()`

Closes [#112](https://github.com/kospex/panopticas/issues/112). Follows [#91](https://github.com/kospex/panopticas/issues/91)
(`changes/2026-11-gradle-ecosystem.md`), and reverses its decision 2.

**Status:** implemented. Verified 2026-11-13 against Gradle's user guide and
Javadoc (`current`).

## Problem

Panopticas tagged Gradle files by exact name: `build.gradle(.kts)` as
`gradle, build, dependencies, Maven`, and `settings.gradle(.kts)` as
`gradle, build`. Any other `*.gradle` or `*.gradle.kts` file had no tags.
`.gradle` maps to Groovy and `.kts` to Kotlin, so their language was right,
but nothing marked them as Gradle or as declaring dependencies.

kospex only reads dependency files that panopticas tags `dependencies`, so
it never saw these files. In a Java codebase where each library or service
had its own `.gradle` file, every one declared dependencies
(`implementation(...)`) and none was read.

## Current state

Counts are from a local kospex database (403 repositories), using the files
git tracks in each synced repository.

| File | Files | Tags before |
|---|---|---|
| `build.gradle` / `.kts` | unchanged by this note | `gradle, build, dependencies, Maven` |
| `settings.gradle` / `.kts` | 77 | `gradle, build` |
| Any other `*.gradle` / `*.gradle.kts` | 148, in 11 repositories | none |

The 148 include:

- renamed build files: every library in firebase-android-sdk
  (`firebase-ai.gradle.kts` and so on);
- script plugins (`errorProne.gradle`, `github_build.gradle`);
- precompiled script plugins (`okhttp.base-conventions.gradle.kts`,
  `bom-conventions.gradle.kts`);
- a committed init script (`dependency-fetcher-init.gradle`).

kospex's existing Gradle build-file parser read 85 of the 148 with rows
(about 1,060 dependencies, 982 of them in firebase-android-sdk), found 48
declaring none, and refused 15. The refused files declare dependencies in
forms it can't read statically, such as `libs.findLibrary(...)` helpers.

Of the 77 settings files, the same parser found plugin or classpath rows in
10 and refused none.

## Findings

- **The extension picks the DSL, not the name.** "Groovy DSL script files
  use the `.gradle` file name extension." "Kotlin DSL script files use the
  `.gradle.kts` file name extension." "To activate the Kotlin DSL, use the
  `.gradle.kts` extension for your build scripts instead of `.gradle`. This
  also applies to the settings file (e.g., `settings.gradle.kts`) and
  initialization scripts." Groovy and Kotlin "are the only accepted
  languages for Gradle scripts."
- **`build.gradle` is only the default.** `ProjectDescriptor.setBuildFileName`
  "Sets the name of the build file. This name is interpreted relative to the
  project directory." firebase-android-sdk's root `settings.gradle.kts` sets
  `project.buildFileName = name` for every project, and
  `health-metrics/apk-size/settings.gradle` sets
  `rootProject.buildFileName='apk-size.gradle'`.
- **Script plugins:** "A script plugin is a plugin written directly in a
  build file (`.gradle` or `.gradle.kts`)", applied with
  `apply from: 'other.gradle'`. Gradle's own advice is that "Script plugins
  should be avoided", but they are common in older builds.
- **Precompiled script plugins:** "a `.gradle.kts` (Kotlin DSL) or `.gradle`
  (Groovy DSL) script stored in a plugin source set (e.g. `buildSrc` or an
  included build like `build-logic`)". "The plugin ID is derived from the
  file name". The suffix sets the scope: `.settings.gradle(.kts)` is a
  settings plugin, `.init.gradle(.kts)` an init plugin, and a plain name a
  project plugin.
- **Init scripts** are passed with `-I` / `--init-script` (any path), or read
  from `GRADLE_USER_HOME/init.gradle(.kts)` and `*.init.gradle(.kts)` in an
  `init.d/` directory. The user-level locations are outside any repository.
  A committed one is usually run with `-I`.
- **Settings files declare dependencies too.** A settings file's
  `plugins { }` block applies settings plugins by id and version, such as
  `foojay-resolver-convention`, `refreshVersions` and `develocity`. A
  `buildscript { dependencies { classpath ... } }` block adds a classpath.
  `pluginManagement { plugins { } }` only sets default plugin versions; that
  is for a consumer to tell apart, not a reason to leave the file untagged.

## Rules

| Match | Tags |
|---|---|
| `is_gradle_script(filename)`: `^.+\.gradle(\.kts)?$`, case-insensitive | `gradle, build, dependencies, Maven` |
| `settings.gradle`, `settings.gradle.kts` (exact) | was `gradle, build`; now `gradle, build, dependencies, Maven` |
| `build.gradle`, `build.gradle.kts` (exact) | unchanged |
| `gradle.properties`, `gradlew`, `gradlew.bat`, Wrapper files, lockfiles, `libs.versions.toml` | unchanged; they aren't scripts and the predicate doesn't match them |

## Decisions

1. **A predicate, not an extension rule.** `get_fileext()` sees `.kts` for
   `foo.gradle.kts`, and `.kts` is also any Kotlin script, so an extension
   rule can't express the Kotlin DSL. A function rule covers both
   extensions in one place.
2. **The predicate is public API, exported from the package.** kospex keeps
   its own registry of dependency files. Each entry recognises filenames
   with a regex, which can drift from panopticas' rules: its requirements
   regex once missed `requirements-wheel-test.txt`, which panopticas
   matched. kospex already delegates to `is_pip_requirements` by name. It
   can delegate Gradle recognition to `is_gradle_script` in the same way,
   so the two can't disagree.
3. **Every Gradle script gets `dependencies` and `Maven`.** This includes
   scripts that turn out to declare none. Whether a file declares
   dependencies can only be told by reading it, and panopticas doesn't open
   files. A consumer that reads a file and finds nothing records it as
   empty, which is the honest result. Leaving the file untagged would hide
   the 85 that do declare dependencies.
4. **Settings files get `dependencies` and `Maven`.** This reverses #91's
   decision 2 ("Settings files declare the build and its repositories, so
   they don't"), on the 10 of 77 settings files above. The exact rules now
   state the full tags rather than relying on the function rule's merge.
5. **The bare `.gradle` doesn't match.** It is Gradle's project cache
   directory, usually gitignored, and never a script. `.gradle.kts` alone
   doesn't match either.
6. **Case-insensitive**, as `extension_rules` have been since
   `changes/2026-11-extension-rules-case.md`.
7. **No new tag and no new filetype.** `gradle`, `build`, `dependencies` and
   `Maven` are all in the vocabulary, so `tests/data/tag_snapshot.txt` is
   unchanged. Languages are unchanged: `.gradle` is Groovy, `.gradle.kts`
   is Kotlin.

## Effect on kospex

The change only adds tags. On re-sync (kospex re-tags when
`last_panopticas_version` changes), 225 files on the estate above gain
`dependencies`: 148 scripts and 77 settings files.

**kospex should change its registry before or with the version pin that
picks this up.** Its `gradle-build` entry matches only
`build\.gradle(\.kts)?`. A newly tagged script that matches no registry
entry is reported `unclassified`, and that outcome outranks `extracted` in
a repository's headline. The kospex change is to delegate that entry
to `is_gradle_script` and raise its panopticas floor to this version in the
same change. kospex's delegation returns False when the predicate is
missing, so without the floor an older panopticas would stop
`build.gradle` matching at all.

## Tests

- `tests/test_gradle_packaging.py`:
  - `test_any_gradle_script`: renamed build files, script plugins,
    precompiled script plugins of each scope, init scripts, mixed case.
  - `test_is_gradle_script`: the predicate on scripts, on the non-script
    Gradle files, on plain `.kts`, on lookalikes (`build.gradle.bak`,
    `build.gradle.kts.orig`, `gradle.kts`) and on the bare `.gradle`.
  - `test_is_gradle_script_is_exported`: it is in `__all__`.
  - `test_plain_kotlin_scripts_not_gradle`: `*.kts` stays untagged.
  - `test_settings_declare_dependencies` replaces
    `test_settings_get_no_ecosystem`.
  - `properties.gradle` left the lookalike list: it is a Gradle script.
- `tests/test_panopticas.py`: `test_gradle_settings_file` now expects
  `dependencies` and `Maven`.
- Before the change, collection failed with an ImportError (no
  `is_gradle_script`). After it, the full suite passes (1,555 tests).

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://docs.gradle.org/current/userguide/kotlin_dsl.html> | `.gradle` is Groovy DSL, `.gradle.kts` is Kotlin DSL, for build, settings and init scripts; mixing both in one build | 2026-11-13 |
| <https://docs.gradle.org/current/userguide/build_file_basics.html> | `build.gradle(.kts)` as the build script; Groovy and Kotlin as the only script languages | 2026-11-13 |
| <https://docs.gradle.org/current/javadoc/org/gradle/api/initialization/ProjectDescriptor.html> | `setBuildFileName`: the build file can be renamed | 2026-11-13 |
| <https://docs.gradle.org/current/userguide/plugins.html> | Script plugins, `apply from:`; "should be avoided" | 2026-11-13 |
| <https://docs.gradle.org/current/userguide/implementing_gradle_plugins_precompiled.html> | Precompiled script plugins, plugin id from the file name, scope from the suffix | 2026-11-13 |
| <https://docs.gradle.org/current/userguide/init_scripts.html> | Init script names and locations | 2026-11-13 |

## Leads

| Page | Why it's here | Checked |
|---|---|---|
| <https://docs.gradle.org/current/userguide/script_plugins.html> | Tried for script plugins; 404. `plugins.html` covers them | 2026-11-13 |
| <https://docs.gradle.org/current/dsl/org.gradle.api.initialization.ProjectDescriptor.html> | Tried for `buildFileName`'s default; 404. The Javadoc above confirms the setter but states no default | 2026-11-13 |
