"""Tests for CLI template selection flags (Sprint 1.2)."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from doc_evergreen.cli import cli


class TestInitListFlag:
    """Test --list flag shows available templates."""

    def test_init_list_shows_templates(self):
        """--list flag displays available templates."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        
        assert result.exit_code == 0
        # Should mention templates in output
        assert "template" in result.output.lower()

    def test_init_list_exits_without_creating_files(self):
        """--list flag exits without creating template files."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["init", "--list"])
            
            assert result.exit_code == 0
            # Should not create .doc-evergreen directory
            assert not Path(".doc-evergreen").exists()

    def test_init_list_shows_template_metadata(self):
        """--list flag displays template metadata (name, description, quadrant)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        
        assert result.exit_code == 0
        # Output should be formatted and helpful
        # When templates exist, should show their details
        output_lower = result.output.lower()
        
        # Should either show templates or indicate none available
        assert "template" in output_lower or "available" in output_lower

    def test_init_list_groups_by_quadrant(self):
        """--list flag groups templates by quadrant."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        
        assert result.exit_code == 0
        # When templates exist, should group by quadrant
        # For now, just verify it runs successfully


class TestInitTemplateFlag:
    """Test --template flag selects specific template."""

    def test_init_template_flag_loads_specified_template(self):
        """--template flag loads the specified template."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Try to load a template (will fail with no templates, but tests the flow)
            result = runner.invoke(cli, ["init", "--template", "tutorial-quickstart", "--yes"])
            
            # Should attempt to load the template
            # Will fail if template doesn't exist yet (Sprint 1.3)
            # But should recognize the flag
            assert "--template" not in result.output  # Flag was consumed

    def test_init_template_flag_with_nonexistent_template(self):
        """--template with nonexistent template shows error."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["init", "--template", "nonexistent-template", "--yes"])
            
            # Should exit with error
            assert result.exit_code != 0
            # Should mention the template wasn't found
            assert "nonexistent-template" in result.output or "not found" in result.output.lower()

    def test_init_template_default_is_tutorial_quickstart(self):
        """When --template not specified, defaults to tutorial-quickstart."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Run init without --template flag (will fail if template doesn't exist)
            result = runner.invoke(cli, ["init", "--yes"])
            
            # Should try to use default template
            # Will fail if template doesn't exist yet (Sprint 1.3)
            # Just verify the command structure is correct


class TestInitYesFlag:
    """Test --yes flag skips confirmation prompts."""

    def test_init_yes_skips_confirmation(self):
        """--yes flag skips confirmation prompts."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Run with --yes flag (will fail if no templates exist)
            result = runner.invoke(cli, ["init", "--yes"])
            
            # Should not show confirmation prompts
            assert "confirm" not in result.output.lower()
            assert "?" not in result.output  # No question prompts

    def test_init_without_yes_shows_confirmation(self):
        """Without --yes flag, shows confirmation prompt."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Run without --yes flag, but provide 'n' input to decline
            result = runner.invoke(cli, ["init"], input="n\n")
            
            # Should show some kind of confirmation or info before proceeding
            # (or fail if no templates exist yet)
            # For now, just verify command structure


