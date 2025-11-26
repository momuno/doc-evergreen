# Sprint 1: Quick Win + Foundation (Divio Infrastructure)

**Updated:** 2025-11-25 with Divio Documentation System framework

**Duration:** 1 week (5 days)
**Goal:** Remove mode confusion + build Divio-aware infrastructure + deliver 4 templates (one per quadrant)
**Value Delivered:** Users get immediate clarity + understand Divio framework + can choose templates by purpose

---

## Why This Sprint?

**Quick Win First**: Remove single-shot mode confusion immediately - this is a 4-6 hour task that eliminates user frustration right away.

**Foundation for Everything**: Build the Divio quadrant-aware template infrastructure (CLI flags, quadrant organization, template loading, validation) that Sprint 2-4 will build upon.

**Prove the Divio Framework**: Ship 4 working templates (one per Divio quadrant) to validate that the framework works end-to-end:
- 📚 **tutorial-quickstart** (Tutorials - "Teach me")
- 🎯 **howto-contributing-guide** (How-to - "Show me how")
- 📖 **reference-cli** (Reference - "Tell me facts")
- 💡 **explanation-architecture** (Explanation - "Help me understand")

**Educational Value**: Users immediately learn the Divio framework through clear quadrant organization.

---

## Deliverables

### 1. Remove Single-Shot Mode Confusion ✨ Quick Win
**Estimated Lines:** -50 lines (code removal) + ~20 lines tests updated

**What it does:**
Eliminates the non-functional `--mode` flag and related fallback code that confuses users.

**Why this sprint:**
- User explicitly confirmed: "I don't think we'll ever want to do a single prompt"
- Quick win (4-6 hours) that removes immediate pain
- Simplifies codebase before building new features
- Closes 2 issues (DE-5hd, DE-00l)

**Implementation notes:**
- Remove `--mode` flag from CLI argument parser
- Remove single_generator import fallback code
- Update all help text (remove mode references)
- Update tests (remove mode-related tests)
- Close issues with explanation

**Files to modify:**
- `src/doc_evergreen/cli.py` - Remove --mode argument
- `src/doc_evergreen/regen_doc.py` - Remove fallback logic
- `tests/` - Update tests to remove mode testing
- `docs/USER_GUIDE.md` - Remove mode documentation

---

### 2. Template Selection Infrastructure
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
Core infrastructure for template library: CLI flags, template discovery, loading, validation.

**Why this sprint:**
- Foundation for all template features
- Needed before any templates can be added
- Enables Sprint 2 template additions

**Implementation notes:**

**CLI Changes:**
```bash
# New flags to add
doc-evergreen init --list                    # List available templates
doc-evergreen init --template <name>         # Use specific template
doc-evergreen init --yes                     # Non-interactive mode
```

**Template Discovery:**
```python
# Template location convention
# Built-in: src/doc_evergreen/templates/{template-name}.json
# Custom: .doc-evergreen/templates/{template-name}.json (future)

TEMPLATES = {
    "readme-concise": "templates/readme-concise.json",
    "readme-standard": "templates/readme-standard.json",
    "readme-detailed": "templates/readme-detailed.json",
    # Sprint 2 will add: api-docs, architecture, contributing
}
```

**Template Metadata:**
```json
{
  "_meta": {
    "name": "readme-concise",
    "description": "Brief README (300-500 lines)",
    "use_case": "Most projects, quick starts, focused documentation"
  },
  "document": { ... }
}
```

**Files to create:**
- `src/doc_evergreen/templates/` - Template directory
- `src/doc_evergreen/template_registry.py` - Template discovery & loading
- `tests/test_template_registry.py` - Template infrastructure tests

**Files to modify:**
- `src/doc_evergreen/cli.py` - Add --list, --template, --yes flags
- `src/doc_evergreen/init.py` - Update to use template registry

---

