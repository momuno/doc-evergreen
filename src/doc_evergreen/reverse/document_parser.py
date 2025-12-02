"""DocumentParser - extracts structure from markdown documents."""

from typing import Optional


class DocumentParser:
    """Parse markdown documents into structured format for template generation."""
    
    def parse(self, markdown_text: str) -> dict:
        """Parse markdown text into structured document.
        
        Args:
            markdown_text: Markdown content to parse
            
        Returns:
            Dictionary with:
            - 'title' (str|None): Document title from H1
            - 'sections' (list): List of section dictionaries
            
            Each section contains:
            - 'heading' (str): Section heading text
            - 'content' (str): Section content paragraphs
            - 'subsections' (list): Nested H3 subsections
        """
        lines = markdown_text.split('\n')
        title = None
        sections = []
        current_section = None
        current_subsection = None
        
        for line in lines:
            if line.startswith('# '):
                title = self._extract_heading(line, 1)
            elif line.startswith('### '):
                current_subsection = self._handle_h3_subsection(
                    line, current_section, current_subsection
                )
            elif line.startswith('## '):
                # Finalize previous section before starting new one
                current_section, current_subsection = self._finalize_section(
                    sections, current_section, current_subsection
                )
                # Start new H2 section
                current_section = {
                    'heading': self._extract_heading(line, 2),
                    'content': '',
                    'subsections': []
                }
            elif line.strip():
                # Add content to current subsection or section
                self._append_content(line, current_subsection, current_section)
        
        # Finalize last section
        self._finalize_section(sections, current_section, current_subsection)
        
        return {
            'title': title,
            'sections': sections
        }
    
    def _extract_heading(self, line: str, level: int) -> str:
        """Extract heading text from markdown heading line.
        
        Args:
            line: Markdown line with heading
            level: Heading level (1-3)
            
        Returns:
            Heading text without markdown markers
        """
        prefix_length = level + 1  # '# ' = 2, '## ' = 3, '### ' = 4
        return line[prefix_length:].strip()
    
    def _handle_h3_subsection(
        self, 
        line: str, 
        current_section: Optional[dict], 
        current_subsection: Optional[dict]
    ) -> Optional[dict]:
        """Handle H3 subsection heading.
        
        Args:
            line: Markdown line with H3 heading
            current_section: Current H2 section being built
            current_subsection: Previous H3 subsection (if any)
            
        Returns:
            New subsection dictionary
        """
        if current_section is not None:
            # Save previous subsection if exists
            if current_subsection:
                self._add_subsection(current_section, current_subsection)
            # Start new subsection
            return {
                'heading': self._extract_heading(line, 3),
                'content': ''
            }
        return None
    
    def _add_subsection(self, section: dict, subsection: dict) -> None:
        """Add subsection to section's subsections list.
        
        Args:
            section: Section to add subsection to
            subsection: Subsection to add
        """
        if 'subsections' not in section:
            section['subsections'] = []
        section['subsections'].append(subsection)
    
    def _append_content(
        self, 
        line: str, 
        current_subsection: Optional[dict], 
        current_section: Optional[dict]
    ) -> None:
        """Append content line to current subsection or section.
        
        Args:
            line: Content line to append
            current_subsection: Current subsection (takes precedence)
            current_section: Current section (fallback)
        """
        text = line.strip()
        target = current_subsection if current_subsection is not None else current_section
        
        if target is not None:
            if target['content']:
                target['content'] += '\n\n' + text
            else:
                target['content'] = text
    
    def _finalize_section(
        self, 
        sections: list, 
        current_section: Optional[dict], 
        current_subsection: Optional[dict]
    ) -> tuple[Optional[dict], Optional[dict]]:
        """Finalize current section and add it to sections list.
        
        Args:
            sections: List of sections to append to
            current_section: Current section to finalize
            current_subsection: Current subsection to save
            
        Returns:
            Tuple of (None, None) to reset section/subsection tracking
        """
        # Save last subsection to current section
        if current_subsection and current_section:
            self._add_subsection(current_section, current_subsection)
        
        # Save current section to sections list
        if current_section:
            sections.append(current_section)
        
        return None, None
