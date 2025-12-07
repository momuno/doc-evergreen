"""NaiveSourceDiscoverer - pattern-based source discovery for template generation."""

from pathlib import Path
from typing import List


# Pattern mapping: section types → glob patterns for typical source files
SECTION_PATTERNS = {
    'installation': [
        'package.json',
        'setup.py',
        'pyproject.toml',
        'requirements.txt',
        'Pipfile',
        'Gemfile',
        'composer.json',
        'pom.xml',
        'build.gradle',
    ],
    'api': [
        'src/**/*.py',
        'lib/**/*.js',
        'lib/**/*.ts',
        'api/**/*',
        'src/**/*.java',
        'src/**/*.go',
    ],
    'configuration': [
        'config/**/*.yaml',
        'config/**/*.yml',
        'config/**/*.json',
        '*.config.js',
        '*.config.ts',
        '.env.example',
        'conf/**/*',
    ],
    'architecture': [
        'docs/architecture.md',
        'docs/ARCHITECTURE.md',
        'src/core/**/*',
        'architecture.md',
        'ARCHITECTURE.md',
    ],
    'contributing': [
        'CONTRIBUTING.md',
        '.github/**/*',
        'docs/contributing.md',
        'docs/CONTRIBUTING.md',
        '.gitlab/**/*',
    ],
    'testing': [
        'tests/**/*.py',
        'test/**/*.js',
        'spec/**/*',
        '__tests__/**/*',
        '*.test.js',
        '*.spec.js',
    ],
    'deployment': [
        'Dockerfile',
        'docker-compose.yml',
        '.github/workflows/**/*',
        '.gitlab-ci.yml',
        'Makefile',
        'deploy/**/*',
    ],
}


class NaiveSourceDiscoverer:
    """Discover source files using pattern matching against section headings."""
    
    def __init__(self, project_root: Path, exclude_path: str | None = None):
        """Initialize discoverer with project root.
        
        Args:
            project_root: Root directory of the project to search
            exclude_path: Relative path to exclude from discovery (e.g., document being reversed)
        """
        self.project_root = Path(project_root)
        self.exclude_path = exclude_path
    
    def discover(self, section_heading: str, section_content: str) -> List[str]:
        """Discover source files for a given section using pattern matching.
        
        Args:
            section_heading: Section heading text (e.g., "Installation", "API Reference")
            section_content: Section content text (not used in naive implementation)
            
        Returns:
            List of source file paths relative to project root
        """
        # Normalize heading for matching (lowercase, remove special chars)
        normalized_heading = self._normalize_heading(section_heading)
        
        # Find matching patterns
        patterns = self._match_patterns(normalized_heading)
        
        if not patterns:
            return []
        
        # Find files matching patterns
        sources = []
        for pattern in patterns:
            matched_files = self._glob_pattern(pattern)
            sources.extend(matched_files)
        
        # Convert to relative paths and filter out excluded document
        relative_paths = []
        for f in sources:
            rel_path = self._relative_path(f)
            # Skip the document being reverse-templated (cyclical reference)
            if self.exclude_path and rel_path == self.exclude_path:
                continue
            relative_paths.append(rel_path)
        
        return relative_paths
    
    def _normalize_heading(self, heading: str) -> str:
        """Normalize heading for pattern matching.
        
        Args:
            heading: Raw heading text
            
        Returns:
            Normalized heading (lowercase, alphanumeric only)
        """
        # Convert to lowercase
        normalized = heading.lower()
        
        # Remove special characters, keep only alphanumeric and spaces
        normalized = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in normalized)
        
        # Collapse multiple spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _match_patterns(self, normalized_heading: str) -> List[str]:
        """Match normalized heading against known section patterns.
        
        Args:
            normalized_heading: Normalized heading text
            
        Returns:
            List of glob patterns to search for
        """
        matched_patterns = []
        
        # Try to match against each known section type
        for section_type, patterns in SECTION_PATTERNS.items():
            if section_type in normalized_heading:
                matched_patterns.extend(patterns)
        
        return matched_patterns
    
    def _glob_pattern(self, pattern: str) -> List[Path]:
        """Find files matching glob pattern in project root.
        
        Args:
            pattern: Glob pattern (e.g., '*.py', 'src/**/*.js')
            
        Returns:
            List of matching file paths
        """
        try:
            # Use rglob for recursive patterns, glob for simple patterns
            if '**' in pattern:
                # Extract the pattern after **
                parts = pattern.split('**/')
                if len(parts) == 2:
                    sub_pattern = parts[1]
                    matched = list(self.project_root.rglob(sub_pattern))
                else:
                    matched = list(self.project_root.glob(pattern))
            else:
                matched = list(self.project_root.glob(pattern))
            
            # Filter to only files (not directories)
            return [f for f in matched if f.is_file()]
        except (OSError, ValueError):
            # Handle invalid patterns gracefully
            return []
    
    def _relative_path(self, file_path: Path) -> str:
        """Convert absolute path to relative path from project root.
        
        Args:
            file_path: Absolute file path
            
        Returns:
            Relative path string from project root
        """
        try:
            return str(file_path.relative_to(self.project_root))
        except ValueError:
            # File is outside project root, return as-is
            return str(file_path)
