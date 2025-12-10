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
    commit: str | None = None  # Optional commit hash for tracking file version

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "file": self.file,
            "reasoning": self.reasoning,
        }
        # Only include commit if it's set (for cleaner JSON)
        if self.commit is not None:
            result["commit"] = self.commit
        return result


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
        """Save outline to JSON file.
        
        Args:
            path: Path to save outline (will be created with parent dirs)
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def generate_versioned_path(cls, output_path: str, base_dir: Path = Path.cwd()) -> Path:
        """Generate versioned outline path based on output document name.
        
        Creates path: .doc-evergreen/outlines/{doc-stem}-{timestamp}.json
        
        Args:
            output_path: Output document path (e.g., "README.md", "docs/API.md")
            base_dir: Base directory (default: current directory)
            
        Returns:
            Versioned outline path
            
        Examples:
            >>> DocumentOutline.generate_versioned_path("README.md")
            .doc-evergreen/outlines/README-20251208-121030.json
            
            >>> DocumentOutline.generate_versioned_path("docs/API.md")
            .doc-evergreen/outlines/API-20251208-121030.json
        """
        from datetime import datetime
        
        # Extract document name (without extension)
        doc_path = Path(output_path)
        doc_stem = doc_path.stem  # e.g., "README" from "README.md"
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Create versioned filename
        outline_filename = f"{doc_stem}-{timestamp}.json"
        
        # Return path in outlines subdirectory
        return base_dir / ".doc-evergreen" / "outlines" / outline_filename
    
    @classmethod
    def load(cls, path: Path) -> "DocumentOutline":
        """Load outline from JSON file."""
        data = json.loads(path.read_text())
        
        def parse_section(s_data) -> Section:
            return Section(
                heading=s_data["heading"],
                level=s_data["level"],
                prompt=s_data["prompt"],
                sources=[SourceReference(
                    file=src["file"],
                    reasoning=src["reasoning"],
                    commit=src.get("commit")  # Optional commit hash
                ) for src in s_data["sources"]],
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
    """Generates hierarchical document outlines using LLM.
    
    Uses Claude to generate custom outlines based on:
    - User intent (doc type, purpose)
    - Relevant files with reasoning
    - Diataxis documentation framework
    """
    
    def __init__(
        self,
        context: IntentContext,
        relevant_files: list[RelevanceScore],
        llm_client=None,
        max_depth: int = 3,
    ):
        """Initialize generator.
        
        Args:
            context: Intent context (doc type, purpose)
            relevant_files: Relevant files with scores and reasoning
            llm_client: LLM client for outline generation (optional, will create if None)
            max_depth: Maximum nesting depth
        """
        self.context = context
        self.relevant_files = relevant_files
        self.max_depth = max_depth
        self.llm_client = llm_client or self._create_llm_client()
    
    def generate(self) -> DocumentOutline:
        """Generate complete hierarchical outline using LLM.
        
        Returns:
            DocumentOutline with nested sections customized to user intent
        """
        # Use LLM to generate custom outline based on intent and relevant files
        outline_response = self._generate_llm_outline()
        
        # Parse LLM response into structured outline
        doc_type = self.context.doc_type.value
        title = outline_response.get("title", self._generate_title())
        sections = self._parse_llm_sections(outline_response.get("sections", []))
        
        return DocumentOutline(
            title=title,
            output_path=self.context.output_path,
            doc_type=doc_type,
            purpose=self.context.purpose,
            sections=sections,
        )
    
    def _create_llm_client(self):
        """Create LLM client for outline generation."""
        from pathlib import Path
        import os
        
        # Simple LLM client wrapper using Anthropic
        class SimpleLLMClient:
            def __init__(self):
                # Get API key from environment (already loaded by CLI)
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    # Fallback to loading from file
                    claude_key_path = Path.home() / ".claude" / "api_key.txt"
                    if claude_key_path.exists():
                        api_key = claude_key_path.read_text().strip()
                        if "=" in api_key:
                            api_key = api_key.split("=", 1)[1].strip()
                
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                
                try:
                    import anthropic
                    self.client = anthropic.Anthropic(api_key=api_key)
                    self.model = "claude-sonnet-4-20250514"
                except ImportError:
                    raise ImportError("anthropic package not installed. Run: pip install anthropic")
            
            def generate(self, prompt: str, temperature: float = 0.0) -> str:
                """Generate response from Claude."""
                from doc_evergreen.prompt_logger import PromptLogger
                
                # Log request
                if PromptLogger.is_enabled():
                    PromptLogger.log_api_call(
                        model=self.model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=4096,
                        location="generate/outline_generator.py:generate"
                    )
                
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = message.content[0].text
                
                # Log response
                if PromptLogger.is_enabled():
                    PromptLogger.log_api_call(
                        model=self.model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=4096,
                        location="generate/outline_generator.py:generate",
                        response=response
                    )
                
                return response
        
        return SimpleLLMClient()
    
    def _generate_llm_outline(self) -> dict:
        """Generate outline using LLM based on user intent and relevant files."""
        # Build context for LLM
        relevant_files_context = self._build_relevant_files_context()
        
        # Create prompt for LLM
        prompt = f"""You are a technical documentation expert. Generate a hierarchical outline for a {self.context.doc_type.value} document.

