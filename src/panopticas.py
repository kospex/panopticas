# panopticas.py
import click
from prettytable import PrettyTable
import panopticas_filetype as ft

@click.group()
def cli():
    """Panopticas is a tool for assessing code and git repositories.
    
    It is designed to analysis external dependencies (e.g. URLs, cloud providers)

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
    table.field_names = ["File", "Language"]
    table.align["File"] = "l"
    table.align["Language"] = "l"
    for file in files:
        table.add_row([file, files[file]])
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
    print(table)
    print()

@cli.command("version")
def version():
    """Print the version of Panopticas."""
    #click.echo(f"Panopticas version {panopticas_core.__version__}")
    click.echo("Panopticas version 0.0.1")

if __name__ == '__main__':
    cli()