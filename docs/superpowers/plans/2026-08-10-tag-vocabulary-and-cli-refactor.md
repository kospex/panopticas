# Tag Vocabulary, JSON Output and Rich Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `get_tags()`, `get_filetypes()` and `get_languages()` so a consumer can ask what vocabulary panopticas uses; expose them as CLI commands; add `--json` to every command; and replace `prettytable` with `rich`.

**Architecture:** The tag vocabulary is *derived* by traversing `METADATA_RULES` and `AI_RULES`, so it cannot drift when a detection rule is added. The language subset cannot be derived, so it is an explicit pair of sets guarded by a completeness test. CLI changes are additive except the table library swap, which is the last phase.

**Tech Stack:** Python 3.12+, Click 8.3.1+, rich 14.0.0+, pathspec, pytest.

Design spec: [`docs/superpowers/specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md`](../specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md)

## Global Constraints

- **Run tests with `uv run --with pytest pytest -v`.** A bare `pytest` fails in this environment — the venv is broken.
- **Never run `twine upload`.** PyPI upload is a deliberate manual gate; hand the built artifacts to the maintainer.
- **Stage by path, never `git add -A` or `git add .`** — `uv.lock` and `.safety-project.ini` are untracked on purpose.
- **Python 3.12+**, matching `requires-python` in `pyproject.toml`.
- Constants and mappings go in `constants.py`; analysis logic in `core.py`; CLI in `cli.py`.
- Every new public function must be added to **both** the `from .core import (...)` block and the `__all__` list in `src/panopticas/__init__.py`.
- Sort every vocabulary with `key=str.lower`. Case-sensitive `sorted()` puts `ZIP` before `binary`, which reads as broken.
- `rich>=14.0.0` is added in Phase 1 (Task 5) because the vocabulary commands need it. `prettytable` is removed in Phase 3 (Task 14). Both dependencies coexist between those tasks — this is expected, not an error.
- Work happens on branch `feature/tag-vocabulary-cli-refactor`, already created.

## Reference values

Used by several tasks. Copy exactly.

**The 32 languages:**
```
C, C Header, C#, C++, CSS, Dockerfile, Go, Groovy, Groovy Server Pages, HTML,
Java, JavaScript, JSX, Jupyter Notebook, Kotlin, Makefile, Objective-C, Perl,
PHP, PowerShell, Python, R, Ruby, Rust, Scala, Shell, SQL, Swift, Terraform,
TSX, TypeScript, Vue
```

**The 44 non-languages**, grouped:
```
Binary/media (11):  DLL, Excel, Executable, GIF, ICO, JPEG, Java Archive,
                    Java Class, PDF, PNG, ZIP
Data/config (8):    CSV, INI, JSON, Properties, TOML, TSV, XML, YAML
Prose (3):          Markdown, ReStructuredText, Text
Named files (14):   CNAME, CODEOWNERS, Dockerignore, GitAttributes, Gitignore,
                    GitLeaksIgnore, Lock, Mailmap, nvmrc, python-version,
                    go.mod, go.sum, SQLFluff, SQLFluffIgnore
Framework/tool (8): ASP.NET, ASP.NET Global, ASP.NET User Control,
                    Apache JMeter, C# Project, SARIF, SVG,
                    Visual Studio Solution
```

Counts at time of writing: **85 tags, 76 filetypes, 32 languages**. Tests must not hardcode these totals — new rules change them legitimately. Assert membership and invariants instead.

---

# Phase 1 — Vocabulary functions and commands

## Task 1: Replace the implicit tag literals with constants

`get_filename_metatypes()` emits `"AI"` and `"license"` as bare string literals. `get_tags()` needs them too, and restating them in a second place would be exactly the drift this feature exists to prevent. Move them to `constants.py` first, so there is one source of truth before anything reads it.

**Files:**
- Modify: `src/panopticas/constants.py` (after the `VERSION` block, before `EXT_FILETYPES`)
- Modify: `src/panopticas/core.py:100-109`
- Test: `tests/test_panopticas.py`

**Interfaces:**
- Consumes: nothing
- Produces: `constants.AI_TAG` (`str`), `constants.LICENSE_TAG` (`str`), `constants.IMPLICIT_TAGS` (`tuple[str, str]`)

- [ ] **Step 1: Write the failing test**

Add to the end of `tests/test_panopticas.py`:

```python
class TestImplicitTags:
    """The tags get_filename_metatypes() emits without a rule table entry."""

    def test_license_tag_still_applied(self):
        assert "license" in get_filename_metatypes("LICENSE")
        assert "license" in get_filename_metatypes("license.md")

    def test_ai_tag_still_applied(self):
        assert "AI" in get_filename_metatypes("CLAUDE.md")

    def test_implicit_tags_exported(self):
        from panopticas.constants import AI_TAG, IMPLICIT_TAGS, LICENSE_TAG

        assert AI_TAG == "AI"
        assert LICENSE_TAG == "license"
        assert set(IMPLICIT_TAGS) == {"AI", "license"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest pytest tests/test_panopticas.py::TestImplicitTags -v`
Expected: `test_implicit_tags_exported` FAILS with `ImportError: cannot import name 'AI_TAG'`. The other two pass already — they guard against breaking current behaviour in Step 3.

- [ ] **Step 3: Add the constants**

In `src/panopticas/constants.py`, immediately after the `VERSION` try/except block:

```python
# Tags emitted directly by get_filename_metatypes() rather than by a rule
# table. "AI" prefixes every AI artifact's tags. "license" is matched on the
# basename-without-extension (LICENSE, license.md, license.txt) so it cannot
# be expressed as an exact_filename rule. get_tags() reads IMPLICIT_TAGS so
# these two are not restated anywhere.
AI_TAG = "AI"
LICENSE_TAG = "license"
IMPLICIT_TAGS = (AI_TAG, LICENSE_TAG)
```

- [ ] **Step 4: Use them in core.py**

In `src/panopticas/core.py`, change the import on line 7:

```python
from .constants import (
    AI_RULES,
    AI_TAG,
    EXT_FILETYPES,
    LANGUAGE_BY_BASENAME,
    LICENSE_TAG,
    METADATA_RULES,
)
```

Then replace the two literals in `get_filename_metatypes()`:

```python
    # Special case for license files
    if file_no_ext == "license":
        tags.append(LICENSE_TAG)

    # AI coding agent artifacts. Runs last so it appends to — rather than
    # competes with — the rules above; .github/copilot-instructions.md
    # keeps its GitHub/Git tags and gains the AI ones.
    ai_metadata = get_ai_metadata(file_path)
    if ai_metadata:
        tags.extend([AI_TAG, ai_metadata["product"], ai_metadata["kind"]])
```

- [ ] **Step 5: Run the full suite**

Run: `uv run --with pytest pytest -v`
Expected: PASS. This is a pure refactor — any failure means behaviour changed.

- [ ] **Step 6: Commit**

```bash
git add src/panopticas/constants.py src/panopticas/core.py tests/test_panopticas.py
git commit -m "Move implicit AI and license tags into constants"
```

---

## Task 2: `get_tags()` and the drift test

The drift test is the load-bearing part of this whole feature. Without it, `get_tags()` is a claim rather than a contract.

**Files:**
- Modify: `src/panopticas/core.py` (add after `get_filename_metatypes()`)
- Modify: `src/panopticas/__init__.py`
- Create: `tests/test_vocabulary.py`

