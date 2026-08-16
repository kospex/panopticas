# AI Coding Agent Detection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect the file and directory artifacts of ~20 AI coding agent products, tag each with `["AI", product, kind]`, and add a `panopticas ai` command that reports which AI tools a repository uses.

**Architecture:** A new `AI_RULES` lookup table in `constants.py` maps indicators to `(product, kind)` across three match modes (exact filename, path fragment, filename suffix). A new `get_ai_metadata()` in `core.py` resolves a path against that table and is the single source of truth; the existing `get_filename_metatypes()` derives its AI tags from it, so `panopticas assess` and kospex both pick up the new tags with no change at their call sites. A new `find_ai_files()` walks a directory for the new `ai` CLI command.

**Tech Stack:** Python 3.12+, Click (CLI), prettytable (output), pathspec (gitignore), pytest (tests).

**Spec:** `changes/design/specs/2026-07-31-ai-agent-detection-design.md`

## Global Constraints

- Detection is **path-based only**. Never open a file to determine AI metadata.
- Tag shape is exactly `["AI", product, kind]` — three tags, in that order.
- Products are **brand-level**: `Claude` (not `Claude Code`/`Claude Desktop`), `Gemini`, `Copilot`, `Cursor`.
- `kind` must be one of the 14 values in `AI_ARTIFACT_KINDS`. No rule may introduce a new kind without adding it there.
- Precedence: exact filename → longest `path_contains` match → longest `filename_suffix` match. First hit wins, one result per path.
- `exact_filename` and `path_contains` keys are **lowercase**; matching lowercases the path first.
- Existing non-AI tag output must not change. `pyproject.toml` and `.github/workflows/ci.yml` produce byte-identical tag lists before and after.
- Run tests with `uv run --with pytest pytest` — a bare `pytest` fails in this repo's environment.
- Baseline before starting: **130 tests passing**.
- Work happens on branch `feat/ai-agent-detection`.

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `src/panopticas/constants.py` | `AI_RULES` table + `AI_ARTIFACT_KINDS` vocabulary; remove 2 legacy AI entries from `METADATA_RULES` | Modify |
| `src/panopticas/core.py` | `get_ai_metadata()`, `find_ai_files()`; extend `get_filename_metatypes()` | Modify |
| `src/panopticas/__init__.py` | Export the two new functions | Modify |
| `src/panopticas/cli.py` | `ai` command | Modify |
| `tests/test_ai_detection.py` | All AI detection tests | Create |
| `CHANGELOG.md`, `README.md`, `changes/202607-ai-agent-detection.md`, `pyproject.toml` | Release docs and version | Modify/Create |

---

### Task 1: AI_RULES table and get_ai_metadata()

Builds the detection engine and the Tier 1 (high-confidence) rules. Tier 2 rules are added in Task 5.

**Files:**
- Modify: `src/panopticas/constants.py` (append after `METADATA_RULES`, which ends at line 181)
- Modify: `src/panopticas/core.py` (import at line 7; new function after `get_extension_filetype`, line 30)
- Test: `tests/test_ai_detection.py` (create)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `constants.AI_ARTIFACT_KINDS: set[str]` — the 14 legal kind values.
  - `constants.AI_RULES: dict[str, dict[str, tuple[str, str]]]` — keys `"exact_filename"`, `"path_contains"`, `"filename_suffix"`; values map indicator → `(product, kind)`.
  - `core.get_ai_metadata(file_path: str) -> dict | None` — returns `{"product": str, "kind": str}` or `None`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ai_detection.py`:

```python
"""
Tests for AI coding agent detection.

Covers: get_ai_metadata() resolution and precedence, AI tags in
get_filename_metatypes(), find_ai_files() directory walking, and
AI_RULES table integrity.
"""

import os
import tempfile

import pytest

from panopticas import get_ai_metadata, get_filename_metatypes
from panopticas.constants import AI_RULES, AI_ARTIFACT_KINDS


