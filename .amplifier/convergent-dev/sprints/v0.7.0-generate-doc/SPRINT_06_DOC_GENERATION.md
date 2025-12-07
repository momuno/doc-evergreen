# Sprint 6: Nesting-Aware Document Generation

**Duration:** 2 days  
**Goal:** Generate content respecting outline structure (structure locked)  
**Value Delivered:** Complete end-to-end generate-doc workflow works!

---

## 🎯 Why This Sprint?

After 5 sprints of building the intelligence (intent capture, file indexing, relevance analysis, outline generation), we finally GENERATE THE DOCUMENTATION! This sprint is about:
1. **Top-down DFS traversal** - Generate from root to leaves
2. **Three-component LLM context** - Prompt + relevancy summaries + full sources
3. **Structure-locked generation** - LLM cannot create new subsections
4. **Nesting-aware context** - Parents know about their children

**The payoff:** Complete end-to-end pipeline from `doc-evergreen generate-doc` to finished documentation.

---

## 📦 Deliverables

### 1. Nesting-Aware Content Generator
**Estimated Lines:** ~280 lines + 200 lines tests

**What it does:**
- Loads outline.json from Sprint 5
- Traverses sections top-down (DFS)
- Generates content for each section using LLM
- Assembles complete document
- Writes to output file

**Why this sprint:**
- The culmination of all previous work
- Delivers end-to-end value
- Proves the concept works

**Implementation notes:**
- Reuse chunked generator patterns from v0.6.0
- Adapt for nesting awareness (inject subsection context)
- Use outline prompts (already nesting-aware from Sprint 5)
- Structure is LOCKED - LLM generates content only, not structure

**Generation algorithm:**
```python
def generate_document(outline_path: Path) -> str:
    """Generate complete document from outline."""
    outline = load_outline(outline_path)
    
    # Generate content for all sections (recursive DFS)
    document_content = []
    
    for section in outline['document']['sections']:
        section_content = generate_section(section, outline_context={
            'doc_type': outline['_meta']['doc_type'],
            'siblings': outline['document']['sections']
        })
        document_content.append(section_content)
    
    # Assemble and write
    full_doc = '\n\n'.join(document_content)
    output_path = outline['document']['output']
    write_file(output_path, full_doc)
    
    return full_doc

def generate_section(section: dict, outline_context: dict) -> str:
    """Generate content for a single section (recursive)."""
    
    # Build three-component LLM context
    llm_context = build_section_context(section, outline_context)
    
    # Generate content for THIS level only
    content = llm_generate(llm_context)
    
    # Add heading
    full_content = f"{section['heading']}\n\n{content}"
    
    # Recursively generate subsections
    if section.get('sections'):
        subsection_content = []
        
        for subsection in section['sections']:
            subsection_text = generate_section(subsection, outline_context={
                'doc_type': outline_context['doc_type'],
                'parent': section,
                'siblings': section['sections']
            })
            subsection_content.append(subsection_text)
        
        full_content += '\n\n' + '\n\n'.join(subsection_content)
    
    return full_content
```

### 2. Three-Component Context Builder
**Estimated Lines:** ~220 lines + 160 lines tests

**What it does:**
- Assembles LLM context with three components:
  1. **Section prompt** - What to generate (nesting-aware)
  2. **Relevancy summaries** - Attention guides (from relevance_notes.json)
  3. **Full source files** - The actual content to reference

**Why this sprint:**
- Critical for quality generation
- Relevancy summaries prevent LLM distraction
- Full sources provide complete information

**Implementation notes:**
- Load relevancy notes for attention guides
- Read full source files for content
- Format context to guide LLM effectively

