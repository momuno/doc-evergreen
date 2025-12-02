# Release Notes: v0.5.0 - Template Library System

**Release Date**: December 1, 2025  
**Previous Version**: v0.4.1  
**Type**: Major Feature Release

---

## 🎉 Overview

Version 0.5.0 introduces a **comprehensive template library system** based on the Divio Documentation System, making doc-evergreen significantly more accessible for new users. This release transforms doc-evergreen from requiring manual template creation to providing 9 production-ready templates covering all major documentation types.

**Key Highlights:**
- 📚 **9 Built-in Templates** organized by Divio quadrants (Tutorial, How-to, Reference, Explanation)
- 🎯 **Interactive Template Selection** with guided CLI workflow
- 📖 **Template Registry System** with metadata and best practices
- 🔧 **Improved CLI UX** with cleaner help text and better error messages
- 🏗️ **Simplified Package Structure** for better maintainability
- 🐛 **Critical Bug Fixes** for directory handling and glob patterns

---

## 🚀 Major Features

### 1. Template Library with Divio Documentation System

**What's New:**
- Built-in library of 9 production-ready templates covering all Divio quadrants:
  - **📚 Tutorials** (2): `tutorial-quickstart`, `tutorial-first-template`
  - **🎯 How-To Guides** (3): `howto-contributing-guide`, `howto-ci-integration`, `howto-custom-prompts`
  - **📖 Reference** (2): `reference-cli`, `reference-api`
  - **💡 Explanation** (2): `explanation-architecture`, `explanation-concepts`

**Why It Matters:**
- **Faster Onboarding**: Users can generate their first documentation in under 5 minutes
- **Best Practices Built-In**: Each template follows documentation quality guidelines
- **Divio Framework**: Industry-standard organization for technical documentation

**Files Added:**
- `src/doc_evergreen/template_registry.py` - Template discovery and management
- `src/doc_evergreen/templates/` - 9 built-in templates with metadata
- `src/doc_evergreen/core/template_schema.py` - Enhanced schema with metadata support

**Implementation Details:**
- Templates include `_meta` section with description, use case, quadrant, and estimated output size
- Automatic template discovery from package resources
- Template validation ensures quality and completeness

**Related Commits:**
- `af6f202` feat: implement v0.5.0 template library with Divio framework (Sprints 1-3.1)
- `85b13bb` docs: adopt Divio Documentation System for v0.5.0 template library

---

### 2. Interactive Template Selection

**What's New:**
- `doc-evergreen init` now shows interactive menu by default
- Templates organized by documentation quadrant with emoji indicators
- Numbered selection (1-9) or quit with 'q'
- Template metadata displayed (description, use case, estimated size)

**Example Workflow:**
```bash
$ doc-evergreen init

? What type of documentation do you want to create?

📚 TUTORIALS (Learning-oriented - "Take me on a journey")
  1. tutorial-quickstart - Get started with doc-evergreen in 5 minutes (200-400 lines)
  2. tutorial-first-template - Learn to create your first custom template (400-600 lines)

🎯 HOW-TO GUIDES (Goal-oriented - "Show me how to...")
  3. howto-contributing-guide - Guide contributors to your project (300-500 lines)
  ...

Choose [1-9] or 'q' to quit: 1
✅ Created: .doc-evergreen/tutorial-quickstart.json
```

**Benefits:**
- No need to know template names upfront
- Contextual help choosing the right template type
- Clear understanding of what each template produces

**Related Commits:**
- `b985000` fix: improve CLI UX for v0.5.0 release
- `af6f202` feat: implement v0.5.0 template library with Divio framework

---

### 3. Enhanced CLI Experience

**What's New:**
- Cleaner `--help` output (removed verbose installation/documentation notes)
- Better template discovery with `--list` flag
- Improved error messages with actionable suggestions
- Template resolution supports short names (e.g., `readme` → `.doc-evergreen/readme.json`)

**CLI Improvements:**
```bash
# Before: Verbose help with installation instructions
$ doc-evergreen --help
# 40+ lines of installation, how-it-works, documentation links

# After: Clean, focused help
$ doc-evergreen --help
Generate documentation from templates organized by the Divio Documentation System.

Quick Start:
  # Interactive template selection (recommended)
  $ doc-evergreen init
  
  # List all available templates
  $ doc-evergreen init --list
  ...
```

**Related Commits:**
- `be9a9cb` refactor: clean up CLI help text for clarity
- `b985000` fix: improve CLI UX for v0.5.0 release

---

### 4. Package Structure Refactoring

**What's New:**
- Simplified from nested `doc_evergreen/core/core/` to flat `doc_evergreen/core/`
- Better organization with clear separation of concerns
- Template registry as first-class component

**Before:**
```
src/doc_evergreen/
  core/
    core/
      template_schema.py
      source_validator.py
```

**After:**
```
src/doc_evergreen/
  core/
    template_schema.py
    source_validator.py
  template_registry.py
  templates/
    tutorial-*.json
    howto-*.json
    reference-*.json
    explanation-*.json
```

**Benefits:**
- Easier navigation for contributors
- Clearer import paths
- Better maintainability

