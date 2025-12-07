# Sprint 3: Intelligent File Relevance Analysis

**Duration:** 2 days  
**Goal:** Context-aware file analysis with note-taking (70-80% accuracy)  
**Value Delivered:** System intelligently identifies which files matter for the doc

---

## 🎯 Why This Sprint?

After Sprint 2 gave us a complete file inventory, we need to answer: **WHICH FILES are actually relevant for this specific documentation?** This sprint adds intelligence by:
1. Analyzing each file against the doc purpose
2. Scoring relevance using LLM
3. Documenting WHY files are relevant
4. Creating attention guides for outline generation

This is the critical bridge between "all files" (Sprint 2) and "intelligent outline" (Sprint 4-5).

---

## 📦 Deliverables

### 1. Context-Aware Relevance Analyzer
**Estimated Lines:** ~250 lines + 180 lines tests

**What it does:**
- Loads file_index.json from Sprint 2
- Loads context.json (doc_type, purpose) from Sprint 1
- For each file: LLM analyzes relevance to doc purpose
- Returns relevance score (0-100) with reasoning
- Filters to top N most relevant files

**Why this sprint:**
- Sprint 4-5 outline generation needs focused file list
- Can't analyze 500+ files - need intelligent filtering to top 20-50
- Reasoning provides attention guides for LLM context

**Implementation notes:**
- Batch processing for efficiency (analyze N files per LLM call)
- Use cheaper/faster LLM model (GPT-3.5 sufficient)
- Focus on high-signal files (source code, docs, config)
- Skip obviously irrelevant (tests, build artifacts)

**Analysis prompt template:**
```
You are analyzing files for documentation generation.

Doc Type: {doc_type}
Doc Purpose: {purpose}

File: {file_path}
File Type: {file_type}
File Size: {size} bytes

Context (first 500 chars):
{file_preview}

Question: Is this file relevant for generating {doc_type} documentation with purpose "{purpose}"?

Respond with:
1. Relevance score (0-100)
2. Reasoning (2-3 sentences: WHY relevant or not relevant)
3. Key material (if relevant: WHAT information in this file is useful)

Format your response as JSON:
{
  "score": 85,
  "reasoning": "Contains main CLI entry point with command definitions...",
  "key_material": "Command structure, argument parsing, help text"
}
```

### 2. File Preview Generator
**Estimated Lines:** ~120 lines + 80 lines tests

**What it does:**
- Extracts file preview (first N lines or bytes)
- Provides enough context for LLM to judge relevance
- Handles different file types appropriately

**Why this sprint:**
- LLM needs context to judge relevance
- Full file content is expensive and unnecessary
- Preview is sufficient signal for relevance scoring

**Implementation notes:**
- Extract first 500 characters for quick scan
- For code: prioritize docstrings, imports, class/function definitions
- For markdown: prioritize headings and first paragraph
- For config: include key top-level keys

**Preview strategies by file type:**
```python
PREVIEW_STRATEGIES = {
    'source_code': {
        'length': 500,
        'include': ['docstrings', 'imports', 'class_defs', 'function_defs']
    },
    'documentation': {
        'length': 800,
        'include': ['headings', 'first_paragraph', 'toc']
    },
    'config': {
        'length': 300,
        'include': ['top_level_keys', 'comments']
    }
}
```

### 3. Relevance Note-Taker
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
- Stores relevance analysis results
- For each relevant file: score, reasoning, key material
- Creates `.doc-evergreen/relevance_notes.json`
- Provides structured input for Sprint 4-5

**Why this sprint:**
- Outline generation needs to know WHY files are relevant
- Reasoning acts as "attention guide" for LLM
- Key material helps map files to specific sections

**Implementation notes:**
- Only store files above relevance threshold (score > 50)
- Sort by relevance score (most relevant first)
- Include metadata (timestamp, total files analyzed)

**relevance_notes.json structure:**
```json
{
  "analyzed_at": "2025-12-06T23:20:00Z",
  "total_files_analyzed": 127,
  "relevant_files_count": 18,
  "threshold": 50,
  "doc_type": "tutorial",
  "purpose": "Help developers get started in 5 minutes",
  "relevant_files": [
    {
      "file": "src/cli.py",
      "score": 95,
      "reasoning": "Main CLI entry point with command definitions, help text, and argument parsing - essential for showing users how to run commands",
      "key_material": "Command structure, argument parsing, usage examples, help text"
    },
    {
      "file": "README.md",
      "score": 85,
      "reasoning": "Existing project overview and getting started guide - provides context about what the tool does",
      "key_material": "Project description, value proposition, high-level architecture"
    },
    {
      "file": "pyproject.toml",
      "score": 75,
      "reasoning": "Defines package metadata and dependencies - needed for installation instructions",
      "key_material": "Package name, version, dependencies, installation method"
    }
  ]
}
```

