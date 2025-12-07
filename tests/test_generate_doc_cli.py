"""Tests for generate-doc CLI command."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import cli


class TestGenerateDocCommand:
    """Test generate-doc CLI command."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_command_exists(self, runner):
        """Should have generate-doc subcommand."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "generate-doc" in result.output

    def test_requires_output_path(self, runner):
        """Should require output path argument."""
        result = runner.invoke(cli, ["generate-doc"])
        assert result.exit_code != 0
        assert "output" in result.output.lower() or "missing argument" in result.output.lower()

    def test_requires_type_option(self, runner):
        """Should require --type option."""
        result = runner.invoke(cli, ["generate-doc", "README.md"])
        assert result.exit_code != 0
        assert "type" in result.output.lower()

    def test_requires_purpose_option(self, runner):
        """Should require --purpose option."""
        result = runner.invoke(cli, ["generate-doc", "README.md", "--type", "tutorial"])
        assert result.exit_code != 0
        assert "purpose" in result.output.lower()

    def test_validates_doc_type(self, runner):
        """Should reject invalid doc types."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "invalid-type",
                "--purpose", "Test purpose"
            ])
            
            assert result.exit_code != 0
            assert "invalid" in result.output.lower()
            assert "tutorial" in result.output.lower()  # Should suggest valid types

    def test_accepts_valid_tutorial_type(self, runner):
        """Should accept 'tutorial' as valid type."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "tutorial",
                "--purpose", "Help developers get started"
            ])
            
            assert result.exit_code == 0
            assert "intent captured" in result.output.lower() or "success" in result.output.lower()

    def test_accepts_all_diataxis_types(self, runner):
        """Should accept all four Diataxis doc types."""
        doc_types = ["tutorial", "howto", "reference", "explanation"]
        
        for doc_type in doc_types:
            with runner.isolated_filesystem():
                result = runner.invoke(cli, [
                    "generate-doc", "README.md",
                    "--type", doc_type,
                    "--purpose", "Test purpose"
                ])
                
                assert result.exit_code == 0, f"Failed for type: {doc_type}"

    def test_case_insensitive_doc_type(self, runner):
        """Should accept doc type in any case."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "TUTORIAL",
                "--purpose", "Test purpose"
            ])
            
            assert result.exit_code == 0

    def test_creates_context_file(self, runner):
        """Should create .doc-evergreen/context.json."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "tutorial",
                "--purpose", "Getting started guide"
            ])
            
            assert result.exit_code == 0
            
            context_file = Path(".doc-evergreen/context.json")
            assert context_file.exists()

    def test_context_file_has_correct_fields(self, runner):
        """Context file should have all required fields."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-doc", "API.md",
                "--type", "reference",
                "--purpose", "API documentation"
            ])
            
            assert result.exit_code == 0
            
            context_file = Path(".doc-evergreen/context.json")
            data = json.loads(context_file.read_text())
            
            assert data["doc_type"] == "reference"
            assert data["purpose"] == "API documentation"
            assert data["output_path"] == "API.md"
            assert data["version"] == "0.7.0"
            assert data["status"] == "intent_captured"
            assert "timestamp" in data

    def test_displays_success_message(self, runner):
        """Should display clear success message."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "tutorial",
                "--purpose", "Help users get started"
            ])
            
            assert result.exit_code == 0
            assert "captured" in result.output.lower() or "saved" in result.output.lower()

    def test_shows_next_steps(self, runner):
        """Should guide user on next steps (placeholder for now)."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "howto",
                "--purpose", "Solve specific problem"
            ])
            
            assert result.exit_code == 0
            # For Sprint 1, just confirm intent captured
            # Future sprints will add actual generation

    def test_overwrites_existing_context(self, runner):
        """Should overwrite existing context file."""
        with runner.isolated_filesystem():
            # First invocation
            runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "tutorial",
                "--purpose", "First purpose"
            ])
            
            # Second invocation (should overwrite)
            result = runner.invoke(cli, [
                "generate-doc", "GUIDE.md",
                "--type", "howto",
                "--purpose", "Second purpose"
            ])
            
            assert result.exit_code == 0
            
            context_file = Path(".doc-evergreen/context.json")
            data = json.loads(context_file.read_text())
            assert data["purpose"] == "Second purpose"
            assert data["output_path"] == "GUIDE.md"

    def test_help_text_describes_command(self, runner):
        """Help text should explain what command does."""
        result = runner.invoke(cli, ["generate-doc", "--help"])
        
        assert result.exit_code == 0
        assert "generate" in result.output.lower()
        assert "document" in result.output.lower() or "doc" in result.output.lower()

    def test_help_text_lists_doc_types(self, runner):
        """Help text should list valid doc types."""
        result = runner.invoke(cli, ["generate-doc", "--help"])
        
        assert result.exit_code == 0
        assert "tutorial" in result.output.lower()
        assert "howto" in result.output.lower()
        assert "reference" in result.output.lower()
        assert "explanation" in result.output.lower()


class TestGenerateDocIntegration:
    """Integration tests for generate-doc workflow."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_full_workflow_sprint_1(self, runner):
        """Test complete Sprint 1 workflow: capture intent."""
        with runner.isolated_filesystem():
            # Run generate-doc command
            result = runner.invoke(cli, [
                "generate-doc", "README.md",
                "--type", "tutorial",
                "--purpose", "Help developers get started in 5 minutes"
            ])
            
            # Should succeed
            assert result.exit_code == 0
            
            # Context file created
            assert Path(".doc-evergreen/context.json").exists()
            
            # Context has correct data
            data = json.loads(Path(".doc-evergreen/context.json").read_text())
            assert data["doc_type"] == "tutorial"
            assert data["purpose"] == "Help developers get started in 5 minutes"
            assert data["output_path"] == "README.md"
            
            # User sees success message
            assert "captured" in result.output.lower() or "saved" in result.output.lower()
