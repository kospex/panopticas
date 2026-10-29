"""
get_filename_metatypes() must not return a tag twice (#55).

It concatenates the tags of every rule that matches a path, so a tag two rules
both contribute used to appear twice. Most tests compare tags as sets, which
hides this, so these assert on the list itself.
"""

import pytest

from panopticas import get_filename_metatypes
from panopticas.constants import AI_RULES, METADATA_RULES


class TestReportedCases:
    """The paths from the issue, with first-seen order preserved."""

    @pytest.mark.parametrize("path,expected", [
        ("tsconfig.json",
         ["TypeScript", "JavaScript", "typechecker", "config"]),
        ("jsconfig.json",
         ["TypeScript", "JavaScript", "typechecker", "config"]),
        (".github/dependabot.yml",
         ["Dependabot", "GitHub", "dependencies", "security", "Git"]),
        (".github/dependabot.yaml",
         ["Dependabot", "GitHub", "dependencies", "security", "Git"]),
        (".github/CODEOWNERS", ["Git", "GitHub"]),
        (".github/.gitignore", ["Git", "ignore", "GitHub"]),
        (".github/.gitattributes", ["Git", "GitHub"]),
        (".github/workflows/azure-pipelines.yml",
         ["pipeline", "Azure DevOps", "workflow", "GitHub", "Git"]),
        ("config/checkstyle/checkstyle.xml",
         ["Java", "linter", "Checkstyle", "config"]),
        ("sorbet/.rubocop.yml",
         ["Ruby", "linter", "formatter", "RuboCop", "config",
          "typechecker", "Sorbet"]),
    ])
    def test_tags_are_unique_and_ordered(self, path, expected):
        assert get_filename_metatypes(path) == expected

    @pytest.mark.parametrize("path", [
        "dependabot.yml", ".gitignore", "package.json",
        ".github/workflows/ci.yml",
    ])
    def test_controls_are_unchanged(self, path):
        # These had no duplicates before; the fix must not alter them.
        tags = get_filename_metatypes(path)
        assert len(tags) == len(set(tags))


def _probe_paths():
    """
    Every rule's filename under every directory a rule matches — the same
    sweep the issue ran. Catches a duplicate introduced by any future rule.
    """
    names = set(METADATA_RULES["exact_filename_rules"])
    names |= set(AI_RULES["exact_filename"])
    names |= {"x" + ext for ext in METADATA_RULES["extension_rules"]}
    names |= {"x" + suffix for suffix in AI_RULES["filename_suffix"]}

    prefixes = {""}
    for fragment in (list(METADATA_RULES["path_contains_rules"])
                     + list(AI_RULES["path_contains"])):
        prefixes.add(fragment if fragment.endswith("/") else fragment + "/")

    return sorted(prefix + name for prefix in prefixes for name in names)


def test_no_path_returns_a_duplicate_tag():
    duplicated = {}
    for path in _probe_paths():
        tags = get_filename_metatypes(path)
        if len(tags) != len(set(tags)):
            duplicated[path] = tags
    assert not duplicated, (
        f"{len(duplicated)} paths return a duplicate tag, e.g. "
        f"{sorted(duplicated.items())[:3]}")
