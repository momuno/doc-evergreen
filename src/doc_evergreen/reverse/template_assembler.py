"""TemplateAssembler - assembles parsed documents and sources into templates."""

import json
from pathlib import Path
from typing import Dict, List, Union


class TemplateAssembler:
    """Assemble parsed documents and discovered sources into template.json format."""
    
    def assemble(
        self,
        parsed_doc: dict,
        source_mappings: Dict[Union[int, tuple], List[str]],
        output_filename: str
    ) -> dict:
        """Assemble template from parsed document and source mappings.
        
        Args:
            parsed_doc: Parsed document structure with title and sections
            source_mappings: Mapping of section indices to source file lists
            output_filename: Output filename for the generated document (e.g., 'README.md')
            
        Returns:
            Complete template dictionary with _meta and document fields
        """
        # Generate template name from output filename
        template_name = self._generate_template_name(output_filename)
        
        # Build metadata
        metadata = self._generate_metadata(
            name=template_name,
            title=parsed_doc.get('title', 'Untitled'),
            sections=parsed_doc.get('sections', [])
        )
        
        # Build document structure
        document = self._build_document(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename=output_filename
        )
        
        return {
            '_meta': metadata,
            'document': document
        }
    
    def save(self, template: dict, output_path: Path) -> None:
        """Save template to JSON file.
        
        Args:
            template: Template dictionary to save
            output_path: Path to write JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
    
    def _generate_template_name(self, output_filename: str) -> str:
        """Generate template name from output filename.
        
        Args:
            output_filename: Output filename (e.g., 'README.md', 'CONTRIBUTING.md')
            
        Returns:
            Template name (e.g., 'readme-reversed', 'contributing-reversed')
        """
        # Remove extension
        name = Path(output_filename).stem
        
        # Convert to lowercase and add suffix
        return f"{name.lower()}-reversed"
    
    def _generate_metadata(self, name: str, title: str, sections: List[dict]) -> dict:
        """Generate template metadata.
        
        Args:
            name: Template name
            title: Document title
            sections: List of section dictionaries
            
        Returns:
            Metadata dictionary with required fields
        """
        # Estimate lines based on section count (rough heuristic)
        section_count = self._count_sections(sections)
        estimated_lines = self._estimate_lines(section_count)
        
        return {
            'name': name,
            'description': f'Auto-generated template from {title}',
            'use_case': 'Regenerate documentation with same structure',
            'quadrant': 'explanation',  # Default for Sprint 1
            'estimated_lines': estimated_lines
        }
    
    def _count_sections(self, sections: List[dict]) -> int:
        """Count total sections including nested subsections.
        
        Args:
            sections: List of section dictionaries
            
        Returns:
            Total section count
        """
        count = len(sections)
        for section in sections:
            count += self._count_sections(section.get('subsections', []))
        return count
    
    def _estimate_lines(self, section_count: int) -> str:
        """Estimate document length based on section count.
        
        Args:
            section_count: Number of sections
            
        Returns:
            Estimated line range string
        """
        if section_count <= 2:
            return '100-200 lines'
        elif section_count <= 5:
            return '200-400 lines'
        elif section_count <= 10:
            return '400-800 lines'
        else:
            return '800+ lines'
    
    def _build_document(
        self,
        parsed_doc: dict,
        source_mappings: Dict[Union[int, tuple], List[str]],
        output_filename: str
    ) -> dict:
        """Build document structure for template.
        
        Args:
            parsed_doc: Parsed document with title and sections
            source_mappings: Source mappings by section index
            output_filename: Output filename
            
        Returns:
            Document dictionary with title, output, and sections
        """
        title = parsed_doc.get('title') or 'Untitled Document'
        sections = parsed_doc.get('sections', [])
        
        # Build template sections
        template_sections = []
        for idx, section in enumerate(sections):
            template_section = self._build_section(
                section=section,
                index=idx,
                source_mappings=source_mappings,
                level=2  # H2 for top-level sections
            )
            template_sections.append(template_section)
        
        return {
            'title': title,
            'output': output_filename,
            'sections': template_sections
        }
    
    def _build_section(
        self,
        section: dict,
        index: Union[int, tuple],
        source_mappings: Dict[Union[int, tuple], List[str]],
        level: int
    ) -> dict:
        """Build a template section from parsed section.
        
        Args:
            section: Parsed section dictionary
            index: Section index (int or tuple for nested)
            source_mappings: Source mappings
            level: Heading level (2-6)
            
        Returns:
            Template section dictionary
        """
        heading = section['heading']
        
        # Add markdown heading syntax if not already present
        if not heading.startswith('#'):
            heading = f"{'#' * level} {heading}"
        
        # Get sources for this section
        sources = source_mappings.get(index, [])
        
        # Generate placeholder prompt
        prompt = self._generate_prompt(section['heading'])
        
        # Build template section
        template_section = {
            'heading': heading,
            'prompt': prompt,
            'sources': sources
        }
        
        # Handle nested subsections
        subsections = section.get('subsections', [])
        if subsections:
            nested_sections = []
            for sub_idx, subsection in enumerate(subsections):
                # Build nested index (e.g., (0, 0) for first subsection of first section)
                nested_index = (index, sub_idx) if isinstance(index, int) else (*index, sub_idx)
                
                nested_template = self._build_section(
                    section=subsection,
                    index=nested_index,
                    source_mappings=source_mappings,
                    level=level + 1
                )
                nested_sections.append(nested_template)
            
            template_section['sections'] = nested_sections
        
        return template_section
    
    def _generate_prompt(self, section_heading: str) -> str:
        """Generate placeholder prompt for a section.
        
        Sprint 1: Simple placeholder prompts
        Sprint 3: Will use LLM to generate intelligent prompts
        
        Args:
            section_heading: Section heading text
            
        Returns:
            Placeholder prompt string
        """
        # Remove markdown heading syntax if present
        clean_heading = section_heading.lstrip('#').strip()
        
        return f"Document the {clean_heading} for this project based on the provided sources."
