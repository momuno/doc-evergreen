"""PromptGenerator - LLM-powered intelligent prompt generation for documentation sections."""

from typing import Any, Dict, List


class PromptGenerator:
    """Generate documentation prompts based on section analysis and discovered sources.
    
    Creates specific, actionable prompts that guide LLM to recreate documentation
    content matching the original section's style and intent.
    """
    
    def __init__(self, llm_client: Any):
        """Initialize generator with LLM client.
        
        Args:
            llm_client: LLM client with generate() method
        """
        self.llm = llm_client
    
    def generate_prompt(
        self,
        section_heading: str,
        section_analysis: Dict,
        discovered_sources: List[str]
    ) -> Dict:
        """Generate a prompt that would recreate similar content.
        
        Args:
            section_heading: Section heading (e.g., "Installation")
            section_analysis: Analysis from ContentIntentAnalyzer
            discovered_sources: List of source file paths
            
        Returns:
            Dictionary with:
            - prompt: Generated prompt text
            - prompt_pattern: Pattern classification
            - confidence: Quality confidence ('high', 'medium', 'low')
        """
        # Build context for LLM
        context = self._build_context(
            section_heading,
            section_analysis,
            discovered_sources
        )
        
        # Call LLM with slight creativity (temperature=0.3)
        generated_text = self.llm.generate(context, temperature=0.3)
        
        # Extract prompt from response
        prompt = self._extract_prompt(generated_text)
        
        # Classify prompt pattern
        pattern = self._classify_prompt_pattern(section_analysis)
        
        # Assess confidence
        confidence = self._assess_confidence(prompt)
        
        return {
            'prompt': prompt,
            'prompt_pattern': pattern,
            'confidence': confidence
        }
    
    def _build_context(
        self,
        section_heading: str,
        section_analysis: Dict,
        discovered_sources: List[str]
    ) -> str:
        """Build LLM context for prompt generation.
        
        Args:
            section_heading: Section heading
            section_analysis: Section analysis metadata
            discovered_sources: Available source files
            
        Returns:
            Formatted context string
        """
        # Format sources
        sources_text = self._format_sources(discovered_sources)
        
        context = f"""Generate a documentation prompt for a section that would guide content generation.

**Section Heading:** {section_heading}

**Section Analysis:**
- Type: {section_analysis['section_type']}
- Quadrant: {section_analysis['divio_quadrant']}
- Intent: {section_analysis['intent']}
- Key Topics: {', '.join(section_analysis['key_topics'])}
- Style: {section_analysis['content_style']}
- Audience: {section_analysis['target_audience']}

**Available Sources:**
{sources_text}

**Task:** Generate a prompt that would guide an LLM to create content for this section. The prompt should:
1. Be specific to this section's purpose and topics
2. Reference the available sources when relevant
3. Match the content style ({section_analysis['content_style']})
4. Be actionable and clear
5. Include any specific instructions based on section type

**Example Prompts:**

For Installation (how-to):
"Provide clear installation instructions for both standard users and developers. Include pip installation command from pyproject.toml for users, and git clone + editable install for developers. Keep it concise and actionable. List prerequisites if any are mentioned in the sources."

For API Reference (reference):
"Document the main API endpoints defined in the source files. For each endpoint, include: route path, HTTP methods, parameters, return values, and example usage. Use the actual function signatures from the code. Keep descriptions brief and factual."

For Architecture (explanation):
"Explain the high-level architecture of the system based on the core modules. Describe the main components, their responsibilities, and how they interact. Focus on 'why' decisions were made, not just 'what' exists. Help readers understand the design philosophy."

For Tutorial (tutorial):
"Create a step-by-step tutorial that teaches users the core concepts through hands-on examples. Start simple and gradually introduce complexity. Explain why each step matters. Make it beginner-friendly and ensure all code examples work."

**Your Generated Prompt:**
(Respond with ONLY the prompt text, no additional commentary)"""
        
        return context
    
    def _format_sources(self, sources: List[str]) -> str:
        """Format source file list for display.
        
        Args:
            sources: List of source file paths
            
        Returns:
            Formatted source list string
        """
        if not sources:
            return "No specific sources identified."
        
        formatted = []
        for source in sources:
            formatted.append(f"- {source}")
        
        return '\n'.join(formatted)
    
    def _extract_prompt(self, generated_text: str) -> str:
        """Extract prompt from LLM response.
        
        Args:
            generated_text: Raw LLM response
            
        Returns:
            Extracted prompt text
        """
        # Clean up response
        prompt = generated_text.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Here's the prompt:",
            "Here is the prompt:",
            "Prompt:",
            "Generated prompt:",
            "**Prompt:**",
            "**Your Generated Prompt:**"
        ]
        
        for prefix in prefixes_to_remove:
            if prompt.lower().startswith(prefix.lower()):
                prompt = prompt[len(prefix):].strip()
        
        # Remove quotes if wrapped
        if prompt.startswith('"') and prompt.endswith('"'):
            prompt = prompt[1:-1]
        if prompt.startswith("'") and prompt.endswith("'"):
            prompt = prompt[1:-1]
        
        return prompt
    
    def _classify_prompt_pattern(self, section_analysis: Dict) -> str:
        """Classify prompt pattern based on section analysis.
        
        Args:
            section_analysis: Section analysis metadata
            
        Returns:
            Prompt pattern classification
        """
        quadrant = section_analysis['divio_quadrant']
        section_type = section_analysis['section_type']
        
        # Tutorial pattern
        if quadrant == 'tutorial':
            return 'tutorial_step_by_step'
        
        # How-to patterns
        if quadrant == 'how-to':
            if section_type == 'installation':
                return 'instructional_how_to'
            return 'instructional_how_to'
        
        # Reference pattern
        if quadrant == 'reference':
            return 'reference_technical'
        
        # Explanation pattern
        if quadrant == 'explanation':
            return 'explanation_conceptual'
        
        # Generic fallback
        return 'generic'
    
    def _assess_confidence(self, prompt: str) -> str:
        """Assess confidence in generated prompt quality.
        
        Args:
            prompt: Generated prompt text
            
        Returns:
            Confidence level ('high', 'medium', 'low')
        """
        # Basic heuristic: length and specificity
        if len(prompt) > 100:
            return 'high'
        elif len(prompt) > 50:
            return 'medium'
        else:
            return 'low'
