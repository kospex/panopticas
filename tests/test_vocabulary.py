"""
Tests for the tag, filetype and language vocabularies.

The drift test is the important one: it synthesises a path for every rule in
METADATA_RULES and AI_RULES and asserts that every tag those paths produce is
present in get_tags(). A future rule whose tags escape the vocabulary fails
here rather than shipping silently.
"""

import pytest

from panopticas import get_filename_metatypes, get_tags
from panopticas.constants import AI_RULES, IMPLICIT_TAGS, METADATA_RULES


def sample_paths():
    """Yield one representative path per detection rule."""
    for ext in METADATA_RULES["extension_rules"]:
        yield f"sample{ext}"
    for filename in METADATA_RULES["exact_filename_rules"]:
        yield filename
    for fragment in METADATA_RULES["path_contains_rules"]:
        yield f"{fragment.rstrip('/')}/sample.yml"
    # is_pip_requirements() is the only function rule.
    yield "requirements.txt"
    # The basename-without-extension special case.
    yield "LICENSE"
    for filename in AI_RULES["exact_filename"]:
        yield filename
    for fragment in AI_RULES["path_contains"]:
        # Most fragments are directories; .vscode/mcp.json is a full path.
        yield f"{fragment}sample.md" if fragment.endswith("/") else fragment
    for suffix in AI_RULES["filename_suffix"]:
        yield f"sample{suffix}"


class TestGetTags:
    """get_tags() — the complete tag vocabulary."""

    def test_returns_sorted_list(self):
        tags = get_tags()
        assert isinstance(tags, list)
        assert tags == sorted(tags, key=str.lower)

    def test_is_deduplicated(self):
        tags = get_tags()
        assert len(tags) == len(set(tags))

    def test_includes_implicit_tags(self):
        tags = get_tags()
        for tag in IMPLICIT_TAGS:
            assert tag in tags

    def test_includes_known_tags(self):
        tags = get_tags()
        for expected in ("Claude", "build", "dependencies", "Git", "pipeline"):
            assert expected in tags

    def test_excludes_directory_kind(self):
        # `directory` is synthesised by find_ai_files(all_files=True) and is
        # never returned by get_filename_metatypes(), so it is not searchable
        # and must not appear in the vocabulary.
        assert "directory" not in get_tags()

    def test_no_tag_is_empty(self):
        assert all(tag and tag.strip() for tag in get_tags())


class TestTagDrift:
    """Every tag any rule can produce must be in get_tags()."""

    @pytest.mark.parametrize("path", list(sample_paths()))
    def test_produced_tags_are_in_vocabulary(self, path):
        vocabulary = set(get_tags())
        produced = set(get_filename_metatypes(path))
        assert produced <= vocabulary, (
            f"{path} produced {sorted(produced - vocabulary)}, "
            "which is missing from get_tags()")

    def test_sample_paths_actually_produce_tags(self):
        # Guards the guard: if the synthesis above stopped matching rules,
        # the drift test would pass vacuously.
        assert all(get_filename_metatypes(p) for p in sample_paths())
