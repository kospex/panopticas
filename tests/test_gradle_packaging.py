"""
Gradle files (#91).

Gradle resolves Maven coordinates (group:name:version), from Maven Central
by default, so files that declare or lock dependencies carry the OSV
ecosystem `Maven` alongside the `gradle` tool tag. Sources in
changes/2026-11-gradle-ecosystem.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language


@pytest.mark.parametrize("path,tags", [
    # Build scripts declare dependencies.
    ("build.gradle", ["gradle", "build", "dependencies", "Maven"]),
    ("build.gradle.kts", ["gradle", "build", "dependencies", "Maven"]),
    ("app/build.gradle.kts", ["gradle", "build", "dependencies", "Maven"]),
    # The version catalog Gradle imports automatically.
    ("gradle/libs.versions.toml", ["gradle", "dependencies", "Maven"]),
    # Dependency locking: one per project, plus the buildscript's.
    ("gradle.lockfile", ["gradle", "dependencies", "Maven"]),
    ("app/gradle.lockfile", ["gradle", "dependencies", "Maven"]),
    ("buildscript-gradle.lockfile", ["gradle", "dependencies", "Maven"]),
    # Build settings. The user-level copy is under ~/.gradle, outside any
    # repository.
    ("gradle.properties", ["gradle", "build", "config"]),
    # The Wrapper, which pins Gradle's own version.
    ("gradlew", ["gradle", "build"]),
    ("gradlew.bat", ["gradle", "build"]),
    ("gradle/wrapper/gradle-wrapper.properties", ["gradle", "build", "config"]),
    ("gradle/wrapper/gradle-wrapper.jar", ["binary", "gradle", "build"]),
])
def test_gradle_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path", ["settings.gradle", "settings.gradle.kts"])
def test_settings_get_no_ecosystem(path):
    # Settings declare the build and its repositories, not dependencies.
    assert get_filename_metatypes(path) == ["gradle", "build"]


def test_maven_unchanged():
    assert get_filename_metatypes("pom.xml") == ["Maven", "build", "dependencies"]


@pytest.mark.parametrize("path", [
    # Other catalogs can have any name, and must be declared explicitly.
    "gradle/other.versions.toml",
    "versions.toml",
    # Lookalikes
    "my-gradle.lockfile",
    "gradle.lockfile.bak",
    "gradlew.sh",
    "properties.gradle",
])
def test_not_tagged(path):
    assert "Maven" not in get_filename_metatypes(path)


@pytest.mark.parametrize("path,filetype", [
    ("gradle/libs.versions.toml", "TOML"),
    ("gradle.lockfile", "Lock"),
    ("buildscript-gradle.lockfile", "Lock"),
    ("gradle.properties", "Properties"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype
