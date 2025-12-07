# v0.7.0 Feature Scope: generate-doc Command

**Release**: v0.7.0  
**Branch**: dev/loop-7  
**Date**: 2025-12-06  
**Timeline**: 6-7 sprints (~12-14 days)

---

## 🎯 Vision

Enable documentation generation **from scratch** - without existing docs to reverse engineer.

**The Gap:** v0.6.0 solves "update existing docs" (reverse → regen). But what if you have NO docs yet? Manual template creation is tedious, and users don't know what structure/sources/prompts to use.

**The Solution:** `doc-evergreen generate-doc` - analyze project, generate intelligent outline, create documentation. Like writing a research paper from scratch with a structured process.

---

## 🔄 The Complete Flow

Inspired by research paper writing process:

```
Phase 1: Intent Definition
  └─> User specifies doc type (tutorial/howto/reference/explanation) + purpose

Phase 2: Repository Indexing  
  └─> Index all files, create traversable structure

Phase 3: File Review with Context Filter
  └─> For each file: "Is this relevant to my doc purpose?"

Phase 4: Note-Taking on Relevant Files
  └─> Document WHY relevant and WHAT material makes it relevant

Phase 5: Outline Generation ⭐ CORE INNOVATION
  └─> Create hierarchical outline with nesting-aware prompts + sourced reasoning

Phase 6: Document Generation
  └─> Generate content respecting outline structure (structure locked)
```

---

## 📦 Feature Breakdown

### Feature 1: Project Analysis & Context Capture
**Sprints**: 1-2  
**Priority**: Supporting  
**Complexity**: LOW-MEDIUM

**What it delivers:**
- CLI interface for doc type and purpose
  ```bash
  doc-evergreen generate-doc README.md \
    --type tutorial \
    --purpose "Help developers get started in 5 minutes"
  ```
- Repository indexing (file inventory, traversable structure)
- Respects .gitignore/.docignore
- Stores context for downstream features

**Success Criteria:**
- ✅ User can specify Divio doc type (tutorial/howto/reference/explanation)
- ✅ User can describe doc purpose (freeform text)
- ✅ Repo indexer builds complete file inventory
- ✅ Efficient file traversal structure created

**Technical Notes:**
- Reuse: Minimal (some file discovery patterns from v0.6.0)
- New: Intent capture CLI, full repo indexing
- Storage: .doc-evergreen/context.json for intent + file index

---

### Feature 2: Intelligent File Relevance Analysis
**Sprints**: 3  
**Priority**: Supporting  
**Complexity**: MEDIUM-HIGH

**What it delivers:**
- Context-aware file relevance analysis (LLM-powered)
- For each file: analyze against doc purpose
- Document WHY relevant and WHAT material
- Output: Annotated file list with reasoning notes

**Example Process:**
```python
intent = "tutorial for getting developers started quickly"
doc_type = "tutorial"

for file in repo_index:
    analysis = analyze_relevance(file, intent, doc_type)
    # Returns:
    # {
    #   "relevant": True/False,
    #   "reasoning": "Contains main CLI entry point, needed for usage examples",
    #   "key_material": "Command definitions, argument parsing, help text"
    # }
```

**Success Criteria:**
- ✅ Analyzes all files against doc purpose
- ✅ Identifies 70-80% of truly relevant files
- ✅ Generates reasoning per relevant file
- ✅ Creates high-level notes (not detailed summaries)

**Technical Notes:**
- Reuse: Conceptual patterns from v0.6.0 (LLM file analysis, relevance scoring)
- New: Context-aware holistic analysis (different from per-section discovery)
- Different from v0.6.0: Analyzes for DOC PURPOSE, not specific section
- Storage: .doc-evergreen/relevance_notes.json

---

### Feature 3: Hierarchical Outline Generation ⭐
**Sprints**: 4-5 (PRIMARY FOCUS)  
**Priority**: 🌟 PRIMARY - THE CORE INNOVATION  
**Complexity**: HIGH

**What it delivers:**
- Generate nested outline from doc purpose + relevant file notes
- Deep nesting support (H1-H6, TOC-style: 1, A, i, ii, B, i, iii, 2, etc.)
- Each section has:
  1. Heading/title
  2. **Nesting-aware prompt** (ONLY for content at this level, NOT subsections)
  3. Sources with reasoning (why this source for this section)
