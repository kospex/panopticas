"""Tests for terminal-safe rendering of untrusted paths and URLs."""

from panopticas.cli import cell, sanitise_for_display


class TestCell:
    """cell() strips control characters and neutralises rich markup."""

    def test_plain_value_unchanged(self):
        assert cell("src/panopticas/core.py") == "src/panopticas/core.py"

    def test_rich_markup_is_escaped(self):
        # Escaped so rich renders the literal text rather than styling it.
        assert cell("[blink]evil.py") != "[blink]evil.py"
        assert "blink" in cell("[blink]evil.py")

    def test_ansi_escape_stripped(self):
        assert "\x1b" not in cell("evil\x1b[31m.py")

    def test_c1_control_character_stripped(self):
        # \x9b is the single-byte CSI introducer in 8-bit control mode.
        assert "\x9b" not in cell("evil\x9b31m.py")

    def test_null_byte_stripped(self):
        assert "\x00" not in cell("evil\x00.py")

    def test_combined_attack_neutralised(self):
        result = cell("\x1b[31m[bold]evil.py")
        assert "\x1b" not in result
        assert not result.startswith("[bold]")

    def test_matches_sanitise_for_display_on_control_characters(self):
        # cell() must not weaken the existing protection.
        value = "a\x1b[31mb\x9fc"
        assert "\x1b" not in cell(value)
        assert sanitise_for_display(value) in cell(value)


class TestBannerSanitisation:
    """The progress lines interpolate a path and must be sanitised too."""

    def test_control_characters_stripped_from_banner(self, capsys):
        from panopticas.cli import banner

        banner("Assessing directory: evil\x1b[31mdir", as_json=False)
        assert "\x1b" not in capsys.readouterr().out

    def test_banner_goes_to_stderr_in_json_mode(self, capsys):
        from panopticas.cli import banner

        banner("Assessing directory: .", as_json=True)
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "Assessing directory" in captured.err


import json

from click.testing import CliRunner

from panopticas.cli import cli


class TestAssessEscapesPaths:
    """A crafted filename cannot style or corrupt assess output."""

    def test_markup_in_filename_is_not_interpreted(self, tmp_path):
        (tmp_path / "[bold]evil.py").write_text("x = 1\n")
        result = CliRunner().invoke(cli, ["assess", str(tmp_path)])
        assert result.exit_code == 0
        # The literal name appears; the markup is not consumed as styling.
        assert "evil.py" in result.output

    def test_json_keeps_the_real_path(self, tmp_path):
        (tmp_path / "[bold]evil.py").write_text("x = 1\n")
        payload = json.loads(
            CliRunner().invoke(cli, ["assess", str(tmp_path), "--json"]).stdout)
        assert any(r["path"] == "[bold]evil.py" for r in payload["files"])


class TestShebangIsUntrusted:
    """The language column can come from the file's own first line."""

    def test_crafted_shebang_does_not_reach_the_terminal_raw(self, tmp_path):
        # get_language() falls back to extract_shebang_language(), which
        # returns text read out of the file — a crafted shebang would
        # otherwise be rendered as markup and control sequences.
        target = tmp_path / "trap"
        target.write_text("#!/usr/bin/env \x1b[31m[blink]sh\n")

        result = CliRunner().invoke(cli, ["assess", str(tmp_path)])
        assert result.exit_code == 0
        assert "\x1b" not in result.output

    def test_file_command_escapes_the_shebang(self, tmp_path):
        target = tmp_path / "trap"
        target.write_text("#!/usr/bin/env \x1b[31m[blink]sh\n")

        result = CliRunner().invoke(cli, ["file", str(target)])
        assert result.exit_code == 0
        assert "\x1b" not in result.output

    def test_json_keeps_the_raw_shebang(self, tmp_path):
        target = tmp_path / "trap"
        target.write_text("#!/usr/bin/env python3\n")
        payload = json.loads(
            CliRunner().invoke(cli, ["file", str(target), "--json"]).stdout)
        assert payload["shebang"] == "#!/usr/bin/env python3"


class TestFileCommandEscapesExtension:
    """The extension row can carry a raw, attacker-controlled filename."""

    def test_extensionless_filename_is_escaped_and_sanitised(self, tmp_path):
        # get_fileext() falls back to os.path.basename() when the file has
        # no extension (core.py), so an extensionless file's raw name lands
        # in the "File extenion" row. Without cell() the markup would be
        # consumed as styling and the ESC byte would reach the terminal raw.
        target = tmp_path / "ev\x1b[31m[bold]il"
        target.write_text("plain content\n")

        result = CliRunner().invoke(cli, ["file", str(target)])
        assert result.exit_code == 0
        assert "\x1b" not in result.output
        # Escaped markup renders as literal text rather than being consumed
        # as a style directive — "bold" survives in the visible output.
        assert "bold" in result.output


class TestAiEscapesPaths:
    """The ai command renders untrusted paths safely."""

    def test_markup_in_ai_filename_is_escaped(self, tmp_path):
        agents = tmp_path / "[bold]dir"
        agents.mkdir()
        (agents / "CLAUDE.md").write_text("guidance")

        result = CliRunner().invoke(cli, ["ai", str(tmp_path)])
        assert result.exit_code == 0
        assert "CLAUDE.md" in result.output
        assert "Claude" in result.output
