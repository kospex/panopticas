"""
Tests for panopticas core functionality.

Covers: file extension detection, language identification, metadata extraction,
shebang parsing, URL extraction, pip requirements matching, and file counting.
"""

import os
import tempfile

import pytest

from panopticas import (
    get_fileext,
    get_extension_filetype,
    get_filename_metatypes,
    get_language,
    get_language_edge_cases,
    extract_shebang_language,
    check_shebang,
    extract_urls,
    extract_urls_from_file,
    is_pip_requirements,
    count_lines,
    identify_files,
    identify_files_with_metrics,
    find_files,
)
from panopticas.constants import EXT_FILETYPES, METADATA_RULES

# Path to test fixture files
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "tests")


class TestGetFileext:
    """Tests for get_fileext() — extracting file extensions."""

    def test_python_file(self):
        assert get_fileext("example.py") == ".py"

    def test_javascript_file(self):
        assert get_fileext("app.js") == ".js"

    def test_nested_path(self):
        assert get_fileext("src/main/App.java") == ".java"

    def test_dotfile(self):
        assert get_fileext(".gitignore") == ".gitignore"

    def test_no_extension(self):
        """Files without extensions return the basename."""
        assert get_fileext("Makefile") == "Makefile"

    def test_double_extension(self):
        """Returns the last extension only."""
        assert get_fileext("archive.tar.gz") == ".gz"


class TestGetExtensionFiletype:
    """Tests for get_extension_filetype() — mapping extensions to languages."""

    def test_python(self):
        assert get_extension_filetype(".py") == "Python"

    def test_javascript(self):
        assert get_extension_filetype(".js") == "JavaScript"

    def test_java(self):
        assert get_extension_filetype(".java") == "Java"

    def test_go(self):
        assert get_extension_filetype(".go") == "Go"

    def test_rust(self):
        assert get_extension_filetype(".rs") == "Rust"

    def test_typescript(self):
        assert get_extension_filetype(".ts") == "TypeScript"

    def test_kotlin(self):
        assert get_extension_filetype(".kt") == "Kotlin"

    def test_ruby(self):
        assert get_extension_filetype(".rb") == "Ruby"

    def test_shell(self):
        assert get_extension_filetype(".sh") == "Shell"

    def test_case_insensitive(self):
        assert get_extension_filetype(".PY") == "Python"
        assert get_extension_filetype(".Js") == "JavaScript"

    def test_unknown_extension(self):
        assert get_extension_filetype(".xyz123") is None

    def test_none_input(self):
        assert get_extension_filetype(None) is None

    def test_empty_string(self):
        assert get_extension_filetype("") is None

    # Data formats
    def test_json(self):
        assert get_extension_filetype(".json") == "JSON"

    def test_yaml(self):
        assert get_extension_filetype(".yaml") == "YAML"
        assert get_extension_filetype(".yml") == "YAML"

    def test_csv(self):
        assert get_extension_filetype(".csv") == "CSV"

    def test_xml(self):
        assert get_extension_filetype(".xml") == "XML"

    # Binary types
    def test_pdf(self):
        assert get_extension_filetype(".pdf") == "PDF"

    def test_gif(self):
        assert get_extension_filetype(".gif") == "GIF"

    def test_png(self):
        assert get_extension_filetype(".png") == "PNG"

    def test_jpeg(self):
        assert get_extension_filetype(".jpg") == "JPEG"
        assert get_extension_filetype(".jpeg") == "JPEG"

    def test_excel(self):
        assert get_extension_filetype(".xls") == "Excel"
        assert get_extension_filetype(".xlsx") == "Excel"

    def test_zip(self):
        assert get_extension_filetype(".zip") == "ZIP"

    def test_jar(self):
        assert get_extension_filetype(".jar") == "Java Archive"

    def test_executable(self):
        assert get_extension_filetype(".exe") == "Executable"

    # Groovy
    def test_groovy(self):
        assert get_extension_filetype(".groovy") == "Groovy"
        assert get_extension_filetype(".gvy") == "Groovy"

    # Infrastructure
    def test_terraform(self):
        assert get_extension_filetype(".tf") == "Terraform"

    def test_dockerfile(self):
        assert get_extension_filetype("dockerfile") == "Dockerfile"

    def test_properties(self):
        assert get_extension_filetype(".properties") == "Properties"

    def test_toml(self):
        assert get_extension_filetype(".toml") == "TOML"

    # .NET types (#10)
    def test_csharp_project(self):
        assert get_extension_filetype(".csproj") == "C# Project"

    def test_dll(self):
        assert get_extension_filetype(".dll") == "DLL"

    def test_aspx(self):
        assert get_extension_filetype(".aspx") == "ASP.NET"

    def test_ascx(self):
        assert get_extension_filetype(".ascx") == "ASP.NET User Control"

    def test_sln(self):
        assert get_extension_filetype(".sln") == "Visual Studio Solution"


