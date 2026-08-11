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
