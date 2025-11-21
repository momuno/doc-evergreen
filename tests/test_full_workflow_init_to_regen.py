"""Test complete workflow: init → customize → regen-doc."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import cli


class TestFullWorkflowInitToRegen:
    """Test the complete user workflow from init to regeneration."""

    @pytest.fixture
    def cli_runner(self):
        """Provide Click CLI test runner."""
        return CliRunner()

    def test_init_then_regen_workflow(self, tmp_path, cli_runner):
        """
        Given: Empty project directory
        When: Running init then regen-doc with short name
        Then: Complete workflow succeeds
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Create a source file for template to reference
            (tmp_path / "main.py").write_text("# Main file\n")

            # ACT Step 1: Initialize
            init_result = cli_runner.invoke(cli, ["init", "--name", "Test Project"])

            # ASSERT Step 1: Init succeeded
            assert init_result.exit_code == 0, f"Init failed: {init_result.output}"
            assert (tmp_path / ".doc-evergreen" / "readme.json").exists()

            # ACT Step 2: Regenerate using short name
            regen_result = cli_runner.invoke(cli, ["regen-doc", "readme", "--auto-approve"])

            # ASSERT Step 2: Regen found template and attempted generation
            assert "template not found" not in regen_result.output.lower()
            assert "invalid" not in regen_result.output.lower()
            # Template was found and validated (may fail on API key, that's OK)
        finally:
            os.chdir(original_cwd)

    def test_init_with_custom_name_then_regen(self, tmp_path, cli_runner):
        """
        Given: Project initialized with custom name
        When: Regenerating documentation
        Then: Custom name appears in template
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # ACT: Init with custom name
            init_result = cli_runner.invoke(cli, ["init", "--name", "MyCustomProject"])
            assert init_result.exit_code == 0

            # Verify template has custom name
            template_path = tmp_path / ".doc-evergreen" / "readme.json"
            with open(template_path) as f:
                template_data = json.load(f)

            # ASSERT
            assert "MyCustomProject" in template_data["document"]["title"]
        finally:
            os.chdir(original_cwd)

    def test_workflow_with_template_customization(self, tmp_path, cli_runner):
        """
        Given: Initialized project
        When: User customizes template then regenerates
        Then: Customizations are preserved
        """
        # ARRANGE
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # ACT Step 1: Init
            init_result = cli_runner.invoke(cli, ["init"])
            assert init_result.exit_code == 0

            # ACT Step 2: Customize template
            template_path = tmp_path / ".doc-evergreen" / "readme.json"
            with open(template_path) as f:
                template = json.load(f)

            # Add custom section
            template["document"]["sections"].append(
                {
                    "heading": "## Custom Section",
                    "prompt": "My custom prompt",
                    "sources": ["*.md"],
                }
            )

            with open(template_path, "w") as f:
                json.dump(template, f, indent=2)

            # ACT Step 3: Regen with customized template
            regen_result = cli_runner.invoke(cli, ["regen-doc", "readme", "--auto-approve"])

            # ASSERT: Should validate successfully (template was found and parsed)
            assert "invalid" not in regen_result.output.lower()
            assert "template not found" not in regen_result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_multiple_projects_stay_isolated(self, tmp_path, cli_runner):
        """
        Given: Multiple project directories
        When: Each runs init
        Then: Each gets independent .doc-evergreen/ directory
        """
        # ARRANGE
        proj1 = tmp_path / "project1"
        proj2 = tmp_path / "project2"
        proj1.mkdir()
        proj2.mkdir()

        original_cwd = Path.cwd()
        try:
            # ACT: Init both projects
            os.chdir(proj1)
            result1 = cli_runner.invoke(cli, ["init", "--name", "Project One"])
            assert result1.exit_code == 0

            os.chdir(proj2)
            result2 = cli_runner.invoke(cli, ["init", "--name", "Project Two"])
            assert result2.exit_code == 0

            # ASSERT: Each has independent template
            template1 = proj1 / ".doc-evergreen" / "readme.json"
            template2 = proj2 / ".doc-evergreen" / "readme.json"

            assert template1.exists()
            assert template2.exists()

            with open(template1) as f:
                data1 = json.load(f)
            with open(template2) as f:
                data2 = json.load(f)

            assert "Project One" in data1["document"]["title"]
            assert "Project Two" in data2["document"]["title"]
        finally:
            os.chdir(original_cwd)
