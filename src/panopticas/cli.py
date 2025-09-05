# panopticas CLI
import click
from prettytable import PrettyTable
from . import core
from .constants import VERSION


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
@click.argument('directory', required=False, type=click.Path(exists=True))
def assess(directory, unknown, lines):
    """Assess a directory."""
    click.echo()
    if directory:
        click.echo(f'Assessing directory: {directory}')
    else:
        click.echo('Assessing current directory.')
        directory = "."
    # Use appropriate function based on whether line counting is requested
    if lines:
        files = core.identify_files_with_metrics(directory)
    else:
        files = core.identify_files(directory)
    click.echo(f'Found {len(files)} files.\n')
    table = PrettyTable()
    
    # Set table headers based on whether line counting is enabled
    if lines:
        table.field_names = ["File", "Language", "Meta", "Lines"]
        table.align["Lines"] = "r"
    else:
        table.field_names = ["File", "Language", "Meta"]
    
    table.align["File"] = "l"
    table.align["Language"] = "l"
    table.align["Meta"] = "l"

    for file, file_info in files.items():
        # Handle different data structures based on line counting
        if lines:
            file_type = file_info['type']
            line_count = file_info['lines']
        else:
            file_type = file_info
            line_count = None
            
        meta = core.get_filename_metatypes(file) if core.get_filename_metatypes(file) else ""
        if meta:
            meta = ", ".join(meta)
        
        # with "unknown", we only include files with unknown language types (e.g. None)
        if unknown:
            if file_type is None:
                #print(f"File: {file} is of unknown language type")
                if lines:
                    table.add_row([file, file_type, meta, line_count])
                else:
                    table.add_row([file, file_type, meta])
        else:
            # Default is we add it to the table
            if lines:
                table.add_row([file, file_type, meta, line_count])
            else:
                table.add_row([file, file_type, meta])

    print(table,"\n")
    
    # Display totals summary
    total_files = len(files)
    if lines:
        # Calculate total lines when line counting is enabled
        total_lines = 0
        files_with_lines = 0
        files_excluded = 0
        
        for file, file_info in files.items():
            line_count = file_info['lines']
            if isinstance(line_count, int):
                total_lines += line_count
                files_with_lines += 1
            else:
                # Handle "N/A" values (binary files)
                files_excluded += 1
        
        if files_excluded > 0:
            print(f"Total files: {total_files}, Total # of Lines: {total_lines:,} ({files_excluded} files excluded - binary/N/A)")
        else:
            print(f"Total files: {total_files}, Total # of Lines: {total_lines:,}")
    else:
        print(f"Total files: {total_files}")
    
    print()

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

    table.add_row(["File extenion", core.get_fileext(file)])
    table.add_row(["File type", core.get_extension_filetype(core.get_fileext(file))])
    shebang = core.check_shebang(file)
    table.add_row(["Shebang", shebang])
    table.add_row(["Shebang Language", core.extract_shebang_language(shebang) if shebang else None])
    table.add_row(["Meta", core.get_filename_metatypes(file)])

    urls = []

    urls = core.extract_urls_from_file(file)
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
    files = core.find_files(directory,all_files=all_files)

    table = PrettyTable()
    table.field_names = ["Filename", "URLs"]
    table.align["Filename"] = "l"
    table.align["URLs"] = "l"

    # core.find_files(directory)
    for f in files:
        urls = core.extract_urls_from_file(f)
        table.add_row([f, '\n'.join(urls)])

    print(table)
    print()

if __name__ == '__main__':
    cli()