- Parent sections: general/introductory (don't cover subsection topics)
- Child sections: specific/detailed (the meat)

**Critical Rule:** Subsections can ONLY be defined by outline. LLM generating content CANNOT create new subsections. Strict separation: outline defines structure, generation fills content.

**Example Output:**
```json
{
  "_meta": {
    "generation_method": "forward",
    "doc_type": "tutorial",
    "user_intent": "Help developers get started in 5 minutes"
  },
  "document": {
    "title": "Getting Started",
    "output": "README.md",
    "sections": [
      {
        "heading": "# Getting Started",
        "level": 1,
        "prompt": "Write welcoming intro (2-3 paragraphs) explaining what this tool does and why it's useful. Don't cover installation or usage details - those are in subsections below.",
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
            "prompt": "Provide step-by-step installation instructions. Include prerequisites, installation command, and verification step. Be specific and complete.",
            "sources": [
              {
                "file": "pyproject.toml",
                "reasoning": "Defines package dependencies and installation method"
              },
              {
                "file": "README.md",
                "reasoning": "May contain existing installation notes"
              }
            ],
            "sections": []
          },
          {
            "heading": "## Your First Command",
            "level": 2,
            "prompt": "Walk through the simplest possible command. Show the command, expected output, and explain what happened. Be encouraging and beginner-friendly.",
            "sources": [
              {
                "file": "src/cli.py",
                "reasoning": "Contains CLI command definitions and help text"
              },
              {
                "file": "examples/basic.py",
                "reasoning": "Shows simple usage example"
              }
            ],
            "sections": []
          }
        ]
      }
    ]
  }
}
```

**Success Criteria:**
- ✅ **80%+ outline quality** - structure feels right on first try
- ✅ Appropriate sections for doc type (tutorial vs reference vs howto)
- ✅ Nesting-aware prompts (parents don't duplicate children's content)
- ✅ Sources mapped to sections with reasoning
- ✅ Deep nesting support (H1-H6, arbitrary depth)
- ✅ Template format includes source reasoning

**Technical Notes:**
- Reuse: Prompt generation concepts from v0.6.0 (heavy adaptation needed)
- New: Hierarchical structure inference, nesting-aware prompt generation
- **This is THE differentiating innovation of v0.7.0!** 🌟
- LLM orchestration: Sophisticated prompt engineering required
- Quality gate: This feature must be excellent (not just "good enough")

**Prompting Strategy:**
- Higher level sections (parents): More general, introductory, don't cover what subsections will cover
- Deeper nested sections (children): More specific, detailed meat
- LLM determines best prompts based on: doc type, relevant source notes, nesting level

---

### Feature 4: Nesting-Aware Document Generation
**Sprints**: 6  
**Priority**: Completion  
**Complexity**: MEDIUM

**What it delivers:**
- Generate content respecting outline structure
- Top-down DFS traversal (simpler than bottom-up)
- LLM CANNOT create subsections during generation (structure locked)
- Context injection: "Don't cover X, that's in subsection Y"

**Generation Algorithm:**
```python
def generate_section(section, outline_context):
    """
    outline_context = what parent/sibling sections exist
    Ensures prompts can reference: "don't cover X, that's in subsection Y"
    """
    
    # Generate content ONLY for this level
    prompt = section.prompt
    
    if section.sections:
        # Add context about subsections
        subsection_headings = [s.heading for s in section.sections]
        prompt += f"""
        
        IMPORTANT: This section has {len(section.sections)} subsections.
        Do NOT generate content for these subsections - they will be generated separately:
        {subsection_headings}
        
        Your content should introduce this topic but leave details to subsections.
        """
    
    content = llm_generate(prompt, section.sources)
    
    # Recursively generate subsections
    for subsection in section.sections:
        subsection_content = generate_section(subsection, outline_context)
        content += "\n\n" + subsection_content
    
    return content
```

**Success Criteria:**
- ✅ Generates content for each section
- ✅ Respects nesting (parents don't duplicate children)
- ✅ Top-down DFS works correctly
- ✅ Full document assembled properly
- ✅ Reasonable quality (doesn't need perfection - focus is on Feature 3)

**Technical Notes:**
- Reuse: Chunked generator from v0.6.0 (adapt for nesting awareness)
- New: Nesting-aware context injection, hierarchical traversal
- Defer: Bottom-up generation (more complex, not needed for MVP)
- Storage: Generated doc written to specified output path

**Two Possible Approaches:**
- **Top-down DFS** (simpler, use for v0.7.0): Generate from root to leaves
- **Bottom-up** (more complex, defer): Generate deepest sections first, parents have context

---

### Feature 5: Outline Review & Iteration Workflow
**Sprints**: 7 (or integrated throughout)  
**Priority**: Workflow  
**Complexity**: LOW

**What it delivers:**
- User can review generated outline before doc generation
- Edit outline.json (add/remove sections, adjust prompts/sources)
- Two-command workflow OR single command with review step

**CLI Design Options:**

**Option A: Two Explicit Commands**
```bash
# Step 1: Generate outline
$ doc-evergreen generate-outline README.md --type tutorial --purpose "..."

📝 Generated outline saved to .doc-evergreen/outline.json

Review and edit outline, then run:
  doc-evergreen generate-from-outline .doc-evergreen/outline.json

# User manually edits .doc-evergreen/outline.json

# Step 2: Generate doc from outline
$ doc-evergreen generate-from-outline .doc-evergreen/outline.json

✨ Generating documentation...
✅ README.md created (450 lines)
```

**Option B: Single Interactive Command**
```bash
$ doc-evergreen generate-doc README.md --type tutorial --purpose "..."

🔍 Analyzing project...
📝 Generating outline...

Generated outline (5 sections):
  1. # Getting Started
     1.1. ## Installation
     1.2. ## Your First Command
  2. # Advanced Usage
     2.1. ## Configuration
  
Review outline? [e]dit / [a]ccept / [r]egenerate: e

[Opens $EDITOR with .doc-evergreen/outline.json]

# User edits, saves, closes editor

Generate document from this outline? [Y/n]: y

✨ Generating documentation...
✅ README.md created
```

**Option C: Dry-Run Flag**
```bash
$ doc-evergreen generate-doc README.md --type tutorial --dry-run

📝 Generated outline saved to .doc-evergreen/outline.json
(Stopping before document generation)

# User edits outline.json

$ doc-evergreen generate-doc README.md --from-outline .doc-evergreen/outline.json

✨ Generating documentation...
✅ README.md created
```

**Success Criteria:**
- ✅ User can review outline before generation
- ✅ Can edit outline.json manually
- ✅ Can regenerate doc from edited outline
- ✅ Simple workflow (minimal ceremony)
- ✅ Clear separation between outline generation and doc generation

**Technical Notes:**
- Reuse: Regen logic from v0.6.0 for generation step
- New: Outline generation as separate step, editor integration
- Decision: Pick one CLI design (recommend Option A for simplicity)

---

## 📊 Sprint Allocation

| Sprint | Feature(s) | Focus | Days |
|--------|-----------|-------|------|
| 1 | F1: Intent Capture | Foundation | 1-2 |
| 2 | F1: Repo Indexing | Foundation | 1-2 |
| 3 | F2: Relevance Analysis | Supporting | 2 |
| 4 | F3: Outline Generation (Core) | 🌟 PRIMARY | 2-3 |
| 5 | F3: Outline Generation (Polish) | 🌟 PRIMARY | 2-3 |
| 6 | F4: Doc Generation | Completion | 2 |
| 7 | F5: Review Workflow | Polish | 1-2 |

**Total: 6-7 sprints (~12-14 days of focused work)**

---

## ✅ Success Metrics

**Quantitative:**
- 80%+ outline quality (structure feels right first try)
- 70-80% file relevance accuracy
- Full end-to-end pipeline works

**Qualitative:**
- "I can generate a doc from scratch and it's 80% right"
- "The outline is so good I barely need to edit it"
- "This is easier than manually creating templates"
- "Outline generation feels intelligent and context-aware"

**Demo Moment:**
```bash
$ cd new-python-cli-project  # Project has NO existing docs!

$ doc-evergreen generate-doc README.md \
    --type tutorial \
    --purpose "Help developers get started in 5 minutes"

🔍 Analyzing project...
   - Detected: Python CLI tool
   - Found: 23 source files
   - Identified 8 relevant files
   
📝 Generating outline...
   - 5 main sections
   - 12 subsections
   - 8 sources mapped with reasoning
   
✨ Generating documentation...
   [Progress for each section]
   
✅ README.md created (450 lines)
💡 Outline saved to .doc-evergreen/outline.json (for future refinement)
```

---

## 🔄 What's Reusable from v0.6.0?

**High Reuse (Adapt):**
- ✅ `chunked_generator.py` - Content generation (adapt for nesting awareness)
- ✅ `template_schema.py` - Template format (extend with source reasoning, level)
- ✅ LLM patterns from `reverse/` - Prompt engineering approaches

**Medium Reuse (Conceptual):**
- 🔄 `intelligent_source_discoverer.py` - File relevance analysis (adapt for context-aware)
- 🔄 `prompt_generator.py` - Prompt creation (make nesting-aware)
- 🔄 `semantic_source_searcher.py` - Source discovery patterns

**New Components (Build Fresh):**
- 🆕 Repo indexer (file inventory, traversal)
- 🆕 Context-aware relevance analyzer (with note-taking)
- 🆕 Hierarchical outline generator (THE CORE INNOVATION!)
- 🆕 Nesting-aware generation orchestrator

---

## 📝 Template Format Changes

**Extended Schema:**

```python
@dataclass
class SourceWithReasoning:
    """Source file with reasoning for inclusion."""
    file: str                # File path/pattern
    reasoning: str           # Why this source is relevant to this section

@dataclass
class Section:
    """Section within a document template."""
    heading: str             # Section heading (e.g., "## Installation")
    level: int              # NEW: Explicit heading level (1-6)
    prompt: str | None       # Instructions for LLM (nesting-aware)
    sources: list[SourceWithReasoning]  # CHANGED: Now includes reasoning
    sections: list["Section"]  # Nested subsections

@dataclass
class TemplateMetadata:
    """Template metadata."""
    name: str
    description: str
    use_case: str
    quadrant: str
    estimated_lines: str
    generation_method: str   # NEW: "forward" or "reverse"
    doc_type: str | None     # NEW: User-specified doc type
    user_intent: str | None  # NEW: User-specified purpose
```

**JSON Example:**
```json
{
  "_meta": {
    "name": "generated-tutorial-2025-12-06",
    "description": "Auto-generated tutorial for getting started",
    "use_case": "Help developers get started in 5 minutes",
    "quadrant": "tutorial",
    "estimated_lines": "400-600 lines",
    "generation_method": "forward",
    "doc_type": "tutorial",
    "user_intent": "Help developers get started in 5 minutes"
  },
  "document": {
    "title": "Getting Started",
    "output": "README.md",
    "sections": [
      {
        "heading": "## Installation",
        "level": 2,
        "prompt": "Step-by-step installation instructions...",
        "sources": [
          {
            "file": "pyproject.toml",
            "reasoning": "Defines package dependencies and installation method"
          }
        ],
        "sections": []
      }
    ]
  }
}
```

**Backward Compatibility:**
- Old templates (v0.6.0): `sources: ["file.py"]` still work
- New templates (v0.7.0): `sources: [{file: "file.py", reasoning: "..."}]`
- Parser supports both formats

---

## 🚫 What's Deferred (Not in v0.7.0)

### From Original "Complete Workflow" Ideas:
- Change detection / staleness awareness → v0.8.0?
- Selective section regeneration → v0.8.0?
- Git integration / CI/CD automation → v0.8.0?
- Watch mode / continuous docs → v0.8.0?

**Rationale:** v0.7.0 focuses on "generate from scratch" problem. The "update workflow" ideas from original convergence are valuable but orthogonal. They can build on v0.7.0's foundation later.

### From Generate-Doc Scope:
- Bottom-up generation (deepest sections first) → Defer, use top-down DFS
- Advanced relevance ML models → Start with LLM-based analysis
- Multi-document generation → Single doc first
- Template learning/improvement → Static generation first

---

## 🎯 Why This Matters

**v0.6.0 Solved:** "I have outdated docs" → reverse → regen → updated docs

**v0.7.0 Solves:** "I have NO docs" → generate-doc → outline → new docs

**Together they cover:**
1. **New projects** (v0.7.0): Generate docs from scratch
2. **Existing projects** (v0.6.0): Update/maintain docs

**The Innovation:** Hierarchical outline generation with nesting-aware prompts. This is what makes doc-evergreen intelligent about structure, not just content.

---

## 📋 Definition of Done (v0.7.0)

- ✅ `doc-evergreen generate-doc <output> --type <type> --purpose <purpose>` works end-to-end
- ✅ Outline generation achieves 80%+ quality on test cases
- ✅ Can generate doc-evergreen's own docs from scratch (dogfood test)
- ✅ All features tested with >80% coverage
- ✅ README updated with generate-doc command usage
- ✅ User can review/edit outline before generation
- ✅ Template format supports both forward and reverse generation
- ✅ Edge cases handled gracefully (empty sections, no relevant sources, etc.)
- ✅ Ready for user testing and feedback

---

**Next Steps:**
1. Create DEFERRED_FEATURES.md for items not in v0.7.0 scope
2. Create CONVERGENCE_COMPLETE.md summarizing the session
3. Begin Sprint 1: Intent Capture & Repo Indexing 🚀
