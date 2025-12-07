# v0.6.0 Feature Scope: Reverse Template Generation

**Release**: v0.6.0  
**Cycle**: Loop 6 of convergent-dev  
**Date**: 2025-12-01  
**Status**: ✅ Converged  
**Effort Estimate**: 6-10 days  
**Learning Goal**: Validate that automated template generation from existing docs works and enables "update workflow"

---

## 🎯 Problem Statement

### The Core Problem
Users have **existing documentation that is well-structured and well-liked**, but has become **outdated** as the codebase evolved. They want to update these docs using doc-evergreen, but face critical blockers:

1. **Can't regenerate without template** → Risk losing structure/approach
2. **Don't know what sources were originally used** → Can't manually recreate template
3. **Manual template creation is too tedious** → High barrier to adoption
4. **Can't reference outdated doc as context** → Creates context poisoning

### User Quote
> "I don't want to manually craft the template based on an existing doc I like. But creating that smart template is going to take some thought or some algorithmic work I imagine, like how we go about automatically reviewing the repo for appropriate source files to include for each section."

### Why This Matters
- **Adoption Barrier**: Existing projects can't easily adopt doc-evergreen
- **Update Workflow**: Enables UC2 (update existing documentation) from original convergence
- **Template Creation Friction**: Manual template creation is the #1 pain point from v0.5.0 testing
- **Differentiation**: No other doc tool does automated template generation well

### Success Criteria
Template generated from existing doc is **70-80% accurate** ("remotely close to what was currently present"):
- Structure matches original doc
- Source files are relevant to each section
- Prompts would recreate similar content approach
- User can run `regen` immediately with reasonable results
- User can refine template to 95%+ with minimal effort

---

## 🚀 Feature Breakdown

### Feature 1: Document Structure Parser
**What it does:**
- Parses existing markdown documentation (README.md, CONTRIBUTING.md, etc.)
- Extracts heading hierarchy (H1, H2, H3)
- Identifies section boundaries and content blocks
- Captures existing structure for template mapping

**Technical Approach:**
- Use markdown parser (e.g., `markdown-it`, `mistune`, or custom regex)
- Build document tree representation
- Map headings to potential template sections

**Acceptance Criteria:**
- ✅ Parses standard markdown with heading levels
- ✅ Handles nested sections correctly
- ✅ Preserves section order and hierarchy
- ✅ Extracts section content for analysis

**Effort**: 0.5-1 day

---

### Feature 2: Content Intent Analyzer (LLM-Powered)
**What it does:**
- Analyzes each section's content to understand purpose and intent
- Classifies section type (overview, installation, API reference, troubleshooting, etc.)
- Extracts key topics, concepts, and technical terms
- Infers Divio quadrant (Tutorial, How-to, Reference, Explanation)

**Technical Approach:**
- Use LLM (current doc-evergreen model) with specialized prompts
- Prompt engineering: "Analyze this documentation section and identify its primary purpose, key topics, and classification"
- Extract structured metadata for each section

**Example:**
```markdown
# Installation

To install doc-evergreen, run:
```bash
pip install doc-evergreen
```
```

**LLM Analysis Output:**
```json
{
  "section_type": "installation",
  "divio_quadrant": "how-to",
  "key_topics": ["installation", "package management", "pip"],
  "intent": "Guide users through installing the package",
  "technical_terms": ["pip", "package manager"]
}
```

**Acceptance Criteria:**
- ✅ Analyzes section content with LLM
- ✅ Classifies section type with reasonable accuracy (>70%)
- ✅ Extracts key topics and technical terms
- ✅ Infers Divio quadrant for template metadata

**Effort**: 1-1.5 days

---

### Feature 3: Intelligent Source Discovery ⭐ (Core Innovation)
**What it does:**
- For each section, automatically discovers relevant source files from the codebase
- Uses pattern matching for common section types (Installation → package.json, setup.py)
- Semantic search of codebase files for relevance to section topics
- LLM-assisted relevance scoring to rank source files

**Technical Approach:**

**Phase 1: Pattern-Based Discovery**
- Maintain mapping of section types → typical source patterns
- Examples:
  - "Installation" → `package.json`, `setup.py`, `pyproject.toml`, `requirements.txt`
  - "API Reference" → Public code files (`.py`, `.js`, `.ts`), API routes
  - "Configuration" → Config files (`.yaml`, `.json`, `.env.example`)
  - "Architecture" → Core modules, system diagrams, architecture docs
  - "Contributing" → `CONTRIBUTING.md`, `.github/` files, dev docs

