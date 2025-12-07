# Sprint Plan: doc-evergreen v0.7.0 - generate-doc Command

**Release**: v0.7.0  
**Branch**: dev/loop-7  
**Timeline**: 12-14 days (6-7 sprints)  
**Philosophy**: Value-first vertical slicing + TDD

---

## 🎯 MVP Scope

**Problem**: Users starting new projects (or projects without docs) face a major barrier - they don't have existing documentation to reverse-engineer templates from. Manual template creation is tedious, and users don't know what structure, sources, or prompts to use.

**Solution**: `doc-evergreen generate-doc` - analyze project, generate intelligent hierarchical outline, create documentation from scratch.

**Success Criteria**: 
- 80%+ outline quality (structure feels right on first try)
- 70-80% file relevance accuracy
- Full end-to-end pipeline works
- Users say "the outline is so good I barely need to edit it"

---

## 🗓️ Sprint Timeline

### Sprint 1 (1-2 days): Intent Capture & CLI Foundation
**Goal**: User can specify doc type and purpose  
**Value**: Working CLI command accepting user input immediately

### Sprint 2 (1-2 days): Repository Indexing
**Goal**: Complete file inventory and traversal structure  
**Value**: System can discover and navigate all project files

### Sprint 3 (2 days): Intelligent File Relevance Analysis
**Goal**: Context-aware file analysis with note-taking  
**Value**: System identifies relevant files with reasoning (70-80% accuracy)

### Sprint 4 (2-3 days): Hierarchical Outline Generation - Core ⭐
**Goal**: Generate nested outline with nesting-aware prompts  
**Value**: THE CORE INNOVATION - intelligent structure generation

### Sprint 5 (2-3 days): Hierarchical Outline Generation - Polish ⭐
**Goal**: 80%+ outline quality with source reasoning  
**Value**: Outline quality reaches production-ready threshold

### Sprint 6 (2 days): Nesting-Aware Document Generation
**Goal**: Generate content respecting outline structure  
**Value**: Complete end-to-end generate-doc workflow works

### Sprint 7 (1-2 days): Outline Review Workflow
**Goal**: User can review/edit outline before generation  
**Value**: Production-ready two-command workflow

**Total Duration**: 12-14 days

---

## 📊 Value Progression

### Sprint 1 Delivers:
✅ CLI command structure for generate-doc  
✅ Doc type selection (tutorial/howto/reference/explanation)  
✅ Purpose capture (freeform text)  
✅ Context storage (.doc-evergreen/context.json)

