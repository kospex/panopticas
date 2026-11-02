# sbt and Mill: the Maven Ecosystem Tag

Closes [#98](https://github.com/kospex/panopticas/issues/98). Applies the
Ecosystem tags rule from #73 the same way #91 did for Gradle
(`changes/2026-11-gradle-ecosystem.md`). Found while doing #72, where
`.csproj` gained `NuGet` under the same rule.

**Status:** implemented. Verified 2026-11-02.

## Findings

- **OSV** defines `Maven` by package coordinates (`groupId:artifactId`), from
  Maven Central unless a repository is given, regardless of build tool. That
  source is already cited in the Gradle note.
- **sbt.** "sbt uses the standard Maven2 repository by default", and the
  defaults are "Maven Central and the local Ivy repository". Dependencies
  are declared as `groupID % artifactID % revision`. sbt 1.3.0 and later
  resolve with Coursier; earlier versions used Apache Ivy. The page gives the
  Maven2 default without limiting it to either.
- **Mill.** "Mill uses coursier to resolve and download dependencies", and
  dependencies have the form `mvn"{organization}:{name}:{version}"`. The
  documentation pages fetched don't name Mill's default repositories, so
  the source was checked. `CoursierConfigModule.defaultRepositories` (main
  at `5ecbf10320`, 2026-11-01) returns any `mill-repositories` set in the
  build header, followed by `CoursierEnv.defaultRepositories(...)`, which is
  Coursier's own default list. Coursier documents that list as the local
  Ivy repository (`~/.ivy2/local`) and Maven Central.

As with `npm` on yarn files, a path can't show a private repository or an
Ivy-only setup, so `Maven` means "this ecosystem".

## Rules

| File | Tags before | Tags after |
|---|---|---|
| `*.sbt` | `sbt, build, dependencies, Scala` | adds `Maven` |
| `build.mill`, `package.mill`, `build.mill.yaml`, `package.mill.yaml`, `build.sc` | `Mill, build, dependencies` | adds `Maven` |

Only files that carry `dependencies` get the ecosystem, as with Gradle. The
sbt launcher's `.sbtopts` and `.jvmopts`, and Mill's version and options
dotfiles, declare no dependencies and are unchanged.

## Effect on kospex

This only adds tags. `Maven` is already in the vocabulary, so the snapshot
and `DEPRECATED_TAGS` don't change. A query for `Maven` now finds Scala
projects built with sbt or Mill, as well as Maven and Gradle ones.

## Tests

`tests/test_scala_detection.py`: the sbt and Mill build-file expectations
now include `Maven`, which failed for 9 cases before the change. The
options and version-file tests keep their exact sets, so a `Maven` tag
there would fail.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://ossf.github.io/osv-schema/> | The `Maven` ecosystem's definition | 2026-11-02 (in the Gradle note) |
| <https://www.scala-sbt.org/1.x/docs/Library-Management.html> | sbt's default repositories; coordinate format; Coursier since 1.3.0 | 2026-11-02 |
| <https://mill-build.org/mill/fundamentals/library-deps.html> | Mill resolves with Coursier; `mvn"org:name:version"` (Mill 1.3.1 docs) | 2026-11-02 |
| <https://github.com/com-lihaoyi/mill/blob/main/libs/javalib/src/mill/javalib/CoursierConfigModule.scala> | `defaultRepositories`: `mill-repositories` then Coursier's defaults | 2026-11-02 (main at `5ecbf10320`) |
| <https://github.com/com-lihaoyi/mill/blob/main/libs/util/java11/src/mill/util/CoursierConfig.scala> | The same default list, for the non-task path | 2026-11-02 (main at `5ecbf10320`) |
| <https://get-coursier.io/docs/other-repositories> | Coursier's defaults: `~/.ivy2/local` and Maven Central | 2026-11-02 |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://mill-build.org/api/latest/mill/javalib/CoursierModule.html> | `repositoriesTask` must be overridden when `CoursierModule` is used stand-alone | Didn't state the default list; source checked instead |
| <https://github.com/com-lihaoyi/mill/pull/2954> | Mill reads Coursier's default config, including `repositories.defaults` | Background; led to the source files above |
| <https://mill-build.org/api/latest/mill/scalalib/CoursierConfigModule$.html> | — | Returned 404 on 2026-11-02 |
| <https://mill-build.org/api/latest/mill/api/daemon/MillRepositories$.html> | Search result only, about `mill-repositories` | Not fetched |