### 3. Tutorial Template: Quickstart
**Estimated Lines:** ~80 lines template JSON + 50 lines tests

**What it does:**
Learning-oriented tutorial template (200-400 lines) that teaches users to get started in 5 minutes.

**Why this sprint:**
- Proves the TUTORIALS quadrant of Divio framework
- Beginner-friendly, step-by-step approach
- Most projects need a quickstart tutorial

**Template structure:**
```json
{
  "_meta": {
    "name": "readme-concise",
    "description": "Brief README (300-500 lines)",
    "use_case": "Most projects - quick starts, focused documentation"
  },
  "document": {
    "title": "Project Documentation",
    "output": "README.md",
    "sections": [
      {
        "heading": "# Overview",
        "prompt": "Provide a brief overview (2-3 paragraphs). What does this project do? What problem does it solve? Be concise and focus on core value.",
        "sources": ["README.md", "pyproject.toml"]
      },
      {
        "heading": "## Quick Start",
        "prompt": "Provide minimal quick start (3-4 paragraphs): (1) Prerequisites (Python version), (2) Installation command, (3) Basic usage example. Be brief and actionable. Skip edge cases.",
        "sources": ["README.md", "pyproject.toml"]
      },
      {
        "heading": "## Key Features",
        "prompt": "List 3-5 key features as bullet points. One sentence per feature. Focus on user benefits, not implementation details.",
        "sources": ["README.md", "src/**/*.py"]
      },
      {
        "heading": "## Links",
        "prompt": "Provide relevant links (1 paragraph): Documentation, GitHub, issues. Just the essentials.",
        "sources": ["README.md", "pyproject.toml"]
      }
    ]
  }
}
```

**Key prompt patterns:**
- Explicit length: "2-3 paragraphs", "3-4 paragraphs", "3-5 bullet points"
- Scope limits: "Be brief", "Skip edge cases", "Just the essentials"
- Focus guidance: "core value", "user benefits", "actionable"

**Files to create:**
- `src/doc_evergreen/templates/readme-concise.json`
- `tests/test_readme_concise.py`

---

### 4. How-to Template: Contributing Guide
**Estimated Lines:** ~100 lines template JSON + 50 lines tests

**What it does:**
Goal-oriented how-to template (300-500 lines) for creating contributing guidelines.

**Why this sprint:**
- Proves the HOW-TO GUIDES quadrant of Divio framework
- Practical, recipe-like approach for experienced users
- Common doc type many projects need

**Template structure:**
```json
{
  "_meta": {
    "name": "readme-standard",
    "description": "Standard README (500-700 lines)",
    "use_case": "Balanced detail - installation, usage, development"
  },
  "document": {
    "title": "Project Documentation",
    "output": "README.md",
    "sections": [
      {
        "heading": "# Overview",
        "prompt": "Provide overview (3-4 paragraphs): What this project does, main purpose, key features, target audience. Be clear but concise.",
        "sources": ["README.md", "pyproject.toml", "src/**/*.py"]
      },
      {
        "heading": "## Installation",
        "prompt": "Provide installation instructions (4-6 paragraphs): (1) Prerequisites, (2) Installation command, (3) Configuration if needed, (4) Verification. Focus on common case. Keep edge cases brief.",
        "sources": ["pyproject.toml", "setup.py", "requirements.txt", "README.md"]
      },
      {
        "heading": "## Usage",
        "prompt": "Provide usage examples (5-7 paragraphs): Common use cases with code examples. Show key workflows. Keep examples focused. Avoid exhaustive coverage.",
        "sources": ["README.md", "examples/**", "src/**/cli.py"]
      },
      {
        "heading": "## Development",
        "prompt": "Document development workflow (4-6 paragraphs): Running tests, building, contributing. Be practical and actionable. Link to CONTRIBUTING.md if exists.",
        "sources": ["README.md", "pyproject.toml", "tests/**/*.py", "CONTRIBUTING.md"]
      }
    ]
  }
}
```