### 4. Batch LLM Processing
**Estimated Lines:** ~180 lines + 120 lines tests

**What it does:**
- Efficiently processes multiple files per LLM call
- Handles rate limiting and retries
- Provides progress feedback

**Why this sprint:**
- Single-file analysis is too slow (hundreds of API calls)
- Batch processing reduces cost and latency
- Better user experience with progress tracking

**Implementation notes:**
- Batch size: 5-10 files per call (balance efficiency vs. quality)
- Use async processing where possible
- Handle partial failures gracefully
- Cache results to avoid re-analysis

**Batch processing pattern:**
```python
async def analyze_files_batch(files: List[FileInfo], context: dict) -> List[RelevanceNote]:
    """Analyze multiple files in batches."""
    results = []
    batch_size = 10
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        
        # Analyze batch
        batch_results = await analyze_batch(batch, context)
        results.extend(batch_results)
        
        # Progress feedback
        progress = (i + len(batch)) / len(files) * 100
        print(f"🔍 Analyzing relevance: {progress:.0f}% ({i+len(batch)}/{len(files)} files)")
    
    return results
```

---

## 🧪 Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all features:

#### 1. 🔴 RED - Write Failing Tests First

**Relevance Analyzer Tests:**
```python
def test_analyzer_scores_relevant_file_high():
    # Test that clearly relevant file scores high
    context = {
        'doc_type': 'tutorial',
        'purpose': 'Help developers get started quickly'
    }
    file = FileInfo(
        path='src/cli.py',
        type='source_code',
        content='def main():\n    # CLI entry point...'
    )
    
    analyzer = RelevanceAnalyzer()
    result = analyzer.analyze_file(file, context)
    
    assert result.score >= 70
    assert 'cli' in result.reasoning.lower() or 'command' in result.reasoning.lower()

def test_analyzer_scores_irrelevant_file_low():
    # Test that clearly irrelevant file scores low
    context = {
        'doc_type': 'tutorial',
        'purpose': 'Help developers get started quickly'
    }
    file = FileInfo(
        path='tests/test_edge_cases.py',
        type='test',
        content='def test_obscure_edge_case()...'
    )
    
    analyzer = RelevanceAnalyzer()
    result = analyzer.analyze_file(file, context)
    
    assert result.score < 50

def test_analyzer_provides_reasoning():
    # Test that reasoning is provided
    result = analyzer.analyze_file(file, context)
    
    assert len(result.reasoning) > 20
    assert result.key_material is not None or result.score < 50
```

**Note-Taker Tests:**
```python
def test_note_taker_filters_by_threshold():
    # Test that low-scoring files are filtered
    notes = [
        RelevanceNote(file='high.py', score=85, reasoning='...', key_material='...'),
        RelevanceNote(file='low.py', score=30, reasoning='...', key_material=None),
    ]
    
    note_taker = RelevanceNoteTaker(threshold=50)
    filtered = note_taker.filter_relevant(notes)
    
    assert len(filtered) == 1
    assert filtered[0].file == 'high.py'

def test_note_taker_sorts_by_score():
    # Test that notes are sorted by relevance
    note_taker = RelevanceNoteTaker()
    sorted_notes = note_taker.sort_by_relevance(notes)
    
    assert sorted_notes[0].score >= sorted_notes[1].score
```

Run tests → Watch them fail → Good!

#### 2. 🟢 GREEN - Write Minimal Implementation

```python
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class RelevanceNote:
    file: str
    score: int
    reasoning: str
    key_material: Optional[str]

class RelevanceAnalyzer:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_file(self, file: FileInfo, context: dict) -> RelevanceNote:
        """Analyze single file relevance."""
        # Generate preview
        preview = self._generate_preview(file)
        
        # Build prompt
        prompt = f"""
        Analyze file relevance for documentation generation.
        
        Doc Type: {context['doc_type']}
        Doc Purpose: {context['purpose']}
        
        File: {file.rel_path}
        Type: {file.type}
        
        Preview:
        {preview}
        
        Score relevance 0-100 and explain why.
        
        JSON format:
        {{"score": 85, "reasoning": "...", "key_material": "..."}}
        """
        
        # Call LLM
        response = self.llm.generate(prompt)
        result = json.loads(response)
        
        return RelevanceNote(
            file=file.rel_path,
            score=result['score'],
            reasoning=result['reasoning'],
            key_material=result.get('key_material')
        )
    
    def _generate_preview(self, file: FileInfo) -> str:
        """Generate file preview for analysis."""
        try:
            with open(file.path, 'r', encoding='utf-8') as f:
                return f.read(500)
        except:
            return "[Unable to read file]"
```

