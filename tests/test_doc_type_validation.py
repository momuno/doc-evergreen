"""Tests for doc type validation (Diataxis framework)."""

import pytest
from doc_evergreen.generate.doc_type import (
    DocType,
    validate_doc_type,
    get_doc_type_description,
    InvalidDocTypeError,
)


class TestDocTypeEnum:
    """Test DocType enum values."""

    def test_tutorial_type_exists(self):
        """Tutorial type should be a valid DocType."""
        assert DocType.TUTORIAL.value == "tutorial"

    def test_howto_type_exists(self):
        """How-to type should be a valid DocType."""
        assert DocType.HOWTO.value == "howto"

    def test_reference_type_exists(self):
        """Reference type should be a valid DocType."""
        assert DocType.REFERENCE.value == "reference"

    def test_explanation_type_exists(self):
        """Explanation type should be a valid DocType."""
        assert DocType.EXPLANATION.value == "explanation"

    def test_all_diataxis_types_present(self):
        """Should have exactly 4 Diataxis doc types."""
        assert len(DocType) == 4


class TestValidateDocType:
    """Test doc type validation function."""

    def test_valid_tutorial_string(self):
        """Should accept 'tutorial' as valid."""
        result = validate_doc_type("tutorial")
        assert result == DocType.TUTORIAL

    def test_valid_howto_string(self):
        """Should accept 'howto' as valid."""
        result = validate_doc_type("howto")
        assert result == DocType.HOWTO

    def test_valid_reference_string(self):
        """Should accept 'reference' as valid."""
        result = validate_doc_type("reference")
        assert result == DocType.REFERENCE

    def test_valid_explanation_string(self):
        """Should accept 'explanation' as valid."""
        result = validate_doc_type("explanation")
        assert result == DocType.EXPLANATION

    def test_case_insensitive_validation(self):
        """Should accept uppercase/mixed case doc types."""
        assert validate_doc_type("TUTORIAL") == DocType.TUTORIAL
        assert validate_doc_type("HowTo") == DocType.HOWTO
        assert validate_doc_type("Reference") == DocType.REFERENCE

    def test_invalid_doc_type_raises_error(self):
        """Should raise InvalidDocTypeError for invalid types."""
        with pytest.raises(InvalidDocTypeError) as exc_info:
            validate_doc_type("invalid-type")
        
        assert "invalid-type" in str(exc_info.value)

    def test_empty_string_raises_error(self):
        """Should raise InvalidDocTypeError for empty string."""
        with pytest.raises(InvalidDocTypeError):
            validate_doc_type("")

    def test_none_raises_error(self):
        """Should raise InvalidDocTypeError for None."""
        with pytest.raises(InvalidDocTypeError):
            validate_doc_type(None)

    def test_error_message_includes_valid_types(self):
        """Error message should list valid doc types."""
        with pytest.raises(InvalidDocTypeError) as exc_info:
            validate_doc_type("blog-post")
        
        error_msg = str(exc_info.value)
        assert "tutorial" in error_msg
        assert "howto" in error_msg
        assert "reference" in error_msg
        assert "explanation" in error_msg


class TestGetDocTypeDescription:
    """Test doc type description retrieval."""

    def test_tutorial_description(self):
        """Should return helpful description for tutorial."""
        desc = get_doc_type_description(DocType.TUTORIAL)
        assert "learning-oriented" in desc.lower()
        assert len(desc) > 20  # Ensure it's a real description

    def test_howto_description(self):
        """Should return helpful description for how-to."""
        desc = get_doc_type_description(DocType.HOWTO)
        assert "goal-oriented" in desc.lower() or "problem-solving" in desc.lower()
        assert len(desc) > 20

    def test_reference_description(self):
        """Should return helpful description for reference."""
        desc = get_doc_type_description(DocType.REFERENCE)
        assert "information-oriented" in desc.lower() or "technical description" in desc.lower()
        assert len(desc) > 20

    def test_explanation_description(self):
        """Should return helpful description for explanation."""
        desc = get_doc_type_description(DocType.EXPLANATION)
        assert "understanding-oriented" in desc.lower() or "clarification" in desc.lower()
        assert len(desc) > 20

    def test_all_types_have_descriptions(self):
        """All doc types should have descriptions."""
        for doc_type in DocType:
            desc = get_doc_type_description(doc_type)
            assert desc is not None
            assert len(desc) > 0


class TestInvalidDocTypeError:
    """Test custom exception for invalid doc types."""

    def test_error_is_value_error(self):
        """InvalidDocTypeError should be a ValueError."""
        assert issubclass(InvalidDocTypeError, ValueError)

    def test_error_message_formatting(self):
        """Error should format message with invalid type and suggestions."""
        error = InvalidDocTypeError("blog-post")
        assert "blog-post" in str(error)
        assert "tutorial" in str(error).lower()