**Phase 2: Semantic Search**
- Index codebase files (use existing file system traversal)
- For each section's key topics/terms, search codebase for relevant files
- Use file content analysis (grep for key terms, code structure analysis)

**Phase 3: LLM Relevance Scoring**
- For candidate source files, use LLM to score relevance
- Prompt: "Given this documentation section about {topic}, rate the relevance of this source file on a scale of 0-10"
- Filter sources with score >5, rank by score

**Example:**
```markdown
# API Reference

The doc-evergreen API provides three main endpoints:
- `/generate` - Generate documentation from template
- `/validate` - Validate template structure
- `/analyze` - Analyze existing documentation
```

**Source Discovery Output:**
```json
{
  "section": "API Reference",
  "sources": [
    {
      "path": "src/api/routes.py",
      "relevance_score": 9,
      "match_reason": "Contains API endpoint definitions"
    },
    {
      "path": "src/api/handlers.py",
      "relevance_score": 8,
      "match_reason": "Implements endpoint logic"
    },
    {
      "path": "src/api/__init__.py",
      "relevance_score": 6,
      "match_reason": "API module initialization"
    }
  ]
}
```

**Acceptance Criteria:**
- ✅ Pattern matching works for common section types (installation, config, etc.)
- ✅ Semantic search finds relevant files based on key topics
- ✅ LLM relevance scoring ranks sources effectively (>70% accuracy)
- ✅ Sources are ranked and filtered (top 3-5 per section)
- ✅ Handles edge cases (no relevant sources found → suggest project root or ask user)

**Effort**: 2-3 days (this is the meaty algorithmic work)

**Note**: This work overlaps with DE-t6l "Smart Source Detection" from backlog

---

### Feature 4: Prompt Generation (LLM-Powered)
**What it does:**
- Given section content + discovered sources, generates appropriate prompt
- Creates prompt that would recreate the section's content approach
- Uses prompt patterns (basic, explanation-focused, tutorial-style, reference-style)

**Technical Approach:**
- Leverage prompt patterns (can use ideas from DE-2t4 "Prompt Templates Library")
- Use LLM to generate prompt based on section analysis:
  - Input: Section content, section type, key topics, discovered sources
  - Output: Prompt that would recreate similar content

**Example:**
```markdown
# Installation

To install doc-evergreen, run:
```bash
pip install doc-evergreen
```

For development installation:
```bash
git clone https://github.com/user/doc-evergreen.git
cd doc-evergreen
pip install -e ".[dev]"
```
```

**Generated Prompt:**
```json
{
  "section": "Installation",
  "prompt": "Provide clear installation instructions for both standard users and developers. Include pip installation command for users, and git clone + editable install for developers. Keep it concise and actionable."
}
```

**Acceptance Criteria:**
- ✅ Generates prompts for each section based on content analysis
- ✅ Prompts are specific enough to guide content generation
- ✅ Prompts reflect the original section's approach (tutorial vs reference style)
- ✅ Handles different section types appropriately

**Effort**: 1-2 days

---

### Feature 5: Template Assembly & Validation
**What it does:**
- Assembles all analyzed components into valid `template.json`
- Validates template structure against schema
- Generates metadata (quadrant, title, description)
- Outputs ready-to-use template file

**Technical Approach:**
- Build template structure from analyzed components
- Infer quadrant from section classifications
- Generate template title/description from doc title and analysis
- Validate using existing template validation logic (DE-b8p if implemented)

**Example Output:**
```json
{
  "name": "README-reversed",
  "description": "Auto-generated template from existing README.md",
  "quadrant": "explanation",
  "sections": [
    {
      "heading": "Introduction",
      "prompt": "Provide a clear overview of doc-evergreen...",
      "sources": ["README.md", "src/__init__.py"]
    },
    {
      "heading": "Installation",
      "prompt": "Provide clear installation instructions...",
      "sources": ["package.json", "pyproject.toml"]
    },
    {
      "heading": "API Reference",
      "prompt": "Document the main API endpoints...",
      "sources": ["src/api/routes.py", "src/api/handlers.py"]
    }
  ]
}
```

