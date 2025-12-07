"""Tests for hierarchical outline generation (Sprint 4-5 CORE)."""

import json
from pathlib import Path

import pytest

from doc_evergreen.generate.doc_type import DocType
from doc_evergreen.generate.intent_context import IntentContext
from doc_evergreen.generate.relevance_analyzer import RelevanceScore
from doc_evergreen.generate.outline_generator import (
    OutlineGenerator,
    Section,
    DocumentOutline,
    SourceReference,
)


class TestSourceReference:
    """Test source reference with reasoning."""

    def test_creates_source_reference(self):
        """Should create source reference."""
        ref = SourceReference(
            file="src/main.py",
            reasoning="Contains main entry point logic",
        )
        
        assert ref.file == "src/main.py"
        assert "entry point" in ref.reasoning.lower()

    def test_to_dict_method(self):
        """Should convert to dict."""
        ref = SourceReference(
            file="README.md",
            reasoning="Project overview",
        )
        
        data = ref.to_dict()
        
        assert data["file"] == "README.md"
        assert data["reasoning"] == "Project overview"


class TestSection:
    """Test section with nesting."""

    def test_creates_section(self):
        """Should create section."""
        section = Section(
            heading="# Getting Started",
            level=1,
            prompt="Write introduction to getting started",
            sources=[],
            sections=[],
        )
        
        assert section.heading == "# Getting Started"
        assert section.level == 1
        assert section.prompt
        assert section.sources == []
        assert section.sections == []

    def test_creates_nested_section(self):
        """Should create section with subsections."""
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
            prompt="Introduction",
            sources=[],
            sections=[subsection],
        )
        
        assert len(parent.sections) == 1
        assert parent.sections[0].heading == "## Installation"

    def test_to_dict_method(self):
        """Should convert to dict recursively."""
        subsection = Section(
            heading="## Installation",
            level=2,
            prompt="Installation steps",
            sources=[SourceReference("package.json", "Dependencies")],
            sections=[],
        )
        
        parent = Section(
            heading="# Getting Started",
            level=1,
            prompt="Introduction",
            sources=[],
            sections=[subsection],
        )
        
        data = parent.to_dict()
        
        assert data["heading"] == "# Getting Started"
        assert data["level"] == 1
        assert len(data["sections"]) == 1
        assert data["sections"][0]["heading"] == "## Installation"


class TestDocumentOutline:
    """Test complete document outline."""

    def test_creates_document_outline(self):
        """Should create document outline."""
        section = Section("# Intro", 1, "Write intro", [], [])
        
        outline = DocumentOutline(
            title="My Tutorial",
            output_path="TUTORIAL.md",
            doc_type="tutorial",
            purpose="Help users get started",
            sections=[section],
        )
        
        assert outline.title == "My Tutorial"
        assert outline.output_path == "TUTORIAL.md"
        assert outline.doc_type == "tutorial"
        assert len(outline.sections) == 1

    def test_to_dict_includes_metadata(self):
        """Should include metadata in dict."""
        section = Section("# Intro", 1, "Write intro", [], [])
        
        outline = DocumentOutline(
            title="My Tutorial",
            output_path="TUTORIAL.md",
            doc_type="tutorial",
            purpose="Help users get started",
            sections=[section],
        )
        
        data = outline.to_dict()
        
        assert "_meta" in data
        assert data["_meta"]["generation_method"] == "forward"
        assert data["_meta"]["doc_type"] == "tutorial"
        assert "document" in data
        assert data["document"]["title"] == "My Tutorial"
        assert data["document"]["output"] == "TUTORIAL.md"

    def test_saves_to_json(self, tmp_path):
        """Should save to JSON file."""
        section = Section("# Intro", 1, "Write intro", [], [])
        
        outline = DocumentOutline(
            title="My Tutorial",
            output_path="TUTORIAL.md",
            doc_type="tutorial",
            purpose="Help users get started",
            sections=[section],
        )
        
        output_path = tmp_path / "outline.json"
        outline.save(output_path)
        
        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data["document"]["title"] == "My Tutorial"

    def test_loads_from_json(self, tmp_path):
        """Should load from JSON file."""
        section = Section("# Intro", 1, "Write intro", [], [])
        
        original = DocumentOutline(
            title="My Tutorial",
            output_path="TUTORIAL.md",
            doc_type="tutorial",
            purpose="Help users get started",
            sections=[section],
        )
        
        output_path = tmp_path / "outline.json"
        original.save(output_path)
        
        loaded = DocumentOutline.load(output_path)
        
        assert loaded.title == "My Tutorial"
        assert len(loaded.sections) == 1


