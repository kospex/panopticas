"""
Panopticas - File type analysis and metadata extraction.
"""

from .constants import VERSION
from .core import (
    get_fileext,
    get_extension_filetype,
    get_filename_metatypes,
    check_shebang,
    get_shebang_language,
    count_lines,
    load_gitignore_patterns,
    identify_files,
    identify_files_with_metrics,
    find_files,
    extract_shebang_language,
    get_language_edge_cases,
    get_language,
    extract_urls,
    extract_urls_from_file,
    is_pip_requirements,
)

__version__ = VERSION
__all__ = [
    'VERSION',
    'get_fileext',
    'get_extension_filetype', 
    'get_filename_metatypes',
    'check_shebang',
    'get_shebang_language',
    'count_lines',
    'load_gitignore_patterns',
    'identify_files',
    'identify_files_with_metrics',
    'find_files',
    'extract_shebang_language',
    'get_language_edge_cases',
    'get_language',
    'extract_urls',
    'extract_urls_from_file',
    'is_pip_requirements',
]