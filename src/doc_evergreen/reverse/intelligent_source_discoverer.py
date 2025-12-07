"""IntelligentSourceDiscoverer - integrated 3-stage discovery pipeline."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List
from collections import Counter

from .naive_source_discovery import NaiveSourceDiscoverer
from .semantic_source_searcher import SemanticSourceSearcher
from .llm_relevance_scorer import LLMRelevanceScorer

# Set up logging
logger = logging.getLogger(__name__)


class IntelligentSourceDiscoverer:
    """
    Multi-stage source discovery pipeline for high-accuracy source detection.
    
    Stage 1: Pattern matching (broad net, high recall)
    Stage 2: Semantic search (narrow to relevant, content-based)
    Stage 3: LLM scoring (precise ranking, semantic understanding)
    """
    
    def __init__(self, project_root: Path, llm_client: Any, exclude_path: str | None = None):
        """Initialize discoverer with all three discovery methods.
        
        Args:
            project_root: Root directory of project
            llm_client: LLM client for relevance scoring
            exclude_path: Relative path to exclude from discovery (e.g., document being reversed)
        """
        self.project_root = Path(project_root)
        self.exclude_path = exclude_path
        
        # Initialize all three discovery stages (all exclude the document being reversed)
        self.pattern_discoverer = NaiveSourceDiscoverer(project_root=project_root, exclude_path=exclude_path)
        self.semantic_searcher = SemanticSourceSearcher(project_root=project_root, exclude_path=exclude_path)
        self.llm_scorer = LLMRelevanceScorer(llm_client=llm_client)
    
    def discover_sources(
        self,
        section_heading: str,
        section_content: str,
        max_sources: int = 5
    ) -> List[Dict]:
        """
        Discover relevant sources through 3-stage pipeline.
        
        Args:
            section_heading: Section heading text
            section_content: Section content text
            max_sources: Maximum number of sources to return
            
        Returns:
            List of source dictionaries with:
            - path: Relative file path
            - relevance_score: LLM score (0-10)
            - match_reason: Why this source is relevant
            - discovery_method: Which methods found this file
            - confidence: LLM confidence level
        """
        all_candidates = []
        
        # Stage 1: Pattern matching (broad net)
        logger.info(f"  [Stage 1/3] Pattern matching for '{section_heading}'...")
        logger.info(f"    ℹ️  Scoring: Pattern matches get fixed score of 6 (catches obvious files)")
        pattern_matches = self.pattern_discoverer.discover(
            section_heading=section_heading,
            section_content=section_content
        )
        logger.info(f"    → Found {len(pattern_matches)} pattern matches")
        all_candidates.extend([
            {'path': p, 'source': 'pattern', 'score': 6}
            for p in pattern_matches
        ])
        
        # Stage 2: Semantic search (narrow to relevant)
        logger.info(f"  [Stage 2/3] Semantic search (content-based matching)...")
        logger.info(f"    ℹ️  Scoring: Variable score based on term frequency + path relevance")
        logger.info(f"              (Higher score = more term matches in content + matching path)")
        key_terms = self._extract_key_terms(section_content)
        # Show all key terms (not truncated)
        if key_terms:
            logger.info(f"    → Extracted {len(key_terms)} key terms:")
            logger.info(f"       {', '.join(key_terms)}")
        else:
            logger.info(f"    → No key terms extracted")
        if key_terms:  # Only search if we have terms
            logger.info(f"    → Searching {len(self.semantic_searcher.file_index)} indexed files...")
            semantic_matches = self.semantic_searcher.search(
                section_heading=section_heading,
                section_content=section_content,
                key_terms=key_terms,
                max_results=20  # Top 20 from semantic search
            )
            logger.info(f"    → Found {len(semantic_matches)} semantic matches")
            all_candidates.extend([
                {
                    'path': m['file_path'],
                    'source': 'semantic',
                    'score': m['score']
                }
                for m in semantic_matches
            ])
        
        # Deduplicate candidates (same file may be found by multiple methods)
        logger.info(f"  Combining results from all stages...")
        logger.info(f"    → Pattern matches: {len([c for c in all_candidates if c['source'] == 'pattern'])}")
        logger.info(f"    → Semantic matches: {len([c for c in all_candidates if c['source'] == 'semantic'])}")
        logger.info(f"    → Total candidates: {len(all_candidates)}")
        
        unique_candidates = self._deduplicate_candidates(all_candidates)
        logger.info(f"    → After deduplication: {len(unique_candidates)} unique files")
        
        # If no candidates, return empty list
        if not unique_candidates:
            logger.info(f"  ⚠️  No candidates found for '{section_heading}'")
            return []
        
        # Stage 3: LLM scoring (precise ranking)
        # Limit to top 10 candidates to control LLM costs
        top_candidates = sorted(
            unique_candidates,
            key=lambda x: x['score'],
            reverse=True
        )[:10]
        
        logger.info(f"    → Selecting top {len(top_candidates)} by initial score (pattern=6, semantic=varies)")
        logger.info(f"")
        logger.info(f"    Top {len(top_candidates)} candidates by initial score:")
        for idx, candidate in enumerate(top_candidates):
            logger.info(f"       {idx+1}. {candidate['path']} (score: {candidate['score']:.2f})")
        logger.info(f"")
        logger.info(f"  [Stage 3/3] LLM scoring ({len(top_candidates)} API calls - this is the slow part)...")
        logger.info(f"    ℹ️  Scoring: LLM assigns 0-10 relevance score (5+ threshold for inclusion)")
        
        # Score each candidate with LLM
        scored_candidates = []
        for idx, candidate in enumerate(top_candidates):
            logger.info(f"    → Scoring {idx+1}/{len(top_candidates)}: {candidate['path']} (via LLM API call)...")
            # Read file content
            file_content = self._read_file(candidate['path'])
            if file_content is None:
                continue
            
            # Score with LLM
            llm_result = self.llm_scorer.score_relevance(
                section_heading=section_heading,
                section_content=section_content,
                source_file_path=candidate['path'],
                source_file_content=file_content
            )
            
            # Log the LLM result
            logger.info(f"       ✓ LLM score: {llm_result['score']}/10 (confidence: {llm_result['confidence']})")
            logger.info(f"         Reason: {llm_result['reasoning'][:80]}{'...' if len(llm_result['reasoning']) > 80 else ''}")
            
            scored_candidates.append({
                'path': candidate['path'],
                'relevance_score': llm_result['score'],
                'match_reason': llm_result['reasoning'],
                'confidence': llm_result['confidence'],
                'discovery_method': f"{candidate['source']} + llm_scored"
            })
        
        # Filter by minimum score (>=5) and sort by score
        relevant = [c for c in scored_candidates if c['relevance_score'] >= 5]
        ranked = sorted(relevant, key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top N results
        return ranked[:max_sources]
    
    def _extract_key_terms(self, section_content: str) -> List[str]:
        """
        Extract key terms from section content using simple heuristics.
        
        Uses frequency-based extraction (no LLM/embeddings for cost efficiency).
        
        Args:
            section_content: Section content text
            
        Returns:
            List of key terms (top 10 most frequent, excluding stop words)
        """
        # Tokenize into words
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', section_content)
        
        # Stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'may', 'might', 'can',
            'if', 'then', 'else', 'when', 'where', 'why', 'how',
            'this', 'that', 'these', 'those', 'it', 'its', 'their', 'them',
            'you', 'your', 'we', 'our', 'they'
        }
        
        # Filter and count
        filtered = [
            w.lower() for w in words
            if len(w) > 2 and w.lower() not in stop_words
        ]
        
        # Count frequency
        term_freq = Counter(filtered)
        
        # Return top 10 most frequent terms
        return [term for term, count in term_freq.most_common(10)]
    
    def _deduplicate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """
        Deduplicate candidates found by multiple discovery methods.
        
        For duplicates, keeps the one with highest score and combines sources.
        
        Args:
            candidates: List of candidate dicts with 'path', 'source', 'score'
            
        Returns:
            Deduplicated list of candidates
        """
        # Group by path
        by_path = {}
        for candidate in candidates:
            path = candidate['path']
            
            if path not in by_path:
                by_path[path] = candidate
            else:
                # Keep higher score
                if candidate['score'] > by_path[path]['score']:
                    by_path[path]['score'] = candidate['score']
                
                # Combine sources
                existing_source = by_path[path]['source']
                new_source = candidate['source']
                if new_source not in existing_source:
                    by_path[path]['source'] = f"{existing_source}+{new_source}"
        
        return list(by_path.values())
    
    def _read_file(self, relative_path: str) -> str:
        """
        Read file content from project.
        
        Args:
            relative_path: Path relative to project root
            
        Returns:
            File content, or None if file can't be read
        """
        try:
            file_path = self.project_root / relative_path
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except (OSError, UnicodeDecodeError):
            return None
