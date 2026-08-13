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

    def test_unknown_filter_matches_the_unknown_language_string(self, tmp_path):
        # Regression test: get_language() returns the string "Unknown"
        # (core.UNKNOWN), never None. The old filter compared against None,
        # so `-unknown` never matched anything.
        (tmp_path / "readable.py").write_text("x = 1\n")
        (tmp_path / "mystery.zzqx").write_text("no idea what this is\n")

        payload = json.loads(
            CliRunner().invoke(
                cli, ["assess", str(tmp_path), "-unknown", "--json"]).stdout)

        assert payload["count"] == 1
        assert payload["files"][0]["path"] == "mystery.zzqx"
        assert payload["files"][0]["language"] == "Unknown"

    def test_stdout_is_only_the_document(self):
        # NOTE: Click 8.2+ changed Result.output to mix stdout+stderr in
        # write order (see Result.output docstring); Result.stdout is the
        # isolated stdout stream, which is what "stdout purity" means here.
        runner = CliRunner()
        result = runner.invoke(
            cli, ["assess", FIXTURES_DIR, "--json"], catch_exceptions=False)
        json.loads(result.stdout)  # raises if chatter leaked onto stdout
        assert "Assessing directory" not in result.stdout


class TestAiJson:
    """ai --json returns one record per AI artifact."""

    def test_documents_paths_and_products(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("guidance")
        (tmp_path / ".cursorrules").write_text("rules")

        result = CliRunner().invoke(cli, ["ai", str(tmp_path), "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)

        assert payload["count"] == 2
        assert payload["products"] == {"Claude": 1, "Cursor": 1}
        by_path = {r["path"]: r for r in payload["paths"]}
        assert by_path["CLAUDE.md"]["product"] == "Claude"
        assert by_path["CLAUDE.md"]["kind"] == "instructions"

    def test_empty_directory_is_still_an_object(self, tmp_path):
        payload = json.loads(
            CliRunner().invoke(cli, ["ai", str(tmp_path), "--json"]).stdout)
        assert payload["count"] == 0
        assert payload["paths"] == []
        assert payload["products"] == {}

    def test_paths_are_not_sanitised_in_json(self, tmp_path):
        # JSON escaping already neutralises control characters, and a consumer
        # needs the real path to open the file. The markup goes in a directory
        # component because AI_RULES matches on the basename — a file named
        # "[bold]CLAUDE.md" is not detected as an AI artifact at all.
        agents = tmp_path / "[bold]dir"
        agents.mkdir()
        (agents / "CLAUDE.md").write_text("guidance")

        payload = json.loads(
            CliRunner().invoke(cli, ["ai", str(tmp_path), "--json"]).stdout)

        assert any(r["path"] == "[bold]dir/CLAUDE.md" for r in payload["paths"])


class TestFileJson:
    """file --json describes a single file."""

    def test_documents_every_detection_method(self, tmp_path):
        target = tmp_path / "example.py"
        target.write_text("#!/usr/bin/env python3\n# see https://example.com\n")

        result = CliRunner().invoke(cli, ["file", str(target), "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)

        assert payload["file"] == str(target)
        assert payload["extension"] == ".py"
        assert payload["filetype"] == "Python"
        assert payload["shebang"] == "#!/usr/bin/env python3"
        assert payload["shebang_language"] == "Python"
        assert payload["meta"] == []
        assert payload["urls"] == ["https://example.com"]

    def test_absent_shebang_is_null(self, tmp_path):
        target = tmp_path / "notes.md"
        target.write_text("hello\n")
        payload = json.loads(
            CliRunner().invoke(cli, ["file", str(target), "--json"]).stdout)
        assert payload["shebang"] is None
        assert payload["shebang_language"] is None


class TestUrlsJson:
    """urls --json returns one record per file."""

    def test_documents_urls_per_file(self, tmp_path):
        (tmp_path / "README.md").write_text("see https://example.com\n")
        (tmp_path / "empty.md").write_text("nothing here\n")

        result = CliRunner().invoke(cli, ["urls", str(tmp_path), "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)

        assert payload["directory"] == str(tmp_path)
        assert payload["count"] == len(payload["files"])
        by_path = {r["path"]: r["urls"] for r in payload["files"]}
        assert by_path["README.md"] == ["https://example.com"]
        assert by_path["empty.md"] == []

    def test_undecodable_file_is_skipped_not_fatal(self, tmp_path):
        # extract_urls_from_file() raises UnicodeDecodeError on binary
        # content. `urls` scans a whole directory, so one bad file (e.g. a
        # .png) must not abort the command for every other file — it is
        # reported with no URLs rather than propagating the error.
        (tmp_path / "README.md").write_text("see https://example.com\n")
        (tmp_path / "image.bin").write_bytes(b"\xff\xfe\x00\x01not valid utf-8")

        result = CliRunner().invoke(cli, ["urls", str(tmp_path), "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)

        by_path = {r["path"]: r["urls"] for r in payload["files"]}
        assert by_path["README.md"] == ["https://example.com"]
        assert by_path["image.bin"] == []


class TestPathValidation:
    """Wrong path types fail at the Click boundary, not inside a handler."""

    def test_assess_rejects_a_file(self, tmp_path):
        target = tmp_path / "example.py"
        target.write_text("x = 1\n")
        result = CliRunner().invoke(cli, ["assess", str(target)])
        assert result.exit_code == 2
        assert "directory" in result.output.lower()

    def test_urls_rejects_a_file(self, tmp_path):
        target = tmp_path / "example.py"
        target.write_text("x = 1\n")
        result = CliRunner().invoke(cli, ["urls", str(target)])
        assert result.exit_code == 2

    def test_file_rejects_a_directory(self, tmp_path):
        result = CliRunner().invoke(cli, ["file", str(tmp_path)])
        assert result.exit_code == 2

    def test_missing_path_still_rejected(self):
        result = CliRunner().invoke(cli, ["assess", "/no/such/directory"])
        assert result.exit_code == 2

    def test_valid_paths_still_accepted(self, tmp_path):
        (tmp_path / "example.py").write_text("x = 1\n")
        assert CliRunner().invoke(
            cli, ["assess", str(tmp_path), "--json"]).exit_code == 0
        assert CliRunner().invoke(
            cli, ["file", str(tmp_path / "example.py"), "--json"]).exit_code == 0
