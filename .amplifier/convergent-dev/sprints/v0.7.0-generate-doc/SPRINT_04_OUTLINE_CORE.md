# Sprint 4: Hierarchical Outline Generation - Core ⭐

**Duration:** 2-3 days  
**Goal:** Generate nested outline with nesting-aware prompts  
**Value Delivered:** THE CORE INNOVATION - intelligent structure generation (basic)

---

## 🎯 Why This Sprint?

This is **THE DEFINING FEATURE** of v0.7.0! After gathering intent (Sprint 1), indexing files (Sprint 2), and identifying relevant files (Sprint 3), we now tackle the hardest problem: **How do you generate intelligent hierarchical documentation structure from scratch?**

This sprint focuses on getting the CORE WORKING:
1. Generate nested section structure (H1-H6)
2. Create nesting-aware prompts (parents vs. children)
3. Map sources to sections with reasoning
4. Produce valid outline.json

Sprint 5 will polish this to 80%+ quality. Sprint 4 is about proving the concept works.

---

## 🌟 THE CORE INNOVATION

**What makes this hard:**
- Must understand doc type implications (tutorial vs. reference structure)
- Must infer logical hierarchy from flat file list
- Must create prompts that don't duplicate across nesting levels
- Must map sources to sections based on relevance notes

**What makes this innovative:**
- **Nesting-aware prompts**: Parent sections say "don't cover X, that's in subsection Y"
- **Source reasoning**: Not just which files, but WHY this file for this section
- **Doc-type awareness**: Tutorial structure ≠ reference structure
- **Hierarchical intelligence**: Knows when to create subsections vs. flat sections

**Example innovation:**

```json
{
  "heading": "# Getting Started",
  "level": 1,
  "prompt": "Write welcoming intro (2-3 paragraphs) explaining what this tool does. Don't cover installation or usage - those are in subsections below.",
  "sources": [
    {
      "file": "README.md",
      "reasoning": "Contains project description and value proposition"
    }
  ],
  "sections": [
    {
      "heading": "## Installation",
      "level": 2,
      "prompt": "Step-by-step installation instructions. Include prerequisites and verification.",
      "sources": [{"file": "pyproject.toml", "reasoning": "Defines dependencies"}]
    }
  ]
}
```

**Notice:**
- Parent prompt explicitly excludes subsection content
- Each section has source reasoning (not just file names)
- Nesting level is explicit (1 vs. 2)
- Structure determines what LLM will generate

---

## 📦 Deliverables

### 1. Outline Structure Generator
**Estimated Lines:** ~300 lines + 200 lines tests

**What it does:**
- Reads context.json (doc_type, purpose)
- Reads relevance_notes.json (relevant files with reasoning)
- Generates hierarchical section structure using LLM
- Produces nested JSON outline

**Why this sprint:**
- Core of the feature - everything leads to this
- Most complex component - needs focused attention
- Enables end-to-end workflow

**Implementation notes:**
- Use iterative refinement (generate → validate → adjust)
- Start with top-level sections, then recurse for subsections
- Validate structure makes sense before returning
- Use GPT-4 (needs reasoning capability)

**Generation algorithm:**
```python
def generate_outline(context, relevant_files):
    """Generate hierarchical outline."""
    # Phase 1: Determine top-level sections
    top_level_sections = llm_generate_sections(
        doc_type=context['doc_type'],
        purpose=context['purpose'],
        available_sources=relevant_files,
        level=1
    )
    
    # Phase 2: For each top-level section, generate subsections
    for section in top_level_sections:
        section['sections'] = generate_subsections(
            parent_section=section,
            available_sources=relevant_files,
            max_depth=3  # Limit nesting for MVP
        )
    
    return {
        '_meta': {...},
        'document': {
            'title': infer_title(context),
            'output': context['output_path'],
            'sections': top_level_sections
        }
    }

def generate_subsections(parent, available_sources, max_depth):
    """Recursively generate subsections."""
    if parent['level'] >= max_depth:
        return []  # Stop at max depth
    
    # Ask LLM: "Does this section need subsections?"
    needs_subsections = llm_should_have_subsections(parent)
    
    if not needs_subsections:
        return []
    
    # Generate subsections
    subsections = llm_generate_sections(
        parent_section=parent,
        available_sources=available_sources,
        level=parent['level'] + 1
    )
    
    # Recurse
    for subsection in subsections:
        subsection['sections'] = generate_subsections(
            subsection, available_sources, max_depth
        )
    
    return subsections
```

