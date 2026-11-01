"""
Rust packaging files (#74).

Shape is [Language, tool, ecosystem, role]; `crates.io` is the ecosystem.
Sources in changes/2026-11-dependency-manifests.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_tags


@pytest.mark.parametrize("path,tags", [
    ("Cargo.toml", ["Rust", "Cargo", "crates.io", "build", "dependencies"]),
    # Every workspace member has its own manifest.
    ("crates/core/Cargo.toml", ["Rust", "Cargo", "crates.io", "build", "dependencies"]),
    ("Cargo.lock", ["Rust", "Cargo", "crates.io", "dependencies"]),
    # Default build script name, in the package root.
    ("build.rs", ["Rust", "Cargo", "build"]),
    ("crates/sys/build.rs", ["Rust", "Cargo", "build"]),
    # rustup toolchain pin; the extensionless name is the legacy form.
    ("rust-toolchain.toml", ["Rust", "rustup", "config"]),
    ("rust-toolchain", ["Rust", "rustup", "config"]),
])
def test_rust_packaging_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path", [
    ".cargo/config.toml",
    ".cargo/config",          # still read, and wins if both exist
    "crates/core/.cargo/config.toml",
])
def test_cargo_config(path):
    assert get_filename_metatypes(path) == ["Rust", "Cargo", "config"]


@pytest.mark.parametrize("path", [
    # Generic names: only the .cargo/ path makes them Cargo's.
    "config.toml",
    "config",
    "app/config.toml",
    # User-level only, under $CARGO_HOME.
    ".cargo/credentials.toml",
    ".cargo/credentials",
    # Lookalikes.
    "src/build.rs.bak",
    "toolchain.toml",
])
def test_not_tagged(path):
    tags = get_filename_metatypes(path)
    assert not {"Cargo", "rustup", "crates.io"} & set(tags)


def test_ordinary_rust_source_untagged():
    assert get_filename_metatypes("src/main.rs") == []


@pytest.mark.parametrize("path,filetype", [
    ("Cargo.toml", "TOML"),
    ("Cargo.lock", "Lock"),
    ("build.rs", "Rust"),
    ("rust-toolchain.toml", "TOML"),
    ("rust-toolchain", "rust-toolchain"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


def test_new_tags_in_vocabulary():
    assert {"Rust", "Cargo", "crates.io", "rustup"} <= set(get_tags())
