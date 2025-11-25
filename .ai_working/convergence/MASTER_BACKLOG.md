# doc_evergreen - Master Feature Backlog

**Purpose**: Consolidated backlog of ALL deferred features from all convergence sessions. This is the single source of truth for what's been explored, what's deferred, and what's been implemented.

**Philosophy**: Nothing is lost. Ideas wait here until the right "reconsider when" conditions are met.

**Last Updated**: 2025-11-24

---

## Overview

| Category | Count | Notes |
|----------|-------|-------|
| **Implemented** | 18 features | Sprints 1-7 (v0.1.0-v0.2.0), Sprints 8-10 (v0.3.0), v0.4.0-v0.4.1 |
| **Problem A Deferred** | 23 features | From template-system convergence |
| **Problem B Deferred** | 13 features | From chunked-generation convergence |
| **Test Case Deferred** | 21 features | From test-case-basic-regen convergence |
| **Standalone Tool Deferred** | 15 features | From 2025-11-20 standalone-tool convergence |
| **Transcript Ideas** | 14 features | From 2025-11-19 conversation with Marc |
| **Template Library Deferred** | 12 features | From 2025-11-24 template-library convergence |
| **Total Backlog** | 98 features | Available for future releases |

---

## ✅ Implemented Features

### Problem A (v0.1.0 - Template System - Sprints 1-4)
- [x] Template-based document structure
- [x] Source resolution (glob patterns)
- [x] Hierarchical source inheritance
- [x] Single-shot full-document generation
- [x] Preview & accept workflow

### Problem B (v0.2.0 - Chunked Generation - Sprints 5-7)
- [x] Section-level prompts (explicit control)
- [x] Sequential DFS generation
- [x] Context flow between sections
- [x] Section review checkpoints
- [x] Source validation (ISSUE-001 fix)
- [x] Source visibility (ISSUE-003 fix)

### Test Case (v0.3.0 - Basic Regeneration - Sprints 8-10)
- [x] Template-based regeneration (JSON templates)
- [x] Change detection (unified diff)
- [x] Manual regeneration command (`regen-doc`)
- [x] Diff preview with user approval
- [x] Progress feedback during generation
- [x] Iterative refinement workflow
- [x] Source specification per section
- [x] Comprehensive documentation (TEMPLATES.md, USER_GUIDE.md, BEST_PRACTICES.md)
- [x] Real-world template examples
- [x] Integration testing (70 tests)

### Standalone Tool (v0.4.0 - Convention-Based)
- [x] Proper Python package (pyproject.toml + entry point)
- [x] Convention-based discovery (cwd = project root)
- [x] Template directory convention (`.doc-evergreen/`)
- [x] Init command (bootstrap projects)
- [x] Updated documentation for standalone usage

### Bug Fixes (v0.4.1)
- [x] Critical: Glob patterns excluding .venv and node_modules
- [x] Smart default exclusions for non-project directories
- [x] Init command generates focused source patterns

---

## 🔄 Active Deferred Features

### Template Library Deferred (from 2025-11-24 convergence)

**Convergence**: [2025-11-24-template-library](./2025-11-24-template-library/)
**Version Planned**: v0.5.0 (Template Library & Prompt Quality)

#### 1. Smart Template Suggestions (AI-Powered)
- **Reconsider When**: Template library (v0.5.0) exists and patterns emerge for which templates work for which repos
- **Effort**: 2-3 days
- **Value**: AI analyzes repo and suggests best template with reasoning
- **Notes**: Needs template library as foundation first

#### 2. Multi-Variant Generation
- **Reconsider When**: Template library exists and users still uncertain which to use
- **Effort**: 3-4 days
- **Value**: Generate 3 versions simultaneously, compare side-by-side
- **Notes**: Increases API costs (3x), needs good templates first

#### 3. Selective Section Regeneration
- **Reconsider When**: Full doc regeneration is slow (>2 minutes) or users frequently want to update just one section
- **Effort**: 2-3 days
- **Value**: Regenerate only specific sections, faster and more controlled
- **Notes**: Requires section-to-source mapping, separate focus area

#### 4. Stability Mode (Variation Reduction)
- **Reconsider When**: Template improvements (v0.5.0) don't reduce variation enough, or users get wildly different output with same template
- **Effort**: 2-3 days
- **Value**: Include current content in prompts to minimize unnecessary changes
- **Notes**: Needs research on variation root cause first

#### 5. Template Validation/Pre-flight Check
- **Reconsider When**: Template library usage reveals common mistakes, or clear patterns emerge (">X sources = too long")
- **Effort**: 1-2 days
- **Value**: Warn about potential issues before generation
- **Notes**: Needs usage data to establish heuristics

