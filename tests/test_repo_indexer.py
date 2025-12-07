"""Tests for repository file indexer."""

import json
from pathlib import Path

import pytest

from doc_evergreen.generate.repo_indexer import (
    RepoIndexer,
    FileEntry,
    FileIndex,
    FileType,
)


class TestFileType:
    """Test file type classification."""

    def test_source_code_types_exist(self):
        """Should have source code file type."""
        assert FileType.SOURCE_CODE.value == "source_code"

    def test_documentation_type_exists(self):
        """Should have documentation file type."""
        assert FileType.DOCUMENTATION.value == "documentation"

    def test_config_type_exists(self):
        """Should have config file type."""
        assert FileType.CONFIG.value == "config"

    def test_test_type_exists(self):
        """Should have test file type."""
        assert FileType.TEST.value == "test"


class TestFileEntry:
    """Test FileEntry dataclass."""

    def test_create_file_entry(self):
        """Should create file entry with all fields."""
        entry = FileEntry(
            path=Path("src/main.py"),
            rel_path="src/main.py",
            size=4521,
            extension=".py",
            file_type=FileType.SOURCE_CODE,
        )
        
        assert entry.path == Path("src/main.py")
        assert entry.rel_path == "src/main.py"
        assert entry.size == 4521
        assert entry.extension == ".py"
        assert entry.file_type == FileType.SOURCE_CODE

    def test_to_dict_method(self):
        """Should convert to dict."""
        entry = FileEntry(
            path=Path("README.md"),
            rel_path="README.md",
            size=2143,
            extension=".md",
            file_type=FileType.DOCUMENTATION,
        )
        
        data = entry.to_dict()
        
        assert data["rel_path"] == "README.md"
        assert data["size"] == 2143
        assert data["extension"] == ".md"
        assert data["type"] == "documentation"