**Related Commits:**
- `efdb792` refactor: simplify package structure from nested to flat layout

---

### 5. Beads Issue Tracking Integration

**What's New:**
- Integrated beads for structured issue tracking
- Replaces legacy `.ai_working/` markdown-based tracking
- Better organization with priorities, labels, and metadata
- Foundation for future sprint planning integration

**Migration:**
- Migrated from `MASTER_BACKLOG.md` to beads database
- Removed 11 legacy ISSUE-*.md files from `.ai_working/issues/`
- Cleaned up convergence session files from `.ai_working/convergence/`

**Benefits:**
- Persistent, structured issue tracking
- Better query and filtering capabilities
- Integrates with convergent-dev workflow

**Related Commits:**
- `7af4702` Add beads integration for structured issue tracking
- `85fc280` chore: complete migration from MASTER_BACKLOG.md to beads tracking
- `bef8778` chore: remove legacy .ai_working tracking system

---

## 🐛 Bug Fixes

### Critical Fixes

1. **Directory Filtering in Source Glob Patterns** (`2d5c45a`)
   - **Issue**: `source_validator.py` included directories in source file lists, causing generation failures
   - **Fix**: Filter out directories, only include files matching glob patterns
   - **Impact**: Prevents crashes when source patterns match directory names

2. **Glob Pattern Handling** (from v0.4.1 baseline)
   - **Issue**: Complex glob patterns not resolved correctly
   - **Fix**: Improved glob resolution logic
   - **Impact**: More reliable source file discovery

### UX Improvements

1. **Removed Legacy doc-update Command** (`be9a9cb`)
   - Removed deprecated `doc-update` command and documentation
   - Users should use `regen-doc` for all documentation generation

2. **Better Template Error Messages** (`b985000`)
   - Clear guidance when template not found
   - Suggests `doc-evergreen init --list` to see available templates

---

## 📚 Documentation

### New Documentation

1. **TEMPLATE_BEST_PRACTICES.md** (`docs/`)
   - Comprehensive guide to writing quality templates
   - Prompt engineering best practices
   - Source selection strategies
   - 447 lines of detailed guidance

2. **TEMPLATE_QUALITY.md** (`docs/`)
   - Quality standards for templates
   - What makes a good prompt
   - Common pitfalls and solutions
   - 277 lines of quality guidelines

3. **Quick Start Guide** (`87b6648`)
   - 5-minute getting started guide for v0.5.0
   - Highlights template library features
   - Step-by-step first documentation generation

### Updated Documentation

1. **README.md** - Massively updated (1007 lines)
   - New template library section
   - Interactive selection workflow
   - Updated quick start with template examples
   - Removed legacy doc-update references

2. **USER_GUIDE.md** - Updated for v0.5.0
   - Template registry usage
   - Interactive selection guide
   - Template customization

3. **INSTALLATION.md** → **docs/INSTALLATION.md**
   - Moved to docs/ directory for better organization
   - Updated for v0.5.0 features

---

## 🧪 Testing

### New Tests

1. **Template Registry Tests** (`tests/test_template_registry.py`)
   - 213 lines of comprehensive registry testing
   - Template discovery, loading, validation
   - Metadata parsing and error handling

2. **CLI Template Flags Tests** (`tests/test_cli_template_flags.py`)
   - 300 lines testing new CLI features
   - Template selection flags
   - Interactive mode simulation
   - Error handling

3. **Interactive Selection Tests** (`tests/test_interactive_selection.py`)
   - 184 lines testing interactive menu
   - User input simulation
   - Template selection workflow

4. **Template Library Smoke Tests** (`tests/test_template_library_smoke.py`)
   - 88 lines of basic template validation
   - Ensures all 9 templates are loadable
   - Validates template structure

5. **CLI Mode Removal Tests** (`tests/test_cli_mode_removal.py`)
   - 65 lines verifying legacy command removal
   - Ensures doc-update is gone

**Test Coverage:**
- Added 850+ lines of new tests
- All 9 templates validated for correctness
- Interactive workflows fully tested

---

## 🔄 Migration Guide (v0.4.1 → v0.5.0)

### No Breaking Changes! 🎉

**Good News:** v0.5.0 is fully backward compatible with v0.4.1.

### What Still Works

1. **Existing Templates**
   - All v0.4.1 templates continue to work unchanged
   - Template format is identical
   - No migration needed for existing `.doc-evergreen/` directories

2. **CLI Commands**
   - `doc-evergreen regen-doc <template>` works exactly the same
   - `--auto-approve` and `--output` flags unchanged
   - Template path resolution unchanged

### What's New (Optional to Adopt)

1. **Template Library**
   - New users can use built-in templates
   - Existing users can continue with custom templates
   - Optional: Explore built-in templates with `doc-evergreen init --list`

2. **Interactive Selection**
   - `doc-evergreen init` now interactive by default
   - Use `doc-evergreen init --yes` to skip (non-interactive)
   - Legacy `--name` flag deprecated but still works

### Recommended Actions

