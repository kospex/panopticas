# AI Coding Agent Detection — Design

**Date:** 2026-07-31
**Status:** Approved, ready for implementation planning

## Problem

Panopticas detects two AI coding agent files: `claude.md` and `gemini.md`. Everything
else an AI agent leaves in a repository — `.claude/`, `AGENTS.md`, `.cursor/rules/`,
`.github/copilot-instructions.md`, MCP configs — is invisible.

Current behaviour:

```
CLAUDE.md                       -> ['Claude', 'AI', 'Claude Code']
.claude/settings.json           -> []
.claude/skills/x/SKILL.md       -> []
AGENTS.md                       -> []
.cursor/rules/a.mdc             -> []
.github/copilot-instructions.md -> ['GitHub', 'Git']
```

The two existing entries are also inconsistent: `claude.md` emits both `Claude` and
`Claude Code`, which overlap and mean the same thing.

## Goal

Detect the file and directory artifacts of roughly 20 AI coding agent products. Tag
each with `AI`, the product brand, and the kind of artifact it is. Expose a
`panopticas ai` command that answers "which AI tools does this repo use?".

Detection is **path-based only** — filenames, directories and suffixes. Panopticas
detects and tags; it does not judge whether a file should be there. File contents are
never read for AI detection.

## Decisions

| Decision | Choice |
|---|---|
| Tag shape | `["AI", product, kind]` — three tags |
| Product granularity | Brand level (`Claude`, not `Claude Code`/`Claude Desktop`) |
| Vendor-neutral files | Pseudo-product tag (`Agents`, `MCP`, `llms.txt`) |
| Coverage | Tier 1 + Tier 2 — ~20 products, ~60 rules |
| Architecture | Dedicated `AI_RULES` table, tags derived from it |
| Query surfaces | File tags (via existing functions) + new `panopticas ai` command |
| Gitignored dirs | Reported only under `--all-files` |
| Legacy `Claude`/`Gemini` tags | Dropped — nothing in kospex queries them |

### Why brand-level products

`Claude Code` and `Claude Desktop` are distinct products with distinct files —
Claude Code owns `CLAUDE.md` and `.claude/`, Claude Desktop owns only
`claude_desktop_config.json`. Both tag as `Claude` so a single
`tech_type LIKE '%|Claude|%'` query in kospex finds all Anthropic tooling. The same
rule applies across the table: `Gemini` covers Gemini CLI and Gemini Code Assist,
`Copilot` covers all GitHub Copilot surfaces.

### Why a separate `AI_RULES` table

The alternative — adding ~60 entries to the existing `exact_filename_rules` and
`path_contains_rules` — was rejected for three reasons:

1. **The `.github/` collision.** `path_contains_rules` stops at the first match
   (`core.py:57`). An AI rule for `.github/prompts/` would match and `break` before
   the generic `.github` rule, silently stripping the `GitHub` and `Git` tags those
   files get today. A separate table runs as its own pass, so both fire.
2. **Positional tag reading.** The `ai` command would have to locate the product at
   `tags[1]`, which breaks on any file that also picks up extension or path tags.
3. **Duplication.** The product string would be retyped once per rule, inviting
   typos across 60 entries.

## Architecture

### `constants.py` — the rules table

```python
AI_RULES = {
    "exact_filename":  { "<basename>": (product, kind) },   # lowercased basename
    "path_contains":   { "<fragment>": (product, kind) },   # longest match wins
    "filename_suffix": { "<suffix>":   (product, kind) },
}
```

**Precedence:** exact filename → longest `path_contains` match → suffix. First hit
wins; exactly one `(product, kind)` per path. No merging, so a file is never
ambiguously two products.

The legacy `claude.md` and `gemini.md` entries are **removed** from
`METADATA_RULES["exact_filename_rules"]` and re-expressed here, so AI knowledge lives
in exactly one place.

### `core.py` — three additions

```python
def get_ai_metadata(file_path):
    """
    Return {"product": str, "kind": str} for a recognised AI coding agent
    artifact, or None. Pure path inspection — never opens the file.
    """
```

Single source of truth. Everything else derives from it.

