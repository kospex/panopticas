"""Every public is_* predicate in panopticas.core is exported from the package.

kospex resolves these by name, as getattr(panopticas, name), and treats a
missing name as "no match" so an older panopticas degrades instead of breaking.
A predicate defined in core but not exported therefore matches nothing in
kospex, silently (#110).
"""
import inspect

import pytest

import panopticas
from panopticas import core


def _core_predicates():
    return sorted(
        name
        for name, obj in inspect.getmembers(core, inspect.isfunction)
        if name.startswith("is_") and obj.__module__ == core.__name__
    )


def test_core_has_predicates():
    # Guards against the export test passing vacuously over an empty list.
    assert "is_pip_requirements" in _core_predicates()


@pytest.mark.parametrize("name", _core_predicates())
def test_predicate_is_exported(name):
    assert name in panopticas.__all__
    assert getattr(panopticas, name) is getattr(core, name)


@pytest.mark.parametrize("name", [
    "is_pylock",
    "is_nuget_project_lock",
    "is_appsettings_environment",
    "is_dotenv",
    "is_dotenv_template",
])
def test_issue_110_predicates_exported(name):
    # The five named in #110, pinned so a rename in core can't drop one
    # from the generic test above without failing here.
    assert getattr(panopticas, name) is getattr(core, name)
