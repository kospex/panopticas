# The 0.0.22 wheel shipped a `tests` package

Issue: [#95](https://github.com/kospex/panopticas/issues/95)

## What happened

The 0.0.22 wheel contains `tests/typedpkg/__init__.pyi` and `tests/typedpkg/py.typed`, and its `top_level.txt` lists `tests` next to `panopticas`. Installing it created `site-packages/tests/typedpkg/`. The 0.0.20 and 0.0.21 wheels have no `tests/` entries.

## Why

`pyproject.toml` had no package configuration, so setuptools used its automatic discovery. For a `src/` layout that finds every directory under `src/` as a package, including namespace packages, so `src/tests/` (fixture files only) was always a candidate. Nothing from it was packaged until #87 added `src/tests/typedpkg/` as a fixture for the `py.typed` and `.pyi` detection, because setuptools includes `py.typed` and `.pyi` files automatically.

## Fix

```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["panopticas*"]
```

Discovery now finds only `panopticas`. The fixture stays where it is. A `.py` fixture added under `src/tests/` later is also kept out of the wheel.

## Checking a wheel

```bash
unzip -p dist/panopticas-*.whl '*.dist-info/top_level.txt'   # must print only: panopticas
unzip -l dist/panopticas-*.whl | grep -c '^ .*tests/'        # must be 0
```
