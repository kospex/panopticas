# CocoaPods and Carthage Detection

Closes [#42](https://github.com/kospex/panopticas/issues/42).

## Summary

Neither dependency manager's files were recognised. Only `Podfile.lock` had a
filetype, and only through the generic `.lock` extension:

    Podfile             []   'Unknown'
    Podfile.lock        []   'Lock'
    Cartfile            []   'Unknown'
    Cartfile.private    []   'Unknown'
    Cartfile.resolved   []   'Unknown'

An iOS or macOS project using either tool therefore looked like it declared no
dependencies. This completes the Apple-platform dependency managers begun with
Swift Package Manager in #38.

## Changes

Five entries in `METADATA_RULES["exact_filename_rules"]`:

    "podfile":           ["dependencies", "CocoaPods"]
    "podfile.lock":      ["dependencies", "CocoaPods"]
    "cartfile":          ["dependencies", "Carthage"]
    "cartfile.private":  ["dependencies", "Carthage"]
    "cartfile.resolved": ["dependencies", "Carthage"]

Two extensionless entries in `EXT_FILETYPES`:

    "podfile":  "Ruby"
    "cartfile": "Cartfile"

Two entries in `LANGUAGE_BY_BASENAME`, and `Cartfile` added to
`NON_LANGUAGE_FILETYPES`:

    "cartfile.private":  "Cartfile"
    "cartfile.resolved": "Cartfile"

Result:

    Podfile             ['dependencies', 'CocoaPods']   'Ruby'
    Podfile.lock        ['dependencies', 'CocoaPods']   'Lock'
    Cartfile            ['dependencies', 'Carthage']    'Cartfile'
    Cartfile.private    ['dependencies', 'Carthage']    'Cartfile'
    Cartfile.resolved   ['dependencies', 'Carthage']    'Cartfile'

## Sources

| Convention | Source |
|---|---|
| The file is named `Podfile` and describes target dependencies | [The Podfile](https://guides.cocoapods.org/using/the-podfile.html) — "The file should simply be named `Podfile`." |
| `Podfile.lock` records the installed version of each pod and is kept in version control | [Using CocoaPods](https://guides.cocoapods.org/using/using-cocoapods.html) |
| An extensionless `Podfile` is loaded as Ruby | [`podfile.rb` in CocoaPods/Core](https://github.com/CocoaPods/Core/blob/master/lib/cocoapods-core/podfile.rb) — `from_file` sends `''`, `.podfile` and `.rb` to `from_ruby` |
| `Cartfile`, `Cartfile.private`, `Cartfile.resolved` and the OGDL-subset syntax | [Carthage Artifacts](https://github.com/Carthage/Carthage/blob/master/Documentation/Artifacts.md) |

## Background: what Carthage is

Recorded because it explains the tagging choices and took some checking.
Verified on 2026-10-09 against the sources named in each row.

| Fact | Detail | Source |
|---|---|---|
| Apple platforms only | Describes itself as "a simple, decentralized dependency manager for Cocoa" | [Repository description](https://github.com/Carthage/Carthage) |
| Platforms | macOS, iOS, tvOS and watchOS | [README](https://github.com/Carthage/Carthage/blob/master/README.md) |
| visionOS | Supported in code — the SDK list includes visionOS and its simulator — but not mentioned in the README | [`Source/XCDBLD/SDK.swift`](https://github.com/Carthage/Carthage/blob/master/Source/XCDBLD/SDK.swift) |
| Languages | "frameworks written in Swift or Objective-C" | README |
| No central registry | "There is no central list of projects" | README |
| Linux and server-side Swift | Not stated either way. Unsupported by inference only: Carthage builds with Xcode's tools | — |
| Maintenance | Not archived; latest release is 0.40.0, September 2024 | [Releases](https://github.com/Carthage/Carthage/releases) |

**Apple does not document Carthage.** It is a community project. A search of
developer.apple.com finds only forum threads and passing mentions in two WWDC
sessions; the
[WWDC22 Xcode Cloud session](https://developer.apple.com/videos/play/wwdc2022/110375/)
refers to CocoaPods and Carthage as third-party dependency managers needing
custom build scripts. Swift Package Manager is the only dependency manager
Apple documents as its own. There is therefore no Apple source to verify a
Carthage convention against — Carthage's own repository is the authority.

Carthage, CocoaPods and Swift Package Manager all serve the same ecosystem.
Swift Package Manager is the default for new projects, so `Cartfile` and
`Podfile` are most often found in older codebases.

## Design notes

- **No language tag.** Both tools manage dependencies for Swift and
  Objective-C projects alike, so a `Swift` tag would be wrong as often as
  right. `Package.swift` carries `Swift` because the manifest itself is Swift.
- **No `build` tag.** These files declare and pin dependencies; they do not
  describe a build. This matches `package.json` and `uv.lock`.
- **`Podfile` is `Ruby`.** The CocoaPods guides do not name the language, but
  the loader evaluates an extensionless `Podfile` as Ruby. This follows the
  existing `Steepfile` and `.rufo` mappings. A Podfile now counts towards a
  repository's Ruby total.
- **`Cartfile` gets its own filetype.** Carthage documents the syntax as a
  restricted subset of OGDL, which panopticas has no name for, so the file
  takes its own name as the other tool-specific formats do. The Carthage
  documentation does not name a syntax for `Cartfile.resolved`; it is given
  the same filetype as the file it is generated from.
- **`Cartfile.private` and `Cartfile.resolved` are mapped by basename.**
  `.private` and `.resolved` are not mapped as extensions — `Package.resolved`
  is JSON, and `.private` means nothing in general. Tests guard that other
  files with those extensions are not claimed.
- **`Podfile.lock` keeps the `Lock` filetype** it already had from its
  extension, like `uv.lock`.
- `CocoaPods` and `Carthage` are new tags and `Cartfile` a new filetype. All
  additive, so kospex is unaffected until a re-sync.

## Not included

- `*.podspec` and `*.podspec.json`, which describe a library published as a
  pod rather than a project's dependencies.
- CocoaPods' alternative Podfile names (`CocoaPods.podfile`,
  `CocoaPods.podfile.yaml`, `Podfile.rb`). The loader accepts them, but the
  guides document only `Podfile`.
- The `Pods/` and `Carthage/` directories.

## Tests

`tests/test_panopticas.py` covers the filetype and tags for all five files, a
subdirectory path, and guards against look-alike names. Fixtures in
`src/tests/`: `Podfile`, `Podfile.lock`, `Cartfile`, `Cartfile.private` and
`Cartfile.resolved`.
