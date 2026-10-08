# `.kts` and `.gradle` Detection

Closes [#36](https://github.com/kospex/panopticas/issues/36).

## Summary

Neither extension was in `EXT_FILETYPES`, so Kotlin scripts and every Gradle
build script reported `Unknown`:

    build.gradle          ['gradle', 'build', 'dependencies']   'Unknown'
    settings.gradle       []                                    'Unknown'
    build.gradle.kts      []                                    'Unknown'
    script.main.kts       []                                    'Unknown'

## Changes

Two entries in `EXT_FILETYPES`:

    ".gradle": "Groovy"
    ".kts":    "Kotlin"

No logic changed. `get_extension_filetype()` uses `os.path.splitext`, which
returns `.kts` for `build.gradle.kts`, so the one entry covers the Gradle
Kotlin DSL and standalone Kotlin scripts alike.

## Why the mapping is safe

Gradle selects the DSL by file extension alone: a `.gradle` file is compiled as
Groovy and a `.gradle.kts` file as Kotlin. There is no content-dependent case,
so no file needs to be opened. This holds for every `.gradle` file, not only
`build.gradle` — `settings.gradle`, `init.gradle` and script plugins applied
with `apply from:` are all Groovy. `.kts` has no competing use.

## Effect on language counts

Gradle build scripts now count towards a repository's Groovy or Kotlin total.
A pure Java or Android project will show a small amount of Groovy (or Kotlin)
that it did not show before. That is accurate, but it is a visible change in
any language breakdown built on panopticas.

Both `Groovy` and `Kotlin` were already in the language vocabulary, so no new
filetype or language name is introduced.

## Build tags

Three entries in `METADATA_RULES["exact_filename_rules"]`, next to the existing
`build.gradle`:

    "build.gradle.kts":    ["gradle", "build", "dependencies"]
    "settings.gradle":     ["gradle", "build"]
    "settings.gradle.kts": ["gradle", "build"]

`build.gradle.kts` matches `build.gradle` exactly. Before this, a project on
the Gradle Kotlin DSL looked like it declared no dependencies, because only the
Groovy filename was recognised.

The settings files declare which projects are in the build, not what they
depend on, so they carry `gradle` and `build` but not `dependencies`.

No new tag is introduced, and all three files were previously untagged, so the
change is purely additive for kospex.

## Tests

`tests/test_panopticas.py` covers both extensions, the tags for all four Gradle
filenames, and a fixture for each of them in `src/tests/`: `build.gradle`,
`build.gradle.kts`, `settings.gradle` and `settings.gradle.kts`.
