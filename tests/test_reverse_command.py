"""Tests for CLI reverse command - end-to-end integration test."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

try:
    from doc_evergreen.cli import cli
except ImportError:
    cli = None


class TestReverseCommand:
    """End-to-end integration tests for template reverse command."""
    
    def test_reverse_command_generates_template_from_readme(self, tmp_path):
        """
        Given: A README.md with structured content
        When: Run `doc-evergreen reverse README.md`
        Then: Generates valid template.json with correct structure
        """
        # ARRANGE
        # Create test README with structure
        readme = tmp_path / "README.md"
        readme.write_text("""# My Project

A sample project for testing.

## Installation

Install using pip:

```bash
pip install my-project
```

## Usage

Run the command:

```bash
my-project run
```

## Configuration

Set up your config file.
""")
        
        # Create some source files for discovery
        (tmp_path / "setup.py").write_text("# setup")
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("# main")
        
        # ACT
        runner = CliRunner()
        result = runner.invoke(cli, ['reverse', str(readme)])
        
        # ASSERT
        assert result.exit_code == 0
        assert "Template generated" in result.output or "✅" in result.output
        
        # Verify template file was created
        template_dir = tmp_path / ".doc-evergreen" / "templates"
        # Template name is from filename, not title: README.md -> readme-reversed.json
        template_file = template_dir / "readme-reversed.json"
        
        assert template_file.exists(), f"Template not found at {template_file}"
        
        # Verify template structure
        with open(template_file) as f:
            template = json.load(f)
        
        assert '_meta' in template
        assert 'document' in template
        assert template['document']['title'] == 'My Project'
        assert len(template['document']['sections']) == 3
    
    def test_reverse_command_with_custom_output_path(self, tmp_path):
        """
        Given: README and custom output path
        When: Run reverse with --output flag
        Then: Saves template to specified path
        """
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("# Test\n\n## Section 1\n\nContent")
        
        custom_output = tmp_path / "custom" / "my-template.json"
        
        # ACT
        runner = CliRunner()
        result = runner.invoke(cli, [
            'reverse',
            str(readme),
            '--output', str(custom_output)
        ])
        
        # ASSERT
        assert result.exit_code == 0
        assert custom_output.exists()
    
    def test_reverse_command_shows_progress_output(self, tmp_path):
        """
        Given: README to reverse
        When: Run reverse command
        Then: Shows progress messages for each step
        """
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("# Project\n\n## Section 1\n\nContent")
        
        # ACT
        runner = CliRunner()
        result = runner.invoke(cli, ['reverse', str(readme)])
        
        # ASSERT
        assert result.exit_code == 0
        output = result.output
        
        # Should show progress steps
        assert "Analyzing" in output or "🔍" in output
        assert "Found" in output or "📝" in output
        assert "Template generated" in output or "✅" in output
    
    def test_reverse_command_handles_missing_file(self, tmp_path):
        """
        Given: Non-existent file path
        When: Run reverse command
        Then: Shows error message and exits with error code
        """
        # ARRANGE
        missing_file = tmp_path / "nonexistent.md"
        
        # ACT
        runner = CliRunner()
        result = runner.invoke(cli, ['reverse', str(missing_file)])
        
        # ASSERT
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "does not exist" in result.output.lower()
    
    def test_reverse_command_end_to_end_workflow(self, tmp_path):
        """
        Given: Complete project structure with README
        When: Run reverse to generate template, then verify it's usable
        Then: Template can be parsed and validated
        """
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("""# Complete Project

Full documentation example.

## Installation

Install instructions here.

## API Reference

API documentation.

### Authentication

Auth details.

## Contributing

How to contribute.
""")
        
        # Create realistic project structure
        (tmp_path / "setup.py").write_text("from setuptools import setup")
        (tmp_path / "CONTRIBUTING.md").write_text("# Contributing Guide")
        
        src = tmp_path / "src"
        src.mkdir()
        (src / "api.py").write_text("# API module")
        (src / "auth.py").write_text("# Auth module")
        
        # ACT
        runner = CliRunner()
        result = runner.invoke(cli, ['reverse', str(readme)])
        
        # ASSERT - Command succeeded
        assert result.exit_code == 0
        
        # ASSERT - Template exists and is valid
        template_dir = tmp_path / ".doc-evergreen" / "templates"
        # Template name from filename: README.md -> readme-reversed.json
        template_file = template_dir / "readme-reversed.json"
        assert template_file.exists()
        
        with open(template_file) as f:
            template = json.load(f)
        
        # Verify complete structure
        assert template['_meta']['name'] == 'readme-reversed'
        assert template['_meta']['quadrant'] == 'explanation'
        
        doc = template['document']
        assert doc['title'] == 'Complete Project'
        assert doc['output'] == 'README.md'
        assert len(doc['sections']) >= 3
        
        # Verify sections have required fields
        for section in doc['sections']:
            assert 'heading' in section
            assert 'prompt' in section
            assert 'sources' in section
            assert section['heading'].startswith('##')
        
        # Verify nested sections preserved
        api_section = next(s for s in doc['sections'] if 'API' in s['heading'])
        if 'sections' in api_section and api_section['sections']:
            assert api_section['sections'][0]['heading'].startswith('###')
    
    def test_reverse_command_discovers_sources_automatically(self, tmp_path):
        """
        Given: Project with various source files
        When: Run reverse command
        Then: Automatically discovers and maps sources to sections
        """
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("""# Project

## Installation

Install guide.

## API Reference

API docs.
""")
        
        # Create discoverable sources
        (tmp_path / "setup.py").write_text("# setup")
        (tmp_path / "requirements.txt").write_text("# requirements")
        
        src = tmp_path / "src"
        src.mkdir()
        (src / "api.py").write_text("# API")
        
        # ACT
        runner = CliRunner()
        result = runner.invoke(cli, ['reverse', str(readme)])
        
        # ASSERT
        assert result.exit_code == 0
        
        # Template name from filename: README.md -> readme-reversed.json
        template_file = tmp_path / ".doc-evergreen" / "templates" / "readme-reversed.json"
        with open(template_file) as f:
            template = json.load(f)
        
        sections = template['document']['sections']
        
        # Installation section should have setup.py, requirements.txt
        install_section = next(s for s in sections if 'Installation' in s['heading'])
        assert len(install_section['sources']) > 0
        assert any('setup.py' in src for src in install_section['sources'])
        
        # API section should have api.py
        api_section = next(s for s in sections if 'API' in s['heading'])
        assert len(api_section['sources']) > 0
        assert any('api.py' in src for src in api_section['sources'])
