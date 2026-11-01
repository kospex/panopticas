"""
Ruby packaging files (#74).

Shape is [Language, tool, ecosystem, role]; `RubyGems` is the ecosystem,
and also the tool for *.gemspec, so it appears once there. Sources in
changes/2026-11-dependency-manifests.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_tags


@pytest.mark.parametrize("path,tags", [
    # Bundler, and its opt-in alternative names
    ("Gemfile", ["Ruby", "Bundler", "RubyGems", "dependencies"]),
    ("Gemfile.lock", ["Ruby", "Bundler", "RubyGems", "dependencies"]),
    ("gems.rb", ["Ruby", "Bundler", "RubyGems", "dependencies"]),
    ("gems.locked", ["Ruby", "Bundler", "RubyGems", "dependencies"]),
    ("engines/billing/Gemfile", ["Ruby", "Bundler", "RubyGems", "dependencies"]),
    # Gem metadata; Rails keeps one per sub-gem directory.
    ("mygem.gemspec", ["Ruby", "RubyGems", "dependencies"]),
    ("activerecord/activerecord.gemspec", ["Ruby", "RubyGems", "dependencies"]),
    # Rake's four accepted names
    ("Rakefile", ["Ruby", "Rake", "build"]),
    ("rakefile", ["Ruby", "Rake", "build"]),
    ("Rakefile.rb", ["Ruby", "Rake", "build"]),
    ("rakefile.rb", ["Ruby", "Rake", "build"]),
    # Imported task files
    ("rakelib/release.rake", ["Ruby", "Rake", "build"]),
    ("lib/tasks/db.rake", ["Ruby", "Rake", "build"]),
    # Cross-tool version pin, like .python-version
    (".ruby-version", ["Ruby", "dependencies"]),
])
def test_ruby_packaging_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path", [
    ".bundle/config",
    "app/.bundle/config",
])
def test_bundle_config(path):
    # Machine-local Bundler settings. Usually gitignored, but tagged when
    # present: whether it belongs in the repository is the consumer's call.
    assert get_filename_metatypes(path) == ["Ruby", "Bundler", "config"]


@pytest.mark.parametrize("path", [
    "config",
    "config/application.rb",
    # Lookalikes
    "Gemfile.bak",
    "gems.txt",
    "make.rb",
    "rakefile.txt",
    "src/rake.rb",
])
def test_not_tagged(path):
    tags = get_filename_metatypes(path)
    assert not {"Bundler", "RubyGems", "Rake"} & set(tags)


def test_ordinary_ruby_source_untagged():
    assert get_filename_metatypes("lib/app.rb") == []


@pytest.mark.parametrize("path,filetype", [
    # Ruby DSL files count as Ruby, like Podfile.
    ("Gemfile", "Ruby"),
    ("gems.rb", "Ruby"),
    ("mygem.gemspec", "Ruby"),
    ("Rakefile", "Ruby"),
    ("rakefile", "Ruby"),
    ("lib/tasks/db.rake", "Ruby"),
    ("Gemfile.lock", "Lock"),
    ("gems.locked", "Lock"),
    (".ruby-version", "ruby-version"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


def test_new_tags_in_vocabulary():
    assert {"Bundler", "RubyGems", "Rake"} <= set(get_tags())
