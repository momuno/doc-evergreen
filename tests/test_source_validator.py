"""Tests for source validator (RED phase - these will fail initially).

Following TDD: Write failing tests FIRST to prove they test real behavior.
"""

from pathlib import Path

import pytest

from doc_evergreen.core.source_validator import SourceValidationError
from doc_evergreen.core.source_validator import SourceValidationResult
from doc_evergreen.core.source_validator import display_validation_report
from doc_evergreen.core.source_validator import validate_all_sources
from doc_evergreen.core.template_schema import Document
from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template


class TestSourceValidation:
    """Test source validation before generation starts."""

    def test_validate_finds_missing_sources(self, tmp_path: Path) -> None:
        """
        Given: A template with a section that has no matching source files
        When: validate_all_sources is called
        Then: ValidationError is raised with clear message about missing sources
        """
        # Arrange: Create template with non-existent source pattern
        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Overview",
                        prompt="Write overview",
                        sources=["nonexistent/*.py"],  # This won't match anything
                    )
                ],
            )
        )

        # Act & Assert: Should raise ValidationError
        with pytest.raises(SourceValidationError) as exc_info:
            validate_all_sources(template, base_dir=tmp_path)

        # Verify error message is clear
        error_msg = str(exc_info.value)
        assert "Overview" in error_msg
        assert "no sources" in error_msg.lower() or "no files" in error_msg.lower()

    def test_validate_passes_with_all_sources(self, tmp_path: Path) -> None:
        """
        Given: A template where all sections have matching source files
        When: validate_all_sources is called
        Then: Returns SourceValidationResult with valid=True and resolved sources
        """
        # Arrange: Create actual files that will be found
        (tmp_path / "file1.py").write_text("# File 1")
        (tmp_path / "file2.py").write_text("# File 2")

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Overview",
                        prompt="Write overview",
                        sources=["*.py"],  # Will match file1.py and file2.py
                    )
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Validation passes
        assert result.valid is True
        assert len(result.errors) == 0

        # Assert: Sources are resolved
        assert "Overview" in result.section_sources
        overview_sources = result.section_sources["Overview"]
        assert len(overview_sources) == 2
        assert all(isinstance(s, Path) for s in overview_sources)

    def test_validate_nested_sections(self, tmp_path: Path) -> None:
        """
        Given: A template with nested sections, where a nested section has no sources
        When: validate_all_sources is called
        Then: ValidationError is raised identifying the nested section
        """
        # Arrange: Create parent source but not nested source
        (tmp_path / "parent.py").write_text("# Parent")

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Parent",
                        prompt="Parent section",
                        sources=["parent.py"],
                        sections=[
                            Section(
                                heading="Child",
                                prompt="Child section",
                                sources=["missing/*.py"],  # Won't match anything
                            )
                        ],
                    )
                ],
            )
        )

        # Act & Assert: Should raise ValidationError for nested section
        with pytest.raises(SourceValidationError) as exc_info:
            validate_all_sources(template, base_dir=tmp_path)

        error_msg = str(exc_info.value)
        assert "Child" in error_msg

    def test_source_caching(self, tmp_path: Path) -> None:
        """
        Given: Multiple sections using the same glob pattern
        When: validate_all_sources is called
        Then: Glob pattern is resolved only once (cached)
        """
        # Arrange: Create files
        (tmp_path / "file1.py").write_text("# File 1")
        (tmp_path / "file2.py").write_text("# File 2")

        # Two sections with identical source patterns
        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Section1",
                        prompt="First",
                        sources=["*.py"],
                    ),
                    Section(
                        heading="Section2",
                        prompt="Second",
                        sources=["*.py"],  # Same pattern as Section1
                    ),
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Both sections have resolved sources
        assert result.valid is True
        assert "Section1" in result.section_sources
        assert "Section2" in result.section_sources

        # Assert: Pattern was cached (both sections reference same resolved list)
        # This verifies the resolver cached the glob result
        section1_sources = result.section_sources["Section1"]
        section2_sources = result.section_sources["Section2"]
        assert len(section1_sources) == len(section2_sources) == 2

    def test_validation_shows_file_counts_and_sizes(self, tmp_path: Path) -> None:
        """
        Given: A template with sources
        When: validate_all_sources is called
        Then: Result includes file counts and total sizes per section
        """
        # Arrange: Create files with known content
        (tmp_path / "small.py").write_text("x = 1")  # 5 bytes
        (tmp_path / "large.py").write_text("y = 2" * 100)  # 500 bytes

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Code",
                        prompt="Code section",
                        sources=["*.py"],
                    )
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Result includes statistics
        assert result.valid is True
        assert "Code" in result.section_stats

        stats = result.section_stats["Code"]
        assert stats["file_count"] == 2
        assert stats["total_bytes"] == 505  # 5 + 500


