"""Tests for file relevance analysis."""

import json
from pathlib import Path

import pytest

from doc_evergreen.generate.doc_type import DocType
from doc_evergreen.generate.intent_context import IntentContext
from doc_evergreen.generate.repo_indexer import FileEntry, FileIndex, FileType
from doc_evergreen.generate.relevance_analyzer import (
    RelevanceAnalyzer,
    RelevanceScore,
    RelevanceNotes,
    FilePreview,
)


class TestFilePreview:
    """Test file preview generation."""

    def test_extracts_preview_from_file(self, tmp_path):
        """Should extract preview from file."""
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        file_path = tmp_path / "test.txt"
        file_path.write_text(content)
        
        preview = FilePreview.extract(file_path, max_chars=20)
        
        assert len(preview) <= 20
        assert preview.startswith("Line 1")

    def test_handles_empty_file(self, tmp_path):
        """Should handle empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")
        
        preview = FilePreview.extract(file_path)
        
        assert preview == ""

    def test_truncates_long_content(self, tmp_path):
        """Should truncate to max_chars."""
        content = "x" * 1000
        file_path = tmp_path / "long.txt"
        file_path.write_text(content)
        
        preview = FilePreview.extract(file_path, max_chars=100)
        
        assert len(preview) == 100


class TestRelevanceScore:
    """Test relevance score dataclass."""

    def test_creates_relevance_score(self):
        """Should create relevance score."""
        score = RelevanceScore(
            file_path="src/main.py",
            score=85,
            reasoning="Contains main entry point",
            key_material="Entry point logic, CLI setup",
        )
        
        assert score.file_path == "src/main.py"
        assert score.score == 85
        assert "entry point" in score.reasoning.lower()
        assert "CLI setup" in score.key_material

    def test_to_dict_method(self):
        """Should convert to dict."""
        score = RelevanceScore(
            file_path="README.md",
            score=75,
            reasoning="Project overview",
            key_material="Description, usage",
        )
        
        data = score.to_dict()
        
        assert data["file"] == "README.md"
        assert data["score"] == 75
        assert data["reasoning"] == "Project overview"
        assert data["key_material"] == "Description, usage"


class TestRelevanceAnalyzer:
    """Test relevance analyzer."""

    @pytest.fixture
    def context(self, tmp_path):
        """Create test intent context."""
        return IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="Help developers get started quickly",
            output_path="README.md",
        )

    @pytest.fixture
    def file_index(self, tmp_path):
        """Create test file index."""
        # Create test files
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main():\n    print('Hello')")
        (tmp_path / "README.md").write_text("# My Project\n\nGetting started guide")
        (tmp_path / "test_app.py").write_text("def test_main():\n    pass")
        
        files = [
            FileEntry(
                tmp_path / "src" / "main.py",
                "src/main.py",
                100,
                ".py",
                FileType.SOURCE_CODE,
            ),
            FileEntry(
                tmp_path / "README.md",
                "README.md",
                200,
                ".md",
                FileType.DOCUMENTATION,
            ),
            FileEntry(
                tmp_path / "test_app.py",
                "test_app.py",
                50,
                ".py",
                FileType.TEST,
            ),
        ]
        
        return FileIndex(project_root=tmp_path, files=files)

    def test_creates_analyzer(self, context, file_index):
        """Should create analyzer."""
        analyzer = RelevanceAnalyzer(context=context, file_index=file_index)
        
        assert analyzer.context == context
        assert analyzer.file_index == file_index

    def test_analyzes_files_for_relevance(self, context, file_index):
        """Should analyze files and return scores."""
        analyzer = RelevanceAnalyzer(context=context, file_index=file_index)
        scores = analyzer.analyze()
        
        assert len(scores) > 0
        assert all(isinstance(s, RelevanceScore) for s in scores)

    def test_filters_by_threshold(self, context, file_index):
        """Should filter out low-scoring files."""
        analyzer = RelevanceAnalyzer(
            context=context,
            file_index=file_index,
            threshold=50,
        )
        scores = analyzer.analyze()
        
        # All returned scores should be above threshold
        assert all(s.score >= 50 for s in scores)

    def test_prefers_documentation_for_tutorial(self, context, file_index):
        """Should score documentation higher for tutorial."""
        analyzer = RelevanceAnalyzer(context=context, file_index=file_index)
        scores = analyzer.analyze()
        
        # Find README.md score
        readme_score = next(s for s in scores if "README" in s.file_path)
        
        # Should have decent relevance for tutorial
        assert readme_score.score > 0

    def test_scores_source_code_appropriately(self, context, file_index):
        """Should score source code based on purpose."""
        analyzer = RelevanceAnalyzer(context=context, file_index=file_index)
        scores = analyzer.analyze()
        
        # Source files should be scored
        source_scores = [s for s in scores if s.file_path.endswith(".py") and "test" not in s.file_path]
        assert len(source_scores) > 0

    def test_provides_reasoning_for_scores(self, context, file_index):
        """Should provide reasoning for each score."""
        analyzer = RelevanceAnalyzer(context=context, file_index=file_index)
        scores = analyzer.analyze()
        
        for score in scores:
            assert score.reasoning
            assert len(score.reasoning) > 10

    def test_identifies_key_material(self, context, file_index):
        """Should identify key material in relevant files."""
        analyzer = RelevanceAnalyzer(context=context, file_index=file_index)
        scores = analyzer.analyze()
        
        # High-scoring files should have key material identified
        high_scores = [s for s in scores if s.score >= 70]
        for score in high_scores:
            assert score.key_material
            assert len(score.key_material) > 5


class TestRelevanceNotes:
    """Test relevance notes persistence."""

    def test_creates_relevance_notes(self):
        """Should create relevance notes."""
        scores = [
            RelevanceScore("src/main.py", 85, "Main entry", "CLI logic"),
            RelevanceScore("README.md", 75, "Project docs", "Overview"),
        ]
        
        notes = RelevanceNotes(
            doc_type="tutorial",
            purpose="Getting started",
            relevant_files=scores,
            total_files_analyzed=10,
            threshold=50,
        )
        
        assert notes.doc_type == "tutorial"
        assert notes.purpose == "Getting started"
        assert len(notes.relevant_files) == 2
        assert notes.total_files_analyzed == 10

    def test_counts_relevant_files(self):
        """Should count relevant files."""
        scores = [
            RelevanceScore("a.py", 80, "R1", "M1"),
            RelevanceScore("b.py", 70, "R2", "M2"),
        ]
        
        notes = RelevanceNotes(
            doc_type="tutorial",
            purpose="Test",
            relevant_files=scores,
            total_files_analyzed=5,
            threshold=50,
        )
        
        assert notes.relevant_files_count == 2

    def test_to_dict_method(self):
        """Should convert to dict."""
        scores = [
            RelevanceScore("src/main.py", 85, "Main entry", "CLI logic"),
        ]
        
        notes = RelevanceNotes(
            doc_type="tutorial",
            purpose="Getting started",
            relevant_files=scores,
            total_files_analyzed=10,
            threshold=50,
        )
        
        data = notes.to_dict()
        
        assert data["doc_type"] == "tutorial"
        assert data["purpose"] == "Getting started"
        assert data["relevant_files_count"] == 1
        assert data["total_files_analyzed"] == 10
        assert data["threshold"] == 50
        assert len(data["relevant_files"]) == 1

    def test_saves_to_json(self, tmp_path):
        """Should save to JSON file."""
        scores = [
            RelevanceScore("src/main.py", 85, "Main entry", "CLI logic"),
        ]
        
        notes = RelevanceNotes(
            doc_type="tutorial",
            purpose="Getting started",
            relevant_files=scores,
            total_files_analyzed=10,
            threshold=50,
        )
        
        output_path = tmp_path / "relevance_notes.json"
        notes.save(output_path)
        
        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data["relevant_files_count"] == 1

    def test_loads_from_json(self, tmp_path):
        """Should load from JSON file."""
        scores = [
            RelevanceScore("src/main.py", 85, "Main entry", "CLI logic"),
        ]
        
        original = RelevanceNotes(
            doc_type="tutorial",
            purpose="Getting started",
            relevant_files=scores,
            total_files_analyzed=10,
            threshold=50,
        )
        
        output_path = tmp_path / "relevance_notes.json"
        original.save(output_path)
        
        loaded = RelevanceNotes.load(output_path)
        
        assert loaded.doc_type == "tutorial"
        assert loaded.relevant_files_count == 1
        assert loaded.relevant_files[0].file_path == "src/main.py"


class TestRelevanceAnalysisIntegration:
    """Integration tests for relevance analysis."""

    def test_end_to_end_analysis(self, tmp_path):
        """Test complete relevance analysis workflow."""
        # Create test files
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "cli.py").write_text("import click\n\ndef main():\n    click.echo('Hello')")
        (tmp_path / "README.md").write_text("# Tutorial\n\nGetting started with the CLI tool")
        (tmp_path / "config.yaml").write_text("name: myapp\nversion: 1.0")
        
        # Create context
        context = IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="Help developers use the CLI tool",
            output_path="TUTORIAL.md",
        )
        
        # Create file index
        files = [
            FileEntry(tmp_path / "src" / "cli.py", "src/cli.py", 100, ".py", FileType.SOURCE_CODE),
            FileEntry(tmp_path / "README.md", "README.md", 200, ".md", FileType.DOCUMENTATION),
            FileEntry(tmp_path / "config.yaml", "config.yaml", 50, ".yaml", FileType.CONFIG),
        ]
        file_index = FileIndex(project_root=tmp_path, files=files)
        
        # Analyze relevance
        analyzer = RelevanceAnalyzer(context=context, file_index=file_index)
        scores = analyzer.analyze()
        
        # Should have relevant files
        assert len(scores) > 0
        
        # Create and save notes
        notes = RelevanceNotes(
            doc_type=context.doc_type.value,
            purpose=context.purpose,
            relevant_files=scores,
            total_files_analyzed=len(file_index.files),
            threshold=50,
        )
        
        output_path = tmp_path / "relevance_notes.json"
        notes.save(output_path)
        
        # Load and verify
        loaded = RelevanceNotes.load(output_path)
        assert loaded.relevant_files_count > 0
