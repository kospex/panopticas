# Tag vocabulary, JSON output and rich migration

**Version:** 0.0.19
**Design:** [`changes/design/specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md`](design/specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md)

## What changed

### Vocabulary functions

`get_tags()`, `get_filetypes()` and `get_languages()` return the vocabularies
panopticas uses, each a sorted, deduplicated list of strings.

`get_tags()` is **derived** by traversing `METADATA_RULES` and `AI_RULES`
rather than maintained as a list, so a new detection rule joins the vocabulary
the moment it is added. A drift test synthesises a path for every rule and
asserts the tags it produces are all in `get_tags()`, which makes that a
contract rather than a claim.

The AI kind `directory` is excluded. It is synthesised inside
`find_ai_files(all_files=True)` and never reaches a file's tags, so it cannot
be searched for in kospex.

### Language classification

`get_languages()` cannot be derived — nothing in the data says whether `PNG`
is a language — so `constants.py` carries `LANGUAGE_FILETYPES` (32) and
`NON_LANGUAGE_FILETYPES` (44). Both sets exist so that a completeness test can
fail when a newly added file type is unclassified; an exclusion list alone
would silently default it to "language".

The principle: a language expresses behaviour or presentation. Data formats
(JSON, YAML, XML), prose (Markdown), binaries (PNG) and named config files
(go.sum) are file types but not languages. This matches what GitHub displays —
its language bar counts only Linguist's `programming` and `markup` types.

### CLI

- New `tags`, `languages` and `filetypes` commands, printing a column grid.
- `--json` (also `-json`) on all seven commands. Every document is a JSON
  object, never a bare array, so fields can be added later without breaking a
  parser. In JSON mode stdout carries only the document; progress messages go
  to stderr.
- Path arguments are validated at the Click boundary. `assess` and `urls`
  require a directory, `file` requires a file. Previously a wrong path type
  gave empty output or an unhandled `IsADirectoryError`.

### rich replaces prettytable

Matches kospex and foundationx. Rich parses `[...]` as markup in anything it
prints, so untrusted paths and URLs now pass through `cell()`, which strips
terminal control characters and escapes markup. Tags, products and kinds come
from `constants.py` and are trusted.

## kospex impact

None. kospex declares `prettytable` and `rich` directly, and depends on
`panopticas>=0.0.18`, so this release reaches it without a manual pin bump.
No tag was renamed or removed, so stored `tech_type` values stay valid.
