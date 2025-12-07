# v0.7.0 Convergence Session Complete

**Date**: 2025-12-06  
**Branch**: dev/loop-7  
**Session Type**: Next Feature Convergence (Scenario 2)  
**Outcome**: 5 features defined for v0.7.0, 6-7 sprint timeline

---

## 🎯 Session Summary

**Starting Point:**
- ✅ v0.6.1 complete (reverse template generation working)
- Ready for next feature scope
- Initial idea: "Complete the workflow" (change detection, selective regen)

**Major Pivot During DIVERGE:**
- Realized more fundamental opportunity: generate docs FROM SCRATCH
- Shifted from "improve update workflow" to "enable fresh doc creation"
- New vision: `generate-doc` command (forward generation, not reverse)

**Final Scope:**
- 5 features for v0.7.0
- 6-7 sprints (~12-14 days)
- Focus: Hierarchical outline generation (THE core innovation)
- Outcome: End-to-end pipeline from project → outline → document

---

## 🌊 Convergence Journey

### Phase 1: DIVERGE (Exploration)

**Initial Direction: "Complete the Workflow"**
- Explored change detection & staleness awareness
- Selective section regeneration
- Automation (git hooks, CI/CD, watch mode)
- Quality validation
- Workflow orchestration

**Major Pivot: "Generate from Scratch"**

User revealed fundamental rethinking:
> "I want a `generate-doc` command that assumes NO existing document"

This sparked exploration of:
- How to create templates/outlines without existing docs?
- Two-phase generation: outline → document
- Different from `reverse` (which extracts structure from docs)
- Outline = template (unified concept, but generated not extracted)

**Deep Dive: The 6-Phase Research Paper Analogy**

User articulated complete vision as research paper writing:
1. **Intent Definition** - What doc type/purpose?
2. **Repository Indexing** - What files exist?
3. **File Review** - What's relevant to my purpose?
4. **Note-Taking** - WHY relevant and WHAT material?
5. **Outline Generation** - Create hierarchical structure ⭐ CORE
6. **Document Generation** - Fill in the content

**Key Insight:** Outline generation is THE differentiating innovation!

---

### Phase 2: CAPTURE (Organization)

Organized 6 phases into coherent feature groups:

1. **Project Analysis & Context** (Phases 1-2)
2. **File Relevance Analysis** (Phases 3-4)
3. **Hierarchical Outline Generation** (Phase 5) ⭐
4. **Nesting-Aware Doc Generation** (Phase 6)
5. **Outline Review Workflow** (Between 5-6)

Identified complexity and reuse potential per feature.

---

### Phase 3: CONVERGE (Decision)

