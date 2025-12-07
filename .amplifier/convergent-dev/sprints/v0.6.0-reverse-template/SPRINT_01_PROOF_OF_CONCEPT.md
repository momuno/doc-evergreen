# Sprint 1: End-to-End Proof of Concept

**Duration:** 2-3 days  
**Goal:** Working reverse template pipeline with naive source discovery  
**Value Delivered:** User can generate valid templates from existing docs TODAY

---

## 🎯 Why This Sprint?

Sprint 1 proves the core concept works end-to-end. Even with naive source discovery (pattern matching only), users can:
- Generate valid templates from existing documentation
- See structure extraction in action
- Test on their own docs immediately
- Manually refine sources if needed

**This validates the approach and motivates the harder work in Sprint 2.**

We're building a vertical slice: parse → discover → assemble → output. Each piece is simple, but together they deliver value.

---

## 📦 Deliverables

### 1. Document Structure Parser
**Estimated Lines:** ~200 lines + 150 lines tests

**What it does:**
- Parses markdown files (README.md, CONTRIBUTING.md, etc.)
- Extracts heading hierarchy (H1, H2, H3)
- Identifies section boundaries and content blocks
- Captures structure for template mapping

**Why this sprint:**
Foundation for everything. Without structure extraction, we can't build templates.

**Implementation notes:**
- Use Python `mistune` or `markdown` library for parsing
- Build document tree representation (nested dict structure)
- Extract headings with level, text, and content
- Keep it simple - handle standard markdown only for now

**TDD approach:**
```python
# 🔴 RED: Write test first
def test_parse_simple_readme():
    doc = "# Title\n\n## Section 1\n\nContent here\n\n## Section 2\n\nMore content"
    result = DocumentParser.parse(doc)
    assert result['sections'][0]['heading'] == 'Title'
    assert len(result['sections'][0]['subsections']) == 2
    # This will FAIL - parser doesn't exist yet

# 🟢 GREEN: Write minimal code
class DocumentParser:
    @staticmethod
    def parse(markdown_text):
        # Minimal implementation to pass test
        # Use mistune to extract headings
        pass

# 🔵 REFACTOR: Clean up, add features
# Extract into proper module structure
# Add better error handling
# Optimize heading extraction
```

---

### 2. Pattern-Based Source Discovery (Naive)
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
- Maintains mapping of section types → typical source patterns
- Pattern matching for common section types
- Returns list of candidate source files per section

**Why this sprint:**
Proves source discovery works. Even simple pattern matching provides value (50-60% accuracy).

**Implementation notes:**
```python
SECTION_PATTERNS = {
    'installation': ['package.json', 'setup.py', 'pyproject.toml', 'requirements.txt'],
    'api reference': ['src/**/*.py', 'lib/**/*.js', 'api/**/*'],
    'configuration': ['config/**/*.yaml', '*.config.js', '.env.example'],
    'architecture': ['docs/architecture.md', 'src/core/**/*'],
    'contributing': ['CONTRIBUTING.md', '.github/**/*', 'docs/contributing.md'],
}

def discover_sources_naive(section_heading, section_content, project_root):
    """
    Match section heading against known patterns.
    Return list of files that match patterns.
    """
    # Normalize heading (lowercase, remove special chars)
    # Match against SECTION_PATTERNS
    # Use glob to find matching files in project_root
    # Return list of found files
    pass
```

**TDD approach:**
```python
# 🔴 RED: Test first
def test_discover_installation_sources():
    sources = discover_sources_naive(
        section_heading="Installation",
        section_content="To install, run pip install...",
        project_root="/fake/project"
    )
    assert 'package.json' in sources or 'setup.py' in sources
    # FAILS - function doesn't exist

# 🟢 GREEN: Implement
def discover_sources_naive(section_heading, section_content, project_root):
    # Simple pattern matching
    # Use glob to find files
    pass

# 🔵 REFACTOR: Improve pattern matching
# Add more patterns
# Better file existence checking
# Handle project type detection
```

---

### 3. Template Assembly & Validation
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
- Assembles parsed structure + discovered sources into template.json
- Generates basic metadata (name, description, quadrant)
- Validates template structure
- Outputs valid template file

**Why this sprint:**
End-to-end delivery - produces usable template.json that works with existing `regen` command.

**Implementation notes:**
```python
def assemble_template(parsed_doc, source_mappings, output_path):
    """
    Build template.json from components.
    
    Template structure:
    {
        "name": "README-reversed",
        "description": "Auto-generated from existing README.md",
        "quadrant": "explanation",  # Default for now
        "sections": [
            {
                "heading": "Installation",
                "prompt": "Document installation instructions",  # Placeholder
                "sources": ["package.json", "setup.py"]
            }
        ]
    }
    """
    # Infer quadrant from section types (start with "explanation" default)
    # Map each section to template section
    # Generate placeholder prompts (Sprint 3 will improve these)
    # Validate against schema
    # Write to output_path
    pass
```

