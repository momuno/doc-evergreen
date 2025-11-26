"""Template registry for discovering and loading built-in templates.

This module provides the TemplateRegistry class that discovers templates
from the package's templates/ directory and provides methods to list
and load templates with their metadata.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from importlib.abc import Traversable
else:
    Traversable = object

from doc_evergreen.core.template_schema import (
    TemplateMetadata,
    TemplateWithMetadata,
    parse_template_with_metadata,
)


class TemplateNotFoundError(Exception):
    """Raised when template name doesn't exist.
    
    This error is raised when attempting to load a template
    that is not available in the registry.
    
    Example:
        >>> registry = TemplateRegistry()
        >>> try:
        ...     registry.load_template("nonexistent")
        ... except TemplateNotFoundError as e:
        ...     print(f"Error: {e}")
    """
    pass


class TemplateValidationError(Exception):
    """Raised when template JSON is malformed.
    
    This error is raised when a template file exists but
    contains invalid JSON or missing required fields.
    
    Example:
        >>> # Template with invalid JSON would raise this error
        >>> try:
        ...     registry.load_template("malformed")
        ... except TemplateValidationError as e:
        ...     print(f"Validation error: {e}")
    """
    pass


class TemplateRegistry:
    """Registry for built-in templates.
    
    Discovers and manages built-in templates from the package's
    templates/ directory. Provides methods to list available
    templates and load them with metadata.
    
    Templates are stored as JSON files in src/doc_evergreen/templates/
    and are discovered automatically on initialization.
    
    Attributes:
        _templates: Dictionary mapping template names to their metadata
        _templates_dir: Path to templates directory
    
    Example:
        >>> registry = TemplateRegistry()
        >>> templates = registry.list_templates()
        >>> for t in templates:
        ...     print(f"{t.name}: {t.description}")
        >>> 
        >>> template = registry.load_template("tutorial-quickstart")
        >>> print(template.meta.name)
        tutorial-quickstart
    """
    
    def __init__(self) -> None:
        """Initialize registry and discover templates.
        
        Discovers all template files in the templates/ directory
        and loads their metadata for quick listing.
        """
        self._templates: dict[str, TemplateMetadata] = {}
        self._templates_dir = self._get_templates_directory()
        self._discover_templates()
    
    def _get_templates_directory(self) -> Union[Path, "Traversable"]:
        """Get path to templates directory.
        
        Uses importlib.resources to access templates in installed package,
        falling back to direct path for development.
        
        Returns:
            Path or Traversable to templates directory
        """
        try:
            # Try importlib.resources for installed package
            from importlib.resources import files
            templates_resource = files("doc_evergreen").joinpath("templates")
            return templates_resource
        except (ImportError, AttributeError, TypeError):
            # Fallback to direct path for development
            package_dir = Path(__file__).parent
            return package_dir / "templates"
    
    def _discover_templates(self) -> None:
        """Discover templates in the templates directory.
        
        Scans the templates/ directory for .json files and loads
        their metadata. Silently skips invalid templates during
        discovery (they'll error when actually loaded).
        """
        # Check if templates directory exists
        if isinstance(self._templates_dir, Path):
            if not self._templates_dir.exists():
                # No templates directory yet - empty registry is OK
                return
            
            template_files = list(self._templates_dir.glob("*.json"))
        else:
            # Handle Traversable (importlib.resources)
            try:
                template_files = [f for f in self._templates_dir.iterdir() if f.name.endswith(".json")]
            except (AttributeError, OSError):
                # Directory doesn't exist or can't be read
                return
        
        # Load metadata from each template
        for template_file in template_files:
            try:
                # Convert Traversable to Path if needed
                if isinstance(template_file, Path):
                    template_path = template_file
                else:
                    # For Traversable, we need to read it differently
                    # For now, skip - will be implemented when we add templates
                    continue
                
                # Parse template to get metadata
                template_with_meta = parse_template_with_metadata(template_path)
                self._templates[template_with_meta.meta.name] = template_with_meta.meta
            except (ValueError, KeyError):
                # Skip invalid templates during discovery
                # They'll raise proper errors when loaded
                continue
    
    def list_templates(self) -> list[TemplateMetadata]:
        """List all available templates with metadata.
        
        Returns templates sorted by quadrant (tutorial, howto, reference,
        explanation) and then alphabetically by name within each quadrant.
        
        Returns:
            List of TemplateMetadata objects, sorted appropriately
        
        Example:
            >>> registry = TemplateRegistry()
            >>> templates = registry.list_templates()
            >>> for template in templates:
            ...     print(f"{template.quadrant}/{template.name}")
            ...     print(f"  {template.description}")
        """
        # Define quadrant sort order
        quadrant_order = {"tutorial": 0, "howto": 1, "reference": 2, "explanation": 3}
        
        # Sort by quadrant first, then by name
        sorted_templates = sorted(
            self._templates.values(),
            key=lambda t: (quadrant_order.get(t.quadrant, 999), t.name)
        )
        
        return sorted_templates
    
    def load_template(self, name: str) -> TemplateWithMetadata:
        """Load template by name.
        
        Loads the complete template including metadata and document
        structure from the template file.
        
        Args:
            name: Template name (e.g., "tutorial-quickstart")
        
        Returns:
            TemplateWithMetadata containing meta and template
        
        Raises:
            TemplateNotFoundError: Template doesn't exist
            TemplateValidationError: Template JSON invalid
        
        Example:
            >>> registry = TemplateRegistry()
            >>> template = registry.load_template("tutorial-quickstart")
            >>> print(template.template.document.title)
            Quick-Start Tutorial
        """
        # Check if template exists
        if name not in self._templates:
            available = ", ".join(sorted(self._templates.keys())) if self._templates else "no templates"
            raise TemplateNotFoundError(
                f"Template '{name}' not found.\n"
                f"Available templates: {available}"
            )
        
        # Get template path
        template_path = self.get_template_path(name)
        
        # Load and parse template
        try:
            return parse_template_with_metadata(template_path)
        except ValueError as e:
            raise TemplateValidationError(f"Template '{name}' is invalid: {e}")
    
    def get_template_path(self, name: str) -> Path:
        """Get path to template file.
        
        Returns the filesystem path to the template file.
        Useful for debugging and internal use.
        
        Args:
            name: Template name
        
        Returns:
            Path to template JSON file
        
        Raises:
            TemplateNotFoundError: Template doesn't exist
        
        Example:
            >>> registry = TemplateRegistry()
            >>> path = registry.get_template_path("tutorial-quickstart")
            >>> print(path.name)
            tutorial-quickstart.json
        """
        if name not in self._templates:
            available = ", ".join(sorted(self._templates.keys())) if self._templates else "no templates"
            raise TemplateNotFoundError(
                f"Template '{name}' not found.\n"
                f"Available templates: {available}"
            )
        
        # Construct path to template file
        if isinstance(self._templates_dir, Path):
            return self._templates_dir / f"{name}.json"
        else:
            # For Traversable, return a Path for now
            # This will need refinement when we actually use importlib.resources
            return Path(str(self._templates_dir)) / f"{name}.json"
