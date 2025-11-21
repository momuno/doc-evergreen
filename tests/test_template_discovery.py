"""Tests for template discovery logic in resolve_template_path()."""

import os
from pathlib import Path

import pytest

# Import function - will be added to cli module
# Temporarily importing from future location to make test fail (RED phase)
try:
    from doc_evergreen.cli import resolve_template_path
except ImportError:
    # Function doesn't exist yet - test will fail appropriately
    resolve_template_path = None  # type: ignore


class TestTemplateDiscovery:
    """Tests for .doc-evergreen/ convention-based template discovery."""

    def test_discovers_template_from_convention_directory(self, tmp_path):
        """
        Given: Template in .doc-evergreen/ directory
        When: resolve_template_path called with short name
        Then: Template found in convention directory
        """
        # ARRANGE
        doc_evergreen = tmp_path / ".doc-evergreen"
        doc_evergreen.mkdir()
        template_file = doc_evergreen / "readme.json"
        template_file.write_text('{"document": {"title": "Test"}}')

        # ACT
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = resolve_template_path("readme")
        finally:
            os.chdir(original_cwd)

        # ASSERT
        assert result == template_file
        assert result.exists()

    def test_absolute_path_still_works(self, tmp_path):
        """
        Given: Template at absolute path
        When: resolve_template_path called with absolute path
        Then: Template found at that path
        """
        # ARRANGE
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        template_file = custom_dir / "doc.json"
        template_file.write_text('{"document": {"title": "Test"}}')

        # ACT
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = resolve_template_path(str(template_file))
        finally:
            os.chdir(original_cwd)

        # ASSERT
        assert result == template_file
        assert result.exists()

    def test_relative_path_works(self, tmp_path):
        """
        Given: Template at relative path
        When: resolve_template_path called with relative path
        Then: Template found relative to cwd
        """
        # ARRANGE
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        template_file = templates_dir / "doc.json"
        template_file.write_text('{"document": {"title": "Test"}}')

        # ACT
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = resolve_template_path("templates/doc.json")
        finally:
            os.chdir(original_cwd)

        # ASSERT
        assert result == template_file
        assert result.exists()

    def test_convention_takes_priority_over_relative(self, tmp_path):
        """
        Given: Template in both .doc-evergreen/ and as relative file
        When: resolve_template_path called with name (no .json)
        Then: Convention directory takes priority
        """
        # ARRANGE
        # Convention directory
        doc_evergreen = tmp_path / ".doc-evergreen"
        doc_evergreen.mkdir()
        convention_template = doc_evergreen / "readme.json"
        convention_template.write_text('{"source": "convention"}')

        # Relative path
        readme_file = tmp_path / "readme.json"
        readme_file.write_text('{"source": "relative"}')

        # ACT
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = resolve_template_path("readme")
        finally:
            os.chdir(original_cwd)

        # ASSERT
        assert result == convention_template
        assert '"source": "convention"' in result.read_text()

    def test_not_found_shows_helpful_error(self, tmp_path):
        """
        Given: Template doesn't exist
        When: resolve_template_path called
        Then: FileNotFoundError with helpful message showing what was tried
        """
        # ARRANGE - no templates

        # ACT & ASSERT
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(FileNotFoundError) as exc_info:
                resolve_template_path("nonexistent")

            error_msg = str(exc_info.value)
            assert "nonexistent" in error_msg
            assert ".doc-evergreen" in error_msg
            assert "init" in error_msg.lower()
        finally:
            os.chdir(original_cwd)

    def test_json_extension_tries_as_path_first(self, tmp_path):
        """
        Given: Name ends with .json, file exists at relative path
        When: resolve_template_path called
        Then: Finds file as path (not checking convention directory)
        """
        # ARRANGE
        # Relative path template
        template_file = tmp_path / "template.json"
        template_file.write_text('{"source": "path"}')

        # Also in convention dir (shouldn't be found)
        doc_evergreen = tmp_path / ".doc-evergreen"
        doc_evergreen.mkdir()
        convention_template = doc_evergreen / "template.json"
        convention_template.write_text('{"source": "convention"}')

        # ACT
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = resolve_template_path("template.json")
        finally:
            os.chdir(original_cwd)

        # ASSERT
        assert result == template_file
        assert '"source": "path"' in result.read_text()
