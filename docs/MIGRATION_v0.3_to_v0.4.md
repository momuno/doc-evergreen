# Migrating from v0.3.0 to v0.4.0

Guide for upgrading from v0.3.0 to v0.4.0 with breaking changes explained.

---

## Summary

v0.4.0 transforms doc-evergreen into a standalone installable tool with convention-based usage. This requires some migration but provides significant UX improvements.

**Time to migrate**: ~15 minutes for most projects

---

## Breaking Changes

### 1. Source Path Resolution ⚠️ BREAKING

**v0.3.0 (OLD)**:
- Sources resolved relative to template file location
- Template in `templates/` → sources from `templates/`

**v0.4.0 (NEW)**:
- Sources resolved relative to current working directory (cwd)
- Run from project root → sources from project root
- Template location doesn't matter

**Migration**:

If your template was in the same directory as your project:
```
# No changes needed - paths stay the same
```

If your template was in a subdirectory:
```json
// OLD (v0.3.0) - template in project/templates/
{
  "sections": [{
    "sources": ["../src/*.py"]  // Relative to template location
  }]
}

// NEW (v0.4.0) - run from project/, template anywhere
{
  "sections": [{
    "sources": ["src/*.py"]  // Relative to cwd (project root)
  }]
}
```

**Rule of thumb**: Remove any `../` from source paths. Sources are now relative to where you RUN the command.

---

### 2. Installation Required ⚠️ BREAKING

**v0.3.0 (OLD)**:
```bash
cd /path/to/doc_evergreen
PYTHONPATH=.. python -m cli regen-doc template.json
```

**v0.4.0 (NEW)**:
```bash
# One-time installation
pip install -e /path/to/doc-evergreen

# Use from anywhere
cd /any-project
doc-evergreen regen-doc template.json
```

**Migration**:
```bash
cd /path/to/doc-evergreen
pip install -e .

# Verify
doc-evergreen --help
```

---

### 3. Template Location Convention 📁 NEW FEATURE

**v0.3.0**: Templates could be anywhere

**v0.4.0**: Convention: `.doc-evergreen/` directory

**Migration** (optional but recommended):

```bash
# In your project
mkdir .doc-evergreen
mv path/to/templates/*.json .doc-evergreen/

# Now use short names
doc-evergreen regen-doc readme  # Finds .doc-evergreen/readme.json
```

**Benefits**:
- Short, memorable commands
- Clear where templates live
- Templates travel with project
- Familiar pattern (like `.github/`)

---

### 4. Command Changes

**v0.3.0**:
```bash
python -m cli regen-doc /abs/path/template.json
```

**v0.4.0**:
```bash
doc-evergreen regen-doc template_name  # Short name
# or
doc-evergreen regen-doc /abs/path/template.json  # Still works
```

**New commands**:
```bash
doc-evergreen init  # Bootstrap new project
```

---

## Migration Checklist

Follow these steps to migrate:

### Step 1: Install v0.4.0

```bash
cd /path/to/doc-evergreen
git pull  # Get latest
pip install -e .
```

Verify:
```bash
doc-evergreen --help
# Should show v0.4.0 commands
```

### Step 2: Update Template Paths

For each template:

1. **If template was in project root**: No changes needed
2. **If template was in subdirectory**: Update source paths
   - Remove `../` prefixes
   - Make paths relative to project root

Example:
```bash
# Open your template
nano templates/readme.json

# Update sources:
# OLD: "../src/*.py"
# NEW: "src/*.py"
```

### Step 3: Adopt Convention (Recommended)

```bash
# In your project
mkdir .doc-evergreen
mv templates/*.json .doc-evergreen/

# Update your scripts/docs
# OLD: doc-evergreen regen-doc templates/readme.json
# NEW: doc-evergreen regen-doc readme
```

### Step 4: Test Regeneration

```bash
cd /your-project
doc-evergreen regen-doc readme --auto-approve

# Verify output is correct
cat README.md
```

### Step 5: Update Automation

If you have scripts or CI/CD:

```yaml
# OLD (.github/workflows/docs.yml)
- run: |
    cd doc_evergreen
    PYTHONPATH=.. python -m cli regen-doc ../templates/readme.json

# NEW
- run: |
    pip install doc-evergreen
    doc-evergreen regen-doc readme --auto-approve
```

---

## What's New in v0.4.0

Beyond breaking changes, v0.4.0 adds:

### ✨ Init Command
```bash
doc-evergreen init
# Creates .doc-evergreen/readme.json starter template
```

### 🔍 Template Discovery
```bash
doc-evergreen regen-doc readme  # Finds .doc-evergreen/readme.json
```

### 📦 Proper Package
```bash
pip install doc-evergreen  # Standard Python package
```

### 📁 Convention
```
your-project/
├── .doc-evergreen/     # Templates here
│   ├── readme.json
│   └── api.json
└── src/               # Sources relative to project root
```

---

## Common Migration Issues

### Issue: "Template has no source files"

**Cause**: Source paths still relative to old template location

**Fix**: Update source paths to be relative to project root
```json
{
  "sources": ["src/*.py"]  // Not "../src/*.py"
}
```

### Issue: "Template not found: readme"

**Cause**: Template not in .doc-evergreen/ directory

**Fix**: Either move template or use full path
```bash
# Move to convention
mv templates/readme.json .doc-evergreen/

# Or use full path
doc-evergreen regen-doc templates/readme.json
```

### Issue: "No such command 'init'"

**Cause**: Using old v0.3.0 installation

**Fix**: Reinstall v0.4.0
```bash
cd /path/to/doc-evergreen
git pull
pip install -e . --force-reinstall
```

---

## Rollback to v0.3.0

If you need to rollback:

```bash
cd /path/to/doc-evergreen
git checkout v0.3.0
pip uninstall doc-evergreen  # Remove v0.4.0

# Use old method
PYTHONPATH=.. python -m cli regen-doc template.json
```

**Note**: Not recommended. v0.4.0 fixes significant UX issues.

---

## Migration Timeline

**Immediate (Day 1)**:
- Install v0.4.0
- Test with existing templates (may need path updates)

**Short-term (Week 1)**:
- Adopt .doc-evergreen/ convention
- Update automation/scripts
- Update team documentation

**Ongoing**:
- Use `init` for new projects
- Enjoy simpler workflow

---

## Getting Help

**Issues during migration**:
- Check this guide's troubleshooting section
- Review USER_GUIDE.md for v0.4.0 workflows
- Open issue: https://github.com/momuno/doc-evergreen/issues

**Questions**:
- Discussions: https://github.com/momuno/doc-evergreen/discussions

---

## Why These Breaking Changes?

The v0.4.0 changes trade migration cost for long-term UX improvements:

**Before (v0.3.0)**:
```bash
cd doc_evergreen
PYTHONPATH=/complex/path python -m cli regen-doc /abs/path/template.json
```

**After (v0.4.0)**:
```bash
cd /my-project
doc-evergreen regen-doc readme  # That's it!
```

**Worth it**. The migration pain is temporary. The UX improvement is permanent.

---

**Ready to migrate? Start with Step 1 above.**
