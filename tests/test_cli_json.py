"""Tests for --json output on the file-scanning commands."""

import json
import os

from click.testing import CliRunner

from panopticas.cli import cli

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "tests")


class TestAssessJson:
    """assess --json returns one record per file."""

    def test_documents_every_file(self):
        result = CliRunner().invoke(cli, ["assess", FIXTURES_DIR, "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["directory"] == FIXTURES_DIR
        assert payload["count"] == len(payload["files"])
        assert payload["files"]

    def test_meta_is_a_list_not_a_joined_string(self):
        payload = json.loads(
            CliRunner().invoke(cli, ["assess", FIXTURES_DIR, "--json"]).stdout)
        for record in payload["files"]:
            assert isinstance(record["meta"], list)
            assert set(record) >= {"path", "language", "meta"}

    def test_lines_absent_without_the_flag(self):
        payload = json.loads(
            CliRunner().invoke(cli, ["assess", FIXTURES_DIR, "--json"]).stdout)
        assert "total_lines" not in payload
        assert all("lines" not in r for r in payload["files"])

    def test_lines_present_with_the_flag(self):
        payload = json.loads(
            CliRunner().invoke(
                cli, ["assess", FIXTURES_DIR, "--lines", "--json"]).stdout)
        assert isinstance(payload["total_lines"], int)
        assert all("lines" in r for r in payload["files"])

    def test_binary_line_count_is_null(self, tmp_path):
        # count_lines() returns the string "N/A" for undecodable files; the
        # JSON contract says null. src/tests/ holds only empty files, so this
        # builds a genuinely non-UTF-8 file rather than passing vacuously.
        (tmp_path / "payload.bin").write_bytes(b"\xff\xfe\x00\x01binary\x80")
        (tmp_path / "readable.py").write_text("x = 1\n")

        payload = json.loads(
            CliRunner().invoke(
                cli, ["assess", str(tmp_path), "--lines", "--json"]).stdout)

        by_path = {r["path"]: r["lines"] for r in payload["files"]}
        assert by_path["payload.bin"] is None
        assert by_path["readable.py"] == 1
        # The undecodable file must not inflate or corrupt the total.
        assert payload["total_lines"] == 1

    def test_stdout_is_only_the_document(self):
        # NOTE: Click 8.2+ changed Result.output to mix stdout+stderr in
        # write order (see Result.output docstring); Result.stdout is the
        # isolated stdout stream, which is what "stdout purity" means here.
        runner = CliRunner()
        result = runner.invoke(
            cli, ["assess", FIXTURES_DIR, "--json"], catch_exceptions=False)
        json.loads(result.stdout)  # raises if chatter leaked onto stdout
        assert "Assessing directory" not in result.stdout
