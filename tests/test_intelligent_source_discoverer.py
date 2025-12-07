"""Tests for IntelligentSourceDiscoverer - integrated 3-stage pipeline."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

try:
    from doc_evergreen.reverse.intelligent_source_discoverer import IntelligentSourceDiscoverer
except ImportError:
    IntelligentSourceDiscoverer = None


class TestIntelligentSourceDiscoverer:
    """Tests for integrated source discovery pipeline."""
    
    def test_discover_sources_returns_top_results(self, tmp_path):
        """
        Given: Project with various source files
        When: Discover sources for a section
        Then: Returns top 3-5 most relevant sources
        """
        # ARRANGE
        # Create project structure
        src = tmp_path / "src"
        src.mkdir()
        (src / "api.py").write_text("def get_users(): pass")
        (src / "models.py").write_text("class User: pass")
        
        # Mock LLM client
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 8, "reasoning": "Relevant", "confidence": "high"}'
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="API Reference",
            section_content="The API provides user endpoints",
            max_sources=5
        )
        
        # ASSERT
        assert isinstance(results, list)
        assert len(results) <= 5
        # Each result should have required fields
        for result in results:
            assert 'path' in result
            assert 'relevance_score' in result
            assert 'match_reason' in result
            assert 'discovery_method' in result
    
    def test_discover_integrates_all_three_stages(self, tmp_path):
        """
        Given: Section to discover sources for
        When: Run discovery pipeline
        Then: Uses pattern matching, semantic search, and LLM scoring
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "api_routes.py").write_text("def api_handler(): pass")
        
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 9, "reasoning": "Implements API", "confidence": "high"}'
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="API Reference",
            section_content="The API provides REST endpoints for data access",
            max_sources=5
        )
        
        # ASSERT
        # LLM should have been called (Stage 3)
        assert mock_llm.generate.call_count > 0
        
        # Results should indicate discovery method
        if results:
            assert any('llm' in r['discovery_method'].lower() for r in results)
    
    def test_discover_deduplicates_candidates(self, tmp_path):
        """
        Given: Same file found by multiple stages
        When: Run discovery
        Then: File appears only once in results
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        # File that will match both pattern and semantic search
        (src / "setup.py").write_text("# Installation setup file")
        
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 8, "reasoning": "Installation file", "confidence": "high"}'
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="Installation",
            section_content="Install using pip install my-project",
            max_sources=10
        )
        
        # ASSERT
        # Count occurrences of setup.py in results
        setup_py_count = sum(1 for r in results if 'setup.py' in r['path'])
        assert setup_py_count <= 1, "setup.py should appear at most once"
    
    def test_discover_limits_llm_calls_to_top_candidates(self, tmp_path):
        """
        Given: Many candidate files from stages 1+2
        When: Run discovery
        Then: Only scores top 10 candidates with LLM (cost optimization)
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        
        # Create 20 files
        for i in range(20):
            (src / f"module_{i}.py").write_text(f"def function_{i}(): pass")
        
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 7, "reasoning": "Relevant", "confidence": "medium"}'
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="Functions",
            section_content="Python function implementations",
            max_sources=5
        )
        
        # ASSERT
        # LLM should be called at most 10 times (top 10 candidates)
        assert mock_llm.generate.call_count <= 10, f"LLM called {mock_llm.generate.call_count} times, should be ≤10"
    
    def test_discover_filters_by_minimum_score(self, tmp_path):
        """
        Given: LLM returns mix of high and low scores
        When: Run discovery
        Then: Only returns files with score >= 5
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "high_relevance.py").write_text("relevant code")
        (src / "low_relevance.py").write_text("unrelated code")
        
        # Mock LLM to return different scores
        mock_llm = Mock()
        mock_llm.generate.side_effect = [
            '{"score": 8, "reasoning": "Relevant", "confidence": "high"}',
            '{"score": 3, "reasoning": "Not relevant", "confidence": "high"}'
        ]
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="Test",
            section_content="Test content",
            max_sources=10
        )
        
        # ASSERT
        # All results should have score >= 5
        assert all(r['relevance_score'] >= 5 for r in results)
    
    def test_discover_sorts_by_relevance_score(self, tmp_path):
        """
        Given: Multiple files with different scores
        When: Run discovery
        Then: Results sorted by score descending
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "file1.py").write_text("code 1")
        (src / "file2.py").write_text("code 2")
        (src / "file3.py").write_text("code 3")
        
        mock_llm = Mock()
        mock_llm.generate.side_effect = [
            '{"score": 6, "reasoning": "Medium", "confidence": "medium"}',
            '{"score": 9, "reasoning": "High", "confidence": "high"}',
            '{"score": 7, "reasoning": "Good", "confidence": "high"}'
        ]
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="Test",
            section_content="Test content",
            max_sources=10
        )
        
        # ASSERT
        # Verify descending order
        scores = [r['relevance_score'] for r in results]
        assert scores == sorted(scores, reverse=True), f"Scores not sorted: {scores}"
    
    def test_extract_key_terms_from_content(self, tmp_path):
        """
        Given: Section content with important terms
        When: Extract key terms
        Then: Returns relevant keywords (no stop words)
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 5, "reasoning": "Test", "confidence": "medium"}'
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        key_terms = discoverer._extract_key_terms(
            "The API provides authentication endpoints for user login and token validation"
        )
        
        # ASSERT
        assert isinstance(key_terms, list)
        assert len(key_terms) > 0
        
        # Should include technical terms
        expected_terms = ['api', 'authentication', 'endpoints', 'user', 'login', 'token', 'validation']
        found_terms = [term.lower() for term in key_terms]
        
        # At least some expected terms should be found
        matches = [term for term in expected_terms if term in found_terms]
        assert len(matches) >= 3, f"Expected technical terms, got: {key_terms}"
        
        # Should NOT include stop words
        stop_words = ['the', 'for', 'and']
        assert not any(stop in found_terms for stop in stop_words)
    
    def test_extract_key_terms_limits_count(self, tmp_path):
        """
        Given: Long content with many terms
        When: Extract key terms
        Then: Returns top N most frequent (e.g., 10)
        """
        # ARRANGE
        mock_llm = Mock()
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # Long content with many different terms
        long_content = " ".join([f"term{i} concept{i} feature{i}" for i in range(50)])
        
        # ACT
        key_terms = discoverer._extract_key_terms(long_content)
        
        # ASSERT
        # Should limit to reasonable number (e.g., 10-15)
        assert len(key_terms) <= 15
        assert len(key_terms) > 0
    
    def test_discover_handles_no_candidates_gracefully(self, tmp_path):
        """
        Given: Project with no matching files
        When: Run discovery
        Then: Returns empty list without errors
        """
        # ARRANGE
        # Empty project or files that don't match
        src = tmp_path / "src"
        src.mkdir()
        (src / "unrelated.txt").write_text("unrelated content")
        
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 2, "reasoning": "Not relevant", "confidence": "high"}'
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="Quantum Computing",
            section_content="Advanced quantum algorithms",
            max_sources=5
        )
        
        # ASSERT
        assert results == []
    
    def test_discover_includes_confidence_in_results(self, tmp_path):
        """
        Given: LLM returns results with confidence levels
        When: Run discovery
        Then: Results include confidence field
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "test.py").write_text("test code")
        
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 8, "reasoning": "Relevant", "confidence": "high"}'
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=tmp_path,
            llm_client=mock_llm
        )
        
        # ACT
        results = discoverer.discover_sources(
            section_heading="Test",
            section_content="Test content",
            max_sources=5
        )
        
        # ASSERT
        if results:
            for result in results:
                assert 'confidence' in result
                assert result['confidence'] in ['low', 'medium', 'high']
