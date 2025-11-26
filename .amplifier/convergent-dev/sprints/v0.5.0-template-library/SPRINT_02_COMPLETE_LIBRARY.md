# Sprint 2: Complete Template Library

**Duration:** 1 week (5 days)
**Goal:** Full template coverage for all common documentation types
**Value Delivered:** Users have 6 complete templates + interactive UX for easy selection

---

## Why This Sprint?

**Complete Divio Coverage**: Expand each of the 4 Divio quadrants with additional templates. Sprint 1 proved each quadrant works; Sprint 2 provides depth and variety.

**Improve Discovery**: Interactive mode with quadrant-organized menu makes template selection obvious and guided. Users understand which quadrant matches their needs.

**Build on Solid Foundation**: Sprint 1's Divio-aware infrastructure makes adding templates fast. Focus is on template design and quadrant characteristics, not plumbing.

**User-Facing Completeness**: After this sprint, the template library is feature-complete from a user perspective with 9 templates across all 4 Divio quadrants. Sprint 3 focuses on quality, not quantity.

---

## Deliverables

### 1. Template: Tutorial - First Template
**Estimated Lines:** ~80 lines template JSON + 50 lines tests

**What it does:**
Learning-oriented tutorial (300-500 lines) that teaches users to create their first doc template hands-on.

**Why this sprint:**
- Expands TUTORIALS quadrant (Sprint 1 had tutorial-quickstart)
- Teaches the tool itself through doing
- Meta: documentation about creating documentation
- Different structure than README (technical reference)
- Shows template library handles diverse doc types

**Template structure:**
```json
{
  "_meta": {
    "name": "api-docs",
    "description": "API documentation (500-700 lines)",
    "use_case": "Technical reference - classes, functions, endpoints, examples"
  },
  "document": {
    "title": "API Documentation",
    "output": "API.md",
    "sections": [
      {
        "heading": "# API Overview",
        "prompt": "Provide API overview (3-4 paragraphs): Purpose, authentication if applicable, base patterns, versioning. Be technical but clear.",
        "sources": ["README.md", "src/**/*.py", "docs/**"]
      },
      {
        "heading": "## Core Classes",
        "prompt": "Document main classes (8-12 paragraphs): Purpose, key methods, parameters, return values, usage examples. One section per major class. Be thorough but organized.",
        "sources": ["src/**/*.py"]
      },
      {
        "heading": "## Functions",
        "prompt": "Document utility functions (4-6 paragraphs): Group by module. Include parameters, return values, examples. Focus on public API.",
        "sources": ["src/**/*.py"]
      },
      {
        "heading": "## Examples",
        "prompt": "Provide comprehensive examples (6-8 paragraphs): Common use cases, code samples, expected output. Show real-world scenarios.",
        "sources": ["examples/**", "tests/**/*.py", "README.md"]
      },
      {
        "heading": "## Error Handling",
        "prompt": "Document errors and exceptions (3-4 paragraphs): Common errors, exception types, handling strategies, troubleshooting.",
        "sources": ["src/**/*.py", "tests/**/*.py"]
      }
    ]
  }
}
```

**Key design decisions:**
- Output to `API.md` (not README.md)
- Heavy focus on source code (`src/**/*.py`)
- Technical reference style (parameters, return values)
- Examples from tests and examples/ directories

**Files to create:**
- `src/doc_evergreen/templates/api-docs.json`
- `tests/test_api_docs.py`

---

### 2. Template: Architecture Documentation
**Estimated Lines:** ~90 lines template JSON + 50 lines tests

**What it does:**
Generate high-level architecture and design documentation focused on system design, decisions, and component interactions.

**Why this sprint:**
- Important for understanding project structure
- Different focus than code (design decisions, not implementation)
- Shows template library handles conceptual docs

