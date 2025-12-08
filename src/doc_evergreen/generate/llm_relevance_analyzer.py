"""LLM-based file relevance analysis for generate-doc (Sprint 3)."""

import asyncio
import json
import logging
import os
from pathlib import Path

from anthropic import AsyncAnthropic

from doc_evergreen.generate.intent_context import IntentContext
from doc_evergreen.generate.repo_indexer import FileIndex, FileType
from doc_evergreen.generate.relevance_analyzer import RelevanceScore

logger = logging.getLogger(__name__)


class LLMRelevanceAnalyzer:
    """LLM-based file relevance analyzer.
    
    Uses Claude to analyze files for relevance to specific documentation
    purpose, providing custom reasoning and key material identification.
    """
    
    def __init__(
        self,
        context: IntentContext,
        file_index: FileIndex,
        threshold: int = 50,
        batch_size: int = 5,
    ):
        """Initialize LLM-based analyzer.
        
        Args:
            context: Intent context (doc type, purpose)
            file_index: File index from Sprint 2
            threshold: Minimum relevance score to include
            batch_size: Files to analyze per batch (for progress feedback)
        """
        logger.info("🤖 Initializing LLMRelevanceAnalyzer")
        logger.debug(f"  Doc type: {context.doc_type.value}")
        logger.debug(f"  Purpose: {context.purpose[:100]}...")
        logger.debug(f"  Files to analyze: {len(file_index.files)}")
        logger.debug(f"  Threshold: {threshold}")
        logger.debug(f"  Batch size: {batch_size}")
        
        self.context = context
        self.file_index = file_index
        self.threshold = threshold
        self.batch_size = batch_size
        
        # Create Anthropic client directly (uses standard API, not beta)
        logger.info("  Creating Anthropic client (standard API)...")
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5"
        self.system_prompt = self._build_system_prompt()
        
        logger.info("  ✓ Anthropic client created successfully")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for relevance analysis."""
        return f"""You are analyzing files for documentation generation.

Your task: Determine if each file is relevant for generating {self.context.doc_type.value} documentation.

Documentation Purpose: {self.context.purpose}

Guidelines:
- Score 0-100 based on how useful the file is for THIS SPECIFIC documentation purpose
- High scores (80-100): Essential files that directly support the purpose
- Medium scores (50-79): Useful supporting files
- Low scores (0-49): Not relevant for this specific purpose

IMPORTANT: Respond ONLY with valid JSON in this exact format:
{{"score": 85, "reasoning": "Explanation here...", "key_material": "What info is useful..."}}

Be specific and purpose-driven in your reasoning. Generic answers like "contains project information" are not helpful.
"""
    
    def _build_analysis_prompt(
        self,
        file_path: str,
        file_type: FileType,
        preview: str,
    ) -> str:
        """Build prompt for analyzing a specific file."""
        return f"""Analyze this file for documentation generation:

File Path: {file_path}
File Type: {file_type.value}

File Preview (first 500 chars):
{preview if preview else "[Unable to read file - binary or permission denied]"}

Question: Is this file relevant for the documentation purpose described in the system prompt?

