# v0.6.0 Deferred Features

**Release**: v0.6.0  
**Date**: 2025-12-01  
**Deferred Count**: 9 issues + 81 backlog items

---

## 📋 Overview

During the v0.6.0 convergence, we explored two major problem spaces:

1. **"Template Creation is Too Manual"** → Original 5 template UX issues from v0.5.0 testing
2. **"Can't Update Existing Good Docs"** → New insight during DIVERGE phase

**Decision**: Focus v0.6.0 on Problem #2 (Reverse Template Generation) because:
- Solves a more fundamental adoption barrier
- Enables the "update workflow" (UC2)
- More novel/differentiating capability
- User expressed strong preference: "love love love option 3 if feasible"

This document explains what was deferred and why.

---

## 🔴 High Priority Deferrals (P0-P1)

### DE-b8p [P0]: Template Validation & Suggestions
**Original Priority**: P0 - Critical  
**Effort**: 1 day  
**Labels**: `cli`, `enhancement`, `from-v0.5.0-testing`, `templates`, `ux`

**Description:**
Validate templates and provide actionable suggestions before generation. Catches common issues (missing sources, poorly scoped sections, ineffective prompts) that only surface after wasted generation runs.

**Why Deferred:**
- Template validation is integrated into v0.6.0's reverse template generation (Feature 5: Template Assembly & Validation)
- Standalone validation feature less urgent since v0.6.0 generates validated templates automatically
- Can be enhanced as standalone command in v0.7.0 if needed

**Reconsider When:**
- v0.6.0 is complete and users need standalone validation tool
- Manual template editing becomes common again
- Template marketplace/sharing requires validation step

**Priority for v0.7.0**: P1 (if not fully covered by v0.6.0 work)

---

### DE-2t4 [P1]: Prompt Templates Library (Pre-built Patterns)
**Original Priority**: P1 - High  
**Effort**: 1 day  
**Labels**: `cli`, `enhancement`, `from-v0.5.0-testing`, `templates`, `ux`

**Description:**
Curated library of pre-built prompt patterns for common documentation sections (Overview, Installation, Usage, API Reference, Contributing, Architecture, Troubleshooting). Eliminates complex manual prompt engineering.

**Why Deferred:**
- v0.6.0's prompt generation (Feature 4) leverages prompt pattern concepts internally
- Automated prompt generation reduces need for user to manually select patterns
- Standalone library more valuable when users manually create templates

**Reconsider When:**
- v0.6.0 is complete and users want to refine generated prompts
- Manual template creation is still common
- Users request ability to swap between prompt styles

**Priority for v0.7.0**: P2 (Nice-to-have for template refinement)

---

### DE-aki [P1]: Template Scaffolding (doc-evergreen template scaffold)
**Original Priority**: P1 - High  
**Effort**: 1-2 days  
**Labels**: `cli`, `enhancement`, `from-v0.5.0-testing`, `templates`, `ux`

**Description:**
Automatically analyze project structure and generate draft templates suggesting appropriate quadrant, sections, and sources. Reduces initial template creation from hours to minutes.

**Why Deferred:**
- Different approach than reverse template generation
- Scaffolding creates templates for NEW docs (forward)
- Reverse generation creates templates from EXISTING docs (backward)
- v0.6.0 solves the more urgent problem (updating existing docs)
- These features may conflict or compete

**Reconsider When:**
- v0.6.0 reverse generation is proven and users want "forward" generation too
- Users creating docs for projects with NO existing documentation
- Can potentially merge with reverse generation (analyze project + existing docs)

**Priority for v0.7.0**: P2 (Complementary to reverse generation)

---

### DE-5hd [P1]: Single-shot mode not implemented
**Original Priority**: P1 - High  
**Effort**: TBD  
**Labels**: `cli`, `generation`, `high-priority`, `missing-feature`, `origin-issue-009`

**Description:**
CLI advertises two generation modes but single-shot mode isn't implemented. Both modes fall back to ChunkedGenerator, making --mode option misleading. Missing file: single_generator.py.

**Why Deferred:**
- Bug fix, not core feature
- Chunked mode is working well for users
- Single-shot mode benefits unclear (needs investigation)
- Not blocking adoption or critical workflows

**Reconsider When:**
- Users explicitly request single-shot mode
- Performance issues with chunked mode for small docs
- Investigation reveals clear benefit of single-shot