**Scope Decision:**
- ✅ All 5 features (end-to-end pipeline)
- ✅ 6-7 sprints (larger than v0.6.0's 4 sprints)
- ✅ PRIMARY FOCUS: Feature 3 (outline generation quality)
- ✅ Supporting features: good enough to feed outline generation
- ✅ Completion features: working, doesn't need perfection

**Success Criteria:**
- 80%+ outline quality (structure feels right first try)
- 70-80% file relevance accuracy  
- Full end-to-end pipeline works
- User can review/edit outline before generation

**Template Format Changes:**
- Sources: string → object with reasoning
- Add `level` field for explicit heading levels
- Add `generation_method` metadata (forward vs reverse)
- Backward compatible with v0.6.0 templates

---

### Phase 4: DEFER (Preservation)

**Major Deferral Theme: "Complete the Workflow"**

All the original change detection, selective regen, and automation ideas deferred to v0.8.0:
- Change detection / staleness awareness
- Selective section regeneration
- Git integration
- Watch mode / CI/CD automation
- Quality validation

**Rationale:** These are update/maintenance features. They build on v0.7.0's foundation but are orthogonal to the "generate from scratch" problem.

**Generate-Doc Enhancements Deferred:**
- Bottom-up generation (use top-down DFS for v0.7.0)
- Advanced ML models (LLM-based is good enough)
- Multi-document generation (single doc first)
- Template learning (need usage data first)
- Interactive UI (JSON editing is fine for MVP)

**Total Deferred:** 15 items (3 P1, 9 P2, 3 P3)

---

## 📋 Final Feature Scope (v0.7.0)

### Feature 1: Project Analysis & Context Capture
**Sprints**: 1-2 | **Priority**: Supporting | **Complexity**: LOW-MEDIUM

CLI for doc type/purpose + repo indexing (file inventory, traversal).

---

### Feature 2: Intelligent File Relevance Analysis
**Sprints**: 3 | **Priority**: Supporting | **Complexity**: MEDIUM-HIGH

Context-aware LLM analysis: which files relevant to doc purpose? Why? What material?

---

### Feature 3: Hierarchical Outline Generation ⭐
**Sprints**: 4-5 | **Priority**: PRIMARY | **Complexity**: HIGH

Generate nested outline (H1-H6) with:
- Nesting-aware prompts (parents don't duplicate children)
- Sources with reasoning per section
- Structure from doc purpose + relevant file notes

**THIS IS THE CORE INNOVATION!** 🌟

---

### Feature 4: Nesting-Aware Document Generation
**Sprints**: 6 | **Priority**: Completion | **Complexity**: MEDIUM

Generate content respecting outline structure. Top-down DFS. LLM cannot add subsections.

---

### Feature 5: Outline Review & Iteration Workflow
**Sprints**: 7 | **Priority**: Workflow | **Complexity**: LOW

User can review/edit generated outline before doc generation. Two-command or interactive.

---

## 🎯 Key Decisions Made

### Decision 1: Outline = Template (Unified Concept)
- Not separate artifacts
- Template is a "verbose writer's outline"
- Can be generated (forward) or extracted (reverse)
- Same format, different provenance

### Decision 2: Keep `regen-doc` Separate (For Now)
- Don't break existing `regen-doc` functionality
- Build `generate-doc` separately with new template model
- Later: assess if/how to update `regen-doc`
- Strategic separation reduces risk

### Decision 3: End-to-End MVP (Not Just Outline Generation)
- Could have stopped at outline generation
- Decision: Need full pipeline to prove value
- Users need to see generated docs, not just outlines
- Success = "I generated a good doc from scratch"

### Decision 4: Primary Focus on Outline Quality
- Feature 3 (outline generation) is where v0.7.0's value comes from
- 80%+ quality target for outlines
- Other features: good enough to support this
- Don't over-invest in supporting features

### Decision 5: Top-Down DFS Generation (Defer Bottom-Up)
- Simpler approach for v0.7.0
- Bottom-up is optimization, not requirement
- Prove top-down works first
- Can revisit based on quality results

### Decision 6: Template Format Extension (Backward Compatible)
- Sources get reasoning: `{file: "...", reasoning: "..."}`
- Add explicit heading level
- Add generation metadata
- Support both old and new formats

---

## 📊 Scope Comparison

| Aspect | v0.6.0 (Reverse) | v0.7.0 (Generate) |
|--------|------------------|-------------------|
| **Problem** | Update existing docs | Create docs from scratch |
| **Input** | Existing markdown doc | Project sources + intent |
| **Process** | Extract structure | Create structure |
| **Sprints** | 4 sprints | 6-7 sprints |
| **Core Challenge** | Source discovery accuracy | Outline generation quality |
| **Innovation** | Intelligent reverse engineering | Hierarchical outline generation |
| **Output** | Template (extracted) | Template (generated) |

---

## ✅ Success Metrics (Reminder)

**Quantitative:**
- 80%+ outline quality
- 70-80% file relevance accuracy
- Full end-to-end pipeline works

**Qualitative:**
- "I can generate a doc from scratch and it's 80% right"
- "The outline is so good I barely need to edit it"
- "This is easier than manually creating templates"

**Demo Moment:**
```bash
$ cd new-project  # No docs!
$ doc-evergreen generate-doc README.md --type tutorial

🔍 Analyzing project...
📝 Generating outline...
✨ Generating documentation...
✅ README.md created!
```

---

## 🔄 What's Reusable from v0.6.0?

**High Reuse:**
- Chunked generator (adapt for nesting)
- Template schema (extend with reasoning)
- LLM patterns (apply to outline generation)

**Medium Reuse:**
- Source discovery (adapt for relevance)
- Prompt generation (make nesting-aware)

**New Components:**
- Repo indexer
- Relevance analyzer
- Hierarchical outline generator (THE HARD PART!)
- Nesting-aware orchestrator

---

## 🚀 What v0.7.0 Enables

**Together with v0.6.0:**

```
v0.6.0: "I have outdated docs"
  → reverse → template → regen → updated docs

v0.7.0: "I have NO docs"
  → generate-doc → outline → new docs

Combined Coverage:
  1. New projects (v0.7.0): Generate from scratch
  2. Existing projects (v0.6.0): Update/maintain
```

**Foundation for v0.8.0+:**
- Update workflow intelligence (change detection, selective regen)
- Automation (git hooks, CI/CD, watch mode)
- Quality & polish (validation, multi-doc, learning)

---

## 📝 Artifacts Created

1. ✅ **FEATURE_SCOPE.md** - 5 features, sprint allocation, success criteria
2. ✅ **DEFERRED_FEATURES.md** - 15 deferred items with rationale
3. ✅ **CONVERGENCE_COMPLETE.md** (this document) - Session summary

---

## 🎓 Key Learnings from This Session

### Learning 1: The Power of Pivoting During DIVERGE
- Started with "complete workflow" ideas
- User revealed deeper architectural rethinking
- Pivot led to more foundational, valuable work
- DIVERGE phase flexibility is crucial!

### Learning 2: Research Paper Analogy Clarified Everything
- User's 6-phase breakdown was incredibly clear
- Concrete process made abstract problem tangible
- Showed where complexity lives (outline generation)
- Enabled precise feature scoping

### Learning 3: "Outline = Template" Unifies Mental Model
- Not two separate artifacts
- One structure, two generation paths (forward/reverse)
- Simplifies architecture and user understanding
- Template format serves both use cases

### Learning 4: Primary Focus Clarifies Priorities
- Not all features equal importance
- Feature 3 (outline generation) is THE value
- Supporting features: good enough to enable primary
- Prevents scope creep and over-engineering

### Learning 5: End-to-End Proves Value
- Could have stopped at outline generation
- Full pipeline shows complete vision
- Users need to see docs, not just structure
- "Good enough" completion better than "perfect" partial

---

## 🎯 Next Steps

### Immediate (Today/Tomorrow):
1. ✅ Review convergence documents (FEATURE_SCOPE, DEFERRED_FEATURES, this doc)
2. 📋 Create Sprint 1 plan (Intent Capture & Repo Indexing)
3. 🏗️ Set up project structure for generate-doc feature
4. 🧪 Consider TDD approach (write tests first for each feature)

### Sprint 1 (Days 1-2):
- Feature 1: Project Analysis & Context Capture
- CLI interface for doc type/purpose
- Repository indexing
- Context storage

### Sprint 2 (Days 3-4):
- Continue Feature 1 if needed
- Begin Feature 2: File Relevance Analysis

### Mid-Point Check (After Sprint 3):
- Review relevance analysis quality
- Ensure good foundation for Feature 3
- Adjust approach if needed

### Sprint 4-5 (Days 7-11):
- **THE CRITICAL SPRINTS**
- Feature 3: Hierarchical Outline Generation
- Focus on quality (80%+ target)
- Test extensively on diverse projects

### Sprint 6 (Days 12-13):
- Feature 4: Nesting-Aware Doc Generation
- Integrate with Feature 3 output

### Sprint 7 (Day 14):
- Feature 5: Review Workflow
- End-to-end testing
- Polish & documentation

---

## 💡 Considerations for Implementation

### Technical Risks:
1. **Outline generation quality** - This is novel/hard, might need iteration
2. **LLM prompt engineering** - Nesting-aware prompts are complex
3. **Source-section mapping** - Need good reasoning, not just file lists
4. **Template format migration** - Ensure backward compatibility

### Mitigation Strategies:
1. **Test on diverse projects early** - Don't optimize for one project type
2. **Iterative prompt refinement** - Expect to tune prompts multiple times
3. **Leverage v0.6.0 learnings** - Source discovery patterns proven
4. **Version template format carefully** - Support both old/new

### Success Factors:
1. **Focus on Feature 3 quality** - This is where value comes from
2. **Don't over-engineer supporting features** - Good enough is fine
3. **Test end-to-end frequently** - Integration issues surface early
4. **Dogfood on doc-evergreen itself** - Best test case

---

## 🎉 Convergence Session Outcome

**Status:** ✅ COMPLETE

**What We Achieved:**
- Clear vision for v0.7.0 (generate-doc)
- 5 features scoped with priorities
- 6-7 sprint timeline defined
- Success criteria established
- 15 items deferred with rationale
- Template format changes defined
- Reuse strategy from v0.6.0 identified

**Confidence Level:** HIGH
- Clear problem definition
- User provided detailed vision
- Natural extension of v0.6.0 capabilities
- Feasible scope (ambitious but achievable)
- Strong foundation to build on

**Ready to Start:** YES 🚀

---

## 📚 Reference Documents

- **FEATURE_SCOPE.md** - Full feature breakdown with success criteria
- **DEFERRED_FEATURES.md** - What we explored but aren't building yet
- **v0.6.0 Sprint Plans** - Reference for sprint structure and TDD approach
- **v0.6.0 Deferred Features** - Context on what was deferred from previous release

---

**Convergence Facilitator Notes:**

This was an excellent convergence session! The user:
- ✅ Came prepared with context (v0.6.1 complete, ready for next work)
- ✅ Was open to pivoting during DIVERGE (started with workflow, pivoted to generate-doc)
- ✅ Provided incredibly detailed vision (6-phase research paper analogy)
- ✅ Made clear scope decisions (all features, 6-7 sprints, primary focus on Feature 3)
- ✅ Understood trade-offs (defer workflow features for foundational work)

The pivot from "complete the workflow" to "generate from scratch" was the key moment. It revealed a more foundational problem worth solving. The research paper analogy crystallized the vision and made feature scoping straightforward.

v0.7.0 will be a significant release that fundamentally expands doc-evergreen's capabilities. Combined with v0.6.0, it covers both major use cases: creating new docs and updating existing docs.

---

**Session Complete! Ready to begin Sprint 1. 🎯**
