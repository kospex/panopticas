# setup.py / setup.cfg Detection

Closes [#21](https://github.com/kospex/panopticas/issues/21).

## Summary

`setup.py` and `setup.cfg` declare dependencies via `install_requires`, but
neither was recognised. Both returned no metatypes at all:

    setup.py           []                                        'Python'
    setup.cfg          []                                        'Unknown'
    pyproject.toml     ['build', 'dependencies', 'Python']       'TOML'
    requirements.txt   ['pip', 'Python', 'PyPi', 'dependencies'] 'Text'

A Python project using setuptools without a `pyproject.toml` therefore looked
like it declared no dependencies. Anything consuming the `dependencies`
metatype to build a dependency-file inventory skipped those repos silently,
with no way to distinguish "no manifest" from "manifest not recognised".

## Changes

Two entries in `METADATA_RULES["exact_filename_rules"]`:

    "setup.py":  ["build", "dependencies", "Python", "setuptools"]
    "setup.cfg": ["build", "dependencies", "Python", "setuptools"]

One entry in `LANGUAGE_BY_BASENAME`:

    "setup.cfg": "INI"

## Why `setuptools` is tagged here but not on pyproject.toml

Tool-specific manifests already carry their tool: `uv.lock` has `uv`,
`pnpm-lock.yaml` has `pnpm`, `packages.config` has `NuGet`. `setup.py` and
`setup.cfg` are setuptools-specific by definition, so the tag is accurate.

`pyproject.toml` deliberately carries no backend tag. Its backend is declared
*inside* the file:

```toml
[build-system]
build-backend = "setuptools.build_meta"   # or hatchling.build, flit_core.buildapi,
                                          # poetry.core.masonry.api, pdm.backend
```

`get_filename_metatypes()` is pure path inspection and never opens the file, so
a pyproject's backend is not knowable from the path. `setup.py` and `setup.cfg`
are the only Python packaging filenames where it is.

The `setuptools` tag is a factual backend identifier. It is **not** a
maintenance or age signal — setuptools is actively maintained and remains the
most widely used backend, including for many modern `pyproject.toml` projects.

## Why setup.cfg is mapped by basename, not by extension

`setup.cfg` is INI — `configparser` reads it. But `.cfg` as an extension is used
for arbitrary formats across other ecosystems, so a blanket `.cfg -> INI` entry
in `EXT_FILETYPES` would assert something panopticas cannot know from a path,
and would change the reported language of every `.cfg` file in every scanned
repo.

`LANGUAGE_BY_BASENAME` is consulted before the extension table in
`get_language()`, so the basename entry resolves `setup.cfg` precisely while
leaving `.cfg` unclaimed. A regression test asserts `tox.cfg` and `app.cfg`
still return `None`.

`setup.py` needs no language entry — it already resolves to Python via `.py`.

## Tests

Six tests added to `tests/test_panopticas.py` (242 passing):

- `TestGetFilenameMetatypes` — `setup.py`, `setup.cfg`, and `setup.py` nested in
  a subdirectory.
- `TestGetLanguageEdgeCases` — `setup.cfg` bare and in a path, plus
  `test_other_cfg_files_are_not_claimed` guarding that `.cfg` stays unclaimed.

## Downstream

kospex consumes the `dependencies` metatype via `get_dependency_files()`, which
selects on `tech_type LIKE '%|dependencies|%'`. This change makes `setup.py` and
`setup.cfg` visible to that inventory. Kospex parsing those files into
`dependency_data` is separate work — see
[kospex#137](https://github.com/kospex/kospex/issues/137).
