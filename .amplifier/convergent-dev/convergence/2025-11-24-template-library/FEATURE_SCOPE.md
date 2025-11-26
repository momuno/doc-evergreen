# Feature Scope: Template Library & Prompt Quality

**Version**: v0.5.0
**Date**: 2025-11-24 (Updated: 2025-11-25 with Divio framework)
**Theme**: Better Templates, Better Defaults

---

## Overview

**Problem**: Users struggle to create good templates. The default `init` template produces docs that are too long (996 lines), and users don't know what prompts work best for different types of documentation.

**Solution**: Provide a library of proven templates organized around the **Divio Documentation System** (four quadrants: Tutorials, How-to Guides, Reference, Explanation), with well-engineered prompts tailored to each documentation type.

**Framework**: [Divio Documentation System](https://docs.divio.com/documentation-system/) - industry-proven approach that organizes documentation into four distinct purposes.

---

## Core Features (5 features)

### 1. Template Library Organized by Divio Quadrants

**What**: Expand `init` to support multiple template types organized around the **Divio Documentation System** - four distinct purposes that users naturally think in: learning, goal-solving, information lookup, and understanding.

**The Divio Four Quadrants**:
```
                  Learning-oriented  │ Understanding-oriented
                 ──────────────────────────────────────────────
                  TUTORIALS          │ EXPLANATION
                  "Teach me"         │ "Help me understand"
                 ──────────────────────────────────────────────
                  HOW-TO GUIDES      │ REFERENCE
                  "Show me how"      │ "Tell me facts"
```

**User Experience**:
```bash
# List available templates (organized by quadrant)
doc-evergreen init --list

# Interactive mode shows quadrant-organized menu (see Feature #3)
doc-evergreen init

# Initialize with specific template
doc-evergreen init --template tutorial-quickstart
doc-evergreen init --template howto-ci-integration
doc-evergreen init --template reference-api
doc-evergreen init --template explanation-architecture
```

**Templates to Include** (organized by quadrant):

#### TUTORIALS Quadrant (Learning-oriented - "Teach me")
Teaching users by doing. Hand-holding, step-by-step, must work reliably for complete beginners.

1. **tutorial-quickstart** - Get started in 5 minutes
   - Sections: Prerequisites, Step 1/2/3, What You've Learned, Next Steps
   - Prompts: Concrete steps, immediate results, encouragement
   - Sources: README.md, main entry point, basic config
   - Length: 200-400 lines

2. **tutorial-first-template** - Create your first doc template (hands-on)
   - Sections: Setup, Create Template, Generate Doc, Review Output, Next Steps
   - Prompts: Learning by doing, explain while building
   - Sources: README.md, .doc-evergreen examples, template schema
   - Length: 300-500 lines

#### HOW-TO GUIDES Quadrant (Goal-oriented - "Show me how")
Recipes for experienced users who know what they want to achieve. Assumes basic knowledge.

3. **howto-ci-integration** - Integrate with CI/CD pipeline
   - Sections: Overview, GitHub Actions Setup, GitLab CI Setup, Testing
   - Prompts: Step-by-step recipes, practical examples
   - Sources: README.md, CI config files, automation docs
   - Length: 300-500 lines

4. **howto-custom-prompts** - Write effective custom prompts
   - Sections: Prompt Basics, Length Control, Examples, Testing
   - Prompts: Problem-solution format, actionable advice
   - Sources: README.md, template examples, prompt engineering docs
   - Length: 400-600 lines

5. **howto-contributing-guide** - Create contributing guidelines
   - Sections: Getting Started, Dev Setup, Code Style, PR Process, Testing
   - Prompts: Onboarding focus, practical workflows
   - Sources: README.md, tests, CI config, development docs
   - Length: 500-700 lines

#### REFERENCE Quadrant (Information-oriented - "Tell me facts")
Dry technical descriptions for quick lookup. Code-determined structure, no fluff.

6. **reference-cli** - Complete CLI command reference
   - Sections: Commands, Options, Examples, Exit Codes
   - Prompts: Technical descriptions, complete parameter lists
   - Sources: CLI code, help text, command implementations
   - Length: 400-600 lines

7. **reference-api** - API reference documentation
   - Sections: API Overview, Classes/Functions, Parameters, Returns, Examples
   - Prompts: Technical reference style, complete signatures
   - Sources: src/**/*.py, docstrings, type hints
   - Length: 600-1000 lines (depends on API size)

#### EXPLANATION Quadrant (Understanding-oriented - "Help me understand")
Context, "why", design decisions. Discusses alternatives and broadens understanding.

8. **explanation-architecture** - Architecture and design decisions
   - Sections: Overview, Design Philosophy, Component Architecture, Trade-offs
   - Prompts: Discuss "why", explain alternatives, provide context
   - Sources: README.md, main code files, design docs, ADRs
   - Length: 500-800 lines

9. **explanation-concepts** - Deep dive into key concepts
   - Sections: Problem Context, How It Works, Design Rationale, Alternatives
   - Prompts: Educational, contextual, discusses trade-offs
   - Sources: README.md, relevant code, documentation
   - Length: 400-700 lines

**Acceptance Criteria**:
- [ ] `doc-evergreen init --list` shows all templates organized by Divio quadrants
- [ ] `doc-evergreen init --template <name>` generates correct template
- [ ] Each template follows Divio principles for its quadrant
- [ ] Templates have well-engineered prompts tailored to their quadrant type
- [ ] Default behavior (`doc-evergreen init`) shows quadrant-organized interactive menu
- [ ] Documentation explains Divio framework and when to use each quadrant
- [ ] Each quadrant has at least 2 templates (proving the framework)

**Phased Implementation**:

**Phase 1 (Sprint 1)**: Foundation + One Per Quadrant (4 templates)
- Build quadrant-aware template infrastructure
- Create one template per quadrant to prove framework:
  - `tutorial-quickstart` (Tutorials)
  - `howto-contributing-guide` (How-to)
  - `reference-cli` (Reference)
  - `explanation-architecture` (Explanation)

**Phase 2 (Sprint 2)**: Expand Library (5 more templates)
- Add additional templates across quadrants:
  - `tutorial-first-template` (Tutorials)
  - `howto-ci-integration`, `howto-custom-prompts` (How-to)
  - `reference-api` (Reference)
  - `explanation-concepts` (Explanation)

**Effort Estimate**: 4-5 days
- Day 1: Quadrant-aware infrastructure + CLI changes (6-8 hours)
- Day 2: Phase 1 - Create 4 templates (one per quadrant) (6-8 hours)
- Day 3: Phase 2 - Create 5 additional templates (6-8 hours)
- Day 4-5: Testing all templates, refinement (8-12 hours)

---

### 2. Improved Prompt Engineering with Divio Principles

**What**: Re-engineer all template prompts to follow Divio quadrant characteristics - each quadrant has distinct prompt patterns, tone, and expectations.

**Problem**: Current default template produces 996-line READMEs. Prompts don't guide LLM on appropriate length, tone, or style based on documentation purpose.

**Solution**: Tailor prompts to Divio quadrant characteristics:

**Divio-Informed Prompt Patterns by Quadrant**:

**TUTORIALS** - Learning-oriented prompts:
```json
{
  "heading": "## Step 1: Install the Tool",
  "prompt": "Write beginner-friendly installation instructions (2-3 paragraphs). Use second person ('you will'). Include: (1) Prerequisites with versions, (2) Single installation command with explanation, (3) How to verify it worked with expected output. Be encouraging. Assume no prior knowledge. Show concrete results immediately."
}
```
- Style: Friendly, encouraging, hand-holding
- Length: Step-focused, immediate results
- Tone: "Follow these steps and you'll succeed"

**HOW-TO GUIDES** - Goal-oriented prompts:
```json
{
  "heading": "## Integrate with GitHub Actions",
  "prompt": "Provide a recipe for CI/CD integration (3-5 paragraphs). Focus on the goal: automated doc updates. Include: (1) Workflow file example, (2) Key configuration options, (3) Testing the integration. Be practical and direct. Assume reader knows basics. Allow for slight variations."
}
```
- Style: Recipe-like, practical, direct
- Length: Problem-solution focused
- Tone: "Here's how to achieve X"

**REFERENCE** - Information-oriented prompts:
```json
{
  "heading": "## Commands",
  "prompt": "Document all CLI commands in technical reference style. For each command, provide: (1) Name and signature, (2) Description (1 sentence), (3) Parameters with types and defaults, (4) Brief usage example. Be dry and complete. No explanations of concepts. Structured like a dictionary entry."
}
```
- Style: Dry, technical, complete
- Length: Code-determined, comprehensive
- Tone: "Here are the facts"

**EXPLANATION** - Understanding-oriented prompts:
```json
{
  "heading": "## Why Section-by-Section Generation?",
  "prompt": "Explain the design rationale for chunked generation (4-6 paragraphs). Discuss: (1) The problem it solves, (2) How it works at a high level, (3) Alternative approaches considered, (4) Trade-offs made. Be discursive and contextual. This is about understanding 'why', not 'how to'. Assume reader wants to think deeply."
}
```
- Style: Discursive, contextual, thoughtful
- Length: Concept-focused, thorough
- Tone: "Let me help you understand why"

**Acceptance Criteria**:
- [ ] Each quadrant has distinct prompt engineering patterns documented
- [ ] Tutorial prompts produce encouraging, step-by-step content (200-500 lines)
- [ ] How-to prompts produce practical recipes (300-600 lines)
- [ ] Reference prompts produce dry, complete technical docs (400-1000 lines)
- [ ] Explanation prompts produce contextual, discursive content (400-800 lines)
- [ ] All prompts tested on multiple projects for consistency
- [ ] TEMPLATE_BEST_PRACTICES.md explains prompt patterns per quadrant

**Effort Estimate**: 2-3 days
- Day 1: Research Divio principles and design prompt patterns per quadrant (4-6 hours)
- Day 2: Rewrite all template prompts with quadrant-specific patterns (6-8 hours)
- Day 3: Test across multiple projects, refine based on output (6-8 hours)

---

### 3. Template Selection Guidance with Divio Quadrants

**What**: Improve `init` command to guide users using the Divio framework - helping them think about their documentation purpose first.

**User Experience**:
```bash
# Interactive mode (new default)
doc-evergreen init

# Output:
? What type of documentation do you need?

📚 TUTORIALS (Learning-oriented - "Teach me")
  1. Quickstart Tutorial - Get started in 5 minutes
  2. First Template Tutorial - Create your first doc template

🎯 HOW-TO GUIDES (Goal-oriented - "Show me how")
  3. CI/CD Integration - Integrate with pipelines
  4. Custom Prompts - Write effective prompts
  5. Contributing Guide - Create contribution guidelines

📖 REFERENCE (Information-oriented - "Tell me facts")
  6. CLI Reference - Complete command reference
  7. API Reference - API documentation

💡 EXPLANATION (Understanding-oriented - "Help me understand")
  8. Architecture Overview - Design decisions and components
  9. Concepts Deep-Dive - Understanding key concepts

Choose [1-9] or 'q' to quit: 1

✓ Created .doc-evergreen/quickstart.json (tutorial-quickstart template)

Next steps:
  1. Review .doc-evergreen/quickstart.json
  2. Run: doc-evergreen regen-doc quickstart
  3. Learn more about the Divio framework: docs/TEMPLATE_BEST_PRACTICES.md
```

**Non-interactive mode** (for CI/scripts):
```bash
doc-evergreen init --template tutorial-quickstart --yes
```

**Acceptance Criteria**:
- [ ] `init` without args enters interactive mode with quadrant-organized menu
- [ ] Each quadrant has clear emoji marker and description
- [ ] Templates grouped visually by quadrant
- [ ] `--template` flag for non-interactive use
- [ ] `--list` shows all templates organized by quadrant
- [ ] Help text explains Divio framework briefly
- [ ] Exit message suggests learning more about the framework

**Effort Estimate**: 1-1.5 days (6-10 hours)
- Increased slightly to account for quadrant-aware UI design

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

### 5. Template Best Practices Documentation with Divio Framework

**What**: Create comprehensive guide teaching the Divio Documentation System and how to apply it with doc-evergreen.

**Content** (new file: `docs/TEMPLATE_BEST_PRACTICES.md`):

1. **Understanding the Divio Documentation System**
   - The four quadrants explained (Tutorials, How-to, Reference, Explanation)
   - When to use each quadrant
   - How users think about their documentation needs
   - Why mixing quadrants creates confusion

2. **Template Design by Quadrant**
   - Tutorial templates: Learning-oriented characteristics
   - How-to templates: Goal-oriented characteristics
   - Reference templates: Information-oriented characteristics
   - Explanation templates: Understanding-oriented characteristics
   - Section structure patterns per quadrant
   - Source selection strategies per quadrant

3. **Prompt Engineering by Quadrant**
   - Tutorial prompts: Encouraging, step-by-step, concrete
   - How-to prompts: Recipe-like, practical, direct
   - Reference prompts: Dry, complete, technical
   - Explanation prompts: Discursive, contextual, exploratory
   - Length control techniques per quadrant
   - Common pitfalls per quadrant

4. **Real-World Examples**
   - Show before/after prompts for each quadrant
   - Explain why certain prompts work better
   - Template examples for different project types
   - Case study: Migrating from mixed to Divio-organized docs

5. **Troubleshooting**
   - Output doesn't match expected quadrant tone? → Review prompt patterns
   - Users confused about which template to use? → Explain quadrant purposes
   - Output too long/short? → Adjust prompt detail level per quadrant
   - Content feels off-topic? → Check if wrong quadrant was chosen

**Acceptance Criteria**:
- [ ] TEMPLATE_BEST_PRACTICES.md created with comprehensive Divio coverage
- [ ] Covers all 5 content areas above
- [ ] Includes detailed examples for each quadrant
- [ ] Visual diagram of Divio quadrants included
- [ ] Referenced from USER_GUIDE.md and README.md
- [ ] Links to official Divio documentation system site
- [ ] Includes lessons learned from v0.5.0 development

**Effort Estimate**: 2-3 days
- Day 1: Write Divio framework explanation and quadrant details (6-8 hours)
- Day 2: Write prompt engineering guide per quadrant with examples (6-8 hours)
- Day 3: Review, add diagrams, refine, integrate with docs (4-6 hours)

---

## Total Effort Estimate

**Feature Breakdown**:
1. Template Library (Divio-organized, 9 templates): 4-5 days
2. Prompt Engineering (per quadrant): 2-3 days
3. Template Selection UX (quadrant-aware): 1-1.5 days
4. Mode Cleanup: 0.5 days
5. Documentation (Divio framework guide): 2-3 days

**Total: 10-13 days (2-2.5 weeks)**

**Conservative: 3.5 weeks** (with testing, refinement, real-world validation across quadrants)

**Note**: Slightly increased from original estimate due to:
- More templates (9 vs 6)
- Quadrant-aware infrastructure
- Additional documentation explaining Divio framework
- Testing across all four quadrant types

---

## Success Metrics

After v0.5.0 ships, users should:

1. **Understand their documentation needs using Divio framework**
   - Users can identify which quadrant they need (Tutorial, How-to, Reference, or Explanation)
   - `init` guides them with clear quadrant descriptions
   - Template library covers all four quadrants

2. **Get output that matches their quadrant's purpose**
   - Tutorial templates: Encouraging, step-by-step, beginner-friendly (200-500 lines)
   - How-to templates: Practical recipes for experienced users (300-600 lines)
   - Reference templates: Dry, complete technical reference (400-1000 lines)
   - Explanation templates: Contextual, discursive understanding (400-800 lines)

3. **Create their own templates with Divio principles**
   - Best practices guide teaches Divio framework
   - Template examples demonstrate quadrant characteristics
   - Users understand prompt patterns per quadrant

4. **No mode confusion**
   - One mode, no misleading options
   - Clear, simple workflow

5. **Apply Divio framework beyond doc-evergreen**
   - Users understand broader documentation organization principles
   - Can structure their entire documentation using Divio quadrants

**If all 5 work → v0.5.0 is successful and teaches valuable framework**

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

**Why these 5 features with Divio framework?**
- Address user's #1 pain point: "Don't know what template to use" → Divio provides principled organization
- Address user's #2 pain point: "Output too long" → Quadrant-specific prompts control length naturally
- Clean up technical debt (mode confusion)
- Teach valuable framework (Divio) that applies beyond doc-evergreen
- Industry-proven approach widely adopted across documentation projects

**Why Divio over ad-hoc organization?**
- **User-centric**: Users naturally think in terms of learning vs solving vs looking up vs understanding
- **Clear boundaries**: Each quadrant has distinct purpose, preventing scope creep and confusion
- **Expandable**: Easy to add templates to the right quadrant without reorganizing
- **Teachable**: Well-documented framework users can apply elsewhere
- **Proven**: Used by Django, Gatsby, and many major projects

**Key Divio Insight**: Documentation problems often come from mixing quadrants
- Tutorials that explain concepts → Confusing for beginners
- How-to guides that teach basics → Frustrating for experienced users
- Reference that provides opinions → Unreliable for lookup
- Explanation that instructs → Misses the "why"

**What we're NOT doing** (deferred):
- Smart AI template suggestions (complex, unproven - but Divio makes this easier later)
- Multi-variant generation (interesting but not essential)
- Selective regeneration (valuable but separate focus)
- Stability mode (needs more research on variation causes)
- Mixed-purpose templates (violates Divio principles)

**Next version candidates** (based on Divio foundations):
- v0.6.0: Smart template suggestions using Divio quadrant classification
- v0.7.0: Selective regeneration with quadrant-aware section detection
- v0.8.0: Template marketplace organized by Divio quadrants

**Divio Resources**:
- Official site: https://docs.divio.com/documentation-system/
- Used by: Django, Gatsby, Cloudflare, NumPy, and many others
- Also known as: "The Grand Unified Theory of Documentation"