Run tests → Watch them pass → Good!

#### 3. 🔵 REFACTOR - Improve Code Quality

- Extract prompt generation to separate function
- Add error handling for LLM failures
- Implement batch processing
- Add caching for repeated analysis
- Improve preview generation by file type

Run tests → Still pass → Good!

### Unit Tests (Write First)

- **Relevance scoring**: High relevance, low relevance, edge cases
- **Reasoning quality**: Validate reasoning makes sense
- **File preview**: Different file types, encoding issues, large files
- **Batch processing**: Multiple files, failures, partial results
- **Filtering**: Threshold application, sorting by score

### Integration Tests (Write First)

- **End-to-end analysis**: file_index.json → relevance_notes.json
- **Context integration**: Uses doc_type and purpose correctly
- **Status update**: context.json status changes to "analyzed"

### Manual Testing (After Automated Tests Pass)

- [ ] Run on doc-evergreen repo - verify sensible relevance scores
- [ ] Check reasoning quality - does it make sense?
- [ ] Verify key_material is useful (not just file name)
- [ ] Test with different doc types - verify type-aware analysis
- [ ] Check relevance_notes.json - verify human-readable

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Semantic Search
- **Why**: LLM-based analysis is sufficient and more flexible
- **Reconsider**: v0.8.0 if performance/cost becomes issue

### ❌ ML-Based Relevance Models
- **Why**: LLM provides good accuracy without training data
- **Reconsider**: v0.8.0 if accuracy is insufficient

### ❌ User Feedback Loop
- **Why**: v0.7.0 is single-pass, no iteration
- **Examples**: User marks files as relevant/irrelevant to improve
- **Reconsider**: v0.8.0 for learning system

### ❌ Content Summarization
- **Why**: Preview is sufficient for relevance, full summary expensive
- **Reconsider**: Sprint 4-5 if outline generation needs more context

### ❌ Relevance Caching Across Runs
- **Why**: Context changes between runs, cache may be stale
- **Reconsider**: v0.8.0 if re-analysis is common workflow

### ❌ Relevance Explanation UI
- **Why**: CLI tool, JSON output is sufficient
- **Examples**: Web UI showing why files scored high/low
- **Reconsider**: v0.9.0 if GUI is added

---

## 📋 Dependencies

### Requires from previous sprints:
- **Sprint 1**: context.json with doc_type and purpose
- **Sprint 2**: file_index.json with complete file list

### Provides for future sprints:
- **relevance_notes.json** for Sprint 4-5 (outline generation input)
- **Filtered file list** for Sprint 4-5 (focused to relevant files only)
- **Attention guides** for Sprint 4-5 (key_material directs LLM focus)

---

## ✅ Acceptance Criteria

### Must Have

- ✅ **Relevance scoring works**: Files scored appropriately (70-80% accuracy)
- ✅ **Reasoning provided**: Each relevant file has clear reasoning
- ✅ **Key material identified**: Relevant files have attention guides
- ✅ **Filtering works**: Only relevant files (score > 50) in output
- ✅ **relevance_notes.json created**: All required data present
- ✅ **Context update**: context.json status updated to "analyzed"
- ✅ **Performance**: Analyzes typical project in <30 seconds
- ✅ **Tests pass**: >80% coverage, all tests green

### Success Targets

- **Precision**: 70%+ (files marked relevant are actually useful)
- **Recall**: 80%+ (most truly relevant files are identified)
- **Reasoning quality**: Makes sense to human reviewer

### Nice to Have (Defer if time constrained)

- ❌ **Confidence intervals**: Score ranges instead of point estimates (defer to v0.8.0)
- ❌ **Interactive refinement**: User can adjust scores (defer to Sprint 7)
- ❌ **Detailed analytics**: Show score distribution, statistics (defer to Sprint 7)

---

## 🛠️ Technical Approach

### Key Decisions