```python
def get_filename_metatypes(file_path):   # existing, extended
```

Gains one block at the end: call `get_ai_metadata()` and, on a match, append
`["AI", product, kind]`. Runs *after* the existing extension / filename / path /
function rules, leaving the `path_contains_rules` block and its `break` untouched.

```python
def find_ai_files(directory, all_files=False):
    """
    Walk a directory, returning {relative_path: {"product":…, "kind":…}}
    for every recognised AI artifact.

    all_files=False (default): honours .gitignore, files only.
    all_files=True: ignores .gitignore, and additionally emits one row per
    known AI directory present on disk, with kind="directory".
    """
```

Follows the existing `find_files(directory, all_files=None)` shape and reuses
`load_gitignore_patterns()`.

All three are exported from `__init__.py`.

### `cli.py` — the `ai` command

```python
@cli.command("ai")
@click.option('--all-files', is_flag=True, default=False,
              help="Include gitignored files and bare AI directories.")
@click.argument('directory', required=False, type=click.Path(exists=True))
def ai(directory, all_files):
    """Find AI coding agent files and directories."""
```

Mirrors `assess`: optional directory defaulting to `.`, PrettyTable output,
left-aligned columns, summary line.

```
$ panopticas ai

Assessing current directory.

+---------------------------------+---------+--------------+
| Path                            | Product | Kind         |
+---------------------------------+---------+--------------+
| CLAUDE.md                       | Claude  | instructions |
| AGENTS.md                       | Agents  | instructions |
| .claude/settings.json           | Claude  | config       |
| .claude/skills/review/SKILL.md  | Claude  | skill        |
| .github/copilot-instructions.md | Copilot | instructions |
| .cursor/rules/style.mdc         | Cursor  | rules        |
+---------------------------------+---------+--------------+

Found 6 AI files. Products: Claude (4), Copilot (1), Cursor (1)
```

The column is `Path`, not `File`, because `--all-files` can yield directories.

No `--json` flag — `find_ai_files()` is exported for programmatic use. Easy to add
later.

## Kind vocabulary

Fixed set of 14 values. A rule may not introduce a kind outside this list.

| Kind | Meaning |
|---|---|
| `instructions` | Natural-language guidance for an agent (`CLAUDE.md`, `AGENTS.md`) |
| `config` | Tool configuration (`settings.json`, `.aider.conf.yml`) |
| `rules` | Rule/policy files (`.cursorrules`, `.clinerules`) |
| `prompt` | Reusable prompt (`.github/prompts/*.prompt.md`) |
| `chatmode` | Chat mode definition (`.github/chatmodes/`) |
| `command` | Slash command definition (`.claude/commands/`) |
| `agent` | Subagent definition (`.claude/agents/`) |
| `skill` | Skill definition (`.claude/skills/`) |
| `hook` | Lifecycle hook (`.claude/hooks/`) |
| `plugin` | Plugin bundle (`.claude/plugins/`) |
| `ignore` | Exclusion file (`.cursorignore`, `.aiexclude`) |
| `history` | Session/chat transcript (`.aider.chat.history.md`) |
| `docs` | LLM-oriented documentation (`llms.txt`) |
| `directory` | Bare AI directory, emitted only under `--all-files` |

## Rules table

Entries marked **(verify)** rest on convention knowledge that may have drifted and
must be confirmed against current product documentation before shipping. Anything
that cannot be confirmed is dropped, not guessed.

### Tier 1

**Claude** — Anthropic

| Mode | Key | Kind |
|---|---|---|
| exact | `claude.md` | instructions |
| exact | `claude.local.md` | instructions |
| exact | `claude_desktop_config.json` | config |
| path | `.claude/skills/` | skill |
| path | `.claude/agents/` | agent |
| path | `.claude/commands/` | command |
| path | `.claude/hooks/` | hook |
| path | `.claude/plugins/` | plugin |
| path | `.claude/` | config |

**Copilot** — GitHub

| Mode | Key | Kind |
|---|---|---|
| exact | `copilot-instructions.md` | instructions |
| path | `.github/instructions/` | instructions |
| path | `.github/prompts/` | prompt |
| path | `.github/chatmodes/` | chatmode |
| suffix | `.instructions.md` | instructions |
| suffix | `.prompt.md` | prompt |
| suffix | `.chatmode.md` | chatmode |

