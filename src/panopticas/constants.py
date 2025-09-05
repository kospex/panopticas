"""
Constants for Panopticas file type analysis.
"""

VERSION = "0.0.11"

EXT_FILETYPES = {
        '.c': 'C',
        '.cpp': 'C++',
        '.cs': 'C#',
        '.css': 'CSS',
        '.csv': 'CSV',
        '.dockerignore': 'Dockerignore',
        '.exe': 'Executable',
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
        '.jar': 'Java Archive',
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
        '.ps1': 'PowerShell',
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
        '.zip': 'ZIP',
        # Special cases for files without extensions or .format files
        "codeowners": "CODEOWNERS",
        'dockerfile': 'Dockerfile',
        'makefile': 'Makefile',
        'cname': 'CNAME', # Often GitHub et al will use a CNAME file for a URL to host from
    }

LANGUAGE_BY_BASENAME = {
    'go.mod': 'go.mod',
    'go.sum': 'go.sum',
}

METADATA_RULES = {
    "extension_rules": {
        ".pm": ["module"],
        ".exe": ["binary"],
        ".jar": ["binary"],
        ".zip": ["binary"],
    },
    "exact_filename_rules": {
        "build.gradle": ["gradle", "build", "dependencies"],
        "claude.md": ["Claude", "AI", "Claude Code"],
        "codeowners": ["Git"],
        "gemini.md": ["Gemini", "AI", "Gemini CLI"],
        "pyproject.toml": ["build", "dependencies", "Python"],
        "uv.lock": ["dependencies", "Python", "uv"],
        "yarn.lock": ["dependencies", "JavaScript", "yarn"],
        ".gitattributes": ["Git"],
        ".gitleaksignore": ["GitLeaks", "Git", "ignore"],
        "eslint.config.js": ["JavaScript", "linter", "eslint", "config"],
        ".mailmap": ["Git"],
        ".python-version": ["Python", "dependencies"],
        ".sqlfluff": ["SQLFluff", "SQL", "linter"],
        ".nvmrc": ["Node", "dependencies"],
        ".gitignore": ["Git", "ignore"],
        "dockerfile": ["IaC", "Docker", "dependencies"],
        ".dockerignore": ["Docker", "ignore"],
        "makefile": ["build"],
        "go.mod": ["Go", "module", "dependencies"],
        "go.sum": ["Go", "dependencies", "checksum"],
        ".sqlfluffignore": ["SQLFluff", "ignore"],
        "codefresh.yml": ["pipeline", "Codefresh"],
        ".travis.yml": ["pipeline", "TravisCI"],
        "package.json": ["npm", "dependencies"],
        "package-lock.json": ["npm", "dependencies"],
        "pom.xml": ["maven", "build", "dependencies"],
    },
    "path_contains_rules": {
        ".github/workflows": ["workflow", "GitHub", "Git"],  # More specific paths first
        ".github": ["GitHub", "Git"],
    },
    "function_rules": [
        ("is_pip_requirements", ["pip", "Python", "PyPi", "dependencies"]),
    ]
}