**Key improvements over current default:**
- Explicit length guidance in every prompt
- "Focus on common case" to avoid over-documentation
- "Keep X brief" to control scope
- Clear paragraph counts

**Files to create:**
- `src/doc_evergreen/templates/readme-standard.json`
- `tests/test_readme_standard.py`

---

### 5. Reference Template: CLI Reference
**Estimated Lines:** ~120 lines template JSON + 50 lines tests

**What it does:**
Information-oriented reference template (400-600 lines) for documenting CLI commands.

**Why this sprint:**
- Completes README size spectrum (concise/standard/detailed)
- Shows full range of template library approach
- Some projects legitimately need detailed docs

**Template structure:**
```json
{
  "_meta": {
    "name": "readme-detailed",
    "description": "Comprehensive README (800-1000 lines)",
    "use_case": "Detailed documentation - complete guide, API reference included"
  },
  "document": {
    "title": "Project Documentation",
    "output": "README.md",
    "sections": [
      {
        "heading": "# Overview",
        "prompt": "Comprehensive overview (4-6 paragraphs): Purpose, features, architecture overview, target use cases, design philosophy. Be thorough but organized.",
        "sources": ["README.md", "pyproject.toml", "src/**/*.py", "docs/**"]
      },
      {
        "heading": "## Features",
        "prompt": "Detailed feature list (8-12 paragraphs): Group features by category. Explain each with examples. Include both user-facing and technical features.",
        "sources": ["README.md", "src/**/*.py", "docs/**"]
      },
      {
        "heading": "## Installation",
        "prompt": "Comprehensive installation (6-8 paragraphs): Prerequisites with versions, multiple installation methods, configuration options, troubleshooting common issues, verification steps.",
        "sources": ["pyproject.toml", "setup.py", "requirements.txt", "README.md", "docs/**"]
      },
      {
        "heading": "## Usage",
        "prompt": "Detailed usage guide (10-15 paragraphs): Cover basic and advanced use cases. Include comprehensive code examples. Show different workflows. Explain options and flags.",
        "sources": ["README.md", "examples/**", "src/**/*.py", "docs/**"]
      },
      {
        "heading": "## API Reference",
        "prompt": "API overview (6-10 paragraphs): Key classes, functions, methods. Include parameter descriptions and return values. Show usage examples for each. Group by module.",
        "sources": ["src/**/*.py"]
      },
      {
        "heading": "## Development",
        "prompt": "Complete development guide (6-8 paragraphs): Project structure, running tests, building, debugging, contributing guidelines, code style, PR process.",
        "sources": ["README.md", "pyproject.toml", "tests/**", "CONTRIBUTING.md", "docs/**"]
      },
      {
        "heading": "## Contributing",
        "prompt": "Contributing guidelines (4-6 paragraphs): How to contribute, code of conduct, development setup, testing requirements, PR guidelines. Link to CONTRIBUTING.md if exists.",
        "sources": ["CONTRIBUTING.md", "README.md", "tests/**"]
      }
    ]
  }
}
```