**Cursor** — Anysphere

| Mode | Key | Kind |
|---|---|---|
| exact | `.cursorrules` | rules |
| exact | `.cursorignore` | ignore |
| exact | `.cursorindexingignore` | ignore |
| path | `.cursor/rules/` | rules |
| path | `.cursor/` | config |
| suffix | `.mdc` | rules |

**Gemini** — Google

| Mode | Key | Kind |
|---|---|---|
| exact | `gemini.md` | instructions |
| exact | `.aiexclude` | ignore |
| exact | `.geminiignore` | ignore *(verify)* |
| path | `.gemini/` | config |

**Codex** — OpenAI

| Mode | Key | Kind |
|---|---|---|
| path | `.codex/` | config |

### Tier 2

| Product | Mode | Key | Kind |
|---|---|---|---|
| Windsurf | exact | `.windsurfrules` | rules |
| Windsurf | exact | `.codeiumignore` | ignore |
| Windsurf | path | `.windsurf/rules/` | rules |
| Windsurf | path | `.windsurf/` | config |
| Aider | exact | `.aider.conf.yml` | config |
| Aider | exact | `.aiderignore` | ignore |
| Aider | exact | `.aider.chat.history.md` | history |
| Aider | exact | `.aider.input.history` | history |
| Cline | exact | `.clinerules` | rules |
| Cline | path | `.clinerules/` | rules |
| Roo Code | exact | `.roorules` | rules |
| Roo Code | path | `.roo/rules/` | rules |
| Roo Code | path | `.roo/` | config |
| Continue | exact | `.continuerc.json` | config |
| Continue | path | `.continue/` | config |
| Amazon Q | exact | `amazonq.md` | instructions *(verify)* |
| Amazon Q | path | `.amazonq/rules/` | rules |
| Amazon Q | path | `.amazonq/` | config |
| Junie | path | `.junie/` | config *(verify)* |
| Goose | exact | `.goosehints` | instructions |
| Goose | path | `.goose/` | config |
| Augment | exact | `.augment-guidelines` | instructions *(verify)* |
| Augment | path | `.augment/` | config *(verify)* |
| OpenHands | path | `.openhands/microagents/` | agent *(verify)* |
| OpenHands | path | `.openhands/` | config *(verify)* |
| Qodo | path | `.qodo/` | config *(verify)* |
| Kilo Code | path | `.kilocode/rules/` | rules *(verify)* |
| Kilo Code | path | `.kilocode/` | config *(verify)* |
| Trae | path | `.trae/rules/` | rules *(verify)* |
| Trae | path | `.trae/` | config *(verify)* |

### Vendor-neutral (pseudo-products)

| Product | Mode | Key | Kind |
|---|---|---|---|
| Agents | exact | `agents.md` | instructions |
| Agents | exact | `.aiignore` | ignore |
| MCP | exact | `.mcp.json` | config |
| MCP | path | `.vscode/mcp.json` | config |
| llms.txt | exact | `llms.txt` | docs |
| llms.txt | exact | `llms-full.txt` | docs |

`.cursor/mcp.json` is deliberately absent — the `.cursor/` path rule already claims
it for Cursor, which is the more useful attribution.

## Resulting behaviour

```
CLAUDE.md                       -> ['AI', 'Claude', 'instructions']
.claude/settings.json           -> ['AI', 'Claude', 'config']
.claude/skills/x/SKILL.md       -> ['AI', 'Claude', 'skill']
AGENTS.md                       -> ['AI', 'Agents', 'instructions']
.cursor/rules/a.mdc             -> ['AI', 'Cursor', 'rules']
.github/copilot-instructions.md -> ['GitHub', 'Git', 'AI', 'Copilot', 'instructions']
.github/workflows/ci.yml        -> ['workflow', 'pipeline', 'GitHub', 'Git']   # unchanged
pyproject.toml                  -> ['build', 'dependencies', 'Python']         # unchanged
```

## kospex integration

