"""SemanticSourceSearcher - content-based source file discovery."""

import re
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter


class SemanticSourceSearcher:
    """Find source files relevant to documentation sections using content-based search."""
    
    def __init__(self, project_root: Path, exclude_path: str | None = None):
        """Initialize searcher with project root.
        
        Args:
            project_root: Root directory of project to search
            exclude_path: Relative path to exclude from indexing (e.g., document being reversed)
        """
        self.project_root = Path(project_root)
        self.exclude_path = exclude_path
        self.file_index = self._build_file_index()
    
    def search(
        self,
        section_heading: str,
        section_content: str,
        key_terms: List[str],
        max_results: int = 20
    ) -> List[Dict]:
        """Search for files relevant to a section.
        
        Args:
            section_heading: Section heading text
            section_content: Section content text
            key_terms: List of key terms to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of result dictionaries with:
            - file_path: Relative path to file
            - score: Relevance score (higher is better)
            - match_reason: Why this file was matched
        """
        if not key_terms:
            return []
        
        # Normalize terms for matching
        normalized_terms = [term.lower() for term in key_terms]
        
        # Score all files
        scored_files = []
        for file_path, file_data in self.file_index.items():
            score = self._score_file(
                file_path=file_path,
                file_content=file_data['content'],
                key_terms=normalized_terms,
                section_heading=section_heading
            )
            
            if score > 0:
                match_reason = self._generate_match_reason(
                    file_content=file_data['content'],
                    key_terms=key_terms,
                    file_path=file_path
                )
                
                scored_files.append({
                    'file_path': file_path,
                    'score': score,
                    'match_reason': match_reason
                })
        
        # Sort by score descending and limit results
        scored_files.sort(key=lambda x: x['score'], reverse=True)
        return scored_files[:max_results]
    
    def _build_file_index(self) -> Dict[str, Dict]:
        """Build searchable index of all source files in project.
        
        Returns:
            Dictionary mapping file paths to file data:
            {
                'relative/path/to/file.py': {
                    'content': 'file contents...',
                    'keywords': ['keyword1', 'keyword2', ...]
                }
            }
        """
        file_index = {}
        
        # Load gitignore patterns
        gitignore_patterns = self._load_gitignore_patterns()
        
        # Walk project directory
        for file_path in self.project_root.rglob('*'):
            # Skip directories
            if not file_path.is_file():
                continue
            
            # Skip ignored files
            if self._is_ignored(file_path, gitignore_patterns):
                continue
            
            # Only index source files (common extensions)
            if not self._is_source_file(file_path):
                continue
            
            try:
                # Read file content
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Get relative path
                relative_path = str(file_path.relative_to(self.project_root))
                
                # CRITICAL: Skip the document being reverse-templated (cyclical reference)
                if self.exclude_path and relative_path == self.exclude_path:
                    continue
                
                # Extract keywords
                keywords = self._extract_keywords(content)
                
                file_index[relative_path] = {
                    'content': content.lower(),  # Lowercase for case-insensitive search
                    'keywords': keywords
                }
            except (OSError, UnicodeDecodeError):
                # Skip files we can't read
                continue
        
        return file_index
    
    def _load_gitignore_patterns(self) -> List[str]:
        """Load .gitignore patterns.
        
        Returns:
            List of gitignore patterns
        """
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            return []
        
        patterns = []
        try:
            with open(gitignore_path) as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except OSError:
            return []
        
        return patterns
    
    def _is_ignored(self, file_path: Path, gitignore_patterns: List[str]) -> bool:
        """Check if file matches gitignore patterns.
        
        Args:
            file_path: Path to check
            gitignore_patterns: List of gitignore patterns
            
        Returns:
            True if file should be ignored
        """
        relative_path = str(file_path.relative_to(self.project_root))
        
        # Common ignore patterns (even without .gitignore)
        common_ignores = [
            '__pycache__',
            '.pytest_cache',
            '.git',
            'node_modules',
            '.venv',
            'venv',
            '*.pyc',
            '*.pyo',
            '*.so',
            '.DS_Store'
        ]
        
        all_patterns = gitignore_patterns + common_ignores
        
        for pattern in all_patterns:
            # Simple pattern matching (directory or extension)
            if pattern.endswith('/'):
                # Directory pattern
                if pattern.rstrip('/') in relative_path.split('/'):
                    return True
            elif pattern.startswith('*.'):
                # Extension pattern
                if file_path.name.endswith(pattern[1:]):
                    return True
            elif pattern in relative_path:
                # Simple substring match
                return True
        
        return False
    
    def _is_source_file(self, file_path: Path) -> bool:
        """Check if file is a source file we should index.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be indexed
        """
        # Source file extensions to index
        source_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.go', '.rs', '.c', '.cpp', '.h', '.hpp',
            '.rb', '.php', '.swift', '.kt',
            '.yaml', '.yml', '.json', '.toml',
            '.md', '.rst', '.txt',
            '.sh', '.bash',
            '.sql'
        }
        
        return file_path.suffix in source_extensions
    
    def _extract_keywords(self, content: str) -> Set[str]:
        """Extract keywords from file content.
        
        Args:
            content: File content
            
        Returns:
            Set of keywords (lowercase)
        """
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content)
        
        # Filter out common words and very short words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'may', 'might', 'can',
            'if', 'then', 'else', 'when', 'where', 'why', 'how',
            'this', 'that', 'these', 'those', 'it', 'its'
        }
        
        keywords = {
            word.lower() for word in words
            if len(word) > 2 and word.lower() not in stop_words
        }
        
        return keywords
    
    def _score_file(
        self,
        file_path: str,
        file_content: str,
        key_terms: List[str],
        section_heading: str
    ) -> float:
        """Score file relevance based on key terms.
        
        Args:
            file_path: Relative file path
            file_content: File content (lowercase)
            key_terms: Key terms to search for (lowercase)
            section_heading: Section heading text
            
        Returns:
            Relevance score (higher is better)
        """
        score = 0.0
        path_lower = file_path.lower()
        
        # Count term occurrences in content
        term_counts = Counter()
        for term in key_terms:
            # Count occurrences (case-insensitive)
            count = file_content.count(term.lower())
            if count > 0:
                term_counts[term] = count
        
        # Base score from content matches
        if term_counts:
            # Use log to reduce impact of very high frequencies
            import math
            for term, count in term_counts.items():
                score += math.log(1 + count)
        
        # Also score based on path relevance (even without content match)
        path_score = 0.0
        
        # Check if path contains section-relevant keywords
        heading_words = section_heading.lower().split()
        for word in heading_words:
            if len(word) > 3 and word in path_lower:
                path_score += 2.0  # Base path relevance score
        
        # Check if path contains key terms
        for term in key_terms:
            if term.lower() in path_lower:
                path_score += 1.5  # Term in path score
        
        # Combine scores
        if score > 0 and path_score > 0:
            # Has both content and path matches - boost the content score
            score *= (1 + path_score * 0.3)
        elif path_score > 0:
            # Only path matches - use path score
            score = path_score
        
        return score
    
    def _generate_match_reason(
        self,
        file_content: str,
        key_terms: List[str],
        file_path: str
    ) -> str:
        """Generate human-readable match reason.
        
        Args:
            file_content: File content (lowercase)
            key_terms: Key terms that matched
            file_path: File path
            
        Returns:
            Match reason string
        """
        matched_terms = []
        for term in key_terms:
            if term.lower() in file_content:
                matched_terms.append(term)
        
        if not matched_terms:
            return "Path relevance"
        
        # Limit to first 3 terms
        terms_str = ", ".join(matched_terms[:3])
        if len(matched_terms) > 3:
            terms_str += f" (+{len(matched_terms) - 3} more)"
        
        return f"Contains: {terms_str}"