**TDD approach:**
```python
# 🔴 RED: Test output structure
def test_assemble_valid_template():
    parsed_doc = {...}  # Mock parsed structure
    sources = {...}     # Mock source mappings
    
    template = assemble_template(parsed_doc, sources, "output.json")
    
    assert template['name'] == 'README-reversed'
    assert len(template['sections']) > 0
    assert template['sections'][0]['heading'] is not None
    # FAILS - function doesn't exist

# 🟢 GREEN: Basic implementation
# 🔵 REFACTOR: Validation, error handling
```

---

### 4. CLI Command Implementation (Basic)
**Estimated Lines:** ~100 lines + 50 lines tests

**What it does:**
- New command: `doc-evergreen template reverse <doc-path>`
- Orchestrates: parse → discover → assemble
- Basic progress output
- Saves template to `.doc-evergreen/templates/`

**Why this sprint:**
User-facing entry point. Makes everything usable.

**Implementation notes:**
```python
@click.command()
@click.argument('doc_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output template path')
def reverse(doc_path, output):
    """Generate template from existing documentation."""
    
    print(f"🔍 Analyzing {doc_path}...")
    
    # Parse document
    with open(doc_path) as f:
        content = f.read()
    parsed_doc = DocumentParser.parse(content)
    print(f"📝 Found {len(parsed_doc['sections'])} sections")
    
    # Discover sources (naive)
    project_root = Path(doc_path).parent
    source_mappings = {}
    for section in parsed_doc['sections']:
        sources = discover_sources_naive(
            section['heading'], 
            section['content'],
            project_root
        )
        source_mappings[section['id']] = sources
    print(f"✅ Found {len(source_mappings)} source mappings")
    
    # Assemble template
    template_name = Path(doc_path).stem + '-reversed'
    output_path = output or f".doc-evergreen/templates/{template_name}.json"
    assemble_template(parsed_doc, source_mappings, output_path)
    
    print(f"✅ Template generated: {output_path}")
    print("\nNext steps:")
    print(f"1. Review: cat {output_path}")
    print(f"2. Test: doc-evergreen regen --template {output_path}")
```

**TDD approach:**
```python
# 🔴 RED: Integration test
def test_reverse_command_end_to_end(tmp_path):
    # Create test README
    readme = tmp_path / "README.md"
    readme.write_text("# Test\n\n## Installation\n\nRun pip install")
    
    # Run command
    runner = CliRunner()
    result = runner.invoke(reverse, [str(readme)])
    
    # Assert template created
    assert result.exit_code == 0
    assert "Template generated" in result.output
    template_path = tmp_path / ".doc-evergreen/templates/README-reversed.json"
    assert template_path.exists()
    # FAILS - command doesn't exist

# 🟢 GREEN: Implement basic command
# 🔵 REFACTOR: Error handling, better output
```

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ LLM Content Analysis
- **Why**: Don't need to understand section intent yet
- **Reconsider**: Sprint 3 (after source discovery works)
- Pattern matching is sufficient for Sprint 1

### ❌ Semantic Search for Sources
- **Why**: Pattern matching proves the concept
- **Reconsider**: Sprint 2 (the main event)
- Naive discovery is 50-60% accurate, good enough for validation

### ❌ Intelligent Prompt Generation
- **Why**: Placeholder prompts work for testing
- **Reconsider**: Sprint 3
- Users can manually refine prompts after generation

### ❌ CLI Options (--dry-run, --verbose)
- **Why**: Basic command proves usability
- **Reconsider**: Sprint 4 (polish)
- Simple happy path is sufficient

### ❌ Advanced Error Handling
- **Why**: Basic validation is enough
- **Reconsider**: Sprint 4
- Focus on working pipeline first

---

## 🧪 Testing Requirements

### TDD Approach (Red-Green-Refactor)

**Day 1:**
- 🔴 Write failing tests for DocumentParser
- 🟢 Implement DocumentParser (minimal)
- 🔵 Refactor DocumentParser
- ✅ Commit (tests green)

**Day 2:**
- 🔴 Write failing tests for source discovery
- 🟢 Implement pattern matching
- 🔵 Refactor pattern logic
- ✅ Commit (tests green)

**Day 3:**
- 🔴 Write failing tests for template assembly
- 🟢 Implement assembly logic
- 🔵 Refactor validation
- 🔴 Write end-to-end CLI test
- 🟢 Wire everything together
- ✅ Final commit & sprint review

### Unit Tests (Write First)
- **DocumentParser**:
  - Parse simple markdown (H1, H2)
  - Handle nested sections (H1 → H2 → H3)
  - Extract section content correctly
  - Handle edge cases (empty sections, no headings)

- **Pattern-based discovery**:
  - Match "Installation" → package files
  - Match "API Reference" → code files
  - Match "Contributing" → CONTRIBUTING.md
  - Handle no matches (return empty list)
  - Handle multiple matches (return all)

- **Template assembly**:
  - Generate valid JSON structure
  - Include all sections from parsed doc
  - Map sources to sections
  - Generate placeholder prompts
  - Validate against schema

