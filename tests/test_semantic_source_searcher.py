"""Tests for SemanticSourceSearcher - content-based source file discovery."""

import pytest
from pathlib import Path

try:
    from doc_evergreen.reverse.semantic_source_searcher import SemanticSourceSearcher
except ImportError:
    SemanticSourceSearcher = None


class TestSemanticSourceSearcher:
    """Tests for semantic search-based source discovery."""
    
    def test_search_finds_api_files_by_content(self, tmp_path):
        """
        Given: Project with API-related files
        When: Search for "API Reference" section
        Then: Finds files containing API-related content
        """
        # ARRANGE
        # Create project structure with API files
        src_api = tmp_path / "src" / "api"
        src_api.mkdir(parents=True)
        (src_api / "routes.py").write_text("""
def get_users():
    '''Get all users endpoint'''
    return User.query.all()

def get_posts():
    '''Get all posts endpoint'''
    return Post.query.all()
""")
        (src_api / "handlers.py").write_text("""
class UserHandler:
    '''Handler for user API requests'''
    def handle_request(self):
        pass
""")
        
        # Create unrelated files
        src_db = tmp_path / "src" / "database"
        src_db.mkdir(parents=True)
        (src_db / "models.py").write_text("""
class User:
    '''User database model'''
    pass
""")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="API Reference",
            section_content="The API provides endpoints for user management and posts",
            key_terms=["API", "endpoints", "users", "posts"]
        )
        
        # ASSERT
        assert len(results) > 0
        file_paths = [r['file_path'] for r in results]
        
        # Should find API files
        assert any('routes.py' in str(p) for p in file_paths)
        assert any('handlers.py' in str(p) for p in file_paths)
        
        # Database models should not be in top results
        model_results = [r for r in results if 'models.py' in r['file_path']]
        if model_results:
            # If models.py appears, it should have lower score than API files
            api_results = [r for r in results if 'routes.py' in r['file_path'] or 'handlers.py' in r['file_path']]
            if api_results and model_results:
                assert api_results[0]['score'] > model_results[0]['score']
    
    def test_search_scores_by_term_frequency(self, tmp_path):
        """
        Given: Files with varying term frequencies
        When: Search for specific terms
        Then: Files with more term matches score higher
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        
        # File with many matches
        (src / "high_match.py").write_text("""
# Authentication module
def authenticate_user():
    '''Authenticate user credentials'''
    pass

def validate_auth_token():
    '''Validate authentication token'''
    pass

def check_auth_permissions():
    '''Check authentication permissions'''
    pass
""")
        
        # File with few matches
        (src / "low_match.py").write_text("""
def process_data():
    '''Process some data'''
    pass

# Brief mention of auth
def get_auth_status():
    return True
""")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="Authentication",
            section_content="User authentication and authorization",
            key_terms=["authentication", "auth", "credentials", "token"]
        )
        
        # ASSERT
        assert len(results) >= 2
        
        # Find the two files in results
        high_match = next(r for r in results if 'high_match.py' in r['file_path'])
        low_match = next(r for r in results if 'low_match.py' in r['file_path'])
        
        # File with more matches should score higher
        assert high_match['score'] > low_match['score']
    
    def test_search_considers_file_path_relevance(self, tmp_path):
        """
        Given: Files in different directories
        When: Search for section
        Then: Files in relevant directories score higher
        """
        # ARRANGE
        # File in relevant directory
        api_dir = tmp_path / "src" / "api"
        api_dir.mkdir(parents=True)
        (api_dir / "endpoints.py").write_text("""
def handle_request():
    pass
""")
        
        # File with same content but in less relevant directory
        utils_dir = tmp_path / "src" / "utils"
        utils_dir.mkdir(parents=True)
        (utils_dir / "helpers.py").write_text("""
def handle_request():
    pass
