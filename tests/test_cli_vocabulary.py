"""Tests for the tags, languages and filetypes CLI commands."""

import json
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


class TestVocabularyJson:
    """--json and -json produce a parseable document."""

    def test_tags_json_shape(self):
        result = CliRunner().invoke(cli, ["tags", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["tags"] == get_tags()
        assert payload["count"] == len(get_tags())

    def test_languages_json_shape(self):
        payload = json.loads(CliRunner().invoke(cli, ["languages", "--json"]).output)
        assert payload["languages"] == get_languages()
        assert payload["count"] == len(get_languages())

    def test_filetypes_json_shape(self):
        payload = json.loads(CliRunner().invoke(cli, ["filetypes", "--json"]).output)
        assert payload["filetypes"] == get_filetypes()
        assert payload["count"] == len(get_filetypes())

    def test_single_dash_json_is_identical(self):
        runner = CliRunner()
        assert (runner.invoke(cli, ["tags", "-json"]).output
                == runner.invoke(cli, ["tags", "--json"]).output)

    def test_top_level_is_an_object(self):
        # Never a bare array — fields can then be added without breaking
        # existing parsers.
        payload = json.loads(CliRunner().invoke(cli, ["tags", "--json"]).output)
        assert isinstance(payload, dict)