#### 6. Interactive Template Builder (Wizard)
- **Reconsider When**: Template library doesn't cover user needs or users struggle to customize templates
- **Effort**: 2-3 days
- **Value**: CLI wizard asks questions and builds custom template
- **Notes**: May not be better than picking from library

#### 7. Template Versioning
- **Reconsider When**: Template format changes break old templates
- **Effort**: 1-2 days
- **Value**: Version compatibility management
- **Notes**: Format is stable, no breaking changes anticipated

#### 8. Smart Change Detection (Source Tracking)
- **Reconsider When**: Selective regeneration exists and users manually track which sections to update
- **Effort**: 2-3 days
- **Value**: Track which sources changed, auto-determine which sections need updating
- **Notes**: Requires selective regeneration (Feature #3) first

#### 9. Output Length Feedback (Post-Generation)
- **Reconsider When**: Template improvements aren't sufficient or length issues persist
- **Effort**: 1 day
- **Value**: Show per-section statistics and suggest improvements after generation
- **Notes**: Reactive rather than proactive (better to fix templates)

#### 10. Template Marketplace / Sharing
- **Reconsider When**: Multiple projects use similar templates or users ask "where can I find templates for X?"
- **Effort**: 1-2 weeks
- **Value**: Community template sharing and discovery
- **Notes**: Infrastructure needed, unclear if templates are reusable across projects

#### 11. CI/CD Template Auto-Update
- **Reconsider When**: Tool is production-stable (1.0+) and users manually regenerate after every commit
- **Effort**: 2-3 days
- **Value**: Automatically regenerate docs in CI, create PR
- **Notes**: Requires stability mode for predictability

#### 12. Performance Optimization (Caching, Parallelization)
- **Reconsider When**: Generation takes >30s per section consistently or API costs become significant
- **Effort**: 2-3 days
- **Value**: Faster regeneration, lower costs
- **Notes**: No evidence of performance issues currently

---

### Standalone Tool Deferred (from 2025-11-20 convergence)

**Convergence**: [2025-11-20-standalone-tool](./2025-11-20-standalone-tool/)

#### 1. PyPI Publishing
- **Reconsider When**: 10+ external users requesting pip install
- **Effort**: 1-2 days
- **Value**: Easier discovery and installation

#### 2. Advanced Template Discovery
- **Reconsider When**: Users request mono-repo support or template sharing
- **Effort**: 3-4 hours
- **Value**: Multi-project template management

#### 3. Project-Level Config File
- **Reconsider When**: Users have 5+ templates with duplicated settings
- **Effort**: 2-3 hours
- **Value**: Reduce configuration duplication

#### 4. Template Marketplace
- **Reconsider When**: 5+ projects documented, common patterns emerge
- **Effort**: 1-2 days
- **Value**: Community template sharing

#### 5. Watch Mode / Auto-Regeneration
- **Reconsider When**: Users report frequent manual regeneration friction
- **Effort**: 4-6 hours
- **Value**: Automated doc updates on file changes

#### 6. CI/CD Integration Helpers
- **Reconsider When**: Multiple users implementing CI/CD, patterns emerge
- **Effort**: 3-4 hours
- **Value**: Pre-built workflow templates

#### 7. Multi-Project Aggregation
- **Reconsider When**: User requests "document my mono-repo"
- **Effort**: 1-2 days
- **Value**: Cross-project documentation

#### 8. IDE Integration
- **Reconsider When**: Tool widely adopted, users request editor integration
- **Effort**: 1-2 weeks
- **Value**: In-editor documentation workflow

#### 9. Git Integration
- **Reconsider When**: Users consistently forget to commit docs
- **Effort**: 4-6 hours
- **Value**: Automated git operations

#### 10. Single-Shot Mode (ISSUE-009)
- **Reconsider When**: Performance issues with chunked mode
- **Effort**: 1 day
- **Value**: Alternative generation strategy

#### 11. Mode Clarity Documentation (ISSUE-008)
- **Reconsider When**: Single-shot mode implemented
- **Effort**: 2-3 hours
- **Value**: Clear mode selection guidance

#### 12. Template Versioning
- **Reconsider When**: Template format changes break old templates
- **Effort**: 4-6 hours
- **Value**: Version compatibility management

#### 13. Dry-Run Mode
- **Reconsider When**: Users want preview without generation cost
- **Effort**: 2-3 hours
- **Value**: Zero-cost preview

#### 14. Backup/Rollback
- **Reconsider When**: Users report data loss incidents
- **Effort**: 4-6 hours
- **Value**: Safety net for overwrite protection

#### 15. Performance Optimization
- **Reconsider When**: Generation takes >30s per section consistently
- **Effort**: 1-2 days
- **Value**: Faster generation for large projects

---

## Previously Deferred Features

### Problem B - Phase 2: Post-Order Validation (After v0.2.0)

**Reconsider When**: v0.2.0 proves chunked generation works but reveals consistency issues

#### 1. Post-Order Validation and Updates
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: After generating all sections, validate consistency and update earlier sections
**Why Valuable**: Earlier sections can reference later concepts, ensures document-wide consistency
**Complexity**: High (bidirectional flow, state management)
**Reconsider When**:
- Users frequently edit earlier sections after seeing later ones
- Inconsistencies between sections are common (>20% of docs)
- Users request "make Introduction match Features" explicitly

#### 2. Sibling Consistency Checks
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Validate sibling sections don't overlap, complement each other
**Why Valuable**: Prevents duplicate content, ensures coverage
**Complexity**: Medium
**Reconsider When**:
- Overlapping content appears frequently (>10% of docs)
- Users manually check for gaps/overlaps
- Clear validation rules emerge

#### 3. Tree Backtracking (Iterative Refinement)
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Multiple passes to refine sections
**Why Valuable**: Higher quality through iterative improvement
**Complexity**: High (convergence criteria, loop control)
**Reconsider When**:
- Single-pass quality is consistently insufficient (<70% acceptable)
- Users frequently regenerate entire docs for minor fixes

---

### Problem B - Phase 3: Dynamic & Adaptive (After Phase 2)

**Reconsider When**: Phase 2 is implemented and static templates prove too rigid

#### 4. Dynamic Tree Growth
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: LLM proposes new sections during generation, user approves
**Why Valuable**: Adapts structure to content
**Complexity**: High (LLM proposals, tree modification)
**Reconsider When**:
- Users frequently add sections manually after generation (>30% of docs)
- Template structure proves too rigid

#### 5. State Management / Resume Capability
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Save progress, resume from checkpoint if interrupted
**Why Valuable**: Handle long-running generations, recover from interruptions
**Complexity**: Medium (state serialization)
**Reconsider When**:
- Generation regularly takes >10 minutes
- Interruptions are common problem

#### 6. Advanced Forward Reference Handling
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Sophisticated forward reference management
**Why Valuable**: Natural technical writing patterns
**Complexity**: Medium
**Reconsider When**:
- Basic forward reference validation proves insufficient
- Complex cross-reference needs emerge

---

### Problem B - Optimizations (Performance/UX)

**Reconsider When**: Core functionality works well, performance becomes bottleneck

#### 7. Parallel Section Generation
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Generate independent sections simultaneously
**Why Valuable**: 2-5x faster generation
**Complexity**: Medium (dependency management)
**Reconsider When**:
- Generation time >5 minutes regularly
- Clear independent sections identified

#### 8. Context Window Modes
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Adaptive context sizing (minimal/standard/comprehensive)
**Why Valuable**: Balance between quality and cost
**Complexity**: Low
**Reconsider When**:
- Token costs become significant
- Context strategies show clear trade-offs

#### 9. Smart Section Ordering
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Optimal generation order based on dependencies
**Why Valuable**: Better context flow
**Complexity**: Medium (dependency analysis)
**Reconsider When**:
- Template order proves suboptimal frequently
- Dependency patterns are clear

---

### Problem B - Advanced Features

**Reconsider When**: All Phase 2 and Phase 3 features implemented, need next evolution

#### 10. Multi-Document Coordination
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Generate multiple related documents with consistency
**Why Valuable**: Documentation suites with cross-references
**Complexity**: High (cross-doc coordination)
**Reconsider When**:
- Users maintain 5+ related docs
- Cross-doc consistency is manual

#### 11. Template Learning from Generated Content
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Improve templates based on what works
**Why Valuable**: Templates evolve with usage
**Complexity**: High (ML/pattern recognition)
**Reconsider When**:
- Clear patterns in successful vs unsuccessful generations
- Template refinement is manual and tedious

---

### Test Case - Phase 2: Automation & Triggers (After Manual Flow Works)

**Reconsider When**: Basic regeneration flow (manual trigger) proves valuable and is used for 10+ regenerations

**Origin**: Test Case convergence (2025-11-19-test-case-basic-regen)

#### 37. Automatic Change Detection
**What**: Detect when source files have changed and determine if documentation needs updating
**Why Valuable**: Eliminates "should I regenerate?" decision overhead. Proactive maintenance.
**Complexity**: Medium (file watching, git integration, heuristics)
**Reconsider When**:
- Manual regeneration used 10+ times successfully
- Users repeatedly ask "how do I know when to regenerate?"
- Checking "should I regenerate?" becomes tedious

#### 38. Git Hook Integration
**What**: Automatically trigger regeneration on git events (pre-commit, post-merge, etc.)
**Why Valuable**: Docs stay in sync with code changes without manual intervention
**Complexity**: Medium (git hooks, performance, user control)
**Reconsider When**:
- Manual regeneration becomes routine part of git workflow
- Users report "I forgot to regenerate before committing" 3+ times
- Git integration patterns emerge from actual usage

#### 39. Watch Mode
**What**: Continuously monitor source files, regenerate on changes
**Why Valuable**: Real-time doc updates during development
**Complexity**: Medium (file watching, debouncing, resource usage)
**Reconsider When**:
- Users manually regenerate multiple times during single dev session
- "I want docs to update as I code" explicitly requested
- Clear use cases for continuous regeneration emerge

#### 40. Scheduled Regeneration
**What**: Cron-like scheduled regeneration (daily, weekly, on release, etc.)
**Why Valuable**: Ensures docs stay fresh even if manual trigger forgotten
**Complexity**: Low (cron integration, scheduling config)
**Reconsider When**:
- Docs fall stale between releases despite manual trigger availability
- Users request "regenerate all docs weekly" explicitly
- CI/CD integration emerges as clear use case

---

### Test Case - Phase 3: Multi-Document Operations (After Single-Doc Works)

**Reconsider When**: Single-document regeneration proves solid, users maintain 5+ docs

**Origin**: Test Case convergence (2025-11-19-test-case-basic-regen)

#### 41. Batch Regeneration
**What**: Regenerate multiple documents in one command: `amplifier regen-doc amplifier/*.md`
**Why Valuable**: Efficient when multiple docs reference same sources
**Complexity**: Medium (batch processing, error handling, progress UI)
**Reconsider When**:
- Users manage 5+ template-based docs
- Manually regenerating docs one-by-one becomes tedious
- Clear patterns emerge for "regenerate all project docs"

#### 42. Multi-Document Orchestration
**What**: Coordinate regeneration across related documents (e.g., README references API docs)
**Why Valuable**: Maintains consistency across documentation suite
**Complexity**: High (dependency tracking, ordering, consistency validation)
**Reconsider When**:
- Users maintain documentation suites with clear cross-references
- Inconsistencies across docs become pain point
- Dependency patterns are well understood

#### 43. Workspace-Wide Regeneration
**What**: One command to regenerate all docs in entire workspace: `amplifier regen-all`
**Why Valuable**: Ultimate convenience for "update everything"
**Complexity**: Medium (discovery, batch processing, configuration)
**Reconsider When**:
- Users manage 10+ docs across multiple projects
- "Regenerate everything" is frequent operation
- Clear conventions for template discovery emerge

---

### Test Case - Phase 4: Advanced Features (Long-Term)

**Reconsider When**: Core functionality mature, advanced needs emerge

**Origin**: Test Case convergence (2025-11-19-test-case-basic-regen)

#### 44. Partial/Selective Updates
**What**: Update only specific sections: `amplifier regen-doc README.md --section Features`
**Why Valuable**: Faster regeneration, less review overhead
**Complexity**: Medium (section targeting, context management)
**Reconsider When**:
- Full-doc regeneration takes >1 minute regularly
- Users frequently discard most changes (only 1-2 sections meaningful)
- Section-level granularity clearly valuable

#### 45. Human Edit Preservation
**What**: Detect human edits in generated docs, preserve across regenerations
**Why Valuable**: Allows manual fixes without losing on next regeneration
**Complexity**: High (diff analysis, merge logic, conflict resolution)
**Reconsider When**:
- Users frequently lose manual edits after regeneration
- Clear patterns emerge for "preserve this section"
- Template-based fixes prove insufficient for edge cases

#### 46. Configuration Files
**What**: Project-wide config for regeneration defaults, LLM settings, source paths
**Why Valuable**: Reduces command-line verbosity, shares settings across team
**Complexity**: Low (config file parsing, precedence rules)
**Reconsider When**:
- Users pass same flags repeatedly (>5 times)
- Team members need shared settings
- Clear configuration needs emerge from usage

#### 47. Review/Approval Workflows
**What**: Multi-stage approval (generate → review → approve → commit) with audit trail
**Why Valuable**: Quality gates, team coordination, accountability
**Complexity**: High (workflow state, multi-user, notifications)
**Reconsider When**:
- Multiple team members regenerate same docs
- Quality control becomes necessary (approval before merge)
- Audit requirements emerge

#### 48. Smart Structure Discovery
**What**: LLM analyzes existing docs, proposes template structure automatically
**Why Valuable**: Reduces manual template creation effort
**Complexity**: High (structure analysis, LLM prompting, validation)
**Reconsider When**:
- Users have created 10+ templates manually
- Clear patterns in successful templates emerge
- Template creation is major friction point

#### 49. LLM-Generated Templates
**What**: Ask LLM to create template from scratch: `amplifier create-template README --type project-readme`
**Why Valuable**: Ultimate convenience for template creation
**Complexity**: Medium (template generation, validation)
**Reconsider When**:
- Manual template creation is well-understood
- Template patterns are codified
- Users explicitly request "generate template for me"

#### 50. Interactive Template Creation Wizard
**What**: CLI wizard to create templates through Q&A: "What type of doc? What sections? What sources?"
**Why Valuable**: Guided template creation with less friction
**Complexity**: Medium (wizard UI, template generation)
**Reconsider When**:
- Manual template creation has clear friction points
- Template patterns are codified enough to guide
- Users explicitly request "help me create template"

---

### Test Case - Optimizations (Performance/UX)

**Reconsider When**: Core functionality works well, performance/UX becomes bottleneck

**Origin**: Test Case convergence (2025-11-19-test-case-basic-regen)

#### 51. Prompt Versioning System
**What**: Version and evolve LLM prompts, track which work best
**Why Valuable**: Improves generation quality over time
**Complexity**: Medium (versioning, analytics, A/B testing)
**Reconsider When**:
- Users frequently tweak prompts for better results
- Clear improvements to prompts emerge
- Quality varies significantly across regenerations

#### 52. Relevancy Scoring
**What**: Score each source file 1-10 for relevance to doc, include only high-scoring sources
**Why Valuable**: Reduces context size, improves focus, lowers cost
**Complexity**: Medium (scoring heuristics, thresholds)
**Reconsider When**:
- Templates regularly include irrelevant sources (>30% unused)
- Context size becomes problem (hitting LLM limits)
- Cost optimization becomes priority

#### 53. Caching/Efficiency Optimizations
**What**: Cache unchanged source content, skip sections that haven't changed, reuse context
**Why Valuable**: Faster regeneration, lower cost
**Complexity**: Medium (cache invalidation, change detection)
**Reconsider When**:
- Regeneration time >30 seconds regularly
- Cost becomes significant (>$1 per regeneration)
- Clear caching opportunities identified

#### 54. Incremental Context Updates
**What**: Track which sources changed since last regeneration, only update relevant context
**Why Valuable**: Efficiency for large source bases
**Complexity**: Medium (change tracking, context diff)
**Reconsider When**:
- Source bases are large (>50 files)
- Full context gathering takes >10 seconds
- Incremental updates clearly faster

#### 55. Progressive/Streaming Output
**What**: Show generated content as it streams from LLM, not just at completion
**Why Valuable**: Better UX for slow generations, see progress
**Complexity**: Medium (streaming, terminal UI)
**Reconsider When**:
- Regeneration regularly takes >30 seconds
- Users report feeling "is this working?" during generation
- Streaming UX clearly valuable

---

### Test Case - Parking Lot (Unclear Fit)

**Reconsider When**: Specific use cases emerge through real usage

**Origin**: Test Case convergence (2025-11-19-test-case-basic-regen)

#### 56. Template Marketplace
**What**: Share/discover templates created by others
**Why Uncertain**: Unclear if templates are reusable across projects, what marketplace would look like
**Next Step**: Understand template reusability through usage first
**Reconsider When**:
- Users create 5+ templates and want to share
- Clear demand for "standard templates" emerges
- Reusability patterns are understood

#### 57. Plugin/Extension System
**What**: Allow custom source readers, LLM providers, output formatters
**Why Uncertain**: Unclear what needs extending. May be premature abstraction
**Next Step**: Identify what users want to customize beyond core capabilities
**Reconsider When**:
- Users request custom functionality 3+ times
- Clear extension points emerge
- Core system proves insufficient for edge cases

---

### Problem A - Version 2 (High Priority)

**Reconsider When**: Template system (v0.1.0) is in active use

#### 58. Automatic Change Detection (Problem A Version)
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Detect when source files changed, determine if docs need updating
**Why Valuable**: Proactive doc maintenance
**Complexity**: Medium (git hooks, heuristics)
**Reconsider When**:
- MVP used for 10+ docs
- Manually checking "should I regenerate?" becomes tedious

#### 59. Template Lifecycle Management
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Create, evolve, and manage templates over time
**Why Valuable**: Templates improve through use
**Complexity**: Medium (versioning, analytics)
**Reconsider When**:
- User has created 3+ templates manually
- Template editing becomes frequent

#### 60. Intelligent Source Discovery
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Auto-identify relevant source files
**Why Valuable**: Eliminates manual source specification
**Complexity**: High (code analysis, dependency tracking)
**Reconsider When**:
- User has regenerated 10+ docs with manual sources
- Manual source specification is primary pain point

#### 61. Automated Quality Validation
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Check generated doc quality against criteria
**Why Valuable**: Catches issues before user review
**Complexity**: Medium (define criteria, implement checks)
**Reconsider When**:
- 5+ successful regenerations show common quality patterns
- User checks same things repeatedly

#### 62. Git Integration (Problem A Version)
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Version control integration for doc history
**Why Valuable**: See evolution, rollback if needed
**Complexity**: Low (git commands, commit messages)
**Reconsider When**:
- User has regenerated same doc 3+ times
- Rollback becomes necessary

#### 63. Template Variants & Specialization
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Multiple templates for different doc types
**Why Valuable**: Specialization improves quality
**Complexity**: Medium (template library, selection)
**Reconsider When**:
- Single template proves insufficient
- User creates 3+ different templates

---

### Problem A - Future Enhancements (Medium Priority)

**Reconsider When**: Version 2 features are implemented, need next capabilities

#### 64-80. (23 total features from Problem A)
See `convergence/2025-11-18-problem-a-template-system/DEFERRED_FEATURES.md` for complete list including:
- Meta-templates & template generation
- Cross-file relationship tracking
- Selective section regeneration
- Multi-format output
- AI-curated source selection
- Incremental context updates
- Collaboration features
- Doc health dashboard
- Background processing
- Rich preview UI
- Undo/redo support
- Caching & reuse
- Template marketplace (parking lot)
- Hooks & extensions (parking lot)
- LLM learning (parking lot)
- Doc publishing integration (parking lot)
- Testing & validation framework (parking lot)

---

## 📊 Backlog Statistics

### By Phase
- **v0.1.0 (Implemented)**: 5 features (Problem A)
- **v0.2.0 (Implemented)**: 6 features (Problem B)
- **v0.3.0 (Planned)**: 5 features (Test Case - Basic Regeneration)
- **Phase 2 (Problem B)**: 3 features
- **Phase 3 (Problem B)**: 3 features
- **Optimizations (Problem B)**: 3 features
- **Advanced (Problem B)**: 2 features
- **Phase 2 (Test Case)**: 4 features (Automation & Triggers)
- **Phase 3 (Test Case)**: 3 features (Multi-Document)
- **Phase 4 (Test Case)**: 7 features (Advanced)
- **Optimizations (Test Case)**: 5 features (Performance/UX)
- **Parking Lot (Test Case)**: 2 features
- **Version 2 (Problem A)**: 6 features
- **Future (Problem A)**: 17 features

### By Complexity
- **Low**: ~8 features
- **Medium**: ~30 features
- **High**: ~19 features

### By Origin
- **Problem A** (Template System): 23 deferred features
- **Problem B** (Chunked Generation): 13 deferred features
- **Test Case** (Basic Regeneration): 21 deferred features

---

## 🎯 Prioritization Framework

Features move from backlog to active development when:

1. **"Reconsider When" conditions are met** (data-driven triggers)
2. **User pain is validated** (multiple requests, clear patterns)
3. **MVP learning is complete** (we understand the problem space)
4. **Complexity is justified** (value > implementation cost)

### Current Priority Queue

**Active Development (v0.3.0 - Test Case)**:
1. Template-based generation
2. Source context gathering
3. Manual regeneration command
4. Structure preservation
5. Change detection

**Next Up After v0.3.0**:
- **If manual flow proves valuable** (used 10+ times):
  - Test Case Phase 2 (Automation & Triggers)
- **If consistency issues emerge in v0.2.0**:
  - Problem B Phase 2 (Post-order validation)
- **If template system (v0.1.0) sees heavy use**:
  - Problem A Version 2 features

**Watching for Triggers**:
- Test Case automation needs
- Problem B consistency patterns
- Problem A template management needs

**Parking Lot**:
- All other features wait for "reconsider when" conditions

---

### Transcript Ideas (from 2025-11-19 conversation)

**Origin**: Discussion with Marc about doc-evergreen evolution
**Convergence**: 2025-11-24-transcript-ideas

#### 81. Update Existing Documentation (UC2)
**Origin**: 2025-11-19-transcript-ideas
**What**: Regenerate existing docs when source files change, preserving stable sections
**Why Valuable**: Keep docs in sync with code without manual tracking
**Complexity**: High (requires change detection, section mapping, stability tracking)
**Reconsider When**:
- MVP used successfully for 5+ initial doc creations
- Users manually update docs and wish they could automate it
- Code changes and docs drift out of sync

#### 82. Include Existing Content in Regeneration (UC2 - Update Flow)
**Origin**: 2025-11-19-transcript-ideas
**What**: When regenerating a section, include its current content as context for LLM
**Why Valuable**: Prevents unnecessary changes, maintains writing style, improves stability
**Complexity**: Medium (section extraction, prompt engineering)
**Reconsider When**:
- Update flow exists but produces too much churn
- Regenerated sections lose valuable context or style
- Users complain about unnecessary rewrites

#### 83. Relevance Check Before Regeneration (UC2 - Update Flow)
**Origin**: 2025-11-19-transcript-ideas
**What**: Check if code changes actually affect a doc section before regenerating it
**Why Valuable**: Reduces unnecessary updates, saves API calls, maintains stability
**Complexity**: Medium (requires source-to-section mapping, heuristics)
**Reconsider When**:
- Update flow generates too many false-positive updates
- API costs become significant due to unnecessary regenerations
- Users want more control over what gets updated

#### 84. Content Hash Change Detection (UC2 - Update Flow)
**Origin**: 2025-11-19-transcript-ideas
**What**: Track content hashes to detect when source files actually changed meaningfully
**Why Valuable**: Trigger updates only when content changes, not just timestamps
**Complexity**: Low (hash comparison, git integration)
**Reconsider When**:
- Update flow exists but triggers on irrelevant changes
- Need to distinguish formatting changes from content changes
- Want to track "what changed" not just "did it change"

#### 85. Selective Section Regeneration (UC2 - Update Flow)
**Origin**: 2025-11-19-transcript-ideas
**What**: Regenerate only affected sections of a doc, not the entire document
**Why Valuable**: Faster updates, less API cost, better stability
**Complexity**: Medium (section-to-source mapping, incremental updates)
**Reconsider When**:
- Full doc regeneration causes too much churn
- API costs from regenerating entire docs become high
- Users want surgical updates to specific sections

#### 86. Stability Tracking for Sections (UC2 - Update Flow)
**Origin**: 2025-11-19-transcript-ideas
**What**: Don't regenerate sections that were recently updated (cooldown period)
**Why Valuable**: Prevents constant churn, respects recent human edits
**Complexity**: Medium (timestamp tracking, cooldown logic, override mechanism)
**Reconsider When**:
- Update flow exists but churns too frequently
- Need to balance freshness with stability
- Users manually edit sections and want them protected temporarily

#### 87. Map Code Changes to Affected Sections (UC2 - Update Flow)
**Origin**: 2025-11-19-transcript-ideas
**What**: Analyze git changes and determine which doc sections they affect
**Why Valuable**: Smart selective updates, reduced unnecessary regeneration
**Complexity**: High (requires section-to-source mapping, change analysis)
**Reconsider When**:
- Selective regeneration exists but affects too many sections
- Need intelligent "what changed affects what docs" logic
- Users want automated impact analysis

#### 88. Generate Template FROM Existing Documentation (Parking Lot)
**Origin**: 2025-11-19-transcript-ideas
**What**: Reverse direction - extract template from well-written existing docs
**Why Valuable**: Onboard existing docs into the system, learn from good examples
**Complexity**: High (structure extraction, section identification, LLM-based analysis)
**Reconsider When**:
- Users have existing high-quality docs they want to maintain with doc_evergreen
- Want to capture organizational documentation standards
- Need to bootstrap templates from examples rather than from scratch

#### 89. Cross-Repo Context Gathering (Cross-Repo)
**Origin**: 2025-11-19-transcript-ideas
**What**: Gather context from multiple repositories for documentation generation
**Why Valuable**: Enables high-level docs that reference multiple projects
**Complexity**: High (multi-repo cloning, context coordination, version alignment)
**Reconsider When**:
- Working in microservices or multi-repo architectures
- Need architectural docs spanning multiple projects
- Want to document cross-project dependencies

#### 90. Update High-Level Doc When Source Changes (Cross-Repo)
**Origin**: 2025-11-19-transcript-ideas
**What**: Detect changes in authoritative source repo and trigger updates in referencing repos
**Why Valuable**: Keeps cross-repo documentation synchronized automatically
**Complexity**: High (cross-repo change detection, webhook integration, dependency tracking)
**Reconsider When**:
- Cross-repo docs exist and drift out of sync frequently
- Multiple repos reference shared authoritative sources
- Need automated propagation of changes across project boundaries

#### 91. Git Integration for Change Detection (UC2 - Implementation)
**Origin**: 2025-11-19-transcript-ideas
**What**: Use git history to detect what files changed since last doc generation
**Why Valuable**: Trigger updates based on actual changes, not manual tracking
**Complexity**: Medium (git API, commit tracking, file change analysis)
**Reconsider When**:
- Update flow needs automated change detection
- Want to use version control as source of truth for changes
- Need "what changed since last run" logic

#### 92. Incremental Context for Changed Files (UC2 - Implementation)
**Origin**: 2025-11-19-transcript-ideas
**What**: Gather context only for files that changed, not entire project
**Why Valuable**: Faster context gathering, reduced API calls for updates
**Complexity**: Medium (requires section-to-source mapping, incremental gathering)
**Reconsider When**:
- Full context gathering for updates is too slow or expensive
- Want to optimize update performance
- Need to scale to larger projects

#### 93. Section-to-Source Mapping (UC2 - Implementation)
**Origin**: 2025-11-19-transcript-ideas
**What**: Track which source files/functions are referenced by each doc section
**Why Valuable**: Enables selective updates, relevance checking, impact analysis
**Complexity**: High (requires analysis during generation, metadata storage, maintenance)
**Reconsider When**:
- Any selective update feature is needed
- Want to answer "what docs are affected by this code change"
- Need intelligent update decisions

#### 94. Template Storage Strategy (Implementation)
**Origin**: 2025-11-19-transcript-ideas
**What**: Decide if templates are separate files or regenerated from existing docs
**Why Valuable**: Architectural decision affecting update flow and template management
**Complexity**: Low (design decision, affects implementation approach)
**Reconsider When**:
- Implementing any template-based feature
- Choosing between "template as source" vs "template as artifact"
- Need to decide template update/versioning strategy

---

## 📝 Using This Backlog

### When MVP Completes
1. Review "Reconsider When" conditions
2. Check which triggers have occurred
3. Prioritize based on actual learnings
4. Move features to active sprint planning

### When New Ideas Arise
1. Add to this document under appropriate origin/phase
2. Include "Reconsider When" conditions
3. Assign complexity estimate
4. Don't immediately implement (defer thoughtfully)

### When Planning Next Release
1. Check all "Reconsider When" conditions
2. Validate with user data (not speculation)
3. Select 3-5 features for next convergence
4. Create new convergence session

---

## 🔗 Related Documents

- **Problem A Details**: `convergence/2025-11-18-problem-a-template-system/DEFERRED_FEATURES.md`
- **Problem B Details**: `convergence/2025-11-18-chunked-generation/DEFERRED_FEATURES.md`
- **Test Case Details**: `convergence/2025-11-19-test-case-basic-regen/DEFERRED_FEATURES.md`
- **Issues Tracker**: `issues/ISSUES_TRACKER.md`
- **Sprint Plans**: `sprints/` (once created)

---

## Philosophy Alignment

This backlog embodies:

**Ruthless Simplicity**:
- Implemented 11 features out of 70 explored (16%)
- 84% thoughtfully deferred with clear conditions

**Trust in Emergence**:
- Features prove necessity through use
- Data beats speculation

**Present-Moment Focus**:
- Solve current problems (documentation control)
- Let needs drive development

**Learning Stance**:
- MVPs teach what matters
- Deferred features wait for validation
- Every release informs the next

---

**Last Review**: 2025-11-24
**Next Review**: After v0.5.0 usage (Template Library & Prompt Quality)
**Review Trigger**: When any "Reconsider When" condition is met

---

## 🎯 v0.5.0 Feature Scope (ACTIVE)

**Convergence**: [2025-11-24-template-library](./2025-11-24-template-library/)
**Status**: Ready for sprint planning
**Theme**: Better Templates, Better Defaults

### Core Features (5 features)
1. **Template Library** - 6 template types (readme-concise/standard/detailed, api-docs, architecture, contributing)
2. **Improved Prompt Engineering** - Length control, scope constraints, style guidance
3. **Template Selection Guidance** - Interactive `init` with clear choices
4. **Remove Mode Confusion** - Drop single-shot mode, embrace chunked-only
5. **Best Practices Documentation** - Comprehensive template creation guide

**Effort**: 7.5-10.5 days (1.5-2 weeks core), 3 weeks conservative
**Deferred**: 12 features with clear reconsider conditions
**Issues Closed**: ISSUE-009 (single-shot), ISSUE-008 (mode clarity)