class TestGetLanguage:
    """Tests for get_language() — full language detection pipeline."""

    def test_python_file(self):
        assert get_language("example.py") == "Python"

    def test_unknown_extension(self):
        assert get_language("file.xyz123") == "Unknown"

    def test_makefile(self):
        assert get_language("Makefile") == "Makefile"

    def test_dockerfile(self):
        assert get_language("Dockerfile") == "Dockerfile"

    def test_skip_shebang(self):
        """With skip_shebang, doesn't try to read the file."""
        result = get_language("nonexistent_file.xyz", skip_shebang=True)
        assert result == "Unknown"


class TestGetLanguageEdgeCases:
    """Tests for get_language_edge_cases() — basename-based detection."""

    def test_go_mod(self):
        assert get_language_edge_cases("go.mod") == "go.mod"

    def test_go_sum(self):
        assert get_language_edge_cases("go.sum") == "go.sum"

    def test_go_mod_in_path(self):
        assert get_language_edge_cases("/some/path/go.mod") == "go.mod"

    def test_regular_file(self):
        assert get_language_edge_cases("main.go") is None

    def test_setup_cfg(self):
        assert get_language_edge_cases("setup.cfg") == "INI"

    def test_setup_cfg_in_path(self):
        assert get_language_edge_cases("packages/foo/setup.cfg") == "INI"

    def test_other_cfg_files_are_not_claimed(self):
        """Only setup.cfg is known to be INI — .cfg generally is not."""
        assert get_language_edge_cases("tox.cfg") is None
        assert get_language_edge_cases("app.cfg") is None


class TestExtractShebangLanguage:
    """Tests for extract_shebang_language() — parsing shebang lines."""

    def test_env_python3(self):
        assert extract_shebang_language("#!/usr/bin/env python3") == "Python"

    def test_env_python(self):
        assert extract_shebang_language("#!/usr/bin/env python") == "Python"

    def test_direct_bash(self):
        assert extract_shebang_language("#!/bin/bash") == "bash"

    def test_direct_sh(self):
        assert extract_shebang_language("#!/bin/sh") == "sh"

    def test_usr_local_perl(self):
        assert extract_shebang_language("#!/usr/local/bin/perl") == "perl"

    def test_env_node(self):
        assert extract_shebang_language("#!/usr/bin/env node") == "node"

    def test_env_ruby(self):
        assert extract_shebang_language("#!/usr/bin/env ruby") == "ruby"


