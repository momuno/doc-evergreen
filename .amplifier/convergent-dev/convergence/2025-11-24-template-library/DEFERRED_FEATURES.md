# Deferred Features

**Version**: Post-v0.5.0 (v0.6.0+)
**Date**: 2025-11-24

---

## Philosophy

These features are valuable but NOT required for template library MVP. Each is deferred with clear **reconsider conditions** - when user feedback or usage patterns indicate need.

---

## Deferred Feature List

### 1. Smart Template Suggestions (AI-Powered)

**What**: `doc-evergreen init --smart` analyzes repo and suggests best template with reasoning.

**Why Valuable**: 
- Removes guesswork from template selection
- Leverages repo context (languages, structure, existing docs)
- Provides explanations for learning

**Why Deferred**:
- Template library needs to exist first (foundation)
- Need data on which templates work for which repos
- Complexity: requires repo analysis, prompt engineering
- User confirmed: wants templates first, smart suggestions later

**Reconsider When**:
- Template library (v0.5.0) is shipped and used
- Patterns emerge: "Python CLI projects use X, libraries use Y"
- Users ask: "Which template should I use for my project?"
- Have 10+ examples of good template selections per project type

**Estimated Effort**: 2-3 days
- Repo analysis logic: 1 day
- Template recommendation engine: 1 day
- Testing across project types: 0.5-1 day

**Implementation Notes**:
- Analyze: Language (Python/JS/etc), structure (CLI/library/app), existing docs
- Rules: "Python CLI → readme-concise + contributing", "Library → readme-standard + api-docs"
- Show reasoning: "I detected a Python CLI project with tests, suggesting readme-concise + contributing"

---

### 2. Multi-Variant Generation

**What**: Generate multiple doc versions from different templates/prompts, compare side-by-side, pick best.

**Why Valuable**:
- Reduces trial-and-error
- Helps users learn what works
- Shows impact of template choices

**Why Deferred**:
- Need good template library first (foundation)
- Increases API costs (3x LLM calls)
- Unclear UX for comparison (how to present 3 READMEs?)
- User needs to validate template library quality first

**Reconsider When**:
- Template library exists and users still uncertain which to use
- Users report: "I wish I could see multiple options before choosing"
- Clear UX pattern for comparison emerges
- API cost is acceptable to users

**Estimated Effort**: 3-4 days
- Parallel generation: 1 day
- Comparison UI/output: 1-2 days
- Testing and refinement: 1 day

**Implementation Notes**:
```bash
doc-evergreen regen-doc readme --variants 3
# Generates 3 versions:
#   - readme-concise.md
#   - readme-standard.md
#   - readme-detailed.md
# Shows side-by-side comparison or summary
```

---

### 3. Selective Section Regeneration

**What**: Regenerate only specific sections instead of entire document.

**Why Valuable**:
- Faster regeneration
- Less API cost
- More control over what changes
- Reduces unnecessary variation

**Why Deferred**:
- Complexity: requires section-to-source mapping
- Needs stability research first (why does regeneration vary?)
- Template improvements (v0.5.0) may reduce need
- Separate focus area (different problem domain)

**Reconsider When**:
- Full doc regeneration is slow (>2 minutes)
- Users frequently want to update just one section
- Template stability is well-understood
- Section-to-source mapping is clear

**Estimated Effort**: 2-3 days
- Section targeting: 1 day
- Context management: 1 day
- Testing: 0.5-1 day

**Implementation Notes**:
```bash
# Manual selection
doc-evergreen regen-doc readme --sections "Usage,Development"

# Only changed sections (requires tracking)
doc-evergreen regen-doc readme --only-changed
```

---

### 4. Stability Mode (Variation Reduction)

**What**: Include current doc content in prompts to minimize unnecessary changes when regenerating.

**Why Valuable**:
- Reduces LLM non-determinism
- Preserves good content
- Provides continuity across regenerations

**Why Deferred**:
- Need to understand variation root cause first
- Template prompt improvements (v0.5.0) may solve this
- Requires experimentation with prompt strategies
- Increases context size (costs more)

**Reconsider When**:
- Users regenerate with same template/sources but get wildly different output
- Template improvements don't reduce variation enough
- Clear evidence that including current content helps
- Users explicitly request: "Keep what's good, only update what changed"

