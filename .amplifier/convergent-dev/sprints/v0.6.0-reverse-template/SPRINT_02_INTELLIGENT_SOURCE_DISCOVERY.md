# Sprint 2: Intelligent Source Discovery ⭐

**Duration:** 2-3 days  
**Goal:** Achieve 70-80% source discovery accuracy through pattern + semantic + LLM approach  
**Value Delivered:** Generated templates have relevant, accurate sources requiring minimal refinement

⚠️ **CRITICAL PATH**: This is the hardest and highest-risk component. Day 5 checkpoint evaluates accuracy.

---

## 🎯 Why This Sprint?

Sprint 1 proved the concept with naive pattern matching (50-60% accuracy). Now we need to hit **70-80% accuracy** to make the feature truly useful.

**The Challenge**: Given a documentation section like "API Reference," automatically discover which source files in the codebase are relevant.

**Why This Is Hard**:
- Pattern matching alone misses context-specific files
- Projects have different structures
- Section headings can be vague ("Features" → which code?)
- Need to balance precision (relevant files) with recall (don't miss important files)

**Why This Sprint Next**:
After Sprint 1, you're motivated by a working prototype and have clear understanding of what "good sources" look like. Now tackle the hard algorithm work.

---

## 📦 Deliverables

### 1. Semantic Search for Source Files
**Estimated Lines:** ~250 lines + 200 lines tests

**What it does:**
- Index codebase files (file paths, content snippets)
- Extract key topics/terms from section content
- Search codebase for files containing those terms
- Return ranked list of candidate files

**Why this sprint:**
Bridges the gap between pattern matching and LLM scoring. Semantic search finds files that pattern matching misses.

**Implementation notes:**
```python
class SemanticSourceSearcher:
    """
    Find source files relevant to a section using content-based search.
    """
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.file_index = self._build_file_index()
    
    def _build_file_index(self):
        """
        Index all source files in project.
        Returns: {file_path: {content_snippet, keywords, metadata}}
        """
        # Walk project directory
        # Read file contents (respecting .gitignore)
        # Extract keywords from files
        # Build searchable index
        pass
    
    def search(self, section_heading, section_content, key_terms):
        """
        Search for files relevant to section.
        
        Args:
            section_heading: "API Reference"
            section_content: "The API provides three endpoints..."
            key_terms: ["API", "endpoints", "routes", "handlers"]
        
        Returns:
            [{file_path, score, match_reason}]
        """
        # Search file_index for key_terms
        # Score files by term frequency
        # Consider file path relevance (api/ directory for API section)
        # Return ranked results
        pass
```

**TDD approach:**
```python
# 🔴 RED: Write failing test
def test_semantic_search_finds_api_files():
    # Mock project structure
    project = create_mock_project({
        'src/api/routes.py': 'def get_users(): ...',
        'src/api/handlers.py': 'class UserHandler: ...',
        'src/database/models.py': 'class User: ...',
        'README.md': '# Project'
    })
    
    searcher = SemanticSourceSearcher(project.root)
    results = searcher.search(
        section_heading="API Reference",
        section_content="The API provides endpoints for user management",
        key_terms=["API", "endpoints", "users"]
    )
    
    # Should find API files, not database files
    file_paths = [r['file_path'] for r in results]
    assert 'src/api/routes.py' in file_paths
    assert 'src/api/handlers.py' in file_paths
    assert 'src/database/models.py' not in file_paths  # Not in top results
    # FAILS - searcher doesn't exist

# 🟢 GREEN: Implement basic search
# Use simple grep-like search for terms
# Score by term frequency

# 🔵 REFACTOR: Improve scoring algorithm
# Add path-based relevance
# Handle synonyms (API → routes, endpoints)
# Optimize for performance
```

**Key algorithm decisions:**
- **File indexing**: Cache file contents to avoid repeated I/O
- **Term extraction**: Use section content keywords (nouns, verbs)
- **Scoring**: TF-IDF style (frequency × rarity)
- **Path weighting**: Files in `api/` score higher for "API" sections

---

### 2. LLM Relevance Scoring
**Estimated Lines:** ~200 lines + 150 lines tests

**What it does:**
- For each candidate source file, use LLM to score relevance (0-10)
- LLM explains why file is relevant (or not)
- Filter sources with score >5
- Rank sources by score

**Why this sprint:**
LLM provides semantic understanding that pattern matching and keyword search can't achieve. Achieves 70-80% accuracy target.

**Implementation notes:**
```python
class LLMRelevanceScorer:
    """
    Use LLM to score source file relevance to documentation section.
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def score_relevance(self, section_heading, section_content, source_file_path, source_file_content):
        """
        Score how relevant a source file is to a doc section.
        
        Returns:
            {
                'score': 7,  # 0-10
                'reasoning': 'This file defines API endpoints mentioned in section',
                'confidence': 'high'  # low/medium/high
            }
        """
        prompt = f"""Given this documentation section:

Heading: {section_heading}
Content (excerpt): {section_content[:500]}

Rate the relevance of this source file on a scale of 0-10:

File: {source_file_path}
Content (excerpt): {source_file_content[:1000]}

Scoring guide:
- 9-10: Directly implements features/APIs described in section
- 7-8: Closely related, provides important context
- 5-6: Somewhat related, mentions similar concepts
- 3-4: Tangentially related
- 0-2: Not relevant

Respond in JSON:
{{
    "score": <0-10>,
    "reasoning": "<one sentence explanation>",
    "confidence": "<low|medium|high>"
}}"""

        response = self.llm.generate(prompt, temperature=0)  # Deterministic
        return self._parse_response(response)
    
    def score_batch(self, section, candidate_files, max_candidates=10):
        """
        Score multiple candidate files.
        Limit to max_candidates to control LLM costs.
        """
        # Score each candidate
        # Filter score >5
        # Sort by score descending
        # Return top N results
        pass
```

**TDD approach:**
```python
# 🔴 RED: Test LLM scoring
def test_llm_scores_relevant_file_highly():
    scorer = LLMRelevanceScorer(mock_llm)
    
    result = scorer.score_relevance(
        section_heading="API Reference",
        section_content="The API provides /users and /posts endpoints",
        source_file_path="src/api/routes.py",
        source_file_content="@app.route('/users')\\ndef get_users(): ..."
    )
    
    assert result['score'] >= 7  # Should be high relevance
    assert 'endpoint' in result['reasoning'].lower()
    # FAILS - scorer doesn't exist

# 🟢 GREEN: Implement LLM call
# Basic prompt engineering
# Parse JSON response

# 🔵 REFACTOR: Improve prompt
# Add few-shot examples
# Handle LLM failures gracefully
# Add confidence estimation
```

**Cost optimization:**
- Limit to top 10 candidates from semantic search (not all files)
- Use temperature=0 for deterministic results
- Cache results (same file + section → same score)
- Consider batch scoring to reduce API calls

---

### 3. Integrated Discovery Pipeline
**Estimated Lines:** ~200 lines + 150 lines tests

**What it does:**
- Combines pattern matching + semantic search + LLM scoring
- Multi-stage filtering: broad → narrow → precise
- Returns top 3-5 sources per section with confidence scores

**Why this sprint:**
Integrates all discovery methods into production-ready pipeline.

**Implementation notes:**
```python
class IntelligentSourceDiscoverer:
    """
    Multi-stage source discovery pipeline.
    
    Stage 1: Pattern matching (broad net)
    Stage 2: Semantic search (narrow to relevant)
    Stage 3: LLM scoring (precise ranking)
    """
    
    def __init__(self, project_root, llm_client):
        self.pattern_discoverer = NaiveSourceDiscoverer(project_root)
        self.semantic_searcher = SemanticSourceSearcher(project_root)
        self.llm_scorer = LLMRelevanceScorer(llm_client)
    
    def discover_sources(self, section_heading, section_content, max_sources=5):
        """
        Discover relevant sources through 3-stage pipeline.
        
        Returns:
            [
                {
                    'path': 'src/api/routes.py',
                    'relevance_score': 8,
                    'match_reason': 'Implements API endpoints',
                    'discovery_method': 'llm_scored'
                },
                ...
            ]
        """
        all_candidates = []
        
        # Stage 1: Pattern matching
        pattern_matches = self.pattern_discoverer.discover(
            section_heading, section_content
        )
        all_candidates.extend([
            {'path': p, 'source': 'pattern', 'score': 6}
            for p in pattern_matches
        ])
        
        # Stage 2: Semantic search
        key_terms = self._extract_key_terms(section_content)
        semantic_matches = self.semantic_searcher.search(
            section_heading, section_content, key_terms
        )
        all_candidates.extend([
            {'path': m['file_path'], 'source': 'semantic', 'score': m['score']}
            for m in semantic_matches[:20]  # Top 20 from semantic
        ])
        
        # Deduplicate candidates
        unique_candidates = self._deduplicate(all_candidates)
        
        # Stage 3: LLM scoring (top 10 candidates only)
        top_candidates = sorted(unique_candidates, key=lambda x: x['score'], reverse=True)[:10]
        
        scored_candidates = []
        for candidate in top_candidates:
            file_content = self._read_file(candidate['path'])
            llm_result = self.llm_scorer.score_relevance(
                section_heading, section_content,
                candidate['path'], file_content
            )
            scored_candidates.append({
                'path': candidate['path'],
                'relevance_score': llm_result['score'],
                'match_reason': llm_result['reasoning'],
                'confidence': llm_result['confidence'],
                'discovery_method': f"{candidate['source']} + llm_scored"
            })
        
        # Filter and rank
        relevant = [c for c in scored_candidates if c['relevance_score'] >= 5]
        ranked = sorted(relevant, key=lambda x: x['relevance_score'], reverse=True)
        
        return ranked[:max_sources]
```

**TDD approach:**
```python
# 🔴 RED: Integration test
def test_integrated_discovery_finds_accurate_sources():
    discoverer = IntelligentSourceDiscoverer(
        project_root='/path/to/doc-evergreen',
        llm_client=mock_llm
    )
    
    sources = discoverer.discover_sources(
        section_heading="CLI Commands",
        section_content="The tool provides commands: generate, validate, reverse...",
        max_sources=5
    )
    
    # Should find CLI-related files
    assert len(sources) > 0
    assert any('cli' in s['path'].lower() for s in sources)
    # All sources should have high relevance
    assert all(s['relevance_score'] >= 5 for s in sources)
    # FAILS - discoverer doesn't exist

# 🟢 GREEN: Wire components together
# 🔵 REFACTOR: Optimize pipeline
# Add caching, better deduplication
```

---

### 4. Accuracy Validation & Metrics
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
- Measure discovery accuracy against known-good test cases
- Compute precision, recall, F1 score
- Generate accuracy report for Day 5 checkpoint

**Why this sprint:**
Day 5 checkpoint requires quantitative accuracy measurement to decide if we're on track or need to adjust.

**Implementation notes:**
```python
class AccuracyValidator:
    """
    Validate source discovery accuracy against ground truth.
    """
    
    def __init__(self, test_cases):
        """
        test_cases = [
            {
                'doc_path': 'README.md',
                'section': 'API Reference',
                'ground_truth_sources': ['src/api/routes.py', 'src/api/handlers.py'],
                'section_content': '...'
            },
            ...
        ]
        """
        self.test_cases = test_cases
    
    def evaluate(self, discoverer):
        """
        Run discoverer on all test cases and compute accuracy metrics.
        
        Returns:
            {
                'precision': 0.75,  # How many discovered sources are correct?
                'recall': 0.80,     # How many correct sources did we find?
                'f1_score': 0.77,
                'per_section': [{...}]
            }
        """
        results = []
        
        for test_case in self.test_cases:
            discovered = discoverer.discover_sources(
                test_case['section'],
                test_case['section_content']
            )
            discovered_paths = {d['path'] for d in discovered}
            ground_truth = set(test_case['ground_truth_sources'])
            
            tp = len(discovered_paths & ground_truth)  # True positives
            fp = len(discovered_paths - ground_truth)  # False positives
            fn = len(ground_truth - discovered_paths)  # False negatives
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            results.append({
                'section': test_case['section'],
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'discovered': list(discovered_paths),
                'ground_truth': list(ground_truth)
            })
        
        # Aggregate metrics
        avg_precision = sum(r['precision'] for r in results) / len(results)
        avg_recall = sum(r['recall'] for r in results) / len(results)
        avg_f1 = sum(r['f1'] for r in results) / len(results)
        
        return {
            'precision': avg_precision,
            'recall': avg_recall,
            'f1_score': avg_f1,
            'per_section': results
        }
```

**Test cases:**
Create ground truth for doc-evergreen's README:
- Installation → `pyproject.toml`, `setup.py` (if exists)
- CLI Commands → `src/cli.py`, `src/commands/`
- Template System → `src/templates/`, template-related modules
- Generation → `src/generator/`, `src/chunked_generator.py`

**TDD approach:**
```python
# 🔴 RED: Test accuracy measurement
def test_accuracy_validator_computes_metrics():
    test_cases = [
        {
            'section': 'Installation',
            'section_content': 'To install...',
            'ground_truth_sources': ['pyproject.toml']
        }
    ]
    
    validator = AccuracyValidator(test_cases)
    mock_discoverer = MockDiscoverer(returns=['pyproject.toml', 'README.md'])
    
    metrics = validator.evaluate(mock_discoverer)
    
    # Precision = 1/2 (found pyproject.toml correctly, README.md is wrong)
    # Recall = 1/1 (found the one ground truth file)
    assert metrics['precision'] == 0.5
    assert metrics['recall'] == 1.0
    # FAILS - validator doesn't exist

# 🟢 GREEN: Implement metrics computation
# 🔵 REFACTOR: Add detailed reporting
```

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Machine Learning Models for Source Discovery
- **Why**: LLM-based approach is sufficient
- **Reconsider**: v0.7.0+ if LLM approach proves insufficient
- Don't over-engineer with custom ML when LLMs work

### ❌ Cross-File Dependency Analysis
- **Why**: Too complex for MVP
- **Reconsider**: Future version if simple approach misses dependencies
- Import analysis, call graphs, etc. are overkill

### ❌ User Feedback Loop for Refinement
- **Why**: Manual template refinement is sufficient
- **Reconsider**: v0.7.0+ after usage patterns emerge
- Learning from corrections adds complexity

### ❌ Multi-Repo Source Discovery
- **Why**: Single repo is MVP scope
- **Reconsider**: Future version for monorepo/microservices
- Keep it simple for now

---

## 🧪 Testing Requirements

### TDD Approach (Red-Green-Refactor)

**Day 1: Semantic Search**
- 🔴 Write semantic search tests
- 🟢 Implement file indexing
- 🟢 Implement keyword search
- 🔵 Refactor scoring algorithm
- ✅ Commit (tests green)

**Day 2: LLM Scoring**
- 🔴 Write LLM scoring tests (with mocks)
- 🟢 Implement LLM prompts
- 🟢 Implement response parsing
- 🔵 Refactor prompt engineering
- Test with real LLM on doc-evergreen README
- ✅ Commit (tests green)

**Day 3: Integration & Validation**
- 🔴 Write integration tests
- 🟢 Wire all components together
- 🟢 Implement accuracy validator
- Test on ground truth test cases
- 🔴 Run Day 5 checkpoint evaluation
- Generate accuracy report
- ✅ Final commit & sprint review

### Unit Tests (Write First)
- **Semantic search**:
  - File indexing works correctly
  - Keyword extraction from section content
  - Search returns relevant files
  - Scoring ranks files appropriately

- **LLM scoring**:
  - Prompt generation is correct
  - Response parsing handles JSON
  - Handles LLM failures gracefully
  - Caching works

- **Integration pipeline**:
  - All stages execute in order
  - Deduplication works
  - Top N filtering works
  - Results are properly formatted

### Integration Tests (After Unit Tests Pass)
- **End-to-end accuracy test**:
  - Run on doc-evergreen README
  - Measure precision, recall, F1
  - Verify 70-80% accuracy achieved

### Manual Testing (After Automated Tests Pass)
- [ ] Run on doc-evergreen README (full doc)
- [ ] Review discovered sources per section
- [ ] Manually verify relevance (are these the right files?)
- [ ] Compare to Sprint 1 naive discovery (is this better?)
- [ ] Test on secondary test case (different project)

**Test Coverage Target:** >80% for new code

---

## 📊 What You Learn

After Sprint 2, you'll discover:

1. **Accuracy achievability**
   - Can we hit 70-80% with this approach?
   - Which discovery method is most effective?
   - Where do we still fail?
   → **Validates v0.6.0 feasibility**

2. **LLM effectiveness for source scoring**
   - Does LLM understand code-to-doc relationships?
   - Is prompt engineering sufficient?
   - What's the cost (API calls)?

3. **Algorithm trade-offs**
   - Precision vs recall balance
   - Performance vs accuracy
   - Cost vs quality

4. **Test case quality**
   - Are ground truth test cases representative?
   - What sections are hardest to discover sources for?
   - What patterns emerge?

---

## ✅ Success Criteria (Day 5 Checkpoint)

### Must Have (Sprint Continues)
- ✅ Integrated discovery pipeline works end-to-end
- ✅ Accuracy on doc-evergreen README: **70-80% F1 score**
- ✅ LLM scoring provides meaningful relevance scores
- ✅ Top 3-5 sources per section are relevant
- ✅ Better than Sprint 1 naive discovery (quantifiable improvement)

### Acceptable (Sprint Continues with Adjustments)
- ⚠️ Accuracy 60-70% F1 score
- ⚠️ Some sections miss sources, but most are good
- **Action**: Adjust algorithm, extend sprint 1 day

### Red Flag (Pivot Required)
- ❌ Accuracy <60% F1 score
- ❌ LLM scoring doesn't improve over keyword search
- **Action**: Simplify approach, defer advanced discovery to v0.7.0, ship with naive discovery only

---

## 🛠️ Technical Approach

### Multi-Stage Filtering Strategy

**Why 3 stages?**
1. **Stage 1 (Pattern)**: Fast, high recall, low precision
   - Casts wide net
   - Minimal cost
   - Catches obvious cases

2. **Stage 2 (Semantic)**: Medium speed, balanced precision/recall
   - Narrows to relevant files
   - Content-based matching
   - No LLM cost yet

3. **Stage 3 (LLM)**: Slow, high precision, high recall
   - Final ranking and filtering
   - Semantic understanding
   - Expensive, so limit to top 10 candidates

**Result**: Best of all worlds - broad coverage + accurate ranking

### Key Decisions

**1. Use LLM for relevance, not discovery**
- LLM scores candidates, doesn't find them
- More cost-effective (fewer LLM calls)
- Leverages LLM's strength (understanding relevance)

**2. Limit LLM scoring to top 10 candidates**
- Controls API costs
- Semantic search narrows to relevant candidates first
- Good enough for 70-80% accuracy

**3. Cache aggressively**
- Same file + same section type → same score
- Reduces redundant LLM calls
- Improves performance

**4. Fail gracefully**
- If LLM fails, fall back to semantic search scores
- If semantic search fails, fall back to pattern matching
- Always return something useful

---

## 📅 Implementation Order

### Day 1: Semantic Search (Foundation)
- 🔴 Write file indexing tests
- 🟢 Implement file walker and indexer
- 🔴 Write keyword search tests
- 🟢 Implement search algorithm
- 🔵 Refactor scoring logic
- Test on doc-evergreen codebase
- ✅ Commit

### Day 2: LLM Scoring (Intelligence)
- 🔴 Write LLM scoring tests (mocked)
- 🟢 Implement prompt engineering
- 🟢 Implement response parsing
- 🔵 Refactor prompt for better results
- Test with real LLM calls
- Iterate on prompt quality
- ✅ Commit

### Day 3: Integration & Validation (Production)
- 🔴 Write integration tests
- 🟢 Wire all components
- 🔴 Write accuracy validation tests
- 🟢 Implement metrics computation
- Run Day 5 checkpoint evaluation
- Generate accuracy report
- **Decision point**: Proceed to Sprint 3 or adjust?
- ✅ Final commit & sprint review

---

## 🎯 Known Limitations (By Design)

1. **LLM costs scale with candidates**
   - Acceptable: Limit to top 10 candidates
   - Monitor costs during testing

2. **No cross-file dependency analysis**
   - Acceptable: Simple approach first
   - Future enhancement if needed

3. **Manual ground truth test cases**
   - Acceptable: Small set for validation
   - Expand in future versions

4. **No user feedback loop**
   - Acceptable: Manual refinement works
   - Future enhancement: learn from corrections

---

## 🔄 Next Sprint Preview

After Sprint 2 ships (assuming 70-80% accuracy achieved), the **most pressing need** will be:

**Intelligent prompt generation** - We have accurate sources, but placeholder prompts like "Document the {section}" aren't useful. Sprint 3 will:
- Analyze section content with LLM to understand intent
- Generate specific, actionable prompts
- Infer Divio quadrant from content
- Complete the full reverse template pipeline

Sprint 2 solves the hard problem (source discovery). Sprint 3 completes the feature (prompt generation + assembly).

---

**⚠️ Day 5 Checkpoint Reminder**: After Day 3 of Sprint 2, evaluate accuracy metrics and decide:
- ✅ **70-80%**: Proceed to Sprint 3
- ⚠️ **60-70%**: Adjust algorithm, extend 1 day
- ❌ **<60%**: Pivot to simpler approach

---

**Ready to tackle the hard part?** 🚀 This sprint makes or breaks the feature!
