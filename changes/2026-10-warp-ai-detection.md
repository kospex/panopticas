# Warp AI Agent Detection

Closes [#33](https://github.com/kospex/panopticas/issues/33).

**Status:** implemented as proposed below. The research is kept as the
evidence base for each rule. The issue was researched on
2026-08-17 and re-verified on 2026-10-30, against Warp docs pages that say
"Last updated Oct 26, 2026". The re-check found one repository convention the
issue does not cover, `.warp/skills/`, so four rules were added where the
issue proposed three.

## Summary

Before this change, Warp (the terminal and agent platform at warp.dev) was
not detected. It was neither in `AI_RULES` nor on the rejected list in `docs/ai-detection-rules.md`,
so it had never been assessed:

    path                          get_ai_metadata()
    WARP.md                       None
    .warp/workflows/deploy.yaml   None
    .warp/skills/x/SKILL.md       None
    .warp/.mcp.json               {'product': 'MCP', 'kind': 'config'}

`.warp/.mcp.json` already got a tag through the existing `.mcp.json`
exact-filename rule (see below).

## Verified conventions

### 1. `WARP.md`: project rules file, at the repository root or in any subdirectory

Warp now treats `AGENTS.md` as its default rules file and keeps `WARP.md` for
backwards compatibility. `WARP.md` takes priority when both are present:

> They're stored in an AGENTS.md file (or WARP.md for backwards compatibility)

> Existing WARP.md files are still fully supported

> If both WARP.md and AGENTS.md exist in the same directory, WARP.md takes priority.

> The filename must be in all caps for Warp to recognize it (e.g., AGENTS.md, not agents.md or Agents.md).

The file can be at the root or "Added in subdirectories for more targeted
guidance". Global rules live in Warp Drive, not in a file, so `WARP.md` has
no user-level twin.

Between August and October the docs changed from "the default is now
`AGENTS.md`" to calling `WARP.md` "for backwards compatibility". It is still
fully supported, though, and repositories that already have one keep it, so
it is still worth detecting. `AGENTS.md` stays with the vendor-neutral
`Agents` pseudo-product.

Source: <https://docs.warp.dev/agent-platform/capabilities/rules/>

### 2. `.warp/workflows/`: YAML workflows scoped to a repository

> {{path_to_git_repo}}/.warp/workflows

Workflow files "must have either a `.yml` or `.yaml` extension". The page
carries a caution, not a deprecation:

> You can continue to use YAML-based workflows … we recommend using new
> workflows in Warp Drive instead for a better editing experience.

This puts it in the same position as `.kilocode/` and `.windsurfrules`, which
are already in the table.

The local, user-level paths are:

| OS | Local path |
|---|---|
| macOS | `$HOME/.warp/workflows/` |
| Linux | `${XDG_DATA_HOME:-$HOME/.local/share}/warp-terminal/workflows/` |
| Windows | `$env:APPDATA\warp\Warp\data\workflows\` |

Only the macOS path looks like the repository form.

Source: <https://docs.warp.dev/terminal/entry/yaml-workflows/>

### 3. `.warp/skills/`: project skills (new since #33 was written)

Warp's Skills page lists the project directories it scans. Each skill is a
subdirectory containing a `SKILL.md`:

> `.agents/skills/` (recommended), `.warp/skills/`, `.claude/skills/`,
> `.codex/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.copilot/skills/`,
> `.factory/skills/`, `.github/skills/`, `.opencode/skills/`

The global form, `~/.warp/skills/`, has the same user-level-twin shape as
workflows. The AI-objects page agrees: "Project Skills - Live in
`.agents/skills/`, `.warp/skills/`, or similar directories in your
repository."

Sources: <https://docs.warp.dev/agents/capabilities/skills/>,
<https://docs.warp.dev/knowledge-and-collaboration/warp-drive/ai-objects>

### 4. `.warp/.mcp.json`: project MCP config (no change needed)

The MCP page names `{repo_root}/.warp/.mcp.json` as the project-level file
and `~/.warp/.mcp.json` as the global one. Exact-filename rules take
precedence, so the existing `".mcp.json": ("MCP", "config")` rule already
claims it. That matches `.vscode/mcp.json` → `(MCP, config)`, where an MCP
file is labelled as MCP whichever product's directory it sits in.

The same page says Warp also reads other agents' project MCP files: `.mcp.json`
at the root, `.codex/config.toml` and `.agents/.mcp.json`. None of those
needs a Warp rule.

Source: <https://docs.warp.dev/agents/capabilities/mcp.md>

## Proposed rules

```python
# exact_filename
"warp.md": ("Warp", "instructions"),

# path_contains
".warp/workflows/": ("Warp", "command"),
".warp/skills/":    ("Warp", "skill"),
".warp/":           ("Warp", "config"),
```

The longest path fragment wins, so `.warp/skills/` and `.warp/workflows/`
take precedence over `.warp/`. This is the same layering as `.claude/skills/`
over `.claude/`.

The only new tag is `Warp`. `instructions`, `command`, `skill` and `config`
are already in `AI_ARTIFACT_KINDS`.

## Decisions

**Kind for workflows: `command`.** `AI_ARTIFACT_KINDS` has no `workflow`
kind. A Warp workflow is a named, parameterised command, so `command` fits
without growing the vocabulary. A new kind would show up downstream, in
`panopticas tags` and in kospex's `tech_type`, so it should not be added
casually.

**User-level twins are accepted.** `~/.warp/` holds Warp's personal files:
themes, tab configs, workflows, launch configurations, `settings.toml`,
`keybindings.yaml`, `.mcp.json`, skills and `tui/`. The file-locations page
lists all of them as home-directory paths, and none as repository paths.
`.warp/` therefore has a user-level twin, the same shape as `~/.junie/` and
`~/.augment/rules/`, which are detected on the strength of their
repository-local form. It is not the `.goose/` or `.qodo/` failure mode, where
no repository-local form exists at all. Add a comment in `constants.py`
beside the rule.

The consequence: a repository that commits stray `~/.warp/` content, such as
a theme, gets `(Warp, config)`. That is a correct product label, if a vague
kind.

**Case.** Warp reads only an all-caps `WARP.md`, but panopticas matches the
lowercased basename, so a lowercase `warp.md` is tagged too. `claude.md` and
`gemini.md` already behave this way, and it is a known and accepted
imprecision.

## Considered and not proposed

| Candidate | Why not |
|---|---|
| `~/.warp/settings.toml`, `themes/`, `keybindings.yaml`, `launch_configurations/`, `tab_configs/`, `tui/` | User-level only, per the file-locations page. They are covered as `(Warp, config)` by the `.warp/` fallback if one is ever committed, with no dedicated rule. |
| Linux and Windows local workflow paths | User-level, and outside `.warp/`. |
| A dedicated `.warp/.mcp.json` rule | Already `(MCP, config)` through the exact-filename rule, which is consistent with `.vscode/mcp.json`. |
| `.agents/skills/` | Warp's recommended skills directory, but a vendor-neutral convention that OpenHands also prefers. It belongs to the `Agents` pseudo-product, not Warp. Out of scope here; raise separately. |

## Effect on kospex

The change only adds rules. `Warp` is a new tag, and no existing tag changes,
so `DEPRECATED_TAGS` needs no entry. The version bump is what makes kospex
re-tag repositories it has already synced.

## Docs and tests

- `tests/test_ai_detection.py`, `TestWarp`: `WARP.md`, `services/api/WARP.md`,
  `.warp/workflows/` (`.yaml` and `.yml`), `.warp/skills/release/SKILL.md` and
  a bare `.warp/` file. Guards check that `.warp/.mcp.json` stays
  `(MCP, config)` and `AGENTS.md` stays `Agents`.
- `src/tests/` fixtures: `WARP.md`, `services/api/WARP.md`,
  `.warp/workflows/deploy.yaml`, `.warp/skills/release/SKILL.md` and
  `.warp/.mcp.json`. The repository `.gitignore` ignores `.warp/` because a
  developer's own Warp directory can sit in the checkout, so
  `!src/tests/.warp/` re-includes the fixtures.
- `tests/data/tag_snapshot.txt`: `Warp` added. The snapshot test failed
  until it was.
- `docs/ai-detection-rules.md`: Warp inventory and source rows, Warp's
  user-level twins in *The user-level trap*, counts (64 rules, 21 products),
  and a note on the verification date.
- `docs/cli.md`, `docs/api.md`: tag count 129 → 130.
- `CHANGELOG.md` under `## [Unreleased]`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://docs.warp.dev/agent-platform/capabilities/rules/> | `WARP.md`: backwards compatibility, priority, all caps, subdirectories | 2026-08-17, 2026-10-30 (page updated 2026-10-26) |
| <https://docs.warp.dev/terminal/entry/yaml-workflows/> | `.warp/workflows/`, local paths per OS, the Warp Drive caution, `.yml`/`.yaml` | 2026-08-17, 2026-10-30 (page updated 2026-10-26) |
| <https://docs.warp.dev/agents/capabilities/skills/> | `.warp/skills/` and the full list of project and global skill directories | 2026-10-30 (page updated 2026-10-26) |
| <https://docs.warp.dev/knowledge-and-collaboration/warp-drive/ai-objects> | Project and global skills, `SKILL.md` | 2026-10-30 (page updated 2026-10-26) |
| <https://docs.warp.dev/agents/capabilities/mcp.md> | `{repo_root}/.warp/.mcp.json`, other agents' MCP files that Warp reads | 2026-10-30 |
| <https://docs.warp.dev/terminal/settings/file-locations.md> | Every `~/.warp/` path is user-level | 2026-10-30 |