### 2. Nesting-Aware Prompt Generator
**Estimated Lines:** ~250 lines + 180 lines tests

**What it does:**
- Generates prompts that are aware of nesting context
- Parent prompts: "Introduce topic, don't cover details in subsections"
- Child prompts: "Cover specific details for this aspect"
- Leaf prompts: "Comprehensive coverage of this specific topic"

**Why this sprint:**
- Prevents content duplication across nesting levels
- Key to quality - prompts determine what LLM generates
- Doc-type-specific prompt styles

**Implementation notes:**
- Different prompt templates for doc types
- Include subsection awareness in prompts
- Use relevance notes (key_material) to guide prompt specificity

**Prompt generation by level:**

```python
def generate_prompt(section_heading, level, has_subsections, doc_type, sources):
    """Generate nesting-aware prompt."""
    
    if has_subsections:
        # Parent section - introduce without details
        if doc_type == 'tutorial':
            template = """
            Write a brief introduction (1-2 paragraphs) to {heading}.
            Explain what the reader will learn in this section.
            
            IMPORTANT: This section has {n} subsections that will cover:
            {subsection_list}
            
            Don't cover those details here - just introduce the topic.
            """
        elif doc_type == 'reference':
            template = """
            Write a brief overview of {heading}.
            Explain what this component does and its role.
            
            Details are in subsections below:
            {subsection_list}
            
            Keep this high-level.
            """
    else:
        # Leaf section - comprehensive content
        if doc_type == 'tutorial':
            template = """
            Write step-by-step instructions for {heading}.
            Be specific and actionable. Include:
            - Clear steps the reader should follow
            - Expected outcomes
            - Common pitfalls to avoid
            
            Use sources: {source_guidance}
            """
        elif doc_type == 'reference':
            template = """
            Write complete reference documentation for {heading}.
            Be thorough and precise. Include:
            - All parameters/options
            - Return values/outputs
            - Example usage
            
            Use sources: {source_guidance}
            """
    
    return template.format(...)
```

### 3. Section-Source Mapper
**Estimated Lines:** ~220 lines + 160 lines tests

**What it does:**
- Maps relevant files to appropriate sections
- Uses relevance notes (key_material) to determine fit
- Generates reasoning for why source maps to section
- Handles sources used by multiple sections

**Why this sprint:**
- LLM needs to know WHICH sources to use for WHICH section
- Reasoning guides LLM attention during generation
- Prevents random source selection

**Implementation notes:**
- Use semantic matching between section topic and key_material
- Allow sources to map to multiple sections
- Prioritize most relevant sources per section (top 3-5)

**Mapping algorithm:**
```python
def map_sources_to_section(section_heading, section_level, relevant_files):
    """Map relevant sources to this section."""
    
    # Build prompt
    prompt = f"""
    Documentation section: {section_heading}
    Level: {section_level}
    
    Available sources:
    {format_available_sources(relevant_files)}
    
    Which sources should be used for this section?
    For each source, explain WHY it's relevant to this specific section.
    
    Respond with JSON:
    [
      {{"file": "src/cli.py", "reasoning": "Contains command definitions..."}},
      ...
    ]
    
    Only include sources directly relevant to this section (not just generally useful).
    Limit to 3-5 most relevant sources.
    """
    
    # LLM selects sources
    response = llm.generate(prompt)
    source_mappings = json.loads(response)
    
    return source_mappings
```

### 4. Outline Validator
**Estimated Lines:** ~150 lines + 120 lines tests

**What it does:**
- Validates generated outline structure
- Checks: valid nesting levels, prompts exist, sources mapped
- Ensures outline is processable by Sprint 6
- Provides helpful error messages

