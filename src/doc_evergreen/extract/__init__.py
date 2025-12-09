"""Document metadata extraction from existing documentation."""

from doc_evergreen.extract.document_metadata import (
    DocumentMetadata,
    extract_document_metadata,
    load_metadata,
    save_metadata,
)

__all__ = [
    "DocumentMetadata",
    "extract_document_metadata",
    "save_metadata",
    "load_metadata",
]
