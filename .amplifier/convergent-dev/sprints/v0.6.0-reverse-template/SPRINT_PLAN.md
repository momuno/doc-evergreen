# Sprint Plan: doc-evergreen v0.6.0 - Reverse Template Generation

**Release**: v0.6.0  
**Branch**: dev/loop-6  
**Timeline**: 6-10 days  
**Philosophy**: Value-first vertical slicing + TDD

---

## 🎯 MVP Scope

**Problem**: Users have existing, well-structured documentation that has become outdated. They want to update these docs using doc-evergreen but face critical blockers:
1. Can't regenerate without template → Risk losing structure
2. Don't know what sources were originally used
3. Manual template creation is too tedious (high barrier)
4. Can't reference outdated doc as context (context poisoning)

**Solution**: Automated template generation FROM existing documentation

**Success Criteria**: 70-80% accuracy ("remotely close")
- Structure matches original doc
- Source files are relevant to each section
- User can run `regen` immediately with reasonable results
- User can refine template to 95%+ with minimal effort

---

## 🗓️ Sprint Timeline

### Sprint 1 (2-3 days): End-to-End Proof of Concept
**Goal**: Working reverse template pipeline with naive source discovery  
**Value**: Proves the concept works, delivers usable output immediately

### Sprint 2 (2-3 days): Intelligent Source Discovery ⭐
**Goal**: Pattern + semantic + LLM-based source matching  
**Value**: Achieves 70-80% accuracy target (the hard part)  
**Critical Checkpoint**: Day 5 - evaluate accuracy, adjust if needed

### Sprint 3 (2-3 days): Prompt Generation & Complete Pipeline
**Goal**: LLM-generated prompts + full template assembly  
**Value**: Complete reverse → regen workflow works end-to-end

### Sprint 4 (1-2 days): Polish & Production Readiness
**Goal**: CLI refinement, edge cases, error handling  
**Value**: Production-ready feature

**Total Duration**: 8-10 days

---

## 📊 Value Progression

### Sprint 1 Delivers:
✅ Parse existing README.md  
✅ Extract section structure  
✅ Basic pattern-based source discovery (Installation → package.json)  
✅ Generate valid template.json  
✅ User can run `doc-evergreen template reverse README.md`

**User Impact**: Can generate templates from docs TODAY (even if sources are 50% accurate)

### Sprint 2 Adds:
✅ Semantic search for source files  
✅ LLM relevance scoring (70-80% accuracy)  
✅ Smart source ranking and filtering  
✅ Handles complex section types

**User Impact**: Source discovery becomes "remotely close" - minimal manual refinement needed

### Sprint 3 Completes:
✅ Content intent analysis (LLM)  
✅ Automated prompt generation  
✅ Template validation  
✅ Full reverse → regen workflow

**User Impact**: Complete automated template generation workflow

### Sprint 4 Polishes:
✅ CLI options (--dry-run, --verbose, --output)  
✅ Error handling and edge cases  
✅ Progress feedback  
✅ Documentation

**User Impact**: Production-ready, polished user experience

---

## 🎯 Sprint Sequencing Rationale

### Why Sprint 1 First?
**End-to-end value immediately.** Even with naive source discovery (pattern matching only), users can:
- Generate valid templates from existing docs
- See the structure extraction work
- Manually refine sources if needed
- Test the concept on their own docs

This validates the approach and motivates the harder work in Sprint 2.

### Why Sprint 2 Next?
**Tackle highest risk when motivated.** After Sprint 1 proves the concept:
- Team is motivated by working prototype
- Clear understanding of what "good sources" looks like
- Day 5 checkpoint provides natural evaluation point
- Can adjust approach if accuracy is too low

### Why Sprint 3 After Source Discovery?
**Sources must be accurate before prompts.** Prompt generation relies on:
- Knowing which sources are relevant
- Understanding section content and intent
- Having confidence in the discovered context

