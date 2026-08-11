# panopticas CLI
import json
import os
import re

import click
from prettytable import PrettyTable
from rich.columns import Columns
from rich.console import Console
from rich.markup import escape
from . import core
from .constants import VERSION

# Shared console for all rich output.
console = Console()


# Both spellings are accepted. The repository already mixes single- and
# double-dash long options, so neither is "wrong" to type.
#
# This must be defined before any command, not beside them: it is applied as
# a decorator, which evaluates when the module loads, so a definition further
# down the file raises NameError on import.
json_option = click.option(
    '--json', '-json', 'as_json', is_flag=True, default=False,
    help="Output as JSON.")


@click.group(invoke_without_command=True)
@click.version_option(version=VERSION)
@click.pass_context
def cli(ctx):
    """Panopticas is a tool for identifying file types, code and git repositories.

    In future, it will be possible identify external dependencies
    (e.g. URLs, cloud providers)

    For documentation on how commands run `panopticas COMMAND --help`.

    See also https://panopticas.io/

    """
    if ctx.invoked_subcommand is None:
        # Default behavior when no command is provided
        click.echo(ctx.get_help())
        ctx.exit(0)

@cli.command("assess")
@click.option('-unknown', is_flag=True, default=False, help="Show only files with an unknown language type.")
@click.option('--lines', is_flag=True, default=False, help="Include line count for each file.")
@json_option
@click.argument('directory', required=False,
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def assess(directory, unknown, lines, as_json):
    """Assess a directory."""
    if not as_json:
        click.echo()
    if directory:
        banner(f'Assessing directory: {directory}', as_json)
    else:
        banner('Assessing current directory.', as_json)
        directory = "."

    if lines:
        files = core.identify_files_with_metrics(directory)
    else:
        files = core.identify_files(directory)

    records = []
    for file, file_info in files.items():
        file_type = file_info['type'] if lines else file_info
        if unknown and file_type is not None:
            continue
        record = {
            "path": file,
            "language": file_type,
            "meta": core.get_filename_metatypes(file),
        }
        if lines:
            line_count = file_info['lines']
            # count_lines() yields "N/A" for binaries; JSON says null.
            record["lines"] = line_count if isinstance(line_count, int) else None
        records.append(record)

    if as_json:
        payload = {
            "directory": directory,
            "count": len(records),
            "files": records,
        }
        if lines:
            payload["total_lines"] = sum(
                r["lines"] for r in records if r["lines"] is not None)
        emit_json(payload)
        return

    banner(f'Found {len(files)} files.\n', as_json)
    table = PrettyTable()

    if lines:
        table.field_names = ["File", "Language", "Meta", "Lines"]
        table.align["Lines"] = "r"
    else:
        table.field_names = ["File", "Language", "Meta"]

    table.align["File"] = "l"
    table.align["Language"] = "l"
    table.align["Meta"] = "l"

    for record in records:
        row = [record["path"], record["language"], ", ".join(record["meta"])]
        if lines:
            row.append(record["lines"] if record["lines"] is not None else "N/A")
        table.add_row(row)

    print(table, "\n")

    total_files = len(records)
    if lines:
        counted = [r["lines"] for r in records if r["lines"] is not None]
        excluded = total_files - len(counted)
        if excluded:
            print(f"Total files: {total_files}, Total # of Lines: {sum(counted):,} "
                  f"({excluded} files excluded - binary/N/A)")
        else:
            print(f"Total files: {total_files}, Total # of Lines: {sum(counted):,}")
    else:
        print(f"Total files: {total_files}")

    print()


def print_vocabulary(values, noun):
    """Print a vocabulary as a column grid with a count beneath."""
    console.print()
    console.print(Columns(values, padding=(0, 2), equal=True))
    console.print(f"\n{len(values)} {noun}\n")


def emit_json(payload):
    """
    Write a JSON document to stdout and nothing else.

    Everything a command would normally print as chatter goes to stderr in
    JSON mode (see banner()), so stdout stays pipeable into jq or a parser.
    """
    click.echo(json.dumps(payload, indent=2))


def banner(message, as_json):
    """
    Print progress chatter, routed to stderr when JSON is being emitted so it
    cannot corrupt the document on stdout.

    Sanitised because callers interpolate a path into the message — an
    argv-supplied directory could otherwise carry terminal control sequences.
    The literal parts contain no control characters, so sanitising the whole
    message is safe and means no call site can forget. Rich markup needs no
    handling here: click.echo() does not parse it.
    """
    click.echo(sanitise_for_display(message), err=as_json)


@cli.command("tags")
@json_option
def tags(as_json):
    """Show every tag panopticas can assign to a file."""
    values = core.get_tags()
    if as_json:
        emit_json({"tags": values, "count": len(values)})
    else:
        print_vocabulary(values, "tags")


@cli.command("languages")
@json_option
def languages(as_json):
    """Show every language panopticas recognises."""
    values = core.get_languages()
    if as_json:
        emit_json({"languages": values, "count": len(values)})
    else:
        print_vocabulary(values, "languages")


@cli.command("filetypes")
@json_option
def filetypes(as_json):
    """Show every file type panopticas recognises, languages or not."""
    values = core.get_filetypes()
    if as_json:
        emit_json({"filetypes": values, "count": len(values)})
    else:
        print_vocabulary(values, "filetypes")

# Filenames may contain almost any byte, and panopticas scans repositories
# it does not control. An escape sequence in a path would be interpreted by
# the terminal rather than displayed, letting a crafted filename rewrite what
# the operator sees. Strip the C0 control range and DEL (\x00-\x1f, \x7f) as
# well as the C1 control range (\x80-\x9f) before printing — C1 includes
# \x9b, the single-byte CSI introducer some terminals in 8-bit control mode
# will interpret as an escape sequence with no preceding ESC.
CONTROL_CHARACTERS = re.compile(r'[\x00-\x1f\x7f-\x9f]')


def sanitise_for_display(text):
    """Remove control characters and ANSI escapes from text bound for a terminal."""
    return CONTROL_CHARACTERS.sub('', text)


def cell(value):
    """
    Render an untrusted value safely for the terminal.

    Two distinct problems. sanitise_for_display() removes control characters
    a crafted filename could use to rewrite what the operator sees. Rich adds
    a second surface: it parses [...] in any string it prints as markup, so
    escape() is needed as well, or a file named "[blink]evil.py" would style
    the output instead of appearing in it.

    Applies to paths and URLs. Tags, products, kinds and file types come from
    constants.py and are trusted.
    """
    return escape(sanitise_for_display(value))


@cli.command("ai")
@click.option('--all-files', is_flag=True, default=False,
              help="Include gitignored files and bare AI directories.")
@json_option
@click.argument('directory', required=False,
                 type=click.Path(exists=True, file_okay=False, dir_okay=True))
def ai(directory, all_files, as_json):
    """Find AI coding agent files and directories."""
    if not as_json:
        click.echo()
    if directory:
        banner(f'Assessing directory: {directory}', as_json)
    else:
        banner('Assessing current directory.', as_json)
        directory = "."
    if not as_json:
        click.echo()

    ai_files = core.find_ai_files(directory, all_files=all_files)

    # Most-used product first, then alphabetical.
    counts = {}
    for metadata in ai_files.values():
        counts[metadata["product"]] = counts.get(metadata["product"], 0) + 1
    counts = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))

    if as_json:
        emit_json({
            "directory": directory,
            "count": len(ai_files),
            "products": counts,
            "paths": [
                {"path": path, "product": ai_files[path]["product"],
                 "kind": ai_files[path]["kind"]}
                for path in sorted(ai_files)
            ],
        })
        return

    table = PrettyTable()
    table.field_names = ["Path", "Product", "Kind"]
    table.align["Path"] = "l"
    table.align["Product"] = "l"
    table.align["Kind"] = "l"

    for path in sorted(ai_files):
        metadata = ai_files[path]
        # Only the path is untrusted — product and kind come from AI_RULES.
        table.add_row(
            [sanitise_for_display(path), metadata["product"], metadata["kind"]])

    print(table, "\n")

    if counts:
        products = ", ".join(
            f"{product} ({count})" for product, count in counts.items())
        print(f"Found {len(ai_files)} AI paths. Products: {products}")
    else:
        print("Found 0 AI paths.")

    print()

