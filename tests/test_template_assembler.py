"""Tests for TemplateAssembler - assembles parsed docs + sources into templates."""

import json
import pytest
from pathlib import Path

try:
    from doc_evergreen.reverse.template_assembler import TemplateAssembler
except ImportError:
    TemplateAssembler = None


class TestTemplateAssembler:
    """Tests for template assembly from parsed documents and sources."""
    
    def test_assemble_basic_template_structure(self, tmp_path):
        """
        Given: Parsed document with sections and source mappings
        When: Assemble template
        Then: Returns valid template with _meta and document fields
        """
        # ARRANGE
        parsed_doc = {
            'title': 'My Project',
            'sections': [
                {'heading': 'Installation', 'content': 'Install using pip...', 'subsections': []},
                {'heading': 'Usage', 'content': 'Run the command...', 'subsections': []}
            ]
        }
        source_mappings = {
            0: ['setup.py', 'requirements.txt'],
            1: ['src/main.py', 'README.md']
        }
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='README.md'
        )
        
        # ASSERT
        assert '_meta' in template
        assert 'document' in template
        assert template['document']['title'] == 'My Project'
        assert len(template['document']['sections']) == 2
    
    def test_assemble_generates_metadata(self, tmp_path):
        """
        Given: Parsed document
        When: Assemble template
        Then: Generates _meta with name, description, use_case, quadrant, estimated_lines
        """
        # ARRANGE
        parsed_doc = {
            'title': 'Documentation Guide',
            'sections': [{'heading': 'Overview', 'content': 'This guide...', 'subsections': []}]
        }
        source_mappings = {0: ['README.md']}
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='GUIDE.md'
        )
        
        # ASSERT
        meta = template['_meta']
        assert 'name' in meta
        assert 'description' in meta
        assert 'use_case' in meta
        assert 'quadrant' in meta
        assert 'estimated_lines' in meta
        
        # Should default to explanation quadrant (Sprint 1)
        assert meta['quadrant'] == 'explanation'
    
    def test_assemble_maps_sections_to_template_sections(self, tmp_path):
        """
        Given: Parsed document with multiple sections
        When: Assemble template
        Then: Each section becomes a template section with heading, prompt, sources
        """
        # ARRANGE
        parsed_doc = {
            'title': 'API Docs',
            'sections': [
                {'heading': 'Authentication', 'content': 'Auth methods...', 'subsections': []},
                {'heading': 'Endpoints', 'content': 'REST endpoints...', 'subsections': []}
            ]
        }
        source_mappings = {
            0: ['src/auth.py'],
            1: ['src/api.py', 'src/routes.py']
        }
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='API.md'
        )
        
        # ASSERT
        sections = template['document']['sections']
        assert len(sections) == 2
        
        # First section
        assert sections[0]['heading'] == '## Authentication'
        assert sections[0]['sources'] == ['src/auth.py']
        assert 'prompt' in sections[0]
        
        # Second section
        assert sections[1]['heading'] == '## Endpoints'
        assert sections[1]['sources'] == ['src/api.py', 'src/routes.py']
        assert 'prompt' in sections[1]
    
    def test_assemble_handles_nested_sections(self, tmp_path):
        """
        Given: Parsed document with nested subsections
        When: Assemble template
        Then: Preserves hierarchical structure in template
        """
        # ARRANGE
        parsed_doc = {
            'title': 'Tech Docs',
            'sections': [
                {
                    'heading': 'Backend',
                    'content': 'Backend overview...',
                    'subsections': [
                        {'heading': 'API Gateway', 'content': 'Gateway details...', 'subsections': []},
                        {'heading': 'Database', 'content': 'DB details...', 'subsections': []}
                    ]
                }
            ]
        }
        source_mappings = {
            0: ['src/backend.py'],
            (0, 0): ['src/gateway.py'],
            (0, 1): ['src/database.py']
        }
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='TECH.md'
        )
        
        # ASSERT
        sections = template['document']['sections']
        assert len(sections) == 1
        assert sections[0]['heading'] == '## Backend'
        assert 'sections' in sections[0]
        assert len(sections[0]['sections']) == 2
        assert sections[0]['sections'][0]['heading'] == '### API Gateway'
        assert sections[0]['sections'][1]['heading'] == '### Database'
    
    def test_assemble_generates_placeholder_prompts(self, tmp_path):
        """
        Given: Parsed document sections
        When: Assemble template
        Then: Generates placeholder prompts for each section (Sprint 1)
        """
        # ARRANGE
        parsed_doc = {
            'title': 'Project Docs',
            'sections': [
                {'heading': 'Installation', 'content': 'Install instructions...', 'subsections': []}
            ]
        }
        source_mappings = {0: ['setup.py']}
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='README.md'
        )
        
        # ASSERT
        section = template['document']['sections'][0]
        prompt = section['prompt']
        
        # Placeholder prompt should reference the section heading
        assert 'Installation' in prompt
        assert len(prompt) > 0
    
    def test_assemble_saves_to_file(self, tmp_path):
        """
        Given: Template assembled
        When: Save to file path
        Then: Writes valid JSON to specified path
        """
        # ARRANGE
        parsed_doc = {
            'title': 'Test Doc',
            'sections': [{'heading': 'Section 1', 'content': 'Content...', 'subsections': []}]
        }
        source_mappings = {0: ['file.py']}
        output_path = tmp_path / 'template.json'
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='TEST.md'
        )
        assembler.save(template, output_path)
        
        # ASSERT
        assert output_path.exists()
        
        # Verify valid JSON
        with open(output_path) as f:
            loaded = json.load(f)
        assert loaded['_meta']['name'] is not None
        assert loaded['document']['title'] == 'Test Doc'
    
    def test_assemble_handles_empty_sections(self, tmp_path):
        """
        Given: Parsed document with no sections
        When: Assemble template
        Then: Creates valid template with empty sections list
        """
        # ARRANGE
        parsed_doc = {
            'title': 'Empty Doc',
            'sections': []
        }
        source_mappings = {}
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='EMPTY.md'
        )
        
        # ASSERT
        assert template['document']['sections'] == []
        assert template['_meta'] is not None
    
    def test_assemble_generates_name_from_output_filename(self, tmp_path):
        """
        Given: Output filename provided
        When: Assemble template
        Then: Generates template name from filename
        """
        # ARRANGE
        parsed_doc = {
            'title': 'Contributing Guide',
            'sections': [{'heading': 'Guidelines', 'content': '...', 'subsections': []}]
        }
        source_mappings = {0: []}
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='CONTRIBUTING.md'
        )
        
        # ASSERT
        # Should generate name like "contributing-reversed" or similar
        name = template['_meta']['name']
        assert 'contributing' in name.lower()
    
    def test_assemble_preserves_heading_levels(self, tmp_path):
        """
        Given: Parsed sections at different heading levels
        When: Assemble template
        Then: Converts to appropriate markdown heading syntax (##, ###, etc.)
        """
        # ARRANGE
        parsed_doc = {
            'title': 'Multi-Level Doc',
            'sections': [
                {
                    'heading': 'Top Section',
                    'content': '...',
                    'subsections': [
                        {'heading': 'Subsection', 'content': '...', 'subsections': []}
                    ]
                }
            ]
        }
        source_mappings = {0: [], (0, 0): []}
        
        assembler = TemplateAssembler()
        
        # ACT
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename='DOC.md'
        )
        
        # ASSERT
        top_section = template['document']['sections'][0]
        assert top_section['heading'].startswith('##')  # H2
        assert top_section['sections'][0]['heading'].startswith('###')  # H3
