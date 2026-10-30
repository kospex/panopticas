# Agent Skills Directory Detection

Closes [#62](https://github.com/kospex/panopticas/issues/62).

**Status:** implemented. Verified on 2026-10-30. The convention came up while
re-verifying Warp for [#33](https://github.com/kospex/panopticas/issues/33),
and was left out of that change because it belongs to no single product.

## Summary

[Agent Skills](https://agentskills.io/) is an open format for agent skills,
which Anthropic originally developed. A skill is a directory containing a
`SKILL.md`, with optional `scripts/`, `references/` and `assets/`. Several
agents now name `.agents/skills/` as the project location for skills, but it
was not detected:

    path                                  before                  after
    .agents/skills/release/SKILL.md       None                    (Agents, skill)
    .openhands/skills/repo/SKILL.md       (OpenHands, config)     (OpenHands, skill)

## Who documents `.agents/skills/`

| Product | What the docs say | Source |
|---|---|---|
| Codex (OpenAI) | "Where Codex loads local skills" lists `$CWD/.agents/skills`, `$CWD/../.agents/skills` and `$REPO_ROOT/.agents/skills` as repository locations, and `$HOME/.agents/skills` as the user one | <https://learn.chatgpt.com/docs/build-skills> (`developers.openai.com/codex/skills` now redirects there) |
| OpenHands | "use `.agents/skills/` for new skills", and it "takes precedence over the legacy directories" | <https://docs.openhands.dev/usage/prompting/microagents-overview> |
| Warp | Lists `.agents/skills/` as "(recommended)" first among the project skill directories it scans | <https://docs.warp.dev/agents/capabilities/skills/> |

The [specification](https://agentskills.io/specification.md) itself defines
the skill directory and the `SKILL.md` format, but names no discovery path.
The location is a convention the clients have agreed on, not part of the
spec.

## OpenHands' legacy `skills/` directory

OpenHands documents two legacy directories:

> Both the legacy `.openhands/skills/` and `.openhands/microagents/`
> directories remain supported.

Only `.openhands/microagents/` had a rule, so `.openhands/skills/` fell
through to `.openhands/` → `config`.

## Rules added

```python
# path_contains
".openhands/skills/": ("OpenHands", "skill"),
".agents/skills/":    ("Agents", "skill"),
```

`Agents` is the existing pseudo-product for vendor-neutral files (`AGENTS.md`,
`.aiignore`), and `skill` is an existing kind.

## Considered and not added

| Candidate | Why not |
|---|---|
| A bare `.agents/` → `(Agents, config)` fallback | The only other documented file is `.agents/.mcp.json`, which Warp reads, and the `.mcp.json` exact-filename rule already tags it `MCP`. Nothing else under `.agents/` is documented, so a fallback would be a guess. |
| `~/.agents/skills/` | User-level. The repository form is documented separately, as with `.junie/` and `.augment/rules/`, so the twin is accepted. It is listed in *The user-level trap*. |
| Per-vendor skill directories Warp also scans (`.codex/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.copilot/skills/`, `.factory/skills/`, `.github/skills/`, `.opencode/skills/`) | Each would need checking against that vendor's own docs. Warp reading them is not evidence that the vendor documents them. The ones under an existing product directory already get that product's `config` tag. |

## Effect on kospex

No tag enters or leaves the vocabulary (still 130), so `tests/data/tag_snapshot.txt`
and `DEPRECATED_TAGS` are unchanged.

Files under `.openhands/skills/` change from `config` to `skill`. Stored
rows keep `config` until a re-sync, which the version bump triggers. A kospex
query for `skill` misses those files until then; a query for `config` keeps
matching them.

## Docs and tests

- `tests/test_ai_detection.py`, `TestAgentSkills`: `.agents/skills/` at the
  root, nested, and on a non-`SKILL.md` file inside a skill; `.openhands/skills/`.
  Guards check that a bare `.agents/` file is not detected and that
  `.agents/.mcp.json` stays `(MCP, config)`. Five tests failed before the rules
  were added; the two guards passed.
- Fixtures: `src/tests/.agents/skills/release/SKILL.md` and
  `src/tests/.openhands/skills/repo/SKILL.md`.
- `docs/ai-detection-rules.md`: inventory rows, a sources row, the
  OpenHands row in *Vendors that have moved or rebranded*, the user-level
  twins, and the rule count (66).
- `CHANGELOG.md` under `## [Unreleased]`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://learn.chatgpt.com/docs/build-skills> | Codex repository and user skill locations | 2026-10-30 |
| <https://docs.openhands.dev/usage/prompting/microagents-overview> | `.agents/skills/` preferred; `.openhands/skills/` and `.openhands/microagents/` legacy | 2026-10-30 |
| <https://docs.warp.dev/agents/capabilities/skills/> | Warp's project and global skill directories | 2026-10-30 (page updated 2026-10-26) |
| <https://agentskills.io/specification.md> | Skill directory and `SKILL.md` format; no discovery path | 2026-10-30 |
| <https://agentskills.io/> | Origin and status of the format | 2026-10-30 |
