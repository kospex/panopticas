"""
Tests for linter, formatter and type checker config detection.

Covers: LINTER_RULES table integrity, its expansion into METADATA_RULES, the
tags produced for each language's tooling, the filetype resolution of
extensionless config dotfiles, and negative guards for the conventions that
were deliberately rejected.
"""

import pytest

from panopticas import get_filename_metatypes, get_language, get_tags
from panopticas.constants import (
    LINTER_ROLES, LINTER_RULES, METADATA_RULES)


def tags_for(path):
    """Tags as a set — rule order is not part of the contract."""
    return set(get_filename_metatypes(path))


class TestLinterRulesTableIntegrity:
    """The table itself must be well formed."""

    def test_every_role_is_a_known_role(self):
        for tool, spec in LINTER_RULES.items():
            for role in spec["roles"]:
                assert role in LINTER_ROLES, (
                    f"{tool} uses role {role!r}, which is not in LINTER_ROLES")

    def test_every_tool_declares_at_least_one_role(self):
        for tool, spec in LINTER_RULES.items():
            assert spec["roles"], f"{tool} declares no role"

    def test_every_tool_declares_at_least_one_indicator(self):
        for tool, spec in LINTER_RULES.items():
            indicators = (spec.get("config", []) + spec.get("ignore", [])
                          + spec.get("path_contains", [])
                          + spec.get("extensions", []))
            assert indicators, f"{tool} declares no files to match"

    def test_filenames_are_lowercase(self):
        # get_filename_metatypes() lowercases the basename before matching, so
        # an uppercase key could never match.
        for tool, spec in LINTER_RULES.items():
            for filename in spec.get("config", []) + spec.get("ignore", []):
                assert filename == filename.lower(), (
                    f"{tool} key {filename!r} must be lowercase")

    def test_path_fragments_end_with_a_slash(self):
        for tool, spec in LINTER_RULES.items():
            for fragment in spec.get("path_contains", []):
                assert fragment.endswith("/"), (
                    f"{tool} fragment {fragment!r} must end with /")

    def test_no_filename_is_claimed_by_two_tools(self):
        seen = {}
        for tool, spec in LINTER_RULES.items():
            for filename in spec.get("config", []) + spec.get("ignore", []):
                assert filename not in seen, (
                    f"{filename!r} claimed by both {seen.get(filename)} "
                    f"and {tool}")
                seen[filename] = tool

    def test_no_tool_is_both_config_and_ignore_for_one_file(self):
        for tool, spec in LINTER_RULES.items():
            overlap = set(spec.get("config", [])) & set(spec.get("ignore", []))
            assert not overlap, f"{tool}: {sorted(overlap)} is both"


class TestExpansionIntoMetadataRules:
    """LINTER_RULES is expanded into the tables get_filename_metatypes reads."""

    def test_config_filenames_reach_exact_filename_rules(self):
        exact = METADATA_RULES["exact_filename_rules"]
        for tool, spec in LINTER_RULES.items():
            for filename in spec.get("config", []):
                assert filename in exact, f"{tool}: {filename} not expanded"

    def test_path_fragments_reach_path_contains_rules(self):
        contains = METADATA_RULES["path_contains_rules"]
        for tool, spec in LINTER_RULES.items():
            for fragment in spec.get("path_contains", []):
                assert fragment in contains, f"{tool}: {fragment} not expanded"

    def test_extensions_reach_extension_rules(self):
        ext_rules = METADATA_RULES["extension_rules"]
        for tool, spec in LINTER_RULES.items():
            for ext in spec.get("extensions", []):
                assert ext in ext_rules, f"{tool}: {ext} not expanded"

    def test_every_expanded_tag_is_in_the_vocabulary(self):
        vocabulary = set(get_tags())
        for tool, spec in LINTER_RULES.items():
            for filename in spec.get("config", []):
                produced = tags_for(filename)
                assert produced <= vocabulary, (
                    f"{filename} produced {sorted(produced - vocabulary)}")