**Context structure:**
```python
def build_section_context(section: dict, outline_context: dict) -> dict:
    """Build three-component LLM context."""
    
    # Component 1: Section prompt (already nesting-aware)
    prompt = section['prompt']
    
    # Add subsection awareness if needed
    if section.get('sections'):
        subsection_headings = [s['heading'] for s in section['sections']]
        prompt += f"""
        
        CRITICAL: This section has {len(section['sections'])} subsections.
        Do NOT generate content for these - they will be generated separately:
        {', '.join(subsection_headings)}
        
        Your content should introduce this topic at a high level only.
        """
    
    # Component 2: Relevancy summaries (attention guides)
    relevancy_guides = []
    for source in section['sources']:
        guide = {
            'file': source['file'],
            'why_relevant': source['reasoning'],
            'key_material': get_key_material(source['file'])  # From relevance_notes.json
        }
        relevancy_guides.append(guide)
    
    # Component 3: Full source content
    source_contents = []
    for source in section['sources']:
        try:
            content = read_file(source['file'])
            source_contents.append({
                'file': source['file'],
                'content': content
            })
        except Exception as e:
            logger.warning(f"Could not read {source['file']}: {e}")
    
    return {
        'prompt': prompt,
        'relevancy_guides': relevancy_guides,
        'sources': source_contents,
        'doc_type': outline_context['doc_type']
    }
```

**LLM prompt format:**
```
Generate documentation content for: {section_heading}

Documentation type: {doc_type}

Instructions:
{section_prompt}

Relevant Source Files:
{for each source}
  File: {file_path}
  Why relevant: {reasoning}
  Key material to focus on: {key_material}
  
  Full file content:
  ```
  {full_content}
  ```
{end for}

Generate the content now. Follow the instructions exactly.
```

### 3. Progress Tracking & Feedback
**Estimated Lines:** ~120 lines + 80 lines tests

**What it does:**
- Shows progress as sections are generated
- Estimates time remaining
- Provides clear feedback on what's happening

**Why this sprint:**
- Generation can take 30-60 seconds
- Users need to know it's working
- Builds confidence

**Implementation notes:**
- Count total sections upfront
- Update progress after each section
- Show section names as they're generated

**Progress display:**
```python
class GenerationProgressTracker:
    """Track and display generation progress."""
    
    def __init__(self, outline: dict):
        self.total_sections = self._count_sections(outline)
        self.completed = 0
        self.start_time = time.time()
    
    def update(self, section_heading: str):
        """Update progress after generating a section."""
        self.completed += 1
        progress_pct = (self.completed / self.total_sections) * 100
        
        elapsed = time.time() - self.start_time
        avg_time_per_section = elapsed / self.completed
        remaining_sections = self.total_sections - self.completed
        estimated_remaining = avg_time_per_section * remaining_sections
        
        print(f"✨ Generating: {section_heading}")
        print(f"   Progress: {self.completed}/{self.total_sections} sections ({progress_pct:.0f}%)")
        print(f"   Estimated time remaining: {estimated_remaining:.0f}s")
    
    def complete(self, output_path: str, line_count: int):
        """Show completion message."""
        total_time = time.time() - self.start_time
        print(f"\n✅ {output_path} created ({line_count} lines)")
        print(f"⏱️  Generated in {total_time:.1f}s")
```

### 4. Output Writer & Formatter
**Estimated Lines:** ~100 lines + 70 lines tests

**What it does:**
- Formats generated content (consistent spacing, markdown formatting)
- Writes to output file
- Updates context.json status to "generated"

**Why this sprint:**
- Ensures output is well-formatted
- Completes the workflow
- Provides clean user-facing result

**Implementation notes:**
- Consistent section spacing (2 blank lines between sections)
- Proper markdown formatting (code blocks, lists, etc.)
- Create parent directories if needed

**Output formatting:**
```python
def format_and_write_document(content: str, output_path: Path):
    """Format and write generated documentation."""
    
    # Normalize spacing
    content = normalize_spacing(content)
    
    # Ensure code blocks are properly formatted
    content = format_code_blocks(content)
    
    # Ensure proper heading hierarchy
    content = validate_heading_hierarchy(content)
    
    # Create parent directories
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    output_path.write_text(content)
    
    # Count lines
    line_count = len(content.splitlines())
    
    # Update context
    update_context_status('generated', {
        'output_path': str(output_path),
        'line_count': line_count,
        'generated_at': datetime.now().isoformat() + 'Z'
    })
    
    return line_count
```

---

## 🧪 Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all features:

#### 1. 🔴 RED - Write Failing Tests First