class TestOutlineGenerator:
    """Test outline generator."""

    @pytest.fixture
    def context(self):
        """Create test context."""
        return IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="Help developers get started quickly",
            output_path="README.md",
        )

    @pytest.fixture
    def relevant_files(self):
        """Create test relevant files."""
        return [
            RelevanceScore(
                file_path="src/cli.py",
                score=85,
                reasoning="Main CLI entry point",
                key_material="Commands, usage",
            ),
            RelevanceScore(
                file_path="README.md",
                score=75,
                reasoning="Project overview",
                key_material="Description, examples",
            ),
        ]

    def test_creates_generator(self, context, relevant_files):
        """Should create outline generator."""
        generator = OutlineGenerator(
            context=context,
            relevant_files=relevant_files,
        )
        
        assert generator.context == context
        assert generator.relevant_files == relevant_files

    def test_generates_basic_outline(self, context, relevant_files):
        """Should generate basic outline structure."""
        generator = OutlineGenerator(context, relevant_files)
        outline = generator.generate()
        
        assert isinstance(outline, DocumentOutline)
        assert outline.title
        assert outline.doc_type == "tutorial"
        assert len(outline.sections) > 0

    def test_tutorial_has_getting_started_structure(self, context, relevant_files):
        """Tutorial should have getting started structure."""
        generator = OutlineGenerator(context, relevant_files)
        outline = generator.generate()
        
        # Should have sections appropriate for tutorial
        headings = [s.heading for s in outline.sections]
        # At least one section should be about getting started
        assert any("start" in h.lower() or "install" in h.lower() 
                   for h in headings)

    def test_sections_have_prompts(self, context, relevant_files):
        """All sections should have prompts."""
        generator = OutlineGenerator(context, relevant_files)
        outline = generator.generate()
        
        def check_prompts(sections):
            for section in sections:
                assert section.prompt
                assert len(section.prompt) > 20
                check_prompts(section.sections)
        
        check_prompts(outline.sections)

    def test_sections_have_source_mappings(self, context, relevant_files):
        """Sections should have relevant sources."""
        generator = OutlineGenerator(context, relevant_files)
        outline = generator.generate()
        
        # At least some sections should have sources
        def has_sources(sections):
            return any(len(s.sources) > 0 or has_sources(s.sections) 
                      for s in sections)
        
        assert has_sources(outline.sections)

    def test_creates_nested_structure(self, context, relevant_files):
        """Should create nested sections."""
        generator = OutlineGenerator(context, relevant_files, max_depth=2)
        outline = generator.generate()
        
        # Should have at least one section with subsections
        has_nesting = any(len(s.sections) > 0 for s in outline.sections)
        assert has_nesting

    def test_respects_max_depth(self, context, relevant_files):
        """Should not exceed max depth."""
        generator = OutlineGenerator(context, relevant_files, max_depth=2)
        outline = generator.generate()
        
        def check_depth(sections, current_depth):
            for section in sections:
                assert section.level <= current_depth
                if section.sections:
                    check_depth(section.sections, current_depth + 1)
        
        check_depth(outline.sections, 1)

    def test_parent_prompts_exclude_subsection_content(self, context, relevant_files):
        """Parent prompts should mention subsections."""
        generator = OutlineGenerator(context, relevant_files, max_depth=2)
        outline = generator.generate()
        
        # Find sections with subsections
        for section in outline.sections:
            if section.sections:
                # Parent prompt should mention not to cover subsection details
                prompt_lower = section.prompt.lower()
                # Should have some indication of subsections
                assert ("subsection" in prompt_lower or 
                        "below" in prompt_lower or
                        "section" in prompt_lower)


class TestOutlineGenerationIntegration:
    """Integration tests for outline generation."""

    def test_end_to_end_outline_generation(self, tmp_path):
        """Test complete outline generation workflow."""
        # Setup
        context = IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="Help developers use the CLI tool",
            output_path="TUTORIAL.md",
        )
        
        relevant_files = [
            RelevanceScore("src/cli.py", 90, "Main CLI", "Commands"),
            RelevanceScore("README.md", 80, "Overview", "Description"),
            RelevanceScore("config.yaml", 60, "Config", "Settings"),
        ]
        
        # Generate
        generator = OutlineGenerator(context, relevant_files)
        outline = generator.generate()
        
        # Verify structure
        assert outline.title
        assert len(outline.sections) >= 2
        
        # Save
        output_path = tmp_path / "outline.json"
        outline.save(output_path)
        
        # Load and verify
        loaded = DocumentOutline.load(output_path)
        assert loaded.title == outline.title
        assert len(loaded.sections) == len(outline.sections)