class TestRoleTags:
    """Every rule carries its role, its tool and config-or-ignore."""

    def test_config_file_is_tagged_config(self):
        assert "config" in tags_for(".eslintrc.json")

    def test_ignore_file_is_tagged_ignore(self):
        assert "ignore" in tags_for(".eslintignore")

    def test_ignore_file_is_not_tagged_config(self):
        assert "config" not in tags_for(".eslintignore")

    def test_formatter_is_distinct_from_linter(self):
        prettier = tags_for(".prettierrc")
        assert "formatter" in prettier
        assert "linter" not in prettier

    def test_typechecker_role(self):
        assert "typechecker" in tags_for("mypy.ini")

    def test_a_tool_can_be_both_linter_and_formatter(self):
        ruff = tags_for("ruff.toml")
        assert {"linter", "formatter"} <= ruff


class TestJavaScriptAndTypeScript:

    def test_eslint_flat_config(self):
        assert {"JavaScript", "TypeScript", "linter", "ESLint", "config"} \
            <= tags_for("eslint.config.js")

    @pytest.mark.parametrize("filename", [
        "eslint.config.mjs", "eslint.config.cjs", "eslint.config.ts",
        "eslint.config.mts", "eslint.config.cts",
    ])
    def test_eslint_flat_config_extensions(self, filename):
        assert "ESLint" in tags_for(filename)

    @pytest.mark.parametrize("filename", [
        ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.yaml",
        ".eslintrc.yml", ".eslintrc.json",
    ])
    def test_eslint_legacy_config(self, filename):
        assert "ESLint" in tags_for(filename)

    def test_eslint_is_recased_from_the_old_lowercase_tag(self):
        # The pre-existing rule tagged `eslint`. Re-cased for consistency with
        # every other tool; kospex matches tags with a case-insensitive LIKE,
        # so this does not break stored queries.
        assert "eslint" not in get_tags()
        assert "ESLint" in get_tags()

    @pytest.mark.parametrize("filename", [
        ".prettierrc", ".prettierrc.json", ".prettierrc.yml",
        ".prettierrc.yaml", ".prettierrc.json5", ".prettierrc.js",
        ".prettierrc.mjs", ".prettierrc.cjs", ".prettierrc.ts",
        ".prettierrc.mts", ".prettierrc.cts", ".prettierrc.toml",
        "prettier.config.js", "prettier.config.mjs", "prettier.config.cjs",
        "prettier.config.ts", "prettier.config.mts", "prettier.config.cts",
    ])
    def test_prettier_config(self, filename):
        assert {"formatter", "Prettier", "config"} <= tags_for(filename)

    def test_prettier_ignore(self):
        assert {"formatter", "Prettier", "ignore"} <= tags_for(".prettierignore")

    def test_stylelint_is_tagged_css_not_javascript(self):
        tags = tags_for(".stylelintrc.json")
        assert {"CSS", "linter", "Stylelint"} <= tags
        assert "JavaScript" not in tags

    def test_stylelint_ignore(self):
        assert {"Stylelint", "ignore"} <= tags_for(".stylelintignore")

    @pytest.mark.parametrize("filename", [
        "biome.json", "biome.jsonc", ".biome.json", ".biome.jsonc",
    ])
    def test_biome_is_linter_and_formatter(self, filename):
        assert {"linter", "formatter", "Biome"} <= tags_for(filename)

    @pytest.mark.parametrize("filename", [
        ".oxlintrc.json", ".oxlintrc.jsonc", "oxlint.config.ts",
        "oxlint.config.mts",
    ])
    def test_oxlint_config(self, filename):
        assert {"linter", "oxlint"} <= tags_for(filename)

    def test_jshint_config_and_ignore(self):
        assert {"JavaScript", "linter", "JSHint", "config"} \
            <= tags_for(".jshintrc")
        assert {"JSHint", "ignore"} <= tags_for(".jshintignore")

    def test_tsconfig_is_a_typechecker_config(self):
        assert {"TypeScript", "typechecker", "config"} <= tags_for("tsconfig.json")

    def test_jsconfig_is_the_javascript_equivalent(self):
        assert {"typechecker", "config"} <= tags_for("jsconfig.json")

    def test_editorconfig_is_language_neutral(self):
        tags = tags_for(".editorconfig")
        assert {"formatter", "EditorConfig", "config"} <= tags
        for language in ("JavaScript", "Python", "C#", "Java"):
            assert language not in tags