**Content Generator Tests:**
```python
def test_generates_content_for_section():
    # Test that content is generated for a section
    section = {
        'heading': '## Installation',
        'level': 2,
        'prompt': 'Write installation instructions...',
        'sources': [{'file': 'pyproject.toml', 'reasoning': '...'}],
        'sections': []
    }
    
    generator = ContentGenerator()
    content = generator.generate_section(section, context={})
    
    assert len(content) > 100
    assert '## Installation' in content

def test_generates_subsections_recursively():
    # Test that subsections are generated
    section_with_subsections = load_test_section('with_subsections.json')
    
    content = generator.generate_section(section_with_subsections, context={})
    
    # Should include parent and all subsection headings
    assert section_with_subsections['heading'] in content
    for subsection in section_with_subsections['sections']:
        assert subsection['heading'] in content

def test_subsection_context_prevents_duplication():
    # Test that parent doesn't duplicate subsection content
    section = load_test_section('parent_with_children.json')
    
    content = generator.generate_section(section, context={})
    
    # Parent content should be brief (has subsections)
    parent_content = content.split(section['sections'][0]['heading'])[0]
    # Brief intro, not comprehensive coverage
    assert len(parent_content) < 500  # Heuristic for "brief"
```

**Context Builder Tests:**
```python
def test_builds_three_component_context():
    # Test that all three components are present
    section = load_test_section('with_sources.json')
    
    builder = ContextBuilder()
    context = builder.build_section_context(section, {})
    
    assert 'prompt' in context
    assert 'relevancy_guides' in context
    assert 'sources' in context
    assert len(context['sources']) > 0

def test_loads_full_source_content():
    # Test that full file content is loaded
    section = {'sources': [{'file': 'test_file.py', 'reasoning': '...'}]}
    
    context = builder.build_section_context(section, {})
    
    source = context['sources'][0]
    assert source['file'] == 'test_file.py'
    assert len(source['content']) > 0
```

Run tests → Watch them fail → Good!

#### 2. 🟢 GREEN - Write Minimal Implementation

```python
class ContentGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.context_builder = ContextBuilder()
    
    def generate_document(self, outline_path: Path) -> str:
        """Generate complete document from outline."""
        outline = json.loads(outline_path.read_text())
        
        # Track progress
        tracker = GenerationProgressTracker(outline)
        
        print("✨ Generating documentation...")
        
        # Generate all sections
        sections_content = []
        for section in outline['document']['sections']:
            content = self.generate_section(section, {
                'doc_type': outline['_meta']['doc_type']
            })
            sections_content.append(content)
            tracker.update(section['heading'])
        
        # Assemble document
        full_doc = '\n\n'.join(sections_content)
        
        # Write output
        output_path = Path(outline['document']['output'])
        line_count = format_and_write_document(full_doc, output_path)
        
        tracker.complete(str(output_path), line_count)
        
        return full_doc
    
    def generate_section(self, section: dict, outline_context: dict) -> str:
        """Generate content for section (recursive)."""
        # Build LLM context
        context = self.context_builder.build_section_context(section, outline_context)
        
        # Generate content
        content = self.llm.generate(self._format_generation_prompt(context))
        
        # Add heading
        result = f"{section['heading']}\n\n{content}"
        
        # Generate subsections recursively
        for subsection in section.get('sections', []):
            subsection_content = self.generate_section(subsection, outline_context)
            result += '\n\n' + subsection_content
        
        return result
```

Run tests → Watch them pass → Good!

#### 3. 🔵 REFACTOR - Improve Code Quality

- Extract prompt formatting to separate function
- Add error handling for source file reading
- Optimize LLM calls (batch if possible)
- Add comprehensive logging

Run tests → Still pass → Good!

### Unit Tests (Write First)

- **Content generation**: Section content, subsection recursion, empty sections
- **Context building**: Three components, source loading, error handling
- **Progress tracking**: Section counting, time estimation, completion
- **Output formatting**: Spacing, markdown, heading hierarchy

### Integration Tests (Write First)

- **End-to-end generation**: outline.json → complete document
- **Real test cases**: doc-evergreen outline, Python library outline
- **Edge cases**: Minimal outline, deep nesting, missing sources

### Manual Testing (After Automated Tests Pass)

- [ ] Generate doc from doc-evergreen outline - verify quality
- [ ] Check nesting awareness - parents don't duplicate children
- [ ] Verify sources are used appropriately
- [ ] Check output formatting - clean and readable
- [ ] Test complete workflow: generate-doc → outline → document

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Bottom-Up Generation
- **Why**: Top-down DFS is simpler and sufficient for MVP
- **Reconsider**: v0.8.0 if users report quality issues