**Decision 1: LLM-based analysis (not semantic search)**
- **Rationale**: More flexible, understands context and intent
- **Alternative considered**: Embedding-based semantic search (faster, less context-aware)
- **Why LLM**: Better accuracy for nuanced relevance judgments

**Decision 2: File previews (not full content)**
- **Rationale**: Sufficient signal, much faster and cheaper
- **Alternative considered**: Full file analysis (expensive, unnecessary)
- **Why preview**: 90% of signal in first 500 chars for most files

**Decision 3: Batch processing**
- **Rationale**: Reduces API calls, faster overall
- **Alternative considered**: Single-file processing (simpler, slower)
- **Why batch**: Cost and performance optimization

**Decision 4: Relevance threshold of 50**
- **Rationale**: Balanced - not too restrictive, filters noise
- **Alternative considered**: Dynamic threshold based on distribution
- **Why fixed**: Simpler, good enough for MVP

### LLM Configuration

```python
# Recommended LLM settings
LLM_CONFIG = {
    'model': 'gpt-3.5-turbo',  # Cheaper, faster, sufficient for relevance
    'temperature': 0.3,         # Lower for consistent scoring
    'max_tokens': 200,          # Short responses (score + reasoning)
}
```

### Implementation Pattern

```python
# src/doc_evergreen/forward/relevance_analyzer.py

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import json

@dataclass
class RelevanceNote:
    """Relevance analysis result for a file."""
    file: str
    score: int
    reasoning: str
    key_material: Optional[str]

class RelevanceAnalyzer:
    """Analyze file relevance for documentation generation."""
    
    RELEVANCE_THRESHOLD = 50
    PREVIEW_LENGTH = 500
    BATCH_SIZE = 10
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_repository(self, context_path: Path = Path('.doc-evergreen/context.json')) -> dict:
        """Analyze all files in repository for relevance."""
        # Load context and file index
        context = self._load_context(context_path)
        file_index = self._load_file_index()
        
        # Filter to analyzable files
        analyzable_files = self._filter_analyzable(file_index['files'])
        
        print(f"🔍 Analyzing {len(analyzable_files)} files for relevance...")
        
        # Analyze in batches
        notes = []
        for i in range(0, len(analyzable_files), self.BATCH_SIZE):
            batch = analyzable_files[i:i+self.BATCH_SIZE]
            batch_notes = self._analyze_batch(batch, context)
            notes.extend(batch_notes)
            
            progress = min((i + self.BATCH_SIZE) / len(analyzable_files) * 100, 100)
            print(f"   Progress: {progress:.0f}%")
        
        # Filter and sort
        relevant_notes = [n for n in notes if n.score >= self.RELEVANCE_THRESHOLD]
        relevant_notes.sort(key=lambda n: n.score, reverse=True)
        
        # Save results
        result = {
            'analyzed_at': datetime.now().isoformat() + 'Z',
            'total_files_analyzed': len(analyzable_files),
            'relevant_files_count': len(relevant_notes),
            'threshold': self.RELEVANCE_THRESHOLD,
            'doc_type': context['doc_type'],
            'purpose': context['purpose'],
            'relevant_files': [self._note_to_dict(n) for n in relevant_notes]
        }
        
        self._save_notes(result)
        self._update_context_status('analyzed')
        
        print(f"✅ Found {len(relevant_notes)} relevant files (out of {len(analyzable_files)})")
        
        return result
    
    def _analyze_batch(self, files: List[dict], context: dict) -> List[RelevanceNote]:
        """Analyze a batch of files."""
        # Build batch prompt
        prompt = self._build_batch_prompt(files, context)
        
        # Call LLM
        response = self.llm.generate(prompt)
        
        # Parse results
        results = json.loads(response)
        
        return [
            RelevanceNote(
                file=r['file'],
                score=r['score'],
                reasoning=r['reasoning'],
                key_material=r.get('key_material')
            )
            for r in results
        ]
    
    def _filter_analyzable(self, files: List[dict]) -> List[dict]:
        """Filter to files worth analyzing."""
        analyzable_types = ['source_code', 'documentation', 'config', 'build']
        return [f for f in files if f['type'] in analyzable_types]
    
    def _build_batch_prompt(self, files: List[dict], context: dict) -> str:
        """Build prompt for batch analysis."""
        file_previews = []
        for f in files:
            preview = self._generate_preview(f)
            file_previews.append(f"""
File: {f['rel_path']}
Type: {f['type']}
Preview:
{preview}
---
            """)
        
        return f"""
Analyze these files for documentation generation relevance.

Doc Type: {context['doc_type']}
Doc Purpose: {context['purpose']}

For each file, provide:
- score: 0-100 relevance score
- reasoning: Why relevant or not (2-3 sentences)
- key_material: What information is useful (if relevant)

Files:
{''.join(file_previews)}

Respond with JSON array:
[
  {{"file": "path/to/file.py", "score": 85, "reasoning": "...", "key_material": "..."}},
  ...
]
        """
    
    def _generate_preview(self, file: dict) -> str:
        """Generate preview of file for analysis."""
        try:
            with open(file['path'], 'r', encoding='utf-8') as f:
                return f.read(self.PREVIEW_LENGTH)
        except Exception as e:
            return f"[Unable to read: {e}]"
```

