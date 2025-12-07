"""File relevance analysis for generate-doc."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from doc_evergreen.generate.intent_context import IntentContext
from doc_evergreen.generate.repo_indexer import FileIndex, FileType


class FilePreview:
    """File preview extraction."""
    
    @staticmethod
    def extract(file_path: Path, max_chars: int = 500) -> str:
        """Extract preview from file.
        
        Args:
            file_path: Path to file
            max_chars: Maximum characters to extract
            
        Returns:
            Preview string (truncated to max_chars)
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            return content[:max_chars]
        except (UnicodeDecodeError, PermissionError):
            # Binary file or permission denied
            return ""


@dataclass
class RelevanceScore:
    """Relevance score for a file."""
    
    file_path: str
    score: int  # 0-100
    reasoning: str
    key_material: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "file": self.file_path,
            "score": self.score,
            "reasoning": self.reasoning,
            "key_material": self.key_material,
        }


@dataclass
class RelevanceNotes:
    """Collection of relevance analysis results."""
    
    doc_type: str
    purpose: str
    relevant_files: list[RelevanceScore]
    total_files_analyzed: int
    threshold: int
    analyzed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @property
    def relevant_files_count(self) -> int:
        """Count of relevant files."""
        return len(self.relevant_files)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "analyzed_at": self.analyzed_at,
            "total_files_analyzed": self.total_files_analyzed,
            "relevant_files_count": self.relevant_files_count,
            "threshold": self.threshold,
            "doc_type": self.doc_type,
            "purpose": self.purpose,
            "relevant_files": [f.to_dict() for f in self.relevant_files],
        }
    
    def save(self, path: Path) -> None:
        """Save to JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "RelevanceNotes":
        """Load from JSON file."""
        data = json.loads(path.read_text())
        
        scores = []
        for f in data["relevant_files"]:
            scores.append(RelevanceScore(
                file_path=f["file"],
                score=f["score"],
                reasoning=f["reasoning"],
                key_material=f["key_material"],
            ))
        
        return cls(
            doc_type=data["doc_type"],
            purpose=data["purpose"],
            relevant_files=scores,
            total_files_analyzed=data["total_files_analyzed"],
            threshold=data["threshold"],
            analyzed_at=data.get("analyzed_at", ""),
        )


class RelevanceAnalyzer:
    """Analyzes file relevance for documentation generation.
    
    For Sprint 3, uses rule-based heuristics for speed. Future sprints
    can add LLM-based analysis for more sophisticated scoring.
    """
    
    def __init__(
        self,
        context: IntentContext,
        file_index: FileIndex,
        threshold: int = 50,
    ):
        """Initialize analyzer.
        
        Args:
            context: Intent context (doc type, purpose)
            file_index: File index from Sprint 2
            threshold: Minimum relevance score to include
        """
        self.context = context
        self.file_index = file_index
        self.threshold = threshold
    
    def analyze(self) -> list[RelevanceScore]:
        """Analyze all files for relevance.
        
        Returns:
            List of relevance scores above threshold
        """
        scores = []
        
        for file_entry in self.file_index.files:
            score = self._score_file(file_entry)
            if score.score >= self.threshold:
                scores.append(score)
        
        # Sort by score (highest first)
        scores.sort(key=lambda s: s.score, reverse=True)
        
        return scores
    
    def _score_file(self, file_entry) -> RelevanceScore:
        """Score individual file for relevance.
        
        Uses rule-based heuristics:
        - Documentation files: high relevance for all doc types
        - Source code: relevance depends on doc type and file name
        - Config: medium relevance for reference/howto
        - Tests: low relevance (mostly excluded)
        
        Args:
            file_entry: File entry from index
            
        Returns:
            RelevanceScore with score and reasoning
        """
        score = 0
        reasoning_parts = []
        key_material_parts = []
        
        doc_type = self.context.doc_type.value
        purpose_lower = self.context.purpose.lower()
        file_path = file_entry.rel_path
        file_type = file_entry.file_type
        
        # Base score by file type
        if file_type == FileType.DOCUMENTATION:
            score += 70
            reasoning_parts.append("Documentation file")
            key_material_parts.append("Project information, usage examples")
            
            # README is especially relevant for tutorials
            if "README" in file_path.upper() and doc_type == "tutorial":
                score += 15
                reasoning_parts.append("README highly relevant for tutorial")
        
        elif file_type == FileType.SOURCE_CODE:
            score += 50
            reasoning_parts.append("Source code file")
            key_material_parts.append("Implementation details")
            
            # Main entry points are more relevant
            if "main" in file_path.lower() or "cli" in file_path.lower():
                score += 20
                reasoning_parts.append("Main entry point or CLI")
                key_material_parts.append("Command structure, entry logic")
            
            # __init__.py files show package structure
            if "__init__" in file_path:
                score += 10
                reasoning_parts.append("Package initialization")
                key_material_parts.append("Package exports, structure")
        
        elif file_type == FileType.CONFIG:
            score += 40
            reasoning_parts.append("Configuration file")
            key_material_parts.append("Project settings, dependencies")
            
            # Package config especially relevant for tutorials (installation)
            if any(name in file_path for name in ["package.json", "pyproject.toml", "setup.py"]):
                if doc_type in ["tutorial", "howto"]:
                    score += 20
                    reasoning_parts.append("Package config relevant for getting started")
                    key_material_parts.append("Installation instructions, dependencies")
        
        elif file_type == FileType.TEST:
            score += 20  # Lower relevance but not zero
            reasoning_parts.append("Test file (lower relevance)")
            key_material_parts.append("Usage examples from tests")
        
        else:
            score += 30
            reasoning_parts.append("Other file type")
        
        # Adjust based on doc type
        if doc_type == "tutorial":
            # Tutorials need getting started info
            if any(word in file_path.lower() for word in ["example", "demo", "quickstart"]):
                score += 15
                reasoning_parts.append("Example/demo file relevant for tutorial")
        
        elif doc_type == "reference":
            # Reference needs API/implementation details
            if any(word in file_path.lower() for word in ["api", "interface", "schema"]):
                score += 15
                reasoning_parts.append("API/interface file relevant for reference")
        
        elif doc_type == "howto":
            # How-to needs specific functionality
            if any(word in purpose_lower for word in file_path.lower().split("/")):
                score += 20
                reasoning_parts.append("File name matches purpose keywords")
        
        # Cap at 100
        score = min(score, 100)
        
        # Build reasoning string
        reasoning = " - ".join(reasoning_parts) if reasoning_parts else "General project file"
        key_material = ", ".join(key_material_parts) if key_material_parts else "Project context"
        
        return RelevanceScore(
            file_path=file_path,
            score=score,
            reasoning=reasoning,
            key_material=key_material,
        )
