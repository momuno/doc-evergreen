"""Tests for DocumentParser - extracts structure from markdown documents."""

import pytest

try:
    from doc_evergreen.reverse.document_parser import DocumentParser
except ImportError:
    DocumentParser = None


class TestDocumentParser:
    """Tests for parsing markdown documents into structured format."""

    def test_parse_simple_markdown_with_headings(self):
        """
        Given: Simple markdown with H1 title and H2 section
        When: Parser extracts structure
        Then: Returns document tree with title and sections
        """
        # ARRANGE
        markdown = "# Title\n\n## Section 1\n\nContent here"
        parser = DocumentParser()
        
        # ACT
        result = parser.parse(markdown)
        
        # ASSERT
        assert result['title'] == 'Title'
        assert len(result['sections']) == 1
        assert result['sections'][0]['heading'] == 'Section 1'
        assert result['sections'][0]['content'] == 'Content here'

    def test_parse_multiple_sections(self):
        """
        Given: Markdown with H1 title and multiple H2 sections
        When: Parser extracts structure
        Then: Returns all sections in order with their content
        """
        # ARRANGE
        markdown = """# Project Title

## Installation

Install using pip.

## Usage

Run the command.

## Configuration

Set up config files."""
        parser = DocumentParser()
        
        # ACT
        result = parser.parse(markdown)
        
        # ASSERT
        assert result['title'] == 'Project Title'
        assert len(result['sections']) == 3
        
        # Check first section
        assert result['sections'][0]['heading'] == 'Installation'
        assert result['sections'][0]['content'] == 'Install using pip.'
        
        # Check second section
        assert result['sections'][1]['heading'] == 'Usage'
        assert result['sections'][1]['content'] == 'Run the command.'
        
        # Check third section
        assert result['sections'][2]['heading'] == 'Configuration'
        assert result['sections'][2]['content'] == 'Set up config files.'

    def test_parse_nested_sections_with_h3(self):
        """
        Given: Markdown with H1, H2, and nested H3 sections
        When: Parser extracts structure
        Then: Returns hierarchical structure with subsections
        """
        # ARRANGE
        markdown = """# API Documentation

## Authentication

Learn about auth methods.

### OAuth Setup

Configure OAuth provider.

### API Keys

Generate API keys.

## Endpoints

Available REST endpoints."""
        parser = DocumentParser()
        
        # ACT
        result = parser.parse(markdown)
        
        # ASSERT
        assert result['title'] == 'API Documentation'
        assert len(result['sections']) == 2
        
        # Check first section with subsections
        assert result['sections'][0]['heading'] == 'Authentication'
        assert result['sections'][0]['content'] == 'Learn about auth methods.'
        assert 'subsections' in result['sections'][0]
        assert len(result['sections'][0]['subsections']) == 2
        
        # Check first subsection
        assert result['sections'][0]['subsections'][0]['heading'] == 'OAuth Setup'
        assert result['sections'][0]['subsections'][0]['content'] == 'Configure OAuth provider.'
        
        # Check second subsection
        assert result['sections'][0]['subsections'][1]['heading'] == 'API Keys'
        assert result['sections'][0]['subsections'][1]['content'] == 'Generate API keys.'
        
        # Check second section without subsections
        assert result['sections'][1]['heading'] == 'Endpoints'
        assert result['sections'][1]['content'] == 'Available REST endpoints.'
        assert result['sections'][1].get('subsections', []) == []

    def test_parse_multi_paragraph_content(self):
        """
        Given: Markdown sections with multiple paragraphs
        When: Parser extracts structure
        Then: Captures all content paragraphs (concatenated or as list)
        """
        # ARRANGE
        markdown = """# Getting Started

## Installation

First, install the package using pip.

Then, verify the installation.

Finally, configure your settings.

## Quick Start

Run the init command to begin."""
        parser = DocumentParser()
        
        # ACT
        result = parser.parse(markdown)
        
        # ASSERT
        assert result['title'] == 'Getting Started'
        assert len(result['sections']) == 2
        
        # Check first section with multiple paragraphs
        # Content should capture all paragraphs (implementation may concatenate or use list)
        installation_content = result['sections'][0]['content']
        assert 'install the package using pip' in installation_content
        assert 'verify the installation' in installation_content
        assert 'configure your settings' in installation_content
        
        # Check second section with single paragraph
        assert result['sections'][1]['heading'] == 'Quick Start'
        assert 'Run the init command' in result['sections'][1]['content']

    def test_parse_markdown_without_h1_title(self):
        """
        Given: Markdown starting with H2 (no H1 title)
        When: Parser extracts structure
        Then: Returns None for title and extracts sections normally
        """
        # ARRANGE
        markdown = """## First Section

Content for first section.

## Second Section

Content for second section."""
        parser = DocumentParser()
        
        # ACT
        result = parser.parse(markdown)
        
        # ASSERT
        # Should handle missing title gracefully
        assert result['title'] is None
        assert len(result['sections']) == 2
        
        # Sections should still be extracted
        assert result['sections'][0]['heading'] == 'First Section'
        assert result['sections'][0]['content'] == 'Content for first section.'
        assert result['sections'][1]['heading'] == 'Second Section'
        assert result['sections'][1]['content'] == 'Content for second section.'

    def test_parse_deeply_nested_subsections_h3_to_h6(self):
        """
        Given: Markdown with H1, H2, and deeply nested H3-H6 subsections
        When: Parser extracts structure
        Then: Returns hierarchical structure with up to 6 levels of nesting
        """
        # ARRANGE
        markdown = """# Technical Documentation

## Architecture

High-level architecture overview.

### Backend Services

The backend consists of multiple services.

#### API Gateway

Handles incoming requests and routing.

##### Authentication Service

Validates user credentials and tokens.

###### JWT Token Handler

Manages JWT token creation and validation.

##### Rate Limiting

Controls request throttling.

#### Database Layer

Manages data persistence.

### Frontend Components

User interface components."""
        parser = DocumentParser()
        
        # ACT
        result = parser.parse(markdown)
        
        # ASSERT
        assert result['title'] == 'Technical Documentation'
        assert len(result['sections']) == 1
        
        # H2: Architecture
        section = result['sections'][0]
        assert section['heading'] == 'Architecture'
        assert section['content'] == 'High-level architecture overview.'
        assert len(section['subsections']) == 2
        
        # H3: Backend Services
        backend = section['subsections'][0]
        assert backend['heading'] == 'Backend Services'
        assert backend['content'] == 'The backend consists of multiple services.'
        assert len(backend['subsections']) == 2
        
        # H4: API Gateway
        api_gateway = backend['subsections'][0]
        assert api_gateway['heading'] == 'API Gateway'
        assert api_gateway['content'] == 'Handles incoming requests and routing.'
        assert len(api_gateway['subsections']) == 2
        
        # H5: Authentication Service
        auth_service = api_gateway['subsections'][0]
        assert auth_service['heading'] == 'Authentication Service'
        assert auth_service['content'] == 'Validates user credentials and tokens.'
        assert len(auth_service['subsections']) == 1
        
        # H6: JWT Token Handler
        jwt_handler = auth_service['subsections'][0]
        assert jwt_handler['heading'] == 'JWT Token Handler'
        assert jwt_handler['content'] == 'Manages JWT token creation and validation.'
        assert jwt_handler.get('subsections', []) == []  # H6 is deepest, no further nesting
        
        # H5: Rate Limiting (sibling to Authentication Service)
        rate_limiting = api_gateway['subsections'][1]
        assert rate_limiting['heading'] == 'Rate Limiting'
        assert rate_limiting['content'] == 'Controls request throttling.'
        
        # H4: Database Layer (sibling to API Gateway)
        database = backend['subsections'][1]
        assert database['heading'] == 'Database Layer'
        assert database['content'] == 'Manages data persistence.'
        
        # H3: Frontend Components (sibling to Backend Services)
        frontend = section['subsections'][1]
        assert frontend['heading'] == 'Frontend Components'
        assert frontend['content'] == 'User interface components.'
