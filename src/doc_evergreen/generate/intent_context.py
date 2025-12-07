"""Intent context storage for generate-doc workflow."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from doc_evergreen.generate.doc_type import DocType, validate_doc_type


class ContextFileError(IOError):
    """Raised when context file operations fail."""
    pass


@dataclass
class IntentContext:
    """User intent for document generation.
    
    Captures what the user wants to generate and why. This context
    guides all downstream features (repo analysis, outline generation, etc.).
    
    Attributes:
        doc_type: Type of documentation (Diataxis framework)
        purpose: Freeform description of what document should accomplish
        output_path: Where to write generated document
        version: doc-evergreen version (for compatibility)
        status: Current workflow status
        timestamp: When context was created (ISO 8601 format)
    """
    
    doc_type: DocType
    purpose: str
    output_path: str
    version: str = "0.7.0"
    status: str = "intent_captured"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary with doc_type as string value
        """
        return {
            "version": self.version,
            "doc_type": self.doc_type.value,  # Convert enum to string
            "purpose": self.purpose,
            "output_path": self.output_path,
            "timestamp": self.timestamp,
            "status": self.status,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "IntentContext":
        """Create IntentContext from dictionary.
        
        Args:
            data: Dictionary with context fields
        
        Returns:
            IntentContext instance
        
        Raises:
            ContextFileError: If required fields missing or invalid
        """
        try:
            # Check required fields first
            required_fields = ["doc_type", "purpose", "output_path"]
            missing = [field for field in required_fields if field not in data]
            if missing:
                raise ContextFileError(
                    f"Missing required fields in context: {', '.join(missing)}"
                )
            
            # Validate and convert doc_type string to enum
            doc_type = validate_doc_type(data["doc_type"])
            
            return cls(
                version=data.get("version", "0.7.0"),
                doc_type=doc_type,
                purpose=data["purpose"],
                output_path=data["output_path"],
                timestamp=data.get("timestamp", ""),
                status=data.get("status", "intent_captured"),
            )
        except ContextFileError:
            raise  # Re-raise our own errors
        except Exception as e:
            raise ContextFileError(f"Invalid context data: {e}")


def save_intent_context(context: IntentContext, project_root: Path = Path.cwd()) -> None:
    """Save intent context to .doc-evergreen/context.json.
    
    Creates .doc-evergreen/ directory if it doesn't exist.
    Overwrites existing context.json if present.
    
    Args:
        context: IntentContext to save
        project_root: Project root directory (default: current directory)
    
    Raises:
        ContextFileError: If cannot create directory or write file
    
    Example:
        >>> context = IntentContext(
        ...     doc_type=DocType.TUTORIAL,
        ...     purpose="Help users get started",
        ...     output_path="README.md"
        ... )
        >>> save_intent_context(context)
    """
    try:
        # Create .doc-evergreen directory if needed
        doc_evergreen_dir = project_root / ".doc-evergreen"
        doc_evergreen_dir.mkdir(exist_ok=True)
        
        # Write context to JSON file
        context_file = doc_evergreen_dir / "context.json"
        context_file.write_text(
            json.dumps(context.to_dict(), indent=2)
        )
    except PermissionError as e:
        raise ContextFileError(f"Permission denied: Cannot save context to {context_file}: {e}")
    except Exception as e:
        raise ContextFileError(f"Failed to save context: {e}")


def load_intent_context(project_root: Path = Path.cwd()) -> IntentContext:
    """Load intent context from .doc-evergreen/context.json.
    
    Args:
        project_root: Project root directory (default: current directory)
    
    Returns:
        Loaded IntentContext
    
    Raises:
        ContextFileError: If file not found, invalid JSON, or missing fields
    
    Example:
        >>> context = load_intent_context()
        >>> print(context.doc_type)
        DocType.TUTORIAL
    """
    context_file = project_root / ".doc-evergreen" / "context.json"
    
    # Check if file exists
    if not context_file.exists():
        raise ContextFileError(
            f"Context file not found: {context_file}. "
            "Run 'doc-evergreen generate-doc' to create it."
        )
    
    try:
        # Read and parse JSON
        data = json.loads(context_file.read_text())
        
        # Convert to IntentContext
        return IntentContext.from_dict(data)
    except json.JSONDecodeError as e:
        raise ContextFileError(f"Invalid JSON in context file: {e}")
    except Exception as e:
        raise ContextFileError(f"Failed to load context: {e}")
