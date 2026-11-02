"""
PHP, Elixir and Dart packaging files (#74).

Shape is [Language, tool, ecosystem, role]. The ecosystems are Packagist,
Hex and Pub, as OSV names them. Dart's tool is `pub`, which differs from
`Pub` only in case, so Dart files carry `Pub` alone. Sources in
changes/2026-11-dependency-manifests.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_languages, get_tags


@pytest.mark.parametrize("path,tags", [
    # PHP / Composer
    ("composer.json", ["PHP", "Composer", "Packagist", "dependencies"]),
    ("composer.lock", ["PHP", "Composer", "Packagist", "dependencies"]),
    # Elixir / Mix; umbrella projects have apps/*/mix.exs
    ("mix.exs", ["Elixir", "Mix", "Hex", "build", "dependencies"]),
    ("apps/web/mix.exs", ["Elixir", "Mix", "Hex", "build", "dependencies"]),
    ("mix.lock", ["Elixir", "Mix", "Hex", "dependencies"]),
    # Dart / pub
    ("pubspec.yaml", ["Dart", "Pub", "dependencies"]),
    ("packages/core/pubspec.yaml", ["Dart", "Pub", "dependencies"]),
    ("pubspec.lock", ["Dart", "Pub", "dependencies"]),
    ("pubspec_overrides.yaml", ["Dart", "Pub", "dependencies", "config"]),
])
def test_packaging_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path,tags", [
    # Read by `mix format`; nested copies are normal.
    (".formatter.exs", ["Elixir", "formatter", "mix format", "config"]),
    ("apps/web/.formatter.exs", ["Elixir", "formatter", "mix format", "config"]),
    # The analyzer reports type errors as well as lints.
    ("analysis_options.yaml",
     ["Dart", "linter", "typechecker", "Dart analyzer", "config"]),
])
def test_linter_configs(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path,filetype", [
    ("lib/app.ex", "Elixir"),
    ("test/app_test.exs", "Elixir"),
    ("mix.exs", "Elixir"),
    (".formatter.exs", "Elixir"),
    ("mix.lock", "Lock"),
    ("lib/main.dart", "Dart"),
    ("pubspec.yaml", "YAML"),
    ("pubspec.lock", "Lock"),
    ("analysis_options.yaml", "YAML"),
    ("composer.json", "JSON"),
    ("composer.lock", "Lock"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


def test_elixir_and_dart_are_languages():
    assert {"Elixir", "Dart"} <= set(get_languages())


@pytest.mark.parametrize("path", [
    "lib/app.ex",
    "lib/main.dart",
    "src/index.php",
])
def test_ordinary_source_untagged(path):
    assert get_filename_metatypes(path) == []


@pytest.mark.parametrize("path", [
    # Composer's credentials file, but the name is generic.
    "auth.json",
    # Lookalikes
    "composer.json.dist",
    "mix.txt",
    "pubspec.yml",
    "my_analysis_options.yaml",
])
def test_not_tagged(path):
    tags = get_filename_metatypes(path)
    assert not {"Composer", "Packagist", "Mix", "Hex", "Pub",
                "mix format", "Dart analyzer"} & set(tags)


def test_dart_has_no_lowercase_pub_tag():
    # `pub` and `Pub` would be one tag under SQLite's case-insensitive LIKE.
    assert "pub" not in get_tags()


def test_new_tags_in_vocabulary():
    assert {"PHP", "Composer", "Packagist", "Elixir", "Mix", "Hex",
            "Dart", "Pub", "mix format", "Dart analyzer"} <= set(get_tags())