**Interfaces:**
- Consumes: `constants.IMPLICIT_TAGS` from Task 1
- Produces: `core.get_tags() -> list[str]`, exported as `panopticas.get_tags`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_vocabulary.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_vocabulary.py -v`
Expected: collection error — `ImportError: cannot import name 'get_tags' from 'panopticas'`.

- [ ] **Step 3: Implement `get_tags()`**

In `src/panopticas/core.py`, after `get_filename_metatypes()`. Add `IMPLICIT_TAGS` to the `from .constants import (...)` block:

```python
def get_tags():
    """
    Return every tag get_filename_metatypes() can emit, sorted.

    Derived by traversing METADATA_RULES and AI_RULES rather than maintained
    by hand, so a new detection rule joins the vocabulary the moment it is
    added.

    AI kinds come from the values used in AI_RULES, not from
    AI_ARTIFACT_KINDS. The two differ by one: `directory` is synthesised
    inside find_ai_files(all_files=True) and never reaches a file's tags, so
    including it would offer a tag nothing can be searched by.
    """
    tags = set(IMPLICIT_TAGS)

    for rule_set in ("extension_rules", "exact_filename_rules",
                     "path_contains_rules"):
        for tag_list in METADATA_RULES[rule_set].values():
            tags.update(tag_list)

    for _func_name, tag_list in METADATA_RULES["function_rules"]:
        tags.update(tag_list)

    for match_mode in AI_RULES.values():
        for product, kind in match_mode.values():
            tags.update((product, kind))

    return sorted(tags, key=str.lower)
```

- [ ] **Step 4: Export it**

In `src/panopticas/__init__.py`, add `get_tags,` to the `from .core import (...)` block and `'get_tags',` to `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_vocabulary.py -v`
Expected: PASS, including one parametrised case per rule.

- [ ] **Step 6: Sanity-check the output by hand**

Run: `uv run python -c "import panopticas; t=panopticas.get_tags(); print(len(t)); print(t)"`
Expected: 85 tags, alphabetical ignoring case, `Claude` and `build` present, `directory` absent.

- [ ] **Step 7: Commit**

```bash
git add src/panopticas/core.py src/panopticas/__init__.py tests/test_vocabulary.py
git commit -m "Add get_tags() with a drift test over every detection rule"
```

---

## Task 3: `get_filetypes()`

**Files:**
- Modify: `src/panopticas/core.py` (after `get_tags()`)
- Modify: `src/panopticas/__init__.py`
- Modify: `tests/test_vocabulary.py`

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces: `core.get_filetypes() -> list[str]`, exported as `panopticas.get_filetypes`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_vocabulary.py`, and add `get_filetypes` to the `from panopticas import ...` line at the top:

```python
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
        from panopticas.constants import EXT_FILETYPES, LANGUAGE_BY_BASENAME

        expected = set(EXT_FILETYPES.values()) | set(LANGUAGE_BY_BASENAME.values())
        assert set(get_filetypes()) == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --with pytest pytest tests/test_vocabulary.py::TestGetFiletypes -v`
Expected: collection error — `cannot import name 'get_filetypes'`.

- [ ] **Step 3: Implement it**

In `src/panopticas/core.py`, after `get_tags()`:

```python
def get_filetypes():
    """
    Return every file type get_language() can return from the lookup tables,
    sorted.

    Two caveats. Shebang detection can return an interpreter name that is not
    in this list (`bash`, `awk`), because it reads the file rather than a
    table. And UNKNOWN ("Unknown") is a sentinel for unrecognised files, not a
    member of the vocabulary.
    """
    filetypes = set(EXT_FILETYPES.values()) | set(LANGUAGE_BY_BASENAME.values())
    return sorted(filetypes, key=str.lower)
```

- [ ] **Step 4: Export it**

Add `get_filetypes,` to the import block and `'get_filetypes',` to `__all__` in `src/panopticas/__init__.py`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_vocabulary.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/panopticas/core.py src/panopticas/__init__.py tests/test_vocabulary.py
git commit -m "Add get_filetypes() for the full file type vocabulary"
```

---

## Task 4: Language classification and `get_languages()`

Both sets are required. An exclusion list alone cannot be complete — a new entry such as `.webp` → `WebP` would default to *language* simply by not appearing in the exclusions, which is the exact drift the completeness test exists to catch.

**Files:**
- Modify: `src/panopticas/constants.py` (after `LANGUAGE_BY_BASENAME`)
- Modify: `src/panopticas/core.py` (after `get_filetypes()`)
- Modify: `src/panopticas/__init__.py`
- Modify: `tests/test_vocabulary.py`

**Interfaces:**
- Consumes: `core.get_filetypes()` from Task 3 (for the completeness test only)
- Produces: `constants.LANGUAGE_FILETYPES` (`frozenset[str]`), `constants.NON_LANGUAGE_FILETYPES` (`frozenset[str]`), `core.get_languages() -> list[str]`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_vocabulary.py`, adding `get_languages` to the `from panopticas import ...` line:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_vocabulary.py -v`
Expected: collection error — `cannot import name 'get_languages'`.

- [ ] **Step 3: Add the classification to constants.py**

In `src/panopticas/constants.py`, after `LANGUAGE_BY_BASENAME`:

```python
# Classification of every value in EXT_FILETYPES and LANGUAGE_BY_BASENAME as
# a language or not. get_languages() returns the first set.
#
# The principle: a language expresses behaviour or presentation. Excluded are
# data and prose formats, binaries, named single-purpose files that are a
# filename convention rather than a format, and framework artifacts whose
# actual language is something else (the code in a .aspx file is C# or
# Visual Basic).
#
# Both sets are required, and a test asserts they cover every value exactly
# once. An exclusion list alone would silently classify a newly added file
# type as a language.
#
# This deliberately diverges from GitHub Linguist on three values, which is
# the closest available benchmark. GitHub's language bar counts only
# Linguist's `programming` and `markup` types, so its `data` and `prose`
# languages (JSON, YAML, Markdown, reStructuredText) are excluded there too.
# See docs/superpowers/specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md
LANGUAGE_FILETYPES = frozenset({
    "C",
    "C Header",
    "C#",
    "C++",
    "CSS",
    "Dockerfile",
    "Go",
    "Groovy",
    "Groovy Server Pages",
    "HTML",
    "Java",
    "JavaScript",
    "JSX",
    "Jupyter Notebook",
    "Kotlin",
    "Makefile",
    "Objective-C",
    "Perl",
    "PHP",
    "PowerShell",
    "Python",
    "R",
    "Ruby",
    "Rust",
    "Scala",
    "Shell",
    "SQL",  # Linguist types SQL as `data`; excluding it would read as a bug.
    "Swift",
    "Terraform",
    "TSX",
    "TypeScript",
    "Vue",
})

NON_LANGUAGE_FILETYPES = frozenset({
    # Binary and media formats
    "DLL",
    "Excel",
    "Executable",
    "GIF",
    "ICO",
    "JPEG",
    "Java Archive",
    "Java Class",
    "PDF",
    "PNG",
    "ZIP",
    # Data and config formats — carry data, not behaviour
    "CSV",
    "INI",
    "JSON",
    "Properties",
    "TOML",
    "TSV",
    "XML",
    "YAML",
    # Prose formats
    "Markdown",
    "ReStructuredText",
    "Text",
    # Named single-purpose files — a filename convention, not a format
    "CNAME",
    "CODEOWNERS",
    "Dockerignore",
    "GitAttributes",
    "Gitignore",
    "GitLeaksIgnore",
    "Lock",
    "Mailmap",
    "nvmrc",
    "python-version",
    "go.mod",
    "go.sum",
    "SQLFluff",
    "SQLFluffIgnore",
    # Framework and tool artifacts — the real language is something else
    "ASP.NET",
    "ASP.NET Global",
    "ASP.NET User Control",
    "Apache JMeter",
    "C# Project",
    "SARIF",
    "SVG",
    "Visual Studio Solution",
})
```

- [ ] **Step 4: Implement `get_languages()`**

In `src/panopticas/core.py`, after `get_filetypes()`. Add `LANGUAGE_FILETYPES` to the `from .constants import (...)` block:

```python
def get_languages():
    """
    Return the programming and presentation languages panopticas recognises,
    sorted.

    A subset of get_filetypes(). Data formats (JSON, YAML, XML), prose
    formats (Markdown), binaries (PNG, ZIP) and named config files
    (.gitignore, go.sum) are file types but not languages.

    The classification is explicit rather than derived — nothing in the data
    says whether PNG is a language — and a test asserts every file type is
    classified, so a newly added extension cannot slip in unclassified.
    """
    return sorted(LANGUAGE_FILETYPES, key=str.lower)