class TestCheckShebang:
    """Tests for check_shebang() — reading shebang from files."""

    def test_file_not_found(self):
        assert check_shebang("/nonexistent/path/file.sh") is None

    def test_file_with_shebang(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write("#!/bin/bash\necho hello\n")
            f.flush()
            result = check_shebang(f.name)
            assert result == "#!/bin/bash"
            os.unlink(f.name)

    def test_file_without_shebang(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("just a regular file\n")
            f.flush()
            result = check_shebang(f.name)
            assert result is None
            os.unlink(f.name)


class TestGetFilenameMetatypes:
    """Tests for get_filename_metatypes() — metadata tag extraction."""

    def test_pyproject_toml(self):
        tags = get_filename_metatypes("pyproject.toml")
        assert "build" in tags
        assert "dependencies" in tags
        assert "Python" in tags

    def test_setup_py(self):
        tags = get_filename_metatypes("setup.py")
        assert "build" in tags
        assert "dependencies" in tags
        assert "Python" in tags
        assert "setuptools" in tags

    def test_setup_cfg(self):
        tags = get_filename_metatypes("setup.cfg")
        assert "build" in tags
        assert "dependencies" in tags
        assert "Python" in tags
        assert "setuptools" in tags

    def test_setup_py_in_subdirectory(self):
        tags = get_filename_metatypes("packages/foo/setup.py")
        assert "dependencies" in tags
        assert "setuptools" in tags

    def test_package_json(self):
        tags = get_filename_metatypes("package.json")
        assert "npm" in tags
        assert "dependencies" in tags

    def test_pnpm_lock_yaml(self):
        tags = get_filename_metatypes("pnpm-lock.yaml")
        assert "dependencies" in tags
        assert "JavaScript" in tags
        assert "pnpm" in tags

    def test_dockerfile(self):
        tags = get_filename_metatypes("Dockerfile")
        assert "Docker" in tags
        assert "dependencies" in tags

    def test_github_workflow(self):
        tags = get_filename_metatypes(".github/workflows/ci.yml")
        assert "pipeline" in tags
        assert "GitHub" in tags

    def test_gitlab_ci(self):
        tags = get_filename_metatypes(".gitlab-ci.yml")
        assert "pipeline" in tags
        assert "GitLab" in tags

    def test_jenkins(self):
        tags = get_filename_metatypes("Jenkinsfile")
        assert "pipeline" in tags
        assert "Jenkins" in tags

    def test_requirements_txt(self):
        tags = get_filename_metatypes("requirements.txt")
        assert "pip" in tags
        assert "dependencies" in tags
        assert "Python" in tags

    def test_requirements_dev_txt(self):
        tags = get_filename_metatypes("requirements-dev.txt")
        assert "pip" in tags
        assert "dependencies" in tags

    def test_go_mod(self):
        tags = get_filename_metatypes("go.mod")
        assert "Go" in tags
        assert "dependencies" in tags

    def test_pom_xml(self):
        tags = get_filename_metatypes("pom.xml")
        assert "maven" in tags
        assert "dependencies" in tags

    def test_gitignore(self):
        tags = get_filename_metatypes(".gitignore")
        assert "Git" in tags
        assert "ignore" in tags

    def test_license_file(self):
        tags = get_filename_metatypes("LICENSE")
        assert "license" in tags

    def test_license_txt(self):
        tags = get_filename_metatypes("LICENSE.txt")
        assert "license" in tags

    def test_claude_md(self):
        tags = get_filename_metatypes("CLAUDE.md")
        assert "Claude" in tags
        assert "AI" in tags

    def test_regular_python_file(self):
        tags = get_filename_metatypes("main.py")
        assert tags == []

    # Binary metadata
    def test_gif_metadata(self):
        tags = get_filename_metatypes("image.gif")
        assert "binary" in tags
        assert "image" in tags

    def test_pdf_metadata(self):
        tags = get_filename_metatypes("test.pdf")
        assert "binary" in tags

    def test_excel_metadata(self):
        tags = get_filename_metatypes("test.xlsx")
        assert "binary" in tags
        assert "Microsoft" in tags

    def test_jmx_metadata(self):
        tags = get_filename_metatypes("testing.jmx")
        assert "Apache" in tags
        assert "JMeter" in tags

    # Dependabot (#6)
    def test_dependabot_yml(self):
        tags = get_filename_metatypes("dependabot.yml")
        assert "Dependabot" in tags
        assert "GitHub" in tags
        assert "dependencies" in tags
        assert "security" in tags

    def test_dependabot_yaml(self):
        tags = get_filename_metatypes("dependabot.yaml")
        assert "Dependabot" in tags

    def test_dependabot_in_github_path(self):
        tags = get_filename_metatypes(".github/dependabot.yml")
        assert "Dependabot" in tags
        assert "GitHub" in tags

    # .NET metadata (#10)
    def test_csproj_metadata(self):
        tags = get_filename_metatypes("MyApp.csproj")
        assert ".NET" in tags
        assert "C#" in tags
        assert "build" in tags
        assert "dependencies" in tags

    def test_sln_metadata(self):
        tags = get_filename_metatypes("MyApp.sln")
        assert ".NET" in tags
        assert "Visual Studio" in tags
        assert "build" in tags

    def test_dll_metadata(self):
        tags = get_filename_metatypes("System.Core.dll")
        assert "binary" in tags
        assert ".NET" in tags

    def test_aspx_metadata(self):
        tags = get_filename_metatypes("Default.aspx")
        assert ".NET" in tags
        assert "ASP.NET" in tags

    def test_ascx_metadata(self):
        tags = get_filename_metatypes("Header.ascx")
        assert ".NET" in tags
        assert "ASP.NET" in tags

    def test_packages_config(self):
        tags = get_filename_metatypes("packages.config")
        assert ".NET" in tags
        assert "NuGet" in tags
        assert "dependencies" in tags

    def test_nuget_config(self):
        tags = get_filename_metatypes("nuget.config")
        assert ".NET" in tags
        assert "NuGet" in tags

    def test_web_config(self):
        tags = get_filename_metatypes("web.config")
        assert ".NET" in tags
        assert "ASP.NET" in tags

    def test_app_config(self):
        tags = get_filename_metatypes("app.config")
        assert ".NET" in tags
        assert "config" in tags

    def test_global_asax(self):
        tags = get_filename_metatypes("global.asax")
        assert ".NET" in tags
        assert "ASP.NET" in tags


class TestIsPipRequirements:
    """Tests for is_pip_requirements() — matching pip requirements filenames."""

    def test_requirements_txt(self):
        assert is_pip_requirements("requirements.txt") is True

    def test_requirements_in(self):
        assert is_pip_requirements("requirements.in") is True

    def test_requirements_dev_txt(self):
        assert is_pip_requirements("requirements-dev.txt") is True

    def test_requirements_dev_in(self):
        assert is_pip_requirements("requirements-dev.in") is True

    def test_requirements_dot_dev_txt(self):
        assert is_pip_requirements("requirements.dev.txt") is True

    def test_not_requirements(self):
        assert is_pip_requirements("readme.txt") is False

    def test_not_requirements_py(self):
        assert is_pip_requirements("requirements.py") is False


class TestExtractUrls:
    """Tests for extract_urls() — finding URLs in text."""

    def test_single_url(self):
        urls = extract_urls("Visit https://example.com for more info")
        assert "https://example.com" in urls

    def test_multiple_urls(self):
        text = "See https://example.com and http://test.org"
        urls = extract_urls(text)
        assert len(urls) == 2

    def test_no_urls(self):
        urls = extract_urls("No URLs here")
        assert urls == []

    def test_url_with_path(self):
        urls = extract_urls("Check https://github.com/kospex/panopticas")
        assert "https://github.com/kospex/panopticas" in urls


class TestExtractUrlsFromFile:
    """Tests for extract_urls_from_file() — including undecodable files."""

    def test_nonexistent_file_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_urls_from_file("/nonexistent/file.txt")

    def test_binary_file_raises_unicode_decode_error_not_type_error(self):
        # Regression test: the handler used to re-raise UnicodeDecodeError
        # with only a message argument, but UnicodeDecodeError.__init__
        # requires five positional arguments (encoding, object, start, end,
        # reason). That raised TypeError instead of UnicodeDecodeError,
        # crashing `urls` and `file` on any binary input.
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(b"\xff\xfe\x00\x01not valid utf-8")
            f.flush()
            path = f.name
        try:
            with pytest.raises(UnicodeDecodeError) as excinfo:
                extract_urls_from_file(path)
            assert path in str(excinfo.value)
        finally:
            os.unlink(path)


class TestCountLines:
    """Tests for count_lines() — counting lines in files."""

    def test_count_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("line 1\nline 2\nline 3\n")
            f.flush()
            assert count_lines(f.name) == 3
            os.unlink(f.name)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.flush()
            assert count_lines(f.name) == 0
            os.unlink(f.name)

    def test_nonexistent_file(self):
        assert count_lines("/nonexistent/file.txt") == "N/A"

    def test_binary_file(self):
        """Binary files return N/A or 0 (small binaries may not trigger decode error)."""
        gif_path = os.path.join(FIXTURES_DIR, "image.gif")
        if os.path.exists(gif_path):
            result = count_lines(gif_path)
            assert result == "N/A" or isinstance(result, int)


class TestFixtureFiles:
    """Tests using the fixture files in src/tests/."""

    @pytest.fixture
    def fixtures_exist(self):
        """Skip if fixtures directory doesn't exist."""
        if not os.path.isdir(FIXTURES_DIR):
            pytest.skip("Fixtures directory not found")

    def test_gif_detected_as_gif(self, fixtures_exist):
        assert get_language("image.gif") == "GIF"

    def test_pdf_detected_as_pdf(self, fixtures_exist):
        assert get_language("test.pdf") == "PDF"

    def test_excel_xls_detected(self, fixtures_exist):
        assert get_language("test.xls") == "Excel"

    def test_excel_xlsx_detected(self, fixtures_exist):
        assert get_language("test.xlsx") == "Excel"

    def test_groovy_detected(self, fixtures_exist):
        assert get_language("file.groovy") == "Groovy"

    def test_java_class_detected(self, fixtures_exist):
        assert get_language("somefile.class") == "Java Class"

    def test_jmx_detected(self, fixtures_exist):
        assert get_language("testing.jmx") == "Apache JMeter"

    def test_properties_detected(self, fixtures_exist):
        assert get_language("config.properties") == "Properties"

    def test_yaml_detected(self, fixtures_exist):
        assert get_language("settings.yaml") == "YAML"

    def test_toml_detected(self, fixtures_exist):
        assert get_language("settings.toml") == "TOML"

    def test_license_detected_as_text(self, fixtures_exist):
        assert get_language("LICENSE") == "Text"
        assert get_language("LICENSE.txt") == "Text"


class TestConstants:
    """Tests for constants integrity."""

    def test_ext_filetypes_not_empty(self):
        assert len(EXT_FILETYPES) > 0

    def test_all_extensions_lowercase(self):
        """All extension keys should be lowercase."""
        for key in EXT_FILETYPES:
            assert key == key.lower(), f"Extension key '{key}' is not lowercase"

    def test_metadata_rules_has_required_sections(self):
        assert "extension_rules" in METADATA_RULES
        assert "exact_filename_rules" in METADATA_RULES
        assert "path_contains_rules" in METADATA_RULES
        assert "function_rules" in METADATA_RULES

    def test_all_metadata_tags_are_strings(self):
        """All metadata tags should be non-empty strings."""
        for section in ["extension_rules", "exact_filename_rules", "path_contains_rules"]:
            for key, tags in METADATA_RULES[section].items():
                for tag in tags:
                    assert isinstance(tag, str) and len(tag) > 0, \
                        f"Invalid tag '{tag}' in {section}[{key}]"


@pytest.fixture
def sample_tree():
    """A temp directory tree with a .gitignore excluding secret.txt and build/.

    Layout:
        app.py          -> Python
        notes.md        -> Markdown
        lib/util.js     -> JavaScript
        .gitignore
        secret.txt      -> gitignored
        build/out.o     -> gitignored (directory)
    """
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "lib"))
        os.makedirs(os.path.join(tmp, "build"))
        with open(os.path.join(tmp, "app.py"), "w") as f:
            f.write("print('hi')\n")
        with open(os.path.join(tmp, "notes.md"), "w") as f:
            f.write("# Notes\n")
        with open(os.path.join(tmp, "lib", "util.js"), "w") as f:
            f.write("export const x = 1;\n")
        with open(os.path.join(tmp, ".gitignore"), "w") as f:
            f.write("secret.txt\nbuild/\n")
        with open(os.path.join(tmp, "secret.txt"), "w") as f:
            f.write("nope\n")
        with open(os.path.join(tmp, "build", "out.o"), "w") as f:
            f.write("artifact\n")
        yield tmp


