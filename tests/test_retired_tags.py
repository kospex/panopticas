"""
Tests for retired tags: get_deprecated_tags() and is_known_tag() (#54).

Stored data outlives the vocabulary. A database synced with an older
panopticas holds tags this version no longer emits, so a consumer needs to
tell a retired tag from one that never existed.
"""

import os

import pytest

from panopticas import get_deprecated_tags, get_tags, is_known_tag
from panopticas.constants import DEPRECATED_TAGS

SNAPSHOT = os.path.join(os.path.dirname(__file__), "data", "tag_snapshot.txt")


def snapshot_tags():
    with open(SNAPSHOT, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


class TestGetDeprecatedTags:

    def test_every_retirement_in_history(self):
        # Reconstructed from every commit that changed tag output; see
        # changes/2026-10-retired-tags.md.
        assert get_deprecated_tags() == {
            "Github": "GitHub",
            "eslint": "ESLint",
            "Claude Code": "Claude",
            "Gemini CLI": "Gemini",
        }

    def test_is_ordered_oldest_first(self):
        assert list(get_deprecated_tags()) == [
            "Github", "eslint", "Claude Code", "Gemini CLI"]

    def test_returns_a_copy(self):
        get_deprecated_tags()["Github"] = "tampered"
        assert get_deprecated_tags()["Github"] == "GitHub"

    def test_no_retired_tag_is_still_current(self):
        assert not set(DEPRECATED_TAGS) & set(get_tags())

    def test_every_replacement_is_a_current_tag(self):
        for retired, replacement in DEPRECATED_TAGS.items():
            assert replacement is None or replacement in get_tags(), (
                f"{retired!r} -> {replacement!r}, which is not a current tag")


class TestIsKnownTag:

    def test_current_tag(self):
        assert is_known_tag("ESLint")

    def test_retired_tag_is_unknown_by_default(self):
        assert not is_known_tag("Claude Code")

    def test_retired_tag_is_known_when_asked(self):
        assert is_known_tag("Claude Code", check_deprecated=True)

    def test_current_tag_is_known_either_way(self):
        assert is_known_tag("Claude", check_deprecated=True)

    def test_match_is_case_sensitive(self):
        # Case-sensitive databases treat these as different tags, so they
        # are. A recase is listed in DEPRECATED_TAGS instead.
        assert not is_known_tag("esLint")
        assert not is_known_tag("esLint", check_deprecated=True)

    def test_recased_spelling_is_known_through_the_retired_list(self):
        assert not is_known_tag("eslint")
        assert is_known_tag("eslint", check_deprecated=True)
        assert is_known_tag("Github", check_deprecated=True)

    def test_never_a_tag(self):
        assert not is_known_tag("NotATag", check_deprecated=True)
        assert not is_known_tag("", check_deprecated=True)

    def test_flag_is_keyword_only(self):
        with pytest.raises(TypeError):
            is_known_tag("eslint", True)


class TestRetirementsAreRecorded:
    """
    tests/data/tag_snapshot.txt holds every tag panopticas has shipped that
    is not retired. A tag leaving get_tags() must be added to DEPRECATED_TAGS,
    which is how Github -> GitHub went unrecorded for a year.
    """

    def test_no_tag_disappears_unrecorded(self):
        missing = snapshot_tags() - set(get_tags()) - set(DEPRECATED_TAGS)
        assert not missing, (
            f"{sorted(missing)} no longer emitted. Add each to DEPRECATED_TAGS "
            "in constants.py with its replacement (or None), document it in "
            "docs/retired-tags.md, then remove it from the snapshot.")

    def test_snapshot_includes_every_current_tag(self):
        new = set(get_tags()) - snapshot_tags()
        assert not new, (
            f"{sorted(new)} not in tests/data/tag_snapshot.txt. Add them so a "
            "later removal is caught.")

    def test_snapshot_holds_no_retired_tag(self):
        assert not snapshot_tags() & set(DEPRECATED_TAGS)
