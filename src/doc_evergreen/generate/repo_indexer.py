"""Repository file indexer for generate-doc."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Counter


class FileType(str, Enum):
    """File type classification."""
    
    SOURCE_CODE = "source_code"
    DOCUMENTATION = "documentation"
    CONFIG = "config"
    TEST = "test"
    BUILD = "build"
    DATA = "data"
    UNKNOWN = "unknown"


@dataclass
class FileEntry:
    """Single file entry in the index."""
    
    path: Path
    rel_path: str
    size: int
    extension: str
    file_type: FileType
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "rel_path": self.rel_path,
            "size": self.size,
            "extension": self.extension,
            "type": self.file_type.value,
        }


@dataclass
class FileIndex:
    """Complete file index for project."""
    
    project_root: Path
    files: list[FileEntry]
    indexed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @property
    def total_files(self) -> int:
        """Total number of files."""
        return len(self.files)
    
    def file_counts_by_type(self) -> dict[FileType, int]:
        """Count files by type."""
        counts: Counter[FileType] = Counter()
        for file_entry in self.files:
            counts[file_entry.file_type] += 1
        return dict(counts)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "project_root": str(self.project_root),
            "total_files": self.total_files,
            "indexed_at": self.indexed_at,
            "files": [f.to_dict() for f in self.files],
            "file_counts": {k.value: v for k, v in self.file_counts_by_type().items()},
        }
    
    def save(self, path: Path) -> None:
        """Save index to JSON file."""
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "FileIndex":
        """Load index from JSON file."""
        data = json.loads(path.read_text())
        
        files = []
        for f in data["files"]:
            files.append(FileEntry(
                path=Path(f["rel_path"]),
                rel_path=f["rel_path"],
                size=f["size"],
                extension=f["extension"],
                file_type=FileType(f["type"]),
            ))
        
        return cls(
            project_root=Path(data["project_root"]),
            files=files,
            indexed_at=data.get("indexed_at", ""),
        )


class RepoIndexer:
    """Repository file indexer."""
    
    # Directories to always exclude
    EXCLUDED_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "venv",
        "build",
        "dist",
        ".tox",
        ".eggs",
        "*.egg-info",
    }
    
    # Extension to file type mapping
    EXTENSION_MAP = {
        # Source code
        ".py": FileType.SOURCE_CODE,
        ".js": FileType.SOURCE_CODE,
        ".ts": FileType.SOURCE_CODE,
        ".java": FileType.SOURCE_CODE,
        ".go": FileType.SOURCE_CODE,
        ".rs": FileType.SOURCE_CODE,
        ".c": FileType.SOURCE_CODE,
        ".cpp": FileType.SOURCE_CODE,
        ".h": FileType.SOURCE_CODE,
        ".rb": FileType.SOURCE_CODE,
        ".php": FileType.SOURCE_CODE,
        
        # Documentation
        ".md": FileType.DOCUMENTATION,
        ".rst": FileType.DOCUMENTATION,
        ".txt": FileType.DOCUMENTATION,
        ".adoc": FileType.DOCUMENTATION,
        
        # Config
        ".yaml": FileType.CONFIG,
        ".yml": FileType.CONFIG,
        ".toml": FileType.CONFIG,
        ".json": FileType.CONFIG,
        ".ini": FileType.CONFIG,
        ".cfg": FileType.CONFIG,
        ".env": FileType.CONFIG,
        
        # Data
        ".csv": FileType.DATA,
        ".xml": FileType.DATA,
    }
    
    def __init__(self, project_root: Path):
        """Initialize indexer.
        
        Args:
            project_root: Root directory of project
        """
        self.project_root = project_root
        self._gitignore_patterns: set[str] = set()
        self._docignore_patterns: set[str] = set()
        self._load_ignore_patterns()
    
    def _load_ignore_patterns(self) -> None:
        """Load .gitignore and .docignore patterns."""
        # Load .gitignore
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            self._gitignore_patterns = self._parse_ignore_file(gitignore_path)
        
        # Load .docignore
        docignore_path = self.project_root / ".docignore"
        if docignore_path.exists():
            self._docignore_patterns = self._parse_ignore_file(docignore_path)
    
    def _parse_ignore_file(self, path: Path) -> set[str]:
        """Parse ignore file into patterns."""
        patterns = set()
        for line in path.read_text().splitlines():
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith("#"):
                patterns.add(line)
        return patterns
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        rel_path = path.relative_to(self.project_root)
        path_str = str(rel_path)
        
        # Check excluded directories
        for part in rel_path.parts:
            if part in self.EXCLUDED_DIRS:
                return True
        
        # Check gitignore patterns
        for pattern in self._gitignore_patterns:
            if self._matches_pattern(path_str, pattern):
                return True
        
        # Check docignore patterns
        for pattern in self._docignore_patterns:
            if self._matches_pattern(path_str, pattern):
                return True
        
        return False
    
    def _matches_pattern(self, path_str: str, pattern: str) -> bool:
        """Simple pattern matching (basic implementation)."""
        # Remove trailing slash
        pattern = pattern.rstrip("/")
        
        # Exact match or directory match
        if path_str == pattern or path_str.startswith(pattern + "/"):
            return True
        
        # Wildcard pattern (simple implementation)
        if "*" in pattern:
            # Convert to simple wildcard matching
            if pattern.startswith("*."):
                # Extension pattern like *.log
                ext = pattern[1:]
                return path_str.endswith(ext)
            elif pattern.endswith("*"):
                # Prefix pattern like generated*
                prefix = pattern[:-1]
                return path_str.startswith(prefix) or any(
                    part.startswith(prefix) for part in path_str.split("/")
                )
        
        # Check if pattern matches any path component
        return pattern in path_str.split("/")
    
    def _classify_file(self, path: Path) -> FileType:
        """Classify file by type."""
        # Check if it's a test file
        if "test_" in path.name or path.name.startswith("test") or "_test" in path.name:
            return FileType.TEST
        
        # Check extension
        ext = path.suffix.lower()
        return self.EXTENSION_MAP.get(ext, FileType.UNKNOWN)
    
    def build_index(self) -> FileIndex:
        """Build complete file index.
        
        Returns:
            FileIndex with all discovered files
        """
        files: list[FileEntry] = []
        
        # Walk directory tree
        for path in self.project_root.rglob("*"):
            # Skip directories
            if path.is_dir():
                continue
            
            # Skip ignored paths
            if self._should_ignore(path):
                continue
            
            # Create file entry
            rel_path = str(path.relative_to(self.project_root))
            files.append(FileEntry(
                path=path,
                rel_path=rel_path,
                size=path.stat().st_size,
                extension=path.suffix,
                file_type=self._classify_file(path),
            ))
        
        return FileIndex(
            project_root=self.project_root,
            files=files,
        )
