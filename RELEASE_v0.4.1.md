# Release v0.4.1 - Bug Fix Release

**Release Date**: 2025-11-21
**Type**: Patch Release (Bug Fix)

---

## 🐛 Critical Bug Fix

### Issue: Glob Patterns Matching Virtual Environment Files

**Problem**: 
Templates using glob patterns like `**/*.py` were matching thousands of files from `.venv/lib/python3.13/site-packages/` instead of just project source files. This caused:
- Extremely slow validation and generation
- Incorrect context sent to LLM (dependency code instead of project code)
- High API costs from processing irrelevant files
- Confusing user experience

**Root Cause**:
The glob resolution had no default exclusions for common non-project directories like `.venv/`, `node_modules/`, etc.

**Solution**:
Added smart default exclusions that automatically skip:
- `.venv/`, `venv/`, `env/`, `.env/` (virtual environments)
- `node_modules/` (Node packages)
- `.git/` (Git metadata)  
- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` (cache directories)
- `build/`, `dist/`, `*.egg-info/` (build artifacts)

**Impact**:
- ✅ `**/*.py` now matches only project files
- ✅ 52-97% reduction in matched files (27 → 13 files in doc-evergreen)
- ✅ Faster generation
- ✅ Lower API costs
- ✅ Correct context for documentation

---

## 🔧 Template Improvements

### Init Command Generates Optimized Templates

**Before**:
```json
"sources": ["**/*.py"]  // Matched everything
```

**After**:
```json
"sources": ["src/**/*.py"]  // Focused on source code
```

**Benefits**:
- New users get best practices by default
- Fewer files matched → faster generation
- More focused context → better documentation

---

## 📝 Changes

### Fixed
- **Critical**: Glob patterns no longer match `.venv/` and `node_modules/` files
- **Template**: `init` command now generates focused source patterns (`src/**/*.py` instead of `**/*.py`)
- **Template**: Updated existing `.doc-evergreen/readme.json` with optimized patterns

### Added
- Default exclusion list for common non-project directories
- Helper function `_should_exclude_path()` for path filtering
- 3 new test cases validating exclusion behavior

### Changed
- `source_validator.py`: Added smart filtering to `resolve_source_pattern()`
- `cli.py`: Init command generates more specific glob patterns
- Version bumped: 0.4.0 → 0.4.1

---

## ✅ Testing

- **All tests pass**: 122/122 tests passing
- **New test coverage**: 
  - `test_excludes_virtual_environment_files`
  - `test_excludes_node_modules`
  - `test_excludes_common_cache_directories`
- **Real-world validation**: Verified with doc-evergreen project itself

---

## 📦 Installation

### Upgrade from v0.4.0:

```bash
# If installed with pipx (recommended)
pipx upgrade doc-evergreen

# If installed with pip
pip install --upgrade git+https://github.com/YOUR_ORG/doc-evergreen.git

# If installed editable
cd /path/to/doc-evergreen
git pull
pipx reinstall doc-evergreen
```

---

## 🔄 Migration

**No migration required!** This is a backward-compatible bug fix.

Your existing templates will work better automatically after upgrading.

**Optional**: Update your templates to use more specific patterns like `src/**/*.py` instead of `**/*.py` for even better performance.

---

## 📊 Impact

### Before v0.4.1
```
Pattern: **/*.py
Matches: ~1000+ files (including all of .venv/)
Result: Slow, expensive, wrong context
```

### After v0.4.1
```
Pattern: **/*.py
Matches: ~13-27 files (project files only)
Result: Fast, efficient, correct context ✅
```

---

## 🙏 Credits

Bug reported and fixed in the same session through systematic debugging with the bug-hunter agent.

---

## 📎 Files Changed

- `src/doc_evergreen/core/source_validator.py` (+58 lines)
- `tests/test_source_validator.py` (+68 lines)
- `src/doc_evergreen/cli.py` (updated init template)
- `.doc-evergreen/readme.json` (optimized patterns)
- `pyproject.toml` (version bump)
- `tests/test_package_config.py` (version assertion update)
- `INSTALLATION.md` (version reference)
- `docs/USER_GUIDE.md` (version and changelog)

---

**This patch release makes glob patterns work correctly out of the box. Upgrade recommended for all users.**