### ❌ Parallel Section Generation
- **Why**: Sequential is simpler, latency is acceptable
- **Reconsider**: v0.8.0 for performance optimization

### ❌ Generation Retries/Refinement
- **Why**: Single-pass generation for v0.7.0, outline quality is good
- **Reconsider**: v0.8.0 if content quality is insufficient

### ❌ Custom Content Templates
- **Why**: Outline prompts provide sufficient guidance
- **Reconsider**: v0.8.0 if users want more control

### ❌ Content Quality Scoring
- **Why**: Outline quality is already high, focus on structure
- **Reconsider**: v0.8.0 for content-level quality gates

### ❌ Multi-Model Generation
- **Why**: Single GPT-4 model is sufficient
- **Examples**: Use different models for different sections
- **Reconsider**: v0.8.0 if quality/cost optimization needed

---

## 📋 Dependencies

### Requires from previous sprints:
- **Sprint 5**: outline.json (80%+ quality)
- **Sprint 3**: relevance_notes.json (for attention guides)
- **Sprint 1**: context.json (doc_type, output_path)

### Provides for future sprints:
- **Generated document** for Sprint 7 (user review)
- **End-to-end workflow** for Sprint 7 (complete pipeline to test)
- **Complete MVP** for users!

---

## ✅ Acceptance Criteria

### Must Have

- ✅ **Generates complete document**: From outline.json to output file
- ✅ **Respects nesting**: Parents don't duplicate subsection content
- ✅ **Uses three-component context**: Prompt + relevancy + sources
- ✅ **Top-down DFS works**: Correct traversal order
- ✅ **Progress feedback**: Clear indication of what's happening
- ✅ **Output formatted**: Clean, readable markdown
- ✅ **Context updated**: status = "generated"
- ✅ **Tests pass**: >80% coverage, all tests green

### Quality Targets

