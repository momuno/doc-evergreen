"""Document generation from outline (Sprint 6)."""

from pathlib import Path

from doc_evergreen.generate.outline_generator import DocumentOutline, Section


class DocumentGenerator:
    """Generates complete documents from outlines.
    
    For Sprint 6 MVP, uses simplified generation. Future enhancements
    can integrate with LLM for full content generation.
    """
    
    def __init__(self, project_root: Path = Path.cwd()):
        """Initialize generator.
        
        Args:
            project_root: Project root directory for reading source files
        """
        self.project_root = project_root
    
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
        """Generate content for a section recursively.
        
        Args:
            section: Section to generate
            depth: Current nesting depth (for indentation tracking)
            
        Returns:
            Generated section content with subsections
        """
        parts = []
        
        # Add heading
        parts.append(section.heading)
        
        # Generate content for this level
        # For Sprint 6 MVP, use placeholder content based on prompt
        content = self._generate_section_content(section)
        parts.append(content)
        
        # Recursively generate subsections
        if section.sections:
            subsection_parts = []
            for subsection in section.sections:
                subsection_content = self._generate_section(subsection, depth + 1)
                subsection_parts.append(subsection_content)
            
            # Add subsections
            if subsection_parts:
                parts.append("\n\n".join(subsection_parts))
        
        return "\n\n".join(parts)
    
    def _generate_section_content(self, section: Section) -> str:
        """Generate content for a section.
        
        For Sprint 6 MVP, generates placeholder content based on prompt.
        Future versions will integrate with LLM for full generation.
        
        Args:
            section: Section to generate content for
            
        Returns:
            Generated content
        """
        # For MVP: Generate simple placeholder showing structure works
        content_parts = []
        
        # Extract key points from prompt
        prompt_snippet = section.prompt[:100] + "..." if len(section.prompt) > 100 else section.prompt
        content_parts.append(f"*[Generated content for: {prompt_snippet}]*")
        
        # Show sources being used
        if section.sources:
            content_parts.append("\n**Sources used:**")
            for source in section.sources:
                content_parts.append(f"- `{source.file}`: {source.reasoning}")
        
        return "\n\n".join(content_parts)
