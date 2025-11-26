# Release Notes: v0.5.0 - Template Library

**Release Date**: 2025-11-26  
**Theme**: Better Templates, Better Defaults  
**Status**: Feature Complete

---

## 🎉 What's New

### Template Library (9 Built-in Templates)

doc-evergreen now includes a complete template library following the **Divio Documentation System**:

#### 📚 **Tutorials** (Learning-oriented - "Take me on a journey")
- `tutorial-quickstart` - Brief quickstart guide (200-400 lines)
- `tutorial-first-template` - Learn to create your first doc-evergreen template (300-500 lines)

#### 🎯 **How-To Guides** (Goal-oriented - "Show me how to...")
- `howto-contributing-guide` - Contributing guidelines for developers (300-500 lines)
- `howto-ci-integration` - Integrate doc-evergreen into CI/CD pipelines (300-500 lines)
- `howto-custom-prompts` - Write effective prompts for better documentation (300-500 lines)

#### 📖 **Reference** (Information-oriented - "Tell me facts")
- `reference-cli` - Complete CLI command reference (400-600 lines)
- `reference-api` - Complete API reference documentation (500-700 lines)

#### 💡 **Explanation** (Understanding-oriented - "Help me understand")
- `explanation-architecture` - Architecture and design explanation (400-800 lines)
- `explanation-concepts` - Core concepts and mental models explained (400-600 lines)

### Interactive Template Selection

Beautiful CLI menu when you run `doc-evergreen init`:

```
? What type of documentation do you want to create?

📚 TUTORIALS (Learning-oriented - "Take me on a journey")
  1. tutorial-quickstart - Brief quickstart guide (200-400 lines)
  2. tutorial-first-template - Create your first template (300-500 lines)

🎯 HOW-TO GUIDES (Goal-oriented - "Show me how to...")
  3. howto-contributing-guide - Contributing guidelines (300-500 lines)
  ...

Choose [1-9] or 'q' to quit: _
```

### Enhanced `--list` Output

Rich template information:
```bash
$ doc-evergreen init --list

Available templates (grouped by Divio quadrant):

📚 TUTORIALS (Learning-oriented - "Take me on a journey")
  tutorial-quickstart
    Brief quickstart guide for new users
    Output: QUICKSTART.md | Estimated: 200-400 lines
    Use when: New users need to get started in 5 minutes
  ...
```

### Quality & Documentation

- **Template Best Practices Guide**: Comprehensive guide on creating effective templates
- **Template Quality Guide**: Customization tips and troubleshooting
- **Validation Report**: All 9 templates tested and validated
- **91 Tests Passing**: Comprehensive test coverage with smoke tests

---

## 🚀 Getting Started

### Use Interactive Selection
```bash
doc-evergreen init
```

### List Available Templates
```bash
doc-evergreen init --list
```

### Use Specific Template
```bash
doc-evergreen init --template tutorial-quickstart
```

### Quick Start (Non-interactive)
```bash
doc-evergreen init --yes  # Uses tutorial-quickstart
```

---

## 🔧 Breaking Changes

### Removed: `--mode` Flag

