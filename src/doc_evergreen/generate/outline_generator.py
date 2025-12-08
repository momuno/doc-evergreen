"""Hierarchical outline generation (Sprint 4-5 CORE INNOVATION)."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from doc_evergreen.generate.intent_context import IntentContext
from doc_evergreen.generate.relevance_analyzer import RelevanceScore


@dataclass
class SourceReference:
    """Source file reference with reasoning."""
    
    file: str
    reasoning: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "file": self.file,
            "reasoning": self.reasoning,
        }


@dataclass
class Section:
    """Section in the document outline."""
    
    heading: str
    level: int
    prompt: str
    sources: list[SourceReference]
    sections: list["Section"]
    
    def to_dict(self) -> dict:
        """Convert to dictionary recursively."""
        return {
            "heading": self.heading,
            "level": self.level,
            "prompt": self.prompt,
            "sources": [s.to_dict() for s in self.sources],
            "sections": [s.to_dict() for s in self.sections],
        }


@dataclass
class DocumentOutline:
    """Complete document outline."""
    
    title: str
    output_path: str
    doc_type: str
    purpose: str
    sections: list[Section]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary with metadata."""
        return {
            "_meta": {
                "name": f"generated-{self.doc_type}-{datetime.now().strftime('%Y%m%d')}",
                "description": self.purpose,
                "use_case": self.purpose,
                "quadrant": self.doc_type,
                "estimated_lines": "400-800 lines",
                "generation_method": "forward",
                "doc_type": self.doc_type,
                "user_intent": self.purpose,
            },
            "document": {
                "title": self.title,
                "output": self.output_path,
                "sections": [s.to_dict() for s in self.sections],
            }
        }
    
    def save(self, path: Path) -> None:
        """Save outline to JSON file."""
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "DocumentOutline":
        """Load outline from JSON file."""
        data = json.loads(path.read_text())
        
        def parse_section(s_data) -> Section:
            return Section(
                heading=s_data["heading"],
                level=s_data["level"],
                prompt=s_data["prompt"],
                sources=[SourceReference(src["file"], src["reasoning"]) 
                        for src in s_data["sources"]],
                sections=[parse_section(sub) for sub in s_data["sections"]],
            )
        
        sections = [parse_section(s) for s in data["document"]["sections"]]
        
        return cls(
            title=data["document"]["title"],
            output_path=data["document"]["output"],
            doc_type=data["_meta"]["doc_type"],
            purpose=data["_meta"]["user_intent"],
            sections=sections,
            generated_at=data["_meta"].get("generated_at", ""),
        )


