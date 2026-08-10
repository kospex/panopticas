"""Tests for the tags, languages and filetypes CLI commands."""

from click.testing import CliRunner

from panopticas import get_filetypes, get_languages, get_tags
from panopticas.cli import cli


class TestVocabularyCommands:
    """Each command prints its vocabulary and a count."""

    def test_tags_lists_every_tag(self):
        result = CliRunner().invoke(cli, ["tags"])
        assert result.exit_code == 0
        for tag in get_tags():
            assert tag in result.output

    def test_tags_reports_the_count(self):
        result = CliRunner().invoke(cli, ["tags"])
        assert f"{len(get_tags())} tags" in result.output

    def test_languages_lists_every_language(self):
        result = CliRunner().invoke(cli, ["languages"])
        assert result.exit_code == 0
        for language in get_languages():
            assert language in result.output

    def test_filetypes_lists_every_filetype(self):
        result = CliRunner().invoke(cli, ["filetypes"])
        assert result.exit_code == 0
        for filetype in get_filetypes():
            assert filetype in result.output

    def test_languages_omits_non_languages(self):
        result = CliRunner().invoke(cli, ["languages"])
        assert "PNG" not in result.output