**Priority for v0.7.0**: P2 (Investigate first, then implement if valuable)

---

## 🟡 Medium Priority Deferrals (P2)

### DE-qyc [P2]: Interactive Template Builder (doc-evergreen template create)
**Original Priority**: P2 - Medium  
**Effort**: 2-3 days  
**Labels**: `cli`, `enhancement`, `from-v0.5.0-testing`, `templates`, `ux`

**Description:**
Interactive CLI wizard for template creation that eliminates manual JSON editing. Step-by-step guidance through all template fields with real-time validation.

**Why Deferred:**
- User explicitly stated NOT interested in interactive Q&A approach
- Reverse template generation provides automated alternative
- Interactive wizard more useful for manual template refinement (not creation)
- Higher effort (2-3 days) for less urgent problem

**Reconsider When:**
- v0.6.0 reverse generation needs refinement workflow
- Users want guided experience for tweaking generated templates
- Manual template creation is still common after v0.6.0

**Priority for v0.7.0**: P2 (Useful for refinement, not creation)

---

### DE-t6l [P2]: Smart Source Detection (Automatic Project Analysis)
**Original Priority**: P2 - Medium  
**Effort**: 1-2 days  
**Labels**: `cli`, `enhancement`, `from-v0.5.0-testing`, `templates`, `ux`

**Description:**
Automatically analyze project structure and suggest relevant source files based on section headings. Pattern matching for common needs (Installation → package.json, API Reference → public code files, etc.)

**Why Deferred:**
- **Core component of v0.6.0 reverse template generation!**
- Smart source detection is Feature 3 of v0.6.0 scope
- No need for standalone implementation - built into reverse generation
- Will be available as part of `doc-evergreen template reverse`

**Reconsider When:**
- v0.6.0 is complete and users want standalone source suggestion tool
- Manual template editing requires source discovery help
- Can extract as reusable module from v0.6.0 work

**Priority for v0.7.0**: P3 (Already in v0.6.0, may extract as standalone)

---

### DE-1y4 [P2]: Makefile regen-doc Missing OUTPUT Parameter
**Original Priority**: P2 - Medium  
**Effort**: TBD (likely < 1 hour)  
**Labels**: `makefile`, `missing-feature`, `origin-issue-010`, `ux`

**Description:**
Makefile regen-doc target doesn't expose the --output CLI option, creating incomplete feature parity between Makefile wrapper and CLI.

**Why Deferred:**
- Small bug fix, not feature
- Low impact (users can use CLI directly)
- Not blocking adoption or critical workflows
- Quick fix can be done anytime

**Reconsider When:**
- User reports this as friction point
- Makefile usage increases
- Cleaning up technical debt

**Priority for v0.7.0**: P3 (Quick fix, low urgency)

---

### DE-00l [P2]: Unclear what "chunked" vs "single-shot" modes do
**Original Priority**: P2 - Medium  
**Effort**: TBD (documentation improvement)  
**Labels**: `cli`, `documentation`, `origin-issue-008`, `ux`

**Description:**
CLI offers two modes but doesn't explain what each does, when to use them, or how they differ. Blocked by DE-5hd (single-shot not implemented).

