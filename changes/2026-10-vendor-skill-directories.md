# Vendor Skill Directories

Closes [#64](https://github.com/kospex/panopticas/issues/64).

**Status:** implemented. Verified on 2026-10-30. Each directory was checked
against its own vendor's docs, and for Codex against the source.

## Summary

[Warp's Skills page](https://docs.warp.dev/agents/capabilities/skills/)
(updated 2026-10-26) lists ten project skill directories it scans:

> `.agents/skills/` (recommended), `.warp/skills/`, `.claude/skills/`,
> `.codex/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.copilot/skills/`,
> `.factory/skills/`, `.github/skills/`, `.opencode/skills/`

Warp reading a directory is not evidence that the vendor documents it, so
each was checked separately.

| Directory | Before | After | Outcome |
|---|---|---|---|
| `.claude/skills/` | `(Claude, skill)` | unchanged | 0.0.17 |
| `.warp/skills/` | — | `(Warp, skill)` | #33 |
| `.agents/skills/` | — | `(Agents, skill)` | #62 |
| `.github/skills/` | — | `(Copilot, skill)` | #65, moved out of this issue |
| `.codex/skills/` | `(Codex, config)` | `(Codex, skill)` | **Added**, as legacy |
| `.cursor/skills/` | `(Cursor, config)` | `(Cursor, skill)` | **Added** |
| `.gemini/skills/` | `(Gemini, config)` | `(Gemini, skill)` | **Added** |
| `.factory/skills/` | — | `(Factory, skill)` | **Added**, new product |
| `.opencode/skills/` | — | `(OpenCode, skill)` | **Added**, new product |
| `.copilot/skills/` | — | — | **Rejected**: user-level only |

## Codex: `.codex/skills/` (legacy, still loaded)

Codex's [current skills page](https://learn.chatgpt.com/docs/build-skills)
(`developers.openai.com/codex/skills` now redirects there) lists only
`.agents/skills` for repositories. The upstream PR that added it,
[openai/codex#10317](https://github.com/openai/codex/pull/10317), merged on
2026-02-01:

> Loading from `.codex/skills/` will remain but will be deprecated soon. The
> change only applies to the REPO scope.

The source confirms that current Codex still loads it.
`codex-rs/ext/skills/src/host_roots.rs`, last changed 2026-10-27 at
`28cade4`, adds `config_folder.join("skills")` as `SkillScope::Repo` for the
project config layer, which is `<repo>/.codex/`. The user-scope equivalent,
`$CODEX_HOME/skills`, is commented "Deprecated user skills location … kept
for backward compatibility".

So `.codex/skills/` is a real repository convention from before February
2026, and is still read. Old repositories will hold it, so it is detected as
`skill`, as `.openhands/skills/` was.

[Cursor's docs](https://cursor.com/docs/skills) corroborate it: "For
compatibility, Cursor also loads skills from Claude and Codex directories:
`.claude/skills/`, `.codex/skills/`…".

## Cursor: `.cursor/skills/`

[cursor.com/docs/skills](https://cursor.com/docs/skills) lists `.agents/skills/`
and `.cursor/skills/` as project-level, and `~/.agents/skills/` and
`~/.cursor/skills/` as user-level.

## Gemini: `.gemini/skills/`

[Gemini CLI, Creating Agent Skills](https://geminicli.com/docs/cli/creating-skills/)
says workspace skills live in "`.gemini/skills/` or the `.agents/skills/`
alias", and user skills in "`~/.gemini/skills/` or the `~/.agents/skills/`
alias". Workspace skills take the highest precedence.

## Factory: `.factory/skills/` and `.factory/` (new product)

[Factory skills](https://docs.factory.com/cli/configuration/skills)
(`docs.factory.ai` now redirects to `docs.factory.com`):

- Project: `<repo>/.factory/skills/<skill-name>/SKILL.md`
- Folder-specific: `<repo>/<project-area>/.factory/skills/<skill-name>/SKILL.md`
- Personal: `~/.factory/skills/<skill-name>/SKILL.md`
- `<project>/.factory/settings.json` holds project-level `disabledSkills`

`.factory/` is documented as a repository directory beyond skills (it holds
`settings.json`), so it gets a `config` fallback like other products. Factory
also reads `.agent/skills/` (singular) for compatibility. That is not added:
no other vendor documents it, and it is not the vendor-neutral `.agents/`.

The product tag is `Factory`, the brand. Droid is its agent, as Claude Code
is Anthropic's.

## OpenCode: `.opencode/skills/` and `.opencode/` (new product)

[OpenCode skills](https://opencode.ai/docs/skills) lists `.opencode/skills/<name>/SKILL.md`,
`.claude/skills/<name>/SKILL.md` and `.agents/skills/<name>/SKILL.md` for
projects. The global equivalent is `~/.config/opencode/skills/`, which is
outside `.opencode/`.

[OpenCode config](https://opencode.ai/docs/config/) documents `.opencode/` as
a project directory with `plugins/`, `agents/`, `commands/`, `modes/`,
`skills/`, `tools/` and `themes/` subdirectories, so it gets a `config`
fallback. Subdirectories use plural names, and "singular names such as
`agent/` are still supported for backwards compatibility".

## Copilot: `.copilot/skills/` (rejected)

GitHub's [Create skills](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills)
page lists `~/.copilot/skills` as personal skills, and `.github/skills`,
`.claude/skills` or `.agents/skills` as repository skills. A repository
`.copilot/` is not documented, so this is the user-level trap. It is added
to the rejected list in `docs/ai-detection-rules.md`, with a negative test
and a fixture that must stay untagged.

## Not added (follow-ups)

| Candidate | Why not, for now |
|---|---|
| `.opencode/agents/`, `.opencode/commands/` (`agent`, `command`) | Documented, but outside this issue's scope. They are tagged `(OpenCode, config)` by the fallback for now. |
| `opencode.json` at the project root | Documented project config. It is an exact-filename rule, outside this issue's scope. |
| `.agent/skills/` (singular) | Factory compatibility only. |
| `.android-studio/skills/` | Android Studio's Gemini agent. The [page](https://developer.android.com/studio/gemini/skills) lists `.agents/skills` or `.android-studio/skills` at the project root or home directory. It would be a new product; not in Warp's list, so outside this issue. Android Studio's legacy `.skills` and `agent/skills` (no dot) are too generic to match. |

## Effect on kospex

There are two new tags, `Factory` and `OpenCode` (132 tags in total), and
both are in `tests/data/tag_snapshot.txt`. Nothing is retired. Files under
`.codex/skills/`, `.cursor/skills/` and `.gemini/skills/` change from
`config` to `skill` on re-sync. A kospex query for `config` stops matching
them, and one for `skill` starts to.

## Docs and tests

- `tests/test_ai_detection.py`, `TestVendorSkillDirectories`: each skill
  directory, a Factory subproject path, the new `config` fallbacks, existing
  Codex and Cursor `config` unchanged, and `.copilot/skills/` not detected.
  Eight tests failed before the rules were added; the three guards passed.
- Fixtures: `src/tests/.{codex,cursor,gemini,factory,opencode,copilot}/skills/review/SKILL.md`
  and `src/tests/.factory/settings.json`.
- `docs/ai-detection-rules.md`: inventory, sources (re-sorted), the
  rejected list (now five), the user-level twins, moved docs (Codex,
  Factory), and counts (79 rules, 23 products).
- `CLAUDE.md`: rejected count, four → five.
- `docs/cli.md`, `docs/api.md`: 130 → 132 tags.
- `CHANGELOG.md` under `## [Unreleased]`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://docs.warp.dev/agents/capabilities/skills/> | The list of ten directories | 2026-10-30 (page updated 2026-10-26) |
| <https://learn.chatgpt.com/docs/build-skills> | Current Codex skill locations; no `.codex/skills` | 2026-10-30 |
| <https://github.com/openai/codex/pull/10317> | `.codex/skills/` remains, to be deprecated | 2026-10-30 |
| <https://github.com/openai/codex/blob/main/codex-rs/ext/skills/src/host_roots.rs> | `.codex/skills` still loaded as repository scope (at `28cade4`, 2026-10-27) | 2026-10-30 |
| <https://cursor.com/docs/skills> | `.cursor/skills/`; Cursor also loads `.codex/skills/` | 2026-10-30 |
| <https://geminicli.com/docs/cli/creating-skills/> | `.gemini/skills/` and the `.agents/skills/` alias | 2026-10-30 |
| <https://docs.factory.com/cli/configuration/skills> | `.factory/skills/`, subproject form, `.factory/settings.json`, `.agent/skills/` | 2026-10-30 |
| <https://opencode.ai/docs/skills> | `.opencode/skills/` and compatibility paths | 2026-10-30 |
| <https://opencode.ai/docs/config/> | `.opencode/` subdirectories, `opencode.json` | 2026-10-30 |
| <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills> | `.copilot/skills` is personal only | 2026-10-30 |
| <https://developer.android.com/studio/gemini/skills> | `.android-studio/skills`; legacy `.skills` and `agent/skills` | 2026-10-30 |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://forge.lthn.ai/core/core-agent-ide/src/commit/0a32acaa2deb8883e9dcbfb80e84957837d39b74/docs/skills.md> | A Codex fork mirroring PR #10317's deprecation note | Confirmed upstream, in the PR itself |
| <https://github.com/openai/codex/discussions/9682> | A maintainer: "you need to place your skills in a `.codex` path for Codex to see them" (before #10317) | Consistent: `.codex/skills/` was the original location |
| <https://smithery.ai/skills/justinlevinedotme/opencode-skills> | Third-party listing: OpenCode project skills at `.opencode/skill/<name>/SKILL.md` (singular) | Contradicted by [opencode.ai/docs/skills](https://opencode.ai/docs/skills), which uses `skills`. OpenCode's config docs say singular subdirectory names are "still supported for backwards compatibility", so this may describe an older form. Kept in case OpenCode's docs change. |
| <https://docs.rs/crate/agentlink-domain/latest/source/providers/codex.toml> | Third-party: Codex walks `.agents/skills/` in addition to `.codex/skills/` | Confirmed by the Codex source |
