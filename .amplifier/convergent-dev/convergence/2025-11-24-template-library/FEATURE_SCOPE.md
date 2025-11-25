# Feature Scope: Template Library & Prompt Quality

**Version**: v0.5.0
**Date**: 2025-11-24
**Theme**: Better Templates, Better Defaults

---

## Overview

**Problem**: Users struggle to create good templates. The default `init` template produces docs that are too long (996 lines), and users don't know what prompts work best for different types of documentation.

**Solution**: Provide a library of proven templates with well-engineered prompts, and improve the default `init` experience to guide users toward appropriate templates.

---

## Core Features (5 features)

### 1. Template Library with Multiple Document Types

**What**: Expand `init` to support multiple template types, each optimized for different documentation needs.

**User Experience**:
```bash
# List available templates
doc-evergreen init --list
# Output:
# Available templates:
#   readme-concise    - Brief README (300-500 lines)
#   readme-standard   - Standard README (current default)
#   readme-detailed   - Comprehensive README (800+ lines)
#   api-docs          - API documentation
#   architecture      - Architecture/design docs
#   contributing      - Contributing guidelines

# Initialize with specific template
doc-evergreen init --template readme-concise
doc-evergreen init --template api-docs
```

**Templates to Include**:
1. **readme-concise** - Brief, focused README (300-500 lines)
   - Sections: Overview, Quick Start, Key Features, Links
   - Optimized prompts for conciseness
   - Minimal sources (README.md, pyproject.toml, main entry point)

2. **readme-standard** - Balanced README (500-700 lines)
   - Sections: Overview, Installation, Usage, Development
   - Current default behavior but with improved prompts
   - Standard source selection

3. **readme-detailed** - Comprehensive README (800+ lines)
   - Sections: Overview, Features, Installation, Usage, API Reference, Development, Contributing
   - Detailed prompts for thoroughness
   - Broad source selection

4. **api-docs** - API documentation
   - Sections: API Overview, Endpoints/Classes, Examples, Error Handling
   - Sources focus on code files (src/**/*.py)
   - Prompts optimized for technical reference

5. **architecture** - Architecture/design documentation
   - Sections: Overview, Design Decisions, Component Architecture, Data Flow
   - Sources: README, main code files, config files
   - Prompts focus on high-level design

6. **contributing** - Contributing guidelines
   - Sections: Getting Started, Development Setup, Code Style, PR Process
   - Sources: README, tests, CI config
   - Prompts focus on developer onboarding

**Acceptance Criteria**:
- [ ] `doc-evergreen init --list` shows all available templates
- [ ] `doc-evergreen init --template <name>` generates correct template
- [ ] Each template produces appropriately-sized documentation
- [ ] Templates have well-engineered prompts tested for quality
- [ ] Default behavior (`doc-evergreen init`) prompts user to choose or defaults to readme-concise
- [ ] Documentation explains each template and when to use it

**Effort Estimate**: 3-4 days
- Day 1: Template structure and CLI changes (6-8 hours)
- Day 2: Create and test 3 README variants (6-8 hours)
- Day 3: Create api-docs, architecture, contributing templates (6-8 hours)
- Day 4: Testing, refinement, documentation (4-6 hours)

---

### 2. Improved Prompt Engineering for Length Control

**What**: Re-engineer all template prompts to produce appropriately-sized output with better quality and focus.

**Problem**: Current default template produces 996-line READMEs. Prompts don't guide LLM on appropriate length or detail level.

**Solution**: 
- Add length guidance to prompts: "Be concise (2-3 paragraphs)" or "Provide comprehensive detail"
- Add style guidance: "Focus on essentials", "Include examples but keep brief"
- Add scope constraints: "Cover only X, Y, Z - do not include..."

**Example Improved Prompts**:

**Before** (generates 996 lines):
```json
{
  "heading": "## Installation",
  "prompt": "Explain how to install and set up this project. Include prerequisites, installation commands, and any configuration needed."
}
```

**After** (generates ~100-150 lines):
```json
{
  "heading": "## Installation",
  "prompt": "Provide concise installation instructions (3-5 paragraphs). Include: (1) Prerequisites (Python version, API keys), (2) Primary installation method with command, (3) Verification step. Be brief and actionable. Do not include troubleshooting or alternative methods unless essential."
}
```

**Prompt Engineering Principles**:
1. **Explicit length guidance**: "2-3 paragraphs", "Brief overview", "Comprehensive with examples"
2. **Scope constraints**: "Include only X, Y, Z", "Focus on common cases", "Do not include edge cases"
3. **Style guidance**: "Be concise", "Actionable and practical", "Technical reference style"
4. **Structure hints**: "List format", "Code examples", "Step-by-step"

**Acceptance Criteria**:
- [ ] readme-concise template produces 300-500 line docs consistently
- [ ] readme-standard template produces 500-700 line docs
- [ ] readme-detailed template produces 800-1000 line docs
- [ ] All prompts include explicit length/scope guidance
- [ ] Prompts tested on multiple projects for consistency
- [ ] Documentation includes prompt engineering best practices guide

**Effort Estimate**: 2-3 days
- Day 1: Research and design prompt patterns (4-6 hours)
- Day 2: Rewrite all template prompts (6-8 hours)
- Day 3: Test across multiple projects, refine (6-8 hours)

---

### 3. Template Selection Guidance in CLI

**What**: Improve `init` command to guide users toward the right template for their needs.

