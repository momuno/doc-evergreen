"""Tests for document metadata extraction (extract-intent command)."""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from doc_evergreen.extract.document_metadata import (
    DocumentMetadata,
    extract_document_metadata,
    load_metadata,
    save_metadata,
    _path_to_cache_filename,
    _parse_llm_response,
)
from doc_evergreen.generate.doc_type import DocType


class TestPathToCacheFilename:
    """Test conversion of document paths to cache filenames."""

    def test_simple_readme(self):
        """Given README.md, should return README.json."""
        assert _path_to_cache_filename("README.md") == "README.json"

    def test_nested_path(self):
        """Given docs/API.md, should return docs-API.json."""
        assert _path_to_cache_filename("docs/API.md") == "docs-API.json"

    def test_deep_nesting(self):
        """Given docs/guides/tutorial.md, should return docs-guides-tutorial.json."""
        assert _path_to_cache_filename("docs/guides/tutorial.md") == "docs-guides-tutorial.json"

    def test_no_extension(self):
        """Given path without extension, should still work."""
        assert _path_to_cache_filename("CONTRIBUTING") == "CONTRIBUTING.json"

    def test_non_md_extension(self):
        """Given .rst file, should strip extension."""
        assert _path_to_cache_filename("docs/API.rst") == "docs-API.json"


class TestParseLlmResponse:
    """Test parsing LLM JSON responses."""

    def test_parse_clean_json(self):
        """Given clean JSON response, should parse successfully."""
        response = json.dumps({
            "intent": "Help users get started quickly",
            "doc_type": "tutorial",
            "confidence": "high",
            "reasoning": "Contains step-by-step instructions"
        })
        
        result = _parse_llm_response(response)
        
        assert result["intent"] == "Help users get started quickly"
        assert result["doc_type"] == "tutorial"
        assert result["confidence"] == "high"

    def test_parse_json_in_markdown(self):
        """Given JSON wrapped in markdown code blocks, should extract it."""
        response = """Here's the analysis:

```json
{
    "intent": "Document API endpoints",
    "doc_type": "reference",
    "confidence": "high",
    "reasoning": "Lists technical specifications"
}
```

Hope this helps!"""
        
        result = _parse_llm_response(response)
        
        assert result["intent"] == "Document API endpoints"
        assert result["doc_type"] == "reference"

    def test_parse_json_without_language_tag(self):
        """Given JSON in code blocks without language tag, should extract it."""
        response = """```
{
    "intent": "Explain design decisions",
    "doc_type": "explanation",
    "confidence": "medium",
    "reasoning": "Discusses architecture rationale"
}
```"""
        
        result = _parse_llm_response(response)
        
        assert result["doc_type"] == "explanation"

    def test_invalid_json_raises_error(self):
        """Given invalid JSON, should raise clear error."""
        response = "This is not JSON at all"
        
        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            _parse_llm_response(response)

    def test_missing_required_field_raises_error(self):
        """Given JSON missing required field, should raise error."""
        response = json.dumps({
            "intent": "Some intent",
            "confidence": "high"
            # Missing doc_type and reasoning
        })
        
        with pytest.raises(ValueError, match="Missing required field"):
            _parse_llm_response(response)