Sprint 2's source discovery unlocks Sprint 3's prompt generation.

### Why Sprint 4 Last?
**Polish after functionality works.** CLI refinement and error handling make sense only after:
- Core pipeline is validated
- Edge cases are discovered through testing
- User workflow is understood

---

## 🚫 Deferred to v0.7.0

### Bug Fixes (P1-P2)
- **DE-5hd [P1]**: Single-shot mode not implemented → v0.5.0 embraced chunked-only
- **DE-00l [P2]**: Unclear what modes do → Low priority documentation
- **DE-1y4 [P2]**: Makefile OUTPUT parameter → Minor UX issue
- **DE-2e2 [P2]**: Misleading success message → Addressed by chunked mode

**Rationale**: Stay laser-focused on reverse template generation. None of these bugs block the v0.6.0 feature work.

### Future Enhancements
- Multi-document reverse generation
- Template learning/improvement
- Advanced validation rules
- Git integration for change detection

**Rationale**: MVP first, enhancements later based on usage patterns

---

## 🧪 Testing Strategy

### Test-Driven Development (TDD)
All sprints follow red-green-refactor cycle:
1. 🔴 RED: Write failing test
2. 🟢 GREEN: Write minimal code to pass
3. 🔵 REFACTOR: Improve code quality
4. ✅ COMMIT: All tests green

### Primary Test Case
**doc-evergreen's own README.md** - used throughout all sprints
- Known good structure
- Clear section types
- Real-world complexity
- Can validate accuracy against known sources

### Secondary Test Cases
- Simple README (Installation, Usage, Contributing)
- Complex technical doc (Architecture guide)
- Edge cases (empty sections, no relevant sources)

### Acceptance Testing
After each sprint, test the `reverse → regen` workflow:
1. Run reverse template generation
2. Review generated template
3. Run regen with generated template
4. Compare output to original
5. Measure accuracy (70-80% target)

---

## 📈 Success Metrics

### Quantitative (70-80% accuracy target)
- **Structure accuracy**: 90%+ (sections match original)
- **Source relevance**: 70-80% (sources are appropriate)
- **Prompt quality**: 70-80% (prompts would recreate similar content)

### Qualitative
- User can generate template in <2 minutes
- Manual refinement takes <5 minutes
- Regenerated doc maintains original structure
- User feels "that's close enough to refine"

---

## 🚀 Next Steps After Sprint Planning

1. **Review Sprint 1 document** in detail
2. **Set up testing environment** (doc-evergreen README as test case)
3. **Start Sprint 1 TDD** with document parser
4. **Daily progress checks** (is this on track?)
5. **Day 5 checkpoint** (is source discovery accurate enough?)

---

## 🎓 What We'll Learn

### Technical Learnings
1. **Source-content relationships**: Which files actually contribute to which doc sections?
2. **Pattern effectiveness**: Do pattern-based heuristics work for common cases?
3. **LLM accuracy**: Can LLMs score source relevance effectively?
4. **Template patterns**: What makes a good auto-generated template?

### Product Learnings
1. **Adoption enablement**: Does this remove the template creation barrier?
2. **Update workflow**: Can users now use reverse → regen for maintenance?
3. **Accuracy threshold**: Is 70-80% "close enough" or do we need 90%+?
4. **User refinement**: How much manual refinement do users actually do?

---

## ✅ Definition of Done (v0.6.0)

- ✅ `doc-evergreen template reverse <doc-path>` command works end-to-end
- ✅ Generated templates are 70-80% accurate on test cases
- ✅ Can regenerate doc-evergreen's own README with reasonable results
- ✅ All components tested with >80% coverage
- ✅ README updated with new command usage
- ✅ User can successfully use reverse → regen workflow
- ✅ Edge cases handled gracefully
- ✅ Ready for user testing and feedback

---

**Ready to start Sprint 1?** The detailed sprint documents provide step-by-step guidance for each sprint. 🚀
