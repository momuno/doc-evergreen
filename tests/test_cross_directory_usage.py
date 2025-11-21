"""Test that doc-evergreen works independently across multiple project directories."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import cli


class TestCrossDirectoryUsage:
    """Test tool works from any directory without interference."""

    @pytest.fixture
    def cli_runner(self):
        """Provide Click CLI test runner."""
        return CliRunner()

    def test_multiple_projects_work_independently(self, tmp_path, cli_runner):
        """
        Given: Multiple project directories with different structures
        When: Running doc-evergreen from each project
        Then: Each generates correctly using its own sources
        """
        # ARRANGE: Create 3 different projects
        projects = []

        # Project 1: src/ layout
        proj1 = tmp_path / "project1"
        proj1.mkdir()
        (proj1 / "src").mkdir()
        (proj1 / "src" / "main.py").write_text("# Project 1 main\n")

        template1 = proj1 / "template.json"
        template1.write_text(
            json.dumps(
                {
                    "document": {
                        "title": "Project 1",
                        "output": "README.md",
                        "sections": [
                            {"heading": "# Project 1", "prompt": "Document project 1", "sources": ["src/main.py"]}
                        ],
                    }
                }
            )
        )
        projects.append((proj1, template1, proj1 / "README.md"))

        # Project 2: lib/ layout
        proj2 = tmp_path / "project2"
        proj2.mkdir()
        (proj2 / "lib").mkdir()
        (proj2 / "lib" / "code.py").write_text("# Project 2 code\n")

        template2 = proj2 / "docs" / "template.json"
        template2.parent.mkdir()
        template2.write_text(
            json.dumps(
                {
                    "document": {
                        "title": "Project 2",
                        "output": "API.md",
                        "sections": [
                            {"heading": "# API", "prompt": "Document API", "sources": ["lib/code.py"]}
                        ],
                    }
                }
            )
        )
        projects.append((proj2, template2, proj2 / "API.md"))

        # Project 3: flat layout
        proj3 = tmp_path / "project3"
        proj3.mkdir()
        (proj3 / "app.py").write_text("# Project 3 app\n")

        template3 = proj3 / ".config" / "template.json"
        template3.parent.mkdir()
        template3.write_text(
            json.dumps(
                {
                    "document": {
                        "title": "Project 3",
                        "output": "DOCS.md",
                        "sections": [{"heading": "# App", "prompt": "Document app", "sources": ["app.py"]}],
                    }
                }
            )
        )
        projects.append((proj3, template3, proj3 / "DOCS.md"))

        # ACT: Generate from each project directory
        original_cwd = Path.cwd()
        try:
            for project_dir, template_path, output_path in projects:
                os.chdir(project_dir)

                result = cli_runner.invoke(
                    cli,
                    ["regen-doc", str(template_path), "--auto-approve"],
                )

                # ASSERT: Sources should be found from cwd (shows in output before LLM call)
                # Success means exit_code 0, but if API key missing, we still verify sources found
                output_lower = result.output.lower()

                # Check that sources were found (appears in progress output)
                assert "sources:" in output_lower, (
                    f"Project {project_dir.name}: Sources should be listed in output"
                )

                # If API key is set and generation succeeded, verify output
                if result.exit_code == 0:
                    assert output_path.exists(), f"Output not created for {project_dir.name}"
                    content = output_path.read_text()
                    assert project_dir.name.replace("project", "Project") in content
                else:
                    # API key missing is OK - we verified sources were found
                    assert "api" in output_lower or "anthropic" in output_lower
        finally:
            os.chdir(original_cwd)

    def test_template_location_doesnt_matter(self, tmp_path, cli_runner):
        """
        Given: Template stored anywhere on filesystem
        When: Running from project directory
        Then: Sources still resolved from project directory
        """
        # ARRANGE: Project at one location
        project = tmp_path / "my_project"
        project.mkdir()
        (project / "code.py").write_text("# Code\n")

        # Template at completely different location
        template_location = tmp_path / "other" / "location" / "templates"
        template_location.mkdir(parents=True)

        template = template_location / "template.json"
        template.write_text(
            json.dumps(
                {
                    "document": {
                        "title": "Test",
                        "output": "OUT.md",
                        "sections": [{"heading": "# Code", "prompt": "Document", "sources": ["code.py"]}],
                    }
                }
            )
        )

        # ACT: Run from project with template elsewhere
        original_cwd = Path.cwd()
        try:
            os.chdir(project)
            result = cli_runner.invoke(cli, ["regen-doc", str(template), "--auto-approve"])
        finally:
            os.chdir(original_cwd)

        # ASSERT: Should find sources from project (shown in progress output)
        output_lower = result.output.lower()
        assert "sources:" in output_lower and "code.py" in output_lower, (
            "Should find code.py from project directory, not template location"
        )

        # If API key set and succeeded, verify output
        if result.exit_code == 0:
            assert (project / "OUT.md").exists()
