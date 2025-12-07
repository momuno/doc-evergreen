"""Tests for intent context storage and retrieval."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from doc_evergreen.generate.doc_type import DocType
from doc_evergreen.generate.intent_context import (
    IntentContext,
    save_intent_context,
    load_intent_context,
    ContextFileError,
)


class TestIntentContext:
    """Test IntentContext dataclass."""

    def test_create_intent_context(self):
        """Should create IntentContext with all required fields."""
        context = IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="Help developers get started",
            output_path="README.md",
        )
        
        assert context.doc_type == DocType.TUTORIAL
        assert context.purpose == "Help developers get started"
        assert context.output_path == "README.md"
        assert context.version == "0.7.0"
        assert context.status == "intent_captured"
        assert isinstance(context.timestamp, str)

    def test_timestamp_is_iso_format(self):
        """Timestamp should be in ISO 8601 format."""
        context = IntentContext(
            doc_type=DocType.HOWTO,
            purpose="Solve specific problem",
            output_path="HOWTO.md",
        )
        
        # Should be parseable as datetime
        parsed = datetime.fromisoformat(context.timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)

    def test_to_dict_method(self):
        """Should convert to dict with doc_type as string."""
        context = IntentContext(
            doc_type=DocType.REFERENCE,
            purpose="API documentation",
            output_path="API.md",
        )
        
        data = context.to_dict()
        
        assert data["doc_type"] == "reference"  # Enum converted to string
        assert data["purpose"] == "API documentation"
        assert data["output_path"] == "API.md"
        assert data["version"] == "0.7.0"
        assert data["status"] == "intent_captured"
        assert "timestamp" in data

    def test_from_dict_method(self):
        """Should create IntentContext from dict."""
        data = {
            "version": "0.7.0",
            "doc_type": "explanation",
            "purpose": "Clarify design decisions",
            "output_path": "EXPLANATION.md",
            "timestamp": "2025-12-06T23:00:00Z",
            "status": "intent_captured",
        }
        
        context = IntentContext.from_dict(data)
        
        assert context.doc_type == DocType.EXPLANATION
        assert context.purpose == "Clarify design decisions"
        assert context.output_path == "EXPLANATION.md"
        assert context.timestamp == "2025-12-06T23:00:00Z"


class TestSaveIntentContext:
    """Test saving intent context to file."""

    def test_saves_to_default_location(self, tmp_path):
        """Should save to .doc-evergreen/context.json by default."""
        context = IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="Getting started guide",
            output_path="README.md",
        )
        
        save_intent_context(context, project_root=tmp_path)
        
        expected_path = tmp_path / ".doc-evergreen" / "context.json"
        assert expected_path.exists()

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Should create .doc-evergreen/ directory if it doesn't exist."""
        context = IntentContext(
            doc_type=DocType.HOWTO,
            purpose="Solve problem",
            output_path="HOWTO.md",
        )
        
        # Directory doesn't exist yet
        assert not (tmp_path / ".doc-evergreen").exists()
        
        save_intent_context(context, project_root=tmp_path)
        
        # Directory created
        assert (tmp_path / ".doc-evergreen").is_dir()

    def test_saves_valid_json(self, tmp_path):
        """Should save valid JSON that can be parsed."""
        context = IntentContext(
            doc_type=DocType.REFERENCE,
            purpose="API reference",
            output_path="API.md",
        )
        
        save_intent_context(context, project_root=tmp_path)
        
        saved_path = tmp_path / ".doc-evergreen" / "context.json"
        data = json.loads(saved_path.read_text())
        
        assert data["doc_type"] == "reference"
        assert data["purpose"] == "API reference"
        assert data["version"] == "0.7.0"

    def test_overwrites_existing_context(self, tmp_path):
        """Should overwrite existing context.json."""
        # Save first context
        context1 = IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="First purpose",
            output_path="README.md",
        )
        save_intent_context(context1, project_root=tmp_path)
        
        # Save second context (should overwrite)
        context2 = IntentContext(
            doc_type=DocType.HOWTO,
            purpose="Second purpose",
            output_path="HOWTO.md",
        )
        save_intent_context(context2, project_root=tmp_path)
        
        # Should contain second context
        saved_path = tmp_path / ".doc-evergreen" / "context.json"
        data = json.loads(saved_path.read_text())
        assert data["purpose"] == "Second purpose"

    def test_raises_error_on_permission_denied(self, tmp_path):
        """Should raise ContextFileError if cannot write file."""
        context = IntentContext(
            doc_type=DocType.TUTORIAL,
            purpose="Test",
            output_path="README.md",
        )
        
        # Create directory but make it read-only
        doc_evergreen_dir = tmp_path / ".doc-evergreen"
        doc_evergreen_dir.mkdir()
        doc_evergreen_dir.chmod(0o444)
        
        try:
            with pytest.raises(ContextFileError) as exc_info:
                save_intent_context(context, project_root=tmp_path)
            
            assert "save" in str(exc_info.value).lower()
        finally:
            # Restore permissions for cleanup
            doc_evergreen_dir.chmod(0o755)


class TestLoadIntentContext:
    """Test loading intent context from file."""

    def test_loads_saved_context(self, tmp_path):
        """Should load previously saved context."""
        original = IntentContext(
            doc_type=DocType.EXPLANATION,
            purpose="Clarify concepts",
            output_path="EXPLANATION.md",
        )
        
        save_intent_context(original, project_root=tmp_path)
        loaded = load_intent_context(project_root=tmp_path)
        
        assert loaded.doc_type == original.doc_type
        assert loaded.purpose == original.purpose
        assert loaded.output_path == original.output_path

    def test_raises_error_if_file_not_exists(self, tmp_path):
        """Should raise ContextFileError if context.json doesn't exist."""
        with pytest.raises(ContextFileError) as exc_info:
            load_intent_context(project_root=tmp_path)
        
        assert "not found" in str(exc_info.value).lower()

    def test_raises_error_on_invalid_json(self, tmp_path):
        """Should raise ContextFileError if JSON is invalid."""
        # Create invalid JSON file
        doc_evergreen_dir = tmp_path / ".doc-evergreen"
        doc_evergreen_dir.mkdir()
        context_file = doc_evergreen_dir / "context.json"
        context_file.write_text("{ invalid json }")
        
        with pytest.raises(ContextFileError) as exc_info:
            load_intent_context(project_root=tmp_path)
        
        assert "invalid json" in str(exc_info.value).lower()

    def test_raises_error_on_missing_required_field(self, tmp_path):
        """Should raise ContextFileError if required field missing."""
        # Create JSON missing 'doc_type' field
        doc_evergreen_dir = tmp_path / ".doc-evergreen"
        doc_evergreen_dir.mkdir()
        context_file = doc_evergreen_dir / "context.json"
        context_file.write_text(json.dumps({
            "purpose": "Test purpose",
            "output_path": "README.md",
        }))
        
        with pytest.raises(ContextFileError) as exc_info:
            load_intent_context(project_root=tmp_path)
        
        assert "missing" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()


class TestContextFileError:
    """Test custom exception for context file errors."""

    def test_error_is_io_error(self):
        """ContextFileError should be an IOError."""
        assert issubclass(ContextFileError, IOError)

    def test_error_message_formatting(self):
        """Error should format message with context."""
        error = ContextFileError("Failed to save context.json")
        assert "context.json" in str(error)