**Why this sprint:**
- Catch issues before saving outline.json
- Prevents Sprint 6 failures due to malformed outline
- Quality gate

**Implementation notes:**
- Schema validation (required fields present)
- Structural validation (nesting makes sense)
- Content validation (prompts are useful)

**Validation rules:**
```python
def validate_outline(outline):
    """Validate outline structure."""
    errors = []
    
    # Required fields in _meta
    if 'doc_type' not in outline['_meta']:
        errors.append("Missing doc_type in _meta")
    
    # Validate each section recursively
    def validate_section(section, parent_level=0):
        # Level increments properly
        if section['level'] != parent_level + 1:
            errors.append(f"Section {section['heading']}: invalid level")
        
        # Has prompt
        if not section.get('prompt'):
            errors.append(f"Section {section['heading']}: missing prompt")
        
        # Has sources (or is parent with subsections)
        if not section['sources'] and not section['sections']:
            errors.append(f"Section {section['heading']}: no sources or subsections")
        
        # Validate subsections
        for subsection in section.get('sections', []):
            validate_section(subsection, section['level'])
    
    for section in outline['document']['sections']:
        validate_section(section)
    
    return errors
```

---

## 🧪 Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all features:

#### 1. 🔴 RED - Write Failing Tests First

**Outline Generator Tests:**
```python
def test_generates_top_level_sections():
    # Test that top-level structure is generated
    context = {'doc_type': 'tutorial', 'purpose': 'Get started quickly'}
    relevant_files = load_test_relevance_notes()
    
    generator = OutlineGenerator()
    outline = generator.generate(context, relevant_files)
    
    assert len(outline['document']['sections']) >= 2
    assert all(s['level'] == 1 for s in outline['document']['sections'])

def test_generates_subsections():
    # Test that subsections are created when appropriate
    outline = generator.generate(context, relevant_files)
    
    # At least one section should have subsections
    has_subsections = any(
        len(s['sections']) > 0 
        for s in outline['document']['sections']
    )
    assert has_subsections

def test_limits_nesting_depth():
    # Test that nesting doesn't go too deep
    outline = generator.generate(context, relevant_files)
    
    max_depth = find_max_depth(outline['document']['sections'])
    assert max_depth <= 4  # H1 -> H2 -> H3 -> H4
```

**Prompt Generator Tests:**
```python
def test_parent_prompt_excludes_subsections():
    # Test that parent prompts don't cover subsection content
    prompt = generate_prompt(
        heading="Getting Started",
        level=1,
        has_subsections=True,
        subsections=["Installation", "First Command"],
        doc_type='tutorial'
    )
    
    assert "don't cover" in prompt.lower() or "subsection" in prompt.lower()
    assert "Installation" in prompt or "First Command" in prompt

def test_leaf_prompt_is_comprehensive():
    # Test that leaf prompts are detailed
    prompt = generate_prompt(
        heading="Installation",
        level=2,
        has_subsections=False,
        doc_type='tutorial'
    )
    
    assert "step-by-step" in prompt.lower() or "detailed" in prompt.lower()
    assert len(prompt) > 100  # Substantial prompt
```

**Source Mapper Tests:**
```python
def test_maps_relevant_sources_to_section():
    # Test that appropriate sources are mapped
    section = {"heading": "## Installation", "level": 2}
    relevant_files = load_test_relevance_notes()
    
    mapper = SourceMapper()
    sources = mapper.map_sources(section, relevant_files)
    
    # Should include pyproject.toml or similar
    assert any('pyproject.toml' in s['file'] or 'setup.py' in s['file'] 
               for s in sources)

def test_provides_reasoning_for_sources():
    # Test that reasoning is provided
    sources = mapper.map_sources(section, relevant_files)
    
    for source in sources:
        assert 'reasoning' in source
        assert len(source['reasoning']) > 20
```

Run tests → Watch them fail → Good!

#### 2. 🟢 GREEN - Write Minimal Implementation