The `--mode` flag has been removed from the `doc-update` command. Chunked generation is now the only mode (it's what works best).

**Before (v0.4.x)**:
```bash
doc-evergreen doc-update readme --mode chunked
```

**After (v0.5.0)**:
```bash
doc-evergreen doc-update readme  # Just works
```

**Migration**: Simply remove `--mode` from your commands and scripts.

---

## 📚 New Documentation

### New Guides
- **[TEMPLATE_BEST_PRACTICES.md](docs/TEMPLATE_BEST_PRACTICES.md)** - Learn to create effective templates
  - Understanding the Divio Documentation System
  - Prompt engineering essentials
  - Source selection strategies
  - Real-world examples with before/after
  - Iteration workflow and common mistakes

- **[TEMPLATE_QUALITY.md](docs/TEMPLATE_QUALITY.md)** - Customization and troubleshooting
  - Expected behavior and known limitations
  - Customization guide with examples
  - Prompt engineering best practices
  - Troubleshooting common issues
  - Template evolution and philosophy

### Updated Guides
- **USER_GUIDE.md** - Added template library section
- **README.md** - Updated with v0.5.0 features

---

## 🎯 Improvements

### Simplified CLI
- **Removed confusing options**: No more `--mode` flag
- **Better defaults**: `--yes` uses sensible default (tutorial-quickstart)
- **Clearer help text**: Examples and guidance in `--help`

### Better Discovery
- **Interactive menu**: Helps users choose the right template
- **Divio organization**: Educational - teaches documentation types
- **Rich descriptions**: Every template shows use case and estimated output

### Enhanced Quality
- **Validated templates**: All 9 templates tested on doc-evergreen
- **Smoke tests**: 28 new tests provide regression protection
- **Best practices**: Captured lessons learned in comprehensive guide

---

## 📊 Technical Details

### Code Changes
- **32 files changed**: 2,122 insertions, 207 deletions
- **5 new test files**: 51 new tests added (91 total)
- **3 new modules**: template_registry.py, TEMPLATE_BEST_PRACTICES.md, TEMPLATE_QUALITY.md
- **9 template files**: Complete Divio coverage

### Test Coverage
- **91 tests passing** (up from 40)
- **Test execution**: 0.46 seconds
- **Coverage**: >80% on new code

### Package Structure
- Templates in `src/doc_evergreen/templates/`
- Registry system for discovery and loading
- Interactive selection with Click
- Enhanced metadata support

---

## 🔄 Upgrade Guide

### From v0.4.x to v0.5.0

**Step 1**: Update installation
```bash
pipx upgrade doc-evergreen
# or
pip install --upgrade doc-evergreen
```

**Step 2**: Remove `--mode` flags from scripts
If you have scripts or CI/CD using `--mode`, simply remove that flag.

**Step 3**: Explore new templates
```bash
doc-evergreen init --list
```

**Step 4**: Read best practices guide
Check out [TEMPLATE_BEST_PRACTICES.md](docs/TEMPLATE_BEST_PRACTICES.md) for tips on creating great templates.

### What Stays the Same
- ✅ Template JSON format (backward compatible)
- ✅ Generation workflow (init → regen-doc)
- ✅ All existing features still work
- ✅ `.doc-evergreen/` convention
- ✅ Existing templates continue to work

---

## 🐛 Known Issues

**None at release time.**

All 9 templates have been validated and tested. All automated tests pass.

---

## 🔮 What's Next

### Post-v0.5.0 Improvements (Based on User Feedback)

**Potential v0.6.0 Features**:
- Smart template suggestions (AI-powered template selection based on project analysis)
- Selective section regeneration (update only changed sections)
- Stability mode (reduce regeneration variation)
- Custom template directories (share templates across projects)
- Template versioning (track template evolution)

See [DEFERRED_FEATURES.md](.amplifier/convergent-dev/convergence/2025-11-24-template-library/DEFERRED_FEATURES.md) for full list with reconsider conditions.

---

## 💬 Feedback

We'd love to hear how v0.5.0 works for you:
- Try the new templates
- Read the best practices guide
- Share your customizations
- Report issues or suggest improvements

**GitHub Issues**: https://github.com/momuno/doc-evergreen/issues  
**Discussions**: https://github.com/momuno/doc-evergreen/discussions

---

## 🙏 Thanks

This release wouldn't be possible without:
- **Divio Documentation System**: Inspiration for template organization
- **Convergent-dev workflow**: Structured sprint planning and execution
- **TDD approach**: Confidence through comprehensive testing
- **Implementation philosophy**: Ruthless simplicity and modular design

Special thanks to the Amplifier AI assistant for implementing this feature following best practices and maintaining high code quality throughout.

---

## 📖 Resources

**New Guides**:
- [Template Best Practices](docs/TEMPLATE_BEST_PRACTICES.md)
- [Template Quality Guide](docs/TEMPLATE_QUALITY.md)
- [Validation Report](.amplifier/convergent-dev/sprints/v0.5.0-template-library/VALIDATION_REPORT.md)

**Existing Guides**:
- [User Guide](docs/USER_GUIDE.md)
- [README](README.md)

**Sprint Documentation**:
- [Sprint Plan](.amplifier/convergent-dev/sprints/v0.5.0-template-library/SPRINT_PLAN.md)
- Sprint 1: [Quick Win + Foundation](.amplifier/convergent-dev/sprints/v0.5.0-template-library/SPRINT_01_QUICK_WIN_FOUNDATION.md)
- Sprint 2: [Complete Library](.amplifier/convergent-dev/sprints/v0.5.0-template-library/SPRINT_02_COMPLETE_LIBRARY.md)
- Sprint 3: [Prompt Quality](.amplifier/convergent-dev/sprints/v0.5.0-template-library/SPRINT_03_PROMPT_QUALITY.md)
- Sprint 4: [Documentation & Polish](.amplifier/convergent-dev/sprints/v0.5.0-template-library/SPRINT_04_DOCUMENTATION_POLISH.md)

---

**v0.5.0 - Template Library Complete** 🎉

Built with ❤️ using the convergent-dev workflow and implementation philosophy principles.
