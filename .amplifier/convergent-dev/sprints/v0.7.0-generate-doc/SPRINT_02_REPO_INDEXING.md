# Sprint 2: Repository Indexing

**Duration:** 1-2 days  
**Goal:** Complete file inventory and efficient traversal structure  
**Value Delivered:** System can discover and navigate all relevant project files

---

## 🎯 Why This Sprint?

After capturing user intent in Sprint 1, we need to discover WHAT FILES exist in the project. This sprint builds the foundation for intelligent file selection by:
1. Creating a complete inventory of all project files
2. Respecting .gitignore/.docignore patterns
3. Building an efficient traversal structure
4. Providing metadata for downstream analysis

Without this, Sprint 3's relevance analysis has nothing to analyze.

---

## 📦 Deliverables

### 1. Repository File Indexer
**Estimated Lines:** ~200 lines + 150 lines tests

**What it does:**
- Discovers all files in the project directory
- Respects .gitignore and .docignore patterns
- Filters out binary files, build artifacts, etc.
- Extracts file metadata (size, extension, path)
- Creates traversable file index structure

**Why this sprint:**
- Sprint 3 needs complete file list for relevance analysis
- Foundation must be solid before adding intelligence
- Quick win that's independently testable

**Implementation notes:**
- Use pathspec library for .gitignore parsing
- Exclude: node_modules, .git, __pycache__, build/, dist/
- Include: source code, docs, config files
- Store relative paths from project root

**Index structure:**
```json
{
  "project_root": "/path/to/project",
  "total_files": 127,
  "indexed_at": "2025-12-06T23:15:00Z",
  "files": [
    {
      "path": "src/main.py",
      "rel_path": "src/main.py",
      "size": 4521,
      "extension": ".py",
      "type": "source_code"
    },
    {
      "path": "README.md",
      "rel_path": "README.md",
      "size": 2143,
      "extension": ".md",
      "type": "documentation"
    }
  ],
  "ignored_patterns": [".git", "node_modules", "__pycache__"],
  "file_counts": {
    "source_code": 89,
    "documentation": 12,
    "config": 15,
    "test": 11
  }
}
```

### 2. File Type Classifier
**Estimated Lines:** ~120 lines + 100 lines tests

**What it does:**
- Classifies files by type (source_code, documentation, config, test, etc.)
- Uses extension patterns and path patterns
- Provides file type metadata for relevance analysis

**Why this sprint:**
- Sprint 3 needs file types for intelligent relevance scoring
- Different file types have different relevance patterns
- Enables type-specific analysis strategies

**Implementation notes:**
- Extension mapping: .py → source_code, .md → documentation
- Path patterns: tests/ → test, docs/ → documentation
- Multiple types possible (e.g., README.md is both documentation and config)

**File type categories:**
```python
class FileType(str, Enum):
    SOURCE_CODE = "source_code"      # .py, .js, .java, etc.
    DOCUMENTATION = "documentation"  # .md, .rst, .txt
    CONFIG = "config"                # .yaml, .toml, .json, .env
    TEST = "test"                    # test_*.py, *.test.js
    BUILD = "build"                  # Makefile, package.json, pyproject.toml
    DATA = "data"                    # .csv, .json (data files)
    UNKNOWN = "unknown"              # Everything else
```

### 3. .docignore Support
**Estimated Lines:** ~80 lines + 60 lines tests

**What it does:**
- Reads .docignore file (if exists)
- Applies additional ignore patterns beyond .gitignore
- Allows users to exclude files from doc generation

**Why this sprint:**
- Users may want to exclude files from docs that are tracked in git
- Examples: generated code, vendored dependencies, internal tools
- Provides control without modifying .gitignore

**Implementation notes:**
- Use same syntax as .gitignore
- Combine with .gitignore patterns (both apply)
- Document in CLI help and README

**.docignore example:**
```
# Exclude generated code
generated/
*.gen.py

# Exclude vendored dependencies
vendor/
third_party/

# Exclude internal tooling
scripts/internal/
```

