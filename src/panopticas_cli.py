# panopticas.py
import click
from prettytable import PrettyTable
import panopticas as ft

@click.group()
def cli():
    """Panopticas is a tool for identifying file types, code and git repositories.
    
    In future, it will be possible identify external dependencies
    (e.g. URLs, cloud providers)

    For documentation on how commands run `panopticas COMMAND --help`.

    See also https://panopticas.io/
    
    """

@cli.command("assess")
#@click.option('--default', is_flag=True, default=False, help="Create the default ~/code directory.")
@click.argument('directory', required=False, type=click.Path(exists=True))
def assess(directory):
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
        table.add_row([file, file_type, meta])
        #click.echo(files[file])
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
    print(table)
    print()

@cli.command("version")
def version():
    """Print the version of Panopticas."""
    #click.echo(f"Panopticas version {panopticas_core.__version__}")
    click.echo("Panopticas version 0.0.2")

if __name__ == '__main__':
    cli()