class TestRepoIndexer:
    """Test repository file indexer."""

    def test_creates_indexer_with_project_root(self, tmp_path):
        """Should create indexer with project root."""
        indexer = RepoIndexer(project_root=tmp_path)
        assert indexer.project_root == tmp_path

    def test_discovers_files_in_directory(self, tmp_path):
        """Should discover all files in directory."""
        # Create test files
        (tmp_path / "file1.py").write_text("# Python file")
        (tmp_path / "file2.md").write_text("# Markdown")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        assert len(index.files) == 2
        assert any(f.rel_path == "file1.py" for f in index.files)
        assert any(f.rel_path == "file2.md" for f in index.files)

    def test_discovers_nested_files(self, tmp_path):
        """Should discover files in subdirectories."""
        # Create nested structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# Main")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "guide.md").write_text("# Guide")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        assert any(f.rel_path == "src/main.py" for f in index.files)
        assert any(f.rel_path == "docs/guide.md" for f in index.files)

    def test_excludes_git_directory(self, tmp_path):
        """Should exclude .git directory."""
        # Create .git directory
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")
        (tmp_path / "src.py").write_text("# Source")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        assert not any(".git" in f.rel_path for f in index.files)
        assert any(f.rel_path == "src.py" for f in index.files)

    def test_excludes_common_directories(self, tmp_path):
        """Should exclude node_modules, __pycache__, etc."""
        # Create excluded directories
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// Lib")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "cache.pyc").write_text("cache")
        (tmp_path / "good.py").write_text("# Good")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        assert not any("node_modules" in f.rel_path for f in index.files)
        assert not any("__pycache__" in f.rel_path for f in index.files)
        assert any(f.rel_path == "good.py" for f in index.files)

    def test_respects_gitignore(self, tmp_path):
        """Should respect .gitignore patterns."""
        # Create .gitignore
        (tmp_path / ".gitignore").write_text("*.log\nbuild/\n")
        
        # Create files
        (tmp_path / "app.log").write_text("logs")
        (tmp_path / "build").mkdir()
        (tmp_path / "build" / "output.txt").write_text("build output")
        (tmp_path / "src.py").write_text("# Source")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        assert not any(f.rel_path == "app.log" for f in index.files)
        assert not any("build" in f.rel_path for f in index.files)
        assert any(f.rel_path == "src.py" for f in index.files)

    def test_respects_docignore(self, tmp_path):
        """Should respect .docignore patterns."""
        # Create .docignore
        (tmp_path / ".docignore").write_text("generated/\n*.gen.py\n")
        
        # Create files
        (tmp_path / "generated").mkdir()
        (tmp_path / "generated" / "code.py").write_text("# Generated")
        (tmp_path / "output.gen.py").write_text("# Generated")
        (tmp_path / "src.py").write_text("# Source")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        assert not any("generated" in f.rel_path for f in index.files)
        assert not any(f.rel_path == "output.gen.py" for f in index.files)
        assert any(f.rel_path == "src.py" for f in index.files)

    def test_classifies_file_types(self, tmp_path):
        """Should classify files by type."""
        # Create files of different types
        (tmp_path / "main.py").write_text("# Python")
        (tmp_path / "README.md").write_text("# Docs")
        (tmp_path / "config.yaml").write_text("# Config")
        (tmp_path / "test_app.py").write_text("# Test")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        # Check classifications
        py_file = next(f for f in index.files if f.rel_path == "main.py")
        assert py_file.file_type == FileType.SOURCE_CODE
        
        md_file = next(f for f in index.files if f.rel_path == "README.md")
        assert md_file.file_type == FileType.DOCUMENTATION
        
        yaml_file = next(f for f in index.files if f.rel_path == "config.yaml")
        assert yaml_file.file_type == FileType.CONFIG
        
        test_file = next(f for f in index.files if f.rel_path == "test_app.py")
        assert test_file.file_type == FileType.TEST

    def test_extracts_file_metadata(self, tmp_path):
        """Should extract size and extension."""
        content = "x" * 1000
        (tmp_path / "test.py").write_text(content)
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        file_entry = index.files[0]
        assert file_entry.size > 0
        assert file_entry.extension == ".py"

    def test_stores_relative_paths(self, tmp_path):
        """Should store paths relative to project root."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("# App")
        
        indexer = RepoIndexer(project_root=tmp_path)
        index = indexer.build_index()
        
        # Should be relative path, not absolute
        assert index.files[0].rel_path == "src/app.py"
        assert not str(index.files[0].rel_path).startswith("/")


class TestFileIndex:
    """Test FileIndex dataclass."""

    def test_creates_file_index(self, tmp_path):
        """Should create file index."""
        files = [
            FileEntry(Path("a.py"), "a.py", 100, ".py", FileType.SOURCE_CODE),
            FileEntry(Path("b.md"), "b.md", 200, ".md", FileType.DOCUMENTATION),
        ]
        
        index = FileIndex(
            project_root=tmp_path,
            files=files,
        )
        
        assert index.project_root == tmp_path
        assert len(index.files) == 2
        assert index.total_files == 2

    def test_calculates_file_counts_by_type(self, tmp_path):
        """Should count files by type."""
        files = [
            FileEntry(Path("a.py"), "a.py", 100, ".py", FileType.SOURCE_CODE),
            FileEntry(Path("b.py"), "b.py", 150, ".py", FileType.SOURCE_CODE),
            FileEntry(Path("c.md"), "c.md", 200, ".md", FileType.DOCUMENTATION),
        ]
        
        index = FileIndex(project_root=tmp_path, files=files)
        counts = index.file_counts_by_type()
        
        assert counts[FileType.SOURCE_CODE] == 2
        assert counts[FileType.DOCUMENTATION] == 1

    def test_to_dict_method(self, tmp_path):
        """Should convert index to dict."""
        files = [
            FileEntry(Path("a.py"), "a.py", 100, ".py", FileType.SOURCE_CODE),
        ]
        
        index = FileIndex(project_root=tmp_path, files=files)
        data = index.to_dict()
        
        assert "project_root" in data
        assert "total_files" in data
        assert data["total_files"] == 1
        assert "files" in data
        assert len(data["files"]) == 1
        assert "file_counts" in data

    def test_saves_to_json_file(self, tmp_path):
        """Should save index to JSON file."""
        files = [
            FileEntry(Path("a.py"), "a.py", 100, ".py", FileType.SOURCE_CODE),
        ]
        
        index = FileIndex(project_root=tmp_path, files=files)
        output_path = tmp_path / "index.json"
        index.save(output_path)
        
        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data["total_files"] == 1

    def test_loads_from_json_file(self, tmp_path):
        """Should load index from JSON file."""
        # Create and save index
        files = [
            FileEntry(Path("a.py"), "a.py", 100, ".py", FileType.SOURCE_CODE),
        ]
        original = FileIndex(project_root=tmp_path, files=files)
        output_path = tmp_path / "index.json"
        original.save(output_path)
        
        # Load it back
        loaded = FileIndex.load(output_path)
        
        assert loaded.total_files == 1
        assert len(loaded.files) == 1
        assert loaded.files[0].rel_path == "a.py"
