"""
Python packaging files (#74).

Shape is [Language, tool, ecosystem, role]; `PyPI` is the ecosystem, and
the tool gets its own tag. Sources in changes/2026-11-dependency-manifests.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_tags


@pytest.mark.parametrize("path,tags", [
    # Pipenv
    ("Pipfile", ["Python", "Pipenv", "PyPI", "dependencies"]),
    ("Pipfile.lock", ["Python", "Pipenv", "PyPI", "dependencies"]),
    # Poetry
    ("poetry.lock", ["Python", "Poetry", "PyPI", "dependencies"]),
    ("poetry.toml", ["Python", "Poetry", "config"]),
    # PDM
    ("pdm.lock", ["Python", "PDM", "PyPI", "dependencies"]),
    ("pdm.toml", ["Python", "PDM", "config"]),
    (".pdm-python", ["Python", "PDM", "config"]),
    # uv
    ("uv.toml", ["Python", "uv", "config"]),
    # setuptools sdist contents
    ("MANIFEST.in", ["Python", "setuptools", "build"]),
    # PEP 561 marker, inside the package directory
    ("src/mypkg/py.typed", ["Python", "typing"]),
    # Type stubs
    ("src/mypkg/__init__.pyi", ["Python", "typing"]),
    ("mypkg-stubs/core.pyi", ["Python", "typing"]),
])
def test_python_packaging_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path", [
    "pylock.toml",
    "pylock.dev.toml",
    "pylock.py312-linux.toml",
    "subdir/pylock.toml",
])
def test_pylock(path):
    # PEP 751: pylock.toml or pylock.<name>.toml. pip, uv and PDM all write
    # it, so no tool tag.
    assert get_filename_metatypes(path) == ["Python", "PyPI", "dependencies"]


@pytest.mark.parametrize("path", [
    "pylock.a.b.toml",   # the name may not contain a dot
    "mypylock.toml",
    "pylock.json",
    "pylock..toml",
])
def test_not_pylock(path):
    assert "PyPI" not in get_filename_metatypes(path)


@pytest.mark.parametrize("path,tags", [
    ("uv.lock", ["dependencies", "Python", "uv", "PyPI"]),
    ("pyproject.toml", ["build", "dependencies", "Python", "PyPI"]),
    ("setup.py", ["build", "dependencies", "Python", "setuptools", "PyPI"]),
    ("setup.cfg", ["build", "dependencies", "Python", "setuptools", "PyPI"]),
])
def test_existing_manifests_gain_pypi(path, tags):
    assert get_filename_metatypes(path) == tags


def test_requirements_unchanged():
    assert get_filename_metatypes("requirements.txt") == \
        ["pip", "Python", "PyPI", "dependencies"]


@pytest.mark.parametrize("path,filetype", [
    ("Pipfile", "TOML"),
    ("Pipfile.lock", "Lock"),
    (".pdm-python", "pdm-python"),
    ("MANIFEST.in", "MANIFEST.in"),
    ("py.typed", "py.typed"),
    ("stub.pyi", "Python"),
    ("pylock.dev.toml", "TOML"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


@pytest.mark.parametrize("path", [
    # Rejected in the research note: generic or arbitrary names.
    "constraints.txt",
    "environment.yml",
    "environment.yaml",
    "auth.json",
    # setuptools calls a bare MANIFEST outdated.
    "MANIFEST",
    # Lookalikes.
    "typed.py",
    "poetry.lock.bak",
])
def test_not_tagged(path):
    tags = get_filename_metatypes(path)
    assert not {"PyPI", "Pipenv", "Poetry", "PDM", "typing"} & set(tags)


def test_new_tags_in_vocabulary():
    assert {"Pipenv", "Poetry", "PDM", "typing"} <= set(get_tags())
