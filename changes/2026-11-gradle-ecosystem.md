# Gradle: the Maven Ecosystem Tag, Catalog, Lockfiles and Wrapper

Closes [#91](https://github.com/kospex/panopticas/issues/91). Follows the
Ecosystem tags rule from #73 and the remaining gap recorded in
`changes/2026-11-dependency-manifests.md`.

**Status:** implemented. Verified 2026-11-02 against Gradle's user guide
(version 9.8.2) and the OSV schema.

## Current state

Counts are from a local kospex database (376 repositories), current files
only.

| File | Files / repos | Tags before |
|---|---|---|
| `build.gradle` | 1,065 / 13 | `gradle, build, dependencies` |
| `build.gradle.kts` | 426 / 13 | `gradle, build, dependencies` |
| `settings.gradle` / `.kts` | 44 / 12, 34 / 12 | `gradle, build` |
| `gradle/libs.versions.toml` | 18 / 13 | none |
| `gradle.properties` | 185 / 17 | none |
| `gradle-wrapper.properties` | 33 / 16 | none |
| `gradle.lockfile` | 0 | none (`Unknown`) |
| `pom.xml`, for comparison | 13 / 6 | `Maven, build, dependencies` |

## Findings

- **The ecosystem is `Maven`.** OSV defines `Maven` by package coordinates,
  not by build tool: "The Maven Java package ecosystem. The `name` field is
  a Maven package name in the format `groupId:artifactId`". It assumes
  Maven Central unless a repository suffix is given, and doesn't mention
  Gradle. Gradle resolves "from one or many repositories based on Maven, Ivy
  or flat directory formats". Its own example is Maven Central
  (`mavenCentral()`) with the coordinate `com.google.guava:guava:30.0-jre`.
  Ivy and flat-directory repositories exist, but a path can't show them, and
  Maven repositories are the default case.
- **The version catalog** is "conventionally declared using a
  `libs.versions.toml` file located in the `gradle` subdirectory", and
  "Gradle automatically imports a catalog in the `gradle` directory named
  `libs.versions.toml`." It's TOML. Other catalogs can have any name and must
  be declared, so only the default name is matched.
- **Lockfiles.** "A file named `gradle.lockfile`, located at the root of each
  project or subproject directory", except "the lockfile for the buildscript
  itself, which is named `buildscript-gradle.lockfile`". "Lockfiles should be
  checked in to source control." A custom name can be set with
  `dependencyLocking { lockFile = ... }`; those aren't matched.
- **`gradle.properties`** is read from "the root directory of your project",
  from "the Gradle user home directory (`GRADLE_USER_HOME`)" (default
  `~/.gradle`), and from `GRADLE_HOME`. The user-level copies are outside any
  repository. A copy inside a repository is project config.
- **The Wrapper.** `gradlew` and `gradlew.bat` are "a shell script and a
  Windows batch script for executing the build with the Wrapper", and you
  "need to check them into version control". `gradle-wrapper.jar`: "Adding
  the JAR file to version control is expected." `gradle-wrapper.properties`
  configures "the Wrapper runtime behavior", including the Gradle version,
  and "is to be committed".

## Rules

| File | Tags |
|---|---|
| `build.gradle`, `build.gradle.kts` | `gradle, build, dependencies, Maven` |
| `libs.versions.toml` | `gradle, dependencies, Maven` |
| `gradle.lockfile`, `buildscript-gradle.lockfile` | `gradle, dependencies, Maven`; filetype `Lock` |
| `gradle.properties` | `gradle, build, config` |
| `gradle-wrapper.properties` | `gradle, build, config` |
| `gradlew`, `gradlew.bat` | `gradle, build` |
| `gradle-wrapper.jar` | `binary` (from `.jar`), `gradle, build` |
| `settings.gradle(.kts)` | unchanged: `gradle, build` |

## Decisions

The four questions in #91 were taken as recommended:

1. `Maven` is the ecosystem for Gradle files.
2. Only files that declare or lock dependencies get it. Settings files
   declare the build and its repositories, so they don't; nor do the
   properties and Wrapper files.
3. `gradle.properties` is tagged by name. The user-level copy lives outside
   any repository, as with `uv.toml` and `.cargo/config.toml`.
4. `gradle` keeps its lower-case spelling. Recasing it to the vendor's
   "Gradle" would be a retirement with a `DEPRECATED_TAGS` entry, and wasn't
   asked for.

As implemented:

- `libs.versions.toml` is matched by exact filename, not by the
  `gradle/libs.versions.toml` path. The name is Gradle's own convention, and
  an exact rule is simpler than a path fragment.
- `gradlew` and `gradlew.bat` get no filetype. `gradlew` is a shell script
  that shebang detection already finds. `.bat` has no filetype yet; that's
  [#78](https://github.com/kospex/panopticas/issues/78).

## Effect on kospex

This only adds tags. `build.gradle(.kts)` gains `Maven`, and the catalog,
lockfiles, properties and Wrapper files gain tags they didn't have. No tag
enters or leaves the vocabulary, so the snapshot doesn't change. A query for
`Maven` now finds Gradle projects as well as `pom.xml` ones.

## Tests

- `tests/test_gradle_packaging.py` covers:
  - every rule;
  - subproject paths;
  - settings files staying without `Maven`;
  - `pom.xml` unchanged;
  - lookalikes (`gradle/other.versions.toml`, `my-gradle.lockfile`,
    `gradlew.sh`), which must not be tagged;
  - the filetypes.
- `tests/test_panopticas.py`: `test_gradle_kotlin_dsl_build_file` now
  expects `Maven`.
- 15 tests failed before the change.
- Fixtures are in `src/tests/gradleproj/`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://ossf.github.io/osv-schema/> | The `Maven` ecosystem's definition; no mention of Gradle | 2026-11-02 |
| <https://docs.gradle.org/current/userguide/declaring_repositories.html> | Repository formats; Maven Central; coordinate example | 2026-11-02 |
| <https://docs.gradle.org/current/userguide/version_catalogs.html> | `gradle/libs.versions.toml`, imported automatically, TOML | 2026-11-02 |
| <https://docs.gradle.org/current/userguide/dependency_locking.html> | `gradle.lockfile`, `buildscript-gradle.lockfile`; commit them | 2026-11-02 |
| <https://docs.gradle.org/current/userguide/build_environment.html> | `gradle.properties` locations and precedence | 2026-11-02 |
| <https://docs.gradle.org/current/userguide/gradle_wrapper.html> | The Wrapper's four files; commit them | 2026-11-02 |

No leads: every page above was used.