**Template structure:**
```json
{
  "_meta": {
    "name": "architecture",
    "description": "Architecture documentation (400-600 lines)",
    "use_case": "Design documentation - overview, decisions, components, data flow"
  },
  "document": {
    "title": "Architecture Documentation",
    "output": "ARCHITECTURE.md",
    "sections": [
      {
        "heading": "# Overview",
        "prompt": "Architectural overview (3-4 paragraphs): High-level design, key principles, technology choices. Focus on 'why' not 'how'.",
        "sources": ["README.md", "pyproject.toml", "docs/**"]
      },
      {
        "heading": "## Design Decisions",
        "prompt": "Document key design decisions (6-8 paragraphs): Why certain approaches chosen, trade-offs considered, alternatives rejected. Be thoughtful and explanatory.",
        "sources": ["README.md", "docs/**", "src/**/*.py"]
      },
      {
        "heading": "## Component Architecture",
        "prompt": "Component breakdown (5-7 paragraphs): Major components, responsibilities, interactions. Show structure without excessive detail. Include diagrams if described in sources.",
        "sources": ["src/**/*.py", "README.md", "docs/**"]
      },
      {
        "heading": "## Data Flow",
        "prompt": "Data flow patterns (4-6 paragraphs): How data moves through system, transformations, key workflows. Use examples to illustrate.",
        "sources": ["src/**/*.py", "docs/**"]
      },
      {
        "heading": "## Future Considerations",
        "prompt": "Future architecture notes (2-3 paragraphs): Known limitations, planned improvements, scalability considerations. Be brief.",
        "sources": ["README.md", "docs/**", "TODO.md", "ROADMAP.md"]
      }
    ]
  }
}
```

**Key design decisions:**
- Output to `ARCHITECTURE.md`
- Focus on design rationale ("why")
- Broader sources (includes docs/, README, even TODO/ROADMAP)
- High-level, conceptual (not code-level detail)

**Files to create:**
- `src/doc_evergreen/templates/architecture.json`
- `tests/test_architecture.py`

---

### 3. Template: Contributing Guidelines
**Estimated Lines:** ~80 lines template JSON + 50 lines tests

**What it does:**
Generate contributing guidelines focused on developer onboarding, setup, code style, and PR process.

**Why this sprint:**
- Essential for open source projects
- Different audience (contributors, not users)
- Shows template library handles process docs

**Template structure:**
```json
{
  "_meta": {
    "name": "contributing",
    "description": "Contributing guidelines (300-500 lines)",
    "use_case": "Contributor onboarding - setup, code style, PR process"
  },
  "document": {
    "title": "Contributing Guidelines",
    "output": "CONTRIBUTING.md",
    "sections": [
      {
        "heading": "# Getting Started",
        "prompt": "Onboarding for contributors (3-4 paragraphs): How to start contributing, what to expect, where to ask questions. Be welcoming and clear.",
        "sources": ["README.md", "CONTRIBUTING.md", "docs/**"]
      },
      {
        "heading": "## Development Setup",
        "prompt": "Development environment setup (4-6 paragraphs): Prerequisites, installation for development, running tests, building locally. Be step-by-step and actionable.",
        "sources": ["README.md", "pyproject.toml", "Makefile", "package.json", "tests/**"]
      },
      {
        "heading": "## Code Style",
        "prompt": "Code standards (3-5 paragraphs): Coding conventions, formatting rules, linting, testing requirements. Reference tools used (black, ruff, etc.).",
        "sources": ["pyproject.toml", ".pre-commit-config.yaml", "tox.ini", "setup.cfg"]
      },
      {
        "heading": "## Pull Request Process",
        "prompt": "PR workflow (4-6 paragraphs): How to submit PRs, what to include, review process, merge criteria. Be clear about expectations.",
        "sources": ["CONTRIBUTING.md", "README.md", ".github/**"]
      },
      {
        "heading": "## Testing",
        "prompt": "Testing guidelines (3-4 paragraphs): How to write tests, running test suite, coverage expectations. Be practical.",
        "sources": ["tests/**/*.py", "pyproject.toml", "tox.ini"]
      }
    ]
  }
}
```

**Key design decisions:**
- Output to `CONTRIBUTING.md`
- Focus on contributor workflow
- Includes config files (.pre-commit, pyproject.toml)
- Welcoming, actionable tone

**Files to create:**
- `src/doc_evergreen/templates/contributing.json`
- `tests/test_contributing.py`

---

### 6. Interactive Divio-Organized Template Selection UX
**Estimated Lines:** ~100 lines + 80 lines tests

**What it does:**
Interactive CLI prompts guide users to appropriate template when running `init` without flags.

