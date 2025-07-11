"""
Analysis functions for Panopticas.
"""
import os
import re
import pathspec
from .constants import VERSION, EXT_FILETYPES, LANGUAGE_BY_BASENAME


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

    file_no_ext = os.path.splitext(filename)[0]

    tags = []

    if ext == ".pm":
        # Perl module
        # Languauge should already be set by the extension
        tags.append("module")

    if filename == "pyproject.toml":
        tags.append("build")
        tags.append("dependencies")
        tags.append("Python")

    # uv specific file, uv is from astral.sh
    if filename == "uv.lock":
        tags.append("dependencies")
        tags.append("Python")
        tags.append("uv")

    if filename == "yarn.lock":
        tags.append("dependencies")
        tags.append("JavaScript")
        tags.append("yarn")

    if ".github" in file_path:
        tags.append("Github")
        tags.append("Git")

    if filename == '.gitattributes':
        tags.append("Git")

    if filename == '.gitleaksignore':
        tags.append("GitLeaks")
        tags.append("Git")
        tags.append("ignore")

    if filename == "eslint.config.js":
        tags.extend(["JavaScript", "linter", "eslint", "config"])

    if filename == ".mailmap":
        tags.append("Git")

    if filename == '.python-version':
        tags.append("Python")
        tags.append("dependencies")

    if is_pip_requirements(filename):
        #if filename == "requirements.txt":
        tags.append("pip")
        tags.append("Python")
        tags.append("dependencies")

    if filename == '.sqlfluff':
        tags.append("SQLFluff")
        tags.append("SQL")
        tags.append("linter")

    if filename == ".mailmap":
        tags.append("Git")

    if filename == '.nvmrc':
        tags.append("Node")
        tags.append("dependencies")

    # Usually the filename will be uppercase CODEOWNERS for GitHub
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

    if filename == ".travis.yml":
            tags.append("pipeline")
            tags.append("TravisCI")

    if filename in ( "package.json", "package-lock.json"):
        tags.append("npm")
        tags.append("dependencies")

    if filename == "pom.xml":
        tags.append("maven")
        tags.append("build")
        tags.append("dependencies")

    if filename == "build.gradle":
        tags.append("gradle")
        tags.append("build")
        tags.append("dependencies")

    if file_no_ext == "license":
        tags.append("license")

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
    """
    Identify files in a directory.
    Returns a dict of the relative path filenams to their file_type
    """

    gitignore_spec = load_gitignore_patterns(directory)

    file_paths = {}

    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)

            relative_path = os.path.relpath(full_path, directory)
            if gitignore_spec and gitignore_spec.match_file(relative_path):
                continue

            ftype = get_language(full_path)

            if directory == ".":
                full_path = full_path.removeprefix("./")

            # TODO - see if we want to add a parameter to return the full path
            #file_paths[fulle_path] = ftype
            file_paths[relative_path] = ftype

    return file_paths

def find_files(directory,all_files=None):
    """
    Find all files in a directory, honoring the gitignore patterns.
    If all_files = True, then find everything.
    Returns a list of the relative path filenames
    """

    gitignore_spec = load_gitignore_patterns(directory)
    if all_files:
        gitignore_spec = None

    file_paths = []

    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)

            relative_path = os.path.relpath(full_path, directory)
            if gitignore_spec and gitignore_spec.match_file(relative_path):
                # Ignore and continue
                continue

            if directory == ".":
                full_path = full_path.removeprefix("./")

            file_paths.append(relative_path)

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

def get_language_edge_cases(file_path):
    """
    Handle edge cases where certain filenames are special file types
    Seems to be a go thing ...
    """
    basename = os.path.basename(file_path)

    if basename:
        return LANGUAGE_BY_BASENAME.get(basename.lower())
    else:
        return None

def get_language(file_path):
    """ Return the language of a file """
    ext = get_fileext(file_path)
    lang = None

    lang_by_basename = get_language_edge_cases(file_path)
    if lang_by_basename:
        return lang_by_basename

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
    Find all HTTP/S URLs from a given string and return a list of URLs found.

    """
    url_pattern = re.compile(r'https?://[^\s\"\'\'\)]+') 
    urls = re.findall(url_pattern, text)
    return urls

def extract_urls_from_file(file_path):
    """
    Extract URLs from a given file.

    Args:
        file_path (str): File to extract URLs from

    Returns:
        list: List of URLs found in the file

    Raises:
        FileNotFoundError: If the specified file does not exist
        UnicodeDecodeError: If the file cannot be decoded as UTF-8
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return extract_urls(content)
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Unable to decode file {file_path} as UTF-8: {str(e)}")

def is_pip_requirements(filename: str) -> bool:
    """
    Returns True if `filename` matches typical pip requirements filenames.
    Examples of matching filenames:
      - requirements.txt
      - requirements-dev.txt
      - requirements-dev.in
      - requirements.in
      - requirements.dev.txt
    """

    PATTERN = re.compile(r'^requirements([-._a-zA-Z0-9]*)\.(txt|in)$')

    return bool(PATTERN.match(filename))