class TestPython:

    @pytest.mark.parametrize("filename,tool", [
        ("ruff.toml", "Ruff"),
        (".ruff.toml", "Ruff"),
        (".flake8", "Flake8"),
        ("pylintrc", "Pylint"),
        (".pylintrc", "Pylint"),
        ("pylintrc.toml", "Pylint"),
        (".pylintrc.toml", "Pylint"),
        ("mypy.ini", "mypy"),
        (".mypy.ini", "mypy"),
        ("pyrightconfig.json", "Pyright"),
        (".isort.cfg", "isort"),
        (".style.yapf", "yapf"),
        (".prospector.yaml", "Prospector"),
        (".prospector.yml", "Prospector"),
    ])
    def test_python_tool_config(self, filename, tool):
        assert {"Python", tool, "config"} <= tags_for(filename)

    def test_yapf_ignore(self):
        assert {"yapf", "ignore"} <= tags_for(".yapfignore")


class TestGo:

    @pytest.mark.parametrize("filename", [
        ".golangci.yml", ".golangci.yaml", ".golangci.toml", ".golangci.json",
    ])
    def test_golangci_lint_config(self, filename):
        assert {"Go", "linter", "golangci-lint", "config"} <= tags_for(filename)

    def test_staticcheck_config(self):
        assert {"Go", "linter", "staticcheck", "config"} \
            <= tags_for("staticcheck.conf")


class TestRuby:

    def test_rubocop_is_linter_and_formatter(self):
        assert {"Ruby", "linter", "formatter", "RuboCop", "config"} \
            <= tags_for(".rubocop.yml")

    def test_rubocop_todo_is_an_exclusion_file(self):
        # --auto-gen-config writes it to exclude existing offences, so it is
        # RuboCop's ignore counterpart rather than another config file.
        assert {"RuboCop", "ignore"} <= tags_for(".rubocop_todo.yml")

    def test_standard_config_and_todo(self):
        assert {"Ruby", "Standard", "config"} <= tags_for(".standard.yml")
        assert {"Standard", "ignore"} <= tags_for(".standard_todo.yml")

    def test_reek_config(self):
        assert {"Ruby", "linter", "Reek", "config"} <= tags_for(".reek.yml")

    def test_rufo_is_a_formatter(self):
        assert {"Ruby", "formatter", "Rufo", "config"} <= tags_for(".rufo")

    def test_erb_lint_config(self):
        assert {"Ruby", "linter", "erb_lint", "config"} \
            <= tags_for(".erb_lint.yml")

    def test_steepfile_is_a_typechecker_config(self):
        assert {"Ruby", "typechecker", "Steep", "config"} <= tags_for("Steepfile")

    def test_sorbet_directory_is_matched_by_path(self):
        assert {"Ruby", "typechecker", "Sorbet"} <= tags_for("sorbet/config")


class TestJava:

    @pytest.mark.parametrize("filename", [
        "checkstyle.xml", "google_checks.xml", "sun_checks.xml",
    ])
    def test_checkstyle_config(self, filename):
        assert {"Java", "linter", "Checkstyle", "config"} <= tags_for(filename)

    def test_checkstyle_gradle_convention_path(self):
        # The Gradle Checkstyle plugin documents config/checkstyle/ as the
        # default location.
        assert {"Java", "linter", "Checkstyle"} \
            <= tags_for("config/checkstyle/rules.xml")


class TestGroovy:

    @pytest.mark.parametrize("filename", [
        ".groovylintrc.json", ".groovylintrc.js", ".groovylintrc.yml",
    ])
    def test_npm_groovy_lint_config(self, filename):
        assert {"Groovy", "linter", "npm-groovy-lint", "config"} \
            <= tags_for(filename)


class TestDotNet:

    def test_globalconfig_is_a_roslyn_analyzer_config(self):
        assert {"C#", ".NET", "linter", "Roslyn", "config"} \
            <= tags_for(".globalconfig")

    def test_ruleset_extension_is_matched(self):
        assert {"linter", "Roslyn"} <= tags_for("CodeAnalysis.ruleset")

    @pytest.mark.parametrize("filename", ["stylecop.json", ".stylecop.json"])
    def test_stylecop_config(self, filename):
        assert {"C#", "linter", "StyleCop", "config"} <= tags_for(filename)


class TestSqlFluffNormalisation:
    """The pre-existing SQLFluff rules move into LINTER_RULES."""

    def test_sqlfluff_keeps_its_original_tags(self):
        # Purely additive: every tag the old literal rule produced is retained.
        assert {"SQLFluff", "SQL", "linter"} <= tags_for(".sqlfluff")

    def test_sqlfluff_gains_the_config_role(self):
        assert "config" in tags_for(".sqlfluff")

    def test_sqlfluffignore_keeps_its_original_tags(self):
        assert {"SQLFluff", "ignore"} <= tags_for(".sqlfluffignore")


