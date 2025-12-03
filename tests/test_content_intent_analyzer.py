"""Tests for ContentIntentAnalyzer - Sprint 3 Deliverable 1 (RED phase)."""

import pytest
from unittest.mock import Mock


class TestContentIntentAnalyzer:
    """Test suite for ContentIntentAnalyzer."""
    
    def test_analyze_installation_section(self):
        """Test analyzing an installation section."""
        from doc_evergreen.reverse import ContentIntentAnalyzer
        
        # Mock LLM client
        mock_llm = Mock()
        mock_llm.generate.return_value = """{
            "section_type": "installation",
            "divio_quadrant": "how-to",
            "key_topics": ["installation", "package management", "pip"],
            "intent": "Guide users through installing the package",
            "technical_terms": ["pip", "package manager", "dependencies"],
            "content_style": "instructional",
            "target_audience": "users"
        }"""
        
        analyzer = ContentIntentAnalyzer(llm_client=mock_llm)
        
        section_heading = "Installation"
        section_content = """
        To install doc-evergreen, run:
        ```bash
        pip install doc-evergreen
        ```
        
        For development installation:
        ```bash
        git clone https://github.com/user/doc-evergreen.git
        cd doc-evergreen
        pip install -e ".[dev]"
        ```
        """
        
        result = analyzer.analyze_section(section_heading, section_content)
        
        # Validate structure
        assert isinstance(result, dict)
        assert 'section_type' in result
        assert 'divio_quadrant' in result
        assert 'key_topics' in result
        assert 'intent' in result
        assert 'technical_terms' in result
        assert 'content_style' in result
        assert 'target_audience' in result
        
        # Validate values
        assert result['section_type'] == 'installation'
        assert result['divio_quadrant'] == 'how-to'
        assert 'installation' in result['key_topics']
        assert 'pip' in result['technical_terms']
        
        # Verify LLM was called with appropriate prompt
        mock_llm.generate.assert_called_once()
        call_args = mock_llm.generate.call_args
        prompt = call_args[0][0]
        assert 'Installation' in prompt
        assert 'pip install' in prompt
    
    def test_analyze_api_reference_section(self):
        """Test analyzing an API reference section."""
        from doc_evergreen.reverse import ContentIntentAnalyzer
        
        mock_llm = Mock()
        mock_llm.generate.return_value = """{
            "section_type": "api-reference",
            "divio_quadrant": "reference",
            "key_topics": ["API", "endpoints", "routes", "handlers"],
            "intent": "Document the API endpoints and their usage",
            "technical_terms": ["REST", "HTTP", "endpoint", "route"],
            "content_style": "reference",
            "target_audience": "developers"
        }"""
        
        analyzer = ContentIntentAnalyzer(llm_client=mock_llm)
        
        section_heading = "API Reference"
        section_content = """
        ## Endpoints
        
        ### GET /api/users
        Returns a list of users.
        
        ### POST /api/users
        Creates a new user.
        """
        
        result = analyzer.analyze_section(section_heading, section_content)
        
        assert result['section_type'] == 'api-reference'
        assert result['divio_quadrant'] == 'reference'
        assert 'API' in result['key_topics']
        assert result['target_audience'] == 'developers'
    
    def test_analyze_architecture_section(self):
        """Test analyzing an architecture/explanation section."""
        from doc_evergreen.reverse import ContentIntentAnalyzer
        
        mock_llm = Mock()
        mock_llm.generate.return_value = """{
            "section_type": "architecture",
            "divio_quadrant": "explanation",
            "key_topics": ["architecture", "design", "components", "patterns"],
            "intent": "Explain the system architecture and design decisions",
            "technical_terms": ["module", "component", "pattern", "design"],
            "content_style": "narrative",
            "target_audience": "architects"
        }"""
        
        analyzer = ContentIntentAnalyzer(llm_client=mock_llm)
        
        section_heading = "Architecture"
        section_content = """
        The system follows a modular architecture with three main components:
        - Template parser
        - Source discoverer  
        - Document generator
        
        This design allows for flexibility and separation of concerns.
        """
        
        result = analyzer.analyze_section(section_heading, section_content)
        
        assert result['section_type'] == 'architecture'
        assert result['divio_quadrant'] == 'explanation'
        assert 'architecture' in result['key_topics']
        assert result['content_style'] == 'narrative'
    
    def test_content_truncation(self):
        """Test that long content is truncated to control LLM costs."""
        from doc_evergreen.reverse import ContentIntentAnalyzer
        
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"section_type": "other", "divio_quadrant": "explanation", "key_topics": [], "intent": "test", "technical_terms": [], "content_style": "descriptive", "target_audience": "users"}'
        
        analyzer = ContentIntentAnalyzer(llm_client=mock_llm)
        
        # Create very long content (>2000 chars)
        long_content = "x" * 3000
        
        analyzer.analyze_section("Test", long_content)
        
        # Verify prompt doesn't contain full content
        call_args = mock_llm.generate.call_args
        prompt = call_args[0][0]
        # Content should be truncated to ~2000 chars
        assert len(prompt) < 3500  # Prompt includes other text, so allow some buffer
    
    def test_temperature_zero_for_deterministic_results(self):
        """Test that analyzer uses temperature=0 for consistency."""
        from doc_evergreen.reverse import ContentIntentAnalyzer
        
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"section_type": "other", "divio_quadrant": "explanation", "key_topics": [], "intent": "test", "technical_terms": [], "content_style": "descriptive", "target_audience": "users"}'
        
        analyzer = ContentIntentAnalyzer(llm_client=mock_llm)
        analyzer.analyze_section("Test", "Content")
        
        # Verify temperature=0 was used
        call_args = mock_llm.generate.call_args
        assert call_args[1]['temperature'] == 0
    
    def test_handle_malformed_json_response(self):
        """Test graceful handling of malformed LLM responses."""
        from doc_evergreen.reverse import ContentIntentAnalyzer
        
        mock_llm = Mock()
        mock_llm.generate.return_value = "This is not valid JSON"
        
        analyzer = ContentIntentAnalyzer(llm_client=mock_llm)
        
        # Should raise appropriate error or return default
        with pytest.raises(ValueError, match="JSON"):
            analyzer.analyze_section("Test", "Content")
    
    def test_handle_missing_fields_in_response(self):
        """Test handling of incomplete LLM responses."""
        from doc_evergreen.reverse import ContentIntentAnalyzer
        
        mock_llm = Mock()
        # Missing several required fields
        mock_llm.generate.return_value = '{"section_type": "installation"}'
        
        analyzer = ContentIntentAnalyzer(llm_client=mock_llm)
        
        # Should raise appropriate error
        with pytest.raises(ValueError, match="Missing required fields"):
            analyzer.analyze_section("Test", "Content")