**Why this sprint:**
- Major UX improvement (no need to know template names)
- Discoverable (users see all options)
- Educational (descriptions help users learn)

**User experience:**
```bash
# Interactive mode (new default)
$ doc-evergreen init

? What type of documentation do you want to create?
  1. Brief README (recommended for most projects)
     → Quick start, focused, 300-500 lines
  
  2. Standard README (balanced detail)
     → Installation, usage, development, 500-700 lines
  
  3. Detailed README (comprehensive)
     → Full guide with API reference, 800-1000 lines
  
  4. API Documentation
     → Technical reference for classes and functions
  
  5. Architecture Documentation
     → Design decisions and component structure
  
  6. Contributing Guidelines
     → Developer onboarding and PR process
  
Choose [1-6] or 'q' to quit: 1

✓ Created .doc-evergreen/readme.json (readme-concise template)

Next steps:
  1. Review .doc-evergreen/readme.json
  2. Run: doc-evergreen regen-doc readme
```

**Implementation approach:**
```python
# Use click.prompt or inquirer for interactivity
import click

def interactive_template_selection():
    """Guide user through template selection."""
    templates = registry.list_templates_with_metadata()
    
    # Show numbered list
    click.echo("\n? What type of documentation do you want to create?\n")
    for i, (name, meta) in enumerate(templates.items(), 1):
        click.echo(f"  {i}. {meta['description']}")
        click.echo(f"     → {meta['use_case']}\n")
    
    # Get user choice
    choice = click.prompt(
        "Choose [1-6] or 'q' to quit",
        type=click.Choice([str(i) for i in range(1, 7)] + ['q'])
    )
    
    if choice == 'q':
        click.echo("Cancelled.")
        return None
    
    # Return selected template name
    template_names = list(templates.keys())
    return template_names[int(choice) - 1]
```

**CLI behavior:**
```bash
# Interactive (new default)
doc-evergreen init  # Shows menu

# Non-interactive (existing)
doc-evergreen init --template readme-concise  # Direct

# Non-interactive with default
doc-evergreen init --yes  # Uses readme-concise (sensible default)

# List templates
doc-evergreen init --list  # Shows all with descriptions
```

**Files to modify:**
- `src/doc_evergreen/cli.py` - Add interactive mode
- `src/doc_evergreen/init.py` - Integrate interactive selection
- `tests/test_interactive.py` - Test interactive flow

---

### 5. Template Guidance and Help Text
**Estimated Lines:** ~50 lines + improvements to help text

**What it does:**
Improve help text, add guidance on template selection, make discovery seamless.

**Why this sprint:**
- Makes template library discoverable
- Educates users on when to use each template
- Completes user-facing polish

**Improvements:**

**Enhanced `--list` output:**
```bash
$ doc-evergreen init --list

Available templates:

README Templates:
  readme-concise     Brief README (300-500 lines)
                     → Recommended for most projects
                     → Quick start, key features, links
  
  readme-standard    Standard README (500-700 lines)
                     → Balanced detail
                     → Installation, usage, development
  
  readme-detailed    Detailed README (800-1000 lines)
                     → Comprehensive documentation
                     → Full guide with API reference

Specialized Templates:
  api-docs          API Documentation (500-700 lines)
                     → Technical reference
                     → Classes, functions, examples
  
  architecture      Architecture Documentation (400-600 lines)
                     → Design and structure
                     → Decisions, components, data flow
  
  contributing      Contributing Guidelines (300-500 lines)
                     → Developer onboarding
                     → Setup, code style, PR process

Tip: Run 'doc-evergreen init' without flags for interactive selection.
```

**Enhanced help text:**
```bash
$ doc-evergreen init --help

Usage: doc-evergreen init [OPTIONS]

  Initialize a new documentation template.

  By default, opens interactive mode to guide template selection.
  Use --template to directly specify a template.

Options:
  --template TEXT  Template name (see --list for options)
  --list           Show all available templates with descriptions
  --yes            Non-interactive mode (uses readme-concise default)
  --help           Show this message and exit.

Examples:
  doc-evergreen init                        # Interactive selection
  doc-evergreen init --template api-docs    # Direct selection
  doc-evergreen init --list                 # Show all templates
  doc-evergreen init --yes                  # Quick start (readme-concise)
```