---

## 🔍 What You Learn

After this sprint, you'll discover:

1. **Relevance patterns**: Which file types are consistently relevant for different doc types
   - → Informs Sprint 4-5 section-to-source mapping strategies
   
2. **LLM accuracy**: How well LLM judges relevance vs. human judgment
   - → Validates LLM approach, or signals need for improvement
   
3. **Key material quality**: Whether attention guides are actually useful
   - → Determines if Sprint 4-5 can rely on them for outline generation
   
4. **Performance characteristics**: Cost and latency of relevance analysis
   - → Informs caching and optimization needs for v0.8.0

---

## 📊 Success Metrics

### Quantitative
- **Precision**: 70%+ (files marked relevant are actually useful)
- **Recall**: 80%+ (most truly relevant files are identified)
- **Performance**: Analyzes 100 files in <30 seconds
- **Test coverage**: >80%

### Qualitative
- Reasoning makes sense to human reviewer
- Key material provides useful attention guides
- Relevant file list feels "right" (no obvious misses)
- Filtering significantly reduces file set (127 → 15-20 files typical)

### Validation Method
**Manual review**: For doc-evergreen repo:
1. Run relevance analyzer for "tutorial" doc
2. Review top 10 relevant files - should be obviously useful
3. Review bottom 5 relevant files - should be borderline
4. Check excluded files - should be clearly irrelevant

---

## 📅 Implementation Order

### TDD-driven daily workflow

**Day 1 (Morning): File Preview Generator**
- 🔴 Write failing tests for preview generation
- 🟢 Implement basic preview extraction
- 🔵 Refactor: Add file-type-specific preview strategies
- ✅ Commit: "feat: add file preview generator"

**Day 1 (Afternoon): Single-File Relevance Analyzer**
- 🔴 Write failing tests for relevance analysis
- 🟢 Implement LLM-based relevance scoring
- 🔵 Refactor: Improve prompt, add error handling
- ✅ Commit: "feat: add relevance analyzer"

**Day 2 (Morning): Batch Processing**
- 🔴 Write failing tests for batch analysis
- 🟢 Implement batch prompt and processing
- 🔵 Refactor: Add progress feedback, optimize batching
- ✅ Commit: "feat: add batch relevance processing"

**Day 2 (Afternoon): Note Taking & Integration**
- 🔴 Write integration tests for complete workflow
- 🟢 Implement note storage and context update
- 🔵 Polish: Sort by score, filter by threshold
- ✅ Manual validation on real project
- ✅ Sprint review: Demo relevance analysis results

**Note:** Each feature follows multiple red-green-refactor micro-cycles

---

## ⚠️ Known Limitations (By Design)

1. **Preview-based analysis** - Not full content analysis
   - Why acceptable: Sufficient signal for relevance judgment, much faster
   
2. **Fixed relevance threshold (50)** - Not adaptive
   - Why acceptable: Good enough for typical projects, simpler
   
3. **No user feedback loop** - Can't refine based on user corrections
   - Why acceptable: Single-pass generation for v0.7.0
   
4. **LLM cost per analysis** - Pay per file analyzed
   - Why acceptable: One-time cost per doc, reasonable for MVP

---

## 🎯 Next Sprint Preview

After this sprint ships, the most pressing need will be:

**Sprint 4-5: Hierarchical Outline Generation (THE CORE INNOVATION ⭐)** - Now that we know WHICH FILES are relevant and WHY, we can generate an intelligent hierarchical outline. These two sprints will implement the core innovation of v0.7.0: nesting-aware outline generation with sophisticated prompt engineering.

The relevance_notes.json from Sprint 3 becomes the critical input - the "attention guides" (key_material) tell the outline generator what information each file contains, enabling intelligent section-to-source mapping.

This is where v0.7.0's real value emerges!
