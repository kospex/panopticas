# Disambiguating `.m` and `.h` — Design

**Date:** 2026-10-09
**Status:** Proposed. Analysis only — nothing is implemented and no approach
has been agreed. Tracked in
[#40](https://github.com/kospex/panopticas/issues/40).

## Problem

Two extensions are shared by more than one language, and panopticas resolves
each with a single fixed answer:

| Extension | Reported today | Actually used by |
|---|---|---|
| `.m` | `Objective-C` | Objective-C, MATLAB/Octave, Mathematica |
| `.h` | `C Header` | C, C++ and Objective-C headers |

So a MATLAB repository is reported as Objective-C, and Objective-C and C++
headers are never counted towards their language. Neither can be fixed with
another extension mapping: the path alone does not carry the answer.

This came out of the 0.0.21 work on Kotlin, Swift and Objective-C detection
(#36, #38), where both cases were recorded as out of scope.

## What can be determined, and how

There are three sources of evidence. They differ in reliability and in how
well they fit the current code.

### 1. The file's own path

One rule is fully path-based and fits the existing model:

- A `.m` file inside a `+package/` or `@ClassName/` directory is MATLAB. Those
  directory names are MATLAB's package and class-folder conventions and are
  not used by Objective-C.

A second is a filename convention rather than a guarantee:

- A header named `*-Bridging-Header.h` is an Objective-C header exposed to
  Swift. Xcode generates that name, but it is configurable.

### 2. The file's content

The languages sharing `.m` look nothing alike, so the first few hundred bytes
settle almost every file.

| File | Objective-C markers | Other-language markers |
|---|---|---|
| `.m` | `#import`, `@interface`, `@implementation`, `@end`, `//` and `/* */` comments | MATLAB: `%` comments, `function … = name(…)`, `classdef` |
| `.h` | `#import`, `@interface`, `@protocol`, `@class`, `@property`, `NS_ASSUME_NONNULL_BEGIN` | C++: `namespace`, `template`, `class`, `std::` |

Reliability:

- **`.m`: high.** Empty and near-empty files stay ambiguous, so the sniffer
  must be able to return "no answer" and fall back to today's result.
- **`.h`, "this is Objective-C": high.** The `@` directives are distinctive.
- **`.h`, "this is C, not C++": not achievable.** No marker proves a header is
  C only, and many headers are deliberately written to be valid in two or all
  three languages (`#ifdef __cplusplus`, `#ifdef __OBJC__`). Content can
  upgrade a header to Objective-C or C++; it cannot confirm plain C.

GitHub Linguist resolves both extensions with content regexes of this kind,
and treats `.m` as a wider collision than two languages. It is the closest
available benchmark and its heuristics are the obvious starting point.

### 3. Other files in the repository

These are hints rather than proof. A mixed repository — MATLAB analysis
scripts beside an iOS app — defeats every repo-wide indicator, which is why
they suit *triggering* a content check better than *deciding* the answer.

**That a `.h` is Objective-C**

| Strength | Indicator |
|---|---|
| Strong, per file | A `Foo.m` or `Foo.mm` beside `Foo.h` |
| Strong, per file | Filename ends `-Bridging-Header.h`; a `-Prefix.pch` in the same target |
| Strong, repo | `project.pbxproj` (inside `.xcodeproj/`), `.xcworkspacedata`, `.xcscheme`, `.xcconfig` |
| Strong, repo | `.xib`, `.storyboard`, `.entitlements`, `.xcassets/` directories, `.podspec` |
| Medium, repo | `Podfile`, `Cartfile`, `Package.swift`, `.swift` files, `.modulemap`, `.lproj/` directories |
| Weak | `Info.plist` and `.strings` (both used outside Apple projects), `fastlane/` (also Android) |

GNUstep projects are Objective-C with no Xcode files at all; a `GNUmakefile`
is the usual sign.

**That a `.m` is MATLAB**

| Strength | Indicator |
|---|---|
| Strong, per file | The file is in a `+package/` or `@ClassName/` directory |
| Strong, repo | `.mlx`, `.slx`, `.mdl`, `.mlapp`, `.mltbx`, `.mat`, `.fig` |
| Strong, repo | Compiled MEX binaries (`.mexw64`, `.mexa64`, `.mexmaci64`), a `resources/project/` directory |
| Medium, repo | `startup.m`, `Contents.m`, `pathdef.m`, `buildfile.m`, `functionSignatures.json`, `.octaverc` |
| Weak | `.prj` (also a GIS format), `.p` (also Pascal), a `private/` directory |

**That a `.m` is Mathematica:** `.nb`, `.wl` or `.wls` files, or a
`PacletInfo.m`.

**That a `.h` is C++:** a `Foo.cpp`, `Foo.cc` or `Foo.cxx` beside `Foo.h`.
This is the one place a sibling check adds something content sniffing cannot
always settle.

> **These lists are unverified.** They were written from general knowledge
> during the analysis, not checked against each vendor's documentation. The
> project rule — verify a convention against current official docs before
> adding it — applies to every row before any of it becomes a mapping.

## How this fits the current code

- **Content reads have a precedent.** `get_language()` already opens a file to
  read its shebang (`check_shebang()` in `core.py`). The "never open a file"
  rule covers AI and linter metadata, not language detection.
- **But the shebang read only happens when the extension lookup fails.** A
  `.m` or `.h` file is resolved by `EXT_FILETYPES` and returns before any file
  is opened. Sniffing these would be the first case of content overriding a
  successful extension match.
- **Repository context has no precedent.** Every function takes one path.
  Sibling and repo-wide hints need an input panopticas does not have.
- **The answer would depend on how the question is asked.** A caller passing
  `skip_shebang=True`, or a path that is not on disk, can only get the
  extension answer. The same file could report two languages.
- **Almost none of the indicator files are recognised.** Of every extension
  listed above, only `.cpp`, `.swift` and `.mm` are in `EXT_FILETYPES`, plus
  the `Package.swift` tags. `.cc`, `.cxx` and `.hpp` report `Unknown`, which
  is a gap in its own right.

## Proposed split between panopticas and kospex

kospex has the full file list for a repository; panopticas sees one path at a
time. That suggests:

- **panopticas** maps the indicator files to filetypes or tags, and exposes a
  sniffer that takes a single file and returns a language or nothing.
- **kospex** decides when to call the sniffer, using the repository's file
  list — for example only when a strong indicator is present.

This keeps panopticas a detector and leaves the "should we look closer"
decision with the consumer that has the context to make it.

The trigger matters unevenly. Reading a few hundred bytes is cheap, so every
`.m` could simply be sniffed, with indicators used only when the content is
inconclusive. The trigger earns its keep on `.h`, where a C codebase can hold
thousands of headers that never need opening.

## Suggested direction

Not agreed — recorded as the starting position for the next session.

1. Add the `+package/` and `@ClassName/` path rule for MATLAB. It is
   path-only and needs no new machinery.
2. Add a content sniffer for `.m` that returns Objective-C, MATLAB,
   Mathematica or nothing.
3. For `.h`, upgrade to Objective-C or C++ only when a marker is found, and
   leave everything else as `C Header`.
4. Map the strong indicator files so kospex can see them.
5. Do not build repo-wide inference into panopticas.

## Open questions

- **API shape.** A new function (`sniff_language(path)`), or a flag on
  `get_language()`? A separate function keeps `get_language()` deterministic
  for a given path, which avoids the two-answers problem above.
- **What does kospex call today, and with what?** If it resolves language from
  paths in git history rather than files on disk, a content sniffer cannot run
  there at all. This needs checking in kospex before designing the API.
- **New names.** `MATLAB` and `Mathematica` would be new languages. Is an
  Objective-C header reported as `Objective-C`, or as a new
  `Objective-C Header` to parallel `C Header`? Same question for C++.
- **Relabelling.** MATLAB files already stored in kospex as `Objective-C`
  would change on re-sync. That is a correction, but it is a rename of
  existing data rather than an addition, which is the case the project treats
  as unsafe. It needs a deliberate decision and a changelog note.
- **Octave.** Report it as `MATLAB`, or separately? The two are not
  distinguishable from most files.
- **How much to read.** A fixed byte budget, and what to do with files whose
  first bytes are a licence header and nothing else.
- **Which indicator rows survive verification.** See the note above.

## Out of scope

- CocoaPods and Carthage dependency tags (`Podfile`, `Cartfile` and their lock
  files). They appear here only as indicators.
- Linter rules for SwiftLint, SwiftFormat, detekt and clang-format.