**Why Deferred:**
- Documentation improvement, not feature
- Blocked by DE-5hd (single-shot mode doesn't exist)
- Low impact (chunked mode works for most users)
- Can be fixed quickly when DE-5hd is resolved

**Reconsider When:**
- DE-5hd (single-shot mode) is implemented
- Users confused about mode selection
- Documentation pass for v0.7.0

**Priority for v0.7.0**: P3 (Document after DE-5hd fixed)

---

### DE-2e2 [P2]: Misleading Success Message When Generated Content Contains Errors
**Original Priority**: P2 - Medium  
**Effort**: TBD  
**Labels**: `cli`, `deferred-to-v0.2.0`, `origin-issue-002`, `ux`

**Description:**
Displays "✅ Accepted: README.md updated" even when generated content contains LLM error messages. Deferred because section-by-section review in chunked mode provides alternative solution.

**Why Deferred:**
- UX polish, not core feature
- Workaround exists (section-by-section review)
- Low frequency (LLM errors are rare with good templates)
- Better addressed with content validation system

**Reconsider When:**
- Users report confusion from misleading success messages
- Content validation system is built
- LLM error rate increases

**Priority for v0.7.0**: P3 (UX polish)

---

## 💎 Backlog Deferrals (P4 - 81 items)

All 81 P4 backlog items remain deferred. Key themes:

### Template System (17 items)
**Why Deferred:** v0.6.0 focuses on template *generation*. Advanced template features (variants, marketplace, versioning) are future enhancements.

**Notable Items:**
- Template variants & specialization
- Template marketplace/community sharing
- Template lifecycle management
- Template versioning
- LLM-generated templates
- Meta-templates

**Reconsider When:** v0.6.0 template generation is proven, users need advanced template features

---

### Generation & Updates (15 items)
**Why Deferred:** v0.6.0 enables the update workflow (reverse → regen). Selective regeneration and advanced update features build on this foundation.

**Notable Items:**
- DE-a4f: Selective section regeneration
- UC2: Update existing documentation
- DE-zav: Automatic change detection
- DE-gbm: Section-to-source mapping
- DE-3b8: Incremental context updates
- DE-59x: Stability mode/variation reduction

**Reconsider When:** v0.6.0 update workflow is proven, users need more granular update control

---

### Automation (10 items)
**Why Deferred:** v0.6.0 focuses on manual workflow first. Automation (git hooks, CI/CD, watch mode) is valuable but not foundational.

**Notable Items:**
- DE-a16: Git integration
- DE-dqo: Watch mode/continuous regeneration
- DE-2h2: CI/CD integration
- Git hook integration
- Scheduled regeneration

**Reconsider When:** Users have established workflows and want automation

---

### Performance (8 items)
**Why Deferred:** Current performance is acceptable. Optimization premature without usage data.

**Notable Items:**
- Caching & reuse
- DE-82t: Performance optimization
- Parallel section generation
- Context window modes
- Progressive streaming output

**Reconsider When:** Performance becomes bottleneck for users

---

### Advanced Features (31 items)
**Why Deferred:** Core features need validation first. Advanced features are future vision.

**Notable Items:**
- Cross-repo context gathering
- DE-7hw: Multi-project documentation aggregation
- Plugin/extension system
- Review and approval workflows
- Doc health dashboard
- IDE integration
- Multi-format output

**Reconsider When:** Core features proven, users request specific advanced capabilities

---

## 🎯 v0.7.0+ Roadmap Hints

Based on deferrals, potential v0.7.0 themes:

### Theme 1: "Refinement Workflow"
- Interactive Template Builder (DE-qyc) - refine generated templates
- Template Validation (DE-b8p) - standalone validation tool
- Prompt Templates Library (DE-2t4) - swap prompt styles

### Theme 2: "Update Optimization"
- Selective section regeneration (DE-a4f)
- Automatic change detection (DE-zav)
- Section-to-source mapping (DE-gbm)
- Only regenerate sections where sources changed

### Theme 3: "Automation & Integration"
- Git integration (DE-a16)
- CI/CD integration (DE-2h2)
- Watch mode (DE-dqo)

### Theme 4: "Template Ecosystem"
- Template Scaffolding (DE-aki) - forward generation
- Template marketplace/sharing
- Template versioning

**Note**: v0.7.0 theme will be determined by v0.6.0 learnings and user feedback!

---

## 📊 Deferral Summary

| Priority | Count | Primary Reason for Deferral |
|----------|-------|----------------------------|
| P0 | 1 | Integrated into v0.6.0 |
| P1 | 3 | Less urgent than reverse generation OR integrated into v0.6.0 |
| P2 | 5 | Lower priority OR integrated into v0.6.0 |
| P4 | 81 | Future enhancements, not foundational |
| **Total** | **90** | **v0.6.0 focuses on reverse template generation** |

---

## ✅ Key Takeaway

**Why These Deferrals Make Sense:**

1. **Focus**: v0.6.0 solves ONE problem excellently (update existing docs)
2. **Integration**: Smart source detection and prompt patterns built INTO v0.6.0
3. **User Preference**: User explicitly chose reverse generation over other features
4. **Foundation**: v0.6.0 enables future work (selective regen, automation, etc.)
5. **Learning**: v0.6.0 will teach us what users actually need next

**Not deferred because they're bad** → Deferred because v0.6.0 has a clear, ambitious, valuable focus.

---

**Next Actions:**
- Update beads backlog to reflect v0.6.0 priorities
- Revisit deferred items after v0.6.0 ships based on learnings
- Gather user feedback on what matters most for v0.7.0