### 4. Index Persistence
**Estimated Lines:** ~60 lines + 40 lines tests

**What it does:**
- Saves file index to `.doc-evergreen/file_index.json`
- Loads existing index for downstream features
- Updates context.json status to "indexed"

**Why this sprint:**
- Sprint 3 needs to load file list
- Enables caching (don't re-scan on every run)
- Provides audit trail

**Implementation notes:**
- JSON format for human readability
- Include metadata (timestamp, file counts)
- Validate index can be loaded correctly

---

## 🧪 Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all features:

#### 1. 🔴 RED - Write Failing Tests First

**Repository Indexer Tests:**
```python
def test_indexer_discovers_all_files(tmp_path):
    # Create test project structure
    create_test_project(tmp_path)
    
    # Test that indexer finds all files
    indexer = RepoIndexer(tmp_path)
    files = indexer.index_files()
    
    assert len(files) == 10  # Known test structure
    assert any(f.rel_path == 'src/main.py' for f in files)

def test_indexer_respects_gitignore(tmp_path):
    # Create .gitignore with patterns
    (tmp_path / '.gitignore').write_text('*.log\nbuild/\n')
    (tmp_path / 'app.log').touch()
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build/output.txt').write_text('test')
    
    # Test that ignored files are excluded
    indexer = RepoIndexer(tmp_path)
    files = indexer.index_files()
    
    assert not any('app.log' in f.rel_path for f in files)
    assert not any('build/' in f.rel_path for f in files)

def test_indexer_classifies_file_types(tmp_path):
    # Create files of different types
    (tmp_path / 'main.py').touch()
    (tmp_path / 'README.md').touch()
    (tmp_path / 'config.yaml').touch()
    
    # Test file type classification
    indexer = RepoIndexer(tmp_path)
    files = indexer.index_files()
    
    py_file = next(f for f in files if 'main.py' in f.rel_path)
    assert py_file.type == FileType.SOURCE_CODE
    
    md_file = next(f for f in files if 'README.md' in f.rel_path)
    assert md_file.type == FileType.DOCUMENTATION
```

Run tests → Watch them fail → Good!

#### 2. 🟢 GREEN - Write Minimal Implementation

```python
from pathlib import Path
import pathspec
from dataclasses import dataclass
from enum import Enum

@dataclass
class FileInfo:
    path: str
    rel_path: str
    size: int
    extension: str
    type: str

class RepoIndexer:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.ignore_spec = self._load_ignore_patterns()
    
    def _load_ignore_patterns(self):
        patterns = []
        
        # Load .gitignore
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            patterns.extend(gitignore.read_text().splitlines())
        
        # Load .docignore
        docignore = self.project_root / '.docignore'
        if docignore.exists():
            patterns.extend(docignore.read_text().splitlines())
        
        # Add default excludes
        patterns.extend(['.git', '__pycache__', 'node_modules'])
        
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def index_files(self) -> list[FileInfo]:
        files = []
        
        for path in self.project_root.rglob('*'):
            if not path.is_file():
                continue
            
            rel_path = path.relative_to(self.project_root)
            
            # Check if ignored
            if self.ignore_spec.match_file(str(rel_path)):
                continue
            
            # Classify file type
            file_type = self._classify_file(path)
            
            files.append(FileInfo(
                path=str(path),
                rel_path=str(rel_path),
                size=path.stat().st_size,
                extension=path.suffix,
                type=file_type
            ))
        
        return files
    
    def _classify_file(self, path: Path) -> str:
        ext = path.suffix.lower()
        
        # Source code
        if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.go']:
            return 'source_code'
        
        # Documentation
        if ext in ['.md', '.rst', '.txt']:
            return 'documentation'
        
        # Config
        if ext in ['.yaml', '.yml', '.toml', '.json', '.ini', '.env']:
            return 'config'
        
        # Tests
        if 'test' in path.name or path.parent.name == 'tests':
            return 'test'
        
        return 'unknown'
```

Run tests → Watch them pass → Good!

#### 3. 🔵 REFACTOR - Improve Code Quality

- Extract file type classifier to separate class
- Add logging for ignored files
- Improve error handling for permission errors
- Add progress feedback for large repos
- Extract ignore pattern loading

Run tests → Still pass → Good!

### Unit Tests (Write First)

- **File discovery**: Empty dir, single file, nested structure, large repo
- **Ignore patterns**: .gitignore, .docignore, default excludes, combined patterns
- **File classification**: All file types, edge cases, multiple types
- **Path handling**: Absolute/relative, symlinks, special characters
- **Error handling**: Permission denied, missing directory, corrupted files

### Integration Tests (Write First)

- **End-to-end indexing**: Real project structure → file_index.json
- **Context update**: Verify context.json status changes to "indexed"
- **Index reload**: Save index, load back, verify contents match

### Manual Testing (After Automated Tests Pass)

- [ ] Run on doc-evergreen repo - verify sensible file list
- [ ] Create .docignore - verify patterns respected
- [ ] Run on large repo (>1000 files) - verify performance acceptable
- [ ] Check file_index.json - verify human-readable format
- [ ] Verify .git and node_modules excluded automatically

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Content Analysis
- **Why**: That's Sprint 3 - file relevance analysis with LLM
- **Reconsider**: Sprint 3 implementation

### ❌ Incremental Indexing
- **Why**: Full scan is fast enough for MVP (<1000 files typical)
- **Reconsider**: v0.8.0 if performance becomes issue with very large repos

### ❌ Git Metadata
- **Why**: Not needed for basic indexing, adds complexity
- **Examples**: Last modified date, blame info, commit history
- **Reconsider**: v0.8.0 for change detection features

### ❌ Language Detection
- **Why**: File extension is sufficient for MVP
- **Examples**: Shebang parsing, content-based detection
- **Reconsider**: v0.8.0 if users report misclassification issues

### ❌ Index Caching/Invalidation
- **Why**: Regenerate index on every run for simplicity
- **Reconsider**: v0.8.0 if performance data shows need

### ❌ Custom File Filters
- **Why**: .docignore provides sufficient control
- **Examples**: CLI flags like --include, --exclude
- **Reconsider**: Sprint 7 polish if users request

---

## 📋 Dependencies

### Requires from previous sprints:
- **Sprint 1**: context.json with doc_type and purpose (used to inform indexing)

### Provides for future sprints:
- **file_index.json** for Sprint 3 (relevance analysis needs file list)
- **FileInfo objects** for Sprint 3 (metadata for relevance scoring)
- **File type classification** for Sprint 3 (type-aware relevance analysis)

---

## ✅ Acceptance Criteria

### Must Have

- ✅ **Complete file discovery**: Indexes all non-ignored files in project
- ✅ **Respects .gitignore**: Honors gitignore patterns correctly
- ✅ **Supports .docignore**: Additional doc-specific ignore patterns work
- ✅ **File classification**: All files have type metadata
- ✅ **Index persistence**: file_index.json created with all required data
- ✅ **Context update**: context.json status updated to "indexed"
- ✅ **Performance**: Indexes typical project (<500 files) in <2 seconds
- ✅ **Tests pass**: >80% coverage, all tests green

### Nice to Have (Defer if time constrained)

- ❌ **Progress feedback**: Show indexing progress for large repos (defer to Sprint 7)
- ❌ **Index statistics**: Summary of file counts by type (defer to Sprint 7)
- ❌ **Verbose mode**: Show ignored files with reasons (defer to Sprint 7)

---

## 🛠️ Technical Approach

### Key Decisions

**Decision 1: Use pathspec library for .gitignore**
- **Rationale**: Correct .gitignore parsing is complex (many edge cases)
- **Alternative considered**: Custom regex parsing (error-prone)
- **Why pathspec**: Battle-tested, handles all .gitignore syntax

**Decision 2: Store relative paths**
- **Rationale**: Portable across machines, easier to share
- **Alternative considered**: Absolute paths (breaks on different machines)
- **Why relative**: Better for version control, more portable

**Decision 3: Include file type metadata**
- **Rationale**: Sprint 3 needs this for intelligent relevance scoring
- **Alternative considered**: Compute on-the-fly (slower)
- **Why pre-compute**: Single pass, available immediately downstream

**Decision 4: Full re-index on every run**
- **Rationale**: Simple, correct, fast enough for typical projects
- **Alternative considered**: Incremental updates (complex, premature optimization)
- **Why full scan**: YAGNI - optimize later if needed

### External Dependencies

```toml
# pyproject.toml additions
[tool.poetry.dependencies]
pathspec = "^0.11.0"  # .gitignore pattern matching
```

### Implementation Pattern

```python
# src/doc_evergreen/forward/repo_indexer.py

from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List
import pathspec
import json
from datetime import datetime

@dataclass
class FileInfo:
    """Information about a file in the repository."""
    path: str           # Absolute path
    rel_path: str       # Relative to project root
    size: int           # File size in bytes
    extension: str      # File extension (e.g., ".py")
    type: str           # Classified type (source_code, documentation, etc.)

class RepoIndexer:
    """Index all files in a repository."""
    
    DEFAULT_EXCLUDES = [
        '.git',
        '__pycache__',
        '.pytest_cache',
        'node_modules',
        '.venv',
        'venv',
        'build',
        'dist',
        '*.pyc',
        '*.pyo',
        '*.egg-info'
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.ignore_spec = self._load_ignore_patterns()
    
    def index_repository(self) -> dict:
        """Index all files and return complete index."""
        files = self._discover_files()
        
        index = {
            'project_root': str(self.project_root),
            'total_files': len(files),
            'indexed_at': datetime.now().isoformat() + 'Z',
            'files': [asdict(f) for f in files],
            'ignored_patterns': self._get_ignore_patterns(),
            'file_counts': self._count_by_type(files)
        }
        
        # Save to .doc-evergreen/file_index.json
        self._save_index(index)
        
        # Update context status
        self._update_context_status('indexed')
        
        return index
    
    def _load_ignore_patterns(self) -> pathspec.PathSpec:
        """Load ignore patterns from .gitignore and .docignore."""
        patterns = list(self.DEFAULT_EXCLUDES)
        
        # Load .gitignore
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            patterns.extend(gitignore.read_text().splitlines())
        
        # Load .docignore
        docignore = self.project_root / '.docignore'
        if docignore.exists():
            patterns.extend(docignore.read_text().splitlines())
        
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def _discover_files(self) -> List[FileInfo]:
        """Discover all non-ignored files."""
        files = []
        
        for path in self.project_root.rglob('*'):
            if not path.is_file():
                continue
            
            rel_path = path.relative_to(self.project_root)
            
            # Skip ignored files
            if self.ignore_spec.match_file(str(rel_path)):
                continue
            
            # Skip binary files (basic heuristic)
            if self._is_binary(path):
                continue
            
            files.append(FileInfo(
                path=str(path),
                rel_path=str(rel_path),
                size=path.stat().st_size,
                extension=path.suffix,
                type=self._classify_file(path)
            ))
        
        return files
    
    def _classify_file(self, path: Path) -> str:
        """Classify file by type."""
        ext = path.suffix.lower()
        name = path.name.lower()
        parent = path.parent.name.lower()
        
        # Source code
        if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.rb']:
            return 'source_code'
        
        # Documentation
        if ext in ['.md', '.rst', '.txt', '.adoc']:
            return 'documentation'
        
        # Configuration
        if ext in ['.yaml', '.yml', '.toml', '.json', '.ini', '.conf', '.cfg', '.env']:
            return 'config'
        
        # Tests
        if 'test' in name or parent in ['tests', 'test']:
            return 'test'
        
        # Build files
        if name in ['makefile', 'dockerfile', 'package.json', 'pyproject.toml', 'setup.py']:
            return 'build'
        
        return 'unknown'
    
    def _is_binary(self, path: Path) -> bool:
        """Simple binary file detection."""
        try:
            with open(path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True
    
    def _save_index(self, index: dict):
        """Save index to .doc-evergreen/file_index.json."""
        context_dir = Path('.doc-evergreen')
        context_dir.mkdir(exist_ok=True)
        
        index_path = context_dir / 'file_index.json'
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
```

---

## 🔍 What You Learn

After this sprint, you'll discover:

1. **File distribution patterns**: What types of files exist in typical projects
   - → Informs Sprint 3 relevance analysis strategies
   
2. **Ignore pattern usage**: What users commonly exclude
   - → Validates .docignore design, informs defaults
   
3. **Classification accuracy**: Whether simple extension mapping works
   - → May reveal need for more sophisticated detection in v0.8.0
   
4. **Performance characteristics**: How long indexing takes for different project sizes
   - → Determines if caching is needed in future versions

---

## 📊 Success Metrics

### Quantitative
- Indexes typical project (<500 files) in <2 seconds
- Correctly classifies 90%+ files by type
- Respects 100% of .gitignore patterns
- Test coverage >80%

### Qualitative
- file_index.json is human-readable and understandable
- .docignore syntax feels natural (matches .gitignore)
- Indexing feels instant (no perceived delay)
- File classification makes sense (types are intuitive)

---

## 📅 Implementation Order

### TDD-driven daily workflow

**Day 1 (Morning): File Discovery**
- 🔴 Write failing tests for file discovery
- 🟢 Implement basic file traversal with Path.rglob()
- 🔵 Refactor: Add binary file detection, improve error handling
- ✅ Commit: "feat: add repository file discovery"

**Day 1 (Afternoon): Ignore Patterns**
- 🔴 Write failing tests for .gitignore/.docignore
- 🟢 Implement pathspec integration and pattern matching
- 🔵 Refactor: Extract ignore loading, add default excludes
- ✅ Commit: "feat: add ignore pattern support"

**Day 2 (Morning): File Classification**
- 🔴 Write failing tests for file type classification
- 🟢 Implement extension-based classification
- 🔵 Refactor: Extract classifier, improve type detection
- ✅ Commit: "feat: add file type classification"

**Day 2 (Afternoon): Index Persistence & Integration**
- 🔴 Write integration tests for complete workflow
- 🟢 Implement index saving and context update
- 🔵 Polish: Add metadata, improve JSON format
- ✅ Manual testing & final commit
- ✅ Sprint review: Demo file indexing on real project

**Note:** Each feature follows multiple red-green-refactor micro-cycles

---

## ⚠️ Known Limitations (By Design)

1. **No incremental updates** - Full re-scan on every run
   - Why acceptable: Fast enough for typical projects, simple and correct
   
2. **Basic binary detection** - NULL byte check only
   - Why acceptable: Catches most binary files, edge cases acceptable for MVP
   
3. **Extension-based classification** - No content analysis
   - Why acceptable: Accurate enough for typical projects, fast
   
4. **No symlink handling** - Symlinks ignored
   - Why acceptable: Uncommon in documentation scenarios, avoid infinite loops

---

## 🎯 Next Sprint Preview

After this sprint ships, the most pressing need will be:

**Sprint 3: Intelligent File Relevance Analysis** - Now that we have a complete file inventory, we need to determine WHICH FILES are relevant for the user's documentation purpose. Sprint 3 will use LLM-powered analysis to identify relevant files and document WHY they're relevant, providing the critical input for Sprint 4-5's outline generation.

The file_index.json from Sprint 2 becomes the input to Sprint 3's relevance analyzer, which will filter down to the 70-80% most relevant files.