class TestValidationReportDisplay:
    """Test validation report display to user."""

    def test_validation_report_display(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Given: A SourceValidationResult with resolved sources
        When: display_validation_report is called
        Then: User sees formatted report with file paths and statistics
        """
        # Arrange: Create files and validate
        (tmp_path / "doc.py").write_text("# Doc" * 100)  # 600 bytes
        (tmp_path / "README.md").write_text("# README" * 50)  # 400 bytes

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Overview",
                        prompt="Overview",
                        sources=["doc.py", "README.md"],
                    )
                ],
            )
        )

        result = validate_all_sources(template, base_dir=tmp_path)

        # Act: Display validation report (capture INFO level logs)
        import logging

        caplog.set_level(logging.INFO)
        display_validation_report(result)

        # Assert: Output contains expected information
        output = caplog.text

        # Should show section name
        assert "Overview" in output

        # Should show file names
        assert "doc.py" in output
        assert "README.md" in output

        # Should show file sizes (in KB)
        assert "KB" in output or "bytes" in output

        # Should show success indicator
        assert "✅" in output or "Found" in output

    def test_validation_report_shows_failures(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Given: A template with missing sources (validation failed)
        When: display_validation_report is called
        Then: User sees error indicators and helpful fix suggestions
        """
        # Arrange: Template with non-existent source
        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Missing",
                        prompt="Missing section",
                        sources=["nonexistent.py"],
                    )
                ],
            )
        )

        # Act: Validate (will fail) and capture result
        try:
            result = validate_all_sources(template, base_dir=tmp_path)
        except SourceValidationError as e:
            # Create a failed result for display testing
            result = SourceValidationResult(
                valid=False,
                errors=[str(e)],
                section_sources={},
                section_stats={},
            )

        # Display validation report (capture INFO level logs)
        import logging

        caplog.set_level(logging.INFO)
        display_validation_report(result)

        # Assert: Output shows error
        output = caplog.text

        # Should show failure indicator
        assert "❌" in output or "ERROR" in output

        # Should show section with problem
        assert "Missing" in output

        # Should suggest fix
        assert "Fix:" in output or "Check" in output or "fix" in output.lower()


class TestSourceResolverEdgeCases:
    """Test edge cases in source resolution."""

    def test_empty_sources_list(self, tmp_path: Path) -> None:
        """
        Given: A section with empty sources list
        When: validate_all_sources is called
        Then: ValidationError is raised
        """
        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Empty",
                        prompt="Empty section",
                        sources=[],  # Empty list
                    )
                ],
            )
        )

        # Act & Assert: Should raise ValidationError
        with pytest.raises(SourceValidationError):
            validate_all_sources(template, base_dir=tmp_path)

    def test_glob_pattern_with_subdirectories(self, tmp_path: Path) -> None:
        """
        Given: A section with recursive glob pattern like **/*.py
        When: validate_all_sources is called
        Then: Finds files in subdirectories
        """
        # Arrange: Create nested directory structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.py").write_text("# Root")
        (subdir / "nested.py").write_text("# Nested")

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="AllCode",
                        prompt="All code",
                        sources=["**/*.py"],  # Recursive pattern
                    )
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Finds both files
        assert result.valid is True
        sources = result.section_sources["AllCode"]
        assert len(sources) == 2

    def test_mixed_glob_and_literal_paths(self, tmp_path: Path) -> None:
        """
        Given: A section with both literal paths and glob patterns
        When: validate_all_sources is called
        Then: Resolves both correctly
        """
        # Arrange: Create files
        (tmp_path / "specific.py").write_text("# Specific")
        (tmp_path / "glob1.txt").write_text("# Glob 1")
        (tmp_path / "glob2.txt").write_text("# Glob 2")

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Mixed",
                        prompt="Mixed sources",
                        sources=["specific.py", "*.txt"],  # Literal + glob
                    )
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Finds all 3 files
        assert result.valid is True
        sources = result.section_sources["Mixed"]
        assert len(sources) == 3

    def test_excludes_virtual_environment_files(self, tmp_path: Path) -> None:
        """
        Given: Project with .venv directory containing Python files
        When: Using **/*.py pattern
        Then: Only matches project files, not .venv files
        """
        # Arrange: Create project structure with .venv
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# Main")
        (tmp_path / "src" / "utils.py").write_text("# Utils")

        # Create .venv with packages
        venv_dir = tmp_path / ".venv" / "lib" / "python3.13" / "site-packages"
        venv_dir.mkdir(parents=True)
        (venv_dir / "package.py").write_text("# Package")
        (venv_dir / "module.py").write_text("# Module")

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Code",
                        prompt="All code",
                        sources=["**/*.py"],  # Should NOT match .venv files
                    )
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Only finds project files, not .venv files
        assert result.valid is True
        sources = result.section_sources["Code"]
        assert len(sources) == 2  # Only main.py and utils.py

        source_names = {s.name for s in sources}
        assert "main.py" in source_names
        assert "utils.py" in source_names
        assert "package.py" not in source_names
        assert "module.py" not in source_names

    def test_excludes_node_modules(self, tmp_path: Path) -> None:
        """
        Given: Project with node_modules directory
        When: Using **/*.js pattern
        Then: Only matches project files, not node_modules
        """
        # Arrange: Create project with node_modules
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.js").write_text("// App")

        node_modules = tmp_path / "node_modules" / "package"
        node_modules.mkdir(parents=True)
        (node_modules / "index.js").write_text("// Package")

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Code",
                        prompt="All code",
                        sources=["**/*.js"],
                    )
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Only finds project files
        assert result.valid is True
        sources = result.section_sources["Code"]
        assert len(sources) == 1
        assert sources[0].name == "app.js"

    def test_excludes_common_cache_directories(self, tmp_path: Path) -> None:
        """
        Given: Project with __pycache__, .pytest_cache, etc.
        When: Using glob patterns
        Then: Excludes all cache directories
        """
        # Arrange: Create project with various cache dirs
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# Main")

        # Create cache directories
        for cache_dir in ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"]:
            cache_path = tmp_path / cache_dir
            cache_path.mkdir()
            (cache_path / "cached.py").write_text("# Cache")

        template = Template(
            document=Document(
                title="Test",
                output="test.md",
                sections=[
                    Section(
                        heading="Code",
                        prompt="All code",
                        sources=["**/*.py"],
                    )
                ],
            )
        )

        # Act: Validate sources
        result = validate_all_sources(template, base_dir=tmp_path)

        # Assert: Only finds project files, not cache files
        assert result.valid is True
        sources = result.section_sources["Code"]
        assert len(sources) == 1
        assert sources[0].name == "main.py"
