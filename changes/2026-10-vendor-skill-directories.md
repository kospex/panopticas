# Vendor Skill Directories

For [#64](https://github.com/kospex/panopticas/issues/64).

**Status:** researched in part, not implemented. This note gathers the
evidence found so far, so that the next pass starts from it rather than
from the issue body.

## Summary

[Warp's Skills page](https://docs.warp.dev/agents/capabilities/skills/)
(updated 2026-10-26) lists ten project skill directories it scans:

> `.agents/skills/` (recommended), `.warp/skills/`, `.claude/skills/`,
> `.codex/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.copilot/skills/`,
> `.factory/skills/`, `.github/skills/`, `.opencode/skills/`

Warp reading a directory is not evidence that the vendor documents it. Each
one has to be confirmed against its own vendor's current docs.

## Already handled

| Directory | Rule | Where |
|---|---|---|
| `.claude/skills/` | `(Claude, skill)` | 0.0.17 |
| `.warp/skills/` | `(Warp, skill)` | [#33](https://github.com/kospex/panopticas/issues/33), `changes/2026-10-warp-ai-detection.md` |
| `.agents/skills/` | `(Agents, skill)` | [#62](https://github.com/kospex/panopticas/issues/62), `changes/2026-10-agents-skills-detection.md` |
| `.github/skills/` | `(Copilot, skill)` | [#65](https://github.com/kospex/panopticas/issues/65), `changes/2026-10-copilot-agents-and-hooks.md`. Moved out of this issue. |

## Remaining candidates

Current behaviour, checked 2026-10-30:

    .codex/skills/a/SKILL.md      (Codex, config)
    .cursor/skills/a/SKILL.md     (Cursor, config)
    .gemini/skills/a/SKILL.md     (Gemini, config)
    .copilot/skills/a/SKILL.md    not detected
    .factory/skills/a/SKILL.md    not detected
    .opencode/skills/a/SKILL.md   not detected

| Directory | Product | Evidence so far |
|---|---|---|
| `.codex/skills/` | Codex | **Doubtful.** Codex's [current skills page](https://learn.chatgpt.com/docs/build-skills) (`developers.openai.com/codex/skills` redirects there) lists only `.agents/skills` for repositories, plus `$HOME/.agents/skills`, `/etc/codex/skills` and bundled skills. It does not mention `.codex/skills`. A downstream mirror of Codex PR #10317 ([forge.lthn.ai](https://forge.lthn.ai/core/core-agent-ide/src/commit/0a32acaa2deb8883e9dcbfb80e84957837d39b74/docs/skills.md)) says the PR added `.agents/skills/` and that `.codex/skills/` loading "will remain but will be deprecated soon", for the repository scope only. That is a mirror, not upstream, so check the upstream PR and [discussion #9682](https://github.com/openai/codex/discussions/9682). If it is a legacy path, add it as legacy, as `.openhands/skills/` was. |
| `.copilot/skills/` | Copilot | **Probably reject.** GitHub's [Create skills](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills) page lists `~/.copilot/skills` as personal, with no repository form; repository skills are `.github/skills`, `.claude/skills` or `.agents/skills`. A user-level-only path goes on the rejected list. |
| `.cursor/skills/` | Cursor | Not yet checked against Cursor's docs. |
| `.gemini/skills/` | Gemini | Not yet checked against the Gemini CLI docs. The [Android Studio Gemini page](https://developer.android.com/studio/gemini/skills) points to `.skills/` or `.agent/skills/` (singular) instead, according to a search summary; read the page itself. Android Studio's Gemini is a different surface from Gemini CLI. |
| `.factory/skills/` | Factory | Not yet checked. A new product means a new tag and a snapshot line. |
| `.opencode/skills/` | OpenCode | Not yet checked. A new product means a new tag and a snapshot line. |

## Rule shape

Where confirmed: `".<tool>/skills/": ("<Product>", "skill")`, layered over
any existing `".<tool>/": (..., "config")`, as `.claude/skills/` is over
`.claude/`. Files moving from `config` to `skill` change their stored tags in
kospex on re-sync; note that in the CHANGELOG.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://docs.warp.dev/agents/capabilities/skills/> | The list of ten directories | 2026-10-30 (page updated 2026-10-26) |
| <https://learn.chatgpt.com/docs/build-skills> | Codex skill locations; no `.codex/skills` | 2026-10-30 |
| <https://forge.lthn.ai/core/core-agent-ide/src/commit/0a32acaa2deb8883e9dcbfb80e84957837d39b74/docs/skills.md> | Lead: `.codex/skills/` to be deprecated (a mirror, unconfirmed) | 2026-10-30, via search summary |
| <https://github.com/openai/codex/discussions/9682> | Lead: configuring the skill folder | Not yet read |
| <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills> | `.copilot/skills` is personal only | 2026-10-30 |
| <https://developer.android.com/studio/gemini/skills> | Lead: Android Studio Gemini skill directories | Not yet read; search summary only |
