# panopticas.py
import click
from prettytable import PrettyTable
import panopticas as ft

VERSION = "0.0.9"

@click.group()
def cli():
    """Panopticas is a tool for identifying file types, code and git repositories.

    In future, it will be possible identify external dependencies
    (e.g. URLs, cloud providers)

    For documentation on how commands run `panopticas COMMAND --help`.

    See also https://panopticas.io/

    """

@cli.command("assess")
@click.option('-unknown', is_flag=True, default=False, help="Show only files with an unknown language type.")
@click.argument('directory', required=False, type=click.Path(exists=True))
def assess(directory,unknown):
    """Assess a directory."""
    click.echo()
    if directory:
        click.echo(f'Assessing directory: {directory}')
    else:
        click.echo('Assessing current directory.')
        directory = "."
    files = ft.identify_files(directory)
    click.echo(f'Found {len(files)} files.\n')
    table = PrettyTable()
    table.field_names = ["File", "Language", "Meta"]
    table.align["File"] = "l"
    table.align["Language"] = "l"
    table.align["Meta"] = "l"

    for file, file_type in files.items():
        meta = ft.get_filename_metatypes(file) if ft.get_filename_metatypes(file) else ""
        if meta:
            meta = ", ".join(meta)
        # with "unknown", we only include files with unknown language types (e.g. None)
        if unknown:
            if file_type is None:
                #print(f"File: {file} is of unknown language type")
                table.add_row([file, file_type, meta])
        else:
            # Default is we add it to the table
            table.add_row([file, file_type, meta])

    print(table,"\n")

@cli.command("file")
@click.argument('file', required=True,type=click.Path(exists=True))
def identify(file):
    """Assess a filetype."""
    click.echo(f'\nAssessing filetype for file {file}')
    click.echo()
    table = PrettyTable()
    table.field_names = ["Method", "Result"]
    table.align["Method"] = "l"
    table.align["Result"] = "l"

    table.add_row(["File extenion", ft.get_fileext(file)])
    table.add_row(["File type", ft.get_extension_filetype(ft.get_fileext(file))])
    shebang = ft.check_shebang(file)
    table.add_row(["Shebang", shebang])
    table.add_row(["Shebang Language", ft.extract_shebang_language(shebang) if shebang else None])
    table.add_row(["Meta", ft.get_filename_metatypes(file)])

    urls = []

    urls = ft.extract_urls_from_file(file)
    table.add_row(["URLs", '\n'.join(urls)])

    print(table)
    print()

@cli.command("urls")
@click.option('-all-files', is_flag=True, default=False, help="Show all files, no gitignore.")
@click.argument('directory', required=True, type=click.Path(exists=True))
def find_urls(directory,all_files):
    """
    Find and show urls for all files in a given directory.
    """
    files = ft.find_files(directory,all_files=all_files)

    table = PrettyTable()
    table.field_names = ["Filename", "URLs"]
    table.align["Filename"] = "l"
    table.align["URLs"] = "l"

    # ft.find_files(directory)
    for f in files:
        urls = ft.extract_urls_from_file(f)
        table.add_row([f, '\n'.join(urls)])

    print(table)
    print()


@cli.command("version")
def version():
    """Print the version of Panopticas."""
    click.echo(f"Panopticas CLI version {VERSION}")
    click.echo(f"Panopticas v{ft.VERSION}")

if __name__ == '__main__':
    cli()