```

- [ ] **Step 5: Export it**

Add `get_languages,` to the import block and `'get_languages',` to `__all__` in `src/panopticas/__init__.py`.

- [ ] **Step 6: Run the full suite**

Run: `uv run --with pytest pytest -v`
Expected: PASS. If `test_classification_is_complete` fails, the failure message names the unclassified values — add each to the correct set rather than adjusting the test.

- [ ] **Step 7: Verify the counts by hand**

Run:
```bash
uv run python -c "
import panopticas as p
print('filetypes', len(p.get_filetypes()))
print('languages', len(p.get_languages()))
print(p.get_languages())"
```
Expected: 76 filetypes, 32 languages.

- [ ] **Step 8: Commit**

```bash
git add src/panopticas/constants.py src/panopticas/core.py src/panopticas/__init__.py tests/test_vocabulary.py
git commit -m "Add get_languages() with an enforced filetype classification"
```

---

## Task 5: The three CLI commands

Adds `rich` as a dependency. `prettytable` stays until Task 14.

**Files:**
- Modify: `pyproject.toml:10-14`
- Modify: `requirements.txt`
- Modify: `src/panopticas/cli.py` (imports at top; new commands after `assess`)
- Create: `tests/test_cli_vocabulary.py`

**Interfaces:**
- Consumes: `core.get_tags()`, `core.get_filetypes()`, `core.get_languages()`
- Produces: CLI commands `tags`, `languages`, `filetypes`; module-level `cli.console` (a `rich.console.Console`) reused by Phase 3

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cli_vocabulary.py`:

```python
"""Tests for the tags, languages and filetypes CLI commands."""

from click.testing import CliRunner

from panopticas import get_filetypes, get_languages, get_tags
from panopticas.cli import cli


class TestVocabularyCommands:
    """Each command prints its vocabulary and a count."""

    def test_tags_lists_every_tag(self):
        result = CliRunner().invoke(cli, ["tags"])
        assert result.exit_code == 0
        for tag in get_tags():
            assert tag in result.output

    def test_tags_reports_the_count(self):
        result = CliRunner().invoke(cli, ["tags"])
        assert f"{len(get_tags())} tags" in result.output

    def test_languages_lists_every_language(self):
        result = CliRunner().invoke(cli, ["languages"])
        assert result.exit_code == 0
        for language in get_languages():
            assert language in result.output

    def test_filetypes_lists_every_filetype(self):
        result = CliRunner().invoke(cli, ["filetypes"])
        assert result.exit_code == 0
        for filetype in get_filetypes():
            assert filetype in result.output

    def test_languages_omits_non_languages(self):
        result = CliRunner().invoke(cli, ["languages"])
        assert "PNG" not in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_cli_vocabulary.py -v`
Expected: FAIL — exit code 2, `No such command 'tags'`.

- [ ] **Step 3: Add the rich dependency**

In `pyproject.toml`, add to `dependencies` (keep `prettytable` for now):

```toml
dependencies = [
    "Click>=8.3.1",
    "prettytable>=3.17.0",
    "pathspec>=0.12.1",
    "rich>=14.0.0",
]
```

In `requirements.txt`, add the pinned lines:

```
markdown-it-py==4.0.0
mdurl==0.1.2
pygments==2.20.0
rich==14.2.0
```

Then confirm the real resolved versions and correct the file if they differ:

```bash
uv run --with rich python -c "
import importlib.metadata as m
for p in ('rich','pygments','markdown-it-py','mdurl'):
    print(p, m.version(p))"
```

- [ ] **Step 4: Add the console and commands to cli.py**

At the top of `src/panopticas/cli.py`, below the existing imports:

```python
from rich.columns import Columns
from rich.console import Console

# Shared console for all rich output.
console = Console()
```

After the `assess` command, add:

```python
def print_vocabulary(values, noun):
    """Print a vocabulary as a column grid with a count beneath."""
    console.print()
    console.print(Columns(values, padding=(0, 2), equal=True))
    console.print(f"\n{len(values)} {noun}\n")


@cli.command("tags")
def tags():
    """Show every tag panopticas can assign to a file."""
    print_vocabulary(core.get_tags(), "tags")


@cli.command("languages")
def languages():
    """Show every language panopticas recognises."""
    print_vocabulary(core.get_languages(), "languages")


@cli.command("filetypes")
def filetypes():
    """Show every file type panopticas recognises, languages or not."""
    print_vocabulary(core.get_filetypes(), "filetypes")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_cli_vocabulary.py -v`
Expected: PASS.

If a test fails because a long value wrapped mid-word, rich sized the columns to the terminal. `CliRunner` reports a width of 80. Widen the console for tests by constructing it as `Console(width=None, soft_wrap=False)`, or assert on `result.output` with whitespace collapsed. Do not shorten the vocabulary values to fit.

- [ ] **Step 6: Look at the real output**

Run: `uv run panopticas tags` and `uv run panopticas languages`
Expected: a readable multi-column grid, count beneath. Check it still reads well in a narrow terminal.

- [ ] **Step 7: Run the full suite and commit**

```bash
uv run --with pytest pytest -v
git add pyproject.toml requirements.txt src/panopticas/cli.py tests/test_cli_vocabulary.py
git commit -m "Add tags, languages and filetypes CLI commands"
```

---

# Phase 2 — JSON output and path validation

## Task 6: JSON helpers and `--json` on the vocabulary commands

Establishes the two helpers every later JSON task reuses.

**Files:**
- Modify: `src/panopticas/cli.py`
- Modify: `tests/test_cli_vocabulary.py`

