"""
Tests for Scala, sbt and Mill detection.

Covers the Scala source extensions, the sbt and Mill build tags, the version
and options dotfiles, and negative guards for the candidates that were
considered and not proposed. The linter and formatter side (Scalafmt,
Scalafix, Scalastyle) lives in test_linter_detection.py.

See changes/2026-10-scala-build-and-linter-detection.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language, get_languages


def tags_for(path):
    """Tags as a set — rule order is not part of the contract."""
    return set(get_filename_metatypes(path))


class TestScalaSourceExtensions:

    @pytest.mark.parametrize("filename", [
        "build.sbt",
        "project/plugins.sbt",
        "script.sc",
        "build.sc",
        "build.mill",
        "foo/package.mill",
    ])
    def test_resolves_to_scala(self, filename):
        assert get_language(filename, skip_shebang=True) == "Scala"

    def test_scala_is_still_a_language(self):
        assert "Scala" in get_languages()

    def test_mill_yaml_build_is_yaml(self):
        # splitext gives ".yaml", so no new entry is needed.
        assert get_language("build.mill.yaml", skip_shebang=True) == "YAML"


class TestSbtBuildTags:

    @pytest.mark.parametrize("path", [
        "build.sbt",
        "project/plugins.sbt",
        "project/assembly.sbt",   # sbt's own plugin example name
        "modules/core/build.sbt",
    ])
    def test_any_sbt_file_is_a_build_definition(self, path):
        assert tags_for(path) == {"sbt", "build", "dependencies", "Scala"}

    def test_build_sbt_tags_are_not_duplicated(self):
        tags = get_filename_metatypes("build.sbt")
        assert len(tags) == len(set(tags))

    @pytest.mark.parametrize("filename", [".sbtopts", ".jvmopts"])
    def test_launcher_options_files(self, filename):
        assert tags_for(filename) == {"sbt", "build"}

    def test_jvmopts_is_not_tagged_jvm(self):
        # Only sbt's launcher reads .jvmopts; Maven and Gradle have their own.
        assert "JVM" not in tags_for(".jvmopts")

    def test_machine_level_sbtopts_is_not_matched(self):
        # /etc/sbt/sbtopts has no leading dot and is not a repository file.
        assert tags_for("etc/sbt/sbtopts") == set()

    @pytest.mark.parametrize("filename,expected", [
        (".sbtopts", "sbtopts"),
        (".jvmopts", "jvmopts"),
    ])
    def test_options_filetype(self, filename, expected):
        assert get_language(filename, skip_shebang=True) == expected


class TestMillBuildTags:

    @pytest.mark.parametrize("path", [
        "build.mill",
        "foo/package.mill",
        "build.mill.yaml",
        "foo/package.mill.yaml",
        "build.sc",               # Mill before 0.12
    ])
    def test_module_definition_files(self, path):
        assert tags_for(path) == {"Mill", "build", "dependencies"}

    def test_helper_mill_file_is_not_a_build_definition(self):
        # Imported helpers define no modules, so only build.mill and
        # package.mill get the build tags.
        assert tags_for("helpers.mill") == set()

    def test_mill_carries_no_language_tag(self):
        # Mill builds Java and Kotlin as first-class targets, like Gradle.
        assert "Scala" not in tags_for("build.mill")

    @pytest.mark.parametrize("path", [
        ".mill-version",
        ".config/mill-version",
        ".mill-jvm-version",
        ".mill-opts",
        ".mill-jvm-opts",
    ])
    def test_version_and_options_files(self, path):
        assert tags_for(path) == {"Mill", "build"}

    @pytest.mark.parametrize("path,expected", [
        (".mill-version", "mill-version"),
        (".config/mill-version", "mill-version"),
        (".mill-jvm-version", "mill-jvm-version"),
        (".mill-opts", "mill-opts"),
        (".mill-jvm-opts", "mill-jvm-opts"),
    ])
    def test_version_and_options_filetype(self, path, expected):
        assert get_language(path, skip_shebang=True) == expected

    def test_plain_script_sc_is_not_a_build_file(self):
        # Only the exact build.sc name is Mill; other .sc files are scripts.
        assert tags_for("script.sc") == set()


class TestNotProposed:
    """Candidates investigated and deliberately left out."""

    @pytest.mark.parametrize("path", [
        "project.scala",
        "src/main/scala/com/example/Project.scala",
        "project/Project.scala",
    ])
    def test_scala_cli_project_scala_is_not_tagged(self, path):
        # The name is only recommended, and lowercase basename matching
        # would also hit Project.scala source files.
        assert tags_for(path) == set()

    def test_sbt_build_properties_is_not_tagged(self):
        # build.properties is also Ant's name, and path_contains is a
        # substring match.
        assert tags_for("project/build.properties") == set()
        assert get_language("project/build.properties",
                            skip_shebang=True) == "Properties"

    def test_mill_bootstrap_script_is_not_tagged(self):
        assert tags_for("mill") == set()