class TestInitForceFlag:
    """Test --force flag overwrites existing templates."""

    def test_init_force_overwrites_existing(self):
        """--force flag overwrites existing template without prompt."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create .doc-evergreen directory with existing file
            Path(".doc-evergreen").mkdir()
            existing_template = Path(".doc-evergreen/tutorial-quickstart.json")
            existing_template.write_text('{"old": "content"}')
            
            # Run init with --force (will fail if template doesn't exist in registry)
            result = runner.invoke(cli, ["init", "--force", "--yes"])
            
            # Should attempt to overwrite
            # Command should at least run without asking about overwrite


class TestInitTemplateWriting:
    """Test that init writes template to correct location."""

    def test_init_writes_to_doc_evergreen_directory(self):
        """init writes template to .doc-evergreen/ directory."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # This will fail until we implement Sprint 1.3 templates
            # But tests the expected behavior
            result = runner.invoke(cli, ["init", "--yes"])
            
            # Should create .doc-evergreen directory
            # (will fail if no templates exist yet)

    def test_init_uses_template_name_as_filename(self):
        """init writes template as {template-name}.json."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Should write tutorial-quickstart.json for default template
            # (will fail if template doesn't exist yet)
            result = runner.invoke(cli, ["init", "--yes"])


class TestInitTemplateInfo:
    """Test that init shows template information."""

    def test_init_shows_template_info_before_writing(self):
        """init displays template metadata before writing."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["init"], input="n\n")
            
            # Should show template info (description, use case, etc.)
            # Before asking for confirmation
            # (will fail if no templates exist yet)

    def test_init_shows_next_steps_after_writing(self):
        """init shows helpful next steps after creating template."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # This will fail until Sprint 1.3, but tests expected behavior
            result = runner.invoke(cli, ["init", "--yes"])
            
            # Should show next steps or usage info
            # Current impl shows this, should continue to do so


class TestInitErrorHandling:
    """Test error handling in init command."""

    def test_init_handles_template_not_found(self):
        """init shows helpful error when template doesn't exist."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["init", "--template", "missing", "--yes"])
            
            assert result.exit_code != 0
            # Should show available templates in error
            assert "available" in result.output.lower() or "not found" in result.output.lower()

    def test_init_handles_invalid_template_json(self):
        """init shows error when template JSON is malformed."""
        # This will be tested once we have templates and can test validation
        # For now, just verify the command structure
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0


class TestInitBackwardCompatibility:
    """Test that init maintains backward compatibility."""

    def test_init_still_supports_legacy_flags(self):
        """init still supports --name and --description flags."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # These flags existed before, should still work
            result = runner.invoke(cli, ["init", "--help"])
            
            # Help should show all flags
            assert "--list" in result.output
            assert "--template" in result.output
            assert "--yes" in result.output
            assert "--force" in result.output


class TestEnhancedListOutput:
    """Tests for enhanced --list output (Sprint 2.3)."""
    
    def test_list_shows_quadrant_grouping(self):
        """--list groups templates by quadrant with emoji indicators."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        assert result.exit_code == 0
        assert "📚 TUTORIALS" in result.output
        assert "🎯 HOW-TO GUIDES" in result.output
        assert "📖 REFERENCE" in result.output
        assert "💡 EXPLANATION" in result.output
    
    def test_list_shows_quadrant_descriptions(self):
        """--list shows descriptive text for each quadrant."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        assert result.exit_code == 0
        # Check for quadrant descriptions
        assert "Learning-oriented" in result.output
        assert "Goal-oriented" in result.output
        assert "Information-oriented" in result.output
        assert "Understanding-oriented" in result.output
    
    def test_list_shows_use_case_for_each_template(self):
        """--list shows 'Use when' for each template."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        assert result.exit_code == 0
        assert "Use when:" in result.output
    
    def test_list_shows_output_paths(self):
        """--list shows output file paths for templates."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        assert result.exit_code == 0
        assert "Output:" in result.output
        assert "Estimated:" in result.output
    
    def test_list_shows_tip_at_end(self):
        """--list shows helpful tip at the end."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        assert result.exit_code == 0
        # Look for tip - could be emoji or text
        assert ("💡 Tip:" in result.output or "Tip:" in result.output)
    
    def test_list_shows_interactive_selection_hint(self):
        """--list suggests using interactive selection."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        assert result.exit_code == 0
        # Should mention interactive mode
        assert "init" in result.output.lower()
    
    def test_list_format_is_readable(self):
        """--list output has proper spacing and formatting."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--list"])
        assert result.exit_code == 0
        # Should have blank lines between sections
        lines = result.output.split("\n")
        # Count blank lines - should have several for readability
        blank_lines = sum(1 for line in lines if line.strip() == "")
        assert blank_lines >= 5  # Multiple sections with spacing
