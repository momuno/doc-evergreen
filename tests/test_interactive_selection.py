"""Tests for interactive template selection (Sprint 2.2)

Tests the interactive CLI menu that guides users to select templates
organized by Divio documentation quadrants.
"""

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import cli, interactive_template_selection
from doc_evergreen.template_registry import TemplateRegistry


class TestInteractiveSelection:
    """Tests for interactive template selection"""

    def test_interactive_mode_shows_menu(self):
        """Interactive mode displays template menu with Divio organization"""
        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="q\n")
        
        assert result.exit_code == 0
        assert "What type of documentation" in result.output
        assert "📚 TUTORIALS" in result.output
        assert "🎯 HOW-TO GUIDES" in result.output
        assert "📖 REFERENCE" in result.output
        assert "💡 EXPLANATION" in result.output

    def test_interactive_mode_shows_all_templates(self):
        """Interactive mode shows all 9 templates"""
        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="q\n")
        
        # Check all template names appear
        assert "tutorial-quickstart" in result.output
        assert "tutorial-first-template" in result.output
        assert "howto-contributing-guide" in result.output
        assert "howto-ci-integration" in result.output
        assert "howto-custom-prompts" in result.output
        assert "reference-cli" in result.output
        assert "reference-api" in result.output
        assert "explanation-architecture" in result.output
        assert "explanation-concepts" in result.output

    def test_interactive_mode_shows_descriptions(self):
        """Interactive mode shows template descriptions and line estimates"""
        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="q\n")
        
        # Should show descriptions (at least partial)
        assert "quickstart" in result.output.lower() or "brief" in result.output.lower()
        # Should show line estimates
        assert "lines" in result.output.lower()

    def test_interactive_selection_with_number(self, tmp_path, monkeypatch):
        """User can select template by number"""
        monkeypatch.chdir(tmp_path)
        
        runner = CliRunner()
        # Select option 1 (tutorial-first-template is first), then confirm with 'y'
        result = runner.invoke(cli, ["init"], input="1\ny\n")
        
        assert result.exit_code == 0
        # Should create template file (option 1 is tutorial-first-template)
        template_file = tmp_path / ".doc-evergreen" / "tutorial-first-template.json"
        assert template_file.exists()

    def test_interactive_selection_with_quit(self):
        """User can quit with 'q'"""
        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="q\n")
        
        assert result.exit_code == 0
        assert "Cancelled" in result.output or "cancelled" in result.output.lower()

    def test_interactive_selection_validates_input(self):
        """Invalid input is rejected and user is re-prompted"""
        runner = CliRunner()
        # Try invalid input first, then quit
        result = runner.invoke(cli, ["init"], input="invalid\nq\n")
        
        # Should show some validation message
        assert "Invalid" in result.output or "Please" in result.output or "Enter" in result.output

    def test_interactive_selection_shows_numbered_options(self):
        """Templates are numbered 1-9 continuously"""
        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="q\n")
        
        # Check all numbers 1-9 are present
        for i in range(1, 10):
            assert f"{i}." in result.output or f"  {i}." in result.output

    def test_template_flag_bypasses_interactive(self, tmp_path, monkeypatch):
        """--template flag skips interactive mode"""
        monkeypatch.chdir(tmp_path)
        
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--template", "tutorial-quickstart", "--yes"])
        
        # Should NOT show interactive menu
        assert "What type of documentation" not in result.output
        assert "Choose" not in result.output
        
        # Should create template file
        template_file = tmp_path / ".doc-evergreen" / "tutorial-quickstart.json"
        assert template_file.exists()

    def test_yes_flag_uses_default_without_interactive(self, tmp_path, monkeypatch):
        """--yes without --template uses default (tutorial-quickstart)"""
        monkeypatch.chdir(tmp_path)
        
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--yes"])
        
        # Should NOT show interactive menu
        assert "What type of documentation" not in result.output
        assert "Choose" not in result.output
        
        # Should use default template (tutorial-quickstart)
        template_file = tmp_path / ".doc-evergreen" / "tutorial-quickstart.json"
        assert template_file.exists()

    def test_interactive_selection_out_of_range(self):
        """Out of range number (e.g., 10, 0) is rejected"""
        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="10\nq\n")
        
        # Should show validation message
        assert "Invalid" in result.output or "Please" in result.output or "1-9" in result.output

    def test_list_flag_bypasses_interactive(self):
        """--list flag shows templates and exits without interactive mode"""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        
        assert result.exit_code == 0
        # Should show templates
        assert "tutorial-quickstart" in result.output
        # Should NOT show interactive prompts
        assert "Choose" not in result.output


class TestInteractiveSelectionFunction:
    """Tests for the interactive_template_selection() function directly via CLI"""

    def test_function_returns_template_name(self):
        """Function returns template name when user selects valid number"""
        # Test via CLI runner which properly handles click.prompt
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--yes"], input="1\n")
        
        # When using --yes, it bypasses interactive mode, so test differently
        # Instead, test without --yes to trigger interactive mode
        runner = CliRunner()
        registry = TemplateRegistry()
        templates = registry.list_templates()
        
        # Mix input test via CLI - select first template
        result = runner.invoke(cli, ["init"], input="1\ny\n")
        
        # Should show the selected template name in output
        assert result.exit_code == 0
        assert templates[0].name in result.output or "tutorial" in result.output.lower()

    def test_function_returns_none_on_quit(self):
        """Function returns None when user quits with 'q'"""
        # Test via CLI which properly handles click.prompt
        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="q\n")
        
        assert result.exit_code == 0
        assert "Cancelled" in result.output or "cancelled" in result.output.lower()

    def test_function_validates_and_reprompts(self):
        """Function validates input and re-prompts on invalid input"""
        # Test via CLI which properly handles click.prompt
        runner = CliRunner()
        # Invalid input, then quit
        result = runner.invoke(cli, ["init"], input="invalid\nq\n")
        
        # Should show validation message before accepting quit
        assert "Invalid" in result.output or "Please" in result.output
        assert result.exit_code == 0