""")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="API Documentation",
            section_content="API endpoint handlers",
            key_terms=["API", "endpoint"]
        )
        
        # ASSERT
        assert len(results) >= 2
        
        # File in api/ directory should score higher than file in utils/
        api_result = next(r for r in results if 'api' in r['file_path'])
        utils_result = next(r for r in results if 'utils' in r['file_path'])
        
        assert api_result['score'] > utils_result['score']
    
    def test_search_returns_empty_for_no_matches(self, tmp_path):
        """
        Given: Project with no matching files
        When: Search for unrelated terms
        Then: Returns empty list
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "code.py").write_text("def foo(): pass")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="Quantum Computing",
            section_content="Advanced quantum algorithms",
            key_terms=["quantum", "qubit", "superposition"]
        )
        
        # ASSERT
        assert results == []
    
    def test_search_handles_case_insensitive_matching(self, tmp_path):
        """
        Given: Files with mixed case content
        When: Search with mixed case terms
        Then: Matches regardless of case
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "code.py").write_text("""
def ConfigureAPI():
    '''Configure API settings'''
    pass

def api_setup():
    '''API initialization'''
    pass
""")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="api reference",  # lowercase
            section_content="API configuration",
            key_terms=["api", "API", "Api"]  # mixed case
        )
        
        # ASSERT
        assert len(results) > 0
        assert any('code.py' in r['file_path'] for r in results)
    
    def test_search_respects_gitignore_patterns(self, tmp_path):
        """
        Given: Project with .gitignore
        When: Search for files
        Then: Ignores files matching .gitignore patterns
        """
        # ARRANGE
        (tmp_path / ".gitignore").write_text("""
__pycache__/
*.pyc
.pytest_cache/
node_modules/
""")
        
        src = tmp_path / "src"
        src.mkdir()
        (src / "code.py").write_text("def api_handler(): pass")
        
        # Create ignored directory
        pycache = src / "__pycache__"
        pycache.mkdir()
        (pycache / "cache.pyc").write_text("cached code")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="Code",
            section_content="handler code",
            key_terms=["handler", "code"]
        )
        
        # ASSERT
        # Should find code.py but not cache.pyc
        file_paths = [r['file_path'] for r in results]
        assert any('code.py' in p for p in file_paths)
        assert not any('cache.pyc' in p for p in file_paths)
        assert not any('__pycache__' in p for p in file_paths)
    
    def test_search_limits_results_to_reasonable_count(self, tmp_path):
        """
        Given: Many matching files
        When: Search returns results
        Then: Limits to reasonable number (e.g., top 20)
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        
        # Create 50 files with similar content
        for i in range(50):
            (src / f"module_{i}.py").write_text(f"""
def api_function_{i}():
    '''API function {i}'''
    pass
""")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="API",
            section_content="API functions",
            key_terms=["API", "function"]
        )
        
        # ASSERT
        # Should limit results (e.g., top 20-30, not all 50)
        assert len(results) <= 30
        assert len(results) > 0
    
    def test_search_includes_match_reason_in_results(self, tmp_path):
        """
        Given: Matching files
        When: Search returns results
        Then: Includes reason for match in result
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "api.py").write_text("""
def get_users():
    '''API endpoint for users'''
    pass
""")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        results = searcher.search(
            section_heading="API Reference",
            section_content="User API endpoints",
            key_terms=["API", "users", "endpoint"]
        )
        
        # ASSERT
        assert len(results) > 0
        result = results[0]
        
        # Should have required fields
        assert 'file_path' in result
        assert 'score' in result
        assert 'match_reason' in result
        
        # Match reason should mention matched terms
        assert result['match_reason'] is not None
        assert len(result['match_reason']) > 0
    
    def test_file_indexing_caches_content(self, tmp_path):
        """
        Given: Large project
        When: Multiple searches performed
        Then: Uses cached file index (doesn't re-read files)
        """
        # ARRANGE
        src = tmp_path / "src"
        src.mkdir()
        (src / "api.py").write_text("def api_call(): pass")
        
        searcher = SemanticSourceSearcher(project_root=tmp_path)
        
        # ACT
        # Perform multiple searches
        results1 = searcher.search("API", "API docs", ["API"])
        results2 = searcher.search("Functions", "Function docs", ["function"])
        
        # ASSERT
        # Both searches should work (using same file index)
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        
        # Index should exist (implementation detail, but validates caching concept)
        assert hasattr(searcher, 'file_index')
        assert searcher.file_index is not None