**Acceptance Criteria:**
- ✅ Generates valid template.json structure
- ✅ Template can be used with `doc-evergreen regen` immediately
- ✅ Includes all required fields (name, quadrant, sections)
- ✅ Validates against template schema
- ✅ Saves to `.doc-evergreen/templates/` directory

**Effort**: 0.5-1 day

---

### Feature 6: CLI Command Implementation
**What it does:**
- New command: `doc-evergreen template reverse <doc-path>`
- Orchestrates all components (parse → analyze → discover → generate → assemble)
- Provides progress feedback to user
- Handles errors gracefully

**Technical Approach:**
```bash
doc-evergreen template reverse README.md

# Output:
🔍 Analyzing README.md structure...
📝 Found 8 sections
🤖 Analyzing section content with LLM...
🔎 Discovering relevant source files...
✅ Found 12 relevant sources
💡 Generating prompts for each section...
📦 Assembling template...
✅ Template generated: .doc-evergreen/templates/README-reversed.json

Next steps:
1. Review template: cat .doc-evergreen/templates/README-reversed.json
2. Test regeneration: doc-evergreen regen --template .doc-evergreen/templates/README-reversed.json --output README-NEW.md
3. Compare results and refine template if needed
```

**CLI Options:**
- `--output <path>` - Specify output template path (default: `.doc-evergreen/templates/{doc-name}-reversed.json`)
- `--dry-run` - Show analysis without generating template
- `--verbose` - Show detailed progress and LLM reasoning

**Acceptance Criteria:**
- ✅ Command executes full reverse template pipeline
- ✅ Provides clear progress feedback
- ✅ Handles common errors (file not found, invalid markdown, LLM failures)
- ✅ Saves template to appropriate location
- ✅ Suggests next steps to user

**Effort**: 1-2 days (includes integration, error handling, testing)

---

## 🧪 Test Cases & Examples

### Test Case 1: doc-evergreen's own README.md
**Input**: Current README.md (which may be outdated)
**Expected Output**:
- Template with 6-8 sections matching current structure
- Sources include: `src/`, `pyproject.toml`, key module files
- Prompts appropriate for each section type
- Can regenerate and get updated README with same structure

### Test Case 2: Simple Project README
**Input**: Basic README with Installation, Usage, Contributing
**Expected Output**:
- Template with 3 sections
- Installation sources: `package.json` or `setup.py`
- Usage sources: Main code files, examples/
- Contributing sources: CONTRIBUTING.md if exists, otherwise project root

### Test Case 3: Complex Technical Documentation
**Input**: Architecture guide with multiple subsections
**Expected Output**:
- Template preserves nested structure
- Sources mapped to architecture-relevant files
- Prompts are explanation-focused (matches Divio "Explanation" quadrant)

### Test Case 4: Edge Cases
- **Empty sections**: Generates prompt asking to fill in content
- **No relevant sources found**: Suggests project root or core modules
- **Very long document**: Handles >50 sections gracefully (may group or summarize)

---

## 🏗️ Architecture Approach

### Component Architecture
```
CLI Command (template reverse)
  ↓
ReverseTemplateOrchestrator
  ├─→ DocumentParser (markdown → structure)
  ├─→ ContentAnalyzer (LLM → section metadata)
  ├─→ SourceDiscoverer (pattern + semantic + LLM → sources)
  ├─→ PromptGenerator (LLM → prompts)
  └─→ TemplateAssembler (components → template.json)
```

### Key Design Decisions

**1. Modular Pipeline**
- Each component is independent and testable
- Can iterate on individual components without rewriting everything
- Enables future improvements (better source discovery, better prompt generation)

**2. LLM as Analysis Tool**
- Use existing LLM infrastructure from doc-evergreen
- Leverage LLM for semantic understanding (content analysis, relevance scoring)
- Keep prompts focused and specific for consistency

**3. "Remotely Close" Philosophy**
- Goal is 70-80% accuracy, not 100%
- User can refine template after generation
- Fast iteration > perfect accuracy
- Learn from user refinements to improve algorithm

**4. Integration with Existing Systems**
- Leverage existing template structure and validation
- Use existing file traversal and source handling
- Build on top of v0.5.0 template library foundation

---

## ⚠️ Risks & Mitigation

