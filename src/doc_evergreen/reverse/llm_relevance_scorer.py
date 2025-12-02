"""LLMRelevanceScorer - LLM-based source file relevance scoring."""

import json
from typing import Dict, List, Any


class LLMRelevanceScorer:
    """Score source file relevance to documentation sections using LLM."""
    
    def __init__(self, llm_client: Any):
        """Initialize scorer with LLM client.
        
        Args:
            llm_client: LLM client with generate() method
        """
        self.llm = llm_client
    
    def score_relevance(
        self,
        section_heading: str,
        section_content: str,
        source_file_path: str,
        source_file_content: str
    ) -> Dict:
        """Score how relevant a source file is to a documentation section.
        
        Args:
            section_heading: Section heading (e.g., "API Reference")
            section_content: Section content text
            source_file_path: Path to source file
            source_file_content: Source file content
            
        Returns:
            Dictionary with:
            - score: 0-10 relevance score
            - reasoning: Explanation for score
            - confidence: 'low', 'medium', or 'high'
            - file_path: Source file path
        """
        # Truncate content to reasonable lengths
        section_excerpt = self._truncate_text(section_content, max_chars=500)
        file_excerpt = self._truncate_text(source_file_content, max_chars=1000)
        
        # Build prompt
        prompt = self._build_prompt(
            section_heading=section_heading,
            section_excerpt=section_excerpt,
            file_path=source_file_path,
            file_excerpt=file_excerpt
        )
        
        # Call LLM with temperature=0 for deterministic results
        try:
            response = self.llm.generate(prompt, temperature=0)
            parsed = self._parse_response(response)
            
            # Add file path to result
            parsed['file_path'] = source_file_path
            
            return parsed
        except Exception as e:
            # Graceful fallback on any error
            return {
                'score': 0,
                'reasoning': f'Parse error or LLM failure: {str(e)}',
                'confidence': 'low',
                'file_path': source_file_path
            }
    
    def score_batch(
        self,
        section_heading: str,
        section_content: str,
        candidates: List[Dict],
        min_score: int = 5,
        max_results: int = 10
    ) -> List[Dict]:
        """Score multiple candidate files and return filtered, ranked results.
        
        Args:
            section_heading: Section heading
            section_content: Section content
            candidates: List of candidate dicts with 'path' and 'content'
            min_score: Minimum score threshold (default: 5)
            max_results: Maximum number of results to return
            
        Returns:
            List of scored results, sorted by score descending
        """
        scored = []
        
        for candidate in candidates:
            result = self.score_relevance(
                section_heading=section_heading,
                section_content=section_content,
                source_file_path=candidate['path'],
                source_file_content=candidate['content']
            )
            
            # Filter by minimum score
            if result['score'] >= min_score:
                scored.append(result)
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit results
        return scored[:max_results]
    
    def _build_prompt(
        self,
        section_heading: str,
        section_excerpt: str,
        file_path: str,
        file_excerpt: str
    ) -> str:
        """Build LLM prompt for relevance scoring.
        
        Args:
            section_heading: Section heading
            section_excerpt: Truncated section content
            file_path: Source file path
            file_excerpt: Truncated file content
            
        Returns:
            Complete prompt string
        """
        prompt = f"""Given this documentation section:

Heading: {section_heading}
Content (excerpt): {section_excerpt}

Rate the relevance of this source file on a scale of 0-10:

File: {file_path}
Content (excerpt): {file_excerpt}

Scoring guide:
- 9-10: Directly implements features/APIs described in section
- 7-8: Closely related, provides important context
- 5-6: Somewhat related, mentions similar concepts
- 3-4: Tangentially related
- 0-2: Not relevant

Respond in JSON format:
{{
    "score": <0-10>,
    "reasoning": "<one sentence explanation>",
    "confidence": "<low|medium|high>"
}}"""
        
        return prompt
    
    def _truncate_text(self, text: str, max_chars: int) -> str:
        """Truncate text to maximum character length.
        
        Args:
            text: Text to truncate
            max_chars: Maximum characters
            
        Returns:
            Truncated text with ellipsis if truncated
        """
        if len(text) <= max_chars:
            return text
        
        return text[:max_chars] + "..."
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM JSON response.
        
        Args:
            response: LLM response string (should be JSON)
            
        Returns:
            Parsed dictionary with score, reasoning, confidence
            
        Raises:
            Exception: If parsing fails
        """
        try:
            # Strip whitespace and parse JSON
            parsed = json.loads(response.strip())
            
            # Validate required fields
            if 'score' not in parsed:
                raise ValueError("Missing 'score' field")
            if 'reasoning' not in parsed:
                raise ValueError("Missing 'reasoning' field")
            if 'confidence' not in parsed:
                raise ValueError("Missing 'confidence' field")
            
            # Validate score range
            score = int(parsed['score'])
            if score < 0 or score > 10:
                raise ValueError(f"Score {score} out of range 0-10")
            
            # Validate confidence
            confidence = parsed['confidence'].lower()
            if confidence not in ['low', 'medium', 'high']:
                raise ValueError(f"Invalid confidence: {confidence}")
            
            return {
                'score': score,
                'reasoning': str(parsed['reasoning']),
                'confidence': confidence
            }
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
        except (KeyError, ValueError, TypeError) as e:
            raise Exception(f"Invalid response format: {e}")
