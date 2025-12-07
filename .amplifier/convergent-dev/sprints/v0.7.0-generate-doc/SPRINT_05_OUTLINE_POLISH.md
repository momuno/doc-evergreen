# Sprint 5: Hierarchical Outline Generation - Polish ⭐

**Duration:** 2-3 days  
**Goal:** Achieve 80%+ outline quality with sophisticated prompt engineering  
**Value Delivered:** Production-ready outline generation that "barely needs editing"

---

## 🎯 Why This Sprint?

Sprint 4 proved the concept works (60-70% quality). Now we make it **excellent** (80%+ quality). This sprint is about:
1. **Sophisticated prompt engineering** - Better nesting-aware prompts
2. **Improved structure inference** - Smarter hierarchical decisions
3. **Better source mapping** - More accurate file-to-section alignment
4. **Quality validation** - Ensure outlines meet production standards

**The difference between Sprint 4 and 5:**
- Sprint 4: "It generates an outline" ✓
- Sprint 5: "The outline is so good I barely need to edit it" ⭐

This is where v0.7.0 delivers on its promise.

---

## 📦 Deliverables

### 1. Advanced Prompt Engineering System
**Estimated Lines:** ~300 lines + 200 lines tests

**What it does:**
- Doc-type-specific prompt templates (tutorial ≠ reference ≠ howto)
- Level-specific prompt patterns (intro vs. detailed vs. comprehensive)
- Context-aware prompt generation (uses source key_material)
- Quality-focused prompt instructions

**Why this sprint:**
- Prompts determine generation quality - worth focused attention
- Sprint 4 showed basic prompts work, now make them excellent
- Different doc types need different prompt styles

**Implementation notes:**
- Rich template library with proven patterns
- Use source reasoning to guide prompt specificity
- Include quality indicators in prompts (be specific, be clear, be actionable)

**Advanced prompt templates:**

```python
TUTORIAL_PROMPTS = {
    'intro': {
        'parent': """
        Write a welcoming introduction to {heading}.
        
        Your audience: Developers who are new to this tool.
        Your goal: Help them understand what they'll learn.
        
        Structure:
        - Brief overview (1-2 sentences) of what this section covers
        - Why this matters (motivation)
        - What they'll be able to do after this section
        
        Tone: Friendly, encouraging, clear.
        
        IMPORTANT: This section has {n} subsections:
        {subsection_list}
        Don't cover the details of these topics - just introduce them.
        """,
        
        'leaf': """
        Write step-by-step tutorial content for {heading}.
        
        Your audience: Developers following this tutorial in sequence.
        Your goal: Guide them through {topic} successfully.
        
        Required elements:
        1. Quick overview of what they'll do (1 sentence)
        2. Prerequisites/requirements (if any)
        3. Step-by-step instructions (numbered steps)
        4. Expected output/result after each key step
        5. Common pitfalls to avoid
        6. Success criteria (how they know it worked)
        
        Style:
        - Use second person ("you will...")
        - Be specific and actionable
        - Include code examples where relevant
        - Keep steps atomic (one action per step)
        
        Sources to reference:
        {source_guidance}
        """
    }
}

REFERENCE_PROMPTS = {
    'intro': {
        'parent': """
        Write a technical overview of {heading}.
        
        Your audience: Developers needing complete reference information.
        Your goal: Provide comprehensive understanding of this component.
        
        Structure:
        - Brief description of what this is
        - Key characteristics/properties
        - When/why to use it
        - Overview of capabilities (detailed docs in subsections)
        
        Tone: Technical, precise, thorough.
        
        This section has {n} subsections:
        {subsection_list}
        Keep this high-level - details are in subsections.
        """,
        
        'leaf': """
        Write complete reference documentation for {heading}.
        
        Your audience: Developers looking up specific details.
        Your goal: Provide all information needed to use {topic}.
        
        Required elements:
        1. Full description of functionality
        2. All parameters/arguments/options:
           - Name, type, description
           - Required vs. optional
           - Default values
        3. Return values/outputs
        4. Examples (minimal but complete)
        5. Edge cases and limitations
        6. Related components (if applicable)
        
        Style:
        - Be exhaustively complete
        - Use technical terminology precisely
        - Provide code examples
        - Cover all edge cases
        
        Sources to reference:
        {source_guidance}
        """
    }
}
```