```python
class OutlineGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.max_depth = 3
    
    def generate(self, context, relevant_files):
        """Generate hierarchical outline."""
        # Generate top-level sections
        top_sections = self._generate_sections(
            doc_type=context['doc_type'],
            purpose=context['purpose'],
            relevant_files=relevant_files,
            level=1
        )
        
        # Generate subsections recursively
        for section in top_sections:
            section['sections'] = self._generate_subsections(
                section, relevant_files, current_depth=1
            )
        
        # Assemble outline
        outline = {
            '_meta': {
                'generation_method': 'forward',
                'doc_type': context['doc_type'],
                'user_intent': context['purpose']
            },
            'document': {
                'title': self._infer_title(context),
                'output': context['output_path'],
                'sections': top_sections
            }
        }
        
        # Validate
        validator = OutlineValidator()
        errors = validator.validate(outline)
        if errors:
            raise ValueError(f"Invalid outline: {errors}")
        
        return outline
    
    def _generate_sections(self, doc_type, purpose, relevant_files, level, parent=None):
        """Generate sections at a given level."""
        prompt = f"""
        Generate section structure for {doc_type} documentation.
        Purpose: {purpose}
        Level: H{level}
        {f'Parent section: {parent["heading"]}' if parent else 'Top level'}
        
        Available sources:
        {self._format_sources(relevant_files)}
        
        Respond with JSON array of sections:
        [{{"heading": "# Title", "level": {level}, "topic": "what this covers"}}]
        """
        
        response = self.llm.generate(prompt)
        sections = json.loads(response)
        
        # Generate prompts and map sources
        for section in sections:
            section['prompt'] = self._generate_prompt(section, doc_type, parent)
            section['sources'] = self._map_sources(section, relevant_files)
            section['sections'] = []  # Will be filled by recursion
        
        return sections
```

Run tests → Watch them pass → Good!

#### 3. 🔵 REFACTOR - Improve Code Quality

- Extract prompt templates to separate file
- Add caching for repeated LLM calls
- Improve error handling
- Add logging for debugging
- Optimize source mapping

Run tests → Still pass → Good!

### Unit Tests (Write First)

- **Structure generation**: Top-level, nested, depth limits
- **Prompt generation**: Parent vs. leaf, doc-type-aware, nesting-aware
- **Source mapping**: Relevance matching, reasoning quality
- **Validation**: Schema, structure, content quality

### Integration Tests (Write First)

- **End-to-end outline generation**: context.json + relevance_notes.json → outline.json
- **Real test cases**: doc-evergreen repo, simple Python project, web API
- **Edge cases**: No relevant sources, all sources equally relevant

### Manual Testing (After Automated Tests Pass)

