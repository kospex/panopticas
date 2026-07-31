"""
Tests for AI coding agent detection.

Covers: get_ai_metadata() resolution and precedence, AI tags in
get_filename_metatypes(), find_ai_files() directory walking, and
AI_RULES table integrity.
"""

import os
import tempfile

import pytest

from panopticas import get_ai_metadata, get_filename_metatypes, find_ai_files
from panopticas.constants import AI_RULES, AI_ARTIFACT_KINDS


class TestGetAiMetadataExactFilename:
    """Exact basename matches."""

    def test_claude_md(self):
        assert get_ai_metadata("CLAUDE.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_claude_md_lowercase(self):
        assert get_ai_metadata("claude.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_claude_md_in_subdirectory(self):
        assert get_ai_metadata("packages/api/CLAUDE.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_agents_md_is_vendor_neutral(self):
        assert get_ai_metadata("AGENTS.md") == {
            "product": "Agents", "kind": "instructions"}

    def test_gemini_md(self):
        assert get_ai_metadata("GEMINI.md") == {
            "product": "Gemini", "kind": "instructions"}

    def test_cursorrules(self):
        assert get_ai_metadata(".cursorrules") == {
            "product": "Cursor", "kind": "rules"}

    def test_cursorignore_is_an_ignore_file(self):
        assert get_ai_metadata(".cursorignore") == {
            "product": "Cursor", "kind": "ignore"}

    def test_mcp_json_is_protocol_not_product(self):
        assert get_ai_metadata(".mcp.json") == {
            "product": "MCP", "kind": "config"}

    def test_claude_desktop_config_tags_as_claude_brand(self):
        assert get_ai_metadata("claude_desktop_config.json") == {
            "product": "Claude", "kind": "config"}

    def test_llms_txt(self):
        assert get_ai_metadata("llms.txt") == {
            "product": "llms.txt", "kind": "docs"}


class TestGetAiMetadataPathContains:
    """Directory fragment matches."""

    def test_claude_settings(self):
        assert get_ai_metadata(".claude/settings.json") == {
            "product": "Claude", "kind": "config"}

    def test_claude_skill(self):
        assert get_ai_metadata(".claude/skills/review/SKILL.md") == {
            "product": "Claude", "kind": "skill"}

    def test_claude_agent(self):
        assert get_ai_metadata(".claude/agents/reviewer.md") == {
            "product": "Claude", "kind": "agent"}

    def test_claude_command(self):
        assert get_ai_metadata(".claude/commands/deploy.md") == {
            "product": "Claude", "kind": "command"}

    def test_copilot_prompt_directory(self):
        assert get_ai_metadata(".github/prompts/refactor.md") == {
            "product": "Copilot", "kind": "prompt"}

    def test_cursor_rules_directory(self):
        assert get_ai_metadata(".cursor/rules/style.mdc") == {
            "product": "Cursor", "kind": "rules"}

    def test_cursor_mcp_json_attributes_to_cursor(self):
        assert get_ai_metadata(".cursor/mcp.json") == {
            "product": "Cursor", "kind": "config"}

    def test_vscode_mcp_json(self):
        assert get_ai_metadata(".vscode/mcp.json") == {
            "product": "MCP", "kind": "config"}

    def test_codex_directory(self):
        assert get_ai_metadata(".codex/config.toml") == {
            "product": "Codex", "kind": "config"}

    def test_gemini_directory(self):
        assert get_ai_metadata(".gemini/settings.json") == {
            "product": "Gemini", "kind": "config"}

    def test_nested_repo_path(self):
        assert get_ai_metadata("vendor/lib/.claude/settings.json") == {
            "product": "Claude", "kind": "config"}


class TestGetAiMetadataSuffix:
    """Filename suffix matches."""

    def test_prompt_md_suffix(self):
        assert get_ai_metadata("docs/refactor.prompt.md") == {
            "product": "Copilot", "kind": "prompt"}

    def test_instructions_md_suffix(self):
        assert get_ai_metadata("docs/python.instructions.md") == {
            "product": "Copilot", "kind": "instructions"}

    def test_mdc_suffix(self):
        assert get_ai_metadata("rules/style.mdc") == {
            "product": "Cursor", "kind": "rules"}


class TestGetAiMetadataPrecedence:
    """Exact beats path; longer path fragment beats shorter."""

    def test_exact_filename_beats_path_fragment(self):
        # .claude/ would give kind "config"; the exact CLAUDE.md rule wins.
        assert get_ai_metadata(".claude/CLAUDE.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_longer_path_fragment_wins(self):
        # Both ".claude/" and ".claude/skills/" match; the longer one wins.
        assert get_ai_metadata(".claude/skills/x/helper.py") == {
            "product": "Claude", "kind": "skill"}

    def test_path_fragment_beats_suffix(self):
        # ".cursor/rules/" and ".mdc" both give (Cursor, rules) here, but
        # the path fragment is what resolves it.
        assert get_ai_metadata(".cursor/rules/a.mdc")["kind"] == "rules"


class TestGetAiMetadataNonMatches:
    """Ordinary files are not AI artifacts."""

    @pytest.mark.parametrize("path", [
        "pyproject.toml",
        "src/panopticas/core.py",
        "README.md",
        "docs/index.html",
        ".github/workflows/ci.yml",
        ".gitignore",
        "package.json",
    ])
    def test_returns_none(self, path):
        assert get_ai_metadata(path) is None

    def test_empty_path(self):
        assert get_ai_metadata("") is None


class TestAiRulesIntegrity:
    """Guards the table against rot as entries are added."""

    def test_only_known_match_modes(self):
        assert set(AI_RULES) == {
            "exact_filename", "path_contains", "filename_suffix"}

    def test_every_value_is_a_product_kind_pair(self):
        for mode, rules in AI_RULES.items():
            for key, value in rules.items():
                assert isinstance(value, tuple), f"{mode}:{key} is not a tuple"
                assert len(value) == 2, f"{mode}:{key} is not a 2-tuple"
                product, kind = value
                assert product and isinstance(product, str)
                assert kind and isinstance(kind, str)

    def test_every_kind_is_in_the_vocabulary(self):
        for mode, rules in AI_RULES.items():
            for key, (_product, kind) in rules.items():
                assert kind in AI_ARTIFACT_KINDS, f"{mode}:{key} has kind {kind!r}"

    def test_exact_filename_keys_are_lowercase(self):
        for key in AI_RULES["exact_filename"]:
            assert key == key.lower()

    def test_path_contains_keys_contain_a_slash(self):
        # Either a directory fragment ending in "/", or a dir-qualified
        # filename such as ".vscode/mcp.json".
        for key in AI_RULES["path_contains"]:
            assert "/" in key, f"{key!r} has no path separator"
            assert key == key.lower()

    def test_filename_suffix_keys_start_with_a_dot(self):
        for key in AI_RULES["filename_suffix"]:
            assert key.startswith("."), f"{key!r} does not start with a dot"
            assert key == key.lower()

    def test_no_key_appears_in_two_modes(self):
        seen = {}
        for mode, rules in AI_RULES.items():
            for key in rules:
                assert key not in seen, f"{key!r} in both {seen.get(key)} and {mode}"
                seen[key] = mode


class TestAiTagsInMetatypes:
    """get_filename_metatypes() derives its AI tags from get_ai_metadata()."""

    def test_claude_md_tags(self):
        assert get_filename_metatypes("CLAUDE.md") == [
            "AI", "Claude", "instructions"]

    def test_claude_settings_tags(self):
        assert get_filename_metatypes(".claude/settings.json") == [
            "AI", "Claude", "config"]

    def test_agents_md_tags(self):
        assert get_filename_metatypes("AGENTS.md") == [
            "AI", "Agents", "instructions"]

    def test_cursor_rule_tags(self):
        assert get_filename_metatypes(".cursor/rules/style.mdc") == [
            "AI", "Cursor", "rules"]

    def test_legacy_bare_claude_tag_is_gone(self):
        # The old rule emitted ["Claude", "AI", "Claude Code"].
        tags = get_filename_metatypes("CLAUDE.md")
        assert "Claude Code" not in tags
        assert tags.count("Claude") == 1

    def test_ai_tag_always_present_for_ai_files(self):
        for path in ["CLAUDE.md", ".claude/settings.json", "AGENTS.md",
                     ".cursorrules", ".mcp.json", "llms.txt"]:
            assert "AI" in get_filename_metatypes(path), path

    def test_ai_tags_come_first_in_their_group(self):
        # ["AI", product, kind] is appended as a contiguous triple.
        tags = get_filename_metatypes(".github/copilot-instructions.md")
        index = tags.index("AI")
        assert tags[index:index + 3] == ["AI", "Copilot", "instructions"]


class TestExistingTagsPreserved:
    """The AI pass must not disturb the existing metadata rules."""

    def test_copilot_instructions_keeps_github_tags(self):
        tags = get_filename_metatypes(".github/copilot-instructions.md")
        assert tags == ["GitHub", "Git", "AI", "Copilot", "instructions"]

    def test_workflow_tags_unchanged(self):
        assert get_filename_metatypes(".github/workflows/ci.yml") == [
            "workflow", "pipeline", "GitHub", "Git"]

    def test_pyproject_tags_unchanged(self):
        assert get_filename_metatypes("pyproject.toml") == [
            "build", "dependencies", "Python"]

    def test_ordinary_file_has_no_ai_tag(self):
        assert "AI" not in get_filename_metatypes("src/panopticas/core.py")


def _build_repo(root):
    """Create a small repo tree with AI artifacts and a .gitignore."""
    def write(relative_path, content=""):
        full = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(content)

    write("CLAUDE.md", "# guidance\n")
    write("AGENTS.md", "# agents\n")
    write("pyproject.toml", "[project]\n")
    write("src/app.py", "print('hi')\n")
    write(".claude/settings.json", "{}\n")
    write(".claude/skills/review/SKILL.md", "# skill\n")
    write(".cursor/rules/style.mdc", "rule\n")
    write(".gitignore", ".cursor/\nsecret.txt\n")
    write("secret.txt", "shh\n")


class TestFindAiFiles:
    """Directory walking, gitignore handling and bare directories."""

    def test_finds_ai_files_only(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            assert "CLAUDE.md" in found
            assert "AGENTS.md" in found
            assert "pyproject.toml" not in found
            assert os.path.join("src", "app.py") not in found

    def test_returns_product_and_kind(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            assert found["CLAUDE.md"] == {
                "product": "Claude", "kind": "instructions"}
            assert found[os.path.join(".claude", "settings.json")] == {
                "product": "Claude", "kind": "config"}
            assert found[os.path.join(".claude", "skills", "review", "SKILL.md")] == {
                "product": "Claude", "kind": "skill"}

    def test_honours_gitignore_by_default(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            # .cursor/ is gitignored, so its rule file must not appear.
            assert not any(".cursor" in path for path in found)

    def test_all_files_surfaces_ignored_files(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root, all_files=True)
            assert os.path.join(".cursor", "rules", "style.mdc") in found

    def test_all_files_emits_bare_directories(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root, all_files=True)
            cursor_dir = ".cursor" + os.sep
            assert cursor_dir in found
            assert found[cursor_dir] == {
                "product": "Cursor", "kind": "directory"}

    def test_default_emits_no_directories(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            assert all(meta["kind"] != "directory" for meta in found.values())

    def test_empty_directory_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as root:
            assert find_ai_files(root) == {}
