# Strengthen Three Weak Tests

Closes [#32](https://github.com/kospex/panopticas/issues/32).

**Status:** implemented. Tests only, with no change to package behaviour, so
there is no CHANGELOG entry.

The issue named three tests from 0.0.19 that would not fail if the code they
guard were broken. Each fix below was checked the same way the problems were
found: break the guarded code on purpose, run the old test and the new one,
and restore it.

## 1. `get_tags()` traversal branches (`tests/test_vocabulary.py`)

`TestTagDrift` asserts that no produced tag escapes the vocabulary. It cannot
see a branch dropped from `get_tags()`, because every tag the
`filename_suffix` rules produce is also produced by another rule. That is
still true after #65: `.agent.md` → `(Copilot, agent)` repeats
`.github/agents/`.

- `TestTagDrift`'s docstring now says what it guarantees and what it does
  not.
- **New `TestEveryTraversalBranch`.** For each of the seven tables
  `get_tags()` reads (three `METADATA_RULES` dicts, `function_rules` and the
  three `AI_RULES` modes), it puts a sentinel rule into that table alone
  with `monkeypatch` and asserts the sentinel tag reaches `get_tags()`. This
  is stronger than the issue's optional suggestion, "each match mode
  contributes at least one reachable tag", because it does not depend on
  today's rule data.

| Mutation | Old tests | New tests |
|---|---|---|
| Skip `filename_suffix` in `get_tags()` | 280 passed | `test_ai_match_mode[filename_suffix]` fails |

## 2. `test_covers_every_table_value` (`tests/test_vocabulary.py`)

As the issue suggested, the only change is a comment. The test computes
`expected` with the same expression `core.get_filetypes()` uses, so it is a
change-detector: a wrong formula would appear on both sides. The other
`TestGetFiletypes` tests exercise the real behaviour.

## 3. `test_combined_attack_neutralised` (`tests/test_cli_escaping.py`)

`assert not result.startswith("[bold]")` passed with `escape()` removed from
`cell()`, because the leftover `[31m` sits in front. It now asserts the
escaped form, `\[bold]`.

`[31m` itself is not escaped. With no closing bracket it is not markup, so
rich leaves it alone. An assertion that it was escaped failed on the correct
code and was dropped.

| Mutation | Old assertion | New assertion |
|---|---|---|
| `cell()` without `escape()` | passed | fails |

## 3b. DEL (`\x7f`)

A `test_del_stripped` case was added to `TestCell`.

**Correction to the issue.** It said `\x7f` had no direct test. It does:
`tests/test_ai_detection.py::TestDisplaySanitisation::test_strips_other_control_bytes`
has asserted `sanitise_for_display("a\x00b\x07c\rd\x7f") == "abcd"` since
`ecb0037` (2026-07-31). The issue looked only at `cell()`'s tests. The new
case still adds coverage at the `cell()` boundary, which is what renders
table cells.

| Mutation | Tests that fail |
|---|---|
| `CONTROL_CHARACTERS` starting at `\x80` | `test_strips_other_control_bytes` (existing) and `test_del_stripped` (new) |

## Result

The full suite passes (932). Every mutation was reverted; `src/` is unchanged.
