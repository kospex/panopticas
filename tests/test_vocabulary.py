"""
Tests for the tag, filetype and language vocabularies.

The drift test is the important one: it synthesises a path for every rule in
METADATA_RULES and AI_RULES and asserts that every tag those paths produce is
present in get_tags(). A future rule whose tags escape the vocabulary fails
here rather than shipping silently.
"""

import pytest

from panopticas import (
    get_filename_metatypes, get_filetypes, get_languages, get_tags)
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
    """
    Every tag any rule can produce must be in get_tags().

    The guarantee is "no tag escapes the vocabulary", not "every branch of
    get_tags() is exercised". Every tag the filename_suffix rules produce is
    also produced by another rule, so deleting that branch from get_tags()
    would not fail these tests. TestEveryTraversalBranch covers that.
    """

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


class TestEveryTraversalBranch:
    """
    get_tags() reads each rule table. A tag only one table can produce must
    reach the vocabulary, so a branch dropped from the traversal fails here
    even when today's rule data happens to repeat its tags elsewhere (#32).
    """

    @pytest.mark.parametrize("table,key", [
        ("extension_rules", ".sentinel-ext"),
        ("exact_filename_rules", "sentinel-exact"),
        ("path_contains_rules", "sentinel-path/"),
    ])
    def test_metadata_rule_table(self, monkeypatch, table, key):
        monkeypatch.setitem(METADATA_RULES[table], key, ["SentinelTag"])
        assert "SentinelTag" in get_tags()

    def test_function_rules(self, monkeypatch):
        monkeypatch.setitem(
            METADATA_RULES, "function_rules",
            METADATA_RULES["function_rules"] + [("sentinel", ["SentinelTag"])])
        assert "SentinelTag" in get_tags()

    @pytest.mark.parametrize("mode,key", [
        ("exact_filename", "sentinel.md"),
        ("path_contains", ".sentinel/"),
        ("filename_suffix", ".sentinel.md"),
    ])
    def test_ai_match_mode(self, monkeypatch, mode, key):
        monkeypatch.setitem(AI_RULES[mode], key, ("SentinelProduct", "prompt"))
        assert "SentinelProduct" in get_tags()


class TestGetFiletypes:
    """get_filetypes() — everything get_language() can return from the tables."""

    def test_returns_sorted_deduplicated_list(self):
        filetypes = get_filetypes()
        assert isinstance(filetypes, list)
        assert filetypes == sorted(filetypes, key=str.lower)
        assert len(filetypes) == len(set(filetypes))

    def test_includes_extension_and_basename_values(self):
        filetypes = get_filetypes()
        assert "Python" in filetypes      # from EXT_FILETYPES
        assert "go.mod" in filetypes      # from LANGUAGE_BY_BASENAME
        assert "PNG" in filetypes

    def test_excludes_the_unknown_sentinel(self):
        # get_language() returns "Unknown" for unrecognised files. It is a
        # sentinel, not a member of the vocabulary.
        assert "Unknown" not in get_filetypes()

    def test_covers_every_table_value(self):
        # A change-detector, not a correctness proof: `expected` is the same
        # expression core.get_filetypes() uses, so a wrong formula (& for |,
        # .keys() for .values()) would appear on both sides and pass. The
        # tests above exercise the real behaviour.
        from panopticas.constants import EXT_FILETYPES, LANGUAGE_BY_BASENAME

        expected = set(EXT_FILETYPES.values()) | set(LANGUAGE_BY_BASENAME.values())
        assert set(get_filetypes()) == expected


class TestLanguageClassification:
    """Every filetype must be explicitly classified — this is the drift guard."""

    def test_classification_is_complete(self):
        from panopticas.constants import (
            LANGUAGE_FILETYPES, NON_LANGUAGE_FILETYPES)

        classified = set(LANGUAGE_FILETYPES) | set(NON_LANGUAGE_FILETYPES)
        unclassified = set(get_filetypes()) - classified
        assert not unclassified, (
            f"unclassified file types: {sorted(unclassified)} — add each to "
            "LANGUAGE_FILETYPES or NON_LANGUAGE_FILETYPES in constants.py")

    def test_no_stale_classifications(self):
        from panopticas.constants import (
            LANGUAGE_FILETYPES, NON_LANGUAGE_FILETYPES)

        classified = set(LANGUAGE_FILETYPES) | set(NON_LANGUAGE_FILETYPES)
        stale = classified - set(get_filetypes())
        assert not stale, f"classified but no longer a file type: {sorted(stale)}"

    def test_sets_do_not_overlap(self):
        from panopticas.constants import (
            LANGUAGE_FILETYPES, NON_LANGUAGE_FILETYPES)

        assert not (set(LANGUAGE_FILETYPES) & set(NON_LANGUAGE_FILETYPES))


class TestGetLanguages:
    """get_languages() — the language subset of get_filetypes()."""

    def test_returns_sorted_deduplicated_list(self):
        languages = get_languages()
        assert isinstance(languages, list)
        assert languages == sorted(languages, key=str.lower)
        assert len(languages) == len(set(languages))

    def test_is_a_subset_of_filetypes(self):
        assert set(get_languages()) <= set(get_filetypes())

    def test_includes_languages(self):
        languages = get_languages()
        for expected in ("Python", "Java", "HTML", "CSS", "JSX", "TSX", "SQL"):
            assert expected in languages

    def test_excludes_non_languages(self):
        # The classification calls most likely to be flipped by accident.
        languages = get_languages()
        for excluded in ("PNG", "JSON", "YAML", "Markdown", "SVG",
                         "ASP.NET", "go.sum", "Text"):
            assert excluded not in languages
            assert excluded in get_filetypes()