**Interfaces:**
- Consumes: `cli.print_vocabulary` from Task 5
- Produces: `cli.emit_json(payload: dict) -> None`, `cli.banner(message: str, as_json: bool) -> None`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_cli_vocabulary.py`, adding `import json` at the top:

```python
class TestVocabularyJson:
    """--json and -json produce a parseable document."""

    def test_tags_json_shape(self):
        result = CliRunner().invoke(cli, ["tags", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["tags"] == get_tags()
        assert payload["count"] == len(get_tags())

    def test_languages_json_shape(self):
        payload = json.loads(CliRunner().invoke(cli, ["languages", "--json"]).output)
        assert payload["languages"] == get_languages()
        assert payload["count"] == len(get_languages())

    def test_filetypes_json_shape(self):
        payload = json.loads(CliRunner().invoke(cli, ["filetypes", "--json"]).output)
        assert payload["filetypes"] == get_filetypes()
        assert payload["count"] == len(get_filetypes())

    def test_single_dash_json_is_identical(self):
        runner = CliRunner()
        assert (runner.invoke(cli, ["tags", "-json"]).output
                == runner.invoke(cli, ["tags", "--json"]).output)

    def test_top_level_is_an_object(self):
        # Never a bare array — fields can then be added without breaking
        # existing parsers.
        payload = json.loads(CliRunner().invoke(cli, ["tags", "--json"]).output)
        assert isinstance(payload, dict)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_cli_vocabulary.py::TestVocabularyJson -v`
Expected: FAIL — exit code 2, `No such option: --json`.

- [ ] **Step 3: Add the helpers**

In `src/panopticas/cli.py`, add `import json` at the top. Then add this **immediately after the `console = Console()` line, above the `cli` group and every command**:

```python
# Both spellings are accepted. The repository already mixes single- and
# double-dash long options, so neither is "wrong" to type.
#
# This must be defined before any command, not beside them: it is applied as
# a decorator, which evaluates when the module loads, so a definition further
# down the file raises NameError on import.
json_option = click.option(
    '--json', '-json', 'as_json', is_flag=True, default=False,
    help="Output as JSON.")
```

Then place these two next to `print_vocabulary` — both are called at runtime, so their position does not matter:

```python
def emit_json(payload):
    """
    Write a JSON document to stdout and nothing else.

    Everything a command would normally print as chatter goes to stderr in
    JSON mode (see banner()), so stdout stays pipeable into jq or a parser.
    """
    click.echo(json.dumps(payload, indent=2))


def banner(message, as_json):
    """
    Print progress chatter, routed to stderr when JSON is being emitted so it
    cannot corrupt the document on stdout.

    Sanitised because callers interpolate a path into the message — an
    argv-supplied directory could otherwise carry terminal control sequences.
    The literal parts contain no control characters, so sanitising the whole
    message is safe and means no call site can forget. Rich markup needs no
    handling here: click.echo() does not parse it.
    """
    click.echo(sanitise_for_display(message), err=as_json)
```

`sanitise_for_display` is defined further down `cli.py` than the commands that call it. That is fine — Python resolves module globals at call time, not at definition time.

- [ ] **Step 4: Add the flag to the three commands**

Replace the three vocabulary commands with:

```python
@cli.command("tags")
@json_option
def tags(as_json):
    """Show every tag panopticas can assign to a file."""
    values = core.get_tags()
    if as_json:
        emit_json({"tags": values, "count": len(values)})
    else:
        print_vocabulary(values, "tags")


@cli.command("languages")
@json_option
def languages(as_json):
    """Show every language panopticas recognises."""
    values = core.get_languages()
    if as_json:
        emit_json({"languages": values, "count": len(values)})
    else:
        print_vocabulary(values, "languages")


@cli.command("filetypes")
@json_option
def filetypes(as_json):
    """Show every file type panopticas recognises, languages or not."""
    values = core.get_filetypes()
    if as_json:
        emit_json({"filetypes": values, "count": len(values)})
    else:
        print_vocabulary(values, "filetypes")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_cli_vocabulary.py -v`
Expected: PASS.

- [ ] **Step 6: Verify it pipes**

Run: `uv run panopticas tags --json | python -m json.tool > /dev/null && echo OK`
Expected: `OK` — proves stdout carries only the document.

- [ ] **Step 7: Commit**

```bash
git add src/panopticas/cli.py tests/test_cli_vocabulary.py
git commit -m "Add --json to the vocabulary commands"
```

---

## Task 7: `--json` for `assess`

**Files:**
- Modify: `src/panopticas/cli.py:29-114`
- Create: `tests/test_cli_json.py`

**Interfaces:**
- Consumes: `cli.emit_json`, `cli.banner`, `cli.json_option` from Task 6
- Produces: no new symbols

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cli_json.py`:

```python
"""Tests for --json output on the file-scanning commands."""

import json
import os

from click.testing import CliRunner

from panopticas.cli import cli

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "tests")


class TestAssessJson:
    """assess --json returns one record per file."""

    def test_documents_every_file(self):
        result = CliRunner().invoke(cli, ["assess", FIXTURES_DIR, "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["directory"] == FIXTURES_DIR
        assert payload["count"] == len(payload["files"])
        assert payload["files"]

    def test_meta_is_a_list_not_a_joined_string(self):
        payload = json.loads(
            CliRunner().invoke(cli, ["assess", FIXTURES_DIR, "--json"]).output)
        for record in payload["files"]:
            assert isinstance(record["meta"], list)
            assert set(record) >= {"path", "language", "meta"}

    def test_lines_absent_without_the_flag(self):
        payload = json.loads(
            CliRunner().invoke(cli, ["assess", FIXTURES_DIR, "--json"]).output)
        assert "total_lines" not in payload
        assert all("lines" not in r for r in payload["files"])

    def test_lines_present_with_the_flag(self):
        payload = json.loads(
            CliRunner().invoke(
                cli, ["assess", FIXTURES_DIR, "--lines", "--json"]).output)
        assert isinstance(payload["total_lines"], int)
        assert all("lines" in r for r in payload["files"])

    def test_binary_line_count_is_null(self):
        # count_lines() returns "N/A" for undecodable files; JSON says null.
        payload = json.loads(
            CliRunner().invoke(
                cli, ["assess", FIXTURES_DIR, "--lines", "--json"]).output)
        for record in payload["files"]:
            assert record["lines"] is None or isinstance(record["lines"], int)

    def test_stdout_is_only_the_document(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["assess", FIXTURES_DIR, "--json"], catch_exceptions=False)
        json.loads(result.output)  # raises if chatter leaked onto stdout
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_cli_json.py::TestAssessJson -v`
Expected: FAIL — `No such option: --json`.

- [ ] **Step 3: Rewrite the assess command**

Replace the whole `assess` function in `src/panopticas/cli.py` with:

```python
@cli.command("assess")
@click.option('-unknown', is_flag=True, default=False, help="Show only files with an unknown language type.")
@click.option('--lines', is_flag=True, default=False, help="Include line count for each file.")
@json_option
@click.argument('directory', required=False, type=click.Path(exists=True))
def assess(directory, unknown, lines, as_json):
    """Assess a directory."""
    if not as_json:
        click.echo()
    if directory:
        banner(f'Assessing directory: {directory}', as_json)
    else:
        banner('Assessing current directory.', as_json)
        directory = "."

    if lines:
        files = core.identify_files_with_metrics(directory)
    else:
        files = core.identify_files(directory)

    records = []
    for file, file_info in files.items():
        file_type = file_info['type'] if lines else file_info
        if unknown and file_type is not None:
            continue
        record = {
            "path": file,
            "language": file_type,
            "meta": core.get_filename_metatypes(file),
        }
        if lines:
            line_count = file_info['lines']
            # count_lines() yields "N/A" for binaries; JSON says null.
            record["lines"] = line_count if isinstance(line_count, int) else None
        records.append(record)

    if as_json:
        payload = {
            "directory": directory,
            "count": len(records),
            "files": records,
        }
        if lines:
            payload["total_lines"] = sum(
                r["lines"] for r in records if r["lines"] is not None)
        emit_json(payload)
        return

    banner(f'Found {len(files)} files.\n', as_json)
    table = PrettyTable()

    if lines:
        table.field_names = ["File", "Language", "Meta", "Lines"]
        table.align["Lines"] = "r"
    else:
        table.field_names = ["File", "Language", "Meta"]

    table.align["File"] = "l"
    table.align["Language"] = "l"
    table.align["Meta"] = "l"

    for record in records:
        row = [record["path"], record["language"], ", ".join(record["meta"])]
        if lines:
            row.append(record["lines"] if record["lines"] is not None else "N/A")
        table.add_row(row)

    print(table, "\n")

    total_files = len(records)
    if lines:
        counted = [r["lines"] for r in records if r["lines"] is not None]
        excluded = total_files - len(counted)
        if excluded:
            print(f"Total files: {total_files}, Total # of Lines: {sum(counted):,} "
                  f"({excluded} files excluded - binary/N/A)")
        else:
            print(f"Total files: {total_files}, Total # of Lines: {sum(counted):,}")
    else:
        print(f"Total files: {total_files}")

    print()
```

Note the behaviour change this consolidates: previously `-unknown` filtered rows but the totals still counted every file. Both paths now report the rows actually shown.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_cli_json.py -v`
Expected: PASS.

- [ ] **Step 5: Verify the human output is unchanged**

Run: `uv run panopticas assess src/tests` and `uv run panopticas assess src/tests --lines`
Expected: the same table as before this task, and totals that match the row count.

- [ ] **Step 6: Run the full suite and commit**

```bash
uv run --with pytest pytest -v
git add src/panopticas/cli.py tests/test_cli_json.py
git commit -m "Add --json to assess"
```

---

## Task 8: `--json` for `ai`

**Files:**
- Modify: `src/panopticas/cli.py` (the `ai` command)
- Modify: `tests/test_cli_json.py`

**Interfaces:**
- Consumes: `cli.emit_json`, `cli.banner`, `cli.json_option`
- Produces: no new symbols

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_cli_json.py`:

```python
class TestAiJson:
    """ai --json returns one record per AI artifact."""

    def test_documents_paths_and_products(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("guidance")
        (tmp_path / ".cursorrules").write_text("rules")

        result = CliRunner().invoke(cli, ["ai", str(tmp_path), "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)

        assert payload["count"] == 2
        assert payload["products"] == {"Claude": 1, "Cursor": 1}
        by_path = {r["path"]: r for r in payload["paths"]}
        assert by_path["CLAUDE.md"]["product"] == "Claude"
        assert by_path["CLAUDE.md"]["kind"] == "instructions"

    def test_empty_directory_is_still_an_object(self, tmp_path):
        payload = json.loads(
            CliRunner().invoke(cli, ["ai", str(tmp_path), "--json"]).output)
        assert payload["count"] == 0
        assert payload["paths"] == []
        assert payload["products"] == {}

    def test_paths_are_not_sanitised_in_json(self, tmp_path):
        # JSON escaping already neutralises control characters, and a
        # consumer needs the real path to open the file.
        (tmp_path / "[bold]CLAUDE.md").write_text("x")
        payload = json.loads(
            CliRunner().invoke(cli, ["ai", str(tmp_path), "--json"]).output)
        assert any(r["path"] == "[bold]CLAUDE.md" for r in payload["paths"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_cli_json.py::TestAiJson -v`
Expected: FAIL — `No such option: --json`.

- [ ] **Step 3: Update the ai command**

Replace the body of `ai` in `src/panopticas/cli.py` with:

```python
@cli.command("ai")
@click.option('--all-files', is_flag=True, default=False,
              help="Include gitignored files and bare AI directories.")
@json_option
@click.argument('directory', required=False,
                 type=click.Path(exists=True, file_okay=False, dir_okay=True))
def ai(directory, all_files, as_json):
    """Find AI coding agent files and directories."""
    if not as_json:
        click.echo()
    if directory:
        banner(f'Assessing directory: {directory}', as_json)
    else:
        banner('Assessing current directory.', as_json)
        directory = "."
    if not as_json:
        click.echo()

    ai_files = core.find_ai_files(directory, all_files=all_files)

    # Most-used product first, then alphabetical.
    counts = {}
    for metadata in ai_files.values():
        counts[metadata["product"]] = counts.get(metadata["product"], 0) + 1
    counts = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))

    if as_json:
        emit_json({
            "directory": directory,
            "count": len(ai_files),
            "products": counts,
            "paths": [
                {"path": path, "product": ai_files[path]["product"],
                 "kind": ai_files[path]["kind"]}
                for path in sorted(ai_files)
            ],
        })
        return

    table = PrettyTable()
    table.field_names = ["Path", "Product", "Kind"]
    table.align["Path"] = "l"
    table.align["Product"] = "l"
    table.align["Kind"] = "l"

    for path in sorted(ai_files):
        metadata = ai_files[path]
        # Only the path is untrusted — product and kind come from AI_RULES.
        table.add_row(
            [sanitise_for_display(path), metadata["product"], metadata["kind"]])

    print(table, "\n")

    if counts:
        products = ", ".join(
            f"{product} ({count})" for product, count in counts.items())
        print(f"Found {len(ai_files)} AI paths. Products: {products}")
    else:
        print("Found 0 AI paths.")

    print()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_cli_json.py -v tests/test_ai_detection.py -v`
Expected: PASS, including the existing AI CLI tests.

- [ ] **Step 5: Commit**

```bash
git add src/panopticas/cli.py tests/test_cli_json.py
git commit -m "Add --json to ai"
```

---

## Task 9: `--json` for `file` and `urls`

**Files:**
- Modify: `src/panopticas/cli.py` (the `identify` and `find_urls` commands)
- Modify: `tests/test_cli_json.py`

**Interfaces:**
- Consumes: `cli.emit_json`, `cli.banner`, `cli.json_option`
- Produces: no new symbols

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_cli_json.py`:

```python
class TestFileJson:
    """file --json describes a single file."""

    def test_documents_every_detection_method(self, tmp_path):
        target = tmp_path / "example.py"
        target.write_text("#!/usr/bin/env python3\n# see https://example.com\n")

        result = CliRunner().invoke(cli, ["file", str(target), "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)

        assert payload["file"] == str(target)
        assert payload["extension"] == ".py"
        assert payload["filetype"] == "Python"
        assert payload["shebang"] == "#!/usr/bin/env python3"
        assert payload["shebang_language"] == "Python"
        assert payload["meta"] == []
        assert payload["urls"] == ["https://example.com"]

    def test_absent_shebang_is_null(self, tmp_path):
        target = tmp_path / "notes.md"
        target.write_text("hello\n")
        payload = json.loads(
            CliRunner().invoke(cli, ["file", str(target), "--json"]).output)
        assert payload["shebang"] is None
        assert payload["shebang_language"] is None


class TestUrlsJson:
    """urls --json returns one record per file."""

    def test_documents_urls_per_file(self, tmp_path):
        (tmp_path / "README.md").write_text("see https://example.com\n")
        (tmp_path / "empty.md").write_text("nothing here\n")

        result = CliRunner().invoke(cli, ["urls", str(tmp_path), "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)

        assert payload["directory"] == str(tmp_path)
        assert payload["count"] == len(payload["files"])
        by_path = {r["path"]: r["urls"] for r in payload["files"]}
        assert by_path["README.md"] == ["https://example.com"]
        assert by_path["empty.md"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_cli_json.py::TestFileJson tests/test_cli_json.py::TestUrlsJson -v`
Expected: FAIL — `No such option: --json`.

- [ ] **Step 3: Update both commands**

Replace `identify` and `find_urls` in `src/panopticas/cli.py`:

```python
@cli.command("file")
@json_option
@click.argument('file', required=True, type=click.Path(exists=True))
def identify(file, as_json):
    """Assess a filetype."""
    extension = core.get_fileext(file)
    shebang = core.check_shebang(file)
    payload = {
        "file": file,
        "extension": extension,
        "filetype": core.get_extension_filetype(extension),
        "shebang": shebang,
        "shebang_language": (
            core.extract_shebang_language(shebang) if shebang else None),
        "meta": core.get_filename_metatypes(file),
        "urls": core.extract_urls_from_file(file),
    }

    if as_json:
        emit_json(payload)
        return

    click.echo(f'\nAssessing filetype for file {file}')
    click.echo()
    table = PrettyTable()
    table.field_names = ["Method", "Result"]
    table.align["Method"] = "l"
    table.align["Result"] = "l"

    table.add_row(["File extenion", payload["extension"]])
    table.add_row(["File type", payload["filetype"]])
    table.add_row(["Shebang", payload["shebang"]])
    table.add_row(["Shebang Language", payload["shebang_language"]])
    table.add_row(["Meta", payload["meta"]])
    table.add_row(["URLs", '\n'.join(payload["urls"])])

    print(table)
    print()


@cli.command("urls")
@click.option('-all-files', is_flag=True, default=False, help="Show all files, no gitignore.")
@json_option
@click.argument('directory', required=True, type=click.Path(exists=True))
def find_urls(directory, all_files, as_json):
    """
    Find and show urls for all files in a given directory.
    """
    files = core.find_files(directory, all_files=all_files)
    records = [{"path": f, "urls": core.extract_urls_from_file(f)} for f in files]

    if as_json:
        emit_json({
            "directory": directory,
            "count": len(records),
            "files": records,
        })
        return

    table = PrettyTable()
    table.field_names = ["Filename", "URLs"]
    table.align["Filename"] = "l"
    table.align["URLs"] = "l"

    for record in records:
        table.add_row([record["path"], '\n'.join(record["urls"])])

    print(table)
    print()
```

Leave the `File extenion` label misspelled — it is existing output that something may match on. Fixing it is not in this change's scope.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_cli_json.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/panopticas/cli.py tests/test_cli_json.py
git commit -m "Add --json to file and urls"
```

---

## Task 10: Tighten the path arguments

Three commands accept an unconstrained `click.Path`, so a wrong path type either produces silently empty output or raises from inside the handler.

**Files:**
- Modify: `src/panopticas/cli.py` (the `assess`, `file` and `urls` argument decorators)
- Modify: `tests/test_cli_json.py`

**Interfaces:**
- Consumes: nothing
- Produces: no new symbols

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_cli_json.py`:

```python
class TestPathValidation:
    """Wrong path types fail at the Click boundary, not inside a handler."""

    def test_assess_rejects_a_file(self, tmp_path):
        target = tmp_path / "example.py"
        target.write_text("x = 1\n")
        result = CliRunner().invoke(cli, ["assess", str(target)])
        assert result.exit_code == 2
        assert "directory" in result.output.lower()

    def test_urls_rejects_a_file(self, tmp_path):
        target = tmp_path / "example.py"
        target.write_text("x = 1\n")
        result = CliRunner().invoke(cli, ["urls", str(target)])
        assert result.exit_code == 2

    def test_file_rejects_a_directory(self, tmp_path):
        result = CliRunner().invoke(cli, ["file", str(tmp_path)])
        assert result.exit_code == 2

    def test_missing_path_still_rejected(self):
        result = CliRunner().invoke(cli, ["assess", "/no/such/directory"])
        assert result.exit_code == 2

    def test_valid_paths_still_accepted(self, tmp_path):
        (tmp_path / "example.py").write_text("x = 1\n")
        assert CliRunner().invoke(
            cli, ["assess", str(tmp_path), "--json"]).exit_code == 0
        assert CliRunner().invoke(
            cli, ["file", str(tmp_path / "example.py"), "--json"]).exit_code == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_cli_json.py::TestPathValidation -v`
Expected: the three rejection tests FAIL with `exit_code == 0` — the wrong path type is currently accepted.

- [ ] **Step 3: Constrain the arguments**

In `src/panopticas/cli.py`, change three decorators. `assess`:

```python
@click.argument('directory', required=False,
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
```

`urls`:

```python
@click.argument('directory', required=True,
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
```

`file`:

```python
@click.argument('file', required=True,
                type=click.Path(exists=True, dir_okay=False))
```

`ai` is already constrained — leave it.

- [ ] **Step 4: Run the full suite**

Run: `uv run --with pytest pytest -v`
Expected: PASS.

- [ ] **Step 5: Check the error message reads well**

Run: `uv run panopticas assess pyproject.toml`
Expected: exit code 2 and a Click usage error naming the directory requirement, rather than an empty table.

- [ ] **Step 6: Commit**

```bash
git add src/panopticas/cli.py tests/test_cli_json.py
git commit -m "Constrain CLI path arguments to file or directory as appropriate"
```

---

# Phase 3 — prettytable to rich

## Task 11: The `cell()` escaping helper

Rich parses `[...]` in cell values as markup, so a path like `[blink]evil.py` would be interpreted rather than displayed. The existing `sanitise_for_display()` strips terminal control characters but knows nothing about markup — both treatments are needed before any table migrates.

**Files:**
- Modify: `src/panopticas/cli.py` (next to `sanitise_for_display`)
- Create: `tests/test_cli_escaping.py`

**Interfaces:**
- Consumes: `cli.sanitise_for_display` (existing)
- Produces: `cli.cell(value: str) -> str`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cli_escaping.py`:

```python
"""Tests for terminal-safe rendering of untrusted paths and URLs."""

from panopticas.cli import cell, sanitise_for_display


class TestCell:
    """cell() strips control characters and neutralises rich markup."""

    def test_plain_value_unchanged(self):
        assert cell("src/panopticas/core.py") == "src/panopticas/core.py"

    def test_rich_markup_is_escaped(self):
        # Escaped so rich renders the literal text rather than styling it.
        assert cell("[blink]evil.py") != "[blink]evil.py"
        assert "blink" in cell("[blink]evil.py")

    def test_ansi_escape_stripped(self):
        assert "\x1b" not in cell("evil\x1b[31m.py")

    def test_c1_control_character_stripped(self):
        # \x9b is the single-byte CSI introducer in 8-bit control mode.
        assert "\x9b" not in cell("evil\x9b31m.py")

    def test_null_byte_stripped(self):
        assert "\x00" not in cell("evil\x00.py")

    def test_combined_attack_neutralised(self):
        result = cell("\x1b[31m[bold]evil.py")
        assert "\x1b" not in result
        assert not result.startswith("[bold]")

    def test_matches_sanitise_for_display_on_control_characters(self):
        # cell() must not weaken the existing protection.
        value = "a\x1b[31mb\x9fc"
        assert "\x1b" not in cell(value)
        assert sanitise_for_display(value) in cell(value)


class TestBannerSanitisation:
    """The progress lines interpolate a path and must be sanitised too."""

    def test_control_characters_stripped_from_banner(self, capsys):
        from panopticas.cli import banner

        banner("Assessing directory: evil\x1b[31mdir", as_json=False)
        assert "\x1b" not in capsys.readouterr().out

    def test_banner_goes_to_stderr_in_json_mode(self, capsys):
        from panopticas.cli import banner

        banner("Assessing directory: .", as_json=True)
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "Assessing directory" in captured.err
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_cli_escaping.py -v`
Expected: collection error — `cannot import name 'cell'`.

- [ ] **Step 3: Implement it**

In `src/panopticas/cli.py`, add `from rich.markup import escape` to the rich imports, then add below `sanitise_for_display`:

```python
def cell(value):
    """
    Render an untrusted value safely for the terminal.

    Two distinct problems. sanitise_for_display() removes control characters
    a crafted filename could use to rewrite what the operator sees. Rich adds
    a second surface: it parses [...] in any string it prints as markup, so
    escape() is needed as well, or a file named "[blink]evil.py" would style
    the output instead of appearing in it.

    Applies to paths and URLs. Tags, products, kinds and file types come from
    constants.py and are trusted.
    """
    return escape(sanitise_for_display(value))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_cli_escaping.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/panopticas/cli.py tests/test_cli_escaping.py
git commit -m "Add cell() to escape untrusted values for rich output"
```

---

## Task 12: Migrate `assess` and `file` to rich

**Files:**
- Modify: `src/panopticas/cli.py` (the `assess` and `identify` commands)
- Modify: `tests/test_cli_escaping.py`

**Interfaces:**
- Consumes: `cli.cell` from Task 11, `cli.console` from Task 5
- Produces: no new symbols

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cli_escaping.py`:

```python
import json

from click.testing import CliRunner

from panopticas.cli import cli


class TestAssessEscapesPaths:
    """A crafted filename cannot style or corrupt assess output."""

    def test_markup_in_filename_is_not_interpreted(self, tmp_path):
        (tmp_path / "[bold]evil.py").write_text("x = 1\n")
        result = CliRunner().invoke(cli, ["assess", str(tmp_path)])
        assert result.exit_code == 0
        # The literal name appears; the markup is not consumed as styling.
        assert "evil.py" in result.output

    def test_json_keeps_the_real_path(self, tmp_path):
        (tmp_path / "[bold]evil.py").write_text("x = 1\n")
        payload = json.loads(
            CliRunner().invoke(cli, ["assess", str(tmp_path), "--json"]).output)
        assert any(r["path"] == "[bold]evil.py" for r in payload["files"])


class TestShebangIsUntrusted:
    """The language column can come from the file's own first line."""

    def test_crafted_shebang_does_not_reach_the_terminal_raw(self, tmp_path):
        # get_language() falls back to extract_shebang_language(), which
        # returns text read out of the file — a crafted shebang would
        # otherwise be rendered as markup and control sequences.
        target = tmp_path / "trap"
        target.write_text("#!/usr/bin/env \x1b[31m[blink]sh\n")

        result = CliRunner().invoke(cli, ["assess", str(tmp_path)])
        assert result.exit_code == 0
        assert "\x1b" not in result.output

    def test_file_command_escapes_the_shebang(self, tmp_path):
        target = tmp_path / "trap"
        target.write_text("#!/usr/bin/env \x1b[31m[blink]sh\n")

        result = CliRunner().invoke(cli, ["file", str(target)])
        assert result.exit_code == 0
        assert "\x1b" not in result.output

    def test_json_keeps_the_raw_shebang(self, tmp_path):
        target = tmp_path / "trap"
        target.write_text("#!/usr/bin/env python3\n")
        payload = json.loads(
            CliRunner().invoke(cli, ["file", str(target), "--json"]).output)
        assert payload["shebang"] == "#!/usr/bin/env python3"
```

- [ ] **Step 2: Run tests to verify they fail or error**

Run: `uv run --with pytest pytest tests/test_cli_escaping.py -v`
Expected: `test_markup_in_filename_is_not_interpreted` may pass under prettytable (which does not parse markup) — that is fine. It exists to lock the behaviour in once rich takes over. `test_json_keeps_the_real_path` should already pass from Task 7.

- [ ] **Step 3: Convert the assess table**

In `src/panopticas/cli.py`, add `from rich.table import Table` to the rich imports. Replace the table-building block in `assess` (everything from `banner(f'Found {len(files)} files.\n', as_json)` to the final `print()`) with:

```python
    caption = f"{len(records)} files"
    if lines:
        counted = [r["lines"] for r in records if r["lines"] is not None]
        excluded = len(records) - len(counted)
        caption = f"{len(records)} files, {sum(counted):,} lines"
        if excluded:
            caption += f" ({excluded} excluded — binary/N/A)"

    table = Table(title=f"Assessment of {cell(directory)}",
                  caption=caption, caption_style="dim")
    table.add_column("File", justify="left", style="cyan", no_wrap=True)
    table.add_column("Language", justify="left", style="magenta")
    table.add_column("Meta", justify="left", style="green")
    if lines:
        table.add_column("Lines", justify="right", style="bright_black")

    for record in records:
        row = [
            cell(record["path"]),
            # The language is untrusted too. get_language() falls back to
            # extract_shebang_language(), which returns text read out of the
            # file's first line — a crafted shebang reaches this column
            # verbatim. Only the Meta column is trusted (it comes from
            # constants.py).
            cell(record["language"] or ""),
            ", ".join(record["meta"]),
        ]
        if lines:
            row.append(str(record["lines"]) if record["lines"] is not None else "N/A")
        table.add_row(*row)

    console.print(table)
    console.print()
```

Rich requires every cell to be a string — `add_row` will not accept the raw `int` line counts or a `None` language.

- [ ] **Step 4: Convert the file table**

Replace the table block in `identify` with:

```python
    console.print(f"\nAssessing filetype for file {cell(file)}\n")
    table = Table()
    table.add_column("Method", justify="left", style="cyan", no_wrap=True)
    table.add_column("Result", justify="left", style="magenta")

    # Extension and file type are looked up in constants.py and are trusted.
    # The shebang rows are read out of the file's first line, so they are
    # untrusted and must go through cell() like the path and the URLs.
    table.add_row("File extenion", payload["extension"] or "")
    table.add_row("File type", payload["filetype"] or "")
    table.add_row("Shebang", cell(payload["shebang"] or ""))
    table.add_row("Shebang Language", cell(payload["shebang_language"] or ""))
    table.add_row("Meta", ", ".join(payload["meta"]))
    table.add_row("URLs", "\n".join(cell(url) for url in payload["urls"]))

    console.print(table)
    console.print()
```

- [ ] **Step 5: Run the full suite**

Run: `uv run --with pytest pytest -v`
Expected: PASS. `tests/test_panopticas.py` and `tests/test_ai_detection.py` must be unaffected.

- [ ] **Step 6: Look at the output**

Run: `uv run panopticas assess src/tests --lines` and `uv run panopticas file src/tests/example.py`
Expected: rich tables with a title and dim caption. Confirm the totals in the caption match the old footer line.

- [ ] **Step 7: Commit**

```bash
git add src/panopticas/cli.py tests/test_cli_escaping.py
git commit -m "Migrate assess and file to rich tables"
```

---

## Task 13: Migrate `ai` and `urls` to rich

**Files:**
- Modify: `src/panopticas/cli.py` (the `ai` and `find_urls` commands)
- Modify: `tests/test_cli_escaping.py`

**Interfaces:**
- Consumes: `cli.cell`, `cli.console`
- Produces: no new symbols

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cli_escaping.py`:

```python
class TestAiEscapesPaths:
    """The ai command renders untrusted paths safely."""

    def test_markup_in_ai_filename_is_escaped(self, tmp_path):
        agents = tmp_path / "[bold]dir"
        agents.mkdir()
        (agents / "CLAUDE.md").write_text("guidance")

        result = CliRunner().invoke(cli, ["ai", str(tmp_path)])
        assert result.exit_code == 0
        assert "CLAUDE.md" in result.output
        assert "Claude" in result.output
```

- [ ] **Step 2: Run test to verify current state**

Run: `uv run --with pytest pytest tests/test_cli_escaping.py::TestAiEscapesPaths -v`
Expected: PASS under prettytable. It locks in behaviour for the conversion.

- [ ] **Step 3: Convert the ai table**

Replace the table block in `ai` (from `table = PrettyTable()` to the final `print()`) with:

```python
    if counts:
        products = ", ".join(
            f"{product} ({count})" for product, count in counts.items())
        caption = f"{len(ai_files)} AI paths • {products}"
    else:
        caption = "0 AI paths"

    table = Table(title=f"AI artifacts in {cell(directory)}",
                  caption=caption, caption_style="dim")
    table.add_column("Path", justify="left", style="cyan", no_wrap=True)
    table.add_column("Product", justify="left", style="magenta")
    table.add_column("Kind", justify="left", style="green")

    for path in sorted(ai_files):
        metadata = ai_files[path]
        # Only the path is untrusted — product and kind come from AI_RULES.
        table.add_row(cell(path), metadata["product"], metadata["kind"])

    console.print(table)
    console.print()
```

- [ ] **Step 4: Convert the urls table**

Replace the table block in `find_urls` with:

```python
    table = Table(title=f"URLs in {cell(directory)}",
                  caption=f"{len(records)} files", caption_style="dim")
    table.add_column("Filename", justify="left", style="cyan", no_wrap=True)
    table.add_column("URLs", justify="left", style="magenta")

    for record in records:
        table.add_row(
            cell(record["path"]),
            "\n".join(cell(url) for url in record["urls"]))

    console.print(table)
    console.print()
```

- [ ] **Step 5: Run the full suite**

Run: `uv run --with pytest pytest -v`
Expected: PASS.

Existing tests in `tests/test_ai_detection.py` assert on `ai` output. If one fails because it matched prettytable's `+---+` borders or the exact `Found N AI paths. Products: …` footer, update that assertion to match the new caption — the information is still present, its presentation changed.

- [ ] **Step 6: Verify no prettytable remains**

Run: `grep -n "PrettyTable\|prettytable" src/panopticas/cli.py`
Expected: no output. If the import line remains, remove it.

- [ ] **Step 7: Commit**

```bash
git add src/panopticas/cli.py tests/test_cli_escaping.py tests/test_ai_detection.py
git commit -m "Migrate ai and urls to rich tables"
```

---

## Task 14: Drop the prettytable dependency

**Files:**
- Modify: `pyproject.toml`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: nothing
- Produces: no new symbols

- [ ] **Step 1: Confirm nothing imports it**

Run: `grep -rn "prettytable\|PrettyTable" src/ tests/`
Expected: no output. If anything remains, remove it before continuing.

- [ ] **Step 2: Remove it from pyproject.toml**

```toml
dependencies = [
    "Click>=8.3.1",
    "pathspec>=0.12.1",
    "rich>=14.0.0",
]
```

- [ ] **Step 3: Remove it from requirements.txt**

Delete the `prettytable==` line. Also delete `wcwidth==` — it is prettytable's dependency, not one of ours. Confirm nothing else needs it:

```bash
uv run python -c "import wcwidth" 2>&1 | head -1
```
An `ImportError` after a clean reinstall is the expected outcome; if some other package pulls it in, uv will restore it.

- [ ] **Step 4: Verify a clean install works**

```bash
uv run --refresh --with pytest pytest -v
uv run panopticas assess src/tests
uv run panopticas ai
```
Expected: tests pass and both commands render rich tables with prettytable absent from the environment.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt
git commit -m "Drop the prettytable dependency"
```

---

# Phase 4 — Release preparation

## Task 15: Change document, changelog and version bump

**Files:**
- Create: `changes/2026-08-tag-vocabulary-and-cli-refactor.md`
- Modify: `CHANGELOG.md`
- Modify: `pyproject.toml:7`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: everything above
- Produces: version `0.0.19`

- [ ] **Step 1: Write the change document**

Create `changes/2026-08-tag-vocabulary-and-cli-refactor.md`:

```markdown
# Tag vocabulary, JSON output and rich migration

**Version:** 0.0.19
**Design:** [`docs/superpowers/specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md`](../docs/superpowers/specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md)

## What changed

### Vocabulary functions

`get_tags()`, `get_filetypes()` and `get_languages()` return the vocabularies
panopticas uses, each a sorted, deduplicated list of strings.

`get_tags()` is **derived** by traversing `METADATA_RULES` and `AI_RULES`
rather than maintained as a list, so a new detection rule joins the vocabulary
the moment it is added. A drift test synthesises a path for every rule and
asserts the tags it produces are all in `get_tags()`, which makes that a
contract rather than a claim.

The AI kind `directory` is excluded. It is synthesised inside
`find_ai_files(all_files=True)` and never reaches a file's tags, so it cannot
be searched for in kospex.

### Language classification

`get_languages()` cannot be derived — nothing in the data says whether `PNG`
is a language — so `constants.py` carries `LANGUAGE_FILETYPES` (32) and
`NON_LANGUAGE_FILETYPES` (44). Both sets exist so that a completeness test can
fail when a newly added file type is unclassified; an exclusion list alone
would silently default it to "language".

The principle: a language expresses behaviour or presentation. Data formats
(JSON, YAML, XML), prose (Markdown), binaries (PNG) and named config files
(go.sum) are file types but not languages. This matches what GitHub displays —
its language bar counts only Linguist's `programming` and `markup` types.

### CLI

- New `tags`, `languages` and `filetypes` commands, printing a column grid.
- `--json` (also `-json`) on all seven commands. Every document is a JSON
  object, never a bare array, so fields can be added later without breaking a
  parser. In JSON mode stdout carries only the document; progress messages go
  to stderr.
- Path arguments are validated at the Click boundary. `assess` and `urls`
  require a directory, `file` requires a file. Previously a wrong path type
  gave empty output or an unhandled `IsADirectoryError`.

### rich replaces prettytable

Matches kospex and foundationx. Rich parses `[...]` as markup in anything it
prints, so untrusted paths and URLs now pass through `cell()`, which strips
terminal control characters and escapes markup. Tags, products and kinds come
from `constants.py` and are trusted.

## kospex impact

None. kospex declares `prettytable` and `rich` directly, and depends on
`panopticas>=0.0.18`, so this release reaches it without a manual pin bump.
No tag was renamed or removed, so stored `tech_type` values stay valid.
```

- [ ] **Step 2: Update CHANGELOG.md**

Add a `0.0.19` section in Keep a Changelog format:

```markdown
## [0.0.19]

### Added
- `get_tags()`, `get_filetypes()` and `get_languages()` return the vocabularies panopticas uses. The tag vocabulary is derived from the detection rules, so it cannot drift.
- `panopticas tags`, `panopticas languages` and `panopticas filetypes` commands.
- `--json` (also accepted as `-json`) on every command. In JSON mode stdout carries only the document; progress messages go to stderr.

### Changed
- Table output now uses `rich` instead of `prettytable`, matching kospex and foundationx.
- Path arguments are validated at the CLI boundary: `assess` and `urls` require a directory, `file` requires a file. Previously a wrong path type produced empty output or an unhandled error.
- `assess -unknown` now reports totals for the rows it shows. Previously it filtered the rows but the footer still counted every scanned file.

### Removed
- The `prettytable` dependency.
```

- [ ] **Step 3: Bump the version**

In `pyproject.toml`, set `version = "0.0.19"`.

- [ ] **Step 4: Document the new commands in CLAUDE.md**

Add to the "Running the CLI" block:

```bash
# Show the vocabularies panopticas uses
panopticas tags
panopticas languages
panopticas filetypes

# Any command can emit JSON
panopticas assess --json
```

**Do not touch `CLAUDE.md`'s release step 8 or its "Relationship to kospex" section.** Both describe kospex as pinning panopticas exactly, which no longer matches kospex's `pyproject.toml` (`panopticas>=0.0.18`). That correction is deliberately out of scope for this change — leave the wording exactly as it is. Only the "Running the CLI" block changes, in Step 4 above.

- [ ] **Step 5: Run the full suite and build**

```bash
uv run --with pytest pytest -v
uv run --with build python -m build
ls dist/panopticas-0.0.19*
```
Expected: tests pass; a wheel and sdist for 0.0.19 exist.

- [ ] **Step 6: Commit**

```bash
git add changes/2026-08-tag-vocabulary-and-cli-refactor.md CHANGELOG.md pyproject.toml CLAUDE.md
git commit -m "Prepare 0.0.19"
```

- [ ] **Step 7: Hand off the upload**

Do **not** run `twine upload`. Report that `dist/panopticas-0.0.19*` is built and ready, and that the maintainer performs the upload. Scoping the glob to this version matters — `dist/*` re-sends every past artifact and PyPI aborts on the duplicates.

---

## Verification checklist

Run before opening the PR:

- [ ] `uv run --with pytest pytest -v` — all tests pass
- [ ] `grep -rn "prettytable\|PrettyTable" src/ tests/ pyproject.toml requirements.txt` — no output
- [ ] `uv run panopticas tags | head -3` and `uv run panopticas tags --json | python -m json.tool > /dev/null` — both work
- [ ] Every command accepts `--json` and `-json`: `assess`, `ai`, `file`, `urls`, `tags`, `languages`, `filetypes`
- [ ] `uv run panopticas assess pyproject.toml` exits 2 with a usage error
- [ ] `git status --porcelain` shows only `.safety-project.ini` and `uv.lock` untracked