class TestDocumentMetadata:
    """Test DocumentMetadata dataclass."""

    def test_to_dict(self):
        """Should serialize to dictionary correctly."""
        metadata = DocumentMetadata(
            document_path="README.md",
            intent="Help users get started",
            doc_type=DocType.TUTORIAL,
            confidence="high",
            reasoning="Contains setup instructions",
            timestamp="2025-12-09T10:00:00Z",
            llm_model="claude-sonnet-4-20250514",
            prompt_used="You are an expert...",
            version="0.7.0"
        )
        
        result = metadata.to_dict()
        
        assert result["version"] == "0.7.0"
        assert result["document_path"] == "README.md"
        assert result["intent"] == "Help users get started"
        assert result["doc_type"] == "tutorial"  # Enum converted to value
        assert result["confidence"] == "high"

    def test_from_dict(self):
        """Should deserialize from dictionary correctly."""
        data = {
            "version": "0.7.0",
            "document_path": "docs/API.md",
            "intent": "Document API endpoints",
            "doc_type": "reference",
            "confidence": "high",
            "reasoning": "Technical specifications",
            "timestamp": "2025-12-09T10:00:00Z",
            "llm_model": "claude-sonnet-4-20250514",
            "prompt_used": "Analyze this..."
        }
        
        metadata = DocumentMetadata.from_dict(data)
        
        assert metadata.document_path == "docs/API.md"
        assert metadata.doc_type == DocType.REFERENCE
        assert metadata.confidence == "high"


class TestSaveAndLoadMetadata:
    """Test saving and loading metadata to/from cache."""

    def test_save_metadata_creates_directory(self, tmp_path):
        """Should create .doc-evergreen/metadata/ directory if it doesn't exist."""
        metadata = DocumentMetadata(
            document_path="README.md",
            intent="Help users",
            doc_type=DocType.TUTORIAL,
            confidence="high",
            reasoning="Setup guide",
            timestamp="2025-12-09T10:00:00Z",
            llm_model="claude-sonnet-4-20250514",
            prompt_used="Analyze...",
            version="0.7.0"
        )
        
        cache_path = save_metadata(metadata, tmp_path)
        
        assert cache_path.exists()
        assert cache_path.parent.name == "metadata"
        assert cache_path.parent.parent.name == ".doc-evergreen"

    def test_save_metadata_writes_json(self, tmp_path):
        """Should write valid JSON to cache file."""
        metadata = DocumentMetadata(
            document_path="docs/API.md",
            intent="API docs",
            doc_type=DocType.REFERENCE,
            confidence="high",
            reasoning="Technical reference",
            timestamp="2025-12-09T10:00:00Z",
            llm_model="claude-sonnet-4-20250514",
            prompt_used="Extract...",
            version="0.7.0"
        )
        
        cache_path = save_metadata(metadata, tmp_path)
        
        # Should be valid JSON
        with open(cache_path) as f:
            data = json.load(f)
        
        assert data["document_path"] == "docs/API.md"
        assert data["doc_type"] == "reference"

    def test_save_metadata_raises_on_existing(self, tmp_path):
        """Should raise FileExistsError if cache already exists (without force)."""
        metadata = DocumentMetadata(
            document_path="README.md",
            intent="Help users",
            doc_type=DocType.TUTORIAL,
            confidence="high",
            reasoning="Setup guide",
            timestamp="2025-12-09T10:00:00Z",
            llm_model="claude-sonnet-4-20250514",
            prompt_used="Analyze...",
            version="0.7.0"
        )
        
        # Save once
        save_metadata(metadata, tmp_path)
        
        # Save again should raise
        with pytest.raises(FileExistsError):
            save_metadata(metadata, tmp_path)

    def test_save_metadata_overwrites_with_force(self, tmp_path):
        """Should overwrite existing cache when force=True."""
        metadata = DocumentMetadata(
            document_path="README.md",
            intent="Original intent",
            doc_type=DocType.TUTORIAL,
            confidence="high",
            reasoning="Original reasoning",
            timestamp="2025-12-09T10:00:00Z",
            llm_model="claude-sonnet-4-20250514",
            prompt_used="Original prompt",
            version="0.7.0"
        )
        
        # Save once
        cache_path = save_metadata(metadata, tmp_path)
        
        # Update metadata
        metadata.intent = "Updated intent"
        
        # Save with force=True
        cache_path = save_metadata(metadata, tmp_path, force=True)
        
        # Should contain updated data
        with open(cache_path) as f:
            data = json.load(f)
        assert data["intent"] == "Updated intent"

    def test_load_metadata_reads_cache(self, tmp_path):
        """Should load metadata from cache file."""
        metadata = DocumentMetadata(
            document_path="CONTRIBUTING.md",
            intent="Guide contributors",
            doc_type=DocType.HOWTO,
            confidence="high",
            reasoning="Step-by-step guide",
            timestamp="2025-12-09T10:00:00Z",
            llm_model="claude-sonnet-4-20250514",
            prompt_used="Extract...",
            version="0.7.0"
        )
        
        # Save first
        save_metadata(metadata, tmp_path)
        
        # Load it back
        loaded = load_metadata("CONTRIBUTING.md", tmp_path)
        
        assert loaded is not None
        assert loaded.document_path == "CONTRIBUTING.md"
        assert loaded.intent == "Guide contributors"
        assert loaded.doc_type == DocType.HOWTO

    def test_load_metadata_returns_none_if_not_found(self, tmp_path):
        """Should return None if cache file doesn't exist."""
        loaded = load_metadata("nonexistent.md", tmp_path)
        assert loaded is None


