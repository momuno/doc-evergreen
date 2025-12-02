"""Tests for NaiveSourceDiscoverer - pattern-based source discovery."""

import pytest
from pathlib import Path

try:
    from doc_evergreen.reverse.naive_source_discovery import NaiveSourceDiscoverer
except ImportError:
    NaiveSourceDiscoverer = None


class TestNaiveSourceDiscoverer:
    """Tests for pattern-based source discovery."""
    
    def test_discover_installation_sources(self, tmp_path):
        """
        Given: Section heading "Installation" 
        When: Discover sources using pattern matching
        Then: Returns package files (package.json, setup.py, pyproject.toml, etc.)
        """
        # ARRANGE
        # Create mock project structure
        (tmp_path / "package.json").write_text('{"name": "test"}')
        (tmp_path / "setup.py").write_text("# setup")
        
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="Installation",
            section_content="To install, run pip install..."
        )
        
        # ASSERT
        assert len(sources) > 0
        # Should find at least one package file
        source_names = [Path(s).name for s in sources]
        assert any(name in source_names for name in ['package.json', 'setup.py', 'pyproject.toml'])
    
    def test_discover_api_reference_sources(self, tmp_path):
        """
        Given: Section heading "API Reference"
        When: Discover sources using pattern matching
        Then: Returns source code files (*.py, *.js, etc.)
        """
        # ARRANGE
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("# main")
        (src_dir / "api.py").write_text("# api")
        
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="API Reference",
            section_content="The API provides the following methods..."
        )
        
        # ASSERT
        assert len(sources) > 0
        # Should find source files
        assert any('main.py' in str(s) for s in sources)
        assert any('api.py' in str(s) for s in sources)
    
    def test_discover_contributing_sources(self, tmp_path):
        """
        Given: Section heading "Contributing"
        When: Discover sources using pattern matching
        Then: Returns CONTRIBUTING.md and .github files
        """
        # ARRANGE
        (tmp_path / "CONTRIBUTING.md").write_text("# Contributing")
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text("# PR Template")
        
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="Contributing",
            section_content="We welcome contributions..."
        )
        
        # ASSERT
        assert len(sources) > 0
        source_names = [Path(s).name for s in sources]
        assert "CONTRIBUTING.md" in source_names
    
    def test_discover_configuration_sources(self, tmp_path):
        """
        Given: Section heading "Configuration"
        When: Discover sources using pattern matching
        Then: Returns config files (*.yaml, *.config.js, .env.example)
        """
        # ARRANGE
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "settings.yaml").write_text("# settings")
        (tmp_path / ".env.example").write_text("API_KEY=xxx")
        
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="Configuration",
            section_content="Configure the application using..."
        )
        
        # ASSERT
        assert len(sources) > 0
        # Should find config files
        assert any('settings.yaml' in str(s) for s in sources)
    
    def test_discover_no_matches_returns_empty(self, tmp_path):
        """
        Given: Section heading that doesn't match any patterns
        When: Discover sources
        Then: Returns empty list (no error)
        """
        # ARRANGE
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="Random Section",
            section_content="Some random content"
        )
        
        # ASSERT
        assert sources == []
    
    def test_discover_handles_multiple_matches(self, tmp_path):
        """
        Given: Multiple files match the pattern
        When: Discover sources
        Then: Returns all matching files
        """
        # ARRANGE
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module1.py").write_text("# module1")
        (src_dir / "module2.py").write_text("# module2")
        (src_dir / "module3.py").write_text("# module3")
        
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="API Reference",
            section_content="API documentation"
        )
        
        # ASSERT
        assert len(sources) >= 3
        # All modules should be found
        assert any('module1.py' in str(s) for s in sources)
        assert any('module2.py' in str(s) for s in sources)
        assert any('module3.py' in str(s) for s in sources)
    
    def test_discover_case_insensitive_heading_match(self, tmp_path):
        """
        Given: Section heading with different case (e.g., "INSTALLATION")
        When: Discover sources
        Then: Matches pattern regardless of case
        """
        # ARRANGE
        (tmp_path / "setup.py").write_text("# setup")
        
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="INSTALLATION",  # uppercase
            section_content="Install instructions"
        )
        
        # ASSERT
        assert len(sources) > 0
        assert any('setup.py' in str(s) for s in sources)
    
    def test_discover_returns_relative_paths(self, tmp_path):
        """
        Given: Files in project
        When: Discover sources
        Then: Returns paths relative to project root
        """
        # ARRANGE
        src_dir = tmp_path / "src" / "nested"
        src_dir.mkdir(parents=True)
        (src_dir / "api.py").write_text("# api")
        
        discoverer = NaiveSourceDiscoverer(project_root=tmp_path)
        
        # ACT
        sources = discoverer.discover(
            section_heading="API",
            section_content="API docs"
        )
        
        # ASSERT
        assert len(sources) > 0
        # Paths should be relative to project root
        for source in sources:
            # Should not be absolute path starting with tmp_path
            assert not str(source).startswith(str(tmp_path))
            # Should be relative (starts with src/)
            assert str(source).startswith('src/')
