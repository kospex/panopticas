# Duplicate Tags from `get_filename_metatypes()`

Closes [#55](https://github.com/kospex/panopticas/issues/55).

## Summary

`get_filename_metatypes()` concatenates the tags of every rule that matches a
path, and did not de-duplicate. A tag that two rules both contributed came back
twice:

    tsconfig.json                     ['TypeScript', 'JavaScript', 'typechecker', 'TypeScript', 'config']
    .github/dependabot.yml            ['Dependabot', 'GitHub', 'dependencies', 'security', 'GitHub', 'Git']
    config/checkstyle/checkstyle.xml  ['Java', 'linter', 'Checkstyle', 'config', 'Java', 'linter', 'Checkstyle', 'config']

## Change

One line at the end of `get_filename_metatypes()`:

    return list(dict.fromkeys(tags))

This keeps the first occurrence of each tag, so the order is otherwise
unchanged. No rule changed.

## Mechanisms

The issue lists three. Two of them hold:

1. **A file's own rule and its directory's rule overlap.** `dependabot.yml`
   gives `GitHub`, and the `.github` path rule gives `GitHub` again. The same
   happens with a tool's languages and its name: `tsconfig.json` is tagged
   `TypeScript` as a language, and again because TypeScript is the tool.
2. **An exact-filename rule and a path rule carry the same tags.** This is the
   `config/checkstyle/` case.

The third does not hold. The issue suggested that nested path rules
(`.github` and `.github/workflows`) both match, but the path-rule loop stops
at the first match, longest fragment first. Only one path rule ever applies.
The `pipeline` duplicate on `.github/workflows/azure-pipelines.yml` comes from
mechanism 1: the filename rule and the workflows rule both contribute
`pipeline`.

The sweep test also found a fourth mechanism, which the issue's probe did not
report: **an AI artifact's `kind` repeating a tag from another rule.** A linter
config inside an AI directory, such as `.amazonq/.biome.json`, gets `config`
from the linter rule and `config` again as its AI kind. Across all
combinations of rule filenames and rule directories, 1,720 paths returned a
duplicate before the fix.

## Compatibility

- **Tag positions.** For an AI artifact whose `kind` was already present, the
  AI triple is no longer the last three tags. Nothing reads it by position:
  `get_ai_metadata()` is the API for AI metadata, the CLI only displays the
  list, and kospex queries tags with `LIKE '%|tag|%'`.
- **Stored kospex rows.** Rows synced before this release keep their
  duplicates until the repository is re-synced. The version bump triggers that
  re-sync through `last_panopticas_version`.
- **Vocabulary.** `get_tags()` already returned a set, so it is unchanged.

## Tests

`tests/test_duplicate_tags.py` contains:

- exact, order-sensitive assertions for every path in the issue, plus the
  issue's control cases;
- a sweep that runs every rule filename (exact names, extensions, AI suffixes)
  under every rule directory, and asserts that no path returns a duplicate.
  The sweep catches a duplicate that any future rule introduces.

Most existing tests compare tags as sets, which is why this went unnoticed.

New fixtures in `src/tests/`: `tsconfig.json`, `jsconfig.json`,
`.github/dependabot.yml`, `.github/CODEOWNERS`,
`config/checkstyle/checkstyle.xml` and `sorbet/.rubocop.yml`. GitHub reads
Dependabot and CODEOWNERS files only at the repository root, so the copies
under `src/tests/.github/` have no effect on the repository.