class TestExtractDocumentMetadata:
    """Test end-to-end metadata extraction."""

    def test_extract_with_mock_llm(self, tmp_path):
        """Should extract metadata using LLM and return DocumentMetadata."""
        # Create a test document
        doc_path = tmp_path / "test_doc.md"
        doc_path.write_text("""# Quick Start Guide

Follow these steps to get started:

1. Install the package
2. Run the setup command
3. Start using the tool
""")
        
        # Mock LLM client
        mock_llm = Mock()
        mock_llm.model = "claude-sonnet-4-20250514"
        mock_llm.generate.return_value = json.dumps({
            "intent": "Help users get started quickly with step-by-step instructions",
            "doc_type": "tutorial",
            "confidence": "high",
            "reasoning": "Contains numbered steps and getting started language typical of tutorials"
        })
        
        # Extract metadata
        metadata = extract_document_metadata(doc_path, mock_llm)
        
        # Verify result
        assert metadata.document_path == str(doc_path)
        assert metadata.intent == "Help users get started quickly with step-by-step instructions"
        assert metadata.doc_type == DocType.TUTORIAL
        assert metadata.confidence == "high"
        assert metadata.llm_model == "claude-sonnet-4-20250514"
        assert "You are a technical documentation expert" in metadata.prompt_used

    def test_extract_truncates_large_documents(self, tmp_path):
        """Should truncate very large documents to avoid token limits."""
        # Create a large document
        doc_path = tmp_path / "large_doc.md"
        large_content = "# Large Doc\n" + ("Lorem ipsum dolor sit amet. " * 1000)
        doc_path.write_text(large_content)
        
        # Mock LLM client
        mock_llm = Mock()
        mock_llm.model = "claude-sonnet-4-20250514"
        mock_llm.generate.return_value = json.dumps({
            "intent": "Some intent",
            "doc_type": "reference",
            "confidence": "medium",
            "reasoning": "Some reasoning"
        })
        
        # Extract metadata
        metadata = extract_document_metadata(doc_path, mock_llm)
        
        # Verify LLM was called with truncated content
        call_args = mock_llm.generate.call_args
        prompt = call_args[0][0]
        
        # Prompt should not contain the full large content
        assert len(prompt) < len(large_content)

    def test_extract_validates_doc_type(self, tmp_path):
        """Should raise error if LLM returns invalid doc_type."""
        doc_path = tmp_path / "test.md"
        doc_path.write_text("# Test")
        
        # Mock LLM returning invalid doc_type
        mock_llm = Mock()
        mock_llm.model = "claude-sonnet-4-20250514"
        mock_llm.generate.return_value = json.dumps({
            "intent": "Some intent",
            "doc_type": "invalid_type",  # Not a valid DocType
            "confidence": "high",
            "reasoning": "Some reasoning"
        })
        
        # Should raise error
        with pytest.raises(ValueError, match="Invalid doc type"):
            extract_document_metadata(doc_path, mock_llm)
