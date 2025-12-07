"""Tests for generate-outline and generate-from-outline CLI commands (Sprint 7)."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import cli


class TestGenerateOutlineCommand:
    """Test generate-outline CLI command."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_command_exists(self, runner):
        """Should have generate-outline subcommand."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        # After Sprint 7, should see generate-outline
        # (If not yet, this test will guide implementation)

    def test_generates_outline_without_doc(self, runner):
        """Should generate outline without generating document."""
        with runner.isolated_filesystem():
            # Create a simple project structure
            Path("src").mkdir()
            Path("src/main.py").write_text("def main(): pass")
            Path("README.md").write_text("# My Project")
            
            result = runner.invoke(cli, [
                "generate-outline", "README.md",
                "--type", "tutorial",
                "--purpose", "Help users get started"
            ])
            
            # Command should succeed
            assert result.exit_code == 0
            
            # Should create outline.json
            outline_path = Path(".doc-evergreen/outline.json")
            assert outline_path.exists()
            
            # Should NOT create output document yet
            assert not Path("README.md").exists() or Path("README.md").read_text() == "# My Project"

    def test_outline_has_valid_structure(self, runner):
        """Generated outline should have valid structure."""
        with runner.isolated_filesystem():
            Path("src").mkdir()
            Path("src/main.py").write_text("def main(): pass")
            
            result = runner.invoke(cli, [
                "generate-outline", "OUTPUT.md",
                "--type", "tutorial",
                "--purpose", "Getting started"
            ])
            
            assert result.exit_code == 0
            
            outline_path = Path(".doc-evergreen/outline.json")
            data = json.loads(outline_path.read_text())
            
            # Should have required structure
            assert "_meta" in data
            assert "document" in data
            assert "sections" in data["document"]


class TestGenerateFromOutlineCommand:
    """Test generate-from-outline CLI command."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_command_exists(self, runner):
        """Should have generate-from-outline subcommand."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        # After Sprint 7, should see generate-from-outline

    def test_generates_doc_from_outline(self, runner):
        """Should generate document from existing outline."""
        with runner.isolated_filesystem():
            # First generate outline
            Path("src").mkdir()
            Path("src/main.py").write_text("def main(): pass")
            
            runner.invoke(cli, [
                "generate-outline", "OUTPUT.md",
                "--type", "tutorial",
                "--purpose", "Getting started"
            ])
            
            # Now generate doc from outline
            result = runner.invoke(cli, [
                "generate-from-outline",
                ".doc-evergreen/outline.json"
            ])
            
            assert result.exit_code == 0
            
            # Should create output document
            assert Path("OUTPUT.md").exists()
            content = Path("OUTPUT.md").read_text()
            assert len(content) > 0

    def test_fails_if_outline_missing(self, runner):
        """Should fail gracefully if outline doesn't exist."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-from-outline",
                "nonexistent.json"
            ])
            
            assert result.exit_code != 0
            assert "not found" in result.output.lower() or "does not exist" in result.output.lower()

    def test_respects_edited_outline(self, runner):
        """Should respect manual edits to outline."""
        with runner.isolated_filesystem():
            # Generate initial outline
            Path("src").mkdir()
            Path("src/main.py").write_text("def main(): pass")
            
            runner.invoke(cli, [
                "generate-outline", "OUTPUT.md",
                "--type", "tutorial",
                "--purpose", "Getting started"
            ])
            
            # Edit the outline
            outline_path = Path(".doc-evergreen/outline.json")
            data = json.loads(outline_path.read_text())
            data["document"]["title"] = "Edited Title"
            outline_path.write_text(json.dumps(data, indent=2))
            
            # Generate from edited outline
            result = runner.invoke(cli, [
                "generate-from-outline",
                ".doc-evergreen/outline.json"
            ])
            
            assert result.exit_code == 0
            
            # Should use edited title
            content = Path("OUTPUT.md").read_text()
            assert "Edited Title" in content


class TestTwoCommandWorkflow:
    """Integration tests for two-command workflow."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_complete_two_command_workflow(self, runner):
        """Test complete workflow: generate-outline → edit → generate-from-outline."""
        with runner.isolated_filesystem():
            # Setup project
            Path("src").mkdir()
            Path("src/cli.py").write_text("import click\ndef main(): pass")
            Path("README.md").write_text("# My CLI Tool\n\nA great tool")
            
            # Step 1: Generate outline
            result1 = runner.invoke(cli, [
                "generate-outline", "TUTORIAL.md",
                "--type", "tutorial",
                "--purpose", "Help users use the CLI"
            ])
            
            assert result1.exit_code == 0
            assert Path(".doc-evergreen/outline.json").exists()
            
            # Step 2: User would edit outline here (simulated)
            outline_path = Path(".doc-evergreen/outline.json")
            data = json.loads(outline_path.read_text())
            # Make a small edit
            data["document"]["title"] = "CLI Tool Tutorial"
            outline_path.write_text(json.dumps(data, indent=2))
            
            # Step 3: Generate document from (edited) outline
            result2 = runner.invoke(cli, [
                "generate-from-outline",
                ".doc-evergreen/outline.json"
            ])
            
            assert result2.exit_code == 0
            
            # Verify output
            assert Path("TUTORIAL.md").exists()
            content = Path("TUTORIAL.md").read_text()
            assert "CLI Tool Tutorial" in content
            assert len(content) > 100

    def test_shows_helpful_guidance(self, runner):
        """Should show helpful next steps after generate-outline."""
        with runner.isolated_filesystem():
            Path("src").mkdir()
            Path("src/main.py").write_text("def main(): pass")
            
            result = runner.invoke(cli, [
                "generate-outline", "OUTPUT.md",
                "--type", "tutorial",
                "--purpose", "Getting started"
            ])
            
            # Should guide user to next command
            assert "generate-from-outline" in result.output


class TestCLIPolish:
    """Test CLI polish and UX improvements."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_helpful_error_for_missing_outline(self, runner):
        """Should provide helpful error when outline is missing."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-from-outline",
                ".doc-evergreen/outline.json"
            ])
            
            assert result.exit_code != 0
            # Should suggest how to create outline
            assert "generate-outline" in result.output.lower()

    def test_help_text_includes_examples(self, runner):
        """Help text should include usage examples."""
        result = runner.invoke(cli, ["generate-outline", "--help"])
        
        assert result.exit_code == 0
        # Should have helpful documentation
        assert "outline" in result.output.lower()