### 2. Structure Quality Analyzer
**Estimated Lines:** ~220 lines + 180 lines tests

**What it does:**
- Analyzes generated outline structure for quality
- Checks: logical flow, appropriate depth, section balance
- Scores outline quality (0-100)
- Provides actionable improvement suggestions

**Why this sprint:**
- Need objective quality measurement (not just subjective "feels good")
- Enables iterative improvement
- Catches structural issues before user sees them

**Implementation notes:**
- Multiple quality dimensions (flow, balance, completeness)
- Compare against doc-type best practices
- Suggest specific improvements

**Quality dimensions:**

```python
class OutlineQualityAnalyzer:
    """Analyze and score outline quality."""
    
    def analyze(self, outline) -> QualityReport:
        scores = {
            'structure': self._score_structure(outline),
            'flow': self._score_logical_flow(outline),
            'balance': self._score_section_balance(outline),
            'prompts': self._score_prompt_quality(outline),
            'sources': self._score_source_mapping(outline),
            'completeness': self._score_completeness(outline)
        }
        
        overall = sum(scores.values()) / len(scores)
        
        suggestions = self._generate_suggestions(scores, outline)
        
        return QualityReport(
            overall_score=overall,
            dimension_scores=scores,
            suggestions=suggestions,
            meets_threshold=(overall >= 80)
        )
    
    def _score_structure(self, outline) -> float:
        """Score structural quality (0-100)."""
        issues = []
        
        # Check section count (not too many, not too few)
        section_count = len(outline['document']['sections'])
        if section_count < 2:
            issues.append("Too few top-level sections (need 2+)")
        elif section_count > 8:
            issues.append("Too many top-level sections (6 max recommended)")
        
        # Check nesting depth (not too shallow, not too deep)
        max_depth = self._calculate_max_depth(outline)
        if max_depth == 1:
            issues.append("No subsections - structure too flat")
        elif max_depth > 4:
            issues.append("Nesting too deep (3-4 levels max)")
        
        # Check subsection distribution
        sections_with_subsections = self._count_parent_sections(outline)
        if sections_with_subsections == 0:
            issues.append("No hierarchical structure")
        
        score = 100 - (len(issues) * 20)
        return max(0, score)
    
    def _score_prompt_quality(self, outline) -> float:
        """Score prompt quality (0-100)."""
        def score_prompt(section):
            prompt = section.get('prompt', '')
            score = 0
            
            # Length check (prompts should be substantial)
            if len(prompt) > 100:
                score += 30
            
            # Nesting awareness (parent prompts reference subsections)
            if section.get('sections'):
                if 'subsection' in prompt.lower() or "don't cover" in prompt.lower():
                    score += 30
            
            # Specificity (mentions sources or topics)
            if any(src['file'] in prompt for src in section.get('sources', [])):
                score += 20
            
            # Actionable (contains instructions)
            if any(word in prompt.lower() for word in ['write', 'explain', 'describe', 'provide']):
                score += 20
            
            return score
        
        all_prompts = self._collect_all_sections(outline)
        if not all_prompts:
            return 0
        
        prompt_scores = [score_prompt(s) for s in all_prompts]
        return sum(prompt_scores) / len(prompt_scores)
```

### 3. Source Mapping Optimizer
**Estimated Lines:** ~180 lines + 140 lines tests

**What it does:**
- Improves source-to-section mapping accuracy
- Uses source key_material more effectively
- Ensures critical sources aren't missed
- Prevents source over-assignment (same source to too many sections)

**Why this sprint:**
- Sprint 4 basic mapping may miss nuances
- Better mapping → better generation quality
- Source reasoning is valuable - use it well

