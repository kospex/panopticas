"""
Gradle files (#91).

Gradle resolves Maven coordinates (group:name:version), from Maven Central
by default, so files that declare or lock dependencies carry the OSV
ecosystem `Maven` alongside the `gradle` tool tag. Sources in
changes/2026-11-gradle-ecosystem.md.
"""

import pytest

import panopticas
from panopticas import get_filename_metatypes, get_language, is_gradle_script

GRADLE_SCRIPT_TAGS = ["gradle", "build", "dependencies", "Maven"]


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
def test_settings_declare_dependencies(path):
    # Reverses #91's decision 2: a settings file's plugins { } block and
    # buildscript classpath declare dependencies. See
    # changes/2026-11-gradle-scripts.md.
    assert get_filename_metatypes(path) == GRADLE_SCRIPT_TAGS


@pytest.mark.parametrize("path", [
    # A build file renamed with ProjectDescriptor.buildFileName.
    "firebase-ai/firebase-ai.gradle.kts",
    "apk-size.gradle",
    # Script plugins, applied with apply from:.
    "gradle/dependencies.gradle",
    "errorProne.gradle",
    # Precompiled script plugins; the suffix sets the plugin's scope.
    "buildSrc/src/main/groovy/code-quality.gradle",
    "build-logic/src/main/kotlin/java-library-conventions.gradle.kts",
    "build-logic/src/main/kotlin/my-settings.settings.gradle.kts",
    # Init scripts, when committed and passed with -I.
    "gradle/init.gradle",
    "ci/dependency-fetcher.init.gradle.kts",
    # Extensions are matched case-insensitively, as extension_rules are.
    "Versions.GRADLE",
    "Conventions.Gradle.Kts",
])
def test_any_gradle_script(path):
    assert get_filename_metatypes(path) == GRADLE_SCRIPT_TAGS


@pytest.mark.parametrize("filename,expected", [
    ("build.gradle", True),
    ("build.gradle.kts", True),
    ("settings.gradle", True),
    ("settings.gradle.kts", True),
    ("dependencies.gradle", True),
    ("java-library-conventions.gradle.kts", True),
    ("code-quality.init.gradle", True),
    ("BUILD.GRADLE", True),
    # Gradle's project cache directory, never a script.
    (".gradle", False),
    (".gradle.kts", False),
    # Gradle files that aren't scripts: they keep their own rules.
    ("gradle.properties", False),
    ("gradle.lockfile", False),
    ("gradlew", False),
    ("gradlew.bat", False),
    ("gradle-wrapper.jar", False),
    ("libs.versions.toml", False),
    # Plain Kotlin scripts aren't Gradle's.
    ("script.kts", False),
    ("main.kts", False),
    # Lookalikes
    ("build.gradle.bak", False),
    ("build.gradle.kts.orig", False),
    ("gradle", False),
    ("gradle.kts", False),
    ("", False),
])
def test_is_gradle_script(filename, expected):
    assert is_gradle_script(filename) is expected


def test_is_gradle_script_is_exported():
    # kospex resolves predicates by name from the top-level package.
    assert "is_gradle_script" in panopticas.__all__
    assert panopticas.is_gradle_script is is_gradle_script


@pytest.mark.parametrize("path", ["script.kts", "scripts/release.main.kts"])
def test_plain_kotlin_scripts_not_gradle(path):
    assert "gradle" not in get_filename_metatypes(path)


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
    "build.gradle.bak",
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
