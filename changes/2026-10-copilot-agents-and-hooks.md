# Copilot Custom Agents, Skills, Hooks, Settings and Setup Steps

Closes [#65](https://github.com/kospex/panopticas/issues/65).

**Status:** implemented. Verified on 2026-10-30.

## Summary

Copilot detection was written for 0.0.17 and covered instructions, prompt
files and chat modes. GitHub has since added repository conventions that
were not detected beyond the generic `.github/` tags:

    path                                         before                after
    .github/agents/reviewer.agent.md             GitHub, Git           + AI, Copilot, agent
    .github/skills/review/SKILL.md               GitHub, Git           + AI, Copilot, skill
    .github/hooks/policy.json                    GitHub, Git           + AI, Copilot, hook
    .github/copilot/settings.json                GitHub, Git           + AI, Copilot, config
    .github/workflows/copilot-setup-steps.yml    workflow tags         + AI, Copilot, config
    agents/reviewer.agent.md                     none                  AI, Copilot, agent

## Chat modes are kept

VS Code renamed chat modes to custom agents:

> Custom agents were previously known as custom chat modes.

> If you have existing `.chatmode.md` files, rename them to `.agent.md` and
> place them in one of the supported custom agent locations.

Repositories from before the rename still hold `.github/chatmodes/` and
`*.chatmode.md`, and panopticas is used to scan repositories from years ago.
The `chatmode` rules stay, and `agent` is added for current repositories.
Nothing is retired, so `DEPRECATED_TAGS` is unchanged. A repository that
followed the rename shows `agent` from then on, and its history shows
`chatmode`.

## Verified conventions

### Custom agents: `.github/agents/` and `*.agent.md`

> Repository: `.github/agents/`

> Each custom agent is defined by a Markdown file with an `.agent.md`
> extension.

The user-level location is `~/.copilot/agents/`. VS Code also accepts a plain
`.md` file in `.github/agents`, so the directory rule covers both. The
`.agent.md` suffix rule follows the existing `.chatmode.md`, `.prompt.md`
and `.instructions.md` suffix rules, which catch files kept in custom
locations, such as an organisation's `agents/` folder.

`.claude/agents/` also holds agent files, in Claude's format. A path rule
beats a suffix rule, so `.claude/agents/x.agent.md` stays `(Claude, agent)`.
A test pins this.

Sources: <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli>,
<https://code.visualstudio.com/docs/copilot/customization/custom-chat-modes>

### Skills: `.github/skills/`

> `.github/skills`, `.claude/skills`, or `.agents/skills` directory

These are the project locations. Personal skills are in `~/.copilot/skills`
or `~/.agents/skills`. Skills are supported by the cloud agent, code review,
the CLI, the Copilot app and VS Code agent mode. This was listed in
[#64](https://github.com/kospex/panopticas/issues/64) and moved here.
`.agents/skills/` is [#62](https://github.com/kospex/panopticas/issues/62).

Source: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills>

### Hooks: `.github/hooks/`

> Repository-level hook files — `.github/hooks/*.json` in the repository
> root.

In the cloud agent, `.github/hooks/*.json` is the only hook configuration
loaded by default. The user-level directory is `~/.copilot/hooks/`.

Source: <https://docs.github.com/en/copilot/reference/hooks-reference>

### Settings: `.github/copilot/`

The same reference lists two repository settings files that can carry
inline hooks:

> `.github/copilot/settings.json` (Git committed)

> `.github/copilot/settings.local.json` (typically gitignored and user specific)

The user-level file is `~/.copilot/settings.json`. Both repository files are
tagged `config`, not `hook`, because the settings file holds more than hooks.

Source: <https://docs.github.com/en/copilot/reference/hooks-reference>

### Cloud agent setup steps: `copilot-setup-steps.yml`

> located at `.github/workflows/copilot-setup-steps.yml` within your
> repository

It is an exact-filename rule. The file is a real GitHub Actions workflow, so
it keeps the `workflow`, `pipeline`, `GitHub` and `Git` tags from
`METADATA_RULES` and gains `AI`, `Copilot` and `config`. Only `.yml` is
documented, so `.yaml` is not matched.

Source: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/customize-the-agent-environment>

## Considered and not added

| Candidate | Why not |
|---|---|
| `copilot-code-review.yml` | Mentioned on the environment page, with no documented location. |
| `copilot-setup-steps.yaml` | Not documented. |
| `~/.copilot/` (agents, skills, hooks, settings) | User-level. Every repository form above is documented separately, so the twin is accepted. It is listed in *The user-level trap*. |
| `AGENTS.md`, `CLAUDE.md` as Copilot | Copilot reads them, but they stay `Agents` and `Claude`. |

## Effect on kospex

No tag enters or leaves the vocabulary: `agent`, `skill`, `hook`, `config`
and `Copilot` already exist. Stored rows for these files gain the AI tags on
the next re-sync, which the version bump triggers.

## Docs and tests

- `tests/test_ai_detection.py`, `TestCopilotCurrentConventions`: each
  convention; chat modes still detected (directory and suffix); `.claude/agents/`
  beating the suffix; setup steps keeping its workflow tags. Ten tests failed
  before the rules were added; the three guards passed.
- Fixtures under `src/tests/.github/`: `agents/reviewer.agent.md`,
  `chatmodes/planner.chatmode.md`, `skills/review/SKILL.md`,
  `hooks/policy.json`, `copilot/settings.json` and
  `workflows/copilot-setup-steps.yml`. That workflow is under `src/tests/`,
  so GitHub Actions does not run it.
- `docs/ai-detection-rules.md`: Copilot inventory, a sources row, the
  chat mode note, the user-level twins and the rule count.
- `CHANGELOG.md` under `## [Unreleased]`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli> | `.github/agents/`, `.agent.md`, `~/.copilot/agents/` | 2026-10-30 |
| <https://code.visualstudio.com/docs/copilot/customization/custom-chat-modes> | Chat modes renamed to custom agents; workspace agent locations | 2026-10-30 |
| <https://code.visualstudio.com/docs/copilot/customization/overview> | Workspace customisation files in VS Code | 2026-10-30 |
| <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills> | `.github/skills/`, personal skill locations, supported surfaces | 2026-10-30 |
| <https://docs.github.com/en/copilot/reference/hooks-reference> | `.github/hooks/*.json`, `.github/copilot/settings.json` and `settings.local.json`, user-level hooks | 2026-10-30 |
| <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/customize-the-agent-environment> | `.github/workflows/copilot-setup-steps.yml` | 2026-10-30 |

### Leads, not used as confirmation

Found while searching. Each pointed at something the official sources above
then confirmed or left out, and none is the basis for a rule.

| Page | What it said | Outcome |
|---|---|---|
| <https://www.developersdigest.tech/reference/copilot-cli/config-files> | Third-party: `.github/copilot/settings.json` is committed repository settings, and `settings.local.json` holds personal overrides | Confirmed by the official hooks reference |
| <https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-skills> | Visual Studio: a skill is a folder with a `SKILL.md` | Consistent with the GitHub skills page; no extra paths |
| <https://awesome-copilot.github.com/instruction/agents/> | Community: `.agent.md` naming is lowercase with hyphens | Naming detail only; not needed for path matching |
