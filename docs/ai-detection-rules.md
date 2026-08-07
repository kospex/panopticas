# AI Coding Agent Detection — Rules Reference

**Rules verified:** 2026-08-01 (panopticas 0.0.17)
**Inventory below generated from:** `AI_RULES` in `src/panopticas/constants.py`

Panopticas detects the file and directory artifacts of AI coding agents and tags
each with three tags: `AI`, the product brand, and the kind of artifact.

```
CLAUDE.md                       -> ['AI', 'Claude', 'instructions']
.cursor/rules/style.mdc         -> ['AI', 'Cursor', 'rules']
.github/copilot-instructions.md -> ['GitHub', 'Git', 'AI', 'Copilot', 'instructions']
```

This document is the **reference and evidence base**: what is detected, the source
that confirms each convention, and — equally important — what was rejected and why.

> For the *principles* governing additions, see `CLAUDE.md` → *AI Agent Detection*.
> For the original design rationale, see
> `docs/superpowers/specs/2026-07-31-ai-agent-detection-design.md` — but note its
> proposed rule table predates verification and contains entries that were
> subsequently rejected. **This document supersedes that table.**

## How matching works

Three match modes, resolved in this precedence order. First hit wins; exactly one
`(product, kind)` per path.

| Order | Mode | Matched against |
|---|---|---|
| 1 | `exact_filename` | the lowercased basename |
| 2 | `path_contains` | a substring of the lowercased path — **longest match wins** |
| 3 | `filename_suffix` | the end of the lowercased basename — longest wins |

Detection is **path-based only**. A file is never opened to determine AI metadata.

Products are **brand-level**: `Claude` covers both Claude Code and Claude Desktop,
`Gemini` covers the CLI and Code Assist. Files owned by no vendor use a
pseudo-product — `Agents`, `MCP`, `llms.txt`.

## The rejected list

**This is the most important section for anyone extending the rules.** Each entry
below was proposed, investigated, and rejected. Re-adding one would mislabel
repositories.

| Candidate | Proposed as | Rejected because | Source |
|---|---|---|---|
| `.goose/` | Goose config directory | **User-level, not a repository artifact.** Goose stores global config at `~/.config/goose`; the docs describe no repo-local `.goose/` directory. Only `.goosehints` is repo-local, and that *is* detected. | https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/ |
| `.qodo/` | Qodo config directory | **User-level, not a repository artifact** — a home-directory cache. Qodo is the only candidate product rejected entirely; it contributes no rules. | Qodo docs |
| `.clinerules` (single file) | Cline rules file | Current Cline docs describe **only** the `.clinerules/` *directory* form at the project root. The single-file variant could not be confirmed as still read. The directory form is detected. | https://docs.cline.bot/customization/cline-rules |
| `amazonq.md` | Amazon Q instructions file | Could not be confirmed against current AWS documentation. `.amazonq/rules/` is documented and is detected. | https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/context-project-rules.html |

`tests/test_ai_detection.py` contains negative tests asserting these return `None`,
so re-adding one fails the suite rather than shipping silently.

### The user-level trap

Two of the four rejections share a cause worth naming. A path like
`~/.config/<tool>/` or `~/.<tool>/` is **not** a repository artifact — panopticas
scans repositories, so such a rule would essentially never fire, and if it did the
match would mean something different from what the tag claims.

Several *detected* products have a user-level twin (`~/.junie/AGENTS.md`,
`~/.augment/rules/`, `~/.codeium/.codeiumignore`, `~/.config/goose/.goosehints`).
Those rules are sound because the repository-level form is **separately and
explicitly documented**. Check for that before adding.

## Sources by product

Every rule was checked against the product's own current documentation before being
added. Weak evidence — a blog post, a third-party listicle — was treated as a lead
to confirm elsewhere, never as confirmation.

| Product | Source |
|---|---|
| Aider | https://aider.chat/docs/config/aider_conf.html |
| Amazon Q | https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/context-project-rules.html |
| Augment | https://docs.augmentcode.com/setup-augment/guidelines |
| Cline | https://docs.cline.bot/customization/cline-rules |
| Continue | https://docs.continue.dev/customize/deep-dives/rules |
| Gemini | https://github.com/google-gemini/gemini-cli — `docs/gemini-ignore.md` |
| Goose | https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/ |
| Junie | https://junie.jetbrains.com/docs/guidelines-and-memory.html |
| Kilo Code | https://github.com/Kilo-Org/kilocode — `custom-rules.md` |
| OpenHands | https://docs.openhands.dev/usage/prompting/microagents-overview |
| Roo Code | https://roocodeinc.github.io/Roo-Code/features/custom-instructions |
| Trae | https://docs.trae.cn/ide/rules |
| Windsurf | https://docs.devin.ai/desktop/cascade/memories |

Claude, Copilot, Cursor, Codex and the vendor-neutral pseudo-products were treated
as well-established and not individually cited.

### Vendors that have moved or rebranded

Documentation hosts change more often than file conventions do. Confirmed during
the 0.0.17 verification pass:

| Product | Docs moved | Note |
|---|---|---|
| Windsurf | `docs.windsurf.com` → `docs.devin.ai` | Cognition/Devin. `.windsurfrules` is described as legacy but still read; `.devin/rules/` is preferred. Brand name kept as `Windsurf` — the filenames belong to that era. |
| Kilo Code | `kilocode.ai` → `kilo.ai` | `.kilocode/rules/` retained for backward compatibility; `.kilo/rules/` is current. Only the former is detected. |
| OpenHands | `docs.all-hands.dev` → `docs.openhands.dev` | `.openhands/microagents/` supported; `.agents/skills/` is preferred for new work. |
| Roo Code | `docs.roocode.com` → GitHub Pages | — |