**Implementation notes:**
- Semantic similarity between section topic and key_material
- Confidence scoring for mappings
- Balance between precision (correct sources) and recall (don't miss sources)

**Optimization strategies:**

```python
class SourceMappingOptimizer:
    """Optimize source-to-section mapping."""
    
    def optimize_mappings(self, outline, relevant_files):
        """Improve source mappings across all sections."""
        
        # Phase 1: Ensure critical sources are mapped
        critical_sources = self._identify_critical_sources(relevant_files)
        self._ensure_critical_sources_mapped(outline, critical_sources)
        
        # Phase 2: Improve mapping quality
        for section in self._all_sections(outline):
            current_sources = section.get('sources', [])
            
            # Score current mapping quality
            quality = self._score_mapping_quality(section, current_sources, relevant_files)
            
            if quality < 0.7:  # Threshold for improvement
                # Re-map with better algorithm
                improved_sources = self._remap_section(section, relevant_files)
                section['sources'] = improved_sources
        
        # Phase 3: Validate no critical gaps
        self._validate_coverage(outline, relevant_files)
        
        return outline
    
    def _identify_critical_sources(self, relevant_files):
        """Identify must-map sources (very high relevance)."""
        return [
            f for f in relevant_files 
            if f['score'] >= 85  # Very high relevance
        ]
    
    def _score_mapping_quality(self, section, sources, available_sources):
        """Score how well sources match section topic."""
        if not sources:
            return 0.0
        
        scores = []
        for source in sources:
            # Semantic match between section heading and source key_material
            heading_tokens = self._tokenize(section['heading'])
            material_tokens = self._tokenize(source.get('key_material', ''))
            
            # Simple overlap score (could use embeddings for better accuracy)
            overlap = len(set(heading_tokens) & set(material_tokens))
            total = len(set(heading_tokens) | set(material_tokens))
            
            similarity = overlap / total if total > 0 else 0
            scores.append(similarity)
        
        return sum(scores) / len(scores)
```

### 4. Iterative Outline Refinement
**Estimated Lines:** ~200 lines + 150 lines tests

**What it does:**
- Generate outline → analyze quality → refine → repeat
- Iterates until quality threshold met (80%+) or max iterations
- Focuses refinement on low-scoring dimensions

**Why this sprint:**
- Single-pass generation may not reach 80%+ quality
- Iterative refinement improves results significantly
- Targets improvements where needed most

**Implementation notes:**
- Max 3 iterations (avoid infinite loops)
- Each iteration targets specific quality issues
- Stop early if quality threshold met

**Refinement algorithm:**

```python
class OutlineRefiner:
    """Iteratively refine outline quality."""
    
    MAX_ITERATIONS = 3
    QUALITY_THRESHOLD = 80
    
    def refine_outline(self, initial_outline, context, relevant_files):
        """Refine outline until quality threshold met."""
        
        outline = initial_outline
        analyzer = OutlineQualityAnalyzer()
        
        for iteration in range(self.MAX_ITERATIONS):
            # Analyze quality
            quality_report = analyzer.analyze(outline)
            
            print(f"🔍 Iteration {iteration + 1}: Quality score = {quality_report.overall_score:.1f}%")
            
            # Check if threshold met
            if quality_report.meets_threshold:
                print(f"✅ Quality threshold met ({self.QUALITY_THRESHOLD}%+)")
                break
            
            # Identify lowest-scoring dimension
            lowest_dimension = min(
                quality_report.dimension_scores.items(),
                key=lambda x: x[1]
            )
            
            print(f"   Improving: {lowest_dimension[0]} (score: {lowest_dimension[1]:.1f}%)")
            
            # Apply targeted refinement
            if lowest_dimension[0] == 'structure':
                outline = self._refine_structure(outline, context)
            elif lowest_dimension[0] == 'prompts':
                outline = self._refine_prompts(outline, context)
            elif lowest_dimension[0] == 'sources':
                outline = self._refine_sources(outline, relevant_files)
            # ... other dimensions
        
        final_quality = analyzer.analyze(outline)
        print(f"📊 Final quality: {final_quality.overall_score:.1f}%")
        
        return outline, final_quality
    
    def _refine_structure(self, outline, context):
        """Improve structural quality."""
        # Identify structural issues
        # - Too many/few sections → adjust
        # - Too flat → add subsections
        # - Too deep → flatten
        
        # Use LLM to restructure
        prompt = f"""
        Improve the structure of this outline.
        Issues identified: {self._describe_structural_issues(outline)}
        
        Current outline:
        {self._format_outline(outline)}
        
        Provide improved structure (JSON format, same schema).
        """
        
        improved = self.llm.generate(prompt)
        return json.loads(improved)
```

---

## 🧪 Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all features:

#### 1. 🔴 RED - Write Failing Tests First

**Quality Analyzer Tests:**
```python
def test_detects_high_quality_outline():
    # Test that good outline scores high
    good_outline = load_test_outline('high_quality.json')
    
    analyzer = OutlineQualityAnalyzer()
    report = analyzer.analyze(good_outline)
    
    assert report.overall_score >= 80
    assert report.meets_threshold

def test_detects_structural_issues():
    # Test that structural problems are identified
    flat_outline = load_test_outline('too_flat.json')
    
    report = analyzer.analyze(flat_outline)
    
    assert report.dimension_scores['structure'] < 70
    assert any('flat' in s.lower() for s in report.suggestions)

def test_detects_prompt_quality_issues():
    # Test that poor prompts are identified
    weak_prompts_outline = load_test_outline('weak_prompts.json')
    
    report = analyzer.analyze(weak_prompts_outline)
    
    assert report.dimension_scores['prompts'] < 70
```

**Refinement Tests:**
```python
def test_refinement_improves_quality():
    # Test that refinement increases quality score
    initial_outline = load_test_outline('medium_quality.json')
    
    refiner = OutlineRefiner()
    refined, quality = refiner.refine_outline(initial_outline, context, files)
    
    initial_quality = analyzer.analyze(initial_outline).overall_score
    assert quality.overall_score > initial_quality

def test_refinement_stops_at_threshold():
    # Test that refinement stops when quality is good enough
    good_outline = load_test_outline('high_quality.json')
    
    refiner = OutlineRefiner()
    refined, quality = refiner.refine_outline(good_outline, context, files)
    
    # Should stop immediately (already good)
    assert refined == good_outline
```

Run tests → Watch them fail → Good!

#### 2. 🟢 GREEN - Write Minimal Implementation

```python
# Implement quality analyzer, refinement loop, etc.
# (See detailed implementations in Deliverables section)
```

Run tests → Watch them pass → Good!

#### 3. 🔵 REFACTOR - Improve Code Quality

- Extract quality scoring functions
- Optimize LLM calls (cache, batch)
- Improve suggestion generation
- Add comprehensive logging

Run tests → Still pass → Good!

### Unit Tests (Write First)

- **Quality scoring**: Each dimension independently, edge cases
- **Structure analysis**: Various outline shapes, depth issues
- **Prompt quality**: Different prompt styles, nesting awareness
- **Source mapping**: Accuracy, coverage, over-assignment
- **Refinement**: Iteration logic, early stopping, targeted improvements

### Integration Tests (Write First)

- **End-to-end polish**: Medium-quality outline → 80%+ quality
- **Real test cases**: doc-evergreen, Python project, API project
- **Quality regression**: Ensure refinement doesn't degrade quality

### Manual Testing (After Automated Tests Pass)

- [ ] Generate outline for doc-evergreen tutorial - verify 80%+ quality
- [ ] Compare Sprint 4 vs Sprint 5 output - verify significant improvement
- [ ] Check all prompts - verify nesting awareness and quality
- [ ] Validate source mappings - verify accuracy and completeness
- [ ] Test with all doc types - verify type-appropriate structures

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Machine Learning for Structure Prediction
- **Why**: LLM-based approach is working, ML requires training data
- **Reconsider**: v0.8.0 if LLM quality plateaus

### ❌ User Preference Learning
- **Why**: No user feedback data yet, premature
- **Reconsider**: v0.8.0 after gathering usage patterns

### ❌ Multi-Model Ensemble
- **Why**: Single GPT-4 model is sufficient for MVP
- **Examples**: Combine GPT-4 + Claude for better results
- **Reconsider**: v0.8.0 if quality needs boost

### ❌ Outline Templates Library
- **Why**: Generate fresh for each case, simpler
- **Reconsider**: v0.8.0 for common patterns

### ❌ Advanced Quality Metrics
- **Why**: Basic quality dimensions are sufficient
- **Examples**: Readability scores, information density
- **Reconsider**: v0.8.0 if users request

---

## 📋 Dependencies

### Requires from previous sprints:
- **Sprint 4**: Working outline generator (60-70% quality baseline)
- **Sprint 3**: relevance_notes.json (source key_material is critical)
- **Sprint 1**: context.json (doc_type guides refinement)

### Provides for future sprints:
- **80%+ quality outline** for Sprint 6 (document generation)
- **Quality analyzer** for Sprint 7 (validation before user review)
- **Refinement patterns** for future improvements

---

## ✅ Acceptance Criteria

### Must Have

- ✅ **80%+ quality outlines**: Achieves target on test cases
- ✅ **Quality analyzer works**: Accurate scoring across dimensions
- ✅ **Iterative refinement works**: Improves quality with each iteration
- ✅ **Advanced prompts**: Doc-type and level-specific prompts
- ✅ **Improved source mapping**: Higher accuracy than Sprint 4
- ✅ **Tests pass**: >80% coverage, all tests green

### Quality Targets (Sprint 5)

- **Overall quality**: 80%+ (human review: "barely needs editing")
- **Structure score**: 85%+ (logical flow, appropriate depth)
- **Prompt score**: 80%+ (nesting-aware, actionable, specific)
- **Source mapping**: 80%+ (relevant sources correctly mapped)
- **Consistency**: 80%+ quality across different doc types

### Success Validation

**Manual review checklist** (for 3 test cases):
1. doc-evergreen tutorial
2. Python CLI library reference
3. Web API howto guide

For each:
- [ ] Structure makes sense for doc type
- [ ] Prompts are specific and actionable
- [ ] Parent prompts clearly avoid subsection content
- [ ] Sources mapped correctly with good reasoning
- [ ] "I would barely edit this outline before generating" ✓

---

## 🛠️ Technical Approach

### Key Decisions

**Decision 1: Iterative refinement (not single-pass)**
- **Rationale**: 80%+ quality is hard to achieve in one shot
- **Alternative considered**: Perfect first-time generation (unrealistic)
- **Why iterative**: Proven pattern, manageable complexity

**Decision 2: Multi-dimensional quality scoring**
- **Rationale**: Quality is multi-faceted, need granular feedback
- **Alternative considered**: Single overall score (less actionable)
- **Why multi-dimensional**: Enables targeted improvements

**Decision 3: Doc-type-specific prompt templates**
- **Rationale**: Tutorial ≠ reference in structure and style
- **Alternative considered**: Generic prompts (lower quality)
- **Why doc-type-specific**: Matches user expectations, higher quality

**Decision 4: Max 3 refinement iterations**
- **Rationale**: Balance quality improvement vs. time/cost
- **Alternative considered**: Unlimited iterations (expensive, slow)
- **Why 3**: Empirically sufficient, prevents infinite loops

### Quality Threshold Philosophy

**Why 80%+:**
- High enough to feel "intelligent" and "barely needs editing"
- Achievable within sprint timeframe
- Leaves room for user customization (not over-fitting)
- Matches convergence success criteria

**Not 95%+:**
- Diminishing returns (80→95 takes 3x effort)
- User preferences vary (one person's perfect is another's preference)
- Enables user agency (they can edit/improve)

---

## 🔍 What You Learn

After this sprint, you'll discover:

1. **Quality ceiling**: Can we consistently hit 80%+ with current approach?
   - → Validates v0.7.0 success OR signals need for alternative strategies
   
2. **Refinement effectiveness**: How much does iteration improve quality?
   - → Informs cost/benefit of refinement in future versions
   
3. **Doc-type patterns**: What structures work best for each doc type?
   - → Could inform template library in v0.8.0
   
4. **Quality dimensions**: Which quality aspects matter most to users?
   - → Prioritizes future quality improvements

---

## 📊 Success Metrics

### Quantitative (Sprint 5 Targets)
- **Overall quality**: 80%+ across test cases
- **Structure**: 85%+ (logical, appropriate depth)
- **Prompts**: 80%+ (nesting-aware, actionable)
- **Sources**: 80%+ (relevant, accurate reasoning)
- **Refinement improvement**: +20-30% per iteration
- **Convergence**: 80%+ achieved within 3 iterations

### Qualitative
- "The outline is so good I barely need to edit it" ✓
- Structure feels appropriate for doc type ✓
- Prompts are specific and useful ✓
- Source mappings make sense ✓
- Ready for production use ✓

### Validation Method
**A/B comparison**: Sprint 4 vs Sprint 5 outlines
- Same test cases (doc-evergreen, Python lib, API)
- Blind review: which is better?
- **Target**: Sprint 5 preferred in 80%+ of comparisons

---

## 📅 Implementation Order

### TDD-driven workflow (2-3 days)

**Day 1 (Morning): Quality Analyzer**
- 🔴 Write failing tests for quality scoring
- 🟢 Implement multi-dimensional quality analyzer
- 🔵 Refactor: Optimize scoring, improve suggestions
- ✅ Commit: "feat: add outline quality analyzer"

**Day 1 (Afternoon): Advanced Prompt Templates**
- 🔴 Write failing tests for doc-type-specific prompts
- 🟢 Implement rich prompt template library
- 🔵 Refactor: Extract templates, add context awareness
- ✅ Commit: "feat: add advanced prompt templates"

**Day 2 (Morning): Source Mapping Optimizer**
- 🔴 Write failing tests for improved mapping
- 🟢 Implement semantic matching and optimization
- 🔵 Refactor: Improve accuracy, add confidence scoring
- ✅ Commit: "feat: optimize source mapping"

**Day 2 (Afternoon): Iterative Refinement**
- 🔴 Write failing tests for refinement loop
- 🟢 Implement iterative refinement with quality targeting
- 🔵 Refactor: Optimize iterations, improve stopping criteria
- ✅ Commit: "feat: add iterative outline refinement"

**Day 3: Integration, Testing & Validation**
- ✅ Run on all test cases (doc-evergreen, library, API)
- ✅ Compare Sprint 4 vs Sprint 5 quality
- ✅ Manual quality review
- ✅ Fix any quality issues
- ✅ Sprint review: Demo 80%+ quality outlines

**Note:** Each feature follows multiple red-green-refactor micro-cycles

---

## ⚠️ Known Limitations (By Design - Sprint 5)

1. **Max 3 iterations** - May not reach 80% in rare cases
   - Why acceptable: 3 iterations sufficient for 90%+ of cases
   
2. **Quality scoring is heuristic** - Not perfect measurement
   - Why acceptable: Good enough proxy, validated by manual review
   
3. **Doc-type templates are static** - Not adaptive
   - Why acceptable: Proven patterns work, user can edit outline
   
4. **LLM cost increases** - Iterative refinement = more API calls
   - Why acceptable: One-time cost, quality is worth it

---

## 🎯 Next Sprint Preview

After this sprint ships, the most pressing need will be:

**Sprint 6: Nesting-Aware Document Generation** - Now that we have excellent outlines (80%+ quality), we need to generate actual documentation content from them. Sprint 6 will implement the top-down DFS content generation with three-component LLM context (prompt + relevancy summaries + full sources), respecting the locked outline structure.

The 80%+ quality outline from Sprint 5 ensures Sprint 6's generation has a solid foundation - "garbage in, garbage out" avoided!
