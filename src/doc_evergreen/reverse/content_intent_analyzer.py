"""ContentIntentAnalyzer - LLM-powered section content analysis for intent extraction."""

import json
from typing import Any, Dict


class ContentIntentAnalyzer:
    """Analyze documentation section content with LLM to understand intent.
    
    Extracts metadata including:
    - Section type (installation, API reference, etc.)
    - Divio quadrant (tutorial, how-to, reference, explanation)
    - Key topics and technical terms
    - Content intent and style
    - Target audience
    """
    
    def __init__(self, llm_client: Any):
        """Initialize analyzer with LLM client.
        
        Args:
            llm_client: LLM client with generate() method
        """
        self.llm = llm_client
    
    def analyze_section(
        self,
        section_heading: str,
        section_content: str
    ) -> Dict:
        """Analyze a documentation section to extract metadata.
        
        Args:
            section_heading: Section heading (e.g., "Installation")
            section_content: Full section content text
            
        Returns:
            Dictionary with analysis results:
            {
                'section_type': str,
                'divio_quadrant': str,
                'key_topics': list[str],
                'intent': str,
                'technical_terms': list[str],
                'content_style': str,
                'target_audience': str
            }
            
        Raises:
            ValueError: If LLM response is malformed or missing required fields
        """
        # Truncate content to control costs (2000 chars max)
        content_excerpt = self._truncate_content(section_content, max_chars=2000)
        
        # Build analysis prompt
        prompt = self._build_prompt(section_heading, content_excerpt)
        
        # Call LLM with temperature=0 for deterministic results
        response = self.llm.generate(prompt, temperature=0)
        
        # Parse and validate JSON response
        analysis = self._parse_response(response)
        
        return analysis
    
    def _truncate_content(self, content: str, max_chars: int = 2000) -> str:
        """Truncate content to maximum character limit.
        
        Args:
            content: Full content text
            max_chars: Maximum characters to keep
            
        Returns:
            Truncated content
        """
        if len(content) <= max_chars:
            return content
        
        # Truncate at word boundary if possible
        truncated = content[:max_chars]
        last_space = truncated.rfind(' ')
        if last_space > max_chars * 0.8:  # Within 80% of limit
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def _build_prompt(self, section_heading: str, section_content: str) -> str:
        """Build analysis prompt for LLM.
        
        Args:
            section_heading: Section heading
            section_content: Section content (truncated)
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze this documentation section and extract metadata:

**Section Heading:** {section_heading}

**Section Content:**
{section_content}

Provide analysis in JSON format:

{{
    "section_type": "<installation|usage|api-reference|configuration|troubleshooting|contributing|architecture|other>",
    "divio_quadrant": "<tutorial|how-to|reference|explanation>",
    "key_topics": ["topic1", "topic2", ...],
    "intent": "<one sentence describing what this section does>",
    "technical_terms": ["term1", "term2", ...],
    "content_style": "<instructional|descriptive|reference|narrative>",
    "target_audience": "<users|developers|contributors|architects>"
}}

Classification guide:
- **Tutorial**: Learning-oriented, teaches concepts step-by-step
- **How-to**: Task-oriented, guides through solving specific problems
- **Reference**: Information-oriented, describes technical details
- **Explanation**: Understanding-oriented, clarifies concepts and design decisions

Respond with ONLY the JSON object, no additional text."""
        
        return prompt
    
    def _parse_response(self, response: str) -> Dict:
        """Parse and validate LLM JSON response.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Parsed and validated analysis dictionary
            
        Raises:
            ValueError: If response is malformed or missing required fields
        """
        # Try to parse JSON
        try:
            # Extract JSON if response contains additional text
            response = response.strip()
            
            # Handle markdown code blocks
            if response.startswith("```"):
                # Extract content between code fences
                lines = response.split('\n')
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        json_lines.append(line)
                response = '\n'.join(json_lines)
            
            analysis = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        
        # Validate required fields
        required_fields = [
            'section_type',
            'divio_quadrant',
            'key_topics',
            'intent',
            'technical_terms',
            'content_style',
            'target_audience'
        ]
        
        missing_fields = [field for field in required_fields if field not in analysis]
        if missing_fields:
            raise ValueError(f"Missing required fields in LLM response: {', '.join(missing_fields)}")
        
        # Validate field types
        if not isinstance(analysis['key_topics'], list):
            raise ValueError("key_topics must be a list")
        if not isinstance(analysis['technical_terms'], list):
            raise ValueError("technical_terms must be a list")
        
        return analysis
