# Editor and IDE Project File Detection

Closes [#20](https://github.com/kospex/panopticas/issues/20).

**Status:** implemented. Verified on 2026-10-30.

## Summary

`.vscode/mcp.json` was detected as MCP config, but every other editor project
file had no tags:

    path                        before    after
    .vscode/settings.json       []        VS Code, editor, config
    project.code-workspace      []        VS Code, editor, config
    .idea/misc.xml              []        JetBrains, editor, config
    app.iml                     []        JetBrains, editor, config
    .zed/settings.json          []        Zed, editor, config
    project.sublime-project     []        Sublime Text, editor, config
    .vscode/mcp.json            AI, MCP, config
                                          VS Code, editor, config, AI, MCP

## Decisions (made with the maintainer)

- **A new `editor` tag**, so one tag finds every editor's project files,
  plus a brand tag per editor. The issue asked whether to introduce `editor`
  as a considered set rather than one editor at a time, and this does.
- **Editors:** VS Code, JetBrains, Zed and Sublime Text.
- **`VS Code` casing:** Microsoft's own short form, and distinct from the
  existing `Visual Studio` tag (from `.sln`), which a `LIKE '%Visual Studio%'`
  query would otherwise also match.
- **`METADATA_RULES`, not `AI_RULES`.** As the issue said, an editor is not an
  AI agent. `.vscode/mcp.json` stays in `AI_RULES`, and `get_filename_metatypes()`
  applies AI tags as a separate pass, so it carries both sets.

## Verified conventions

### VS Code: `.vscode/` and `*.code-workspace`

> VS Code stores workspace settings at the root of the project in a `.vscode` folder.

> Workspace settings are stored in `.vscode/settings.json` when you open a folder as a workspace.

> Workspace or folder specific tasks are configured from the tasks.json file in the .vscode folder for a workspace.

The multi-root workspaces page: "When you save your workspace, it will create
a `.code-workspace` file", and "Relative paths are better when you want to
share Workspace files." The file has no fixed location, so it is an extension
rule. It is JSON with comments, so its filetype is `JSONC`.

Sources: <https://code.visualstudio.com/docs/configure/settings>,
<https://code.visualstudio.com/docs/editing/workspaces/workspaces>,
<https://code.visualstudio.com/docs/debugtest/tasks>,
<https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces>

### JetBrains: `.idea/` and `*.iml`

> For the directory-based format, the IDE creates the .iml file and the .idea
> directory that keeps project settings.

This is the format shared by IntelliJ IDEA, PyCharm, WebStorm, Rider and the
other JetBrains IDEs, so the brand tag is `JetBrains`, not one IDE. On version
control, JetBrains' 2017.2 help says to share `.idea/` except `workspace.xml`
and `tasks.xml`, which hold user-specific settings, and to share the `.iml`
files. That page is old, but no current page that replaces it was found. The
rules tag everything under `.idea/`: panopticas detects, and whether a file
should be committed is a policy question for kospex.

The legacy file-based format (`.ipr`, `.iws`) is not added. It still exists,
but was not checked further.

Sources: <https://www.jetbrains.com/help/idea/creating-and-managing-projects.html>,
<https://www.jetbrains.com/help/idea/2017.2/managing-projects-under-version-control.html>

### Zed: `.zed/`

From Zed's docs source (`docs/src/configuring-zed.md`):

> Override user settings for a specific project by creating a
> `.zed/settings.json` file in your project root.

Tasks: "in the worktree-specific (local) `.zed/tasks.json` file". Debug
configurations go in `.zed/debug.json` at the project root. The user-level
equivalents are under `~/.config/zed/`, outside `.zed/`.

Sources: <https://zed.dev/docs/configuring-zed> (via
<https://github.com/zed-industries/zed/blob/main/docs/src/configuring-zed.md>),
<https://zed.dev/docs/tasks>, <https://zed.dev/docs/debugger>

### Sublime Text: `*.sublime-project` and `*.sublime-workspace`

> the .sublime-workspace file, which contains user specific data, such as the
> open files and the modifications to each.

> the .sublime-project file would be checked into version control … the
> .sublime-workspace file would not.

Both are tagged, because a committed `.sublime-workspace` is still a Sublime
Text file. Both are JSON.

Source: <https://www.sublimetext.com/docs/projects.html>

## The `break` in `path_contains_rules`

Only the longest matching path fragment applies (`core.py`). The existing
fragments are `.github/workflows`, `.github`, `.buildkite/`, `.circleci/`,
`config/checkstyle/` and `sorbet/`. A file would have to sit inside both
directories to match two, for example `.github/.vscode/x`, which is not a
real convention. No interaction.

## Considered and not added

| Candidate | Why not |
|---|---|
| Cursor | Cursor's repository directory, `.cursor/`, holds AI rules, skills and MCP config, which `AI_RULES` already tags as Cursor. Cursor is a VS Code fork; per its forum, though not its docs, it reads workspace settings from `.vscode/settings.json`, which is now tagged VS Code. There is no Cursor-specific editor settings file to tag. Raised with the maintainer. |
| `.vs/` (Visual Studio) | Visual Studio's per-user cache, conventionally gitignored. Not checked against Microsoft's docs. |
| `.fleet/` (JetBrains Fleet) | Not checked. |
| `.dir-locals.el` (Emacs), `.exrc` (Vim) | Not checked. Editor settings outside a dedicated directory. |
| `.editorconfig` | Editor-neutral and already a linter rule. A test pins it as not `editor`. |

## Effect on kospex

Five new tags: `editor`, `VS Code`, `JetBrains`, `Zed` and `Sublime Text`
(137 in total, with #64's `Factory` and `OpenCode`), all in `tests/data/tag_snapshot.txt`. The files were
untagged before, so nothing changes or is retired. `.vscode/mcp.json` gains
three tags.

## Docs and tests

- `tests/test_editor_detection.py`: each editor file, a nested project,
  `.vscode/mcp.json` keeping its AI tags, the new filetypes, and
  `.editorconfig` unchanged. Nineteen tests failed before the rules were
  added; the `.editorconfig` guard passed.
- Fixtures: `src/tests/.vscode/{settings,launch,tasks,extensions}.json`,
  `src/tests/.idea/misc.xml`, `src/tests/.zed/{settings,tasks}.json`,
  `src/tests/sample.code-workspace`, `src/tests/sample.iml` and
  `src/tests/sample.sublime-project`.
- `docs/cli.md`, `docs/api.md`: tag count.
- `CHANGELOG.md` under `## [Unreleased]`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://code.visualstudio.com/docs/configure/settings> | `.vscode/` workspace settings | 2026-10-30 |
| <https://code.visualstudio.com/docs/editing/workspaces/workspaces> | `.vscode/settings.json` | 2026-10-30 |
| <https://code.visualstudio.com/docs/debugtest/tasks> | `.vscode/tasks.json` | 2026-10-30 |
| <https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces> | `.code-workspace` | 2026-10-30 |
| <https://www.jetbrains.com/help/idea/creating-and-managing-projects.html> | `.idea/` and `.iml` | 2026-10-30 |
| <https://www.jetbrains.com/help/idea/2017.2/managing-projects-under-version-control.html> | Which `.idea/` files are shared (old, but the only official page found) | 2026-10-30, via search summary |
| <https://github.com/zed-industries/zed/blob/main/docs/src/configuring-zed.md> | `.zed/settings.json`, quoted from source | 2026-10-30 |
| <https://zed.dev/docs/tasks> | `.zed/tasks.json` | 2026-10-30 |
| <https://zed.dev/docs/debugger> | `.zed/debug.json` | 2026-10-30, via search summary |
| <https://www.sublimetext.com/docs/projects.html> | `.sublime-project` and `.sublime-workspace` | 2026-10-30 |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://forum.cursor.com/t/cursor-specific-overrides-to-vscode-settings-json/118861> | A feature request for Cursor-specific overrides of `.vscode/settings.json`, which implies Cursor reads it | The basis for "Cursor reads `.vscode/`" above; not documented by Cursor |
| <https://github.com/zed-industries/zed/pull/29160> | "Implement basic support for VS Code debug configurations", merged 2025-04-22: Zed reads `.vscode/launch.json` when there is no `.zed/debug.json` | `.vscode/` files are tagged `VS Code`, the format's owner, even when another editor reads them. Worth revisiting if `.vscode/` tagging changes. |
| <https://docs.cursor.sh/settings/vsc-import> | Cursor imports VS Code settings and extensions | User-level import; no repository file |
| <https://intellij-support.jetbrains.com/hc/articles/206544839> | A community-edited JetBrains support article on `.idea/` under version control | Consistent with the 2017.2 help page |