**User Impact**: Can start using the command TODAY (even if it doesn't generate yet)

### Sprint 2 Adds:
✅ Complete repository file inventory  
✅ Respects .gitignore/.docignore  
✅ Efficient file traversal structure  
✅ Integration with Sprint 1 context

**User Impact**: System can analyze entire project automatically

### Sprint 3 Adds:
✅ LLM-powered file relevance analysis  
✅ Context-aware relevance scoring (70-80% accuracy)  
✅ Per-file reasoning notes (why relevant, what material)  
✅ Annotated file list output

**User Impact**: System intelligently identifies which files matter for the doc

### Sprint 4 Delivers:
✅ Basic hierarchical outline generation  
✅ Nested structure support (H1-H6)  
✅ Section-to-source mapping  
✅ Initial nesting-aware prompts

**User Impact**: First working outline generation (may need polish)

### Sprint 5 Completes:
✅ 80%+ outline quality  
✅ Sophisticated nesting-aware prompts  
✅ Source reasoning per section  
✅ Doc-type-appropriate structure  
✅ Deep nesting support validated

**User Impact**: Outline quality reaches "barely need to edit" level ⭐

### Sprint 6 Completes:
✅ Top-down DFS content generation  
✅ Three-component LLM context (prompt + relevancy + sources)  
✅ Structure-locked generation  
✅ Complete document assembly  
✅ Full end-to-end pipeline works

**User Impact**: Can generate complete documentation from scratch!

### Sprint 7 Polishes:
✅ Two-command workflow (generate-outline + generate-from-outline)  
✅ Outline review/edit capability  
✅ CLI polish and error handling  
✅ Documentation and examples

**User Impact**: Production-ready user experience

---

## 🎯 Sprint Sequencing Rationale

### Why Sprint 1-2 First (Foundation)?
**Build the data pipeline first.** Before any intelligence can work:
- Need to capture user intent (what doc to create)
- Need to discover all project files
- Need to store context for downstream features

These are quick wins (1-2 days each) that provide solid foundation.

### Why Sprint 3 Next (Supporting)?
**Understand relevance before generating structure.** File relevance analysis:
- Must happen before outline generation (need to know what's relevant)
- Provides critical input to Sprint 4-5 (outline generators)
- Can be validated independently (70-80% accuracy target)

This is a natural checkpoint - if relevance is poor, outline will be poor.

### Why Sprint 4-5 Together (Core Innovation)?
**Give proper time to the hardest problem.** Hierarchical outline generation:
- IS THE CORE INNOVATION of v0.7.0 🌟
- Requires sophisticated LLM orchestration
- Needs iteration to reach 80%+ quality
- Worth 4-6 days of focused effort

Split into two sprints:
- Sprint 4: Get it working (basic outline)
- Sprint 5: Make it excellent (80%+ quality)

This allows mid-point evaluation and adjustment.

### Why Sprint 6 After Outline?
**Can't generate without good outline.** Document generation:
- Depends on outline structure (structure must be locked)
- Reuses patterns from v0.6.0 (lower risk)
- Is simpler than outline generation (already know what to generate)

Once outline is excellent, generation is straightforward.

### Why Sprint 7 Last (Polish)?
**Polish after functionality works.** Review workflow:
- Only makes sense after full pipeline works
- Enables user refinement of generated outlines
- Completes the production-ready experience

---

## 🧪 Testing Strategy

### Test-Driven Development (TDD)
All sprints follow red-green-refactor cycle:
1. 🔴 RED: Write failing test
2. 🟢 GREEN: Write minimal code to pass
3. 🔵 REFACTOR: Improve code quality
4. ✅ COMMIT: All tests green

### Primary Test Case
**doc-evergreen's own documentation generation** - used throughout sprints 4-7:
- Real-world complexity
- Can dogfood the feature
- Known structure to validate against
- Clear success/failure criteria

### Secondary Test Cases
- Simple Python CLI project (tutorial)
- Python library (reference docs)
- Web API project (howto guides)
- Edge cases (minimal project, no clear structure)

### Acceptance Testing
After Sprint 6, test the full `generate-doc` workflow:
1. Run generate-doc with various doc types
2. Review generated outline quality
3. Review generated document quality
4. Measure accuracy (80%+ outline, 70-80% relevance)

---

## 🚫 Deferred to v0.8.0

### From Original "Complete Workflow" Ideas
- Change detection / staleness awareness → v0.8.0
- Selective section regeneration → v0.8.0
- Git integration / CI/CD automation → v0.8.0
- Watch mode / continuous docs → v0.8.0

**Rationale**: v0.7.0 focuses on "generate from scratch" problem. Update workflow ideas are valuable but orthogonal.

### From Generate-Doc Scope
- Bottom-up generation (deepest sections first) → Defer, use top-down DFS
- Advanced relevance ML models → Start with LLM-based analysis
- Multi-document generation → Single doc first
- Template learning/improvement → Static generation first

**Rationale**: Deliver working MVP first, optimize later based on real usage.

---

## 📈 Success Metrics

### Quantitative (Sprint 5 Checkpoint)
- **Outline quality**: 80%+ (structure feels right first try)
- **Source relevance**: 70-80% (files are appropriate)
- **Section prompts**: 80%+ (prompts are nesting-aware and useful)
- **Test coverage**: >80% for all new code

### Qualitative (End of Sprint 7)
- "I can generate a doc from scratch and it's 80% right"
- "The outline is so good I barely need to edit it"
- "This is easier than manually creating templates"
- "Outline generation feels intelligent and context-aware"

### Demo Moment (Sprint 6 Complete)
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

### High Reuse (Adapt)
- ✅ `chunked_generator.py` - Content generation (adapt for nesting awareness)
- ✅ `template_schema.py` - Template format (extend with source reasoning, level)
- ✅ LLM patterns from `reverse/` - Prompt engineering approaches

### Medium Reuse (Conceptual)
- 🔄 `intelligent_source_discoverer.py` - File relevance analysis (adapt for context-aware)
- 🔄 `prompt_generator.py` - Prompt creation (make nesting-aware)
- 🔄 `semantic_source_searcher.py` - Source discovery patterns

### New Components (Build Fresh)
- 🆕 Repo indexer (file inventory, traversal)
- 🆕 Context-aware relevance analyzer (with note-taking)
- 🆕 Hierarchical outline generator (THE CORE INNOVATION! ⭐)
- 🆕 Nesting-aware generation orchestrator

---

## ✅ Definition of Done (v0.7.0)

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

## 🚀 Next Steps After Sprint Planning

1. **Review Sprint 1 document** in detail
2. **Set up development environment** for new command
3. **Start Sprint 1 TDD** with CLI interface
4. **Daily progress checks** (is this on track?)
5. **Sprint 4-5 checkpoint** (is outline quality reaching 80%+?)
6. **Sprint 6 validation** (does end-to-end workflow work?)

---

## 🎓 What We'll Learn

### Technical Learnings
1. **Outline generation patterns**: How to create intelligent nested structures
2. **Nesting-aware prompting**: How to prevent parent/child content duplication
3. **Context-aware relevance**: Which files matter for which doc types
4. **LLM orchestration**: How to chain multiple LLM calls effectively

### Product Learnings
1. **Adoption enablement**: Does this remove the "starting from scratch" barrier?
2. **Accuracy threshold**: Is 80% outline quality "good enough"?
3. **User refinement**: How much manual editing do users actually do?
4. **Value proposition**: Do users prefer generate-doc or reverse templates?

---

**Ready to start Sprint 1?** The detailed sprint documents provide step-by-step guidance for each sprint. 🚀
