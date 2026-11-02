"""
.NET build, dependency and config files (#72, part one).

NuGet is the OSV ecosystem, so files that declare or lock NuGet packages
carry it alongside the tool tag, as Gradle files carry Maven. Sources in
changes/2026-10-dotnet-detection.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_tags


@pytest.mark.parametrize("path,tags", [
    # Solutions: the XML format and solution filters.
    ("App.slnx", [".NET", "Visual Studio", "build"]),
    ("App.slnf", [".NET", "Visual Studio", "build"]),
    # Project files declare PackageReference dependencies.
    ("src/App/App.csproj", [".NET", "C#", "NuGet", "build", "dependencies"]),
    ("src/Lib/Lib.fsproj", [".NET", "F#", "NuGet", "build", "dependencies"]),
    ("src/Vb/Vb.vbproj",
     [".NET", "Visual Basic", "NuGet", "build", "dependencies"]),
    # MSBuild picks these up from the project's directory or a parent.
    ("Directory.Build.props", [".NET", "MSBuild", "build"]),
    ("src/Directory.Build.targets", [".NET", "MSBuild", "build"]),
    ("Directory.Build.rsp", [".NET", "MSBuild", "build"]),
    ("Directory.Solution.props", [".NET", "MSBuild", "build"]),
    ("Directory.Solution.targets", [".NET", "MSBuild", "build"]),
    # Central package management holds the versions.
    ("Directory.Packages.props", [".NET", "MSBuild", "NuGet", "dependencies"]),
    ("src/App/packages.lock.json", [".NET", "NuGet", "dependencies"]),
    # A .NET tool is a NuGet package.
    (".config/dotnet-tools.json", [".NET", "NuGet", "dependencies"]),
    ("App.nuspec", [".NET", "NuGet", "build", "dependencies"]),
    ("global.json", [".NET", "build", "config"]),
    # Paket resolves NuGet packages.
    ("paket.dependencies", [".NET", "Paket", "NuGet", "dependencies"]),
    ("paket.lock", [".NET", "Paket", "NuGet", "dependencies"]),
    ("src/App/paket.references", [".NET", "Paket", "NuGet", "dependencies"]),
    # Build tools
    ("build.cake", [".NET", "Cake", "build"]),
    (".nuke/parameters.json", [".NET", "NUKE", "build"]),
    # ASP.NET Core and dotnet run settings
    ("src/App/appsettings.json", [".NET", "config"]),
    ("src/App/Properties/launchSettings.json", [".NET", "config"]),
])
def test_dotnet_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path,filetype", [
    ("App.slnx", "Visual Studio Solution"),
    ("App.slnf", "JSON"),
    ("Lib.fsproj", "F# Project"),
    ("Vb.vbproj", "Visual Basic Project"),
    ("Directory.Build.props", "XML"),
    ("Directory.Build.targets", "XML"),
    ("Directory.Solution.props", "XML"),
    ("Directory.Solution.targets", "XML"),
    ("Directory.Packages.props", "XML"),
    ("Directory.Build.rsp", "MSBuild Response File"),
    ("App.nuspec", "XML"),
    # Both document comments.
    ("global.json", "JSONC"),
    ("appsettings.json", "JSONC"),
    ("packages.lock.json", "JSON"),
    ("paket.dependencies", "Paket"),
    ("paket.references", "Paket"),
    ("paket.lock", "Lock"),
    # Cake is a C# DSL.
    ("build.cake", "C#"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


def test_global_asax_filetype():
    # The old ".global.asax" key could never match: splitext gives ".asax".
    assert get_language("Global.asax", skip_shebang=True) == "ASP.NET Global"


@pytest.mark.parametrize("path", [
    # Generic MSBuild extensions; NuGet packages ship <id>.props too.
    "MyPackage.props",
    "MyPackage.targets",
    # Not exact-matchable variants and lookalikes
    "packages.App.lock.json",
    "appsettings.Development.json",
    "my-global.json",
    "build.ps1",
    "nuke/parameters.json",
])
def test_not_tagged(path):
    assert not {".NET", "MSBuild", "NuGet", "Paket", "NUKE"} & \
        set(get_filename_metatypes(path))


def test_new_tags_in_vocabulary():
    assert {"F#", "Visual Basic", "MSBuild", "Paket", "Cake", "NUKE"} <= \
        set(get_tags())