**Files to modify:**
- `src/doc_evergreen/cli.py` - Enhanced help text
- `src/doc_evergreen/template_registry.py` - Better --list formatting

---

## What Gets Punted (Deliberately Excluded)

### ❌ Custom Template Directories
- **Why**: Built-in templates sufficient for now
- **Reconsider**: v0.6.0+ if users request custom template sharing

### ❌ Template Validation Warnings
- **Why**: Templates work or they don't (validation is pass/fail)
- **Reconsider**: Sprint 3 if issues arise during testing

### ❌ Template Testing Across Multiple Projects
- **Why**: Need all templates first
- **Reconsider**: Sprint 3 (systematic cross-project testing)

### ❌ Prompt Refinement
- **Why**: Start with best-guess prompts
- **Reconsider**: Sprint 3 (data-driven refinement)

### ❌ Template Preview/Dry Run
- **Why**: Users can review template JSON directly
- **Reconsider**: Future if users request preview feature

---

## Dependencies

**Requires from previous sprints:**
- Sprint 1: Template registry infrastructure
- Sprint 1: CLI --template and --list flags
- Sprint 1: README templates as pattern examples

**Provides for future sprints:**
- Complete template library (Sprint 3 tests all 6)
- Interactive UX patterns (could extend in future)
- Template metadata patterns (standard for all templates)

---

## Acceptance Criteria

### Must Have

**Specialized Templates:**
- ✅ api-docs template exists and generates valid API.md
- ✅ architecture template exists and generates valid ARCHITECTURE.md
- ✅ contributing template exists and generates valid CONTRIBUTING.md
- ✅ Each specialized template has metadata
- ✅ Each specialized template tested (unit tests)

**Interactive UX:**
- ✅ `init` without args enters interactive mode
- ✅ Interactive mode shows all 6 templates with descriptions
- ✅ User can select template by number
- ✅ User can quit interactive mode ('q')
- ✅ Selected template loads correctly
- ✅ Success message shows next steps

**Non-Interactive Support:**
- ✅ `--template <name>` still works (backward compatible)
- ✅ `--list` shows enhanced output with grouping
- ✅ `--yes` uses sensible default (readme-concise)
- ✅ Help text improved and informative

**Testing:**
- ✅ All 3 new templates have unit tests
- ✅ Interactive mode tested (simulated input)
- ✅ Manual test: Generate docs with each new template
- ✅ Test coverage >80% for new code

### Nice to Have (Defer if time constrained)

- ❌ Template search/filter (only 6 templates, not needed)
- ❌ Template preview before generation
- ❌ Template recommendations based on project structure

---

## Technical Approach

### TDD Approach

Follow red-green-refactor cycle for all features:

**For Each Specialized Template:**
1. 🔴 Write test: template loads and validates → Fail
2. 🟢 Create template JSON → Pass
3. 🔵 Refactor template structure for consistency
4. ✅ Commit
5. 🔴 Write test: template generates valid doc → Fail
6. 🟢 Test with real project, fix issues → Pass
7. 🔵 Polish prompts
8. ✅ Commit

**For Interactive UX:**
1. 🔴 Write test: interactive mode shows menu → Fail
2. 🟢 Implement menu display → Pass
3. 🔵 Refactor display logic
4. ✅ Commit
5. 🔴 Write test: user selection loads template → Fail
6. 🟢 Implement selection logic → Pass
7. 🔵 Refactor, add error handling
8. ✅ Commit

### Key Decisions

**Decision 1: Template Organization**
- **Choice**: Group templates by type (README, Specialized) in --list
- **Rationale**: Makes navigation easier with 6 templates
- **Trade-off**: Fixed grouping (but extensible)

**Decision 2: Interactive Library**
- **Choice**: Use click.prompt (built-in, simple)
- **Rationale**: No new dependencies, integrates with click CLI
- **Trade-off**: Less fancy than inquirer but adequate

**Decision 3: Default Template**
- **Choice**: readme-concise for --yes flag
- **Rationale**: Most common use case, appropriate for most projects
- **Trade-off**: Not comprehensive but that's intentional