class TestGetAiMetadataExactFilename:
    """Exact basename matches."""

    def test_claude_md(self):
        assert get_ai_metadata("CLAUDE.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_claude_md_lowercase(self):
        assert get_ai_metadata("claude.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_claude_md_in_subdirectory(self):
        assert get_ai_metadata("packages/api/CLAUDE.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_agents_md_is_vendor_neutral(self):
        assert get_ai_metadata("AGENTS.md") == {
            "product": "Agents", "kind": "instructions"}

    def test_gemini_md(self):
        assert get_ai_metadata("GEMINI.md") == {
            "product": "Gemini", "kind": "instructions"}

    def test_cursorrules(self):
        assert get_ai_metadata(".cursorrules") == {
            "product": "Cursor", "kind": "rules"}

    def test_cursorignore_is_an_ignore_file(self):
        assert get_ai_metadata(".cursorignore") == {
            "product": "Cursor", "kind": "ignore"}

    def test_mcp_json_is_protocol_not_product(self):
        assert get_ai_metadata(".mcp.json") == {
            "product": "MCP", "kind": "config"}

    def test_claude_desktop_config_tags_as_claude_brand(self):
        assert get_ai_metadata("claude_desktop_config.json") == {
            "product": "Claude", "kind": "config"}

    def test_llms_txt(self):
        assert get_ai_metadata("llms.txt") == {
            "product": "llms.txt", "kind": "docs"}


class TestGetAiMetadataPathContains:
    """Directory fragment matches."""

    def test_claude_settings(self):
        assert get_ai_metadata(".claude/settings.json") == {
            "product": "Claude", "kind": "config"}

    def test_claude_skill(self):
        assert get_ai_metadata(".claude/skills/review/SKILL.md") == {
            "product": "Claude", "kind": "skill"}

    def test_claude_agent(self):
        assert get_ai_metadata(".claude/agents/reviewer.md") == {
            "product": "Claude", "kind": "agent"}

    def test_claude_command(self):
        assert get_ai_metadata(".claude/commands/deploy.md") == {
            "product": "Claude", "kind": "command"}

    def test_copilot_prompt_directory(self):
        assert get_ai_metadata(".github/prompts/refactor.md") == {
            "product": "Copilot", "kind": "prompt"}

    def test_cursor_rules_directory(self):
        assert get_ai_metadata(".cursor/rules/style.mdc") == {
            "product": "Cursor", "kind": "rules"}

    def test_cursor_mcp_json_attributes_to_cursor(self):
        assert get_ai_metadata(".cursor/mcp.json") == {
            "product": "Cursor", "kind": "config"}

    def test_vscode_mcp_json(self):
        assert get_ai_metadata(".vscode/mcp.json") == {
            "product": "MCP", "kind": "config"}

    def test_codex_directory(self):
        assert get_ai_metadata(".codex/config.toml") == {
            "product": "Codex", "kind": "config"}

    def test_gemini_directory(self):
        assert get_ai_metadata(".gemini/settings.json") == {
            "product": "Gemini", "kind": "config"}

    def test_nested_repo_path(self):
        assert get_ai_metadata("vendor/lib/.claude/settings.json") == {
            "product": "Claude", "kind": "config"}


class TestGetAiMetadataSuffix:
    """Filename suffix matches."""

    def test_prompt_md_suffix(self):
        assert get_ai_metadata("docs/refactor.prompt.md") == {
            "product": "Copilot", "kind": "prompt"}

    def test_instructions_md_suffix(self):
        assert get_ai_metadata("docs/python.instructions.md") == {
            "product": "Copilot", "kind": "instructions"}

    def test_mdc_suffix(self):
        assert get_ai_metadata("rules/style.mdc") == {
            "product": "Cursor", "kind": "rules"}


class TestGetAiMetadataPrecedence:
    """Exact beats path; longer path fragment beats shorter."""

    def test_exact_filename_beats_path_fragment(self):
        # .claude/ would give kind "config"; the exact CLAUDE.md rule wins.
        assert get_ai_metadata(".claude/CLAUDE.md") == {
            "product": "Claude", "kind": "instructions"}

    def test_longer_path_fragment_wins(self):
        # Both ".claude/" and ".claude/skills/" match; the longer one wins.
        assert get_ai_metadata(".claude/skills/x/helper.py") == {
            "product": "Claude", "kind": "skill"}

    def test_path_fragment_beats_suffix(self):
        # ".cursor/rules/" and ".mdc" both give (Cursor, rules) here, but
        # the path fragment is what resolves it.
        assert get_ai_metadata(".cursor/rules/a.mdc")["kind"] == "rules"


class TestGetAiMetadataNonMatches:
    """Ordinary files are not AI artifacts."""

    @pytest.mark.parametrize("path", [
        "pyproject.toml",
        "src/panopticas/core.py",
        "README.md",
        "docs/index.html",
        ".github/workflows/ci.yml",
        ".gitignore",
        "package.json",
    ])
    def test_returns_none(self, path):
        assert get_ai_metadata(path) is None

    def test_empty_path(self):
        assert get_ai_metadata("") is None


class TestAiRulesIntegrity:
    """Guards the table against rot as entries are added."""

    def test_only_known_match_modes(self):
        assert set(AI_RULES) == {
            "exact_filename", "path_contains", "filename_suffix"}

    def test_every_value_is_a_product_kind_pair(self):
        for mode, rules in AI_RULES.items():
            for key, value in rules.items():
                assert isinstance(value, tuple), f"{mode}:{key} is not a tuple"
                assert len(value) == 2, f"{mode}:{key} is not a 2-tuple"
                product, kind = value
                assert product and isinstance(product, str)
                assert kind and isinstance(kind, str)

    def test_every_kind_is_in_the_vocabulary(self):
        for mode, rules in AI_RULES.items():
            for key, (_product, kind) in rules.items():
                assert kind in AI_ARTIFACT_KINDS, f"{mode}:{key} has kind {kind!r}"

    def test_exact_filename_keys_are_lowercase(self):
        for key in AI_RULES["exact_filename"]:
            assert key == key.lower()

    def test_path_contains_keys_contain_a_slash(self):
        # Either a directory fragment ending in "/", or a dir-qualified
        # filename such as ".vscode/mcp.json".
        for key in AI_RULES["path_contains"]:
            assert "/" in key, f"{key!r} has no path separator"
            assert key == key.lower()

    def test_filename_suffix_keys_start_with_a_dot(self):
        for key in AI_RULES["filename_suffix"]:
            assert key.startswith("."), f"{key!r} does not start with a dot"
            assert key == key.lower()

    def test_no_key_appears_in_two_modes(self):
        seen = {}
        for mode, rules in AI_RULES.items():
            for key in rules:
                assert key not in seen, f"{key!r} in both {seen.get(key)} and {mode}"
                seen[key] = mode
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q`
Expected: collection error — `ImportError: cannot import name 'get_ai_metadata' from 'panopticas'`

- [ ] **Step 3: Add AI_ARTIFACT_KINDS and AI_RULES to constants.py**

Append to the end of `src/panopticas/constants.py` (after `METADATA_RULES`):

```python
# The complete set of legal `kind` values for an AI artifact.
# A rule may not use a kind outside this set.
AI_ARTIFACT_KINDS = {
    "instructions",  # natural-language guidance for an agent
    "config",        # tool configuration
    "rules",         # rule/policy files
    "prompt",        # reusable prompt
    "chatmode",      # chat mode definition
    "command",       # slash command definition
    "agent",         # subagent definition
    "skill",         # skill definition
    "hook",          # lifecycle hook
    "plugin",        # plugin bundle
    "ignore",        # exclusion file
    "history",       # session/chat transcript
    "docs",          # LLM-oriented documentation
    "directory",     # bare AI directory (find_ai_files(all_files=True) only)
}

# AI coding agent artifacts, mapping an indicator to (product, kind).
#
# Products are brand-level: "Claude" covers both Claude Code and Claude
# Desktop, so a single tag finds all Anthropic tooling. Files owned by no
# brand use a pseudo-product ("Agents", "MCP", "llms.txt").
#
# Precedence when resolving a path: exact_filename, then the longest
# matching path_contains fragment, then the longest matching
# filename_suffix. See core.get_ai_metadata().
AI_RULES = {
    # Matched against the lowercased basename.
    "exact_filename": {
        # Claude — Anthropic
        "claude.md": ("Claude", "instructions"),
        "claude.local.md": ("Claude", "instructions"),
        "claude_desktop_config.json": ("Claude", "config"),
        # Copilot — GitHub
        "copilot-instructions.md": ("Copilot", "instructions"),
        # Cursor — Anysphere
        ".cursorrules": ("Cursor", "rules"),
        ".cursorignore": ("Cursor", "ignore"),
        ".cursorindexingignore": ("Cursor", "ignore"),
        # Gemini — Google
        "gemini.md": ("Gemini", "instructions"),
        ".aiexclude": ("Gemini", "ignore"),
        # Vendor-neutral
        "agents.md": ("Agents", "instructions"),
        ".aiignore": ("Agents", "ignore"),
        ".mcp.json": ("MCP", "config"),
        "llms.txt": ("llms.txt", "docs"),
        "llms-full.txt": ("llms.txt", "docs"),
    },
    # Matched as a substring of the lowercased path. Longest match wins,
    # so more specific fragments may be listed in any order.
    "path_contains": {
        # Claude
        ".claude/skills/": ("Claude", "skill"),
        ".claude/agents/": ("Claude", "agent"),
        ".claude/commands/": ("Claude", "command"),
        ".claude/hooks/": ("Claude", "hook"),
        ".claude/plugins/": ("Claude", "plugin"),
        ".claude/": ("Claude", "config"),
        # Copilot
        ".github/instructions/": ("Copilot", "instructions"),
        ".github/prompts/": ("Copilot", "prompt"),
        ".github/chatmodes/": ("Copilot", "chatmode"),
        # Cursor
        ".cursor/rules/": ("Cursor", "rules"),
        ".cursor/": ("Cursor", "config"),
        # Gemini
        ".gemini/": ("Gemini", "config"),
        # Codex — OpenAI
        ".codex/": ("Codex", "config"),
        # Vendor-neutral
        ".vscode/mcp.json": ("MCP", "config"),
    },
    # Matched against the end of the lowercased basename. Longest wins.
    "filename_suffix": {
        ".instructions.md": ("Copilot", "instructions"),
        ".prompt.md": ("Copilot", "prompt"),
        ".chatmode.md": ("Copilot", "chatmode"),
        ".mdc": ("Cursor", "rules"),
    },
}
```

- [ ] **Step 4: Add get_ai_metadata() to core.py**

Change the import on `src/panopticas/core.py:7` from:

```python
from .constants import EXT_FILETYPES, LANGUAGE_BY_BASENAME, METADATA_RULES
```

to:

```python
from .constants import AI_RULES, EXT_FILETYPES, LANGUAGE_BY_BASENAME, METADATA_RULES
```

Then insert this function after `get_extension_filetype()` (which ends at line 30), before `get_filename_metatypes()`:

```python
def get_ai_metadata(file_path):
    """
    Return AI coding agent metadata for a path, or None.

    Returns {"product": str, "kind": str} when the path is a recognised
    AI agent artifact, for example:
        CLAUDE.md              -> {"product": "Claude", "kind": "instructions"}
        .cursor/rules/x.mdc    -> {"product": "Cursor", "kind": "rules"}

    This is pure path inspection — the file is never opened, and the path
    need not exist. Precedence is exact filename, then the longest matching
    path fragment, then the longest matching filename suffix.
    """
    if not file_path:
        return None

    # Normalise Windows separators and case so the rule keys stay lowercase.
    path = file_path.replace(os.sep, "/").lower()
    filename = os.path.basename(path)

    rule = AI_RULES["exact_filename"].get(filename)
    if rule:
        return {"product": rule[0], "kind": rule[1]}

    for fragment in sorted(AI_RULES["path_contains"], key=len, reverse=True):
        if fragment in path:
            rule = AI_RULES["path_contains"][fragment]
            return {"product": rule[0], "kind": rule[1]}

    for suffix in sorted(AI_RULES["filename_suffix"], key=len, reverse=True):
        if filename.endswith(suffix):
            rule = AI_RULES["filename_suffix"][suffix]
            return {"product": rule[0], "kind": rule[1]}

    return None
```

- [ ] **Step 5: Export get_ai_metadata from `__init__.py`**

In `src/panopticas/__init__.py`, add `get_ai_metadata,` to the `from .core import (...)` block (after `get_filename_metatypes,`) and `'get_ai_metadata',` to `__all__` (after `'get_filename_metatypes',`).

- [ ] **Step 6: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q`
Expected: PASS (~45 tests)

Then confirm nothing regressed:

Run: `uv run --with pytest pytest -q`
Expected: 130 existing tests still pass, plus the new ones.

- [ ] **Step 7: Commit**

```bash
git add src/panopticas/constants.py src/panopticas/core.py \
        src/panopticas/__init__.py tests/test_ai_detection.py
git commit -m "feat: add AI_RULES table and get_ai_metadata()"
```

---

### Task 2: Emit AI tags from get_filename_metatypes()

Wires detection into the function kospex and `panopticas assess` already call, and retires the two legacy AI entries.

**Files:**
- Modify: `src/panopticas/core.py:32-68` (`get_filename_metatypes`)
- Modify: `src/panopticas/constants.py` (remove 2 entries from `METADATA_RULES["exact_filename_rules"]`, currently lines 134 and 137)
- Test: `tests/test_ai_detection.py` (append)

**Interfaces:**
- Consumes: `core.get_ai_metadata(file_path) -> dict | None` from Task 1.
- Produces: `get_filename_metatypes()` appends `["AI", product, kind]` when `get_ai_metadata()` matches. No signature change.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_ai_detection.py`:

```python
class TestAiTagsInMetatypes:
    """get_filename_metatypes() derives its AI tags from get_ai_metadata()."""

    def test_claude_md_tags(self):
        assert get_filename_metatypes("CLAUDE.md") == [
            "AI", "Claude", "instructions"]

    def test_claude_settings_tags(self):
        assert get_filename_metatypes(".claude/settings.json") == [
            "AI", "Claude", "config"]

    def test_agents_md_tags(self):
        assert get_filename_metatypes("AGENTS.md") == [
            "AI", "Agents", "instructions"]

    def test_cursor_rule_tags(self):
        assert get_filename_metatypes(".cursor/rules/style.mdc") == [
            "AI", "Cursor", "rules"]

    def test_legacy_bare_claude_tag_is_gone(self):
        # The old rule emitted ["Claude", "AI", "Claude Code"].
        tags = get_filename_metatypes("CLAUDE.md")
        assert "Claude Code" not in tags
        assert tags.count("Claude") == 1

    def test_ai_tag_always_present_for_ai_files(self):
        for path in ["CLAUDE.md", ".claude/settings.json", "AGENTS.md",
                     ".cursorrules", ".mcp.json", "llms.txt"]:
            assert "AI" in get_filename_metatypes(path), path

    def test_ai_tags_come_first_in_their_group(self):
        # ["AI", product, kind] is appended as a contiguous triple.
        tags = get_filename_metatypes(".github/copilot-instructions.md")
        index = tags.index("AI")
        assert tags[index:index + 3] == ["AI", "Copilot", "instructions"]


class TestExistingTagsPreserved:
    """The AI pass must not disturb the existing metadata rules."""

    def test_copilot_instructions_keeps_github_tags(self):
        tags = get_filename_metatypes(".github/copilot-instructions.md")
        assert tags == ["GitHub", "Git", "AI", "Copilot", "instructions"]

    def test_workflow_tags_unchanged(self):
        assert get_filename_metatypes(".github/workflows/ci.yml") == [
            "workflow", "pipeline", "GitHub", "Git"]

    def test_pyproject_tags_unchanged(self):
        assert get_filename_metatypes("pyproject.toml") == [
            "build", "dependencies", "Python"]

    def test_ordinary_file_has_no_ai_tag(self):
        assert "AI" not in get_filename_metatypes("src/panopticas/core.py")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q -k "Metatypes or Preserved"`
Expected: FAIL — `test_claude_md_tags` gets `['Claude', 'AI', 'Claude Code']`, and the `.claude/settings.json` cases get `[]`.

- [ ] **Step 3: Remove the two legacy entries from constants.py**

In `src/panopticas/constants.py`, delete these two lines from `METADATA_RULES["exact_filename_rules"]`:

```python
        "claude.md": ["Claude", "AI", "Claude Code"],
        "gemini.md": ["Gemini", "AI", "Gemini CLI"],
```

Both are now expressed in `AI_RULES`, so AI knowledge lives in exactly one place.

- [ ] **Step 4: Append the AI block to get_filename_metatypes()**

In `src/panopticas/core.py`, inside `get_filename_metatypes()`, insert this immediately before the final `return tags` (currently line 68), after the license special case:

```python
    # AI coding agent artifacts. Runs last so it appends to — rather than
    # competes with — the rules above; .github/copilot-instructions.md
    # keeps its GitHub/Git tags and gains the AI ones.
    ai_metadata = get_ai_metadata(file_path)
    if ai_metadata:
        tags.extend(["AI", ai_metadata["product"], ai_metadata["kind"]])
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q`
Expected: PASS

- [ ] **Step 6: Check the full suite for regressions**

Run: `uv run --with pytest pytest -q`
Expected: All pass.

The existing suite asserts on `METADATA_RULES` contents and may reference the removed `claude.md`/`gemini.md` entries. If a test fails there, update that test to reflect the new location of the rule — do not restore the legacy entries.

Run: `uv run --with pytest pytest -q -k "constants or Constants" -v`
to see the integrity tests specifically.

- [ ] **Step 7: Verify the end-to-end tag output by hand**

Run:

```bash
uv run --quiet python -c "
import sys; sys.path.insert(0,'src')
import panopticas as p
for f in ['CLAUDE.md','.claude/settings.json','.claude/skills/x/SKILL.md','AGENTS.md','.cursor/rules/a.mdc','.github/copilot-instructions.md','.github/workflows/ci.yml','pyproject.toml']:
    print(f'{f:38} -> {p.get_filename_metatypes(f)}')
"
```

Expected:

```
CLAUDE.md                              -> ['AI', 'Claude', 'instructions']
.claude/settings.json                  -> ['AI', 'Claude', 'config']
.claude/skills/x/SKILL.md              -> ['AI', 'Claude', 'skill']
AGENTS.md                              -> ['AI', 'Agents', 'instructions']
.cursor/rules/a.mdc                    -> ['AI', 'Cursor', 'rules']
.github/copilot-instructions.md        -> ['GitHub', 'Git', 'AI', 'Copilot', 'instructions']
.github/workflows/ci.yml               -> ['workflow', 'pipeline', 'GitHub', 'Git']
pyproject.toml                         -> ['build', 'dependencies', 'Python']
```

- [ ] **Step 8: Commit**

```bash
git add src/panopticas/constants.py src/panopticas/core.py tests/test_ai_detection.py
git commit -m "feat: emit AI tags from get_filename_metatypes()"
```

---

### Task 3: find_ai_files() directory walker

**Files:**
- Modify: `src/panopticas/core.py` (new function after `find_files()`, which ends at line 229)
- Modify: `src/panopticas/__init__.py`
- Test: `tests/test_ai_detection.py` (append)

**Interfaces:**
- Consumes: `core.get_ai_metadata()` from Task 1; existing `core.load_gitignore_patterns(directory)`.
- Produces: `core.find_ai_files(directory: str, all_files: bool = False) -> dict[str, dict]` — maps relative path to `{"product": str, "kind": str}`. Directory entries have a trailing `/` in their key and `kind == "directory"`.

- [ ] **Step 1: Write the failing tests**

Add `find_ai_files` to the existing `from panopticas import ...` block at the top of `tests/test_ai_detection.py`, then append:

```python
def _build_repo(root):
    """Create a small repo tree with AI artifacts and a .gitignore."""
    def write(relative_path, content=""):
        full = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(content)

    write("CLAUDE.md", "# guidance\n")
    write("AGENTS.md", "# agents\n")
    write("pyproject.toml", "[project]\n")
    write("src/app.py", "print('hi')\n")
    write(".claude/settings.json", "{}\n")
    write(".claude/skills/review/SKILL.md", "# skill\n")
    write(".cursor/rules/style.mdc", "rule\n")
    write(".gitignore", ".cursor/\nsecret.txt\n")
    write("secret.txt", "shh\n")


class TestFindAiFiles:
    """Directory walking, gitignore handling and bare directories."""

    def test_finds_ai_files_only(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            assert "CLAUDE.md" in found
            assert "AGENTS.md" in found
            assert "pyproject.toml" not in found
            assert os.path.join("src", "app.py") not in found

    def test_returns_product_and_kind(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            assert found["CLAUDE.md"] == {
                "product": "Claude", "kind": "instructions"}
            assert found[os.path.join(".claude", "settings.json")] == {
                "product": "Claude", "kind": "config"}
            assert found[os.path.join(".claude", "skills", "review", "SKILL.md")] == {
                "product": "Claude", "kind": "skill"}

    def test_honours_gitignore_by_default(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            # .cursor/ is gitignored, so its rule file must not appear.
            assert not any(".cursor" in path for path in found)

    def test_all_files_surfaces_ignored_files(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root, all_files=True)
            assert os.path.join(".cursor", "rules", "style.mdc") in found

    def test_all_files_emits_bare_directories(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root, all_files=True)
            cursor_dir = ".cursor" + os.sep
            assert cursor_dir in found
            assert found[cursor_dir] == {
                "product": "Cursor", "kind": "directory"}

    def test_default_emits_no_directories(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            found = find_ai_files(root)
            assert all(meta["kind"] != "directory" for meta in found.values())

    def test_empty_directory_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as root:
            assert find_ai_files(root) == {}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q -k FindAiFiles`
Expected: collection error — `ImportError: cannot import name 'find_ai_files'`

- [ ] **Step 3: Implement find_ai_files()**

Add to `src/panopticas/core.py` after `find_files()`:

```python
def find_ai_files(directory, all_files=False):
    """
    Find AI coding agent artifacts in a directory.

    Returns a dict of relative path -> {"product": str, "kind": str}.

    By default the walk honours .gitignore and returns files only. With
    all_files=True it ignores .gitignore and additionally returns one entry
    per known AI directory found on disk, keyed with a trailing separator
    and carrying kind "directory". That surfaces tooling a team has
    configured locally but excluded from the repo.
    """
    gitignore_spec = None if all_files else load_gitignore_patterns(directory)

    ai_files = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            if gitignore_spec and gitignore_spec.match_file(relative_path):
                continue
            metadata = get_ai_metadata(relative_path)
            if metadata:
                ai_files[relative_path] = metadata

        if all_files:
            for name in dirs:
                relative_dir = os.path.relpath(
                    os.path.join(root, name), directory) + os.sep
                metadata = get_ai_metadata(relative_dir)
                if metadata:
                    ai_files[relative_dir] = {
                        "product": metadata["product"], "kind": "directory"}

    return ai_files
```

- [ ] **Step 4: Export find_ai_files from `__init__.py`**

Add `find_ai_files,` to the `from .core import (...)` block (after `find_files,`) and `'find_ai_files',` to `__all__` (after `'find_files',`).

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/panopticas/core.py src/panopticas/__init__.py tests/test_ai_detection.py
git commit -m "feat: add find_ai_files() directory walker"
```

---

### Task 4: The `panopticas ai` command

**Files:**
- Modify: `src/panopticas/cli.py` (new command after `assess`, which ends at line 112)
- Test: `tests/test_ai_detection.py` (append)

**Interfaces:**
- Consumes: `core.find_ai_files(directory, all_files=False)` from Task 3.
- Produces: the `ai` CLI command. No importable API.

- [ ] **Step 1: Write the failing tests**

Add these to the import block at the top of `tests/test_ai_detection.py`:

```python
from click.testing import CliRunner

from panopticas.cli import cli
```

Then append:

```python
class TestAiCommand:
    """The `panopticas ai` CLI command."""

    def test_lists_ai_files(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            result = CliRunner().invoke(cli, ["ai", root])
            assert result.exit_code == 0
            assert "CLAUDE.md" in result.output
            assert "Claude" in result.output
            assert "instructions" in result.output

    def test_omits_non_ai_files(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            result = CliRunner().invoke(cli, ["ai", root])
            assert "pyproject.toml" not in result.output

    def test_summary_counts_products(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            result = CliRunner().invoke(cli, ["ai", root])
            assert "Claude (3)" in result.output
            assert "Agents (1)" in result.output

    def test_all_files_flag_includes_ignored(self):
        with tempfile.TemporaryDirectory() as root:
            _build_repo(root)
            result = CliRunner().invoke(cli, ["ai", root, "--all-files"])
            assert "Cursor" in result.output

    def test_empty_directory_reports_zero(self):
        with tempfile.TemporaryDirectory() as root:
            result = CliRunner().invoke(cli, ["ai", root])
            assert result.exit_code == 0
            assert "Found 0 AI files." in result.output

    def test_rejects_a_file_argument(self):
        with tempfile.TemporaryDirectory() as root:
            target = os.path.join(root, "CLAUDE.md")
            with open(target, "w", encoding="utf-8") as handle:
                handle.write("# guidance\n")
            result = CliRunner().invoke(cli, ["ai", target])
            # click.Path(file_okay=False) rejects it rather than silently
            # walking nothing and reporting an AI-free repo.
            assert result.exit_code != 0

    def test_rejects_a_missing_directory(self):
        result = CliRunner().invoke(cli, ["ai", "/no/such/directory"])
        assert result.exit_code != 0


class TestDisplaySanitisation:
    """Paths come from repositories panopticas does not control."""

    def test_strips_escape_character(self):
        assert sanitise_for_display("\x1b[31mred") == "[31mred"

    def test_strips_other_control_bytes(self):
        assert sanitise_for_display("a\x00b\x07c\rd\x7f") == "abcd"

    def test_leaves_ordinary_paths_untouched(self):
        assert sanitise_for_display(".claude/settings.json") == \
            ".claude/settings.json"

    def test_ai_command_output_has_no_escape_sequences(self):
        with tempfile.TemporaryDirectory() as root:
            evil_dir = os.path.join(root, "\x1b[31mnotes")
            os.makedirs(evil_dir)
            with open(os.path.join(evil_dir, "CLAUDE.md"), "w",
                      encoding="utf-8") as handle:
                handle.write("# guidance\n")
            result = CliRunner().invoke(cli, ["ai", root])
            assert result.exit_code == 0
            assert "\x1b" not in result.output
            assert "CLAUDE.md" in result.output
```

Add `sanitise_for_display` to the `from panopticas.cli import ...` line so it
reads `from panopticas.cli import cli, sanitise_for_display`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q -k AiCommand`
Expected: FAIL — exit code 2, `Error: No such command 'ai'.`

- [ ] **Step 3: Implement the command**

Add `import re` to the imports at the top of `src/panopticas/cli.py`, then add
this helper and the command after `assess`:

```python
# Filenames may contain almost any byte, and panopticas scans repositories
# it does not control. An escape sequence in a path would be interpreted by
# the terminal rather than displayed, letting a crafted filename rewrite what
# the operator sees. Strip ESC and the other control bytes before printing.
CONTROL_CHARACTERS = re.compile(r'[\x00-\x1f\x7f]')


def sanitise_for_display(text):
    """Remove control characters and ANSI escapes from text bound for a terminal."""
    return CONTROL_CHARACTERS.sub('', text)


@cli.command("ai")
@click.option('--all-files', is_flag=True, default=False,
              help="Include gitignored files and bare AI directories.")
@click.argument('directory', required=False,
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def ai(directory, all_files):
    """Find AI coding agent files and directories."""
    click.echo()
    if directory:
        click.echo(f'Assessing directory: {directory}')
    else:
        click.echo('Assessing current directory.')
        directory = "."
    click.echo()

    ai_files = core.find_ai_files(directory, all_files=all_files)

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

    # Summarise which products the repo uses, most-used first.
    counts = {}
    for metadata in ai_files.values():
        counts[metadata["product"]] = counts.get(metadata["product"], 0) + 1

    if counts:
        products = ", ".join(
            f"{product} ({count})" for product, count in
            sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        )
        print(f"Found {len(ai_files)} AI files. Products: {products}")
    else:
        print("Found 0 AI files.")

    print()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q`
Expected: PASS

- [ ] **Step 5: Run the command against this repo by hand**

Run: `uv run --quiet python -m panopticas.cli ai .`

Expected: a table listing `CLAUDE.md` as `Claude / instructions`, plus any `.claude/` files present, and a summary line. Then:

Run: `uv run --quiet python -m panopticas.cli ai . --all-files`
Expected: additionally lists any gitignored AI files and bare AI directories.

Run: `uv run --quiet python -m panopticas.cli assess . | head -20`
Expected: the Meta column now shows `AI, Claude, instructions` for `CLAUDE.md`.

- [ ] **Step 6: Commit**

```bash
git add src/panopticas/cli.py tests/test_ai_detection.py
git commit -m "feat: add panopticas ai command"
```

---

### Task 5: Tier 2 product rules

Adds the remaining ~15 products. Each entry is a claim about a third-party product's conventions, so this task **verifies before adding**.

**Files:**
- Modify: `src/panopticas/constants.py` (`AI_RULES`)
- Test: `tests/test_ai_detection.py` (append)

**Interfaces:**
- Consumes: `constants.AI_RULES` and `core.get_ai_metadata()` from Task 1.
- Produces: additional `AI_RULES` entries. No API change.

- [ ] **Step 1: Verify each candidate convention**

For each product below, confirm the indicator against its **current official documentation** before adding it. Use WebSearch/WebFetch. Record the source URL in the commit message.

**Drop any entry you cannot confirm.** A wrong rule is worse than a missing one: it mislabels a repo, and the label flows into kospex where someone will act on it.

| Product | Candidate indicators | Confidence |
|---|---|---|
| Windsurf | `.windsurfrules`, `.windsurf/rules/`, `.windsurf/`, `.codeiumignore` | high |
| Aider | `.aider.conf.yml`, `.aiderignore`, `.aider.chat.history.md`, `.aider.input.history` | high |
| Cline | `.clinerules`, `.clinerules/` | high |
| Continue | `.continue/`, `.continuerc.json` | high |
| Roo Code | `.roorules`, `.roo/rules/`, `.roo/` | medium |
| Amazon Q | `.amazonq/rules/`, `.amazonq/`, `amazonq.md` | medium |
| Goose | `.goosehints`, `.goose/` | medium |
| Junie | `.junie/` | low — verify |
| Augment | `.augment-guidelines`, `.augment/` | low — verify |
| OpenHands | `.openhands/microagents/`, `.openhands/` | low — verify |
| Qodo | `.qodo/` | low — verify |
| Kilo Code | `.kilocode/rules/`, `.kilocode/` | low — verify |
| Trae | `.trae/rules/`, `.trae/` | low — verify |
| Gemini | `.geminiignore` | low — verify |

- [ ] **Step 2: Write the failing tests for the confirmed entries**

Append to `tests/test_ai_detection.py`. Include a case **only for entries Step 1 confirmed** — delete the rest.

```python
class TestTier2Products:
    """Established AI agents beyond the majors."""

    @pytest.mark.parametrize("path,product,kind", [
        (".windsurfrules", "Windsurf", "rules"),
        (".windsurf/rules/style.md", "Windsurf", "rules"),
        (".codeiumignore", "Windsurf", "ignore"),
        (".aider.conf.yml", "Aider", "config"),
        (".aiderignore", "Aider", "ignore"),
        (".aider.chat.history.md", "Aider", "history"),
        (".clinerules", "Cline", "rules"),
        (".clinerules/general.md", "Cline", "rules"),
        (".continue/config.yaml", "Continue", "config"),
        (".roo/rules/style.md", "Roo Code", "rules"),
        (".amazonq/rules/style.md", "Amazon Q", "rules"),
        (".goosehints", "Goose", "instructions"),
    ])
    def test_tier2_detection(self, path, product, kind):
        assert get_ai_metadata(path) == {"product": product, "kind": kind}
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q -k Tier2`
Expected: FAIL — every case returns `None`.

- [ ] **Step 4: Add the confirmed entries to AI_RULES**

Add to the relevant sections of `AI_RULES` in `src/panopticas/constants.py`. Add only what Step 1 confirmed.

Into `"exact_filename"`:

```python
        # Windsurf — Codeium
        ".windsurfrules": ("Windsurf", "rules"),
        ".codeiumignore": ("Windsurf", "ignore"),
        # Aider
        ".aider.conf.yml": ("Aider", "config"),
        ".aiderignore": ("Aider", "ignore"),
        ".aider.chat.history.md": ("Aider", "history"),
        ".aider.input.history": ("Aider", "history"),
        # Cline
        ".clinerules": ("Cline", "rules"),
        # Roo Code
        ".roorules": ("Roo Code", "rules"),
        # Continue
        ".continuerc.json": ("Continue", "config"),
        # Goose — Block
        ".goosehints": ("Goose", "instructions"),
```

Into `"path_contains"`:

```python
        # Windsurf
        ".windsurf/rules/": ("Windsurf", "rules"),
        ".windsurf/": ("Windsurf", "config"),
        # Cline
        ".clinerules/": ("Cline", "rules"),
        # Roo Code
        ".roo/rules/": ("Roo Code", "rules"),
        ".roo/": ("Roo Code", "config"),
        # Continue
        ".continue/": ("Continue", "config"),
        # Amazon Q — AWS
        ".amazonq/rules/": ("Amazon Q", "rules"),
        ".amazonq/": ("Amazon Q", "config"),
        # Goose
        ".goose/": ("Goose", "config"),
```

Plus any low-confidence entries Step 1 confirmed, following the same
`(product, kind)` shape. If Step 1 confirmed `.junie/`, for example, add
`".junie/": ("Junie", "config"),` to `"path_contains"`.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --with pytest pytest tests/test_ai_detection.py -q`
Expected: PASS. The `TestAiRulesIntegrity` cases from Task 1 also run here and will catch a malformed entry, a kind outside the vocabulary, or a key duplicated across match modes.

- [ ] **Step 6: Check for accidental over-matching**

Run the detector across this repo and eyeball the result for false positives:

```bash
uv run --quiet python -m panopticas.cli ai . --all-files
```

Expected: only genuine AI artifacts listed. If an ordinary source file appears, the responsible rule is too broad — tighten or remove it.

- [ ] **Step 7: Commit**

```bash
git add src/panopticas/constants.py tests/test_ai_detection.py
git commit -m "feat: add Tier 2 AI product detection rules"
```

Include the documentation URLs used to verify each product in the commit body, and note explicitly which candidates were dropped as unconfirmed.

---

### Task 6: Documentation and release prep

**Files:**
- Create: `changes/202607-ai-agent-detection.md`
- Modify: `CHANGELOG.md`, `README.md`, `pyproject.toml:7`

**Interfaces:**
- Consumes: everything from Tasks 1-5.
- Produces: no code.

- [ ] **Step 1: Run the full suite one final time**

Run: `uv run --with pytest pytest -q`
Expected: all pass. Record the total count — it goes in the changelog.

- [ ] **Step 2: Write the change document**

Create `changes/202607-ai-agent-detection.md`:

```markdown
# AI Coding Agent Detection

## Summary

Panopticas now detects the file and directory artifacts of ~20 AI coding
agent products and tags each with `AI`, the product brand, and the kind of
artifact it is.

Before, only two AI files were recognised — `claude.md` and `gemini.md`.

## Tag shape

Every recognised artifact emits three tags:

    CLAUDE.md              -> ["AI", "Claude", "instructions"]
    .claude/settings.json  -> ["AI", "Claude", "config"]
    .cursor/rules/x.mdc    -> ["AI", "Cursor", "rules"]

Products are brand-level: `Claude` covers both Claude Code and Claude
Desktop, so one tag finds all Anthropic tooling. Files owned by no brand
use a pseudo-product — `Agents` for `AGENTS.md`, `MCP` for `.mcp.json`.

## New API

- `get_ai_metadata(file_path)` — returns `{"product", "kind"}` or `None`.
  Pure path inspection; the file is never opened.
- `find_ai_files(directory, all_files=False)` — walks a directory,
  returning path -> metadata. With `all_files=True` it ignores
  `.gitignore` and also reports bare AI directories.

## New CLI command

    panopticas ai [DIRECTORY]
    panopticas ai --all-files

Lists AI artifacts with their product and kind, and summarises which
products the repository uses.

## kospex impact

None required. kospex calls `get_filename_metatypes()`, which now includes
the AI tags, stored as `|AI|Claude|instructions|` in `tech_type`. The
existing `tech_type LIKE '%|AI|%'` query finds every AI file; swapping in
a product name narrows to one brand.

`last_panopticas_version` tracking means a version bump re-tags already
synced repos automatically.

## Breaking change

`CLAUDE.md` previously emitted `["Claude", "AI", "Claude Code"]` and now
emits `["AI", "Claude", "instructions"]`. The bare `Claude Code` tag is
gone. Verified that nothing in kospex queries it.

## Design

See `changes/design/specs/2026-07-31-ai-agent-detection-design.md`.
```

- [ ] **Step 3: Add the CHANGELOG entry**

Insert into `CHANGELOG.md` directly above the `## 0.0.16 - 2026-05-21` heading, following the existing Keep a Changelog style:

```markdown
## 0.0.17 - 2026-07-31

### Added
 - AI coding agent detection — ~20 products detected via a new `AI_RULES` table, tagging artifacts with `AI`, the product brand, and the artifact kind (e.g. `AI, Claude, instructions`)
 - `panopticas ai [DIRECTORY]` command listing AI files with their product and kind, plus a summary of which AI products the repo uses; `--all-files` additionally reports gitignored files and bare AI directories
 - `get_ai_metadata(file_path)` returning `{"product", "kind"}` or `None` for a path
 - `find_ai_files(directory, all_files=False)` returning path -> AI metadata for a directory tree
 - Test coverage for AI detection, precedence, tag output and rules-table integrity

### Changed
 - `CLAUDE.md` now tags as `AI, Claude, instructions` (was `Claude, AI, Claude Code`) and `GEMINI.md` as `AI, Gemini, instructions` (was `Gemini, AI, Gemini CLI`) — product tags are now brand-level and consistent across all AI entries
 - AI detection rules moved out of `METADATA_RULES` into the dedicated `AI_RULES` table
```

Replace `2026-07-31` with the actual release date if it differs.

- [ ] **Step 4: Document the command in README.md**

Add to the CLI examples section, following the format of the existing entries:

```markdown
# Find AI coding agent files and directories
panopticas ai
panopticas ai /path/to/directory
panopticas ai --all-files
```

- [ ] **Step 5: Bump the version**

In `pyproject.toml`, change line 7 from `version = "0.0.16"` to `version = "0.0.17"`.

- [ ] **Step 6: Verify the version is picked up**

Run: `uv run --quiet python -m panopticas.cli --version`
Expected: reports `0.0.17`.

Note: `VERSION` resolves through `importlib.metadata`, so it reflects the
*installed* package. If it still shows 0.0.16, reinstall with
`pip install -e .` — that is an environment artifact, not a code bug.

- [ ] **Step 7: Commit**

```bash
git add CHANGELOG.md README.md changes/202607-ai-agent-detection.md pyproject.toml
git commit -m "docs: document AI agent detection and bump to 0.0.17"
```

- [ ] **Step 8: Final verification**

Run: `uv run --with pytest pytest -q`
Expected: all pass.

Run: `git status --short`
Expected: only the three pre-existing untracked files — `.safety-project.ini`, `ideas/`, `uv.lock`. These are deliberately uncommitted; leave them alone.

---

## Out of Scope

Do not implement these — they were explicitly excluded during design:

- Content-based detection (reading files for AI attribution markers)
- A stored repo-level AI rollup — `find_ai_files()` is exported if kospex wants to build one
- A `--json` flag on the `ai` command
- Policy judgements about whether an AI file belongs in a given location
- Tightening `click.Path` on the existing `assess` and `urls` commands — same loose constraint, but a separate change
