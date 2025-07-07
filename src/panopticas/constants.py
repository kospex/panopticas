"""
Constants for Panopticas file type analysis.
"""

VERSION = "0.0.12"

EXT_FILETYPES = {
        '.c': 'C',
        '.cpp': 'C++',
        '.cs': 'C#',
        '.css': 'CSS',
        '.csv': 'CSV',
        '.dockerignore': 'Dockerignore',
        '.gitignore': 'Gitignore',
        '.gitattributes': 'GitAttributes',
        '.go': 'Go',
        '.gif': "GIF",
        '.gitleaksignore': "GitLeaksIgnore",
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
        '.lock': 'Lock',
        '.m': 'Objective-C',
        '.mailmap': 'Mailmap',
        '.md': 'Markdown',
        '.nvmrc': "nvmrc",
        '.php': 'PHP',
        '.pl': 'Perl',
        '.pm': 'Perl',
        '.png': 'PNG',
        '.py': 'Python',
        '.python-version': "python-version",
        '.r': 'R',
        '.rb': 'Ruby',
        '.rs': 'Rust',
        '.rst': 'ReStructuredText',
        '.sarif': 'SARIF', # Static Analysis Results Interchange Format
        # https://sarifweb.azurewebsites.net/
        '.scala': 'Scala',
        '.sh': 'Shell',
        '.sql': 'SQL',
        '.sqlfluff': 'SQLFluff',
        '.sqlfluffignore': 'SQLFluffIgnore',
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
        'cname': 'CNAME', # Often github et al will use a CNAME file for a URL to host from
    }

LANGUAGE_BY_BASENAME = {
    'go.mod': 'go.mod',
    'go.sum': 'go.sum',
}