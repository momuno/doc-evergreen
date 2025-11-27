# Quick Start: Using v0.5.0 Template Library Features

## 🎯 What's New in v0.5.0

You now have **9 built-in templates** organized by the **Divio Documentation System**:

### 📚 **Tutorials** (Learning-oriented)
- `tutorial-quickstart` - Get users started quickly (QUICKSTART.md)
- `tutorial-first-template` - Teach template creation (docs/FIRST_TEMPLATE.md)

### 🎯 **How-To Guides** (Goal-oriented)
- `howto-contributing-guide` - Developer onboarding (CONTRIBUTING.md)
- `howto-ci-integration` - CI/CD setup guide (docs/CI_INTEGRATION.md)
- `howto-custom-prompts` - Prompt engineering guide (docs/PROMPT_GUIDE.md)

### 📖 **Reference** (Information-oriented)
- `reference-cli` - Complete CLI reference (docs/CLI_REFERENCE.md)
- `reference-api` - API documentation (docs/API.md)

### 💡 **Explanation** (Understanding-oriented)
- `explanation-architecture` - System design docs (docs/ARCHITECTURE.md)
- `explanation-concepts` - Conceptual documentation (docs/CONCEPTS.md)

---

## 🚀 How to Use the New Features

### **1. List All Available Templates**

```bash
doc-evergreen init --list
```

**What you'll see:**
- All 9 templates grouped by Divio quadrant
- Description of each template
- Typical output file for each
- Use case for when to use each template

---

### **2. Interactive Template Selection (Recommended)**

```bash
doc-evergreen init
```

**What happens:**
- Interactive menu appears with all templates organized by quadrant
- Choose by number (1-9) or 'q' to quit
- Guided selection based on your documentation needs
- Template is copied to `.doc-evergreen/` directory

**Example session:**
```
? What type of documentation do you want to create?

📚 Tutorials (Learning-oriented)
  1. tutorial-quickstart - Quick start guide for new users
  2. tutorial-first-template - Learn to create templates

🎯 How-To Guides (Goal-oriented)
  3. howto-contributing-guide - Contributing guidelines
  4. howto-ci-integration - CI/CD integration guide
  5. howto-custom-prompts - Prompt engineering guide

📖 Reference (Information-oriented)
  6. reference-cli - Complete CLI reference
  7. reference-api - API documentation

💡 Explanation (Understanding-oriented)
  8. explanation-architecture - Architecture documentation
  9. explanation-concepts - Conceptual documentation

Choose [1-9] or 'q' to quit: 
```

---

### **3. Direct Template Selection**

If you know which template you want:

```bash
# Use a specific template by name
doc-evergreen init --template tutorial-quickstart

# For a contributing guide
doc-evergreen init --template howto-contributing-guide

# For API documentation
doc-evergreen init --template reference-api
```

**This will:**
- Copy the specified template to `.doc-evergreen/`
- Skip interactive menu
- Faster workflow when you know what you need

---

### **4. Non-Interactive Mode**

For scripts or automation:

```bash
# Accept defaults, no prompts
doc-evergreen init --yes

# Combine with specific template
doc-evergreen init --template tutorial-quickstart --yes
```

---

### **5. After Initialization - Generate Documentation**

Once you've initialized with a template:

```bash
# Generate the documentation
doc-evergreen regen-doc <template-name>

# Examples:
doc-evergreen regen-doc tutorial-quickstart
doc-evergreen regen-doc contributing-guide
doc-evergreen regen-doc api-docs
```

**Note:** The `--mode` flag has been removed! Chunked generation is now the only mode (it's what works best).

---

## 📚 Real-World Usage Examples

### **Example 1: Starting a New Open Source Project**

```bash
# Step 1: Create a README
cd my-new-project
doc-evergreen init --template tutorial-quickstart
doc-evergreen regen-doc tutorial-quickstart

# Step 2: Add contributing guidelines
doc-evergreen init --template howto-contributing-guide
doc-evergreen regen-doc howto-contributing-guide

# Result: QUICKSTART.md and CONTRIBUTING.md generated
```

---

### **Example 2: Documenting Your API**

```bash
# Use the API reference template
doc-evergreen init --template reference-api
doc-evergreen regen-doc reference-api

# Result: docs/API.md with comprehensive API documentation
```

---

### **Example 3: Setting Up CI/CD Documentation**

```bash
# Use the CI integration how-to
doc-evergreen init --template howto-ci-integration
doc-evergreen regen-doc howto-ci-integration

# Result: docs/CI_INTEGRATION.md with GitHub Actions, GitLab CI examples
```

---

### **Example 4: Architecture Documentation**

```bash
# Document your system design
doc-evergreen init --template explanation-architecture
doc-evergreen regen-doc explanation-architecture

# Result: docs/ARCHITECTURE.md explaining system structure
```

---

## 🎨 Key Improvements Over v0.4.x

### ✅ **No More Confusion**
- ❌ Old: Single `--mode` flag that didn't work
- ✅ New: Just chunked generation (removed confusing option)

### ✅ **Right-Sized Output**
- ❌ Old: Default template produced 996-line README
- ✅ New: Templates tuned for appropriate length
  - Quickstart: 200-400 lines
  - Contributing: 300-500 lines
  - API docs: 500-700 lines

### ✅ **Clear Purpose**
- ❌ Old: Generic "readme.json" template
- ✅ New: 9 purpose-specific templates organized by documentation type

### ✅ **Better Prompts**
All templates now include:
- Explicit length guidance ("3-5 paragraphs")
- Scope constraints ("Skip edge cases")
- Style directives ("Be concise and actionable")

---

## 🛠️ Customizing Templates

After initialization, you can customize any template:

```bash
# Templates are in .doc-evergreen/
ls .doc-evergreen/

# Edit the JSON file to customize prompts, sections, or sources
nano .doc-evergreen/tutorial-quickstart.json
```

**See the full guide:**
```bash
# Read the comprehensive best practices guide
cat docs/TEMPLATE_BEST_PRACTICES.md
```

---

## 📖 Where to Learn More

1. **Template Best Practices**: `docs/TEMPLATE_BEST_PRACTICES.md`
   - How to create custom templates
   - Prompt engineering techniques
   - Source selection strategies
   - Real-world examples

2. **Template Quality Guide**: `docs/TEMPLATE_QUALITY.md`
   - Quality standards for templates
   - Testing methodology

3. **Release Notes**: `RELEASE_NOTES_v0.5.0.md`
   - Complete list of changes
   - Breaking changes
   - Migration guide

---

## 🤔 Which Template Should I Use?

**Quick decision tree:**

- **New users need to get started?** → `tutorial-quickstart`
- **Teaching how to do something?** → `howto-*` templates
- **Need complete technical reference?** → `reference-*` templates
- **Explaining concepts/design?** → `explanation-*` templates

**When in doubt:** Run `doc-evergreen init` and use the interactive menu!

---

## 💡 Pro Tips

1. **Start with built-in templates** - They're battle-tested and tuned
2. **Customize gradually** - Use a built-in template as starting point
3. **Read the best practices guide** - Learn prompt engineering patterns
4. **Use `--list` to browse** - Explore what's available before choosing
5. **Multiple docs?** - Use different templates for different needs

---

## 🎉 Next Steps

1. Try the interactive menu: `doc-evergreen init`
2. Generate your first doc: `doc-evergreen regen-doc <name>`
3. Read the best practices: `docs/TEMPLATE_BEST_PRACTICES.md`
4. Customize if needed: Edit `.doc-evergreen/*.json`

**Happy documenting! 📝**
