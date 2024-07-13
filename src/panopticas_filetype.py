""" File type analysis functions for Panopticas """
import os
import pathspec

def get_fileext(file_path):
    """ Get the file extension of a file """
    file_type = None
    if os.path.isfile(file_path):
        file_type = os.path.splitext(file_path)[1]
    if file_type:
        return file_type
    else:
        return os.path.basename(file_path)

def get_extension_filetype(file_path):
    """ Get the file extension of a file, using an exact match """ 
    filetypes = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.html': 'HTML',
            '.htm': 'HTML',
            '.css': 'CSS',
            '.c': 'C',
            '.cpp': 'C++',
            '.java': 'Java',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.sh': 'Shell',
            '.pl': 'Perl',
            '.go': 'Go',
            '.rs': 'Rust',
            '.kt': 'Kotlin',
            '.swift': 'Swift',
            '.r': 'R',
            '.cs': 'C#',
            '.m': 'Objective-C',
            '.scala': 'Scala',
            '.sql': 'SQL',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.ini': 'INI',
            '.md': 'Markdown',
            '.rst': 'ReStructuredText',
            '.txt': 'Text',
            '.csv': 'CSV',
            '.ts': 'TypeScript',
            '.jsx': 'JSX',
            '.tf': 'Terraform',
            '.tsx': 'TSX',
            '.vue': 'Vue',
            '.xml': 'XML',
            '.gitignore': 'Gitignore',
            '.dockerignore': 'Dockerignore',
            'dockerfile': 'Dockerfile',
            }

    if file_path:
        return filetypes.get(file_path.lower(), None)
    else:
        return None

def check_shebang(file_path):
    """ Check if a file has a shebang """
    with open(file_path) as file:
        first_line = file.readline()
        if first_line and first_line.startswith("#!"):
            return first_line.strip()
        else:
            return None

def get_shebang_language(shebang):
    """ Return the language of a shebang """
    return None

def load_gitignore_patterns(directory):
    """
    Load gitignore patterns from a directory
    """
    gitignore_path = os.path.join(directory, '.gitignore')

    if os.path.exists(gitignore_path):

        with open(gitignore_path, 'r') as file:
            patterns = file.read().splitlines()
            # Add .git to the patterns
            patterns.append('.git')
            # These seem to be ignore by git
            patterns.append('.jekyll-cache')
            patterns.append('.ruff_cache')
            patterns.append('.DS_Store')

        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    return None

def identify_files(directory):
    """ Identify files in a directory """

    gitignore_spec = load_gitignore_patterns(directory)

    file_paths = {}
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            if gitignore_spec and gitignore_spec.match_file(relative_path):
                continue
            ftype = None
            ext = get_fileext(full_path)
            if ext:
                ftype = get_extension_filetype(ext)

            if directory == ".":
                full_path = full_path.removeprefix("./")

            file_paths[full_path] = ftype

    return file_paths


def extract_shebang_language(shebang: str) -> str:
    """
    Take a string like 
    #!/usr/bin/env python3
    and return the language (python3)
    """
    parts = shebang.split()
    # Check if the shebang string starts with '#!' and has at least two parts
    # Check for #!/usr/bin/env python3 pattern
    if "#!" in parts[0] and len(parts) > 1:

        # Split the second part by '/' and check if it contains 'env'
        if 'env' in parts[0]:
            return parts[-1]  # The interpreter is the last part

    # Check for 
    # #!/usr/local/bin/perl style pattern
    else:
        return shebang.split('/')[-1]  # Otherwise, the interpreter is the last 

    return None

def get_language(file_path):
    """ Return the language of a file """
    return None

def basename_check(file_path):
    """
    Return a guessed type based on the basename 
    """

    return None