@cli.command("file")
@json_option
@click.argument('file', required=True, type=click.Path(exists=True, dir_okay=False))
def identify(file, as_json):
    """Assess a filetype."""
    extension = core.get_fileext(file)
    shebang = core.check_shebang(file)
    payload = {
        "file": file,
        "extension": extension,
        "filetype": core.get_extension_filetype(extension),
        "shebang": shebang,
        "shebang_language": (
            core.extract_shebang_language(shebang) if shebang else None),
        "meta": core.get_filename_metatypes(file),
        "urls": core.extract_urls_from_file(file),
    }

    if as_json:
        emit_json(payload)
        return

    click.echo(f'\nAssessing filetype for file {file}')
    click.echo()
    table = PrettyTable()
    table.field_names = ["Method", "Result"]
    table.align["Method"] = "l"
    table.align["Result"] = "l"

    table.add_row(["File extenion", payload["extension"]])
    table.add_row(["File type", payload["filetype"]])
    table.add_row(["Shebang", payload["shebang"]])
    table.add_row(["Shebang Language", payload["shebang_language"]])
    table.add_row(["Meta", payload["meta"]])
    table.add_row(["URLs", '\n'.join(payload["urls"])])

    print(table)
    print()


@cli.command("urls")
@click.option('-all-files', is_flag=True, default=False, help="Show all files, no gitignore.")
@json_option
@click.argument('directory', required=True,
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def find_urls(directory, all_files, as_json):
    """
    Find and show urls for all files in a given directory.
    """
    files = core.find_files(directory, all_files=all_files)
    # find_files() returns paths relative to `directory`, not to the
    # process's cwd — join with `directory` to read the file, but keep the
    # relative path in the record so JSON/table output matches prior output.
    records = [
        {"path": f, "urls": core.extract_urls_from_file(os.path.join(directory, f))}
        for f in files
    ]

    if as_json:
        emit_json({
            "directory": directory,
            "count": len(records),
            "files": records,
        })
        return

    table = PrettyTable()
    table.field_names = ["Filename", "URLs"]
    table.align["Filename"] = "l"
    table.align["URLs"] = "l"

    for record in records:
        table.add_row([record["path"], '\n'.join(record["urls"])])

    print(table)
    print()

if __name__ == '__main__':
    cli()