A rebrand is **not** a reason to rename the product tag. The tag names the
convention's origin, and repositories still contain the old files.

## Known limitation: unanchored path matching

`path_contains` is a plain substring test, so a directory whose name *ends* with a
fragment matches it: `notes.claude/config.json` tags as Claude. Every fragment
begins with a dot, so ordinary paths cannot trip this, and it is consistent with
how `METADATA_RULES` has always matched `.github`. Accepted deliberately; noted
here so it is not rediscovered as a bug.

## Re-verifying

`AI_RULES` encodes 20 vendors' conventions, which change without notice. Two of the
four rejections above were candidates that had already gone stale when proposed.

To re-verify: work down *Sources by product*, confirm each indicator still appears
in current documentation, and check the *rejected list* in case a rejection has
become valid. Record the outcome by updating this document's **Rules verified**
date.

The governing rule, from `CLAUDE.md`: **a missing rule is better than a wrong one.**
A wrong rule mislabels a repository, and the label flows downstream into kospex
where someone will act on it. Drop what cannot be confirmed.

## Inventory

60 rules across 20 products. Generated from `AI_RULES`; regenerate rather than
hand-edit.

### Agents

| Match | Indicator | Kind |
|---|---|---|
| filename | `.aiignore` | `ignore` |
| filename | `agents.md` | `instructions` |

### Aider

| Match | Indicator | Kind |
|---|---|---|
| filename | `.aider.chat.history.md` | `history` |
| filename | `.aider.conf.yml` | `config` |
| filename | `.aider.input.history` | `history` |
| filename | `.aiderignore` | `ignore` |

### Amazon Q

| Match | Indicator | Kind |
|---|---|---|
| path | `.amazonq/` | `config` |
| path | `.amazonq/rules/` | `rules` |

### Augment

| Match | Indicator | Kind |
|---|---|---|
| filename | `.augment-guidelines` | `instructions` |
| path | `.augment/` | `config` |
| path | `.augment/rules/` | `rules` |

### Claude

| Match | Indicator | Kind |
|---|---|---|
| filename | `claude.local.md` | `instructions` |
| filename | `claude.md` | `instructions` |
| filename | `claude_desktop_config.json` | `config` |
| path | `.claude/` | `config` |
| path | `.claude/agents/` | `agent` |
| path | `.claude/commands/` | `command` |
| path | `.claude/hooks/` | `hook` |
| path | `.claude/plugins/` | `plugin` |
| path | `.claude/skills/` | `skill` |

### Cline

| Match | Indicator | Kind |
|---|---|---|
| path | `.clinerules/` | `rules` |

### Codex

| Match | Indicator | Kind |
|---|---|---|
| path | `.codex/` | `config` |

### Continue

| Match | Indicator | Kind |
|---|---|---|
| filename | `.continuerc.json` | `config` |
| path | `.continue/` | `config` |

### Copilot

| Match | Indicator | Kind |
|---|---|---|
| filename | `copilot-instructions.md` | `instructions` |
| path | `.github/chatmodes/` | `chatmode` |
| path | `.github/instructions/` | `instructions` |
| path | `.github/prompts/` | `prompt` |
| suffix | `.chatmode.md` | `chatmode` |
| suffix | `.instructions.md` | `instructions` |
| suffix | `.prompt.md` | `prompt` |

### Cursor

| Match | Indicator | Kind |
|---|---|---|
| filename | `.cursorignore` | `ignore` |
| filename | `.cursorindexingignore` | `ignore` |
| filename | `.cursorrules` | `rules` |
| path | `.cursor/` | `config` |
| path | `.cursor/rules/` | `rules` |
| suffix | `.mdc` | `rules` |

### Gemini

| Match | Indicator | Kind |
|---|---|---|
| filename | `.aiexclude` | `ignore` |
| filename | `.geminiignore` | `ignore` |
| filename | `gemini.md` | `instructions` |
| path | `.gemini/` | `config` |

### Goose

| Match | Indicator | Kind |
|---|---|---|
| filename | `.goosehints` | `instructions` |

### Junie

| Match | Indicator | Kind |
|---|---|---|
| path | `.junie/` | `config` |

### Kilo Code

| Match | Indicator | Kind |
|---|---|---|
| path | `.kilocode/` | `config` |
| path | `.kilocode/rules/` | `rules` |

### llms.txt

| Match | Indicator | Kind |
|---|---|---|
| filename | `llms-full.txt` | `docs` |
| filename | `llms.txt` | `docs` |

### MCP

| Match | Indicator | Kind |
|---|---|---|
| filename | `.mcp.json` | `config` |
| path | `.vscode/mcp.json` | `config` |

### OpenHands

| Match | Indicator | Kind |
|---|---|---|
| path | `.openhands/` | `config` |
| path | `.openhands/microagents/` | `skill` |

### Roo Code

| Match | Indicator | Kind |
|---|---|---|
| filename | `.roorules` | `rules` |
| path | `.roo/` | `config` |
| path | `.roo/rules/` | `rules` |

### Trae

| Match | Indicator | Kind |
|---|---|---|
| path | `.trae/` | `config` |
| path | `.trae/rules/` | `rules` |

### Windsurf

| Match | Indicator | Kind |
|---|---|---|
| filename | `.codeiumignore` | `ignore` |
| filename | `.windsurfrules` | `rules` |
| path | `.windsurf/` | `config` |
| path | `.windsurf/rules/` | `rules` |