class TestModuleExtensionFiletypes:
    """.mjs/.cjs/.mts/.cts were missing from EXT_FILETYPES entirely."""

    @pytest.mark.parametrize("filename,expected", [
        ("index.mjs", "JavaScript"),
        ("index.cjs", "JavaScript"),
        ("index.mts", "TypeScript"),
        ("index.cts", "TypeScript"),
    ])
    def test_module_extensions_resolve_to_their_language(self, filename, expected):
        assert get_language(filename, skip_shebang=True) == expected

    def test_they_are_classified_as_languages(self):
        from panopticas import get_languages

        assert "JavaScript" in get_languages()
        assert "TypeScript" in get_languages()


class TestConfigFiletypeResolution:
    """Extensionless config files resolve to a format where one is documented."""

    @pytest.mark.parametrize("filename,expected", [
        # Documented single format -> that format.
        (".editorconfig", "INI"),
        (".flake8", "INI"),
        (".globalconfig", "INI"),
        (".pylintrc", "INI"),
        ("pylintrc", "INI"),
        (".isort.cfg", "INI"),
        (".style.yapf", "INI"),
        (".jshintrc", "JSON"),
        ("staticcheck.conf", "TOML"),
        (".rufo", "Ruby"),
        ("Steepfile", "Ruby"),
        ("CodeAnalysis.ruleset", "XML"),
        # Several accepted formats -> its own name.
        (".eslintrc", "ESLintRC"),
        (".prettierrc", "Prettierrc"),
        (".stylelintrc", "StylelintRC"),
        # Pattern files.
        (".eslintignore", "ESLintIgnore"),
        (".prettierignore", "PrettierIgnore"),
        (".stylelintignore", "StylelintIgnore"),
        (".jshintignore", "JSHintIgnore"),
        (".yapfignore", "YapfIgnore"),
        # Data formats new to the table.
        ("biome.jsonc", "JSONC"),
        (".prettierrc.json5", "JSON5"),
    ])
    def test_filetype(self, filename, expected):
        assert get_language(filename, skip_shebang=True) == expected

    def test_no_linter_config_resolves_to_unknown(self):
        unresolved = []
        for spec in LINTER_RULES.values():
            for filename in spec.get("config", []) + spec.get("ignore", []):
                if get_language(filename, skip_shebang=True) == "Unknown":
                    unresolved.append(filename)
        assert not unresolved, (
            f"no filetype for {sorted(unresolved)} — add an EXT_FILETYPES or "
            "LANGUAGE_BY_BASENAME entry")


class TestRejectedConventions:
    """
    Guards for conventions investigated and deliberately rejected. Each of
    these would be a wrong rule, and a wrong rule mislabels repositories.
    """

    def test_revive_toml_is_not_detected(self):
        # revive auto-discovers only $HOME/revive.toml, a user-level path, not
        # a repository artifact.
        assert "revive" not in tags_for("revive.toml")

    def test_spotbugs_filter_files_are_not_detected(self):
        # SpotBugs filter files are arbitrarily named and passed with
        # -exclude/-include; there is no convention to match.
        assert "SpotBugs" not in tags_for("spotbugs-exclude.xml")

    def test_pmd_rulesets_are_not_detected(self):
        assert "PMD" not in tags_for("ruleset.xml")

    def test_codenarc_rulesets_are_not_detected(self):
        assert "CodeNarc" not in tags_for("codenarc.xml")

    def test_setup_cfg_is_not_tagged_as_a_linter_config(self):
        # setup.cfg really can hold flake8, isort and yapf config, but which
        # tool is inside cannot be known from the path.
        tags = tags_for("setup.cfg")
        assert "linter" not in tags
        assert "Flake8" not in tags

    def test_pyproject_toml_is_not_tagged_as_a_linter_config(self):
        tags = tags_for("pyproject.toml")
        assert "linter" not in tags
        assert "Ruff" not in tags

    def test_tox_ini_is_not_tagged_as_a_linter_config(self):
        assert "linter" not in tags_for("tox.ini")

    def test_black_has_no_dedicated_config_file(self):
        # Black is configured only in pyproject.toml, so it is undetectable.
        assert "Black" not in get_tags()
