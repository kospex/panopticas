"""
JavaScript package-manager files (#73).

`npm` means the npm ecosystem/registry; the tool, where it is not npm, gets
its own tag (yarn, pnpm, Bun). Sources in
changes/2026-11-js-package-managers.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_tags


@pytest.mark.parametrize("path,tags", [
    # npm
    (".npmrc", ["JavaScript", "npm", "config"]),
    ("npm-shrinkwrap.json", ["JavaScript", "npm", "dependencies"]),
    (".npmignore", ["JavaScript", "npm", "ignore"]),
    ("packages/ui/.npmignore", ["JavaScript", "npm", "ignore"]),
    # Yarn
    (".yarnrc.yml", ["JavaScript", "yarn", "npm", "config"]),
    (".yarnrc", ["JavaScript", "yarn", "npm", "config"]),
    (".pnp.cjs", ["JavaScript", "yarn", "dependencies"]),
    (".pnp.loader.mjs", ["JavaScript", "yarn", "dependencies"]),
    # pnpm
    ("pnpm-workspace.yaml", ["JavaScript", "pnpm", "npm", "config", "dependencies"]),
    (".pnpmfile.cjs", ["JavaScript", "pnpm", "config"]),
    (".pnpmfile.mjs", ["JavaScript", "pnpm", "config"]),
    # Bun
    ("bun.lock", ["JavaScript", "Bun", "npm", "dependencies"]),
    ("bun.lockb", ["JavaScript", "Bun", "npm", "dependencies", "binary"]),
    ("bunfig.toml", ["JavaScript", "Bun", "config"]),
    # Deno: no npm tag (it also resolves from JSR) and no language tag
    ("deno.json", ["Deno", "config"]),
    ("deno.jsonc", ["Deno", "config"]),
    ("deno.lock", ["Deno", "dependencies"]),
])
def test_package_manager_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path", [
    ".yarn/releases/yarn-4.1.0.cjs",
    ".yarn/plugins/@yarnpkg/plugin-workspace-tools.cjs",
    ".yarn/sdks/typescript/lib/tsserver.js",
    ".yarn/patches/lodash-npm-4.17.21.patch",
])
def test_yarn_directory(path):
    assert get_filename_metatypes(path) == ["JavaScript", "yarn"]


def test_yarn_cache_archive_keeps_binary():
    # Zero-Installs commits package zips under .yarn/cache/.
    assert get_filename_metatypes(".yarn/cache/lodash-npm-4.17.21.zip") == \
        ["binary", "JavaScript", "yarn"]


@pytest.mark.parametrize("path", ["package.json", "package-lock.json"])
def test_npm_manifests_gain_javascript(path):
    assert get_filename_metatypes(path) == ["npm", "dependencies", "JavaScript"]


def test_existing_lock_files_unchanged():
    assert get_filename_metatypes("yarn.lock") == ["dependencies", "JavaScript", "yarn", "npm"]
    assert get_filename_metatypes("pnpm-lock.yaml") == ["dependencies", "JavaScript", "pnpm", "npm"]


@pytest.mark.parametrize("path,filetype", [
    (".npmrc", "npmrc"),
    (".npmignore", "npmignore"),
    (".yarnrc", "yarnrc"),
    ("bun.lockb", "Bun Lockfile"),
    ("deno.jsonc", "JSONC"),
    (".yarnrc.yml", "YAML"),
    ("bunfig.toml", "TOML"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


@pytest.mark.parametrize("path", [
    # User-level names are not repository rules. Bun's user config is the
    # dotted .bunfig.toml; only the project's bunfig.toml is a rule.
    ".bunfig.toml",
    # pnpm's global settings and auth live outside the repository.
    "config.yaml",
    "auth.ini",
    # Not package-manager files.
    "yarn.txt",
    "src/yarn/index.js",
])
def test_not_tagged(path):
    tags = get_filename_metatypes(path)
    assert "Bun" not in tags and "yarn" not in tags and "pnpm" not in tags


def test_new_tags_in_vocabulary():
    assert {"Bun", "Deno"} <= set(get_tags())
