"""Template schema for doc_evergreen with section-level prompts."""

import json
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


@dataclass
class Section:
    """Section within a document template."""

    heading: str
    prompt: str | None = None
    sources: list[str] = field(default_factory=list)
    sections: list["Section"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Convert dict sections to Section objects."""
        self.sections = [Section(**s) if isinstance(s, dict) else s for s in self.sections]


@dataclass
class Document:
    """Document structure with sections."""

    title: str
    output: str
    sections: list[Section]


@dataclass
class Template:
    """Complete template containing document definition."""

    document: Document


@dataclass
class ValidationResult:
    """Result of template validation."""

    valid: bool
    errors: list[str]


@dataclass
class TemplateMetadata:
    """Template metadata from _meta field.
    
    Attributes:
        name: Template identifier (e.g., "tutorial-quickstart")
        description: One-line description of template purpose
        use_case: When to use this template
        quadrant: Divio documentation quadrant (tutorial|howto|reference|explanation)
        estimated_lines: Approximate document length
    
    Example:
        >>> meta = TemplateMetadata(
        ...     name="tutorial-quickstart",
        ...     description="Quick-start tutorial template",
        ...     use_case="First-time user guides",
        ...     quadrant="tutorial",
        ...     estimated_lines="50-100"
        ... )
    """
    name: str
    description: str
    use_case: str
    quadrant: str
    estimated_lines: str


@dataclass
class TemplateWithMetadata:
    """Template bundled with its metadata.
    
    Combines template metadata with the actual template structure
    for complete template representation.
    
    Attributes:
        meta: Template metadata from _meta field
        template: The template structure with document definition
    
    Example:
        >>> template_with_meta = TemplateWithMetadata(
        ...     meta=meta,
        ...     template=template
        ... )
    """
    meta: TemplateMetadata
    template: Template


def parse_template(path: Path) -> Template:
    """Parse a JSON template file into a Template object.

    Args:
        path: Path to JSON template file

    Returns:
        Template object

    Raises:
        ValueError: If JSON is invalid or required fields are missing
    """
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    if "document" not in data:
        raise ValueError("Template missing required 'document' key")

    doc_data = data["document"]

    if "title" not in doc_data or "output" not in doc_data:
        raise ValueError("Document missing required fields: 'title' and 'output'")

    sections = [_parse_section(s) for s in doc_data.get("sections", [])]

    document = Document(title=doc_data["title"], output=doc_data["output"], sections=sections)

    return Template(document=document)


def _parse_section(data: dict) -> Section:
    """Parse section data recursively."""
    nested_sections = [_parse_section(s) for s in data.get("sections", [])]

    return Section(
        heading=data["heading"],
        prompt=data.get("prompt"),
        sources=data.get("sources", []),
        sections=nested_sections,
    )


def validate_template(template: Template, mode: str = "single") -> ValidationResult:
    """Validate template based on generation mode.

    Args:
        template: Template to validate
        mode: Generation mode - "single" or "chunked"

    Returns:
        ValidationResult with validation status and errors
    """
    errors: list[str] = []

    if mode == "chunked":
        # In chunked mode, all sections must have prompts
        _check_prompts_recursive(template.document.sections, errors)

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def _check_prompts_recursive(sections: list[Section], errors: list[str]) -> None:
    """Recursively check that all sections have prompts."""
    for section in sections:
        if section.prompt is None:
            errors.append(f"Section '{section.heading}' missing required prompt for chunked mode")

        # Check nested sections
        if section.sections:
            _check_prompts_recursive(section.sections, errors)


def parse_template_with_metadata(path: Path) -> TemplateWithMetadata:
    """Parse template JSON including _meta field.
    
    Parses a template file that includes both metadata (_meta field)
    and template structure (document field). Validates that both
    required fields are present.
    
    Args:
        path: Path to template JSON file
    
    Returns:
        TemplateWithMetadata with parsed meta and template
    
    Raises:
        ValueError: If _meta or document missing/invalid
    
    Example:
        >>> path = Path("templates/tutorial-quickstart.json")
        >>> template_with_meta = parse_template_with_metadata(path)
        >>> print(template_with_meta.meta.name)
        tutorial-quickstart
    """
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    # Validate required fields
    if "_meta" not in data:
        raise ValueError("Template missing required '_meta' field")
    
    if "document" not in data:
        raise ValueError("Template missing required 'document' field")
    
    # Parse metadata
    meta_data = data["_meta"]
    required_meta_fields = ["name", "description", "use_case", "quadrant", "estimated_lines"]
    
    for field in required_meta_fields:
        if field not in meta_data:
            raise ValueError(f"Template metadata missing required field: '{field}'")
    
    meta = TemplateMetadata(
        name=meta_data["name"],
        description=meta_data["description"],
        use_case=meta_data["use_case"],
        quadrant=meta_data["quadrant"],
        estimated_lines=meta_data["estimated_lines"]
    )
    
    # Parse template using existing function
    # Create a temporary structure with just the document
    doc_data = data["document"]
    
    if "title" not in doc_data or "output" not in doc_data:
        raise ValueError("Document missing required fields: 'title' and 'output'")
    
    sections = [_parse_section(s) for s in doc_data.get("sections", [])]
    document = Document(title=doc_data["title"], output=doc_data["output"], sections=sections)
    template = Template(document=document)
    
    return TemplateWithMetadata(meta=meta, template=template)
