# Scala, sbt, Mill and Scala Linter Detection

**Status:** proposed, not yet implemented. Tracked in
[#56](https://github.com/kospex/panopticas/issues/56), for which the research
below is the evidence base.

## Summary

The only Scala support today is `.scala` → `Scala`. Every other Scala file
reports `Unknown`, and none of the build or tooling files gets a tag:

    path                      ext              filetype     tags
    build.sbt                 '.sbt'           'Unknown'    []
    project/plugins.sbt       '.sbt'           'Unknown'    []
    project/build.properties  '.properties'    'Properties' []
    build.sc                  '.sc'            'Unknown'    []
    build.mill                '.mill'          'Unknown'    []
    build.mill.yaml           '.yaml'          'YAML'       []
    .mill-version             '.mill-version'  'Unknown'    []
    .scalafmt.conf            '.conf'          'Unknown'    []
    .scalafix.conf            '.conf'          'Unknown'    []
    scalastyle-config.xml     '.xml'           'XML'        []

So a repository that builds with sbt looks like it has no build file and
declares no dependencies. A Gradle or Maven project shows both.

## Proposed changes

### 1. Extensions (`EXT_FILETYPES`)

| Extension | Filetype | Why |
|---|---|---|
| `.sbt` | `Scala` | sbt build definitions are Scala, in a DSL. |
| `.sc` | `Scala` | Scala scripts (Scala CLI, Ammonite), worksheets, and Mill build files before 0.12. All of them are Scala. |
| `.mill` | `Scala` | Mill build files from 0.12 onwards. The 1.0.0 changelog says "`build.mill` and `package.mill` files are now written in Scala 3.7.1". |
| `.mill-version` | `mill-version` | Version pin file, the same pattern as `.python-version` and `.nvmrc`. |
| `.mill-jvm-version` | `mill-jvm-version` | Mill's JVM version pin. |
| `.mill-opts`, `.mill-jvm-opts` | `mill-opts`, `mill-jvm-opts` | Launcher and JVM options for Mill, one per line. |
| `.sbtopts`, `.jvmopts` | `sbtopts`, `jvmopts` | Launcher and JVM options for sbt, one per line. |

`Scala` is already a language, so the three source extensions add no new
vocabulary. The version and options files each get their own filetype name,
because none of them documents a standard content format. All of these new
names go into `NON_LANGUAGE_FILETYPES`.

`.mill.yaml` needs no entry. `os.path.splitext` returns `.yaml`, so
`build.mill.yaml` already resolves to `YAML`.

### 2. Config filetypes by basename (`LANGUAGE_BY_BASENAME`)

`.conf` is used for arbitrary formats, so these are mapped by basename, the
same reasoning as `staticcheck.conf`:

| Basename | Filetype |
|---|---|
| `.scalafmt.conf` | `HOCON` |
| `.scalafix.conf` | `HOCON` |
| `mill-version` | `mill-version` (the `.config/mill-version` form) |

Both tools document HOCON as the only format. `HOCON` is a new filetype and
goes into `NON_LANGUAGE_FILETYPES`.

### 3. Build tags (`METADATA_RULES`)

| Rule | Match | Tags |
|---|---|---|
| extension | `.sbt` | `sbt`, `build`, `dependencies`, `Scala` |
| exact | `build.mill` | `Mill`, `build`, `dependencies` |
| exact | `package.mill` | `Mill`, `build`, `dependencies` |
| exact | `build.mill.yaml` | `Mill`, `build`, `dependencies` |
| exact | `package.mill.yaml` | `Mill`, `build`, `dependencies` |
| exact | `build.sc` | `Mill`, `build`, `dependencies` (judgement call, see below) |
| exact | `.mill-version` | `Mill`, `build` |
| exact | `mill-version` | `Mill`, `build` |
| exact | `.mill-jvm-version`, `.mill-opts`, `.mill-jvm-opts` | `Mill`, `build` |
| exact | `.sbtopts`, `.jvmopts` | `sbt`, `build` |

**sbt options files.** The sbt launcher reads `.sbtopts` and `.jvmopts` from
the current directory, which in practice is the project root. Its usage text
says: "`.jvmopts` if this file exists in the current directory, its contents
are appended to `JAVA_OPTS`". The command-line reference documents both files.
The launcher's machine-level and user-level files are named `sbtopts` without
a leading dot (`/etc/sbt/sbtopts`, `${config_home}/sbtopts`, `conf/sbtopts`),
so an exact `.sbtopts` rule cannot match them.

The name `.jvmopts` sounds JVM-generic, but it is tagged `sbt` and not `JVM`.
Its readers are sbt's launcher and the sbt-extras script, and nothing else.
The other JVM build tools have their own files: Maven uses `.mvn/jvm.config`
(documented on [Configuring Apache Maven](https://maven.apache.org/configure.html)),
and Gradle uses `org.gradle.jvmargs` in `gradle.properties`. Kotlin projects
build through one of those two. A `.jvmopts` in a Java project still means the
project builds with sbt.

**Mill options files.** `.mill-jvm-version`, `.mill-opts` and
`.mill-jvm-opts` came up while checking the Mill changelog: 0.12.1 added
`.mill-opts` and env-var interpolation in `.mill-jvm-opts`, and 1.0.0
describes `.mill-jvm-version` as an "external configuration file". Mill 1.0's
`//|` build header can now set the same values, but the files are still read.

**sbt uses an extension rule, not `build.sbt`.** The sbt docs say the build is
defined in "`build.sbt` (actually any files named `*.sbt`)", and that
"naming them `build.sbt` … [is a] convention only". sbt's own plugin examples
use `project/assembly.sbt` and `project/site.sbt`, not `plugins.sbt`. Any
`.sbt` file can declare `libraryDependencies` or `addSbtPlugin`, so all of them
get `dependencies`.

An extension rule also avoids duplicate tags. `get_filename_metatypes()`
concatenates the extension and exact-filename results without de-duplicating,
so an exact `build.sbt` rule on top of an extension rule would emit `sbt` and
`build` twice.

**Mill uses exact names, not `.mill`.** A Mill build can contain helper `.mill`
files that are imported rather than being module definitions. Only
`build.mill` and `package.mill` (and their `.yaml` forms) define modules and
their dependencies.

**Language tag.** `.sbt` carries `Scala`, the same way `pyproject.toml` carries
`Python` and `go.mod` carries `Go`. Mill does not: it builds Java and Kotlin
projects as first-class targets, so like Gradle it gets no language tag.

**Tool casing.** sbt brands itself in lowercase (`sbt`), and Mill is
capitalised (`Mill`). This follows the vendor-casing rule.

### 4. Linter and formatter rules (`LINTER_RULES`)

```python
"Scalafmt": {
    "languages": ["Scala"],
    "roles": ["formatter"],
    "config": [".scalafmt.conf"],
},
"Scalafix": {
    "languages": ["Scala"],
    "roles": ["linter"],
    "config": [".scalafix.conf"],
},
"Scalastyle": {
    "languages": ["Scala"],
    "roles": ["linter"],
    "config": ["scalastyle-config.xml", "scalastyle-test-config.xml"],
},
```

- **Scalafmt** reads `.scalafmt.conf` from the current directory, then from the
  root of the git repository. This is a project-level path, not a user-level one.
- **Scalafix** "reads configuration from a file `.scalafix.conf` in the root
  directory of your project". It rewrites code as well as linting it, but its
  rewrites are refactorings, not canonical formatting, so it gets `linter` and
  not `formatter`.
- **Scalastyle**: the sbt plugin defaults `scalastyleConfig` to
  `file("scalastyle-config.xml")`, with `scalastyle-test-config.xml` used for
  `Test` (`Plugin.scala`, lines 96–101). The tool is effectively unmaintained
  (core repo last pushed 2022-09, sbt plugin 2020-01), but it is kept for the
  same reason legacy `.eslintrc` names are kept: a repository that has the file
  still uses Scalastyle.

## Considered and not proposed

| Candidate | Why not |
|---|---|
| `project.scala` (Scala CLI) | The docs only *recommend* this name, and any `.scala` file can hold `//> using` directives. Basenames are matched in lowercase, so the rule would also hit `Project.scala` source files and sbt `project/Project.scala` helpers. It would mislabel repositories. |
| `project/build.properties` (sbt version pin) | Documented by sbt, but `build.properties` is also Apache Ant's conventional name. `path_contains` is a substring match, so `subproject/build.properties` in an Ant build would match. `.sbt` files already identify the build. Revisit if path matching becomes component-aware. |
| `.scala-build/`, `.bsp/`, `.bloop/`, `.metals/` | Generated by Scala CLI, BSP, Bloop and Metals, and normally gitignored. They are build and IDE output, not repository configuration. |
| `mill` / `mill.bat` bootstrap scripts | The extensionless name `mill` is too generic to tag. The script already resolves to `Shell` through its shebang. |
| WartRemover | No config file. It is configured through sbt settings (`wartremoverErrors`, `wartremoverWarnings`, `wartremoverExcluded`), `-P:wartremover:` scalac options, the gradle-wartremover plugin, or scala-maven-plugin `<args>`. The same case as Spotless. |
| Scapegoat | No config file. It is configured through sbt-scapegoat settings (`scapegoatDisabledInspections`, `scapegoatIgnoredFiles`, …) or `-P:scapegoat:` scalac options. Its reports go to `target/`, which is build output. |
| `scalac -Xlint` | Compiler flags only. |

### Judgement call: `build.sc` (decided: include)

Mill used `build.sc` up to 0.11. The 0.12.0 changelog says:

> The `build.sc` file has been renamed `build.mill` to prevent confusion with
> Ammonite/Scala-CLI scripts.

Mill 1.1.0 then stopped recognising `.sc` build files altogether. The rename
was made because `build.sc` is ambiguous: a Scala CLI or Ammonite script could
have that name. In practice, though, `build.sc` at a repository root is almost
always a pre-0.12 Mill build, and those repositories are still common, so it
is included. This is the same kind of call as `checkstyle.xml`: the name is
unambiguous in practice even though nothing guarantees it.

## Effect on kospex

All of this is additive: new filetypes and new tags, with nothing renamed or
removed. Two effects will be visible:

- `.sbt`, `.sc` and `.mill` files now count towards a repository's Scala
  total, so an sbt or Mill project shows slightly more Scala than before.
  Mill builds of Java projects gain a small Scala share. This is the same
  effect `.gradle` had on Groovy.
- New tags: `sbt`, `Mill`, `Scalafmt`, `Scalafix`, `Scalastyle`. New filetypes:
  `HOCON`, `mill-version`, `mill-jvm-version`, `mill-opts`, `mill-jvm-opts`,
  `sbtopts`, `jvmopts`.

## Docs and tests

- `docs/linter-detection-rules.md`: add a Scala section to the inventory, the
  sources, and the rejected rows above that apply to linters.
- `src/tests/` fixtures: `build.sbt`, `project/plugins.sbt`, `build.mill`,
  `package.mill`, `build.mill.yaml`, `build.sc`, `.mill-version`,
  `.mill-jvm-version`, `.mill-opts`, `.mill-jvm-opts`, `.sbtopts`, `.jvmopts`,
  `.scalafmt.conf`, `.scalafix.conf`, `scalastyle-config.xml`, plus a `.sc`
  script.
- `tests/test_panopticas.py`: filetype and tag assertions for each fixture,
  plus negative cases: `Project.scala` gets no build tag, and
  `project/build.properties` stays `Properties` with no tags.

## Sources

| Tool | Source |
|---|---|
| sbt | [Directory structure](https://www.scala-sbt.org/1.x/docs/Directories.html), [Organizing the build](https://www.scala-sbt.org/1.x/docs/Organizing-Build.html), [Using plugins](https://www.scala-sbt.org/1.x/docs/Using-Plugins.html), [Build definition](https://www.scala-sbt.org/1.x/docs/Basic-Def.html), [Command line reference](https://www.scala-sbt.org/1.x/docs/Command-Line-Reference.html) and the [`sbt` launcher script](https://github.com/sbt/sbt/blob/develop/sbt) (`.sbtopts`, `.jvmopts`); [sbt-extras](https://github.com/paulp/sbt-extras) also reads `.jvmopts` |
| Maven | [Configuring Apache Maven](https://maven.apache.org/configure.html) (`.mvn/jvm.config`, the reason `.jvmopts` is not tagged `JVM`) |
| WartRemover | [Install and setup](https://www.wartremover.org/doc/install-setup.html) |
| Scapegoat | [scapegoat README](https://github.com/scapegoat-scala/scapegoat), [sbt-scapegoat README](https://github.com/scapegoat-scala/sbt-scapegoat) |
| Mill | [Installation & IDE setup](https://mill-build.org/mill/cli/installation-ide.html) (`.mill-version`, `.config/mill-version`); [`changelog.adoc`](https://github.com/com-lihaoyi/mill/blob/main/changelog.adoc), entries 0.12.0 (`build.sc` → `build.mill`, `package.mill`), 1.0.0 (Scala 3 build files) and 1.1.0 (`build.mill.yaml`; `.sc` no longer recognised) |
| Scala CLI | [Using directives](https://scala-cli.virtuslab.org/docs/guides/introduction/using-directives/), [Root directory](https://scala-cli.virtuslab.org/docs/reference/root-dir/) |
| Scalafmt | [Configuration](https://scalameta.org/scalafmt/docs/configuration.html), [Installation](https://scalameta.org/scalafmt/docs/installation.html) |
| Scalafix | [Configuration](https://scalacenter.github.io/scalafix/docs/users/configuration.html) |
| Scalastyle | [`Plugin.scala`](https://github.com/scalastyle/scalastyle-sbt-plugin/blob/master/src/main/scala/org/scalastyle/sbt/Plugin.scala) in scalastyle-sbt-plugin; [scalastyle/scalastyle](https://github.com/scalastyle/scalastyle) for the maintenance status (last pushed 2022-09). scalastyle.org returned 503 during research. |