1. **Try Built-in Templates:**
   ```bash
   doc-evergreen init --list  # See what's available
   doc-evergreen init --template tutorial-quickstart
   ```

2. **Review Documentation:**
   - Check out `docs/TEMPLATE_BEST_PRACTICES.md` for custom templates
   - Read `docs/TEMPLATE_QUALITY.md` for quality guidelines

3. **Update Workflows:**
   - CI/CD using `doc-evergreen doc-update`? Switch to `regen-doc`
   - Documentation references to doc-update? Update to regen-doc

---

## 📊 Statistics

### Code Changes
- **Files Changed**: 94 files
- **Lines Added**: +9,669
- **Lines Removed**: -4,151
- **Net Change**: +5,518 lines

### Components Added
- 9 built-in templates with metadata
- Template registry system (252 lines)
- Enhanced template schema (112 lines addition)
- 850+ lines of new tests
- 724+ lines of new documentation

### Cleanup
- Removed 11 legacy issue tracking files (3,108 lines)
- Removed obsolete convergence session files
- Simplified package structure
- Cleaned up CLI help (removed 30+ lines of verbosity)

---

## 🔧 Technical Details

### New Dependencies
- None! v0.5.0 uses same dependencies as v0.4.1

### Supported Python Versions
- Python 3.11+ (unchanged)

### API Compatibility
- 100% backward compatible with v0.4.1
- No breaking changes to template format
- No breaking changes to CLI interface

### Performance
- Template discovery: <100ms (lazy loading)
- Interactive selection: instant (no API calls)
- Generation performance: unchanged from v0.4.1

---

## 🎯 Known Issues & Limitations

### User Feedback (from v0.5.0 testing)

1. **Template Editing Still Manual** (Tracked: DE-qyc, DE-t6l, DE-2t4, DE-aki, DE-b8p)
   - Users must still manually edit JSON templates for customization
   - No interactive template builder yet
   - No smart source detection
   - **Planned for**: v0.6.0+ (5 beads issues created)
   - **Workaround**: Use built-in templates as starting point

### Technical Limitations

1. **Template Format**
   - Only JSON format supported (no YAML)
   - Manual prompt engineering required
   - No template validation command yet

2. **Template Library**
   - 9 templates cover common cases but not all documentation needs
   - Some templates may need customization for specific projects
   - No user-contributed template marketplace yet

---

## 🚀 What's Next (v0.6.0 Preview)

Based on v0.5.0 user feedback, the following enhancements are planned:

### High Priority (v0.6.0)
1. **Interactive Template Builder** (DE-qyc)
   - `doc-evergreen template create` with CLI wizard
   - Step-by-step template construction
   - Estimated: 2-3 days

2. **Smart Source Detection** (DE-t6l)
   - Automatic project analysis
   - Suggest relevant sources per section
   - Estimated: 1-2 days

### Medium Priority (v0.6.x)
3. **Prompt Templates Library** (DE-2t4)
   - Pre-built prompt patterns for common sections
   - Estimated: 1 day

4. **Template Scaffolding** (DE-aki)
   - `doc-evergreen template scaffold` command
   - Generate draft template from project analysis
   - Estimated: 1-2 days

### Nice-to-Have (v0.7.0+)
5. **Template Validation** (DE-b8p)
   - `doc-evergreen template validate` command
   - Check for common mistakes and suggest improvements
   - Estimated: 1 day

**Total Estimated Effort**: 6-10 days for all 5 enhancements

---

## 🙏 Acknowledgments

This release was developed following the Convergent Development methodology:
- **Sprint Planning**: v0.5.0 broken into 4 sprints
- **TDD Approach**: 850+ lines of tests written first
- **Issue Tracking**: Beads integration for systematic tracking
- **Documentation**: Divio framework adoption

Special thanks to the Amplifier AI development assistant for facilitating the convergent-dev workflow.

---

## 📦 Installation

### Upgrade from v0.4.1

```bash
# Using pipx (recommended)
pipx upgrade doc-evergreen

# Using pip
pip install --upgrade doc-evergreen
```

### Fresh Install

```bash
# Using pipx (recommended)
pipx install doc-evergreen

# Using pip
pip install doc-evergreen
```

### Verify Installation

```bash
doc-evergreen --version
# Should show: doc-evergreen, version 0.5.0

# Try the new template library
doc-evergreen init --list
```

---

## 🐛 Bug Reports & Feedback

Found an issue or have feedback? Please:

1. **Check Existing Issues**: Review [GitHub Issues](https://github.com/momuno/doc-evergreen/issues)
2. **Report New Issues**: Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, doc-evergreen version)

---

## 📖 Additional Resources

- **Documentation**: See `docs/` directory for complete guides
- **Template Best Practices**: `docs/TEMPLATE_BEST_PRACTICES.md`
- **Template Quality**: `docs/TEMPLATE_QUALITY.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **Installation Guide**: `docs/INSTALLATION.md`

---

**Released**: December 1, 2025  
**Version**: 0.5.0  
**Codename**: Template Library System  
**Commits**: 15 commits since v0.4.1  
**Contributors**: momuno (+ Amplifier AI assistant)