### Integration Tests (After Unit Tests Pass)
- **End-to-end workflow**:
  - Parse doc-evergreen README
  - Discover sources for each section
  - Generate valid template
  - Template can be used with `regen` command

### Manual Testing (After Automated Tests Pass)
- [ ] Run on doc-evergreen's README
- [ ] Inspect generated template structure
- [ ] Verify sources are reasonable (50-60% accuracy expected)
- [ ] Test template with `regen` command
- [ ] Compare regenerated output to original

**Test Coverage Target:** >80% for new code

---

## 📊 What You Learn

After Sprint 1, you'll discover:

1. **Structure extraction feasibility**
   - Can we reliably parse markdown structure?
   - What edge cases exist in real docs?
   - Does heading hierarchy map well to templates?

2. **Pattern matching accuracy**
   - How often do patterns find correct sources?
   - What patterns are most reliable?
   - Where does naive discovery fail?
   → **This motivates Sprint 2's intelligent discovery**

3. **Template generation viability**
   - Does auto-generated template structure make sense?
   - Can users actually use the generated templates?
   - What's missing for production use?
   → **This validates the v0.6.0 approach**

4. **User workflow validation**
   - Is the `reverse → regen` workflow intuitive?
   - What friction points exist?
   - What features are most needed?

---

## ✅ Success Criteria

### Must Have
- ✅ CLI command `doc-evergreen template reverse README.md` works
- ✅ Generates valid template.json with structure matching input doc
- ✅ Pattern-based source discovery finds sources for common sections (50-60% accuracy)
- ✅ Template can be used immediately with `regen` command
- ✅ All tests pass with >80% coverage

### Nice to Have (Defer if Time Constrained)
- ❌ Support for non-markdown formats (RST, etc.) → Sprint 4
- ❌ Advanced pattern matching → Sprint 2
- ❌ Detailed progress output → Sprint 4

---

## 🛠️ Technical Approach

### Architecture
```
CLI Command (template reverse)
  ↓
ReverseTemplateOrchestrator
  ├─→ DocumentParser
  │     Input: markdown text
  │     Output: {title, sections: [{heading, level, content}]}
  │
  ├─→ NaiveSourceDiscoverer
  │     Input: section heading + content
  │     Output: [list of source file paths]
  │
  └─→ TemplateAssembler
        Input: parsed doc + source mappings
        Output: template.json
```

### Key Decisions

**1. Use mistune for markdown parsing**
- Well-tested library
- Handles edge cases
- Good performance
- Alternative: markdown-it-py

**2. Start with pattern dictionary**
- Simple to implement
- Easy to test
- Sufficient for proof of concept
- Foundation for Sprint 2 improvements

**3. Placeholder prompts**
- "Document the {section_heading} for this project"
- Good enough for Sprint 1
- Sprint 3 will generate intelligent prompts

**4. Default to "explanation" quadrant**
- Most READMEs are explanatory
- Can be manually refined
- Sprint 3 will infer quadrant properly

---

## 📅 Implementation Order

### Day 1: Document Parser
- 🔴 Write DocumentParser tests
- 🟢 Implement basic parsing with mistune
- 🔵 Refactor into clean module
- Test on doc-evergreen README
- ✅ Commit

### Day 2: Source Discovery + Assembly
- 🔴 Write source discovery tests
- 🟢 Implement pattern matching
- 🔵 Refactor pattern logic
- 🔴 Write assembly tests
- 🟢 Implement template builder
- 🔵 Refactor validation
- ✅ Commit

### Day 3: CLI + Integration
- 🔴 Write CLI integration test
- 🟢 Wire components together
- 🔵 Refactor error handling
- Manual testing on real docs
- Documentation update
- ✅ Final commit & sprint review

---

## 🎯 Known Limitations (By Design)

1. **Pattern matching is naive (50-60% accuracy)**
   - Acceptable: Proves concept, Sprint 2 will improve
   - Users can manually refine sources

2. **Placeholder prompts aren't intelligent**
   - Acceptable: Sprint 3 will generate proper prompts
   - Basic prompts work for testing reverse → regen workflow

3. **No quadrant inference**
   - Acceptable: Defaults to "explanation"
   - Sprint 3 will analyze content to infer quadrant

4. **Limited error handling**
   - Acceptable: Happy path testing only
   - Sprint 4 will add robust error handling

5. **No CLI options (--dry-run, --verbose, etc.)**
   - Acceptable: Basic command proves usability
   - Sprint 4 will add polish

---

## 🔄 Next Sprint Preview

After Sprint 1 ships, the **most pressing need** will be:

**Better source discovery** - Pattern matching finds sources 50-60% of the time, but we need 70-80% accuracy for the feature to be truly useful. Sprint 2 will add:
- Semantic search (grep for keywords from section content)
- LLM relevance scoring (rate sources 0-10 for each section)
- Smart ranking and filtering (top 3-5 sources per section)

Sprint 1 proves the pipeline works. Sprint 2 makes it accurate enough to ship.

---

**Ready to start building?** 🚀 Follow the TDD approach and commit frequently!
