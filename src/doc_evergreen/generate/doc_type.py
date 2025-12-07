"""Doc type validation based on Diataxis framework."""

from enum import Enum


class DocType(Enum):
    """Valid documentation types from Diataxis framework.
    
    Diataxis framework: https://diataxis.fr/
    Four documentation types based on user needs:
    - Tutorial: Learning-oriented (getting started)
    - How-to: Goal-oriented (solving problems)
    - Reference: Information-oriented (technical description)
    - Explanation: Understanding-oriented (clarification)
    """
    
    TUTORIAL = "tutorial"
    HOWTO = "howto"
    REFERENCE = "reference"
    EXPLANATION = "explanation"


class InvalidDocTypeError(ValueError):
    """Raised when an invalid doc type is provided."""
    
    def __init__(self, invalid_type: str | None):
        valid_types = [dt.value for dt in DocType]
        super().__init__(
            f"Invalid doc type: '{invalid_type}'. "
            f"Valid types are: {', '.join(valid_types)}"
        )


def validate_doc_type(doc_type_str: str | None) -> DocType:
    """Validate and convert doc type string to DocType enum.
    
    Args:
        doc_type_str: Doc type as string (case-insensitive)
    
    Returns:
        DocType enum value
    
    Raises:
        InvalidDocTypeError: If doc type is invalid or None
    
    Example:
        >>> validate_doc_type("tutorial")
        DocType.TUTORIAL
        >>> validate_doc_type("HOWTO")
        DocType.HOWTO
    """
    if doc_type_str is None or doc_type_str == "":
        raise InvalidDocTypeError(doc_type_str)
    
    # Normalize to lowercase for case-insensitive matching
    normalized = doc_type_str.lower().strip()
    
    # Try to match against valid doc types
    for doc_type in DocType:
        if doc_type.value == normalized:
            return doc_type
    
    # No match found
    raise InvalidDocTypeError(doc_type_str)


def get_doc_type_description(doc_type: DocType) -> str:
    """Get human-readable description of doc type.
    
    Args:
        doc_type: DocType enum value
    
    Returns:
        Description string explaining the doc type purpose
    
    Example:
        >>> get_doc_type_description(DocType.TUTORIAL)
        'Learning-oriented: Guides users through getting started...'
    """
    descriptions = {
        DocType.TUTORIAL: (
            "Learning-oriented: Guides users through getting started with hands-on lessons. "
            "Focuses on building confidence and initial understanding."
        ),
        DocType.HOWTO: (
            "Goal-oriented: Problem-solving guides that help users accomplish specific tasks. "
            "Focuses on practical steps to achieve a goal."
        ),
        DocType.REFERENCE: (
            "Information-oriented: Technical descriptions of APIs, commands, and features. "
            "Focuses on accurate, complete information for lookup."
        ),
        DocType.EXPLANATION: (
            "Understanding-oriented: Clarification of concepts and design decisions. "
            "Focuses on helping users understand the 'why' behind the system."
        ),
    }
    
    return descriptions[doc_type]