**Decision 4: Template Output Files**
- **Choice**: Different output files per template type
  - README templates → README.md
  - API template → API.md
  - Architecture template → ARCHITECTURE.md
  - Contributing template → CONTRIBUTING.md
- **Rationale**: Standard file names for each doc type
- **Trade-off**: Fixed naming (but conventional)

---

## Testing Requirements

### TDD Approach

**🔴 RED - Write Failing Tests First:**

**Specialized Template Tests:**
```python
def test_api_docs_template_exists():
    registry = TemplateRegistry()
    template = registry.load_template("api-docs")
    assert template["_meta"]["name"] == "api-docs"
    assert template["document"]["output"] == "API.md"

def test_api_docs_generates_valid_doc():
    result = runner.invoke(cli, ["init", "--template", "api-docs"])
    assert result.exit_code == 0
    assert os.path.exists(".doc-evergreen/api-docs.json")

# Similar tests for architecture and contributing
```

**Interactive UX Tests:**
```python
def test_interactive_mode_shows_menu():
    result = runner.invoke(cli, ["init"], input="q\n")
    assert "What type of documentation" in result.output
    assert "readme-concise" in result.output
    assert "api-docs" in result.output

def test_interactive_mode_selection():
    # Simulate user selecting option 1 (readme-concise)
    result = runner.invoke(cli, ["init"], input="1\n")
    assert result.exit_code == 0
    assert "readme-concise template" in result.output
    assert os.path.exists(".doc-evergreen/readme.json")

def test_interactive_mode_quit():
    result = runner.invoke(cli, ["init"], input="q\n")
    assert "Cancelled" in result.output
    assert result.exit_code == 0
```

**Enhanced Help Tests:**
```python
def test_list_shows_grouped_templates():
    result = runner.invoke(cli, ["init", "--list"])
    assert "README Templates:" in result.output
    assert "Specialized Templates:" in result.output
    assert "readme-concise" in result.output
    assert "api-docs" in result.output
```

**🟢 GREEN - Write Minimal Implementation:**

Implement just enough to make tests pass.

**🔵 REFACTOR - Improve Code Quality:**

After tests pass:
- Extract common template patterns
- Clean up interactive mode logic
- Improve error handling
- Add helpful messages

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each template is complete and tested
- Commit after interactive UX is working
- All commits have passing tests

---

## Implementation Order

**TDD-driven daily workflow:**

### Day 1: API Documentation Template
- 🔴 Write tests for api-docs template
- 🟢 Create api-docs.json template
- 🔵 Refactor, ensure consistency with README templates
- ✅ Manual test: Generate API.md for doc-evergreen
- ✅ Review output, refine prompts
- ✅ Commit (api-docs complete)

### Day 2: Architecture + Contributing Templates
- 🔴 Write tests for architecture template
- 🟢 Create architecture.json template
- 🔵 Refactor and polish
- ✅ Manual test: Generate ARCHITECTURE.md
- ✅ Commit (architecture complete)
- 🔴 Write tests for contributing template
- 🟢 Create contributing.json template
- 🔵 Refactor and polish
- ✅ Manual test: Generate CONTRIBUTING.md
- ✅ Commit (contributing complete)

### Day 3: Interactive UX (Part 1)
- 🔴 Write tests for interactive menu display
- 🟢 Implement interactive_template_selection()
- 🔵 Refactor display logic
- ✅ Commit (menu display working)
- 🔴 Write tests for user selection handling
- 🟢 Implement selection logic
- 🔵 Add error handling, polish UX
- ✅ Commit (selection working)

### Day 4: Interactive UX (Part 2) + Help Text
- 🔴 Write tests for --yes flag (default)
- 🟢 Implement --yes with readme-concise default
- 🔵 Refactor CLI argument handling
- ✅ Commit (--yes working)
- 🔵 Enhance --list output (grouping)
- 🔵 Improve help text
- ✅ Manual testing of all interactive flows
- ✅ Commit (help text polished)

### Day 5: Integration Testing + Polish
- ✅ Test all 6 templates on doc-evergreen project
- ✅ Test interactive mode with all selections
- ✅ Test non-interactive modes (--template, --yes)
- ✅ Cross-project testing if time allows
- 🔵 Fix any issues found
- 🔵 Final polish and refactoring
- ✅ Final commit & sprint review