class OutlineGenerator:
    """Generates hierarchical document outlines.
    
    For Sprint 4-5, uses rule-based generation. Future enhancements
    can add LLM-based structure generation for more sophisticated outlines.
    """
    
    def __init__(
        self,
        context: IntentContext,
        relevant_files: list[RelevanceScore],
        max_depth: int = 3,
    ):
        """Initialize generator.
        
        Args:
            context: Intent context (doc type, purpose)
            relevant_files: Relevant files with scores and reasoning
            max_depth: Maximum nesting depth
        """
        self.context = context
        self.relevant_files = relevant_files
        self.max_depth = max_depth
    
    def generate(self) -> DocumentOutline:
        """Generate complete hierarchical outline.
        
        Returns:
            DocumentOutline with nested sections
        """
        doc_type = self.context.doc_type.value
        
        # Generate title
        title = self._generate_title()
        
        # Generate top-level sections based on doc type
        sections = self._generate_top_level_sections(doc_type)
        
        # Generate subsections for each top-level section
        for section in sections:
            if section.level < self.max_depth:
                section.sections = self._generate_subsections(section, doc_type)
        
        return DocumentOutline(
            title=title,
            output_path=self.context.output_path,
            doc_type=doc_type,
            purpose=self.context.purpose,
            sections=sections,
        )
    
    def _generate_title(self) -> str:
        """Generate document title from purpose."""
        purpose = self.context.purpose
        doc_type = self.context.doc_type.value
        
        # Simple title generation
        if doc_type == "tutorial":
            return "Getting Started Guide"
        elif doc_type == "howto":
            return "How-To Guide"
        elif doc_type == "reference":
            return "Reference Documentation"
        elif doc_type == "explanation":
            return "Technical Overview"
        else:
            return "Documentation"
    
    def _generate_top_level_sections(self, doc_type: str) -> list[Section]:
        """Generate top-level sections based on doc type."""
        if doc_type == "tutorial":
            return self._tutorial_sections()
        elif doc_type == "howto":
            return self._howto_sections()
        elif doc_type == "reference":
            return self._reference_sections()
        elif doc_type == "explanation":
            return self._explanation_sections()
        else:
            return self._default_sections()
    
    def _tutorial_sections(self) -> list[Section]:
        """Generate tutorial structure."""
        sections = []
        
        # Introduction
        sections.append(Section(
            heading="# Introduction",
            level=1,
            prompt=(
                "Write a welcoming introduction (2-3 paragraphs) that explains what "
                "this tool/project does and why it's useful. Set expectations for what "
                "the reader will learn. Don't cover installation or usage details - "
                "those are in sections below."
            ),
            sources=self._get_sources_for_section("overview"),
            sections=[],
        ))
        
        # Getting Started
        sections.append(Section(
            heading="# Getting Started",
            level=1,
            prompt=(
                "Provide a high-level overview of getting started. "
                "Introduce the subsections below but don't repeat their content. "
                "Keep this brief (1-2 paragraphs)."
            ),
            sources=self._get_sources_for_section("getting_started"),
            sections=[],
        ))
        
        # Next Steps
        sections.append(Section(
            heading="# Next Steps",
            level=1,
            prompt=(
                "Suggest what the reader should do next after completing this tutorial. "
                "Point to additional resources or advanced topics. "
                "If there are subsections below, introduce them briefly without covering their details."
            ),
            sources=self._get_sources_for_section("next_steps"),
            sections=[],
        ))
        
        return sections
    
    def _howto_sections(self) -> list[Section]:
        """Generate how-to structure."""
        return [
            Section(
                heading="# Overview",
                level=1,
                prompt="Brief overview of the problem and solution approach.",
                sources=self._get_sources_for_section("overview"),
                sections=[],
            ),
            Section(
                heading="# Prerequisites",
                level=1,
                prompt="List what the reader needs before starting.",
                sources=self._get_sources_for_section("prerequisites"),
                sections=[],
            ),
            Section(
                heading="# Steps",
                level=1,
                prompt="High-level overview. Details in subsections below.",
                sources=self._get_sources_for_section("steps"),
                sections=[],
            ),
        ]
    
    def _reference_sections(self) -> list[Section]:
        """Generate reference structure."""
        return [
            Section(
                heading="# Overview",
                level=1,
                prompt="Technical overview of the component or API.",
                sources=self._get_sources_for_section("overview"),
                sections=[],
            ),
            Section(
                heading="# API Reference",
                level=1,
                prompt="Overview of API. Details in subsections below.",
                sources=self._get_sources_for_section("api"),
                sections=[],
            ),
        ]
    
    def _explanation_sections(self) -> list[Section]:
        """Generate explanation structure."""
        return [
            Section(
                heading="# Overview",
                level=1,
                prompt="High-level explanation of the concept or design.",
                sources=self._get_sources_for_section("overview"),
                sections=[],
            ),
            Section(
                heading="# Design Rationale",
                level=1,
                prompt="Explain why things are designed this way.",
                sources=self._get_sources_for_section("design"),
                sections=[],
            ),
        ]
    
    def _default_sections(self) -> list[Section]:
        """Generate default structure."""
        return [
            Section(
                heading="# Overview",
                level=1,
                prompt="General overview of the topic.",
                sources=self._get_sources_for_section("overview"),
                sections=[],
            ),
        ]
    
    def _generate_subsections(self, parent: Section, doc_type: str) -> list[Section]:
        """Generate subsections for a parent section."""
        subsections = []
        
        # Generate subsections based on parent heading (exact matching)
        # Only "Getting Started" section gets Installation/Quick Start
        if parent.heading == "# Getting Started":
            subsections.append(Section(
                heading="## Installation",
                level=parent.level + 1,
                prompt=(
                    "Provide step-by-step installation instructions. Include prerequisites, "
                    "installation commands, and verification steps."
                ),
                sources=self._get_sources_for_section("installation"),
                sections=[],
            ))
            
            subsections.append(Section(
                heading="## Quick Start",
                level=parent.level + 1,
                prompt=(
                    "Show the simplest possible example to get users started. "
                    "Include a complete working example with expected output."
                ),
                sources=self._get_sources_for_section("quickstart"),
                sections=[],
            ))
        
        # For how-to "Steps" section (not "Next Steps")
        elif parent.heading == "# Steps":
            # For how-to, generate step subsections
            subsections.append(Section(
                heading="## Step 1: Setup",
                level=parent.level + 1,
                prompt="Detailed instructions for the setup phase.",
                sources=self._get_sources_for_section("step1"),
                sections=[],
            ))
            
            subsections.append(Section(
                heading="## Step 2: Implementation",
                level=parent.level + 1,
                prompt="Detailed implementation instructions.",
                sources=self._get_sources_for_section("step2"),
                sections=[],
            ))
        
        elif "API" in parent.heading:
            # For reference, generate API subsections
            subsections.append(Section(
                heading="## Functions",
                level=parent.level + 1,
                prompt="Document all public functions with parameters and return values.",
                sources=self._get_sources_for_section("functions"),
                sections=[],
            ))
            
            subsections.append(Section(
                heading="## Classes",
                level=parent.level + 1,
                prompt="Document all public classes with methods and properties.",
                sources=self._get_sources_for_section("classes"),
                sections=[],
            ))
        
        return subsections
    
    def _get_sources_for_section(self, section_type: str) -> list[SourceReference]:
        """Get relevant sources for a section type."""
        sources = []
        
        # Map section types to file relevance
        if section_type in ["overview", "getting_started"]:
            # Use documentation files
            for rf in self.relevant_files[:3]:  # Top 3 most relevant
                if "README" in rf.file_path or rf.file_path.endswith(".md"):
                    sources.append(SourceReference(
                        file=rf.file_path,
                        reasoning=rf.reasoning,
                    ))
        
        elif section_type in ["installation", "prerequisites"]:
            # Use config files
            for rf in self.relevant_files:
                if any(name in rf.file_path for name in ["package.json", "pyproject.toml", "setup.py", "requirements"]):
                    sources.append(SourceReference(
                        file=rf.file_path,
                        reasoning=rf.reasoning,
                    ))
        
        elif section_type in ["quickstart", "step1", "step2"]:
            # Use source code, examples, and README for context
            # First, add README for overview
            for rf in self.relevant_files:
                if "README" in rf.file_path.upper():
                    sources.append(SourceReference(
                        file=rf.file_path,
                        reasoning=rf.reasoning,
                    ))
                    break
            
            # Then add main source files (CLI entry points, main modules)
            for rf in self.relevant_files[:5]:
                if rf.file_path.endswith((".py", ".js", ".ts")) and "test" not in rf.file_path:
                    if "cli" in rf.file_path.lower() or "main" in rf.file_path.lower():
                        sources.append(SourceReference(
                            file=rf.file_path,
                            reasoning=rf.reasoning,
                        ))
                        break
        
        elif section_type in ["api", "functions", "classes"]:
            # Use source code
            for rf in self.relevant_files:
                if rf.file_path.endswith((".py", ".js", ".ts")) and "test" not in rf.file_path:
                    sources.append(SourceReference(
                        file=rf.file_path,
                        reasoning=rf.reasoning,
                    ))
        
        else:
            # Default: use top relevant files
            for rf in self.relevant_files[:2]:
                sources.append(SourceReference(
                    file=rf.file_path,
                    reasoning=rf.reasoning,
                ))
        
        return sources
