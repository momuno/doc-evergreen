# Release Notes

## v0.4.0 - Standalone Tool (2025-11-21)

**Theme**: Convention-Based Standalone Tool

This is the first official release of doc-evergreen as a standalone, installable tool that works with ANY project on your filesystem.

---

### 🎉 What's New

#### Standalone Installation
- **Install once, use everywhere**: `pipx install doc-evergreen`
- Works as a global command with any project
- Isolated dependencies (no conflicts with your projects)
- Clean uninstall: `pipx uninstall doc-evergreen`

#### Convention-Based Discovery
- **Zero configuration**: Run from your project root, it just works
- **`.doc-evergreen/` convention**: Familiar pattern like `.github/` or `.vscode/`
- **Short commands**: `doc-evergreen regen-doc readme` finds `.doc-evergreen/readme.json`
- **Flexible**: Still supports full paths when needed

#### Bootstrap New Projects
- **`init` command**: `doc-evergreen init` creates starter template
- **Customizable**: Prompts for project name, description (or uses defaults)
- **Ready to use**: Generated template works immediately
- **Clear workflow**: Initialize → Customize → Generate

#### Improved CLI
- **Better help text**: Clear, readable formatting with proper line breaks
- **Command clarity**: `regen-doc` is primary, `doc-update` marked as legacy
- **Option visibility**: `--output`, `--auto-approve`, and `--help` surfaced clearly
- **Error messages**: Actionable guidance when things go wrong

#### Documentation Overhaul
- **Quick Start in README**: Get started in 5 minutes
- **Reference in USER_GUIDE**: Detailed documentation for all features
- **Clear separation**: Tutorial (README) vs Reference (USER_GUIDE)
- **Installation guide**: Comprehensive setup, troubleshooting, and uninstall
- **No external references**: Fully standalone documentation

---

### 🔧 Breaking Changes

#### Source Path Resolution (Migration Required)
**Before (v0.3.0)**:
- Sources were relative to template location
- Example: `../src/main.py` from `templates/readme.json`

**After (v0.4.0)**:
- Sources are relative to project root (cwd)
- Example: `src/main.py` from anywhere in project

**Migration**:
1. Move templates to `.doc-evergreen/` in your project root
2. Update source paths to be relative to project root
3. Test with `doc-evergreen regen-doc <template-name>`

#### Installation Required
**Before (v0.3.0)**:
- Run from repository with PYTHONPATH setup

**After (v0.4.0)**:
- Install globally: `pipx install doc-evergreen`
- Run from any project directory

---

### ✅ Issues Resolved

- **ISSUE-011**: Project root support → Superseded by convention-based cwd approach
- **ISSUE-004**: CLI help text unclear → Improved help formatting with clear sections
- **Documentation**: Removed all external references, standardized naming

---

### 📚 Documentation

#### New Documentation Structure
- **README.md**: Quick start and overview (entry point)
- **INSTALLATION.md**: Detailed installation, troubleshooting, uninstall
- **docs/USER_GUIDE.md**: Complete command reference
- **docs/TEMPLATES.md**: Template creation guide
- **docs/BEST_PRACTICES.md**: Design patterns and best practices

#### Key Improvements
- Quick Start only in README (no duplication)
- `--output` parameter surfaced in Quick Start
- Clear command hierarchy (`regen-doc` primary, `doc-update` legacy)
- Consistent naming (doc-evergreen, not doc_evergreen)
- Version updated to 0.4.0 throughout
- No external project references

---

### 🎯 Features Delivered

From the v0.4.0 Feature Scope (5 features planned):

1. ✅ **Proper Python Package**
   - pyproject.toml with entry point
   - `doc-evergreen` command available globally
   - Automatic dependency installation
   - Works with pip and pipx

2. ✅ **Convention-Based Discovery**
   - cwd = project root (zero configuration)
   - Sources relative to project root
   - Works with any directory structure
   - No `--project` flag needed

3. ✅ **Template Directory Convention**
   - `.doc-evergreen/` standard location
   - Short-form commands: `regen-doc readme`
   - Clear errors if template not found
   - Absolute paths still supported

4. ✅ **Init Command**
   - `doc-evergreen init` bootstraps projects
   - Creates `.doc-evergreen/readme.json`
   - Prompts for customization (optional)
   - Provides starter sections

5. ✅ **Updated Documentation**
   - Installation instructions
   - Convention-based examples
   - Migration guide
   - All examples tested
   - Standalone documentation

---

### 📈 Development History

This release represents the culmination of 4 convergence sessions and 13 sprints:

#### v0.1.0 - Template System (Sprints 1-4)
- Template-based document structure
- Source resolution with glob patterns
- Single-shot generation
- Preview & accept workflow

#### v0.2.0 - Chunked Generation (Sprints 5-7)
- Section-level prompts
- Sequential generation
- Context flow between sections
- Source validation

#### v0.3.0 - Basic Regeneration (Sprints 8-10)
- Template-based regeneration
- Change detection with diff preview
- Iterative refinement workflow
- Comprehensive documentation
- 119 tests (all passing)

#### v0.4.0 - Standalone Tool (Sprints 11-13 + Polish)
- Installable package
- Convention-based usage
- Init command
- Documentation restructure
- External reference cleanup

---

### 🧪 Testing

- **Test Suite**: 119 tests (all passing)
- **Coverage**: Template parsing, source resolution, generation, CLI, change detection
- **Real-world validation**: Tested with multiple project structures
- **Installation testing**: Verified pip and pipx installation methods

---

### 🚀 Getting Started

```bash
# Install
pipx install git+https://github.com/YOUR_ORG/doc-evergreen.git

# Set up API key
export ANTHROPIC_API_KEY=your_key_here

# Use with any project
cd /your-project
doc-evergreen init
doc-evergreen regen-doc readme
```

See [README.md](./README.md) for complete Quick Start guide.

---

### 🔮 What's Next?

See [.ai_working/convergence/MASTER_BACKLOG.md](./.ai_working/convergence/MASTER_BACKLOG.md) for the complete feature backlog.

**Potential future features** (based on usage data):
- PyPI publishing (when 10+ external users)
- Watch mode / auto-regeneration
- CI/CD integration helpers
- Multi-project aggregation
- Template marketplace

**Philosophy**: Features earn their way into releases through real usage and validated need.

---

### 📊 By The Numbers

- **4 versions** developed (v0.1.0 → v0.4.0)
- **13 sprints** completed
- **11 issues** tracked (8 resolved, 3 open)
- **72 features** in backlog (18 implemented, 54 deferred)
- **119 tests** (100% passing)
- **5 comprehensive docs** (README, INSTALLATION, USER_GUIDE, TEMPLATES, BEST_PRACTICES)
- **46 development history files** preserved in `.ai_working/`

---

### 🙏 Acknowledgments

Built using the Amplifier development philosophy:
- **Ruthless Simplicity**: 16% of explored features implemented
- **Trust in Emergence**: Features prove necessity through use
- **Present-Moment Focus**: Solve current problems, defer speculation
- **Learning Stance**: Every release teaches what matters next

Development artifacts preserved in `.ai_working/` for complete transparency.

---

### 📝 License

MIT License - See [LICENSE](./LICENSE) file

---

**Ready to keep your docs in sync?** See [README.md](./README.md) to get started.
