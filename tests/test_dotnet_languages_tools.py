"""
.NET languages, linters, formatters and editor files (#72, part two).

F#, Visual Basic and Razor are languages; XAML and .resx are XML formats.
CSharpier and FSharpLint join LINTER_RULES. Fantomas and `dotnet format`
are rejected: both are configured in .editorconfig, a shared file. Sources
in changes/2026-10-dotnet-detection.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_languages, get_tags


@pytest.mark.parametrize("path,filetype", [
    # F# spec: "Source code files, with extensions .fs, .fsi, .fsx, or
    # .fsscript". GLSL fragment shaders sometimes use .fs too.
    ("src/Lib/Library.fs", "F#"),
    ("src/Lib/Library.fsi", "F#"),
    ("scripts/build.fsx", "F#"),
    ("scripts/build.fsscript", "F#"),
    ("src/Vb/Module1.vb", "Visual Basic"),
    ("Pages/Index.cshtml", "Razor"),
    ("Components/Counter.razor", "Razor"),
    ("MainWindow.xaml", "XAML"),
    ("Properties/Resources.resx", "XML"),
    # CSharpier: .csharpierrc is JSON or YAML, so it gets its own name.
    (".csharpierrc", "CSharpierRC"),
    (".csharpierrc.json", "JSON"),
    (".csharpierrc.yaml", "YAML"),
    (".csharpierignore", "CSharpierIgnore"),
    ("fsharplint.json", "JSON"),
    # Rider's team-shared settings layer is XML.
    ("App.sln.DotSettings", "XML"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


def test_new_languages():
    assert {"F#", "Visual Basic", "Razor"} <= set(get_languages())


def test_xaml_is_not_a_language():
    # UI markup in XML, like SVG.
    assert "XAML" not in get_languages()


@pytest.mark.parametrize("path", [
    "src/Lib/Library.fs",
    "src/Vb/Module1.vb",
    "Pages/Index.cshtml",
    "Components/Counter.razor",
    "MainWindow.xaml",
    "Properties/Resources.resx",
])
def test_source_files_untagged(path):
    # Source files carry no tags, as .cs does.
    assert get_filename_metatypes(path) == []


@pytest.mark.parametrize("path,tags", [
    (".csharpierrc", ["C#", ".NET", "formatter", "CSharpier", "config"]),
    (".csharpierrc.json", ["C#", ".NET", "formatter", "CSharpier", "config"]),
    ("src/.csharpierrc.yaml",
     ["C#", ".NET", "formatter", "CSharpier", "config"]),
    (".csharpierignore", ["C#", ".NET", "formatter", "CSharpier", "ignore"]),
    ("fsharplint.json", ["F#", ".NET", "linter", "FSharpLint", "config"]),
])
def test_linter_configs(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path,tags", [
    # The team-shared layer, meant to be committed. The extension's case is
    # always mixed.
    ("App.sln.DotSettings", ["JetBrains", "editor", "config"]),
    # Per-user and usually gitignored; tagged because it is there.
    (".vs/App/v17/.suo", ["Visual Studio", "editor", "config"]),
    (".vs/ProjectSettings.json", ["Visual Studio", "editor", "config"]),
])
def test_editor_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path", [
    # The per-user layer; ".user" is too generic to tag.
    "App.sln.DotSettings.user",
    "App.csproj.user",
    # .vscode/ must not match the .vs/ rule.
    ".vscode/settings.json",
])
def test_not_visual_studio_or_rider(path):
    tags = set(get_filename_metatypes(path))
    assert "Visual Studio" not in tags
    assert not ("JetBrains" in tags and path.endswith(".user"))


@pytest.mark.parametrize("path", [
    # Rejected: Fantomas and dotnet format read .editorconfig, which stays
    # tool-neutral.
    ".editorconfig",
])
def test_editorconfig_not_claimed_by_dotnet_formatters(path):
    tags = set(get_filename_metatypes(path))
    assert not {"Fantomas", "dotnet format", "CSharpier"} & tags


def test_new_tags_in_vocabulary():
    assert {"CSharpier", "FSharpLint"} <= set(get_tags())
