"""Extension rules match regardless of case (#80).

get_extension_filetype() lowercased the extension but get_filename_metatypes()
did not, so App.CSPROJ had a filetype and no tags.
"""

import pytest

from panopticas.constants import METADATA_RULES
from panopticas.core import get_extension_filetype, get_filename_metatypes


@pytest.mark.parametrize("ext", sorted(METADATA_RULES["extension_rules"]))
def test_upper_case_extension_gets_the_same_tags(ext):
    assert get_filename_metatypes("x" + ext.upper()) == get_filename_metatypes("x" + ext)


def test_mixed_case_extension():
    assert get_filename_metatypes("App.Sln") == get_filename_metatypes("App.sln")
    assert get_filename_metatypes("App.Sln") != []


def test_filetype_and_tags_agree_on_case():
    # The two lookups must not disagree: a filetype with no tags was the bug.
    assert get_extension_filetype(".CSPROJ") == get_extension_filetype(".csproj")
    assert get_filename_metatypes("src/App/App.CSPROJ") == \
        get_filename_metatypes("src/App/App.csproj")


def test_exact_filename_rules_already_ignore_case():
    assert get_filename_metatypes("DOCKERFILE") == get_filename_metatypes("Dockerfile")


def test_path_rules_stay_case_sensitive():
    # Deliberately unchanged: path conventions are case-sensitive in git, and
    # GitHub reads .github/workflows/, not .GitHub/workflows/.
    assert get_filename_metatypes(".GitHub/workflows/ci.yml") == []