**User Intent:**
{self.context.purpose}

**Documentation Type:** {self.context.doc_type.value}
{self._get_doc_type_guidance(self.context.doc_type.value)}

**Relevant Files Discovered:**
{relevant_files_context}

**Task:**
Generate a custom outline with sections and subsections that:
1. Aligns with the user's intent and purpose
2. Places relevant source files in appropriate sections
3. Follows the {self.context.doc_type.value} documentation pattern
4. Has meaningful prompts that guide content generation

**Output Format (JSON):**
{{
  "title": "Document Title",
  "sections": [
    {{
      "heading": "# Section Name",
      "level": 1,
      "prompt": "Clear instruction for what content should be generated in this section",
      "sources": [
        {{
          "file": "path/to/file.py",
          "reasoning": "Why this file is relevant to this section"
        }}
      ],
      "sections": [
        {{
          "heading": "## Subsection Name",
          "level": 2,
          "prompt": "Clear instruction for subsection content",
          "sources": [...],
          "sections": []
        }}
      ]
    }}
  ]
}}

**Important Guidelines:**
- Maximum 3 levels of nesting (level 1, 2, 3)
- Each section should have 1-5 relevant source files
- Prompts should be specific and actionable
- Structure should flow logically for the documentation type
- Match source files to sections based on their relevance reasoning

Generate the outline as valid JSON:"""
        
        # Call LLM
        response = self.llm_client.generate(prompt, temperature=0.3)
        
        # Parse JSON response (extract JSON from markdown code blocks if present)
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        
        return json.loads(response)
    
    def _build_relevant_files_context(self) -> str:
        """Build context string from relevant files."""
        if not self.relevant_files:
            return "No relevant files identified."
        
        lines = []
        for i, rf in enumerate(self.relevant_files[:20], 1):  # Top 20 files
            lines.append(f"{i}. {rf.file_path} (score: {rf.score})")
            lines.append(f"   Reasoning: {rf.reasoning}")
        
        return "\n".join(lines)
    
    def _get_doc_type_guidance(self, doc_type: str) -> str:
        """Get guidance for specific doc type."""
        guidance = {
            "tutorial": """
**Tutorial Characteristics:**
- Learning-oriented, takes user on a journey
- Step-by-step progression
- Focuses on getting user to complete a first task successfully
- Should include: Introduction, Prerequisites, Installation, Quick Start, Next Steps""",
            "howto": """
**How-To Characteristics:**
- Goal-oriented, problem-solving
- Practical steps to achieve a specific outcome
- Should include: Problem statement, Prerequisites, Step-by-step solution, Verification""",
            "reference": """
**Reference Characteristics:**
- Information-oriented, factual
- Comprehensive technical details
- Should include: Overview, API/Commands, Parameters, Examples, Return values""",
            "explanation": """
**Explanation Characteristics:**
- Understanding-oriented, conceptual
- Clarifies and illuminates
- Should include: Overview, Key Concepts, Design Rationale, Trade-offs, Related Topics"""
        }
        return guidance.get(doc_type, "")
    
    def _parse_llm_sections(self, sections_data: list) -> list[Section]:
        """Parse LLM-generated sections into Section objects."""
        sections = []
        
        for section_data in sections_data:
            # Parse sources
            sources = []
            for src_data in section_data.get("sources", []):
                sources.append(SourceReference(
                    file=src_data.get("file", ""),
                    reasoning=src_data.get("reasoning", "")
                ))
            
            # Parse subsections recursively
            subsections = self._parse_llm_sections(section_data.get("sections", []))
            
            sections.append(Section(
                heading=section_data.get("heading", ""),
                level=section_data.get("level", 1),
                prompt=section_data.get("prompt", ""),
                sources=sources,
                sections=subsections
            ))
        
        return sections
    
    def _generate_title(self) -> str:
        """Generate document title from purpose (fallback)."""
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

