"""Tests for PromptGenerator - Sprint 3 Deliverable 2 (RED phase)."""

import pytest
from unittest.mock import Mock


class TestPromptGenerator:
    """Test suite for PromptGenerator."""
    
    def test_generate_installation_prompt(self):
        """Test generating prompt for installation section."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = """Provide clear installation instructions for both standard users and developers. Include pip installation command from pyproject.toml for users, and git clone + editable install for developers. Keep it concise and actionable. List prerequisites if any are mentioned in the sources."""
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_heading = "Installation"
        section_analysis = {
            'section_type': 'installation',
            'divio_quadrant': 'how-to',
            'intent': 'Guide users through installing the package',
            'key_topics': ['installation', 'pip', 'development setup'],
            'content_style': 'instructional',
            'target_audience': 'users'
        }
        sources = ['pyproject.toml', 'setup.py']
        
        result = generator.generate_prompt(section_heading, section_analysis, sources)
        
        # Validate structure
        assert isinstance(result, dict)
        assert 'prompt' in result
        assert 'prompt_pattern' in result
        assert 'confidence' in result
        
        # Validate prompt quality
        assert len(result['prompt']) > 50, "Prompt should be substantial"
        assert 'install' in result['prompt'].lower(), "Installation prompt should mention 'install'"
        
        # Validate pattern classification
        assert result['prompt_pattern'] == 'instructional_how_to'
        
        # Verify LLM was called
        mock_llm.generate.assert_called_once()
    
    def test_generate_api_reference_prompt(self):
        """Test generating prompt for API reference section."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = """Document the main API endpoints defined in the source files. For each endpoint, include: route path, HTTP methods, parameters, return values, and example usage. Use the actual function signatures from the code. Keep descriptions brief and factual."""
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_heading = "API Reference"
        section_analysis = {
            'section_type': 'api-reference',
            'divio_quadrant': 'reference',
            'intent': 'Document the API endpoints and their usage',
            'key_topics': ['API', 'endpoints', 'routes'],
            'content_style': 'reference',
            'target_audience': 'developers'
        }
        sources = ['src/api/routes.py', 'src/api/handlers.py']
        
        result = generator.generate_prompt(section_heading, section_analysis, sources)
        
        assert result['prompt_pattern'] == 'reference_technical'
        assert 'API' in result['prompt'] or 'endpoint' in result['prompt'].lower()
        assert len(result['prompt']) > 50
    
    def test_generate_architecture_prompt(self):
        """Test generating prompt for architecture/explanation section."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = """Explain the high-level architecture of the system based on the core modules. Describe the main components, their responsibilities, and how they interact. Focus on 'why' decisions were made, not just 'what' exists. Help readers understand the design philosophy."""
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_heading = "Architecture"
        section_analysis = {
            'section_type': 'architecture',
            'divio_quadrant': 'explanation',
            'intent': 'Explain the system architecture and design decisions',
            'key_topics': ['architecture', 'design', 'components'],
            'content_style': 'narrative',
            'target_audience': 'architects'
        }
        sources = ['src/core/module.py', 'docs/design.md']
        
        result = generator.generate_prompt(section_heading, section_analysis, sources)
        
        assert result['prompt_pattern'] == 'explanation_conceptual'
        assert len(result['prompt']) > 50
    
    def test_generate_tutorial_prompt(self):
        """Test generating prompt for tutorial section."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = """Create a step-by-step tutorial that teaches users how to build their first documentation template. Start with a simple example and gradually introduce concepts. Include explanations of why each step matters. Make it beginner-friendly and hands-on."""
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_heading = "Getting Started Tutorial"
        section_analysis = {
            'section_type': 'usage',
            'divio_quadrant': 'tutorial',
            'intent': 'Teach users the basics through hands-on example',
            'key_topics': ['tutorial', 'getting started', 'basics'],
            'content_style': 'instructional',
            'target_audience': 'users'
        }
        sources = ['examples/basic.py', 'docs/tutorial.md']
        
        result = generator.generate_prompt(section_heading, section_analysis, sources)
        
        assert result['prompt_pattern'] == 'tutorial_step_by_step'
        assert len(result['prompt']) > 50
    
    def test_prompt_includes_sources(self):
        """Test that generated prompt references the available sources."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = "Based on pyproject.toml, provide installation instructions."
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_analysis = {
            'section_type': 'installation',
            'divio_quadrant': 'how-to',
            'intent': 'Guide users through installation',
            'key_topics': ['installation'],
            'content_style': 'instructional',
            'target_audience': 'users'
        }
        sources = ['pyproject.toml']
        
        generator.generate_prompt("Installation", section_analysis, sources)
        
        # Verify sources were included in LLM context
        call_args = mock_llm.generate.call_args
        prompt_context = call_args[0][0]
        assert 'pyproject.toml' in prompt_context
    
    def test_temperature_for_creativity(self):
        """Test that generator uses appropriate temperature for slight creativity."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = "Test prompt"
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_analysis = {
            'section_type': 'other',
            'divio_quadrant': 'explanation',
            'intent': 'test',
            'key_topics': [],
            'content_style': 'descriptive',
            'target_audience': 'users'
        }
        
        generator.generate_prompt("Test", section_analysis, [])
        
        # Verify temperature is between 0 and 0.5 (slight creativity, still deterministic)
        call_args = mock_llm.generate.call_args
        temperature = call_args[1].get('temperature', 0)
        assert 0 <= temperature <= 0.5, "Temperature should allow slight creativity"
    
    def test_confidence_based_on_prompt_length(self):
        """Test that confidence is assessed based on prompt quality."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_analysis = {
            'section_type': 'installation',
            'divio_quadrant': 'how-to',
            'intent': 'Guide users',
            'key_topics': ['installation'],
            'content_style': 'instructional',
            'target_audience': 'users'
        }
        
        # Test high confidence with substantial prompt
        mock_llm.generate.return_value = "This is a detailed and substantial prompt with specific instructions for generating installation documentation that covers multiple aspects."
        result_high = generator.generate_prompt("Test", section_analysis, [])
        assert result_high['confidence'] == 'high'
        
        # Test medium/low confidence with short prompt
        mock_llm.generate.return_value = "Install it."
        result_low = generator.generate_prompt("Test", section_analysis, [])
        assert result_low['confidence'] in ['medium', 'low']
    
    def test_few_shot_examples_in_prompt(self):
        """Test that generator includes few-shot examples to improve quality."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = "Test prompt"
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_analysis = {
            'section_type': 'installation',
            'divio_quadrant': 'how-to',
            'intent': 'Guide users',
            'key_topics': ['installation'],
            'content_style': 'instructional',
            'target_audience': 'users'
        }
        
        generator.generate_prompt("Installation", section_analysis, ['pyproject.toml'])
        
        # Verify few-shot examples are included
        call_args = mock_llm.generate.call_args
        prompt_context = call_args[0][0]
        assert 'Example' in prompt_context or 'example' in prompt_context
    
    def test_pattern_classification_logic(self):
        """Test that prompt patterns are correctly classified."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = "Test prompt"
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        # Test tutorial pattern
        tutorial_analysis = {
            'section_type': 'usage',
            'divio_quadrant': 'tutorial',
            'intent': 'Teach',
            'key_topics': [],
            'content_style': 'instructional',
            'target_audience': 'users'
        }
        result = generator.generate_prompt("Tutorial", tutorial_analysis, [])
        assert result['prompt_pattern'] == 'tutorial_step_by_step'
        
        # Test how-to + installation pattern
        howto_install_analysis = {
            'section_type': 'installation',
            'divio_quadrant': 'how-to',
            'intent': 'Guide',
            'key_topics': [],
            'content_style': 'instructional',
            'target_audience': 'users'
        }
        result = generator.generate_prompt("Installation", howto_install_analysis, [])
        assert result['prompt_pattern'] == 'instructional_how_to'
        
        # Test reference pattern
        reference_analysis = {
            'section_type': 'api-reference',
            'divio_quadrant': 'reference',
            'intent': 'Document',
            'key_topics': [],
            'content_style': 'reference',
            'target_audience': 'developers'
        }
        result = generator.generate_prompt("API", reference_analysis, [])
        assert result['prompt_pattern'] == 'reference_technical'
        
        # Test explanation pattern
        explanation_analysis = {
            'section_type': 'architecture',
            'divio_quadrant': 'explanation',
            'intent': 'Explain',
            'key_topics': [],
            'content_style': 'narrative',
            'target_audience': 'architects'
        }
        result = generator.generate_prompt("Architecture", explanation_analysis, [])
        assert result['prompt_pattern'] == 'explanation_conceptual'
    
    def test_handle_empty_sources_list(self):
        """Test graceful handling when no sources are available."""
        from doc_evergreen.reverse import PromptGenerator
        
        mock_llm = Mock()
        mock_llm.generate.return_value = "Generate documentation for this section."
        
        generator = PromptGenerator(llm_client=mock_llm)
        
        section_analysis = {
            'section_type': 'other',
            'divio_quadrant': 'explanation',
            'intent': 'Explain concept',
            'key_topics': ['concept'],
            'content_style': 'descriptive',
            'target_audience': 'users'
        }
        
        # Should not fail with empty sources
        result = generator.generate_prompt("Concept", section_analysis, [])
        assert 'prompt' in result
        assert len(result['prompt']) > 0
