# AI Coding Agent Detection

## Summary

Panopticas now detects the file and directory artifacts of 20 AI coding
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
gone. `GEMINI.md` previously emitted `["Gemini", "AI", "Gemini CLI"]` and
now emits `["AI", "Gemini", "instructions"]`. The bare `Gemini CLI` tag is
gone. Verified that nothing in kospex queries either.

## Numbers

60 detection rules across 20 products: Agents, Aider, Amazon Q, Augment,
Claude, Cline, Codex, Continue, Copilot, Cursor, Gemini, Goose, Junie,
Kilo Code, MCP, OpenHands, Roo Code, Trae, Windsurf, llms.txt. `Agents`,
`MCP` and `llms.txt` are deliberate pseudo-products for vendor-neutral
files, not real brands. 235 tests pass at release (up from 130 before
this branch).

## Design

See `docs/superpowers/specs/2026-07-31-ai-agent-detection-design.md`.