**No kospex code or schema change is required.**

- `kospex_git.py:539` calls `get_filename_metatypes()` and stores the result as
  `tech_type`.
- `kospex_schema.py:550` runs it through `array_to_db_tags()`, producing
  `|AI|Claude|instructions|`.
- `kospex_query.py:2364` already queries `tech_type LIKE '%|{tag}|%'`.

So `tag = "AI"` returns every AI-tagged file and `tag = "Claude"` narrows to one
brand, using machinery that already exists.

`kospex_core.py:1074` tracks `last_panopticas_version` and re-syncs when it changes,
so bumping the panopticas version re-tags already-synced repos automatically.

Verified: nothing in kospex hardcodes a `Claude`, `Gemini` or `AI` tag, so dropping
the redundant bare `Claude` tag breaks no downstream consumer.

`panopticas assess` also gains the AI tags in its Meta column with no change to the
`assess` command, because it calls the same `get_filename_metatypes()`.

## Testing

New `tests/test_ai_detection.py`, class-per-function to match the existing style in
`tests/test_panopticas.py`.

**`TestGetAiMetadata`**
- One assertion per product for exact, path and suffix matches
- `None` for ordinary files (`pyproject.toml`, `src/panopticas/core.py`, `README.md`)
- Precedence: exact beats path; `.claude/skills/` beats `.claude/`
- Case-insensitivity: `CLAUDE.md` and `claude.md` both match

**`TestAiTagsInMetatypes`**
- `get_filename_metatypes()` emits `['AI', product, kind]` for AI paths
- Regression guard: `.github/copilot-instructions.md` retains `GitHub` and `Git`
  alongside the AI tags
- Regression guard: `.github/workflows/ci.yml` and `pyproject.toml` produce output
  identical to current behaviour

**`TestFindAiFiles`**
- Temp tree with a `.gitignore`; default honours it
- `all_files=True` surfaces ignored files and emits bare directories with
  kind `directory`

**`TestAiRulesIntegrity`** — guards the table against rot as entries are added
- Every value is a 2-tuple of non-empty strings
- Every kind is in the fixed vocabulary
- Every `path_contains` key contains a `/` (either a directory fragment ending in
  `/`, or a dir-qualified filename such as `.vscode/mcp.json`); every
  `filename_suffix` key starts with `.`
- Every `exact_filename` key is lowercase
- No key appears in more than one match mode

## Risks

1. **Convention accuracy.** Entries marked *(verify)* must be confirmed against
   current product documentation during implementation. Drop what cannot be
   confirmed.
2. **Substring path matching.** `path_contains` uses plain substring matching,
   inherited from the existing rules. `.claude/` matches `vendor/.claude/x` — still
   a Claude artifact, so acceptable, and consistent with how `.github` behaves today.
3. **The `.mdc` suffix.** Mapping `*.mdc` to Cursor anywhere is a mild over-reach;
   the extension is not formally reserved. Kept because `.mdc` has no meaningful
   competing use, but it is the one suffix rule worth revisiting if false positives
   appear.
4. **Tag count growth.** `tech_type` gains up to three tags per AI file. It is a TEXT
   column queried with `LIKE`, so there is no schema pressure.

## Out of scope

- **Content-based detection.** No reading files for AI attribution markers
  (e.g. "Generated with Claude Code" in a commit or header). Path-based only.
- **Repo-level aggregation API.** The `ai` command summarises per invocation;
  no stored repo-level rollup. `find_ai_files()` is exported if kospex wants to
  build one.
- **Policy judgements.** Panopticas reports what it finds. Rules about whether an AI
  file belongs in a given location live in kospex.

## Delivery

1. `AI_RULES` table in `constants.py`; remove the two legacy entries from
   `METADATA_RULES`
2. `get_ai_metadata()` and `find_ai_files()` in `core.py`; extend
   `get_filename_metatypes()`
3. Export all three from `__init__.py`
4. `ai` command in `cli.py`
5. `tests/test_ai_detection.py`
6. `changes/202607-ai-agent-detection.md`, `CHANGELOG.md` entry, `README.md` line
7. Minor version bump in `pyproject.toml`