### Risk 1: Source Discovery Accuracy Too Low
**Risk**: Intelligent source discovery doesn't find relevant files (< 50% accuracy)
**Impact**: Generated templates have wrong sources, regeneration produces bad docs
**Mitigation**:
- Start with pattern matching (high confidence for common cases)
- Add semantic search as enhancement
- Allow user to review/edit sources before regen
- Iterate on algorithm based on test results
- Consider fallback: suggest top-level directories if unsure

### Risk 2: LLM Consistency Issues
**Risk**: LLM produces inconsistent analysis or prompts across runs
**Impact**: Template quality varies, hard to debug
**Mitigation**:
- Use temperature=0 for deterministic results
- Validate LLM outputs with schemas (JSON mode if available)
- Test on same documents repeatedly to ensure consistency
- Add retry logic for invalid LLM responses

### Risk 3: Complexity Creep
**Risk**: Feature takes longer than 10 days due to algorithmic complexity
**Impact**: v0.6.0 delayed, scope needs reduction
**Mitigation**:
- Build iteratively: Parser → Analyzer → Simple Source Discovery → Full Source Discovery
- Set checkpoint at day 5: Evaluate progress, adjust scope if needed
- MVP mindset: Ship "remotely close" not "perfect"
- Can defer advanced source discovery to v0.6.1 if needed

### Risk 4: Edge Cases Break Pipeline
**Risk**: Unusual markdown formats, very large docs, or no relevant sources cause failures
**Impact**: Command fails ungracefully, bad user experience
**Mitigation**:
- Extensive error handling at each pipeline stage
- Graceful degradation (e.g., skip LLM if fails, use defaults)
- Clear error messages with suggested fixes
- Test on diverse document types early

---

## 📅 Timeline & Milestones

### Day 1-2: Foundation
- ✅ Document parser implementation
- ✅ Content analyzer with LLM integration
- ✅ Test on doc-evergreen README

### Day 3-5: Source Discovery (Critical Path)
- ✅ Pattern-based source discovery
- ✅ Semantic search implementation
- ✅ LLM relevance scoring
- ✅ Test accuracy on multiple projects

### Day 6-7: Prompt & Assembly
- ✅ Prompt generation logic
- ✅ Template assembly and validation
- ✅ End-to-end testing

### Day 8-9: CLI & Integration
- ✅ CLI command implementation
- ✅ Error handling and edge cases
- ✅ User feedback and progress display

### Day 10: Polish & Documentation
- ✅ Final testing on real projects
- ✅ Update README with new command
- ✅ Prepare for release

**Checkpoint at Day 5**: Evaluate source discovery accuracy. If < 60%, consider simplified approach or extend timeline.

---

## 🎓 What We'll Learn

1. **Source-Content Relationships**: Which source files actually contribute to which documentation sections?
2. **Template Patterns**: What prompt patterns work best for different section types?
3. **Adoption Enablement**: Does this feature actually remove the barrier for existing projects?
4. **Update Workflow Validation**: Can users now maintain docs with `reverse → regen` workflow?
5. **Algorithm Refinement**: What heuristics work best for source discovery and prompt generation?

---

## 🔗 Related Work

**From Backlog:**
- **DE-tbz [P4]**: "Generate Template FROM Existing Documentation" → This feature!
- **DE-t6l [P2]**: "Smart Source Detection" → Core component of this work
- **DE-2t4 [P1]**: "Prompt Templates Library" → Leveraged for prompt generation
- **DE-b8p [P0]**: "Template Validation" → Used in template assembly

**Enables Future Work:**
- UC2: Update existing documentation workflow
- Selective section regeneration (only update changed sections)
- Template learning and improvement
- Community template generation from popular docs

---

## ✅ Definition of Done

v0.6.0 is complete when:
- ✅ `doc-evergreen template reverse <doc-path>` command works end-to-end
- ✅ Generated templates are 70-80% accurate on test cases
- ✅ Can regenerate doc-evergreen's own README with reasonable results
- ✅ All components are tested and documented
- ✅ README updated with new command usage
- ✅ User can successfully use reverse → regen workflow
- ✅ Edge cases handled gracefully
- ✅ Ready for user testing and feedback

---

**Next Steps After Convergence:**
1. Update beads backlog with v0.6.0 priorities
2. Sprint planning with zen-architect
3. TDD-driven implementation with modular-builder
4. Iterate based on testing with doc-evergreen's own docs
