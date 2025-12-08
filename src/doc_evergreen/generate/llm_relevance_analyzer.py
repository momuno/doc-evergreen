"""LLM-based file relevance analysis for generate-doc (Sprint 3)."""

import asyncio
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from doc_evergreen.generate.intent_context import IntentContext
from doc_evergreen.generate.repo_indexer import FileIndex, FileType
from doc_evergreen.generate.relevance_analyzer import RelevanceScore


class FileRelevanceResponse(BaseModel):
    """LLM response for file relevance analysis."""
    
    score: int = Field(
        description="Relevance score 0-100. 0=completely irrelevant, 100=essential",
        ge=0,
        le=100
    )
    reasoning: str = Field(
        description="2-3 sentences explaining WHY this file is or isn't relevant for the specific documentation purpose"
    )
    key_material: str = Field(
        description="If relevant (score >= 50): WHAT specific information in this file is useful. If not relevant: 'N/A'"
    )


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
        self.context = context
        self.file_index = file_index
        self.threshold = threshold
        self.batch_size = batch_size
        
        # Create pydantic-ai agent for relevance analysis
        self.agent = Agent(
            "anthropic:claude-3-5-sonnet-20241022",
            result_type=FileRelevanceResponse,
            system_prompt=self._build_system_prompt(),
        )
    
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

Provide:
1. Relevance score (0-100)
2. Reasoning: WHY is this file relevant/irrelevant for THIS PURPOSE?
3. Key material: WHAT specific information from this file would be useful?

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
        scores = []
        total_files = len(self.file_index.files)
        
        # Process in batches for progress feedback
        for i in range(0, total_files, self.batch_size):
            batch = self.file_index.files[i:i + self.batch_size]
            
            # Analyze batch concurrently
            batch_tasks = [
                self._analyze_file_async(file_entry)
                for file_entry in batch
            ]
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Filter by threshold
            for score in batch_results:
                if score.score >= self.threshold:
                    scores.append(score)
            
            # Progress callback
            if progress_callback:
                current = min(i + self.batch_size, total_files)
                progress_callback(current, total_files, batch[-1].rel_path)
        
        # Sort by score (highest first)
        scores.sort(key=lambda s: s.score, reverse=True)
        
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
        # Extract file preview
        preview = self._extract_preview(file_entry)
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            file_path=file_entry.rel_path,
            file_type=file_entry.file_type,
            preview=preview,
        )
        
        try:
            # Call LLM
            result = await self.agent.run(prompt)
            response = result.data
            
            return RelevanceScore(
                file_path=file_entry.rel_path,
                score=response.score,
                reasoning=response.reasoning,
                key_material=response.key_material,
            )
        
        except Exception as e:
            # Fallback on error (don't fail entire analysis)
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
            # Get absolute path
            abs_path = Path(file_entry.abs_path)
            
            # Read preview
            content = abs_path.read_text(encoding='utf-8')
            return content[:max_chars]
        
        except (UnicodeDecodeError, PermissionError, FileNotFoundError):
            # Binary file, permission denied, or file not found
            return ""