class TestIdentifyFiles:
    """Tests for identify_files() — maps relative paths to file types.

    Used by kospex (kospex_git.py), so behavior here is part of the public API.
    """

    def test_maps_relative_paths_to_languages(self, sample_tree):
        result = identify_files(sample_tree)
        assert result["app.py"] == "Python"
        assert result["notes.md"] == "Markdown"
        assert result[os.path.join("lib", "util.js")] == "JavaScript"

    def test_honors_gitignore(self, sample_tree):
        result = identify_files(sample_tree)
        assert "secret.txt" not in result
        assert os.path.join("build", "out.o") not in result

    def test_returns_relative_not_absolute_paths(self, sample_tree):
        result = identify_files(sample_tree)
        assert result, "expected at least one file"
        for key in result:
            assert not os.path.isabs(key), f"{key!r} is not relative"


class TestFindFiles:
    """Tests for find_files() — lists relative paths, optionally ignoring gitignore."""

    def test_returns_relative_path_list_honoring_gitignore(self, sample_tree):
        result = find_files(sample_tree)
        assert isinstance(result, list)
        assert "app.py" in result
        assert os.path.join("lib", "util.js") in result
        assert "secret.txt" not in result

    def test_all_files_true_includes_gitignored(self, sample_tree):
        result = find_files(sample_tree, all_files=True)
        assert "secret.txt" in result
        assert os.path.join("build", "out.o") in result


class TestIdentifyFilesWithMetrics:
    """Tests for identify_files_with_metrics() — file type plus line count."""

    def test_values_have_type_and_line_count(self, sample_tree):
        result = identify_files_with_metrics(sample_tree)
        assert result["app.py"] == {"type": "Python", "lines": 1}
        for value in result.values():
            assert set(value) == {"type", "lines"}

    def test_honors_gitignore(self, sample_tree):
        result = identify_files_with_metrics(sample_tree)
        assert "secret.txt" not in result


class TestImplicitTags:
    """The tags get_filename_metatypes() emits without a rule table entry."""

    def test_license_tag_still_applied(self):
        assert "license" in get_filename_metatypes("LICENSE")
        assert "license" in get_filename_metatypes("license.md")

    def test_ai_tag_still_applied(self):
        assert "AI" in get_filename_metatypes("CLAUDE.md")

    def test_implicit_tags_exported(self):
        from panopticas.constants import AI_TAG, IMPLICIT_TAGS, LICENSE_TAG

        assert AI_TAG == "AI"
        assert LICENSE_TAG == "license"
        assert set(IMPLICIT_TAGS) == {"AI", "license"}