**User Experience**:
```bash
# Interactive mode (new default)
doc-evergreen init

# Output:
? What type of documentation do you want to create?
  1. Brief README (recommended for most projects)
  2. Standard README (balanced detail)
  3. Detailed README (comprehensive)
  4. API Documentation
  5. Architecture Documentation
  6. Contributing Guidelines
  
Choose [1-6] or 'q' to quit: 1

✓ Created .doc-evergreen/readme.json (readme-concise template)

Next steps:
  1. Review .doc-evergreen/readme.json
  2. Run: doc-evergreen regen-doc readme
```

**Non-interactive mode** (for CI/scripts):
```bash
doc-evergreen init --template readme-concise --yes
```

**Acceptance Criteria**:
- [ ] `init` without args enters interactive mode
- [ ] Interactive mode shows clear descriptions of each template
- [ ] `--template` flag for non-interactive use
- [ ] `--list` shows all templates with descriptions
- [ ] Help text guides users on template selection
- [ ] Default choice is clearly marked (readme-concise)

**Effort Estimate**: 1 day (6-8 hours)

---

### 4. Remove Single-Shot Mode Confusion (Cleanup)

**What**: Remove misleading single-shot mode option, embrace chunked-only approach.

**Changes**:
```bash
# Before:
doc-evergreen regen-doc readme --mode single   # Doesn't work!
doc-evergreen regen-doc readme --mode chunked  # Works

# After:
doc-evergreen regen-doc readme  # Just works (chunked)
# No --mode flag
```

**Implementation**:
- Remove `--mode` option from CLI
- Remove single_generator import fallback code
- Update help text to remove mode references
- Update documentation to reflect chunked-only approach
- Close ISSUE-009 as "Won't implement"
- Close ISSUE-008 as "N/A - single mode removed"

**Why Now**: User confirmed they don't need single-shot mode, and it's causing confusion with non-functional feature advertising.

**Acceptance Criteria**:
- [ ] `--mode` flag removed from CLI
- [ ] No import fallback code for single_generator
- [ ] Help text updated (no mode references)
- [ ] Documentation updated
- [ ] ISSUE-009 closed with explanation
- [ ] ISSUE-008 closed with explanation
- [ ] All tests updated (remove mode tests)

**Effort Estimate**: 4-6 hours
- Remove code and flags (2 hours)
- Update tests (2 hours)
- Update documentation (2 hours)

---

### 5. Template Best Practices Documentation

**What**: Create comprehensive guide on template creation, prompt engineering, and source selection.

**Content** (new file: `docs/TEMPLATE_BEST_PRACTICES.md`):

1. **Template Design Principles**
   - When to use each template type
   - How to structure sections
   - Source selection strategies

2. **Prompt Engineering Guide**
   - Length control techniques
   - Style guidance patterns
   - Scope constraint examples
   - Common pitfalls and solutions

3. **Real-World Examples**
   - Show before/after prompts
   - Explain why certain prompts work better
   - Common templates for different project types

4. **Troubleshooting**
   - Output too long? → Tighten prompts
   - Output too vague? → Add specificity
   - Output off-topic? → Add scope constraints

**Acceptance Criteria**:
- [ ] TEMPLATE_BEST_PRACTICES.md created
- [ ] Covers all 4 content areas above
- [ ] Includes 5+ real examples with explanations
- [ ] Referenced from USER_GUIDE.md and README.md
- [ ] Includes lessons learned from v0.5.0 development

**Effort Estimate**: 1-2 days
- Day 1: Write guide with examples (6-8 hours)
- Day 2: Review, refine, integrate with docs (4-6 hours)

---

## Total Effort Estimate

**Feature Breakdown**:
1. Template Library: 3-4 days
2. Prompt Engineering: 2-3 days
3. Template Selection UX: 1 day
4. Mode Cleanup: 0.5 days
5. Documentation: 1-2 days

**Total: 7.5-10.5 days (1.5-2 weeks)**

**Conservative: 3 weeks** (with testing, refinement, real-world validation)

---

## Success Metrics

After v0.5.0 ships, users should:

1. **Find the right template easily**
   - `init` guides them to appropriate template
   - Template library covers common doc types

2. **Get appropriately-sized output**
   - readme-concise: 300-500 lines (not 996!)
   - Other templates: predictable, appropriate length

3. **Understand prompt engineering**
   - Best practices guide teaches them
   - Template examples show good patterns

4. **No mode confusion**
   - One mode, no misleading options
   - Clear, simple workflow

**If all 4 work → v0.5.0 is successful**

---

## Dependencies

- None (all new features)
- Closes: ISSUE-009 (single-shot), ISSUE-008 (mode clarity)
- Partially addresses backlog items: Template discovery, prompt quality

---

## Philosophy Alignment

**Ruthless Simplicity**:
- ✓ Remove confusing mode option
- ✓ Provide templates, not complex generators
- ✓ Clear, focused prompts

**Trust in Emergence**:
- ✓ Templates emerge from real usage patterns
- ✓ Learn what prompts work through iteration
- ✓ Best practices codify learnings

**Present-Moment Focus**:
- ✓ Solve actual user pain (templates + length)
- ✓ Don't build AI analyzers or complex features
- ✓ Proven templates over smart suggestions

---

## Notes

**Why these 5 features?**
- Address user's #1 pain point: "Don't know what template to use"
- Address user's #2 pain point: "Output too long"
- Clean up technical debt (mode confusion)
- Preserve learning (best practices doc)

**What we're NOT doing** (deferred):
- Smart AI template suggestions (complex, unproven)
- Multi-variant generation (interesting but not essential)
- Selective regeneration (valuable but separate focus)
- Stability mode (needs more research on variation causes)

**Next version candidates** (based on these foundations):
- v0.6.0: Smart template suggestions (using template library as base)
- v0.7.0: Selective regeneration (using improved templates)
