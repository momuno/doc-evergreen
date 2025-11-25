# Agent Instructions for doc-evergreen

## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

## Project-Specific: Bug vs Feature Differentiation

This project follows industry best practices for managing bugs, features, and enhancements:

### Issue Types in bd

**Use these types appropriately:**

1. **`bug`** - Something broken that needs fixing
   - Current functionality doesn't work as expected
   - Error, crash, or incorrect behavior
   - Examples: "Template fails with empty context", "CLI help text unclear"
   - Priority: Based on severity (0=critical, 1=high, 2=medium, 3=low)

2. **`feature`** - New capability or enhancement
   - Adds NEW functionality that doesn't exist
   - Major improvements to existing capabilities
   - Examples: "Add template library", "Support multi-variant generation"
   - Priority: Based on value/impact (0=highest value, 1=high, 2=medium, 3=low, 4=backlog)

3. **`task`** - Work item (tests, docs, refactoring)
   - Testing, documentation, refactoring
   - Technical debt reduction
   - Examples: "Write tests for chunked generation", "Document best practices"
   - Priority: Based on urgency

4. **`epic`** - Large feature with subtasks
   - Big initiatives composed of multiple features/tasks
   - Use parent-child dependencies to link subtasks
   - Examples: "Template Library & Prompt Quality (v0.5.0)"

5. **`chore`** - Maintenance work
   - Dependency updates, tooling, build system
   - Examples: "Update to Python 3.12", "Fix linting warnings"

### Status Workflow

**Issues flow through these states:**

- **`open`** - Newly created, needs triage or blocked by dependencies
- **`ready`** - Unblocked and ready to work on (use `bd ready` to find these!)
- **`in_progress`** - Currently being worked on (claim it!)
- **`blocked`** - Waiting on something (use dependencies to track what blocks it)
- **`closed`** - Completed or won't fix

### Priority Levels

**Context-dependent priority:**

For **bugs** (severity-based):
- `0` - **Critical**: Data loss, security, broken builds, can't ship
- `1` - **High**: Major functionality broken, affects many users
- `2` - **Medium**: Minor issues, workarounds exist
- `3` - **Low**: Cosmetic, edge cases
- `4` - **Backlog**: Nice-to-fix someday

For **features** (value-based):
- `0` - **Highest Value**: Core MVP, blocks other work, critical user need
- `1` - **High Value**: Important capabilities, strong user demand
- `2` - **Medium Value**: Nice-to-have, moderate impact
- `3` - **Low Value**: Polish, optimization
- `4` - **Backlog**: Deferred ideas (reconsider when conditions met)

### Labels for Organization

**Use labels to categorize by theme:**
- `template-system` - Template-related features
- `cli` - Command-line interface
- `performance` - Speed/efficiency improvements
- `cross-repo` - Multi-repository features
- `documentation` - Docs and guides
- `testing` - Test infrastructure
- `ux` - User experience improvements

### Dependencies

**Use dependency types appropriately:**

- **`blocks`** - Hard blocker (B must finish before A can start)
  - Example: `bd dep add DE-42 blocks DE-41` (DE-42 blocks DE-41)

- **`related`** - Soft connection (FYI, doesn't block)
  - Example: Similar features, common theme

- **`parent-child`** - Epic/subtask hierarchy
  - Example: Epic "Template Library" has child tasks

- **`discovered-from`** - Found during work on another issue
  - Example: `bd create "Bug found" --deps discovered-from:DE-10`

## Workflow for AI Agents

### 1. Check Ready Work
```bash
bd ready --json
```
Shows unblocked issues ready to work on.

### 2. Claim Your Task
```bash
bd update DE-42 --status in_progress --json
```

### 3. Work on It
Implement, test, document.

### 4. Discover New Work?
Create linked issues:
```bash
bd create "Found bug in template parsing" -t bug -p 1 --deps discovered-from:DE-42 --json
```

### 5. Complete
```bash
bd close DE-42 --reason "Implemented and tested" --json
```

### 6. Commit Together
Always commit the `.beads/issues.jsonl` file together with code changes.

## Managing Backlog Items (Deferred Features)

**Special workflow for deferred features from convergence sessions:**

### When Migrating from MASTER_BACKLOG.md

Deferred features should be created as:
- **Type**: `feature` or `epic`
- **Status**: `open` (will show as not ready if dependencies exist)
- **Priority**: `4` (backlog) initially, raise when "reconsider when" conditions met
- **Labels**: Add origin, phase, theme labels
- **Description**: Include:
  - What it does
  - Why it's valuable
  - Reconsider when conditions
  - Effort estimate
  - Complexity (low/medium/high)

### Example: Creating Deferred Feature

```bash
bd create "Template Marketplace" \
  -t feature \
  -p 4 \
  --assignee "" \
  -d "Share/discover templates created by others.

Reconsider When:
- Users create 5+ templates and want to share
- Clear demand for 'standard templates' emerges
- Reusability patterns are understood

Effort: 1-2 weeks
Complexity: High
Value: Community template sharing and discovery
Origin: 2025-11-24-template-library convergence" \
  --json
```

Then add labels:
```bash
bd label add DE-123 template-system
bd label add DE-123 community
bd label add DE-123 phase-3
```

## Best Practices (Industry Standards)

Based on research of high-performing engineering teams:

1. **Keep everything in one tracker** - Don't split bugs and features into separate systems
2. **Allocate time wisely** - 15-20% of capacity for bug fixes and technical debt
3. **Bug backlog ratio** - Maintain ~5 bugs per developer as healthy ratio
4. **Age limits** - Any issue older than 12 months should be reviewed and closed or moved to secondary backlog
5. **Regular refinement** - Review backlog regularly to ensure it reflects current priorities

## Auto-Sync

bd automatically syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

## MCP Server Integration

This project has the beads MCP server installed. Use MCP functions:
- `mcp__plugin_beads_beads__ready()`
- `mcp__plugin_beads_beads__create()`
- `mcp__plugin_beads_beads__list()`
- `mcp__plugin_beads_beads__show()`
- `mcp__plugin_beads_beads__update()`
- `mcp__plugin_beads_beads__close()`
- etc.

See the MCP function signatures for available parameters.

## Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag or MCP functions for programmatic use
- ✅ Differentiate bugs (broken) from features (new)
- ✅ Use priority context-appropriately (severity for bugs, value for features)
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ✅ Use labels for themes and categorization
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

## Related Documentation

- **MASTER_BACKLOG.md** - Legacy backlog (being migrated to bd)
- **.ai_working/** - Development workflow documentation
- **README.md** - Project overview

---

**For beads documentation, see: https://github.com/steveyegge/beads**
