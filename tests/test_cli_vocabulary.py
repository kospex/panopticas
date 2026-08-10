"""Tests for the tags, languages and filetypes CLI commands."""

import re

from click.testing import CliRunner

from panopticas import get_filetypes, get_languages, get_tags
from panopticas.cli import cli


def rendered_values(output):
    """Recover the exact values from a rich Columns grid.

    Columns pads cells apart with two or more spaces, while multi-word
    values (C Header, Groovy Server Pages) contain single spaces — so
    splitting on 2+ whitespace gives back the cells intact. Substring
    assertions cannot do this: "C" appears inside "CSS".
    """
    return {v for v in re.split(r"\s{2,}|\n", output.strip()) if v}


class TestVocabularyCommands:
    """Each command prints its vocabulary and a count."""

    def test_tags_lists_every_tag(self):
        result = CliRunner().invoke(cli, ["tags"])
        assert result.exit_code == 0
        assert set(get_tags()) <= rendered_values(result.output)

    def test_tags_reports_the_count(self):
        result = CliRunner().invoke(cli, ["tags"])
        assert f"{len(get_tags())} tags" in result.output

    def test_languages_lists_every_language(self):
        result = CliRunner().invoke(cli, ["languages"])
        assert result.exit_code == 0
        assert set(get_languages()) <= rendered_values(result.output)

    def test_filetypes_lists_every_filetype(self):
        result = CliRunner().invoke(cli, ["filetypes"])
        assert result.exit_code == 0
        assert set(get_filetypes()) <= rendered_values(result.output)

    def test_languages_omits_non_languages(self):
        result = CliRunner().invoke(cli, ["languages"])
        assert "PNG" not in result.output