Remember:
- Be specific about WHY relevant/irrelevant
- Consider the SPECIFIC documentation purpose
- Identify WHAT information from this file would be used
"""
    
    async def analyze_async(self, progress_callback=None) -> list[RelevanceScore]:
        """Analyze all files for relevance using LLM (async).
        
        Args:
            progress_callback: Optional callback(current, total, file_path) for progress
        
        Returns:
            List of relevance scores above threshold
        """
        logger.info(f"🔍 Starting LLM-based relevance analysis for {len(self.file_index.files)} files")
        scores = []
        total_files = len(self.file_index.files)
        
        # Process in batches for progress feedback
        for i in range(0, total_files, self.batch_size):
            batch = self.file_index.files[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_files + self.batch_size - 1) // self.batch_size
            
            logger.debug(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} files)")
            
            # Analyze batch concurrently
            batch_tasks = [
                self._analyze_file_async(file_entry)
                for file_entry in batch
            ]
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Filter by threshold
            batch_relevant = 0
            for score in batch_results:
                if score.score >= self.threshold:
                    scores.append(score)
                    batch_relevant += 1
            
            logger.debug(f"    → {batch_relevant}/{len(batch)} files above threshold")
            
            # Progress callback
            if progress_callback:
                current = min(i + self.batch_size, total_files)
                progress_callback(current, total_files, batch[-1].rel_path)
        
        # Sort by score (highest first)
        scores.sort(key=lambda s: s.score, reverse=True)
        
        logger.info(f"  ✓ Analysis complete: {len(scores)} relevant files found (threshold: {self.threshold})")
        return scores
    
    def analyze(self, progress_callback=None) -> list[RelevanceScore]:
        """Analyze all files for relevance using LLM (sync wrapper).
        
        Args:
            progress_callback: Optional callback(current, total, file_path) for progress
        
        Returns:
            List of relevance scores above threshold
        """
        return asyncio.run(self.analyze_async(progress_callback))
    
    async def _analyze_file_async(self, file_entry) -> RelevanceScore:
        """Analyze single file for relevance using LLM.
        
        Args:
            file_entry: File entry from index
            
        Returns:
            RelevanceScore with LLM-generated score and reasoning
        """
        logger.debug(f"    Analyzing: {file_entry.rel_path}")
        
        # Extract file preview
        preview = self._extract_preview(file_entry)
        logger.debug(f"      Preview length: {len(preview)} chars")
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            file_path=file_entry.rel_path,
            file_type=file_entry.file_type,
            preview=preview,
        )
        
        try:
            # Call standard Anthropic API (NOT beta)
            logger.debug(f"      Calling Claude API (standard, non-beta)...")
            logger.debug(f"      Prompt (first 200 chars): {prompt[:200]}...")
            
            # Use standard messages.create (NOT beta.messages.create)
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            logger.debug(f"      ✓ Got response from Claude")
            
            # Extract text from response
            response_text = response.content[0].text
            logger.debug(f"      Response text (first 200 chars): {response_text[:200]}...")
            
            # Parse JSON from response
            # Claude might wrap it in markdown code blocks, so extract JSON
            if "```json" in response_text:
                # Extract JSON from markdown code block
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                # Generic code block
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            response_json = json.loads(response_text)
            
            logger.debug(f"      Parsed JSON successfully")
            logger.debug(f"      Score: {response_json['score']}")
            logger.debug(f"      Reasoning (first 100 chars): {response_json['reasoning'][:100]}...")
            logger.debug(f"      Key material: {response_json.get('key_material', 'N/A')[:100]}...")
            
            return RelevanceScore(
                file_path=file_entry.rel_path,
                score=response_json['score'],
                reasoning=response_json['reasoning'],
                key_material=response_json.get('key_material', 'N/A'),
            )
        
        except AttributeError as e:
            # Specific handling for attribute errors (likely API change)
            logger.error(f"      ✗ AttributeError for {file_entry.rel_path}: {e}")
            logger.error(f"      Result object: {result if 'result' in locals() else 'not created'}")
            logger.error(f"      Result dir: {dir(result) if 'result' in locals() else 'N/A'}")
            return RelevanceScore(
                file_path=file_entry.rel_path,
                score=0,
                reasoning=f"AttributeError: {str(e)}",
                key_material="N/A",
            )
        
        except Exception as e:
            # Fallback on error (don't fail entire analysis)
            logger.warning(f"      ✗ LLM analysis failed for {file_entry.rel_path}: {e}")
            logger.warning(f"      Exception type: {type(e).__name__}")
            import traceback
            logger.debug(f"      Traceback: {traceback.format_exc()}")
            return RelevanceScore(
                file_path=file_entry.rel_path,
                score=0,
                reasoning=f"Analysis error: {str(e)}",
                key_material="N/A",
            )
    
    def _extract_preview(self, file_entry, max_chars: int = 500) -> str:
        """Extract file preview for LLM analysis.
        
        Args:
            file_entry: File entry from index
            max_chars: Maximum characters to extract
            
        Returns:
            Preview string
        """
        try:
            # Construct absolute path from project root + relative path
            abs_path = self.file_index.project_root / file_entry.rel_path
            
            # Read preview
            content = abs_path.read_text(encoding='utf-8')
            return content[:max_chars]
        
        except (UnicodeDecodeError, PermissionError, FileNotFoundError):
            # Binary file, permission denied, or file not found
            return ""
