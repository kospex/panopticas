"""
Constants for Panopticas file type analysis.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("panopticas")
except PackageNotFoundError:
    VERSION = "unknown"

# Tags emitted directly by get_filename_metatypes() rather than by a rule
# table. "AI" prefixes every AI artifact's tags. "license" is matched on the
# basename-without-extension (LICENSE, license.md, license.txt) so it cannot
# be expressed as an exact_filename rule. get_tags() reads IMPLICIT_TAGS so
# these two are not restated anywhere.
AI_TAG = "AI"
LICENSE_TAG = "license"
IMPLICIT_TAGS = (AI_TAG, LICENSE_TAG)

EXT_FILETYPES = {
    ".c": "C",
    ".class": "Java Class",
    ".cpp": "C++",
    ".cs": "C#",
    ".cjs": "JavaScript",   # CommonJS module, explicit
    ".cts": "TypeScript",   # TypeScript emitting CommonJS
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
    ".json5": "JSON5",
    ".jsonc": "JSONC",      # JSON with comments
    ".jsx": "JSX",
    ".kt": "Kotlin",
    ".lock": "Lock",
    ".m": "Objective-C",
    ".mailmap": "Mailmap",
    ".md": "Markdown",
    ".mjs": "JavaScript",   # ES module, explicit
    ".mts": "TypeScript",   # TypeScript emitting an ES module
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
    # Linter, formatter and type checker config files. Where the tool
    # documents a single content format the extension maps to that format;
    # where several are accepted the file gets its own name. See LINTER_RULES.
    ".editorconfig": "INI",
    ".eslintignore": "ESLintIgnore",
    ".eslintrc": "ESLintRC",            # JSON, YAML or JS
    ".flake8": "INI",
    ".globalconfig": "INI",
    ".jshintignore": "JSHintIgnore",
    ".jshintrc": "JSON",
    ".prettierignore": "PrettierIgnore",
    ".prettierrc": "Prettierrc",        # JSON or YAML
    ".pylintrc": "INI",
    ".ruleset": "XML",
    ".rufo": "Ruby",                    # evaluated as Ruby by the formatter
    ".stylelintignore": "StylelintIgnore",
    ".stylelintrc": "StylelintRC",      # JSON or YAML
    ".yapf": "INI",                     # .style.yapf
    ".yapfignore": "YapfIgnore",
    # Special cases for files without extensions or .format files
    "codeowners": "CODEOWNERS",
    "dockerfile": "Dockerfile",
    "license": "Text",
    "makefile": "Makefile",
    "pylintrc": "INI",
    "steepfile": "Ruby",
    "cname": "CNAME",  # Often GitHub et al will use a CNAME file for a URL to host from
}

LANGUAGE_BY_BASENAME = {
    "go.mod": "go.mod",
    "go.sum": "go.sum",
    # setup.cfg is INI (it is read by configparser). Mapped by basename rather
    # than adding ".cfg" to EXT_FILETYPES — that extension is used for arbitrary
    # formats elsewhere, so a blanket ".cfg" -> INI rule would over-claim.
    "setup.cfg": "INI",
    # ".cfg" and ".conf" are used for arbitrary formats elsewhere, so these
    # are mapped by basename for the same reason setup.cfg is.
    ".isort.cfg": "INI",
    "staticcheck.conf": "TOML",
}

# Classification of every value in EXT_FILETYPES and LANGUAGE_BY_BASENAME as
# a language or not. get_languages() returns the first set.
#
# The principle: a language expresses behaviour or presentation. Excluded are
# data and prose formats, binaries, named single-purpose files that are a
# filename convention rather than a format, and framework artifacts whose
# actual language is something else (the code in a .aspx file is C# or
# Visual Basic).
#
# Both sets are required, and a test asserts they cover every value exactly
# once. An exclusion list alone would silently classify a newly added file
# type as a language.
#
# This deliberately diverges from GitHub Linguist on three values, which is
# the closest available benchmark. GitHub's language bar counts only
# Linguist's `programming` and `markup` types, so its `data` and `prose`
# languages (JSON, YAML, Markdown, reStructuredText) are excluded there too.
# See changes/design/specs/2026-08-10-tag-vocabulary-and-cli-refactor-design.md
LANGUAGE_FILETYPES = frozenset({
    "C",
    "C Header",
    "C#",
    "C++",
    "CSS",
    "Dockerfile",
    "Go",
    "Groovy",
    "Groovy Server Pages",
    "HTML",
    "Java",
    "JavaScript",
    "JSX",
    "Jupyter Notebook",
    "Kotlin",
    "Makefile",
    "Objective-C",
    "Perl",
    "PHP",
    "PowerShell",
    "Python",
    "R",
    "Ruby",
    "Rust",
    "Scala",
    "Shell",
    "SQL",  # Linguist types SQL as `data`; excluding it would read as a bug.
    "Swift",
    "Terraform",
    "TSX",
    "TypeScript",
    "Vue",
})

NON_LANGUAGE_FILETYPES = frozenset({
    # Binary and media formats
    "DLL",
    "Excel",
    "Executable",
    "GIF",
    "ICO",
    "JPEG",
    "Java Archive",
    "Java Class",
    "PDF",
    "PNG",
    "ZIP",
    # Data and config formats — carry data, not behaviour
    "CSV",
    "INI",
    "JSON",
    "JSON5",
    "JSONC",
    "Properties",
    "TOML",
    "TSV",
    "XML",
    "YAML",
    # Prose formats
    "Markdown",
    "ReStructuredText",
    "Text",
    # Named single-purpose files — a filename convention, not a format
    "CNAME",
    "CODEOWNERS",
    "Dockerignore",
    "GitAttributes",
    "Gitignore",
    "GitLeaksIgnore",
    "ESLintIgnore",
    "ESLintRC",
    "JSHintIgnore",
    "PrettierIgnore",
    "Prettierrc",
    "StylelintIgnore",
    "StylelintRC",
    "YapfIgnore",
    "Lock",
    "Mailmap",
    "nvmrc",
    "python-version",
    "go.mod",
    "go.sum",
    "SQLFluff",
    "SQLFluffIgnore",
    # Framework and tool artifacts — the real language is something else
    "ASP.NET",
    "ASP.NET Global",
    "ASP.NET User Control",
    "Apache JMeter",
    "C# Project",
    "SARIF",
    "SVG",
    "Visual Studio Solution",
})

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
        ".nvmrc": ["Node", "dependencies"],
        ".gitignore": ["Git", "ignore"],
        "dockerfile": ["IaC", "Docker", "dependencies"],
        ".dockerignore": ["Docker", "ignore"],
        "makefile": ["build"],
        "go.mod": ["Go", "module", "dependencies"],
        "go.sum": ["Go", "dependencies", "checksum"],
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

# The roles a code-quality tool can play. A LINTER_RULES entry may not use a
# role outside this set.
LINTER_ROLES = frozenset({
    "linter",       # reports violations
    "formatter",    # rewrites code to a canonical form
    "typechecker",  # checks static types
})

LINTER_RULES = {
    # --- JavaScript / TypeScript ---------------------------------------
    "ESLint": {
        "languages": ["JavaScript", "TypeScript"],
        "roles": ["linter"],
        "config": [
            # Flat config, the current format.
            "eslint.config.js", "eslint.config.mjs", "eslint.config.cjs",
            "eslint.config.ts", "eslint.config.mts", "eslint.config.cts",
            # eslintrc, removed in v9 but still present in many repositories.
            ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.yaml",
            ".eslintrc.yml", ".eslintrc.json",
        ],
        "ignore": [".eslintignore"],
    },
    "Prettier": {
        # Prettier formats far more than these three, but tagging every
        # parser it ships would put seven languages on one config file.
        "languages": ["JavaScript", "TypeScript", "CSS"],
        "roles": ["formatter"],
        "config": [
            ".prettierrc", ".prettierrc.json", ".prettierrc.yml",
            ".prettierrc.yaml", ".prettierrc.json5", ".prettierrc.js",
            ".prettierrc.mjs", ".prettierrc.cjs", ".prettierrc.ts",
            ".prettierrc.mts", ".prettierrc.cts", ".prettierrc.toml",
            "prettier.config.js", "prettier.config.mjs",
            "prettier.config.cjs", "prettier.config.ts",
            "prettier.config.mts", "prettier.config.cts",
        ],
        "ignore": [".prettierignore"],
    },
    "Stylelint": {
        "languages": ["CSS"],
        "roles": ["linter"],
        "config": [
            "stylelint.config.js", "stylelint.config.mjs",
            "stylelint.config.cjs", "stylelint.config.ts",
            ".stylelintrc", ".stylelintrc.js", ".stylelintrc.mjs",
            ".stylelintrc.cjs", ".stylelintrc.yml", ".stylelintrc.yaml",
            ".stylelintrc.json",
        ],
        "ignore": [".stylelintignore"],
    },
    "Biome": {
        "languages": ["JavaScript", "TypeScript", "CSS"],
        "roles": ["linter", "formatter"],
        "config": ["biome.json", "biome.jsonc", ".biome.json", ".biome.jsonc"],
    },
    "oxlint": {
        "languages": ["JavaScript", "TypeScript"],
        "roles": ["linter"],
        "config": [".oxlintrc.json", ".oxlintrc.jsonc", "oxlint.config.ts",
                   "oxlint.config.mts"],
    },
    "JSHint": {
        "languages": ["JavaScript"],
        "roles": ["linter"],
        "config": [".jshintrc"],
        "ignore": [".jshintignore"],
    },
    # tsc is a compiler, but tsconfig.json is where a project's type checking
    # is configured (strict, noImplicitAny). jsconfig.json is the same file
    # applied to a JavaScript project.
    "TypeScript": {
        "languages": ["TypeScript", "JavaScript"],
        "roles": ["typechecker"],
        "config": ["tsconfig.json", "jsconfig.json"],
    },
    # Language-neutral by design, so it carries no language tag.
    "EditorConfig": {
        "languages": [],
        "roles": ["formatter"],
        "config": [".editorconfig"],
    },
    # --- Python ---------------------------------------------------------
    "Ruff": {
        "languages": ["Python"],
        "roles": ["linter", "formatter"],
        "config": ["ruff.toml", ".ruff.toml"],
    },
    "Flake8": {
        "languages": ["Python"],
        "roles": ["linter"],
        "config": [".flake8"],
    },
    "Pylint": {
        "languages": ["Python"],
        "roles": ["linter"],
        "config": ["pylintrc", ".pylintrc", "pylintrc.toml", ".pylintrc.toml"],
    },
    "mypy": {
        "languages": ["Python"],
        "roles": ["typechecker"],
        "config": ["mypy.ini", ".mypy.ini"],
    },
    "Pyright": {
        "languages": ["Python"],
        "roles": ["typechecker"],
        "config": ["pyrightconfig.json"],
    },
    "isort": {
        "languages": ["Python"],
        "roles": ["formatter"],
        "config": [".isort.cfg"],
    },
    "yapf": {
        "languages": ["Python"],
        "roles": ["formatter"],
        "config": [".style.yapf"],
        "ignore": [".yapfignore"],
    },
    "Prospector": {
        "languages": ["Python"],
        "roles": ["linter"],
        "config": [".prospector.yaml", ".prospector.yml"],
    },
    # --- Go -------------------------------------------------------------
    "golangci-lint": {
        "languages": ["Go"],
        "roles": ["linter"],
        "config": [".golangci.yml", ".golangci.yaml", ".golangci.toml",
                   ".golangci.json"],
    },
    "staticcheck": {
        "languages": ["Go"],
        "roles": ["linter"],
        "config": ["staticcheck.conf"],
    },
    # --- Ruby -----------------------------------------------------------
    "RuboCop": {
        "languages": ["Ruby"],
        "roles": ["linter", "formatter"],
        "config": [".rubocop.yml"],
        # Written by --auto-gen-config to exclude existing offences, so it is
        # the exclusion file rather than a second config.
        "ignore": [".rubocop_todo.yml"],
    },
    "Standard": {
        "languages": ["Ruby"],
        "roles": ["linter", "formatter"],
        "config": [".standard.yml"],
        "ignore": [".standard_todo.yml"],
    },
    "Reek": {
        "languages": ["Ruby"],
        "roles": ["linter"],
        "config": [".reek.yml"],
    },
    "Rufo": {
        "languages": ["Ruby"],
        "roles": ["formatter"],
        "config": [".rufo"],
    },
    "erb_lint": {
        "languages": ["Ruby"],
        "roles": ["linter"],
        "config": [".erb_lint.yml"],
    },
    "Steep": {
        "languages": ["Ruby"],
        "roles": ["typechecker"],
        "config": ["steepfile"],
    },
    "Sorbet": {
        "languages": ["Ruby"],
        "roles": ["typechecker"],
        # sorbet/config plus the generated sorbet/rbi tree.
        "path_contains": ["sorbet/"],
    },
    # --- Java -----------------------------------------------------------
    # Checkstyle itself documents no fixed filename; google_checks.xml and
    # sun_checks.xml ship with the distribution and config/checkstyle/ is the
    # Gradle plugin's documented default. PMD and SpotBugs are deliberately
    # absent — their ruleset and filter files are arbitrarily named.
    "Checkstyle": {
        "languages": ["Java"],
        "roles": ["linter"],
        "config": ["checkstyle.xml", "google_checks.xml", "sun_checks.xml"],
        "path_contains": ["config/checkstyle/"],
    },
    # --- Groovy ---------------------------------------------------------
    "npm-groovy-lint": {
        "languages": ["Groovy"],
        "roles": ["linter"],
        "config": [".groovylintrc.json", ".groovylintrc.js",
                   ".groovylintrc.yml"],
    },
    # --- C# / .NET ------------------------------------------------------
    "Roslyn": {
        "languages": ["C#", ".NET"],
        "roles": ["linter"],
        "config": [".globalconfig"],
        # Legacy Code Analysis rule sets, deprecated for .globalconfig but
        # still common in older solutions.
        "extensions": [".ruleset"],
    },
    "StyleCop": {
        "languages": ["C#", ".NET"],
        "roles": ["linter"],
        "config": ["stylecop.json", ".stylecop.json"],
    },
    # --- SQL ------------------------------------------------------------
    "SQLFluff": {
        "languages": ["SQL"],
        "roles": ["linter", "formatter"],
        "config": [".sqlfluff"],
        "ignore": [".sqlfluffignore"],
    },
}


def _expand_linter_rules():
    """Expand LINTER_RULES into the METADATA_RULES tables."""
    for tool, spec in LINTER_RULES.items():
        base = list(spec.get("languages", [])) + list(spec["roles"]) + [tool]
        for filename in spec.get("config", ()):
            METADATA_RULES["exact_filename_rules"][filename] = base + ["config"]
        for filename in spec.get("ignore", ()):
            METADATA_RULES["exact_filename_rules"][filename] = base + ["ignore"]
        for fragment in spec.get("path_contains", ()):
            METADATA_RULES["path_contains_rules"][fragment] = base + ["config"]
        for ext in spec.get("extensions", ()):
            METADATA_RULES["extension_rules"][ext] = base + ["config"]


_expand_linter_rules()

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
