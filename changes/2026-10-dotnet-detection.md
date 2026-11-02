# .NET Build, Dependency, Language and Tooling Detection

For [#72](https://github.com/kospex/panopticas/issues/72).

**Status:** part one implemented (build, dependency and config files, and
the `Global.asax` fix). Part two (languages, linters and editors) is still
to do. Researched 2026-10-30; the three open checks were done 2026-11-02.
See *Decisions* and *Implemented: part one* at the end.

## Summary

Only C# and the classic Visual Studio files are covered. In a modern .NET
repository, most of the build and dependency files have no tags, and F#,
Visual Basic, Razor and XAML report `Unknown`:

    path                                      filetype                tags
    App.sln                                   Visual Studio Solution  .NET, Visual Studio, build
    App.slnx                                  Unknown                 []
    src/App/App.csproj                        C# Project              .NET, C#, build, dependencies
    src/Lib/Lib.fsproj                        Unknown                 []
    src/Vb/Vb.vbproj                          Unknown                 []
    Directory.Build.props                     Unknown                 []
    Directory.Build.targets                   Unknown                 []
    Directory.Packages.props                  Unknown                 []
    global.json                               JSON                    []
    src/App/packages.lock.json                JSON                    []
    .config/dotnet-tools.json                 JSON                    []
    paket.dependencies                        Unknown                 []
    build.cake                                Unknown                 []
    src/Lib/Lib.fs, x.fsi, x.fsx              Unknown                 []
    x.vb                                      Unknown                 []
    Pages/Index.cshtml, Counter.razor         Unknown                 []
    MainWindow.xaml                           Unknown                 []
    App.sln.DotSettings                       Unknown                 []
    .csharpierrc                              Unknown                 []
    Global.asax                               Unknown                 .NET, ASP.NET   (bug, below)

Already covered: `.sln`, `.csproj`, `.cs`, `.dll`, `.aspx`, `.ascx`,
`packages.config`, `nuget.config`, `web.config`, `app.config`, and the
Roslyn (`.globalconfig`, `.ruleset`) and StyleCop (`stylecop.json`) linter
rules.

The effect is the same one Scala had before #56: a project using F#, VB,
central package management or a lock file looks as if it has no build files
or dependencies.

## Two existing bugs found

### `Global.asax` reports `Unknown`

`EXT_FILETYPES` has the key `".global.asax"` → `ASP.NET Global`. Extensions
come from `os.path.splitext`, which returns `.asax`, so that key can never
match. It has been dead since 0.0.16 (`985aedb`). The `global.asax`
exact-filename rule still adds tags, so only the filetype is wrong.

Fix: map `global.asax` in `LANGUAGE_BY_BASENAME`, or add `.asax` →
`ASP.NET Global` to `EXT_FILETYPES`, and remove the dead key.

### Extension rules are case-sensitive

**Now tracked in [#80](https://github.com/kospex/panopticas/issues/80)**, to
be fixed separately from #72. It affects every extension rule, not only .NET.
The `Global.asax` bug above stays in #72. The analysis below is kept for
reference.

`get_extension_filetype()` lowercases the extension; `get_filename_metatypes()`
does not, before looking up `extension_rules`:

    App.CSPROJ   filetype C# Project              tags []
    App.Sln      filetype Visual Studio Solution  tags []

Exact-filename rules are lowercased, so only extension rules are affected.
It matters here because Rider's `*.sln.DotSettings` extension is always
mixed case, and repositories from Windows often have upper-case extensions.

Fix: lowercase `ext` in `get_filename_metatypes()`. All `extension_rules`
keys are already lowercase. This changes tags only for files whose extension
has upper-case letters, adding the tags they should always have had. It
needs a CHANGELOG line, and a test over every extension rule in upper case.

## Verified conventions and proposals

Proposed tags reuse existing vocabulary where possible (`.NET`, `NuGet`,
`build`, `dependencies`, `config`, `Visual Studio`, `JetBrains`, `editor`).
New tags are marked **new**.

### Solutions: `.slnx` and `.slnf`

> we've moved away from a proprietary format and adopted XML for the
> solution file structure.

MSBuild, the .NET CLI and C# Dev Kit support `.slnx`. Microsoft
"strongly recommend[s] not having both .SLN and .SLNX files in the same
repository". Solution filters (`.slnf`) "will continue to work with the new
.SLNX format". A third-party post says .NET 10 makes `.slnx` the default for
`dotnet new sln`; that is not confirmed from Microsoft.

| Extension | Filetype | Tags |
|---|---|---|
| `.slnx` | `Visual Studio Solution` (reuse) | `.NET`, `Visual Studio`, `build` (as `.sln`) |
| `.slnf` | `JSON` | `.NET`, `Visual Studio`, `build` |

Sources: <https://devblogs.microsoft.com/visualstudio/new-simpler-solution-file-format/>,
<https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview> (globs
exclude `**/*.sln(x)`)

### Project files: `.fsproj`, `.vbproj`

> Project files, which have extensions like *.csproj* for C# projects and
> *.fsproj* for F# projects, are in XML format.

`.vbproj` is not named on that page. It needs a Microsoft source before it is
added, though it is the long-standing Visual Basic project extension.

| Extension | Filetype | Tags |
|---|---|---|
| `.fsproj` | `F# Project` **new filetype** | `.NET`, `F#` **new**, `build`, `dependencies` |
| `.vbproj` | `Visual Basic Project` **new filetype** | `.NET`, `Visual Basic` **new**, `build`, `dependencies` |

Source: <https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview>

### MSBuild directory files

From *Customize the build by folder* (updated 2026-10-20):

| File | Purpose (Microsoft's table) |
|---|---|
| `Directory.Build.props` | Set default properties for projects |
| `Directory.Build.targets` | Add custom targets and late properties |
| `Directory.Build.rsp` | Set default command-line arguments |
| `Directory.Solution.props` | Set properties for solution builds |
| `Directory.Solution.targets` | Add targets for solution builds |

MSBuild searches upward from the project. On Linux, "the casing of the
*Directory.Build.props* filename [must match] exactly". Panopticas matches
exact filenames lowercased, which is more lenient, as with `claude.md`.

Proposed: all five → `.NET`, `MSBuild` **new**, `build`. The filetypes are
`XML` for the `.props`/`.targets` files and their own name for `.rsp`.
Generic `.props`/`.targets` extensions are not proposed: NuGet packages ship
`<package_id>.props` and `.targets` too, but whether a given one is MSBuild
is not knowable from a generic extension, and they rarely sit in a repo.

Source: <https://learn.microsoft.com/en-us/visualstudio/msbuild/customize-by-directory>

### Central package management: `Directory.Packages.props`

> create a `Directory.Packages.props` file at the root of your repository and
> set the MSBuild property `ManagePackageVersionsCentrally` to `true` …
> define `<PackageVersion />` elements to specify the package IDs and
> versions

This is where the versions are when CPM is on, so the `.csproj` files
reference packages without versions.

Proposed: `.NET`, `NuGet`, `MSBuild`, `dependencies`. Filetype `XML`.

Source: <https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management>

### Lock file: `packages.lock.json`

> NuGet restore will generate a lock file (`packages.lock.json`) at the
> project root directory that lists all the package dependencies.

Microsoft says to check it in for applications, and not for libraries. Its
documented variant is `packages.<project_name>.lock.json`, for several
projects in one directory, which an exact-filename rule cannot match.

Proposed: `.NET`, `NuGet`, `dependencies`. Other ecosystems' lock files
(`package-lock.json`) carry `dependencies` with no lock-specific tag, so none
is added here. `Cargo.lock`, `poetry.lock` and `Gemfile.lock` had no tags at
all when this was written; #74 has since tagged them.

Source: <https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files>
(*Locking dependencies*)

### SDK pin: `global.json`

> The *global.json* file allows you to define which .NET SDK version is used
> when you run .NET CLI commands.

It can also pin MSBuild project SDKs (`msbuild-sdks`) and, from .NET 10,
the test runner. It supports comments.

Proposed: `.NET`, `build`, `config`. Filetype: `JSONC`, since the page
documents comments. **Decision:** `global.json` is a fairly generic name.
No other ecosystem's convention for it was found, but a non-.NET repository
could have one. The precedent is `azure-pipelines.yml`, which is tagged by
name alone.

Source: <https://learn.microsoft.com/en-us/dotnet/core/tools/global-json>

### Local tools: `.config/dotnet-tools.json`

> The *.config/dotnet-tools.json* file … After you check in the manifest file
> to the repository, other developers can … run a single
> `dotnet tool restore` command.

Proposed, as an exact filename: `dotnet-tools.json` → `.NET`, `dependencies`.
The name is specific enough not to need the `.config/` path.

Source: <https://learn.microsoft.com/en-us/dotnet/core/tools/local-tools-how-to-use>

### NuGet package manifest: `.nuspec`

> an XML manifest that contains package metadata. This manifest is used both
> to build the package and to provide information to consumers.

It is not required for SDK-style projects, but it is common in older
repositories.

Proposed: `.nuspec` → filetype `XML`, tags `.NET`, `NuGet`, `build`,
`dependencies`. A nuspec declares the package's dependencies.

Source: <https://learn.microsoft.com/en-us/nuget/reference/nuspec>

### Paket: `paket.dependencies`, `paket.lock`, `paket.references`

Paket is the F# community's alternative to NuGet's client:

> `paket.dependencies`, where you specify your dependencies and their
> versions for your entire codebase … `paket.references`, a file that
> specifies a subset of your dependencies for every project … All three file
> types must be committed to source control.

Proposed: all three → `.NET`, `Paket` **new**, `dependencies`. The
project-specific `<Project>.fsproj.paket.references` form is not
exact-matchable.

Sources: <https://fsprojects.github.io/Paket/learn-how-to-use-paket.html>,
<https://fsprojects.github.io/Paket/dependencies-file.html>,
<https://fsprojects.github.io/Paket/references-files.html>

### Build tools: Cake and NUKE

**Cake:** "By convention this will execute the build script named
`build.cake`". Proposed: `.cake` → filetype `C#` (Cake is a C# DSL), tags
`.NET`, `Cake` **new**, `build`.

**NUKE:** its setup docs (from the repository, because `nuke.build` did not
resolve on 2026-10-30) show:

```
├── .nuke                           # Root directory marker
│   ├── build.schema.json           # Build schema file
│   └── parameters.json             # Default parameters file
├── build
│   ├── _build.csproj               # Build project file
├── build.cmd / build.ps1 / build.sh
```

Proposed: path `.nuke/` → `.NET`, `NUKE` **new**, `build`. `_build.csproj`
already gets the `.csproj` tags. The `build.*` bootstrap scripts are generic
names and are not proposed.

Sources: <https://cakebuild.net/docs/running-builds/runners/dotnet-tool>,
<https://github.com/nuke-build/nuke/blob/develop/docs/01-getting-started/02-setup.md>

### Languages: F#, Visual Basic, Razor, XAML

| Extension | Filetype | Classification | Source |
|---|---|---|---|
| `.fs`, `.fsi`, `.fsx`, `.fsscript` | `F#` | language | F# spec: "Source code files, with extensions .fs, .fsi, .fsx, or .fsscript". Microsoft: "Scripts use the file extension .fsx" |
| `.vb` | `Visual Basic` | language | .NET project SDK overview: "source code files (`*.cs`, `*.vb`, and other language-specific extensions)" |
| `.cshtml`, `.razor` | `Razor` | language (decision) | "Files containing Razor generally have a `.cshtml` file extension. Razor is also found in Razor component files (`.razor`)." |
| `.xaml` | `XAML` | non-language (decision) | "XAML files are XML files that generally have the `.xaml` extension." |
| `.resx` | `XML` | non-language | "XML (.resx) files" |

**Decisions:**
- **`.fs` collision.** `.fs` is also used for GLSL fragment shaders. F# is far
  more common in .NET repositories, and shaders mostly use `.frag` or
  `.glsl`. The proposal is F#, with the ambiguity noted, as #40 does for
  `.m` and `.h`.
- **Razor as a language?** HTML and Vue are in `LANGUAGE_FILETYPES`, and
  Razor is markup with embedded C#, so it is proposed as a language.
- **XAML** is UI markup in XML, so it is proposed as a non-language.

New language filetypes (`F#`, `Visual Basic`, `Razor`) raise the language
count. `get_languages()` is part of the vocabulary that kospex reads.

Sources: <https://fsharp.github.io/fslang-spec/program-structure>,
<https://learn.microsoft.com/en-us/dotnet/fsharp/tools/fsharp-interactive>,
<https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview>,
<https://learn.microsoft.com/en-us/aspnet/core/mvc/views/razor>,
<https://learn.microsoft.com/en-us/dotnet/desktop/wpf/xaml/>,
<https://learn.microsoft.com/en-us/dotnet/core/extensions/resources>

### ASP.NET Core settings: `launchSettings.json`, `appsettings.json`

From *Use multiple environments in ASP.NET Core* (via search summary; the
current en-US page was not fetched): `launchSettings.json` lives in the
project's `Properties` folder and sets the environment for local
development. `appsettings.{Environment}.json` overrides the base
`appsettings.json`.

Proposed: `launchsettings.json` and `appsettings.json` → `.NET`, `config`.
**Decisions:** the environment variants (`appsettings.Development.json`)
cannot be exact-matched, and `appsettings.json` may be named elsewhere.
`launchSettings.json` "shouldn't store secrets", but `appsettings*.json`
often does in practice. That is a kospex policy concern, not a tag.

Source to fetch at implementation: <https://learn.microsoft.com/en-us/aspnet/core/fundamentals/environments>

### Linters and formatters

| Tool | Proposal | Source |
|---|---|---|
| **CSharpier** (formatter, C#) | `config`: `.csharpierrc`, `.csharpierrc.json`, `.csharpierrc.yaml`. `.csharpierrc` is JSON or YAML, so its filetype is its own name. `.csharpierignore` exists according to MegaLinter, but CSharpier's own Configuration page does not name it; check the *Ignoring Code* page | <https://csharpier.com/docs/Configuration> |
| **FSharpLint** (linter, F#) | `config`: `fsharplint.json`. "The linter by default looks for a file named `fsharplint.json` in the current working directory … in the root of your project." | <https://fsprojects.github.io/FSharpLint/how-tos/rule-configuration.html> |
| **Fantomas** (formatter, F#) | **Reject**: its settings live in `.editorconfig`, a shared config file, which CLAUDE.md says must not be tagged with one tool | <https://fsprojects.github.io/fantomas/docs/end-users/Configuration.html> |
| `dotnet format` | **Reject**: reads `.editorconfig`, same reason | — |

### Editor files

| Path | Proposal | Source |
|---|---|---|
| `*.sln.DotSettings` | `JetBrains`, `editor`, `config`. The team-shared layer, meant to be committed. Needs the case-sensitivity fix, since the extension is `.DotSettings` | <https://jetbrains.com/help/rider/Sharing_Configuration_Options.html> |
| `*.sln.DotSettings.user` | Per-user, "should not add it to your VCS". Its extension is `.user`, which is too generic to tag | same |
| `.vs/` | `Visual Studio`, `editor`, `config`. Per-user and almost always gitignored, but a detector tags what is there (detector, not policy) | Microsoft's `.suo` page (VS 2015) says per-user solution options must not go in source control; no current page on `.vs/` was found |
| `*.csproj.user` | Not proposed: the `.user` extension is generic, and there are no compound-suffix extension rules | VS SourceSafe design note (old) |

`.vs/` joins the `editor` set from #20, with the existing `Visual Studio`
brand tag.

## Not proposed

| Candidate | Why |
|---|---|
| Generic `.props`, `.targets` | Not knowable from the extension alone |
| `build.ps1`, `build.sh`, `build.cmd` (Cake/NUKE bootstrap) | Generic names |
| `packages.<project>.lock.json` | Not exact-matchable; matched by pattern since (see *Implemented: part one*) |
| `appsettings.<Environment>.json` | Not exact-matchable; matched by pattern since (see *Implemented: part one*) |
| `.fsproj.paket.references` | Not exact-matchable |
| Fantomas, `dotnet format` | Configured in `.editorconfig` |

## New vocabulary if everything is accepted

- **Tags:** `F#`, `Visual Basic`, `MSBuild`, `Paket`, `Cake`, `NUKE`,
  `CSharpier`, `FSharpLint` (8). `Razor` and `XAML` would be filetypes
  only.
- **Filetypes:** `F#`, `Visual Basic`, `Razor`, `XAML`, `F# Project`,
  `Visual Basic Project`, `csharpierrc`, `Directory.Build.rsp`'s own name.
- **Languages:** `F#`, `Visual Basic`, `Razor`.

All additive, so nothing goes in `DEPRECATED_TAGS`. The two bug fixes add
tags to files that should already have had them.

## Decisions

Taken as proposed in #72, on 2026-11-02:

1. `.fs` is F#, with the GLSL ambiguity noted (part two).
2. Razor is a language and XAML is not (part two).
3. `global.json` is tagged by name, as `azure-pipelines.yml` is.
4. `appsettings.json` and `launchSettings.json` are tagged. Taken first as
   base names only; on 2026-11-02 Peter asked for the documented variants
   too, `appsettings.{ENVIRONMENT}.json` and
   `packages.<project_name>.lock.json`, matched by pattern as
   `pylock.<name>.toml` is.
5. `.vs/` is tagged, as detector-not-policy (part two).
6. The work is split in two: (a) the `Global.asax` fix plus build,
   dependency and config files; (b) languages, linters and editors.

## Checked before implementing (2026-11-02)

- **`.vbproj`.** Microsoft's Visual Basic docs: "You can compile project
  (.vbproj) files at a command prompt by using MSBuild."
- **`launchSettings.json`.** The current en-US *runtime environments* page
  (updated 2026-10-31): "The environment for local development can be set in
  the `Properties\launchSettings.json` file of the project." It "Is only used
  on the local development machine" and "Isn't deployed when the app is
  published."
- **`appsettings.json`.** That page doesn't describe it; *Configuration in
  ASP.NET Core* (updated 2026-10-31) does. The default sources include
  "General app settings file configuration via `appsettings.json`", and
  "Comments in `appsettings.json` and `appsettings.{ENVIRONMENT}.json` files
  are supported". So it reports as `JSONC`, as `global.json` does. The same
  page says "Never store passwords or other sensitive data ... in plain text
  configuration files", which is kospex's concern, not a tag.
- **.NET tools are NuGet packages.** "A .NET tool is a special NuGet package
  that contains a console application." So `dotnet-tools.json` carries
  `NuGet`, which the research table above left out.
- `.csharpierignore` is part two and is still to check.

## Implemented: part one

| File | Tags | Filetype |
|---|---|---|
| `.slnx`, `.slnf` | `.NET, Visual Studio, build` | Visual Studio Solution, JSON |
| `.csproj` | `.NET, C#, NuGet, build, dependencies` (gains `NuGet`) | C# Project (unchanged) |
| `.fsproj` | `.NET, F#, NuGet, build, dependencies` | F# Project |
| `.vbproj` | `.NET, Visual Basic, NuGet, build, dependencies` | Visual Basic Project |
| `Directory.Build.props/.targets/.rsp`, `Directory.Solution.props/.targets` | `.NET, MSBuild, build` | XML; `.rsp` is MSBuild Response File |
| `Directory.Packages.props` | `.NET, MSBuild, NuGet, dependencies` | XML |
| `packages.lock.json`, `packages.<project_name>.lock.json`, `dotnet-tools.json` | `.NET, NuGet, dependencies` | JSON |
| `.nuspec` | `.NET, NuGet, build, dependencies` | XML |
| `global.json` | `.NET, build, config` | JSONC |
| `paket.dependencies`, `paket.lock`, `paket.references` | `.NET, Paket, NuGet, dependencies` | Paket; `paket.lock` is Lock |
| `.cake` | `.NET, Cake, build` | C# |
| `.nuke/` | `.NET, NUKE, build` | — |
| `appsettings.json`, `appsettings.<Environment>.json`, `launchSettings.json` | `.NET, config` | JSONC, JSONC, JSON |
| `Global.asax` | unchanged | ASP.NET Global (was Unknown) |

Three things differ from the proposals above:

- **`NuGet` on the project files.** `.csproj`, `.fsproj` and `.vbproj`
  declare `PackageReference` dependencies, and NuGet is their OSV ecosystem.
  This follows the Ecosystem tags rule from #73, as #91 gave Gradle files
  `Maven`. The research table predates that rule.
- **`NuGet` on Paket's files and `dotnet-tools.json`.** Paket resolves NuGet
  packages, as yarn resolves npm ones, and a .NET tool is a NuGet package.
- **Paket's two extensionless-format files** report as their own `Paket`
  filetype rather than `Unknown`.

**The variants.** Both are documented by name:

- *Configuration in ASP.NET Core*: "`appsettings.{ENVIRONMENT}.json`, where
  the `{ENVIRONMENT}` placeholder is the app's environment (examples:
  `appsettings.Production.json`, `appsettings.Development.json`)". The
  environments page says "the environment can be any string value".
- *NuGet PackageReference in project files* (updated 2026-08-15): "If you
  have multiple projects in the same directory, NuGet supports project
  specific lock file `packages.<project_name>.lock.json`".

They are function rules, `is_appsettings_environment()` and
`is_nuget_project_lock()` in `core.py`. Both allow dots in the middle part,
because .NET project names often have them (`Contoso.Api`), and the
environment can be any string. A custom `NuGetLockFilePath` cannot be
matched. `get_language()` reports the environment files as `JSONC` too, since
the configuration page documents comments in "`appsettings.json` and
`appsettings.{ENVIRONMENT}.json` files".

`Global.asax` is fixed by mapping `global.asax` in `LANGUAGE_BY_BASENAME`
and removing the dead `.global.asax` key.

The vocabulary goes from 160 to 166 tags (`F#`, `Visual Basic`, `MSBuild`,
`Paket`, `Cake`, `NUKE`) and 107 to 111 filetypes. Languages are unchanged
until part two.

Tests are in `tests/test_dotnet_build_dependencies.py`, which had 40 failing
before the rules were added, and 6 more before the variant rules. Fixtures are in `src/tests/dotnetapp/`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://learn.microsoft.com/en-us/visualstudio/msbuild/customize-by-directory> | `Directory.Build.*`, `Directory.Solution.*`, search, case | 2026-10-30 (updated 2026-10-20) |
| <https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management> | `Directory.Packages.props` | 2026-10-30 (updated 2026-03-03) |
| <https://learn.microsoft.com/en-us/dotnet/core/tools/global-json> | `global.json`, comments supported | 2026-10-30 (updated 2026-04-30) |
| <https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files> | `packages.lock.json`; `packages.<project_name>.lock.json` | 2026-10-30, again 2026-11-02 (updated 2026-08-15) |
| <https://learn.microsoft.com/en-us/dotnet/core/tools/local-tools-how-to-use> | `.config/dotnet-tools.json` | 2026-10-30, again 2026-11-02 (updated 2026-04-28) |
| <https://devblogs.microsoft.com/visualstudio/new-simpler-solution-file-format/> | `.slnx`, `.slnf` | 2026-10-30 (post 2025-03-13) |
| <https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview> | `.csproj`/`.fsproj` are XML MSBuild files; `*.vb`, `*.resx` | 2026-10-30 (updated 2026-07-01) |
| <https://learn.microsoft.com/en-us/nuget/reference/nuspec> | `.nuspec` | 2026-10-30, via search summary |
| <https://learn.microsoft.com/en-us/aspnet/core/mvc/views/razor> | `.cshtml`, `.razor` | 2026-10-30 (updated 2026-10-29) |
| <https://learn.microsoft.com/en-us/dotnet/desktop/wpf/xaml/> | `.xaml` is XML | 2026-10-30 (updated 2026-04-14) |
| <https://learn.microsoft.com/en-us/dotnet/core/extensions/resources> | `.resx` is XML | 2026-10-30 (updated 2026-03-26) |
| <https://fsharp.github.io/fslang-spec/program-structure> | F# extensions | 2026-10-30, via search summary |
| <https://learn.microsoft.com/en-us/dotnet/fsharp/tools/fsharp-interactive> | `.fsx` scripts | 2026-10-30, via search summary (non-English locale) |
| <https://fsprojects.github.io/Paket/learn-how-to-use-paket.html> | Paket's three files, committed | 2026-10-30 |
| <https://fsprojects.github.io/Paket/dependencies-file.html>, <https://fsprojects.github.io/Paket/references-files.html> | Paket file details | 2026-10-30, via search summary |
| <https://cakebuild.net/docs/running-builds/runners/dotnet-tool> | `build.cake` convention | 2026-10-30 |
| <https://github.com/nuke-build/nuke/blob/develop/docs/01-getting-started/02-setup.md> | NUKE's `.nuke/` layout | 2026-10-30 |
| <https://csharpier.com/docs/Configuration> | CSharpier config files | 2026-10-30 |
| <https://fsprojects.github.io/FSharpLint/how-tos/rule-configuration.html> | `fsharplint.json` | 2026-10-30 |
| <https://fsprojects.github.io/fantomas/docs/end-users/Configuration.html> | Fantomas uses `.editorconfig` | 2026-10-30, via search summary (v7.0.1 page) |
| <https://jetbrains.com/help/rider/Sharing_Configuration_Options.html> | `.sln.DotSettings`, `.DotSettings.user` | 2026-10-30, via search summary |
| <https://learn.microsoft.com/en-us/aspnet/core/fundamentals/environments> | `Properties\launchSettings.json`, local development only | 2026-11-02 (updated 2026-10-31) |
| <https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/> | `appsettings.json` and its variants; comments supported; no secrets in plain-text config | 2026-11-02 (updated 2026-10-31) |
| <https://learn.microsoft.com/en-us/dotnet/visual-basic/reference/command-line-compiler/building-from-the-command-line> | `.vbproj` is the Visual Basic project file | 2026-11-02 (updated 2021-09-15) |
| <https://learn.microsoft.com/en-us/dotnet/core/tools/global-tools> | "A .NET tool is a special NuGet package" | 2026-11-02 (updated 2025-12-17) |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://www.neteye-blog.com/blog/2025/12/19/the-new-slnx-format-for-dotnet-solution/> | .NET 10 makes `.slnx` the default for `dotnet new sln` | Not confirmed from Microsoft; noted only |
| <https://codewithmukesh.com/blog/slnx-solution-format-dotnet/> | `dotnet sln migrate` needs SDK 9.0.200; Rider supports `.slnx` since 2024.3 | Background only |
| <https://megalinter.io/latest/descriptors/csharp_csharpier/> | `.csharpierignore` exists | To confirm against CSharpier's *Ignoring Code* page |
| <https://khalidabuhakmeh.com/what-is-razor-aspnet> | Razor files use `.cshtml`, `.vbhtml` or `.razor` | `.vbhtml` (VB Razor) not in Microsoft's current page; not proposed |
| <https://learn.microsoft.com/ru-ru/previous-versions/bb165680(v=vs.100)>, <https://msdn.microsoft.com/zh-tw/library/bb165909.aspx> | Old VS docs: `.suo` per-user, not for source control; `.csproj.user` private | Old; supports `.vs/` being per-user |
| <https://learn.microsoft.com/visualstudio/msbuild/walkthrough-using-msbuild> | Search summary (2026-11-02): a Visual Basic project's file would be `BuildApp.vbproj` | Not fetched; the Visual Basic page above confirms `.vbproj` |
