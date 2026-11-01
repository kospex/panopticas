# Extension Rules Ignore Case

Closes [#80](https://github.com/kospex/panopticas/issues/80).

**Status:** implemented.

## Bug

`get_extension_filetype()` lowercases the extension before looking it up.
`get_filename_metatypes()` did not lowercase it before looking up
`METADATA_RULES["extension_rules"]`. So a file with an upper- or mixed-case
extension had a filetype but no tags:

    App.CSPROJ   filetype C# Project              tags []
    App.Sln      filetype Visual Studio Solution  tags []

Found during the .NET research for #72 (see
`changes/2026-10-dotnet-detection.md`). It matters for repositories that
come from Windows, and for Rider's `*.sln.DotSettings` files, whose names are
always mixed case.

## Fix

`get_filename_metatypes()` now lowercases the extension, as
`get_extension_filetype()` does. All 23 `extension_rules` keys were
already lowercase, so no existing rule changes meaning.

## Match modes after the change

| Mode | Case |
|---|---|
| Extension rules | Ignored (this fix) |
| Exact-filename rules | Ignored (unchanged; the filename was already lowercased) |
| Path rules | **Case-sensitive** (unchanged, deliberately) |

#80 suggested pinning all three modes as case-insensitive. Path rules are
kept case-sensitive: git paths are case-sensitive, and the conventions the
path rules describe use exact names. GitHub reads `.github/workflows/`, not
`.GitHub/workflows/`. A test pins this, so a future change to it is deliberate.

## Effect on kospex

Files with upper-case extensions gain the tags their lower-case versions
always had. The change only adds tags, and nothing enters or leaves the
vocabulary. A re-sync picks them up.

## Tests

`tests/test_extension_case.py`:

- An upper-case form of every extension rule gets the same tags as the lower-case one.
- A mixed-case extension (`App.Sln`) is covered.
- Filetype and tags agree.
- Exact-filename rules are confirmed to ignore case, and path rules are pinned as case-sensitive.

Before the fix, 25 tests failed and the two guards passed.
