"""Tests for doc-evergreen init command."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import cli
from doc_evergreen.core.template_schema import parse_template


class TestInitCommand:
    """Tests for init command that bootstraps projects."""

    @pytest.fixture
    def cli_runner(self):
        """Provide Click CLI test runner."""
        return CliRunner()

    def test_init_creates_directory(self, tmp_path, cli_runner):
        """
        Given: Empty project directory
        When: init command is run
        Then: .doc-evergreen/ directory is created
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # ACT
            result = cli_runner.invoke(cli, ["init"])

            # ASSERT
            assert result.exit_code == 0, f"Init failed: {result.output}"
            assert (tmp_path / ".doc-evergreen").exists()
            assert (tmp_path / ".doc-evergreen").is_dir()
        finally:
            os.chdir(original_cwd)

    def test_init_creates_readme_template(self, tmp_path, cli_runner):
        """
        Given: Empty project directory
        When: init command is run
        Then: readme.json template is created
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # ACT
            result = cli_runner.invoke(cli, ["init"])

            # ASSERT
            assert result.exit_code == 0
            template_path = tmp_path / ".doc-evergreen" / "readme.json"
            assert template_path.exists()
            assert template_path.is_file()
        finally:
            os.chdir(original_cwd)

    def test_generated_template_is_valid(self, tmp_path, cli_runner):
        """
        Given: Empty directory
        When: init creates template
        Then: Template has valid structure with document, sections
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # ACT
            result = cli_runner.invoke(cli, ["init"])

            # ASSERT
            assert result.exit_code == 0
            template_path = tmp_path / ".doc-evergreen" / "readme.json"

            # Verify it parses as valid template
            template = parse_template(template_path)
            assert template.document.title is not None
            assert template.document.output is not None
            assert len(template.document.sections) >= 3  # At least 3 sections
        finally:
            os.chdir(original_cwd)

    def test_no_overwrite_without_force(self, tmp_path, cli_runner):
        """
        Given: Existing .doc-evergreen/readme.json
        When: init run without --force
        Then: Refuses to overwrite
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            doc_dir = tmp_path / ".doc-evergreen"
            doc_dir.mkdir()
            existing = doc_dir / "readme.json"
            existing.write_text('{"custom": "content"}')

            # ACT
            result = cli_runner.invoke(cli, ["init"])

            # ASSERT
            assert result.exit_code != 0
            assert "exists" in result.output.lower() or "force" in result.output.lower()
            assert existing.read_text() == '{"custom": "content"}'  # Unchanged
        finally:
            os.chdir(original_cwd)

    def test_force_overwrites_existing(self, tmp_path, cli_runner):
        """
        Given: Existing template
        When: init run with --force
        Then: Overwrites existing template
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            doc_dir = tmp_path / ".doc-evergreen"
            doc_dir.mkdir()
            existing = doc_dir / "readme.json"
            existing.write_text('{"old": "content"}')

            # ACT
            result = cli_runner.invoke(cli, ["init", "--force"])

            # ASSERT
            assert result.exit_code == 0
            content = existing.read_text()
            assert '{"old": "content"}' not in content
            # Should have new template structure
            data = json.loads(content)
            assert "document" in data
        finally:
            os.chdir(original_cwd)

    def test_uses_directory_name_by_default(self, tmp_path, cli_runner):
        """
        Given: Directory named "my_awesome_project"
        When: init run without --name
        Then: Template title uses directory name
        """
        # ARRANGE
        project_dir = tmp_path / "my_awesome_project"
        project_dir.mkdir()

        original_cwd = Path.cwd()
        try:
            os.chdir(project_dir)

            # ACT
            result = cli_runner.invoke(cli, ["init"])

            # ASSERT
            assert result.exit_code == 0
            template_path = project_dir / ".doc-evergreen" / "readme.json"
            template = parse_template(template_path)
            assert "my_awesome_project" in template.document.title.lower()
        finally:
            os.chdir(original_cwd)

    def test_custom_name_option(self, tmp_path, cli_runner):
        """
        Given: Any directory
        When: init run with --name "Custom Project"
        Then: Template uses provided name
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # ACT
            result = cli_runner.invoke(cli, ["init", "--name", "Custom Project"])

            # ASSERT
            assert result.exit_code == 0
            template_path = tmp_path / ".doc-evergreen" / "readme.json"
            template = parse_template(template_path)
            assert "Custom Project" in template.document.title
        finally:
            os.chdir(original_cwd)

    def test_generated_template_works_with_regen(self, tmp_path, cli_runner):
        """
        Given: Fresh init
        When: Immediately running regen-doc with short name
        Then: Should work without errors (validates template structure)
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Create some source files for template to reference
            (tmp_path / "README.md").write_text("# Existing readme\n")

            # ACT: Init then regen
            init_result = cli_runner.invoke(cli, ["init"])
            assert init_result.exit_code == 0

            regen_result = cli_runner.invoke(cli, ["regen-doc", "readme", "--auto-approve"])

            # ASSERT: Regen should at least validate template (may fail on API key, that's OK)
            # Check that template was found and parsed
            assert "template not found" not in regen_result.output.lower()
            assert "invalid json" not in regen_result.output.lower()
        finally:
            os.chdir(original_cwd)