**Key differences from standard:**
- More paragraphs per section
- More sections (Features, API Reference, Contributing)
- Broader source selection (includes docs/**)
- "Comprehensive", "detailed", "thorough" guidance

**Files to create:**
- `src/doc_evergreen/templates/readme-detailed.json`
- `tests/test_readme_detailed.py`

---

## What Gets Punted (Deliberately Excluded)

### ❌ Interactive Template Selection
- **Why**: CLI flags sufficient for Sprint 1
- **Reconsider**: Sprint 2 (adds interactive UX)

### ❌ Specialized Templates (api-docs, architecture, contributing)
- **Why**: Focus on README variants first (proves concept)
- **Reconsider**: Sprint 2 (completes library)

### ❌ Template Testing Across Projects
- **Why**: Need all templates first
- **Reconsider**: Sprint 3 (systematic testing)

### ❌ Prompt Refinement Based on Real Results
- **Why**: Start with best-guess prompts, refine in Sprint 3
- **Reconsider**: Sprint 3 (data-driven refinement)

### ❌ Documentation
- **Why**: Focus on working code first
- **Reconsider**: Sprint 4 (comprehensive docs)

---

## Dependencies

**Requires from previous sprints:**
- None (first sprint)

**Provides for future sprints:**
- Template registry infrastructure (Sprint 2 needs this)
- 3 README templates as examples (Sprint 2 follows patterns)
- CLI template flags (Sprint 2 adds to)

---

## Acceptance Criteria

### Must Have

**Mode Removal:**
- ✅ `--mode` flag removed from CLI
- ✅ No import fallback code for single_generator
- ✅ Help text updated (no mode references)
- ✅ All tests updated (no mode tests)
- ✅ Issues DE-5hd and DE-00l closed

**Template Infrastructure:**
- ✅ `--list` flag shows available templates
- ✅ `--template <name>` loads specified template
- ✅ Template registry discovers and loads templates
- ✅ Template validation works (catches malformed templates)
- ✅ Clear error messages for invalid templates

**README Templates:**
- ✅ tutorial-quickstart template exists and works (Tutorials quadrant)
- ✅ howto-contributing-guide template exists and works (How-to quadrant)
- ✅ reference-cli template exists and works (Reference quadrant)
- ✅ explanation-architecture template exists and works (Explanation quadrant)
- ✅ Each template has metadata (name, description, use_case)
- ✅ Each template generates valid README.md

**Testing:**
- ✅ Template registry unit tests pass
- ✅ Each template has basic tests
- ✅ Manual test: Generate docs with each template
- ✅ Test coverage >80% for new code

### Nice to Have (Defer if time constrained)

- ❌ Custom template directory support
- ❌ Template validation warnings (non-blocking)
- ❌ Detailed template comparison in help

---

## Technical Approach

### TDD Approach

Follow red-green-refactor cycle for all features:

**For Mode Removal:**
1. 🔴 Update tests to expect no --mode flag → Fail
2. 🟢 Remove --mode flag from CLI → Pass
3. 🔵 Clean up related code
4. ✅ Commit

**For Template Infrastructure:**
1. 🔴 Write test: template registry loads templates → Fail
2. 🟢 Implement template registry → Pass
3. 🔵 Refactor loading logic
4. ✅ Commit
5. 🔴 Write test: CLI --list shows templates → Fail
6. 🟢 Add --list flag → Pass
7. 🔵 Refactor CLI code
8. ✅ Commit

**For Each Template:**
1. 🔴 Write test: template loads and validates → Fail
2. 🟢 Create template JSON → Pass
3. 🔵 Refactor template structure
4. ✅ Commit
5. 🔴 Write test: template generates valid doc → Fail
6. 🟢 Fix any template issues → Pass
7. ✅ Commit

### Key Decisions

**Decision 1: Template Storage Location**
- **Choice**: Built-in templates in `src/doc_evergreen/templates/`
- **Rationale**: Simple, version-controlled, distributed with package
- **Trade-off**: Custom templates need future support (Sprint 2+)

**Decision 2: Template Metadata Format**
- **Choice**: `_meta` field in template JSON
- **Rationale**: Self-contained, easy to parse, extensible
- **Trade-off**: Slightly verbose but clear

**Decision 3: Default Template**
- **Choice**: No automatic default (require explicit --template)
- **Rationale**: Forces user to think about choice, sets up Sprint 2 interactive mode
- **Trade-off**: Sprint 2 will add smart default

**Decision 4: Prompt Engineering Strategy**
- **Choice**: Start with best-guess length guidance, refine in Sprint 3
- **Rationale**: Get templates working first, data-driven refinement later
- **Trade-off**: May need iteration but that's expected

---

## Testing Requirements

### TDD Approach

**🔴 RED - Write Failing Tests First:**

**Mode Removal Tests:**
```python
def test_no_mode_flag_in_cli():
    # Test that --mode flag no longer exists
    result = runner.invoke(cli, ["regen-doc", "readme", "--mode", "chunked"])
    assert result.exit_code != 0  # Should fail
    assert "mode" not in result.output.lower()
```

**Template Infrastructure Tests:**
```python
def test_template_registry_discovers_templates():
    # Test that registry finds built-in templates
    registry = TemplateRegistry()
    templates = registry.list_templates()
    assert "readme-concise" in templates
    assert "readme-standard" in templates
    assert "readme-detailed" in templates

def test_template_loading():
    # Test that templates load and validate
    registry = TemplateRegistry()
    template = registry.load_template("readme-concise")
    assert template["_meta"]["name"] == "readme-concise"
    assert "document" in template
```

**Template Generation Tests:**
```python
def test_readme_concise_generates_valid_doc():
    # Test that readme-concise template generates valid README
    result = runner.invoke(cli, ["init", "--template", "readme-concise"])
    assert result.exit_code == 0
    assert os.path.exists(".doc-evergreen/readme.json")
    
    # Verify template content
    with open(".doc-evergreen/readme.json") as f:
        template = json.load(f)
    assert template["document"]["sections"][0]["heading"] == "# Overview"
```

**🟢 GREEN - Write Minimal Implementation:**

Implement just enough code to make each test pass.

**🔵 REFACTOR - Improve Code Quality:**

After tests pass:
- Extract common template loading logic
- Clean up CLI argument parsing
- Improve error messages
- Add docstrings

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## Implementation Order

**TDD-driven daily workflow:**

### Day 1: Mode Removal (Quick Win!)
- 🔴 Write tests for no --mode flag
- 🟢 Remove --mode from CLI, remove fallback code
- 🔵 Clean up related code and docs
- ✅ Manual test: Verify `doc-evergreen regen-doc readme` works
- ✅ Commit (all tests green)
- ✅ Close issues DE-5hd and DE-00l

### Day 2: Template Infrastructure (Foundation)
- 🔴 Write tests for template registry
- 🟢 Implement TemplateRegistry class
- 🔵 Refactor for clean API
- ✅ Commit (registry working)
- 🔴 Write tests for CLI --list flag
- 🟢 Add --list to CLI
- 🔵 Refactor CLI code
- ✅ Commit (--list working)
- 🔴 Write tests for CLI --template flag
- 🟢 Add --template to CLI
- 🔵 Refactor template loading
- ✅ Commit (--template working)

### Day 3: README Templates (Part 1)
- 🔴 Write tests for readme-concise
- 🟢 Create readme-concise.json template
- 🔵 Refactor template structure
- ✅ Manual test: Generate doc with readme-concise
- ✅ Commit (concise working)
- 🔴 Write tests for readme-standard
- 🟢 Create readme-standard.json template
- 🔵 Refactor common patterns
- ✅ Manual test: Generate doc with readme-standard
- ✅ Commit (standard working)

### Day 4: README Templates (Part 2) + Integration
- 🔴 Write tests for readme-detailed
- 🟢 Create readme-detailed.json template
- 🔵 Refactor for consistency
- ✅ Manual test: Generate doc with readme-detailed
- ✅ Commit (detailed working)
- 🔴 Write integration tests (all templates)
- 🟢 Fix any integration issues
- 🔵 Polish and refactor
- ✅ Commit (integration solid)

### Day 5: Polish + Manual Testing
- 🔵 Review all code, refactor for quality
- ✅ Manual testing checklist (see below)
- ✅ Test across different projects
- ✅ Fix any bugs found
- ✅ Final commit & sprint review

---

## Manual Testing Checklist

After automated tests pass:

### Mode Removal
- [ ] `doc-evergreen regen-doc readme` works (no --mode needed)
- [ ] `doc-evergreen regen-doc readme --mode chunked` fails with clear error
- [ ] Help text doesn't mention modes: `doc-evergreen regen-doc --help`

### Template Infrastructure
- [ ] `doc-evergreen init --list` shows 3 templates with descriptions
- [ ] `doc-evergreen init --template readme-concise` creates template
- [ ] `doc-evergreen init --template invalid-name` fails with clear error
- [ ] Template files exist in correct location

### README Templates
- [ ] Generate doc with readme-concise: Verify ~300-500 lines (ballpark)
- [ ] Generate doc with readme-standard: Verify ~500-700 lines (ballpark)
- [ ] Generate doc with readme-detailed: Verify ~800+ lines (ballpark)
- [ ] All generated docs are valid markdown
- [ ] Section headings match template structure

### Cross-Project Testing
- [ ] Test on doc-evergreen itself (Python CLI project)
- [ ] Test on different project if available (library, app, etc.)
- [ ] Verify templates adapt to project structure

---

## What You Learn

After this sprint, you'll discover:

1. **Template Infrastructure Complexity**
   - How complex is template discovery and loading?
   - What validation is really needed?
   - → Informs Sprint 2 specialized templates

2. **Prompt Engineering Effectiveness**
   - Do length hints ("2-3 paragraphs") work?
   - Which prompts produce best results?
   - → Informs Sprint 3 systematic refinement

3. **User Workflow Clarity**
   - Is CLI flag approach clear enough?
   - Do users understand template choices?
   - → Motivates Sprint 2 interactive mode

4. **Template Patterns**
   - What's common across all 3 README templates?
   - What's unique to each?
   - → Guides Sprint 2 specialized templates

---

## Success Metrics

### Quantitative
- **Mode removal**: 0 references to single-shot mode in codebase
- **Templates**: 3 README templates working
- **Test coverage**: >80% for new code
- **CLI**: 3 new flags (--list, --template, --yes) working

### Qualitative
- **User clarity**: No mode confusion (removed entirely)
- **Template quality**: Each template generates valid, appropriate-length docs
- **Developer confidence**: Infrastructure feels solid for Sprint 2
- **Code quality**: Clean, testable, well-documented

---

## Known Limitations (By Design)

1. **No interactive mode yet** - CLI flags only
   - Why acceptable: Sprint 2 adds interactive UX
   - Users can still use --template flag

2. **Prompt engineering not yet refined** - Best-guess prompts
   - Why acceptable: Sprint 3 does systematic testing/refinement
   - Templates still work, just may need tuning

3. **No specialized templates yet** - Only README variants
   - Why acceptable: Sprint 2 adds api-docs, architecture, contributing
   - Proves concept before expanding

4. **Length targets are estimates** - Not guaranteed
   - Why acceptable: LLM output varies, prompts guide but don't guarantee
   - Sprint 3 refines based on real results

---

## Next Sprint Preview

After Sprint 1 ships, the most pressing need will be:

**Sprint 2: Complete Template Library**
- Add 3 specialized templates (api-docs, architecture, contributing)
- Build interactive template selection UX
- Make template discovery seamless

**Why Sprint 2 is ready:**
- Sprint 1 infrastructure supports adding more templates easily
- README template patterns inform specialized templates
- User feedback on 3 templates guides remaining 3
- Interactive mode motivated by Sprint 1 CLI-only experience

---

## Sprint 1 Philosophy

**Ship Fast**: Mode removal + 3 templates in 1 week

**Prove Concept**: Template library approach works end-to-end

**Build Foundation**: Infrastructure Sprint 2-4 needs

**Learn and Adapt**: Discoveries inform remaining sprints

**Value First**: Users get immediate value (mode clarity + size choice)

---

**Sprint 1 Mantra**: "Quick win + solid foundation = momentum"
