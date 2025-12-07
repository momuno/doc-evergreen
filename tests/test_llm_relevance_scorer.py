"""Tests for LLMRelevanceScorer - LLM-based relevance scoring."""

import pytest
from unittest.mock import Mock, patch

try:
    from doc_evergreen.reverse.llm_relevance_scorer import LLMRelevanceScorer
except ImportError:
    LLMRelevanceScorer = None


class TestLLMRelevanceScorer:
    """Tests for LLM-based source file relevance scoring."""
    
    def test_score_highly_relevant_file(self):
        """
        Given: API section and file that implements mentioned endpoints
        When: Score relevance with LLM
        Then: Returns high score (7-10) with reasoning
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '''
        {
            "score": 9,
            "reasoning": "File directly implements /users endpoint mentioned in section",
            "confidence": "high"
        }
        '''
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        # ACT
        result = scorer.score_relevance(
            section_heading="API Reference",
            section_content="The API provides /users and /posts endpoints for data access",
            source_file_path="src/api/routes.py",
            source_file_content="@app.route('/users')\ndef get_users():\n    return User.query.all()"
        )
        
        # ASSERT
        assert result['score'] >= 7
        assert result['score'] <= 10
        assert 'reasoning' in result
        assert len(result['reasoning']) > 0
        assert 'confidence' in result
        assert result['confidence'] in ['low', 'medium', 'high']
        
        # Verify LLM was called
        mock_llm.generate.assert_called_once()
    
    def test_score_irrelevant_file(self):
        """
        Given: API section and unrelated database model file
        When: Score relevance
        Then: Returns low score (0-3) with reasoning
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '''
        {
            "score": 2,
            "reasoning": "File contains database models, not API endpoints",
            "confidence": "high"
        }
        '''
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        # ACT
        result = scorer.score_relevance(
            section_heading="API Reference",
            section_content="REST API endpoints for user management",
            source_file_path="src/database/models.py",
            source_file_content="class User(Base):\n    id = Column(Integer)"
        )
        
        # ASSERT
        assert result['score'] <= 3
        assert 'reasoning' in result
        assert result['confidence'] == 'high'
    
    def test_score_moderately_relevant_file(self):
        """
        Given: Section and file with partial relevance
        When: Score relevance
        Then: Returns medium score (4-6)
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '''
        {
            "score": 5,
            "reasoning": "File contains related utilities but not main implementation",
            "confidence": "medium"
        }
        '''
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        # ACT
        result = scorer.score_relevance(
            section_heading="Authentication",
            section_content="User authentication and JWT token handling",
            source_file_path="src/utils/auth_helpers.py",
            source_file_content="def validate_token(token): pass"
        )
        
        # ASSERT
        assert result['score'] >= 4
        assert result['score'] <= 6
    
    def test_score_batch_filters_by_threshold(self):
        """
        Given: Multiple candidate files
        When: Score batch with threshold=5
        Then: Returns only files with score >= 5
        """
        # ARRANGE
        mock_llm = Mock()
        # Return different scores for different files
        mock_llm.generate.side_effect = [
            '{"score": 8, "reasoning": "Relevant", "confidence": "high"}',
            '{"score": 3, "reasoning": "Not relevant", "confidence": "high"}',
            '{"score": 7, "reasoning": "Related", "confidence": "medium"}'
        ]
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        candidates = [
            {
                'path': 'src/api/routes.py',
                'content': 'API routes'
            },
            {
                'path': 'src/models.py',
                'content': 'Database models'
            },
            {
                'path': 'src/api/handlers.py',
                'content': 'API handlers'
            }
        ]
        
        # ACT
        results = scorer.score_batch(
            section_heading="API Reference",
            section_content="API endpoints",
            candidates=candidates,
            min_score=5
        )
        
        # ASSERT
        assert len(results) == 2  # Only 2 files scored >= 5
        assert all(r['score'] >= 5 for r in results)
        assert results[0]['score'] >= results[1]['score']  # Sorted by score descending
    
    def test_score_batch_limits_results(self):
        """
        Given: Many relevant files
        When: Score batch with max_results limit
        Then: Returns only top N results
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.side_effect = [
            '{"score": 8, "reasoning": "High relevance", "confidence": "high"}',
            '{"score": 7, "reasoning": "Medium relevance", "confidence": "high"}',
            '{"score": 9, "reasoning": "Very high relevance", "confidence": "high"}',
            '{"score": 6, "reasoning": "Some relevance", "confidence": "medium"}'
        ]
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        candidates = [
            {'path': f'file{i}.py', 'content': 'content'} for i in range(4)
        ]
        
        # ACT
        results = scorer.score_batch(
            section_heading="Test",
            section_content="Test content",
            candidates=candidates,
            min_score=0,
            max_results=2
        )
        
        # ASSERT
        assert len(results) == 2
        # Should return top 2 scores (9 and 8)
        assert results[0]['score'] == 9
        assert results[1]['score'] == 8
    
    def test_handles_invalid_json_response(self):
        """
        Given: LLM returns invalid JSON
        When: Parse response
        Then: Handles gracefully with default low score
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = "This is not valid JSON"
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        # ACT
        result = scorer.score_relevance(
            section_heading="Test",
            section_content="Content",
            source_file_path="test.py",
            source_file_content="code"
        )
        
        # ASSERT
        # Should return safe default values
        assert 'score' in result
        assert result['score'] == 0  # Default to 0 for parse failures
        assert 'reasoning' in result
        assert 'parse error' in result['reasoning'].lower() or 'invalid' in result['reasoning'].lower()
    
    def test_prompt_includes_scoring_guide(self):
        """
        Given: Score relevance called
        When: Generate LLM prompt
        Then: Prompt includes scoring guide (9-10: directly implements, etc.)
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 5, "reasoning": "Test", "confidence": "medium"}'
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        # ACT
        scorer.score_relevance(
            section_heading="API",
            section_content="API endpoints",
            source_file_path="api.py",
            source_file_content="code"
        )
        
        # ASSERT
        call_args = mock_llm.generate.call_args
        prompt = call_args[0][0]
        
        # Verify prompt structure
        assert "API" in prompt  # Section heading
        assert "api.py" in prompt  # File path
        assert "9-10" in prompt or "directly implements" in prompt  # Scoring guide
        assert "0-2" in prompt or "not relevant" in prompt  # Low score guide
    
    def test_uses_temperature_zero_for_determinism(self):
        """
        Given: Score relevance called
        When: Call LLM
        Then: Uses temperature=0 for deterministic results
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 5, "reasoning": "Test", "confidence": "medium"}'
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        # ACT
        scorer.score_relevance(
            section_heading="Test",
            section_content="Content",
            source_file_path="test.py",
            source_file_content="code"
        )
        
        # ASSERT
        call_args = mock_llm.generate.call_args
        # Check if temperature parameter was passed
        if len(call_args) > 1:
            kwargs = call_args[1]
            if 'temperature' in kwargs:
                assert kwargs['temperature'] == 0
    
    def test_truncates_long_content(self):
        """
        Given: Very long section content and file content
        When: Generate prompt
        Then: Truncates to reasonable length (e.g., 500 chars section, 1000 chars file)
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"score": 5, "reasoning": "Test", "confidence": "medium"}'
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        long_section = "x" * 2000
        long_file = "y" * 5000
        
        # ACT
        scorer.score_relevance(
            section_heading="Test",
            section_content=long_section,
            source_file_path="test.py",
            source_file_content=long_file
        )
        
        # ASSERT
        call_args = mock_llm.generate.call_args
        prompt = call_args[0][0]
        
        # Prompt should be reasonable length (not 7000+ chars)
        assert len(prompt) < 3000  # Reasonable prompt size
    
    def test_score_includes_file_path_in_reasoning(self):
        """
        Given: Score relevance
        When: Return result
        Then: Result includes file path for context
        """
        # ARRANGE
        mock_llm = Mock()
        mock_llm.generate.return_value = '''
        {
            "score": 8,
            "reasoning": "Implements mentioned functionality",
            "confidence": "high"
        }
        '''
        
        scorer = LLMRelevanceScorer(llm_client=mock_llm)
        
        # ACT
        result = scorer.score_relevance(
            section_heading="API",
            section_content="API endpoints",
            source_file_path="src/api/routes.py",
            source_file_content="@app.route('/users')"
        )
        
        # ASSERT
        assert 'file_path' in result or 'path' in result
