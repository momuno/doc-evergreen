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
            - 'subsections' (list): Nested subsections (H3-H6)
        """
        lines = markdown_text.split('\n')
        title = None
        sections = []
        
        # Stack to track current hierarchy: [(level, node), ...]
        # node is the dict being built at that level
        hierarchy_stack = []
        
        # Track if we're inside a code block
        in_code_block = False
        
        for line in lines:
            # Check for code fence (``` or ~~~)
            if line.strip().startswith('```') or line.strip().startswith('~~~'):
                in_code_block = not in_code_block
                # Still append code fence as content if we have a section
                if hierarchy_stack:
                    self._append_content(line, hierarchy_stack)
                continue
            
            # Skip heading detection inside code blocks
            if in_code_block:
                if hierarchy_stack:
                    self._append_content(line, hierarchy_stack)
                continue
            
            heading_level = self._get_heading_level(line)
            
            if heading_level == 1:
                # H1 is the document title (only if not in code block)
                title = self._extract_heading(line, 1)
            elif heading_level == 2:
                # H2 starts a new section
                # Finalize any previous hierarchy
                self._finalize_hierarchy(sections, hierarchy_stack)
                
                # Create new section
                new_section = {
                    'heading': self._extract_heading(line, 2),
                    'content': '',
                    'subsections': []
                }
                hierarchy_stack = [(2, new_section)]
            elif heading_level >= 3 and heading_level <= 6:
                # H3-H6 are nested subsections
                self._handle_subsection(line, heading_level, hierarchy_stack)
            elif line.strip() and hierarchy_stack:
                # Content line - add to the deepest current node
                self._append_content(line, hierarchy_stack)
        
        # Finalize remaining hierarchy
        self._finalize_hierarchy(sections, hierarchy_stack)
        
        return {
            'title': title,
            'sections': sections
        }
    
    def _get_heading_level(self, line: str) -> int:
        """Get the heading level (1-6) from a markdown line.
        
        Args:
            line: Markdown line
            
        Returns:
            Heading level (1-6), or 0 if not a heading
        """
        if not line.startswith('#'):
            return 0
        
        # Count leading # characters followed by a space
        level = 0
        for char in line:
            if char == '#':
                level += 1
            elif char == ' ':
                return level if level <= 6 else 0
            else:
                return 0
        return 0
    
    def _extract_heading(self, line: str, level: int) -> str:
        """Extract heading text from markdown heading line.
        
        Args:
            line: Markdown line with heading
            level: Heading level (1-6)
            
        Returns:
            Heading text without markdown markers
        """
        prefix_length = level + 1  # '# ' = 2, '## ' = 3, etc.
        return line[prefix_length:].strip()
    
    def _handle_subsection(
        self,
        line: str,
        level: int,
        hierarchy_stack: list
    ) -> None:
        """Handle subsection heading (H3-H6).
        
        Args:
            line: Markdown line with heading
            level: Heading level (3-6)
            hierarchy_stack: Current hierarchy stack
        """
        if not hierarchy_stack:
            return  # No parent section, ignore orphan subsection
        
        # Pop stack until we find the parent level
        while len(hierarchy_stack) > 0 and hierarchy_stack[-1][0] >= level:
            popped_level, popped_node = hierarchy_stack.pop()
            if len(hierarchy_stack) > 0:
                parent_level, parent_node = hierarchy_stack[-1]
                self._add_subsection(parent_node, popped_node)
        
        # Create new subsection at current level
        new_subsection = {
            'heading': self._extract_heading(line, level),
            'content': '',
            'subsections': []
        }
        hierarchy_stack.append((level, new_subsection))
    
    def _add_subsection(self, parent: dict, subsection: dict) -> None:
        """Add subsection to parent's subsections list.
        
        Args:
            parent: Parent node to add subsection to
            subsection: Subsection to add
        """
        if 'subsections' not in parent:
            parent['subsections'] = []
        parent['subsections'].append(subsection)
    
    def _append_content(self, line: str, hierarchy_stack: list) -> None:
        """Append content line to the deepest node in hierarchy.
        
        Args:
            line: Content line to append
            hierarchy_stack: Current hierarchy stack
        """
        if not hierarchy_stack:
            return
        
        text = line.strip()
        # Add content to the deepest node (last in stack)
        _, current_node = hierarchy_stack[-1]
        
        if current_node['content']:
            current_node['content'] += '\n\n' + text
        else:
            current_node['content'] = text
    
    def _finalize_hierarchy(self, sections: list, hierarchy_stack: list) -> None:
        """Finalize the hierarchy and add the root section to sections list.
        
        Args:
            sections: List of sections to append to
            hierarchy_stack: Hierarchy stack to finalize
        """
        if not hierarchy_stack:
            return
        
        # Pop all nodes from stack, adding subsections to their parents
        while len(hierarchy_stack) > 1:
            _, child_node = hierarchy_stack.pop()
            _, parent_node = hierarchy_stack[-1]
            self._add_subsection(parent_node, child_node)
        
        # Add the root section (H2) to sections list
        if hierarchy_stack:
            _, root_section = hierarchy_stack[0]
            sections.append(root_section)
            hierarchy_stack.clear()
