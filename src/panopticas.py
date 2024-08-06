"""
Analysis functions for Panopticas.
"""
import os
import re
import pathspec

VERSION = "0.0.5"

EXT_FILETYPES = {
        '.c': 'C',
        '.cpp': 'C++',
        '.cs': 'C#',
        '.css': 'CSS',
        '.csv': 'CSV',
        '.dockerignore': 'Dockerignore',
        '.gitignore': 'Gitignore',
        '.go': 'Go',
        '.gif': "GIF",
        '.h': 'C Header',
        '.htm': 'HTML',
        '.html': 'HTML',
        '.ico': 'ICO',
        '.ini': 'INI',
        '.ipynb': 'Jupyter Notebook',
        '.java': 'Java',
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.js': 'JavaScript',
        '.json': 'JSON',
        '.jsx': 'JSX',
        '.kt': 'Kotlin',
        '.m': 'Objective-C',
        '.mailmap': 'Mailmap',
        '.md': 'Markdown',
        '.php': 'PHP',
        '.pl': 'Perl',
        '.pm': 'Perl',
        '.png': 'PNG',
        '.py': 'Python',
        '.r': 'R',
        '.rb': 'Ruby',
        '.rs': 'Rust',
        '.rst': 'ReStructuredText',
        '.scala': 'Scala',
        '.sh': 'Shell',
        '.sql': 'SQL',
        '.sqlfluff': 'SQLFluff',
        '.svg': 'SVG',
        '.swift': 'Swift',
        '.tf': 'Terraform',
        '.toml': 'TOML',
        '.ts': 'TypeScript',
        '.tsv': 'TSV',
        '.tsx': 'TSX',
        '.txt': 'Text',
        '.vue': 'Vue',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        # Special cases for files without extensions or .format files
        "codeowners": "CODEOWNERS",
        'dockerfile': 'Dockerfile',
        'makefile': 'Makefile',
    }


def get_fileext(file_path):
    """ Get the file extension of a file """
    file_type = None

    #if os.path.isfile(file_path):
    #    file_type = os.path.splitext(file_path)[1]
    file_type = os.path.splitext(file_path)[1]

    if file_type:
        return file_type
    else:
        return os.path.basename(file_path)

def get_extension_filetype(file_ext):
    """ Get the file extension of a file, using an exact match """ 

    if file_ext:
        return EXT_FILETYPES.get(file_ext.lower(), None)
    else:
        return None

def get_filename_metatypes(file_path):
    """
    Return an array of metatypes based on the file_path 
    For example:
        pyproject.toml will return build, dependencies
        .github/workflows/python-app.yml will return Github, workflow
    """

    filename = os.path.basename(file_path).lower()
    ext = get_fileext(file_path)

    tags = []

    if ext == ".pm":
        # Perl module
        # Languauge should already be set by the extension
        tags.append("module")

    if filename == "pyproject.toml":
        tags.append("build")
        tags.append("dependencies")
        tags.append("Python")

    if ".github" in file_path:
        tags.append("Github")
        tags.append("Git")

    if filename == "eslint.config.js":
        tags.extend(["JavaScript", "linter", "eslint", "config"])

    if filename == ".mailmap":
        tags.append("Git")

    # TODO - use a regex style pattern to match the filename
    # try to catch the following patterns
    # requirements.txt
    # requirements-dev.txt
    # requirements-dev.in
    # requirements.in
    # requirements.dev.txt
    if filename == "requirements.txt":
        tags.append("pip")
        tags.append("Python")
        tags.append("dependencies")

    if filename == '.sqlfluff':
        tags.append("SQLFluff")
        tags.append("SQL")
        tags.append("linter")

    if filename == ".mailmap":
        tags.append("Git")

    # Usually the filename will be CODEOWNERS
    if filename == "codeowners":
        tags.append("Git")

    if filename == ".gitignore":
        tags.append("Git")
        tags.append("ignore")

    if filename == "dockerfile":
        tags.append("IaC")
        tags.append("Docker")
        tags.append("dependencies")

    if filename == ".dockerignore":
        tags.append("Docker")
        tags.append("ignore")

    if filename == "makefile":
        tags.append("build")

    if ".github/workflows" in file_path:
        tags.append("workflow")

    if filename == "go.mod":
        tags.append("Go")
        tags.append("module")
        tags.append("dependencies")

    if filename == "go.sum":
        tags.append("Go")
        tags.append("dependencies")
        # TODO - check what we actually want to call hashes etc
        # maybe integrity-checks
        tags.append("checksum")

    if filename == ".sqlfluffignore":
        tags.append("SQLFluff")
        tags.append("ignore")

    if filename == "codefresh.yml":
        tags.append("pipeline")
        tags.append("Codefresh")

    return tags

def check_shebang(file_path):
    """ Check if a file has a shebang """
    try:

        with open(file_path) as file:
            first_line = file.readline()
            if first_line and first_line.startswith("#!"):
                return first_line.strip()
            else:
                return None

    except FileNotFoundError:
        # TODO - better logging instead of print
        #print(f"File {file_path} not found")
        return None
    except UnicodeDecodeError:
        # TODO - log this exception
        return None


def get_shebang_language(shebang):
    """ Return the language of a shebang """
    lang = extract_shebang_language(shebang)
    return lang

def load_gitignore_patterns(directory):
    """
    Load gitignore patterns from a directory
    """
    gitignore_path = os.path.join(directory, '.gitignore')

    if os.path.exists(gitignore_path):

        with open(gitignore_path, 'r', encoding='utf-8') as file:
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
            # ftype = None
            # ext = get_fileext(full_path)
            ftype = get_language(full_path)
            # if ext:
            #     ftype = get_extension_filetype(ext)
            #     if not ftype:
            #         ftype = get_shebang_language(check_shebang(full_path))
            #         #ftype = basename_check(full_path)

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
            interpreter = parts[-1]
            #return parts[-1]  # The interpreter is the last part
            if interpreter.startswith("python"):
                return "Python"
            else:
                return interpreter

    # Check for the following pattern
    # #!/usr/local/bin/perl style pattern
    else:
        return shebang.split('/')[-1]  # Otherwise, the interpreter is the last 

    return None

def get_language(file_path):
    """ Return the language of a file """
    ext = get_fileext(file_path)
    lang = None

    if ext:
        lang = get_extension_filetype(ext)

    if lang:
        return lang

    shebang = check_shebang(file_path)

    if shebang:
        lang = get_shebang_language(shebang)

    return lang

#def basename_check(file_path):
#    """
#    Return a guessed type based on the basename 
#    """

#    return None

def extract_urls(text):
    """
    Find all URLs from a given string and return a list of them.

    """
    url_pattern = re.compile(r'https?://[^\s]+')
    urls = re.findall(url_pattern, text)
    return urls