**Estimated Effort**: 2-3 days
- Prompt engineering research: 1 day
- Implementation: 1 day
- Testing variation reduction: 0.5-1 day

**Implementation Notes**:
```python
# Include current content in context
prompt = f"""
Current content:
{current_section_content}

Source materials:
{source_files}

Task: Update the content above if needed based on source changes.
Preserve good content. Only change what's necessary.
"""
```

---

### 5. Template Validation/Pre-flight Check

**What**: Before generation, analyze template and warn about potential issues.

**Why Valuable**:
- Prevents "too long" surprises
- Guides template improvements
- Educational for template authors

**Why Deferred**:
- Need template library data first (what's "too many sources"?)
- Heuristics not yet established
- May be premature optimization
- Template improvements may make this less necessary

**Reconsider When**:
- Users frequently generate docs, find them too long, regenerate
- Clear patterns emerge (">X sources = too long")
- Template library usage reveals common mistakes
- Users ask: "Will this template produce a reasonable size doc?"

**Estimated Effort**: 1-2 days
- Heuristics development: 0.5-1 day
- Validation logic: 0.5 day
- Warning system: 0.5 day

**Implementation Notes**:
```bash
doc-evergreen regen-doc readme
# Output:
⚠ Pre-flight check:
  - Section 'Overview' has 52 source files (high, may be too broad)
  - Estimated length: 800-1000 lines
  - Recommendation: Consider narrowing sources or using 'readme-concise'

Proceed? [y/N]
```

---

### 6. Interactive Template Builder (Wizard)

**What**: CLI wizard that asks questions and builds custom template.

**Why Valuable**:
- Guides beginners
- Reduces template creation friction
- Educational

**Why Deferred**:
- Template library provides ready-made templates
- Wizard is complex to build well
- Not clear it's better than picking from library
- User can edit templates directly

**Reconsider When**:
- Template library doesn't cover user needs
- Users struggle to customize templates
- Pattern emerges: users want guided template creation
- Clear questions/workflow identified

**Estimated Effort**: 2-3 days
- Wizard logic: 1 day
- Question flow: 1 day
- Testing: 0.5-1 day

**Implementation Notes**:
```bash
doc-evergreen init --interactive

? What type of documentation? [readme/api/architecture/custom]
? Who is the audience? [users/developers/contributors]
? How detailed? [brief/standard/comprehensive]
? Include installation section? [y/N]
? Include API reference? [y/N]
...
✓ Created custom template: .doc-evergreen/readme.json
```

---

### 7. Template Versioning

**What**: Version templates, lock projects to template versions, handle breaking changes.

**Why Valuable**:
- Stability across tool updates
- Clear migration paths
- Version compatibility

**Why Deferred**:
- Template format is stable
- No breaking changes anticipated
- Adds complexity without proven need
- Tool is young, format still evolving

**Reconsider When**:
- Template format changes break old templates
- Users need to lock to specific versions
- Multiple incompatible template versions exist
- Tool reaches 1.0 and needs stability guarantees

**Estimated Effort**: 1-2 days
- Version schema: 0.5 day
- Migration system: 0.5-1 day
- Documentation: 0.5 day

---

### 8. Smart Change Detection (Source Tracking)

**What**: Track which sources changed since last generation, auto-determine which sections need updating.

**Why Valuable**:
- Intelligent selective regeneration
- Avoid unnecessary work
- Clear impact analysis

**Why Deferred**:
- Requires selective regeneration (Feature #3) first
- Needs source-to-section mapping
- Complex: git integration, file tracking, heuristics
- Template improvements may reduce need

**Reconsider When**:
- Selective regeneration exists and is used
- Users manually track which sections to update
- Git integration makes sense (files changed in commits)
- Clear algorithm for change-to-section mapping

**Estimated Effort**: 2-3 days
- Git integration: 1 day
- Change detection: 1 day
- Section mapping: 1 day

**Implementation Notes**:
```bash
doc-evergreen regen-doc readme --smart

# Output:
Detecting changes since last generation...
✓ src/cli.py changed → affects sections: Usage
✓ tests/ changed → affects sections: Development
✓ README.md unchanged → skip section: Overview

Regenerating 2 of 4 sections...
```

---

### 9. Output Length Feedback (Post-Generation)

**What**: After generation, show per-section statistics and suggest improvements.

**Why Valuable**:
- Learning tool for template authors
- Helps identify sections that need tightening
- Guides iterative improvement

**Why Deferred**:
- Template library (v0.5.0) should solve length issues upfront
- Post-generation feedback is reactive, not proactive
- Better to fix templates than warn about results
- Users can check length themselves

**Reconsider When**:
- Template improvements aren't sufficient
- Users want feedback for custom templates
- Length issues persist despite good templates
- Clear actionable feedback patterns emerge

**Estimated Effort**: 1 day
- Length tracking: 0.5 day
- Feedback generation: 0.5 day

**Implementation Notes**:
```bash
doc-evergreen regen-doc readme

# Output after generation:
✓ Generated: README.md (847 lines)

Section Statistics:
  Overview: 150 lines ⚠ (might be too long for intro)
  Installation: 97 lines ✓
  Usage: 420 lines ⚠ (consider splitting into sub-sections)
  Development: 180 lines ✓

Suggestions:
  - Overview: Consider "readme-concise" template for briefer intro
  - Usage: Split into "Basic Usage" and "Advanced Usage"?
```

---

### 10. Template Marketplace / Sharing

**What**: Share templates across projects, community templates, template discovery.

**Why Valuable**:
- Leverage community expertise
- Reduce duplicate template creation
- Discover patterns

**Why Deferred**:
- Need proven templates first (template library)
- Infrastructure: hosting, discovery, versioning
- Unclear if templates are reusable across projects
- Premature standardization

**Reconsider When**:
- Multiple projects use similar templates
- Users ask: "Where can I find templates for X?"
- Template patterns emerge across projects
- Community wants to contribute templates

**Estimated Effort**: 1-2 weeks
- Infrastructure: 1 week
- Discovery/search: 2-3 days
- Version management: 2-3 days

---

### 11. CI/CD Template Auto-Update

**What**: Detect source changes in CI, automatically regenerate docs, create PR.

**Why Valuable**:
- Docs stay fresh automatically
- No manual regeneration needed
- CI integration

**Why Deferred**:
- Manual workflow sufficient for now
- CI/CD usage patterns unclear
- Tool not stable enough for automated use
- Requires stability mode (Feature #4) for predictability

**Reconsider When**:
- Tool is production-stable (1.0+)
- Users manually regenerate after every commit
- Clear demand for automation
- Stability is sufficient for automated use

**Estimated Effort**: 2-3 days
- GitHub Actions template: 1 day
- Auto-commit logic: 1 day
- Testing: 0.5-1 day

---

### 12. Performance Optimization (Caching, Parallelization)

**What**: Cache unchanged sources, parallel section generation, optimized prompts.

**Why Valuable**:
- Faster regeneration
- Lower API costs
- Better UX for large projects

**Why Deferred**:
- Current performance acceptable (<30s per section)
- No user complaints about speed
- Premature optimization
- Template improvements may reduce generation time naturally

**Reconsider When**:
- Generation takes >30s per section consistently
- Large projects hit performance limits
- API costs become significant concern
- Users explicitly request faster generation

**Estimated Effort**: 2-3 days
- Caching: 1 day
- Parallel generation: 1 day
- Testing: 0.5-1 day

---

## Summary

**Total Deferred**: 12 features

**Grouped by Theme**:
- **Template Intelligence** (3): Smart suggestions, multi-variant, validation
- **Selective Updates** (3): Section regeneration, stability mode, change detection
- **UX Improvements** (2): Interactive builder, length feedback
- **Advanced Features** (4): Template versioning, marketplace, CI/CD, performance

**Highest Priority for Next Version** (v0.6.0 candidates):
1. Smart Template Suggestions (builds on v0.5.0 library)
2. Stability Mode (reduces regeneration variation)
3. Selective Section Regeneration (targeted updates)

**Parking Lot** (needs more clarity):
- Template marketplace (unclear if needed)
- CI/CD integration (tool too young)
- Performance (no evidence of problems)

---

## Return to Backlog

All deferred features should be added to `MASTER_BACKLOG.md` with:
- Reconsider conditions
- Estimated effort
- Links to this document

When conditions are met, features can be pulled into future convergence cycles.

---

## Remember

**Deferral ≠ Rejection**

Every deferred feature:
- Has clear value
- Could be implemented later
- Has conditions for reconsideration
- Is preserved for future planning

**Focus wins**: Shipping 5 features well > planning 17 features poorly.
