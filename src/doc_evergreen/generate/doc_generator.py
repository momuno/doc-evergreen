"""Document generation from outline (Sprint 6)."""

import os
from pathlib import Path

from doc_evergreen.generate.outline_generator import DocumentOutline, Section


class DocumentGenerator:
    """Generates complete documents from outlines using LLM.
    
    Uses depth-first traversal to generate content, maintaining context
    from parent sections to child sections for coherent flow.
    """
    
    def __init__(self, project_root: Path = Path.cwd(), llm_client=None):
        """Initialize generator.
        
        Args:
            project_root: Project root directory for reading source files
            llm_client: LLM client for content generation (optional, will create if None)
        """
        self.project_root = project_root
        self.llm_client = llm_client or self._create_llm_client()
        self.section_context = []  # Stack of parent section content for context flow
    
    def generate_from_outline(self, outline_path: Path) -> str:
        """Generate complete document from outline.
        
        Args:
            outline_path: Path to outline.json file
            
        Returns:
            Generated document content as string
        """
        # Load outline
        outline = DocumentOutline.load(outline_path)
        
        # Generate content for all sections (top-down DFS)
        document_parts = []
        
        # Add title
        document_parts.append(f"# {outline.title}\n")
        
        # Generate sections
        for section in outline.sections:
            section_content = self._generate_section(section)
            document_parts.append(section_content)
        
        # Assemble complete document
        full_document = "\n\n".join(document_parts)
        
        # Write to output file
        output_path = self.project_root / outline.output_path
        output_path.write_text(full_document)
        
        return full_document
    
    def _generate_section(self, section: Section, depth: int = 0) -> str:
        """Generate content for a section recursively using DFS.
        
        DFS approach: Generate parent content first, then children with parent context.
        
        Args:
            section: Section to generate
            depth: Current nesting depth (for indentation tracking)
            
        Returns:
            Generated section content with subsections
        """
        parts = []
        
        # Add heading
        parts.append(section.heading)
        
        # Generate content for this level using LLM with parent context
        content = self._generate_section_content(section)
        parts.append(content)
        
        # Push this section's content onto context stack for children (DFS)
        self.section_context.append(content)
        
        # Recursively generate subsections with parent context
        if section.sections:
            subsection_parts = []
            for subsection in section.sections:
                subsection_content = self._generate_section(subsection, depth + 1)
                subsection_parts.append(subsection_content)
            
            # Add subsections
            if subsection_parts:
                parts.append("\n\n".join(subsection_parts))
        
        # Pop context when leaving this section (maintain DFS stack)
        self.section_context.pop()
        
        return "\n\n".join(parts)
    
    def _create_llm_client(self):
        """Create LLM client for content generation."""
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
            
            def generate(self, prompt: str, temperature: float = 0.3) -> str:
                """Generate response from Claude."""
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
        
        return SimpleLLMClient()
    
    def _read_source_files(self, section: Section) -> str:
        """Read and format source files for a section.
        
        Args:
            section: Section with source file references
            
        Returns:
            Formatted source file content
        """
        if not section.sources:
            return "No source files provided for this section."
        
        source_parts = []
        for source in section.sources[:5]:  # Limit to 5 sources to avoid token limits
            file_path = self.project_root / source.file
            
            if not file_path.exists():
                source_parts.append(f"**{source.file}** (file not found)")
                continue
            
            try:
                # Read file with size limit
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Truncate if too large (keep first 2000 chars)
                if len(content) > 2000:
                    content = content[:2000] + "\n\n[... truncated ...]"
                
                source_parts.append(f"**File: {source.file}**\n```\n{content}\n```")
            except Exception as e:
                source_parts.append(f"**{source.file}** (error reading: {e})")
        
        return "\n\n".join(source_parts)
    
    def _generate_section_content(self, section: Section) -> str:
        """Generate content for a section using LLM.
        
        Uses DFS approach: parent section context flows to child sections.
        
        Args:
            section: Section to generate content for
            
        Returns:
            Generated content
        """
        # Build context from parent sections (DFS context flow)
        context_info = ""
        if self.section_context:
            context_info = "\n\n**Context from parent sections:**\n"
            for i, parent_content in enumerate(self.section_context[-2:], 1):  # Last 2 parents
                preview = parent_content[:300] + "..." if len(parent_content) > 300 else parent_content
                context_info += f"Parent level {i}: {preview}\n\n"
        
        # Read source files
        source_content = self._read_source_files(section)
        
        # Build LLM prompt
        prompt = f"""You are a technical documentation writer. Generate content for a documentation section.

**Section Heading:** {section.heading}

**Content Instructions:**
{section.prompt}

**Source Files to Reference:**
{source_content}
{context_info}

**Important Guidelines:**
- Write clear, concise, beginner-friendly content
- Use concrete examples from the source files
- Focus on practical, actionable information
- Use proper markdown formatting
- Keep the tone professional but approachable
- Do NOT include the section heading (it's already added)
- Write 2-4 paragraphs for top-level sections, 1-3 for subsections

Generate the content now:"""
        
        # Generate content using LLM
        content = self.llm_client.generate(prompt, temperature=0.3)
        
        return content.strip()
