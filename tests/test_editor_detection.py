"""
Editor and IDE project files (#20).

Tagged editor, the editor's brand and config. These are METADATA_RULES, not
AI_RULES: an editor is not an AI agent. Sources in
changes/2026-10-editor-detection.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language


@pytest.mark.parametrize("path,brand", [
    (".vscode/settings.json", "VS Code"),
    (".vscode/launch.json", "VS Code"),
    (".vscode/tasks.json", "VS Code"),
    (".vscode/extensions.json", "VS Code"),
    ("project.code-workspace", "VS Code"),
    (".idea/misc.xml", "JetBrains"),
    (".idea/runConfigurations/app.xml", "JetBrains"),
    ("app.iml", "JetBrains"),
    (".zed/settings.json", "Zed"),
    (".zed/tasks.json", "Zed"),
    (".zed/debug.json", "Zed"),
    ("project.sublime-project", "Sublime Text"),
    ("project.sublime-workspace", "Sublime Text"),
])
def test_editor_files(path, brand):
    assert get_filename_metatypes(path) == [brand, "editor", "config"]


def test_nested_project():
    assert get_filename_metatypes("services/api/.vscode/settings.json") == [
        "VS Code", "editor", "config"]


def test_vscode_mcp_json_keeps_its_ai_tags():
    # AI_RULES is a separate pass, so the MCP config carries both.
    assert get_filename_metatypes(".vscode/mcp.json") == [
        "VS Code", "editor", "config", "AI", "MCP"]


@pytest.mark.parametrize("path,filetype", [
    # VS Code reads workspace files as JSON with comments.
    ("project.code-workspace", "JSONC"),
    ("project.sublime-project", "JSON"),
    ("project.sublime-workspace", "JSON"),
    ("app.iml", "XML"),
])
def test_filetypes(path, filetype):
    assert get_language(path) == filetype


def test_editorconfig_is_unchanged():
    # Editor-neutral, and already a linter rule.
    assert "editor" not in get_filename_metatypes(".editorconfig")
