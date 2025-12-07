"""Tests for document generation (Sprint 6)."""

from pathlib import Path

import pytest

from doc_evergreen.generate.outline_generator import (
    Section,
    SourceReference,
    DocumentOutline,
)
from doc_evergreen.generate.doc_generator import DocumentGenerator


class TestDocumentGenerator:
    """Test document generator."""

    def test_creates_generator(self, tmp_path):
        """Should create document generator."""
        generator = DocumentGenerator(project_root=tmp_path)
        assert generator.project_root == tmp_path

    def test_generates_from_outline(self, tmp_path):
        """Should generate document from outline."""
        # Create simple outline
        section = Section(
            heading="# Introduction",
            level=1,
            prompt="Write an introduction",
            sources=[],
            sections=[],
        )
        
        outline = DocumentOutline(
            title="Test Document",
            output_path="TEST.md",
            doc_type="tutorial",
            purpose="Test purpose",
            sections=[section],
        )
        
        # Save outline
        outline_path = tmp_path / "outline.json"
        outline.save(outline_path)
        
        # Generate document
        generator = DocumentGenerator(project_root=tmp_path)
        content = generator.generate_from_outline(outline_path)
        
        # Should have content
        assert len(content) > 0
        assert "Test Document" in content

    def test_includes_section_headings(self, tmp_path):
        """Should include all section headings."""
        sections = [
            Section("# Introduction", 1, "Intro prompt", [], []),
            Section("# Getting Started", 1, "Getting started prompt", [], []),
        ]
        
        outline = DocumentOutline(
            title="Test Doc",
            output_path="TEST.md",
            doc_type="tutorial",
            purpose="Test",
            sections=sections,
        )
        
        outline_path = tmp_path / "outline.json"
        outline.save(outline_path)
        
        generator = DocumentGenerator(project_root=tmp_path)
        content = generator.generate_from_outline(outline_path)
        
        assert "# Introduction" in content
        assert "# Getting Started" in content

    def test_handles_nested_sections(self, tmp_path):
        """Should handle nested section structure."""
        subsection = Section(
            heading="## Installation",
            level=2,
            prompt="Installation steps",
            sources=[],
            sections=[],
        )
        
        parent = Section(
            heading="# Getting Started",
            level=1,
            prompt="Getting started intro",
            sources=[],
            sections=[subsection],
        )
        
        outline = DocumentOutline(
            title="Test Doc",
            output_path="TEST.md",
            doc_type="tutorial",
            purpose="Test",
            sections=[parent],
        )
        
        outline_path = tmp_path / "outline.json"
        outline.save(outline_path)
        
        generator = DocumentGenerator(project_root=tmp_path)
        content = generator.generate_from_outline(outline_path)
        
        # Should have both parent and subsection
        assert "# Getting Started" in content
        assert "## Installation" in content

    def test_shows_source_references(self, tmp_path):
        """Should show source references in content."""
        sources = [
            SourceReference("src/main.py", "Main entry point"),
            SourceReference("README.md", "Project overview"),
        ]
        
        section = Section(
            heading="# Overview",
            level=1,
            prompt="Write overview",
            sources=sources,
            sections=[],
        )
        
        outline = DocumentOutline(
            title="Test Doc",
            output_path="TEST.md",
            doc_type="tutorial",
            purpose="Test",
            sections=[section],
        )
        
        outline_path = tmp_path / "outline.json"
        outline.save(outline_path)
        
        generator = DocumentGenerator(project_root=tmp_path)
        content = generator.generate_from_outline(outline_path)
        
        # Should mention source files
        assert "src/main.py" in content or "Sources used" in content

    def test_writes_to_output_file(self, tmp_path):
        """Should write generated content to file."""
        section = Section("# Test", 1, "Test prompt", [], [])
        
        outline = DocumentOutline(
            title="Test Doc",
            output_path="OUTPUT.md",
            doc_type="tutorial",
            purpose="Test",
            sections=[section],
        )
        
        outline_path = tmp_path / "outline.json"
        outline.save(outline_path)
        
        generator = DocumentGenerator(project_root=tmp_path)
        generator.generate_from_outline(outline_path)
        
        # Output file should exist
        output_file = tmp_path / "OUTPUT.md"
        assert output_file.exists()
        
        # Should have content
        content = output_file.read_text()
        assert len(content) > 0
        assert "Test Doc" in content

    def test_preserves_section_order(self, tmp_path):
        """Should preserve section order."""
        sections = [
            Section("# First", 1, "First", [], []),
            Section("# Second", 1, "Second", [], []),
            Section("# Third", 1, "Third", [], []),
        ]
        
        outline = DocumentOutline(
            title="Test Doc",
            output_path="TEST.md",
            doc_type="tutorial",
            purpose="Test",
            sections=sections,
        )
        
        outline_path = tmp_path / "outline.json"
        outline.save(outline_path)
        
        generator = DocumentGenerator(project_root=tmp_path)
        content = generator.generate_from_outline(outline_path)
        
        # Check order
        first_pos = content.index("# First")
        second_pos = content.index("# Second")
        third_pos = content.index("# Third")
        
        assert first_pos < second_pos < third_pos


class TestDocumentGenerationIntegration:
    """Integration tests for document generation."""

    def test_end_to_end_document_generation(self, tmp_path):
        """Test complete document generation workflow."""
        # Create nested outline
        subsections = [
            Section("## Installation", 2, "Install steps", 
                   [SourceReference("package.json", "Dependencies")], []),
            Section("## Quick Start", 2, "First example",
                   [SourceReference("README.md", "Examples")], []),
        ]
        
        sections = [
            Section("# Introduction", 1, "Intro", [], []),
            Section("# Getting Started", 1, "Getting started", [], subsections),
            Section("# Next Steps", 1, "Next steps", [], []),
        ]
        
        outline = DocumentOutline(
            title="Complete Tutorial",
            output_path="TUTORIAL.md",
            doc_type="tutorial",
            purpose="Help developers get started",
            sections=sections,
        )
        
        # Save outline
        outline_path = tmp_path / "outline.json"
        outline.save(outline_path)
        
        # Generate document
        generator = DocumentGenerator(project_root=tmp_path)
        content = generator.generate_from_outline(outline_path)
        
        # Verify structure
        assert "# Complete Tutorial" in content
        assert "# Introduction" in content
        assert "# Getting Started" in content
        assert "## Installation" in content
        assert "## Quick Start" in content
        assert "# Next Steps" in content
        
        # Verify file written
        output_file = tmp_path / "TUTORIAL.md"
        assert output_file.exists()
        
        # Verify order
        intro_pos = content.index("# Introduction")
        getting_started_pos = content.index("# Getting Started")
        installation_pos = content.index("## Installation")
        
        assert intro_pos < getting_started_pos < installation_pos
