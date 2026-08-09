"""
Constants for Panopticas file type analysis.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("panopticas")
except PackageNotFoundError:
    VERSION = "unknown"

EXT_FILETYPES = {
    ".c": "C",
    ".class": "Java Class",
    ".cpp": "C++",
    ".cs": "C#",
    ".csproj": "C# Project",
    ".css": "CSS",
    ".csv": "CSV",
    ".dockerignore": "Dockerignore",
    ".dll": "DLL",
    ".exe": "Executable",
    ".gitignore": "Gitignore",
    ".gitattributes": "GitAttributes",
    ".go": "Go",
    ".gif": "GIF",
    ".global.asax": "ASP.NET Global",
    ".gitleaksignore": "GitLeaksIgnore",
    ".gvy": "Groovy",  # Less common for Groovy
    ".groovy": "Groovy",
    ".gsp": "Groovy Server Pages",
    ".h": "C Header",
    ".aspx": "ASP.NET",
    ".ascx": "ASP.NET User Control",
    ".htm": "HTML",
    ".html": "HTML",
    ".ico": "ICO",
    ".ini": "INI",
    ".ipynb": "Jupyter Notebook",
    ".java": "Java",
    ".jar": "Java Archive",
    ".jmx": "Apache JMeter",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".js": "JavaScript",
    ".json": "JSON",
    ".jsx": "JSX",
    ".kt": "Kotlin",
    ".lock": "Lock",
    ".m": "Objective-C",
    ".mailmap": "Mailmap",
    ".md": "Markdown",
    ".nvmrc": "nvmrc",
    ".pdf": "PDF",
    ".php": "PHP",
    ".pl": "Perl",
    ".pm": "Perl",
    ".png": "PNG",
    ".properties": "Properties",
    ".ps1": "PowerShell",
    ".py": "Python",
    ".python-version": "python-version",
    ".r": "R",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".rst": "ReStructuredText",
    ".sarif": "SARIF",  # Static Analysis Results Interchange Format
    # https://sarifweb.azurewebsites.net/
    ".scala": "Scala",
    ".sh": "Shell",
    ".sln": "Visual Studio Solution",
    ".sql": "SQL",
    ".sqlfluff": "SQLFluff",
    ".sqlfluffignore": "SQLFluffIgnore",
    ".svg": "SVG",
    ".swift": "Swift",
    ".tf": "Terraform",
    ".toml": "TOML",
    ".ts": "TypeScript",
    ".tsv": "TSV",
    ".tsx": "TSX",
    ".txt": "Text",
    ".vue": "Vue",
    ".xml": "XML",
    ".xls": "Excel",
    ".xlsx": "Excel",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".zip": "ZIP",
    # Special cases for files without extensions or .format files
    "codeowners": "CODEOWNERS",
    "dockerfile": "Dockerfile",
    "license": "Text",
    "makefile": "Makefile",
    "cname": "CNAME",  # Often GitHub et al will use a CNAME file for a URL to host from
}

LANGUAGE_BY_BASENAME = {
    "go.mod": "go.mod",
    "go.sum": "go.sum",
    # setup.cfg is INI (it is read by configparser). Mapped by basename rather
    # than adding ".cfg" to EXT_FILETYPES — that extension is used for arbitrary
    # formats elsewhere, so a blanket ".cfg" -> INI rule would over-claim.
    "setup.cfg": "INI",
}

METADATA_RULES = {
    "extension_rules": {
        ".pm": ["module"],
        ".exe": ["binary"],
        ".gif": ["binary", "image"],
        ".jar": ["binary"],
        ".jpg": ["binary", "image"],
        ".jpeg": ["binary", "image"],
        ".zip": ["binary"],
        ".class": ["binary", "Java"],
        ".pdf": ["binary"],
        ".xls": ["binary", "Microsoft"],
        ".xlsx": ["binary", "Microsoft"],
        ".jmx": ["Apache", "JMeter", "XML"],
        ".dll": ["binary", ".NET"],
        ".sln": [".NET", "Visual Studio", "build"],
        ".csproj": [".NET", "C#", "build", "dependencies"],
        ".ascx": [".NET", "ASP.NET"],
        ".aspx": [".NET", "ASP.NET"],
    },
    "exact_filename_rules": {
        "azure-pipelines.yml": ["pipeline", "Azure DevOps"],
        "bitbucket-pipelines.yml": ["pipeline", "Bitbucket"],
        "build.gradle": ["gradle", "build", "dependencies"],
        "dependabot.yml": ["Dependabot", "GitHub", "dependencies", "security"],
        "dependabot.yaml": ["Dependabot", "GitHub", "dependencies", "security"],
        "global.asax": [".NET", "ASP.NET"],
        "packages.config": [".NET", "NuGet", "dependencies"],
        "nuget.config": [".NET", "NuGet", "config"],
        "web.config": [".NET", "ASP.NET", "config"],
        "app.config": [".NET", "config"],
        "codeowners": ["Git"],
        "eslint.config.js": ["JavaScript", "linter", "eslint", "config"],
        "pyproject.toml": ["build", "dependencies", "Python"],
        # setup.py / setup.cfg are setuptools-specific, so they carry the
        # backend tag. pyproject.toml does not: its build-backend is declared
        # inside the file and cannot be known from the path.
        "setup.py": ["build", "dependencies", "Python", "setuptools"],
        "setup.cfg": ["build", "dependencies", "Python", "setuptools"],
        "uv.lock": ["dependencies", "Python", "uv"],
        "yarn.lock": ["dependencies", "JavaScript", "yarn", "npm"],
        "pnpm-lock.yaml": ["dependencies", "JavaScript", "pnpm", "npm"],
        ".gitattributes": ["Git"],
        ".gitlab-ci.yml": ["pipeline", "GitLab"],  # Three letter YAML extension
        ".gitlab-ci.yaml": ["pipeline", "GitLab"],  # Full four letter YAML extension
        ".gitleaksignore": ["GitLeaks", "Git", "ignore"],
        "jenkinsfile": ["pipeline", "Jenkins"],
        "jenkinsfile.groovy": ["pipeline", "Jenkins"],
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
        # Order of precendence is important, as the search will return most likely the first
        # More specific rules first
        ".github/workflows": [
            "workflow",
            "pipeline",
            "GitHub",
            "Git",
        ],  # More specific paths first
        ".buildkite/": ["pipeline", "Buildkite"],
        ".circleci/": ["pipeline", "CircleCI"],
        ".github": ["GitHub", "Git"],
    },
    "function_rules": [
        ("is_pip_requirements", ["pip", "Python", "PyPi", "dependencies"]),
    ],
}

# The complete set of legal `kind` values for an AI artifact.
# A rule may not use a kind outside this set.
AI_ARTIFACT_KINDS = {
    "instructions",  # natural-language guidance for an agent
    "config",        # tool configuration
    "rules",         # rule/policy files
    "prompt",        # reusable prompt
    "chatmode",      # chat mode definition
    "command",       # slash command definition
    "agent",         # subagent definition
    "skill",         # skill definition
    "hook",          # lifecycle hook
    "plugin",        # plugin bundle
    "ignore",        # exclusion file
    "history",       # session/chat transcript
    "docs",          # LLM-oriented documentation
    "directory",     # bare AI directory (find_ai_files(all_files=True) only)
}

# AI coding agent artifacts, mapping an indicator to (product, kind).
#
# Products are brand-level: "Claude" covers both Claude Code and Claude
# Desktop, so a single tag finds all Anthropic tooling. Files owned by no
# brand use a pseudo-product ("Agents", "MCP", "llms.txt").
#
# Precedence when resolving a path: exact_filename, then the longest
# matching path_contains fragment, then the longest matching
# filename_suffix. See core.get_ai_metadata().
AI_RULES = {
    # Matched against the lowercased basename.
    "exact_filename": {
        # Claude — Anthropic
        "claude.md": ("Claude", "instructions"),
        "claude.local.md": ("Claude", "instructions"),
        "claude_desktop_config.json": ("Claude", "config"),
        # Copilot — GitHub
        "copilot-instructions.md": ("Copilot", "instructions"),
        # Cursor — Anysphere
        ".cursorrules": ("Cursor", "rules"),
        ".cursorignore": ("Cursor", "ignore"),
        ".cursorindexingignore": ("Cursor", "ignore"),
        # Gemini — Google. .aiexclude is Gemini Code Assist, .geminiignore
        # is Gemini CLI; both are current, neither replaced the other.
        "gemini.md": ("Gemini", "instructions"),
        ".aiexclude": ("Gemini", "ignore"),
        ".geminiignore": ("Gemini", "ignore"),
        # Windsurf — Codeium, now Devin (Cognition). The single-file rules
        # and the Codeium-era ignore file are legacy but still read.
        ".windsurfrules": ("Windsurf", "rules"),
        ".codeiumignore": ("Windsurf", "ignore"),
        # Aider
        ".aider.conf.yml": ("Aider", "config"),
        ".aiderignore": ("Aider", "ignore"),
        ".aider.chat.history.md": ("Aider", "history"),
        ".aider.input.history": ("Aider", "history"),
        # Roo Code — fallback when .roo/rules/ is absent or empty.
        ".roorules": ("Roo Code", "rules"),
        # Continue — workspace-level configuration.
        ".continuerc.json": ("Continue", "config"),
        # Goose — Block
        ".goosehints": ("Goose", "instructions"),
        # Augment
        ".augment-guidelines": ("Augment", "instructions"),
        # Vendor-neutral
        "agents.md": ("Agents", "instructions"),
        ".aiignore": ("Agents", "ignore"),
        ".mcp.json": ("MCP", "config"),
        "llms.txt": ("llms.txt", "docs"),
        "llms-full.txt": ("llms.txt", "docs"),
    },
    # Matched as a substring of the lowercased path. Longest match wins,
    # so more specific fragments may be listed in any order.
    "path_contains": {
        # Claude
        ".claude/skills/": ("Claude", "skill"),
        ".claude/agents/": ("Claude", "agent"),
        ".claude/commands/": ("Claude", "command"),
        ".claude/hooks/": ("Claude", "hook"),
        ".claude/plugins/": ("Claude", "plugin"),
        ".claude/": ("Claude", "config"),
        # Copilot
        ".github/instructions/": ("Copilot", "instructions"),
        ".github/prompts/": ("Copilot", "prompt"),
        ".github/chatmodes/": ("Copilot", "chatmode"),
        # Cursor
        ".cursor/rules/": ("Cursor", "rules"),
        ".cursor/": ("Cursor", "config"),
        # Gemini
        ".gemini/": ("Gemini", "config"),
        # Codex — OpenAI
        ".codex/": ("Codex", "config"),
        # Windsurf. .devin/rules/ is now the preferred location upstream,
        # but is left out here: it would mean a new "Devin" product.
        ".windsurf/rules/": ("Windsurf", "rules"),
        ".windsurf/": ("Windsurf", "config"),
        # Cline. Only the directory form is documented; a bare .clinerules
        # file is deliberately not matched (unconfirmed).
        ".clinerules/": ("Cline", "rules"),
        # Roo Code
        ".roo/rules/": ("Roo Code", "rules"),
        ".roo/": ("Roo Code", "config"),
        # Continue
        ".continue/": ("Continue", "config"),
        # Amazon Q — AWS
        ".amazonq/rules/": ("Amazon Q", "rules"),
        ".amazonq/": ("Amazon Q", "config"),
        # Junie — JetBrains. Current guidelines live at .junie/AGENTS.md,
        # which the vendor-neutral agents.md rule claims first by design.
        ".junie/": ("Junie", "config"),
        # Augment
        ".augment/rules/": ("Augment", "rules"),
        ".augment/": ("Augment", "config"),
        # OpenHands — All Hands AI. Microagents are now called skills and
        # new ones belong in the cross-vendor .agents/skills/, but these
        # directories remain supported.
        ".openhands/microagents/": ("OpenHands", "skill"),
        ".openhands/": ("OpenHands", "config"),
        # Kilo Code, since rebranded to Kilo. Superseded by .kilo/rules/
        # plus kilo.jsonc, but kept working for backward compatibility.
        ".kilocode/rules/": ("Kilo Code", "rules"),
        ".kilocode/": ("Kilo Code", "config"),
        # Trae — ByteDance
        ".trae/rules/": ("Trae", "rules"),
        ".trae/": ("Trae", "config"),
        # Vendor-neutral
        ".vscode/mcp.json": ("MCP", "config"),
    },
    # Matched against the end of the lowercased basename. Longest wins.
    "filename_suffix": {
        ".instructions.md": ("Copilot", "instructions"),
        ".prompt.md": ("Copilot", "prompt"),
        ".chatmode.md": ("Copilot", "chatmode"),
        ".mdc": ("Cursor", "rules"),
    },
}
