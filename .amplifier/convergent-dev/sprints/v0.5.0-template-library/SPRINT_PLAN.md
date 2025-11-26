# Sprint Plan: Template Library & Prompt Quality v0.5.0

**Updated**: 2025-11-25 with Divio Documentation System framework

## MVP Scope

**Problem**: Users struggle to create good templates. The default `init` template produces docs that are too long (996 lines), and users don't know what prompts work best for different types of documentation.

**Solution**: Provide a library of proven templates organized around the **Divio Documentation System** (four quadrants: Tutorials, How-to Guides, Reference, Explanation) with well-engineered prompts tailored to each documentation type.

**Theme**: Better Templates, Better Defaults

**Framework**: [Divio Documentation System](https://docs.divio.com/documentation-system/) - industry-proven approach used by Django, Gatsby, and major projects.

---

## Timeline

- **Sprint 1**: 1 week - Quick Win + Foundation (Divio Infrastructure + One Per Quadrant)
- **Sprint 2**: 1 week - Complete Template Library (Expand Across Quadrants)
- **Sprint 3**: 1 week - Prompt Quality & Testing (Divio-Informed Refinement)
- **Sprint 4**: 2.5 days - Documentation & Polish (Teach Divio Framework)
- **Total: 3.5 weeks** (conservative estimate with testing and refinement)

**Note**: Timeline unchanged from original estimate despite Divio adoption - the framework provides better organization without adding significant complexity.

---

## Value Progression

### Sprint 1: Quick Win + Foundation (Divio Infrastructure)
**Value**: Users get immediate clarity (mode removal) + understand Divio framework + 4 working templates (one per quadrant)

- ✅ No more single-shot mode confusion
- ✅ Quadrant-aware template infrastructure working
- ✅ 4 templates prove Divio framework works:
  - 📚 tutorial-quickstart (Tutorials)
  - 🎯 howto-contributing-guide (How-to)
  - 📖 reference-cli (Reference)
  - 💡 explanation-architecture (Explanation)
- ✅ Users can choose templates by purpose, not just size

**Shippable**: YES - Divio framework proven, core library works end-to-end

### Sprint 2: Complete Template Library (Expand Quadrants)
**Value**: Full Divio coverage with 9 templates across all four quadrants

- ✅ 9 total templates available (2-3 per quadrant)
- ✅ Interactive `init` with quadrant-organized menu
- ✅ Each quadrant has multiple template options
- ✅ `--list` shows templates grouped by quadrant
- ✅ Users understand which quadrant matches their need

**Shippable**: YES - complete Divio-organized template library

### Sprint 3: Prompt Quality & Testing (Divio-Informed Refinement)
**Value**: Templates produce output that matches their quadrant's characteristics

- ✅ Tutorial templates: Encouraging, step-by-step (200-500 lines)
- ✅ How-to templates: Practical recipes (300-600 lines)
- ✅ Reference templates: Dry, complete technical docs (400-1000 lines)
- ✅ Explanation templates: Contextual, discursive (400-800 lines)
- ✅ All prompts tested with Divio principles
- ✅ Predictable, quadrant-appropriate output

**Shippable**: YES - production-ready quality following Divio principles

### Sprint 4: Documentation & Polish (Teach Divio Framework)
**Value**: Users learn Divio framework + can apply it beyond doc-evergreen

- ✅ TEMPLATE_BEST_PRACTICES.md teaches Divio framework
- ✅ Each quadrant explained with examples
- ✅ Prompt engineering guide per quadrant
- ✅ All docs updated with Divio references
- ✅ v0.5.0 ready to ship with educational value

**Shippable**: YES - complete release that teaches valuable framework

---

## Sprint Breakdown

### Sprint 1: Quick Win + Foundation (1 week)
**Goal**: Ship working template library with immediate value

**Delivers**:
- Single-shot mode removed (0.5 days)
- Template infrastructure (CLI, loading, selection) (2 days)
- 3 README templates (concise, standard, detailed) (2.5 days)

**Why first**: Removes confusion + delivers core value fast

---

### Sprint 2: Complete Template Library (1 week)
**Goal**: Full template coverage for all common doc types

**Delivers**:
- 3 specialized templates (api-docs, architecture, contributing) (3 days)
- Interactive template selection UX (1 day)
- Template guidance and help text (1 day)

**Why second**: Builds on Sprint 1 infrastructure, completes library

---

### Sprint 3: Prompt Quality & Testing (1 week)
**Goal**: Consistent, appropriate-length output from all templates

**Delivers**:
- Re-engineer all 6 templates with length guidance (2 days)
- Test across multiple projects (1.5 days)
- Refine based on results (1.5 days)

**Why third**: Need complete template library before systematic testing

---

### Sprint 4: Documentation & Polish (2.5 days)
**Goal**: Ship complete v0.5.0 with comprehensive documentation

**Delivers**:
- TEMPLATE_BEST_PRACTICES.md guide (1.5 days)
- Update all documentation (0.5 day)
- Final testing and polish (0.5 day)

**Why last**: Documents learnings from implementation

---

## Dependencies

### External Dependencies
- None (all new features)

### Sprint Dependencies
- Sprint 2 requires Sprint 1 (template infrastructure)
- Sprint 3 requires Sprint 2 (complete template set)
- Sprint 4 requires Sprint 3 (implementation learnings)

**Note**: Each sprint builds on the previous but delivers standalone value

---

## Issues Addressed

### Closed
- **DE-5hd**: Single-shot mode removal (Sprint 1)
- **DE-00l**: Mode clarity documentation (Sprint 1 - resolved by removal)

### Partially Addressed
From backlog (if any relevant issues exist - TBD during implementation)

---

## Deferred to v0.6.0+

**From convergence session** - 12 features deferred with clear reconsider conditions:

1. Smart Template Suggestions (needs library first)
2. Multi-Variant Generation (needs good templates first)
3. Selective Section Regeneration (separate focus)
4. Stability Mode (needs research)
5. Template Validation (needs usage data)
6. Interactive Builder (library sufficient)
7. Template Versioning (format stable)
8. Change Detection (complex, unclear need)
9. Length Feedback (reactive, not proactive)
10. Template Marketplace (premature)
11. CI/CD Integration (tool too young)
12. Performance Optimization (no evidence of issues)

**Reference**: `.amplifier/convergent-dev/convergence/2025-11-24-template-library/DEFERRED_FEATURES.md`

---

## Success Criteria for v0.5.0

After v0.5.0 ships, users should be able to:

1. **Choose the right template easily**
   - ✅ `init` shows clear options
   - ✅ Each template documented with use case
   - ✅ Interactive mode guides to appropriate choice

2. **Get appropriately-sized docs**
   - ✅ readme-concise: 300-500 lines (not 996!)
   - ✅ readme-standard: 500-700 lines
   - ✅ readme-detailed: 800-1000 lines
   - ✅ Specialized templates: appropriate length

3. **Create good templates themselves**
   - ✅ Best practices guide teaches prompt engineering
   - ✅ Real examples show what works
   - ✅ Clear patterns to follow

4. **No confusion about modes**
   - ✅ One mode (chunked), no misleading options
   - ✅ Clear, simple workflow
   - ✅ Documentation reflects reality

**If all 4 work smoothly → v0.5.0 is successful**

---

## Risk Management

### Risk 1: Prompt Engineering Harder Than Expected
**Mitigation**: Sprint 3 has 1.5 days buffer for refinement. Can extend if needed.

### Risk 2: Templates Don't Generalize Well
**Mitigation**: Test across multiple projects in Sprint 3. Adjust prompts based on results.

### Risk 3: User Feedback Requires Changes
**Mitigation**: Each sprint is shippable. Can release early and iterate.

### Risk 4: Timeline Slips
**Mitigation**: Sprint 4 (documentation) can be compressed if needed. Core features in Sprints 1-3.

---

## Testing Strategy

### Per Sprint
- **Sprint 1**: Test template selection, verify mode removal
- **Sprint 2**: Test all 6 templates, verify UX flows
- **Sprint 3**: Cross-project testing, length validation
- **Sprint 4**: Documentation review, final integration test

### TDD Approach
All sprints follow test-driven development:
1. 🔴 Write failing tests first
2. 🟢 Write minimal code to pass
3. 🔵 Refactor while tests protect
4. ✅ Commit on green

**Test coverage target**: >80% for new code

---

## Philosophy Alignment

### Ruthless Simplicity ✅
- Remove confusing mode option (Sprint 1)
- Provide templates, not complex generators
- Clear, focused prompts

### Trust in Emergence ✅
- Templates emerge from real usage patterns
- Learn what prompts work through iteration
- Best practices codify learnings

### Present-Moment Focus ✅
- Solve actual user pain (templates + length)
- Don't build AI analyzers or complex features
- Proven templates over smart suggestions

### Value-First Delivery ✅
- Sprint 1: Immediate value (mode removal + 3 templates)
- Sprint 2: Complete value (full library)
- Sprint 3: Quality value (reliable output)
- Sprint 4: Learning value (documentation)

---

## Next Steps

1. **Review Sprint 1 document**
   - Understand deliverables
   - Clarify any uncertainties
   - Break down into daily tasks if helpful

2. **Set up development environment**
   - Review current template structure
   - Understand CLI implementation
   - Plan test strategy

3. **Start Sprint 1!**
   - Follow implementation order
   - Test as you go (TDD)
   - Ship when acceptance criteria met

4. **After Sprint 1:**
   - Review what you learned
   - Adjust Sprint 2 plan if needed
   - Celebrate shipping!

---

## Convergence Session Reference

**Source**: `.amplifier/convergent-dev/convergence/2025-11-24-template-library/`

- FEATURE_SCOPE.md - Detailed feature specs
- DEFERRED_FEATURES.md - What's NOT in v0.5.0
- CONVERGENCE_COMPLETE.md - Process and decisions

**User validated**: All 5 features, timeline, and deferred items

---

## Version History

- **v0.5.0**: Template Library & Prompt Quality (this release)
- **v0.4.0**: Standalone Tool
- **v0.3.0**: Test Case Basic Regeneration
- **v0.2.0**: Chunked Generation
- **v0.1.0**: Template System

**Next planned**: v0.6.0 - Smart Template Suggestions (using v0.5.0 library as foundation)