---

## Manual Testing Checklist

After automated tests pass:

### Specialized Templates
- [ ] Generate API.md with api-docs template
- [ ] Generate ARCHITECTURE.md with architecture template
- [ ] Generate CONTRIBUTING.md with contributing template
- [ ] Verify all outputs are valid markdown
- [ ] Check appropriate length (ballpark estimates)
- [ ] Verify sections make sense for project

### Interactive UX
- [ ] `doc-evergreen init` shows interactive menu
- [ ] All 6 templates listed with descriptions
- [ ] Select option 1 (readme-concise) → works
- [ ] Select option 4 (api-docs) → works
- [ ] Enter 'q' → cancels gracefully
- [ ] Invalid input → shows error, reprompts

### Non-Interactive Modes
- [ ] `doc-evergreen init --template api-docs` → works
- [ ] `doc-evergreen init --template invalid` → clear error
- [ ] `doc-evergreen init --yes` → creates readme-concise
- [ ] `doc-evergreen init --list` → shows grouped list

### Help & Documentation
- [ ] `doc-evergreen init --help` → shows clear help
- [ ] `doc-evergreen init --list` → shows descriptions
- [ ] Help includes examples
- [ ] Error messages are helpful

### Cross-Template Testing
- [ ] All 6 templates load without errors
- [ ] Metadata is consistent across templates
- [ ] Output files have correct names
- [ ] Templates don't conflict with each other

---

## What You Learn

After this sprint, you'll discover:

1. **Template Specialization Patterns**
   - How do specialized templates differ from READMEs?
   - What sources work best for each doc type?
   - → Informs future template additions

2. **Interactive UX Effectiveness**
   - Do users find interactive mode helpful?
   - Is template discovery improved?
   - → Validates approach, could extend to other commands

3. **Template Coverage Completeness**
   - Do 6 templates cover common needs?
   - What's missing that users request?
   - → Informs v0.6.0+ template additions

4. **Prompt Patterns Across Templates**
   - What prompt patterns work across all templates?
   - What needs customization per template type?
   - → Guides Sprint 3 systematic refinement

---

## Success Metrics

### Quantitative
- **Templates**: 6 total (3 README + 3 specialized)
- **Interactive UX**: 1 new mode working
- **Test coverage**: >80% for new code
- **CLI improvements**: Enhanced --list, --yes, help text

### Qualitative
- **Completeness**: Library feels complete for common needs
- **Discoverability**: Users can find right template easily
- **UX smoothness**: Interactive mode feels natural
- **Documentation quality**: All templates generate good docs

---

## Known Limitations (By Design)

1. **Prompt engineering not yet refined** - Best-guess prompts
   - Why acceptable: Sprint 3 does systematic testing and refinement
   - Templates work, may need tuning based on real results

2. **No custom template support** - Built-in only
   - Why acceptable: 6 templates cover common needs
   - Future versions can add custom template directories

3. **Fixed output file names** - Can't customize per template
   - Why acceptable: Standard names are conventional
   - Could add customization in future if needed

4. **No template preview** - Can't see template structure before init
   - Why acceptable: Can view template JSON after init, before regen
   - Could add preview in future if users request

---

## Next Sprint Preview

After Sprint 2 ships, the most pressing need will be:

**Sprint 3: Prompt Quality & Testing**
- Test all 6 templates across multiple projects
- Refine prompts based on real output
- Ensure consistent, appropriate-length docs
- Validate length targets (concise 300-500, etc.)

**Why Sprint 3 is ready:**
- Complete template library to test systematically
- Real usage will reveal prompt weaknesses
- Can now compare results across templates
- Sprint 2 learnings inform refinement strategy

---

## Sprint 2 Philosophy

**Complete the Library**: 6 templates covers common doc types

**Improve Discovery**: Interactive mode makes selection obvious

**Build on Foundation**: Sprint 1 infrastructure makes this fast

**User-Facing Completeness**: Library is feature-complete after this

**Set Up Quality Phase**: Sprint 3 can focus on refinement, not features

---

**Sprint 2 Mantra**: "Complete library + great UX = user delight"