- **Content quality**: Reasonable (doesn't need to be perfect)
- **Structure adherence**: 100% (matches outline exactly)
- **Source usage**: Appropriate (uses provided sources)
- **Nesting awareness**: 90%+ (parents don't duplicate children)

### Success Validation

**End-to-end test:**
```bash
$ doc-evergreen generate-doc README.md \
    --type tutorial \
    --purpose "Help developers get started in 5 minutes"

🔍 Analyzing project...
   Found 23 files, identified 8 relevant

📝 Generating outline...
   5 sections, 12 subsections
   Quality: 85%

✨ Generating documentation...
   ✨ Generating: # Getting Started
      Progress: 1/17 sections (6%)
   ✨ Generating: ## Installation
      Progress: 2/17 sections (12%)
   ...
   
✅ README.md created (450 lines)
⏱️  Generated in 45.2s
```

---

## 🛠️ Technical Approach

### Key Decisions

**Decision 1: Top-down DFS (not bottom-up)**
- **Rationale**: Simpler to implement, natural traversal order
- **Alternative considered**: Bottom-up (children first, then parents with context)
- **Why top-down**: MVP first, can add bottom-up in v0.8.0 if needed

**Decision 2: Structure-locked generation**
- **Rationale**: LLM only generates content, not structure
- **Alternative considered**: Allow LLM to create subsections dynamically
- **Why locked**: Outline quality is high, structure should not change

**Decision 3: Three-component context**
- **Rationale**: Balance attention (relevancy) with completeness (full source)
- **Alternative considered**: Only summaries (incomplete) or only full sources (distracting)
- **Why three components**: Best of both worlds

**Decision 4: Reuse v0.6.0 generation patterns**
- **Rationale**: Proven patterns, reduce risk
- **Alternative considered**: Build from scratch
- **Why reuse**: Chunked generator works well, adapt for nesting

### LLM Configuration

```python
# Document generation uses GPT-4 for quality
GENERATION_LLM_CONFIG = {
    'model': 'gpt-4',
    'temperature': 0.5,  # Some creativity, but consistent
    'max_tokens': 2000,  # Generous for comprehensive sections
}
```

### Reusable from v0.6.0

```python
# Adapt chunked_generator.py for nesting awareness
from doc_evergreen.core.chunked_generator import ChunkedGenerator

class NestingAwareGenerator(ChunkedGenerator):
    """Extends ChunkedGenerator with nesting awareness."""
    
    def generate_section_content(self, section: dict, context: dict) -> str:
        """Override to inject subsection context."""
        # Build nesting-aware prompt
        prompt = section['prompt']
        
        if section.get('sections'):
            # Add subsection awareness
            prompt = self._inject_subsection_context(prompt, section['sections'])
        
        # Call parent class with enhanced prompt
        return super().generate_content(prompt, section['sources'])
```

---

## 🔍 What You Learn

After this sprint, you'll discover:

1. **Generation quality**: Does the content match outline quality?
   - → Validates end-to-end workflow OR signals need for content refinement
   
2. **Nesting effectiveness**: Do parents properly avoid subsection content?
   - → Validates Sprint 5 prompt quality
   
3. **Source usage**: Do generated docs properly reference sources?
   - → Validates three-component context design
   
4. **Performance**: How long does generation take?
   - → Informs caching/optimization needs for v0.8.0

---

## 📊 Success Metrics

### Quantitative
- **Structure adherence**: 100% (matches outline)
- **Nesting awareness**: 90%+ (parents don't duplicate children)
- **Source coverage**: 80%+ (uses provided sources)
- **Generation speed**: <60s for typical doc (10-15 sections)
- **Test coverage**: >80%

### Qualitative
- Generated content is coherent and useful
- Structure feels right (outline structure preserved)
- No obvious hallucinations or errors
- Output is readable and well-formatted

### Validation Method
**Manual review** (for doc-evergreen tutorial):
- [ ] Read generated README - does it make sense?
- [ ] Check parent sections - are they brief intros?
- [ ] Check leaf sections - are they comprehensive?
- [ ] Verify sources are used - can you trace content to sources?
- [ ] Would you ship this? (with minor edits)

---

## 📅 Implementation Order

### TDD-driven workflow (2 days)

**Day 1 (Morning): Content Generator Core**
- 🔴 Write failing tests for section content generation
- 🟢 Implement basic LLM-based content generation
- 🔵 Refactor: Extract prompt formatting, improve error handling
- ✅ Commit: "feat: add content generator"

**Day 1 (Afternoon): Recursive Generation & Context Building**
- 🔴 Write failing tests for recursive subsection generation
- 🟢 Implement DFS traversal and three-component context
- 🔵 Refactor: Optimize context building, add caching
- ✅ Commit: "feat: add recursive generation and context building"

**Day 2 (Morning): Progress Tracking & Output**
- 🔴 Write failing tests for progress tracking
- 🟢 Implement progress display and output formatting
- 🔵 Refactor: Improve feedback messages, optimize formatting
- ✅ Commit: "feat: add progress tracking and output"

**Day 2 (Afternoon): Integration & Testing**
- 🔴 Write integration tests for end-to-end workflow
- 🟢 Wire everything together, test on real outlines
- 🔵 Polish: Fix issues, improve quality
- ✅ Manual testing on doc-evergreen
- ✅ Sprint review: Demo complete generate-doc workflow!

**Note:** Each feature follows multiple red-green-refactor micro-cycles

---

## ⚠️ Known Limitations (By Design)

1. **Top-down only** - No bottom-up generation option
   - Why acceptable: Simpler for MVP, works for most cases
   
2. **Structure locked** - Cannot adjust structure during generation
   - Why acceptable: Outline quality is high, users can edit outline first
   
3. **Single-pass generation** - No content refinement
   - Why acceptable: Outline prompts are good, content should be acceptable
   
4. **Sequential generation** - Not parallelized
   - Why acceptable: Reasonable speed, simpler implementation

---

## 🎯 Next Sprint Preview

After this sprint ships, the most pressing need will be:

**Sprint 7: Outline Review Workflow** - Now that we can generate docs end-to-end, we need to give users the ability to REVIEW AND EDIT the outline before generation. Sprint 7 will implement a two-command workflow (generate-outline → edit → generate-from-outline) that makes the tool production-ready.

Sprint 6 proves the technology works. Sprint 7 makes it user-friendly and production-ready!
