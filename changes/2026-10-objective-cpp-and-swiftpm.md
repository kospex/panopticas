# Objective-C++ and Swift Package Manager Detection

Closes [#38](https://github.com/kospex/panopticas/issues/38).

## Summary

`.mm` was not in `EXT_FILETYPES`, and neither Swift Package Manager file was
recognised as a dependency file:

    file.mm            []                                           'Unknown'
    Package.swift      []                                           'Swift'
    Package.resolved   []                                           'Unknown'

A Swift package therefore looked like it declared no dependencies, the same gap
`build.gradle.kts` had for the Gradle Kotlin DSL.

## Changes

One entry in `EXT_FILETYPES`, and `Objective-C++` added to
`LANGUAGE_FILETYPES`:

    ".mm": "Objective-C++"

Two entries in `METADATA_RULES["exact_filename_rules"]`:

    "package.swift":    ["build", "dependencies", "Swift", "SwiftPM"]
    "package.resolved": ["dependencies", "Swift", "SwiftPM"]

One entry in `LANGUAGE_BY_BASENAME`:

    "package.resolved": "JSON"

Result:

    file.mm            []                                           'Objective-C++'
    Package.swift      ['build', 'dependencies', 'Swift', 'SwiftPM'] 'Swift'
    Package.resolved   ['dependencies', 'Swift', 'SwiftPM']          'JSON'

## Design notes

- **`Package.resolved` is mapped by basename, not by extension.** It is JSON,
  but Carthage's `Cartfile.resolved` shares the `.resolved` extension and is
  plain text. A blanket `".resolved" -> JSON` rule would mislabel it.
- **The lock file does not carry `build`.** It pins dependency versions; it
  does not describe how to build. This matches `uv.lock` and `pnpm-lock.yaml`.
- **Detection is by filename, so location does not matter.** In an Xcode app
  project `Package.resolved` lives inside the project bundle, under
  `.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/`, and is tagged there
  too.
- **`SwiftPM` is the tool's own short name**, not a panopticas convention.
  The official documentation is titled
  [Package Manager (SwiftPM)](https://docs.swift.org/latest/documentation/packagemanagerdocs/)
  — set as the display name in
  [`Documentation.md`](https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/Documentation.md)
  — and the project README refers to "SwiftPM's bug tracker".
- **`Swift` and `SwiftPM` are new tags** and `Objective-C++` a new language
  name. `Swift` existed as a language but had never been used as a tag. All
  are additions, so kospex is unaffected until a re-sync.

## Not included

- `.h` still always reports `C Header` and `.m` always `Objective-C`. Neither
  an Objective-C header nor a MATLAB `.m` file can be told apart from the path,
  and detection is path-based only.
- CocoaPods (`Podfile`, `Podfile.lock`) and Carthage (`Cartfile`,
  `Cartfile.resolved`) files are still untagged.

## Tests

`tests/test_panopticas.py` covers the extension, the basename filetype, the
tags for both files, the lock file inside an Xcode project path, and guards
that `Cartfile.resolved` and ordinary `.swift` files are not claimed. Fixtures
in `src/tests/`: `file.mm`, `Package.swift` and `Package.resolved`.