- [ ] Generate outline for doc-evergreen tutorial - verify structure makes sense
- [ ] Check prompts - verify nesting awareness (parents don't duplicate children)
- [ ] Check source mappings - verify reasoning quality
- [ ] Validate outline.json - verify human-readable and editable
- [ ] Test with different doc types - verify structure differences

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ 80%+ Quality Target
- **Why**: Sprint 4 focuses on "working", Sprint 5 focuses on "excellent"
- **Target for Sprint 4**: 60-70% quality (proves concept)
- **Reconsider**: Sprint 5 will polish to 80%+

### ❌ Advanced Nesting Strategies
- **Why**: Start with simple recursive approach, optimize later
- **Examples**: Bottom-up generation, parallel section generation
- **Reconsider**: Sprint 5 if quality is insufficient

### ❌ Outline Learning/Improvement
- **Why**: Static generation for MVP, learning requires feedback data
- **Reconsider**: v0.8.0 after gathering user feedback

### ❌ Multi-Document Outlines
- **Why**: Single doc for v0.7.0, adds complexity
- **Reconsider**: v0.8.0 if users request

### ❌ Template Reuse
- **Why**: Generate fresh for each run, simpler
- **Examples**: Reuse outline from similar doc, learn from previous generations
- **Reconsider**: v0.8.0 for efficiency

### ❌ Interactive Outline Refinement During Generation
- **Why**: Sprint 7 handles review workflow, keep generation separate
- **Reconsider**: Sprint 7 implementation

---

## 📋 Dependencies

### Requires from previous sprints:
- **Sprint 1**: context.json with doc_type and purpose
- **Sprint 3**: relevance_notes.json with filtered relevant files

### Provides for future sprints:
- **outline.json** for Sprint 5 (polish and improve quality)
- **Outline structure** for Sprint 6 (document generation)
- **Working prototype** for Sprint 5 (baseline to improve upon)

---

## ✅ Acceptance Criteria

### Must Have

- ✅ **Generates nested outline**: At least 2 levels of nesting
- ✅ **Nesting-aware prompts**: Parents reference subsections
- ✅ **Source mapping**: Each section has relevant sources with reasoning
- ✅ **Valid structure**: Passes validation, processable by Sprint 6
- ✅ **outline.json created**: All required fields present
- ✅ **Context update**: context.json status updated to "outlined"
- ✅ **Tests pass**: >80% coverage, all tests green

### Quality Targets (Sprint 4)

- **Outline quality**: 60-70% (proves concept, needs polish)
- **Structure appropriateness**: Sections feel reasonable for doc type
- **Prompt quality**: Prompts are useful (even if not perfect)
- **Source mapping accuracy**: 70%+ sources are relevant to sections

### Nice to Have (Defer to Sprint 5)

- ❌ **80%+ outline quality**: Polish in Sprint 5
- ❌ **Sophisticated nesting**: Basic nesting first, optimize in Sprint 5
- ❌ **Perfect prompts**: Good enough prompts now, excellent in Sprint 5

---

## 🛠️ Technical Approach

### Key Decisions

**Decision 1: Recursive generation (top-down)**
- **Rationale**: Natural way to think about hierarchy, easier to implement
- **Alternative considered**: Bottom-up (generate leaves first, group into parents)
- **Why top-down**: Simpler for MVP, can optimize later

**Decision 2: GPT-4 for outline generation**
- **Rationale**: Needs sophisticated reasoning for structure inference
- **Alternative considered**: GPT-3.5 (cheaper but less capable)
- **Why GPT-4**: Quality is critical for core innovation, worth the cost

**Decision 3: Separate prompt generation step**
- **Rationale**: Clearer separation of concerns, easier to test
- **Alternative considered**: Generate structure and prompts together
- **Why separate**: More modular, easier to improve prompts independently

**Decision 4: Max depth of 3-4 levels**
- **Rationale**: Deeper nesting is rare, adds complexity
- **Alternative considered**: Unlimited depth
- **Why limit**: Simpler for MVP, 99% of docs don't need >4 levels

### LLM Configuration

```python
# Outline generation uses GPT-4 for quality
OUTLINE_LLM_CONFIG = {
    'model': 'gpt-4',
    'temperature': 0.7,  # Some creativity for structure
    'max_tokens': 2000,  # Complex reasoning requires space
}
```

### Critical Prompt Engineering

**Structure generation prompt:**
```
You are generating a {doc_type} documentation outline.

Purpose: {purpose}

Available sources (with relevance notes):
{formatted_relevant_files}

Generate top-level sections (H1) for this documentation.

Guidelines for {doc_type}:
- Tutorial: Learning-oriented, step-by-step progression
- Howto: Goal-oriented, solve specific problems
- Reference: Information-oriented, comprehensive coverage
- Explanation: Understanding-oriented, conceptual depth

Respond with JSON array:
[
  {
    "heading": "# Section Title",
    "level": 1,
    "topic": "Brief description of what this section covers",
    "should_have_subsections": true/false
  }
]

Generate 3-6 top-level sections.
```

---

## 🔍 What You Learn

After this sprint, you'll discover:

1. **Structure generation feasibility**: Can LLM generate reasonable hierarchical structure?
   - → Validates approach OR signals need for alternative strategy in Sprint 5
   
2. **Prompt quality baseline**: How good are auto-generated prompts?
   - → Informs Sprint 5 improvements
   
3. **Source mapping accuracy**: Do sources map sensibly to sections?
   - → Validates relevance notes from Sprint 3
   
4. **Quality gaps**: Where does outline fall short of expectations?
   - → Targeted improvements for Sprint 5

---

## 📊 Success Metrics

### Quantitative (Sprint 4 Targets)
- **Outline quality**: 60-70% (human review: "reasonable but needs work")
- **Structure validity**: 100% (valid JSON, passes validation)
- **Prompt nesting-awareness**: 70%+ (prompts reference subsections)
- **Source mapping relevance**: 70%+ (sources make sense for section)

### Qualitative
- Structure feels appropriate for doc type
- Prompts are useful (even if could be better)
- Source reasoning makes sense
- Outline is human-readable and editable

### Validation Method
**Manual review checklist** (for doc-evergreen tutorial outline):
- [ ] Does structure make sense? (intro, install, usage, etc.)
- [ ] Do parent prompts avoid duplicating subsections?
- [ ] Are sources mapped appropriately? (install section → pyproject.toml)
- [ ] Is reasoning clear and helpful?
- [ ] Could I edit this outline and use it?

---

## 📅 Implementation Order

### TDD-driven workflow (2-3 days)

**Day 1 (Morning): Structure Generator Core**
- 🔴 Write failing tests for top-level section generation
- 🟢 Implement basic LLM-based structure generation
- 🔵 Refactor: Extract prompt building, improve error handling
- ✅ Commit: "feat: add outline structure generator"

**Day 1 (Afternoon): Recursive Subsection Generation**
- 🔴 Write failing tests for nested subsection generation
- 🟢 Implement recursive subsection generation with depth limit
- 🔵 Refactor: Optimize recursion, add progress feedback
- ✅ Commit: "feat: add recursive subsection generation"

**Day 2 (Morning): Nesting-Aware Prompts**
- 🔴 Write failing tests for prompt generation
- 🟢 Implement doc-type-aware and nesting-aware prompts
- 🔵 Refactor: Extract prompt templates, improve quality
- ✅ Commit: "feat: add nesting-aware prompt generation"

**Day 2 (Afternoon): Source Mapping**
- 🔴 Write failing tests for source-to-section mapping
- 🟢 Implement LLM-based source mapping with reasoning
- 🔵 Refactor: Improve relevance matching, optimize queries
- ✅ Commit: "feat: add section-source mapping"

**Day 3 (Morning): Validation & Integration**
- 🔴 Write integration tests for complete workflow
- 🟢 Implement outline validator and persistence
- 🔵 Polish: Improve error messages, add metadata
- ✅ Commit: "feat: add outline validation and persistence"

**Day 3 (Afternoon): Testing & Refinement**
- ✅ Run on real test cases (doc-evergreen, simple project)
- ✅ Manual quality review
- ✅ Fix critical issues
- ✅ Sprint review: Demo outline generation

**Note:** Each feature follows multiple red-green-refactor micro-cycles

---

## ⚠️ Known Limitations (By Design - Sprint 4)

1. **60-70% quality** - Not production-ready yet
   - Why acceptable: Sprint 4 proves concept, Sprint 5 polishes
   
2. **Basic nesting strategy** - Simple top-down recursion
   - Why acceptable: Works for most cases, optimize in Sprint 5 if needed
   
3. **Limited prompt sophistication** - Templates could be better
   - Why acceptable: Functional prompts now, excellent prompts in Sprint 5
   
4. **No outline iteration** - Single-pass generation
   - Why acceptable: User can edit outline.json manually (Sprint 7)

---

## 🎯 Next Sprint Preview

After this sprint ships, the most pressing need will be:

**Sprint 5: Hierarchical Outline Generation - Polish ⭐** - Now that we have a working outline generator (60-70% quality), Sprint 5 will focus on reaching the 80%+ quality target through:
- Sophisticated prompt engineering
- Better structure inference strategies
- Improved source-to-section mapping
- Quality validation and refinement

Sprint 5 is where "it works" becomes "it's excellent" - the difference between a proof of concept and a production-ready feature.
