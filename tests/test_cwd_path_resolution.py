"""Test that source paths are resolved relative to cwd, not template location."""

import json
import os
from pathlib import Path

import pytest

from doc_evergreen.chunked_generator import ChunkedGenerator
from doc_evergreen.core.template_schema import parse_template
from doc_evergreen.core.source_validator import validate_all_sources, SourceValidationError


class TestCwdPathResolution:
    """Test convention-based path resolution (cwd = project root)."""

    def test_sources_resolved_from_cwd_not_template_directory(self, tmp_path):
        """
        Given: Template in one directory, sources in another
        When: Source validation runs with base_dir = cwd
        Then: Sources found from cwd, NOT from template directory
        """
        # ARRANGE: Create project with source file
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        source_dir = project_dir / "src"
        source_dir.mkdir()

        source_file = source_dir / "code.py"
        source_file.write_text("def hello():\n    return 'world'\n")

        # Template in DIFFERENT location
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        template_file = template_dir / "doc.json"
        template_data = {
            "document": {
                "title": "Test Documentation",
                "output": "output.md",
                "sections": [
                    {
                        "heading": "# Test",
                        "prompt": "Document the code",
                        "sources": ["src/code.py"],  # Relative path
                    }
                ],
            }
        }
        template_file.write_text(json.dumps(template_data, indent=2))

        # Parse template
        template = parse_template(template_file)

        # ACT: Test with cwd as base_dir (CORRECT behavior)
        original_cwd = Path.cwd()
        try:
            os.chdir(project_dir)

            # This is what cli.py SHOULD do: base_dir = Path.cwd()
            validation_cwd = validate_all_sources(template, base_dir=Path.cwd())

            # This is what cli.py USED TO do (wrong): base_dir = Path(template_path).parent
            # Should raise error because sources don't exist at template location
            template_raised_error = False
            try:
                validation_template = validate_all_sources(template, base_dir=template_file.parent)
            except SourceValidationError:
                template_raised_error = True
        finally:
            os.chdir(original_cwd)

        # ASSERT: With cwd base_dir, sources SHOULD be found
        assert validation_cwd.valid, (
            f"With base_dir=cwd ({project_dir}), should find src/code.py"
        )
        assert len(validation_cwd.section_sources) > 0

        # ASSERT: With template base_dir, should raise error (no sources found)
        assert template_raised_error, (
            f"With base_dir=template.parent ({template_dir}), should raise error "
            f"because src/code.py doesn't exist at {template_dir}/src/code.py"
        )

    def test_nested_template_location_ignored(self, tmp_path):
        """
        Given: Deeply nested template location, flat source structure
        When: Validation with base_dir = cwd
        Then: Sources found from cwd, template nesting irrelevant
        """
        # ARRANGE: Flat source at cwd
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        source_file = project_dir / "main.py"
        source_file.write_text("# Main file\n")

        # Deeply nested template
        nested_template_dir = tmp_path / "a" / "b" / "c" / "templates"
        nested_template_dir.mkdir(parents=True)

        template_file = nested_template_dir / "doc.json"
        template_data = {
            "document": {
                "title": "Test Documentation",
                "output": "output.md",
                "sections": [
                    {
                        "heading": "# Test",
                        "prompt": "Document main.py",
                        "sources": ["main.py"],
                    }
                ],
            }
        }
        template_file.write_text(json.dumps(template_data, indent=2))

        # Parse template
        template = parse_template(template_file)

        # ACT: Test from project root
        original_cwd = Path.cwd()
        try:
            os.chdir(project_dir)

            # With cwd: should find main.py at project_dir/main.py
            validation_cwd = validate_all_sources(template, base_dir=Path.cwd())

            # With template parent: would look at .../c/templates/main.py (doesn't exist)
            template_raised_error = False
            try:
                validation_template = validate_all_sources(template, base_dir=template_file.parent)
            except SourceValidationError:
                template_raised_error = True
        finally:
            os.chdir(original_cwd)

        # ASSERT: cwd finds it, template location raises error
        assert validation_cwd.valid, f"Should find main.py from cwd: {project_dir}"
        assert template_raised_error, f"Should raise error from template dir: {template_file.parent}"
