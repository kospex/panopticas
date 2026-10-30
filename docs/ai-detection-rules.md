---
layout: default
title: AI Detection Rules
description: Every AI coding agent artifact panopticas detects, the source confirming each convention, and the candidates that were investigated and rejected.
---

# AI Coding Agent Detection — Rules Reference

**Rules verified:** 2026-08-01 (panopticas 0.0.17). Unchanged since — 0.0.18 and
0.0.19 added no AI rules, and the inventory below matches `AI_RULES` as shipped in
0.0.19. Rules added on 2026-10-30 were each verified against the vendor's docs
that day: Warp; `.agents/skills/` and `.openhands/skills/`; Copilot's custom
agents, skills, hooks, settings and setup steps; the Codex, Cursor and Gemini
skill directories; and Factory and OpenCode. Rules that existed before were not
re-checked then.
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

> For the *principles* governing additions, see
> [`CLAUDE.md`](https://github.com/kospex/panopticas/blob/main/CLAUDE.md) →
> *AI Agent Detection*. For the original design rationale, see
> [`changes/design/specs/2026-07-31-ai-agent-detection-design.md`](https://github.com/kospex/panopticas/blob/main/changes/design/specs/2026-07-31-ai-agent-detection-design.md)
> — but note its proposed rule table predates verification and contains entries
> that were subsequently rejected. **This document supersedes that table.**

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
| `.copilot/skills/` | Copilot project skills directory (Warp scans it) | **User-level, not a repository artifact.** GitHub lists `~/.copilot/skills` as personal skills; repository skills are `.github/skills`, `.claude/skills` or `.agents/skills`, and those are detected. Another tool reading a directory is not the vendor documenting it. | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills |

`tests/test_ai_detection.py` contains negative tests asserting these return `None`,
so re-adding one fails the suite rather than shipping silently.

### The user-level trap

Three of the five rejections share a cause worth naming. A path like
`~/.config/<tool>/` or `~/.<tool>/` is **not** a repository artifact — panopticas
scans repositories, so such a rule would essentially never fire, and if it did the
match would mean something different from what the tag claims.

Several *detected* products have a user-level twin (`~/.junie/AGENTS.md`,
`~/.augment/rules/`, `~/.codeium/.codeiumignore`, `~/.config/goose/.goosehints`,
`~/.warp/workflows/`, `~/.warp/skills/`, `~/.agents/skills/`, `~/.copilot/`, `~/.factory/`).
Those rules are sound because the repository-level form is **separately and
explicitly documented**. Check for that before adding.

## Sources by product

Every rule was checked against the product's own current documentation before being
added. Weak evidence — a blog post, a third-party listicle — was treated as a lead
to confirm elsewhere, never as confirmation.

| Product | Source |
|---|---|
| Agents (`.agents/skills/`) | https://learn.chatgpt.com/docs/build-skills (Codex), https://docs.openhands.dev/usage/prompting/microagents-overview, https://docs.warp.dev/agents/capabilities/skills/. Format: https://agentskills.io/specification.md, which names no discovery path itself |
| Aider | https://aider.chat/docs/config/aider_conf.html |
| Amazon Q | https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/context-project-rules.html |
| Augment | https://docs.augmentcode.com/setup-augment/guidelines |
| Cline | https://docs.cline.bot/customization/cline-rules |
| Codex (`.codex/skills/`) | https://github.com/openai/codex/pull/10317 (legacy, still loaded: `codex-rs/ext/skills/src/host_roots.rs`) |
| Continue | https://docs.continue.dev/customize/deep-dives/rules |
| Copilot (agents, skills, hooks, settings, setup steps) | https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli, https://code.visualstudio.com/docs/copilot/customization/custom-chat-modes, https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills, https://docs.github.com/en/copilot/reference/hooks-reference, https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/customize-the-agent-environment |
| Cursor (`.cursor/skills/`) | https://cursor.com/docs/skills |
| Factory | https://docs.factory.com/cli/configuration/skills |
| Gemini | https://github.com/google-gemini/gemini-cli — `docs/gemini-ignore.md`; skills: https://geminicli.com/docs/cli/creating-skills/ |
| Goose | https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/ |
| Junie | https://junie.jetbrains.com/docs/guidelines-and-memory.html |
| Kilo Code | https://github.com/Kilo-Org/kilocode — `custom-rules.md` |
| OpenCode | https://opencode.ai/docs/skills, https://opencode.ai/docs/config/ |
| OpenHands | https://docs.openhands.dev/usage/prompting/microagents-overview |
| Roo Code | https://roocodeinc.github.io/Roo-Code/features/custom-instructions |
| Trae | https://docs.trae.cn/ide/rules |
| Warp | https://docs.warp.dev/agent-platform/capabilities/rules/ (`WARP.md`), https://docs.warp.dev/terminal/entry/yaml-workflows/ (`.warp/workflows/`), https://docs.warp.dev/agents/capabilities/skills/ (`.warp/skills/`) |
| Windsurf | https://docs.devin.ai/desktop/cascade/memories |

Claude, Cursor, Codex and the vendor-neutral pseudo-products were treated
as well-established and not individually cited. Copilot's original instructions,
prompt and chat mode rules were too; its later conventions are cited above.

### Vendors that have moved or rebranded

Documentation hosts change more often than file conventions do. Confirmed during
the 0.0.17 verification pass:

| Product | Docs moved | Note |
|---|---|---|
| Windsurf | `docs.windsurf.com` → `docs.devin.ai` | Cognition/Devin. `.windsurfrules` is described as legacy but still read; `.devin/rules/` is preferred. Brand name kept as `Windsurf` — the filenames belong to that era. |
| Kilo Code | `kilocode.ai` → `kilo.ai` | `.kilocode/rules/` retained for backward compatibility; `.kilo/rules/` is current. Only the former is detected. |
| OpenHands | `docs.all-hands.dev` → `docs.openhands.dev` | `.openhands/microagents/` and `.openhands/skills/` are legacy but supported; `.agents/skills/` is preferred and takes precedence. All three are detected. |
| Roo Code | `docs.roocode.com` → GitHub Pages | — |
| Codex | `developers.openai.com/codex/skills` → `learn.chatgpt.com/docs/build-skills` | Redirect seen 2026-10-30. The current page lists only `.agents/skills` for repositories; `.codex/skills/` is legacy but still loaded. |
| Factory | `docs.factory.ai` → `docs.factory.com` | Redirect seen 2026-10-30. |

A rebrand is **not** a reason to rename the product tag. The tag names the
convention's origin, and repositories still contain the old files.

## Known limitation: unanchored path matching

`path_contains` is a plain substring test, so a directory whose name *ends* with a
fragment matches it: `notes.claude/config.json` tags as Claude. Every fragment
begins with a dot, so ordinary paths cannot trip this, and it is consistent with
how `METADATA_RULES` has always matched `.github`. Accepted deliberately; noted
here so it is not rediscovered as a bug.

## Re-verifying

`AI_RULES` encodes 23 vendors' conventions, which change without notice. Two of the
five rejections above were candidates that had already gone stale when proposed.

To re-verify: work down *Sources by product*, confirm each indicator still appears
in current documentation, and check the *rejected list* in case a rejection has
become valid. Record the outcome by updating this document's **Rules verified**
date.

The governing rule, from `CLAUDE.md`: **a missing rule is better than a wrong one.**
A wrong rule mislabels a repository, and the label flows downstream into kospex
where someone will act on it. Drop what cannot be confirmed.

## Inventory

79 rules across 23 products. Generated from `AI_RULES`; regenerate rather than
hand-edit.

### Agents

| Match | Indicator | Kind |
|---|---|---|
| filename | `.aiignore` | `ignore` |
| filename | `agents.md` | `instructions` |
| path | `.agents/skills/` | `skill` |

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
| path | `.codex/skills/` | `skill` |

### Continue

| Match | Indicator | Kind |
|---|---|---|
| filename | `.continuerc.json` | `config` |
| path | `.continue/` | `config` |

### Copilot

| Match | Indicator | Kind |
|---|---|---|
| filename | `copilot-instructions.md` | `instructions` |
| filename | `copilot-setup-steps.yml` | `config` |
| path | `.github/agents/` | `agent` |
| path | `.github/chatmodes/` | `chatmode` |
| path | `.github/copilot/` | `config` |
| path | `.github/hooks/` | `hook` |
| path | `.github/instructions/` | `instructions` |
| path | `.github/prompts/` | `prompt` |
| path | `.github/skills/` | `skill` |
| suffix | `.agent.md` | `agent` |
| suffix | `.chatmode.md` | `chatmode` |
| suffix | `.instructions.md` | `instructions` |
| suffix | `.prompt.md` | `prompt` |

Chat modes were renamed to custom agents. VS Code: "Custom agents were
previously known as custom chat modes". Both are detected, because older
repositories still hold `.github/chatmodes/` and `*.chatmode.md`.

### Cursor

| Match | Indicator | Kind |
|---|---|---|
| filename | `.cursorignore` | `ignore` |
| filename | `.cursorindexingignore` | `ignore` |
| filename | `.cursorrules` | `rules` |
| path | `.cursor/` | `config` |
| path | `.cursor/rules/` | `rules` |
| path | `.cursor/skills/` | `skill` |
| suffix | `.mdc` | `rules` |

### Factory

| Match | Indicator | Kind |
|---|---|---|
| path | `.factory/` | `config` |
| path | `.factory/skills/` | `skill` |

### Gemini

| Match | Indicator | Kind |
|---|---|---|
| filename | `.aiexclude` | `ignore` |
| filename | `.geminiignore` | `ignore` |
| filename | `gemini.md` | `instructions` |
| path | `.gemini/` | `config` |
| path | `.gemini/skills/` | `skill` |

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
| path | `.openhands/skills/` | `skill` |

### OpenCode

| Match | Indicator | Kind |
|---|---|---|
| path | `.opencode/` | `config` |
| path | `.opencode/skills/` | `skill` |

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

### Warp

| Match | Indicator | Kind |
|---|---|---|
| filename | `warp.md` | `instructions` |
| path | `.warp/` | `config` |
| path | `.warp/skills/` | `skill` |
| path | `.warp/workflows/` | `command` |

### Windsurf

| Match | Indicator | Kind |
|---|---|---|
| filename | `.codeiumignore` | `ignore` |
| filename | `.windsurfrules` | `rules` |
| path | `.windsurf/` | `config` |
| path | `.windsurf/rules/` | `rules` |

