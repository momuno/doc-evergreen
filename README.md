# doc-evergreen

**AI-powered documentation that stays in sync with your code**

Keep your documentation fresh without the manual grind. Define templates once, regenerate as your code evolves.

---

## Quick Start

Get productive in 5 minutes.

### Installation

```bash
# Install with pipx (recommended)
pipx install git+https://github.com/momuno/doc-evergreen.git

# Or with pip
pip install git+https://github.com/momuno/doc-evergreen.git

# Verify installation
doc-evergreen --help
```

See [INSTALLATION.md](./INSTALLATION.md) for detailed installation, troubleshooting, and alternative methods.

### Your First Documentation

```bash
# 1. Navigate to your project
cd /path/to/your-project

# 2. Set up API key (required for AI generation)
export ANTHROPIC_API_KEY=your_key_here
# Get key from: https://console.anthropic.com/

# 3. Initialize (creates .doc-evergreen/readme.json)
doc-evergreen init

# 4. (Optional) Customize the template
nano .doc-evergreen/readme.json

# 5. Generate documentation
doc-evergreen regen-doc readme

# See all available options
doc-evergreen regen-doc --help
```

### Important Options

```bash
# Auto-approve for CI/CD (skips approval prompt)
doc-evergreen regen-doc readme --auto-approve

# Override output location
doc-evergreen regen-doc readme --output custom/path.md

# Use full path to template (instead of short name)
doc-evergreen regen-doc .doc-evergreen/readme.json
```

**Works with any project.** The generated template is fully customizable.

**Next steps:** See [docs/USER_GUIDE.md](./docs/USER_GUIDE.md) for complete reference documentation.

---

## What It Does

**The Problem:**
Documentation gets stale. Code changes, docs don't. Users get confused, developers spend hours manually updating.

**The Solution:**
Define documentation structure in templates. Regenerate with one command. Preview changes. Approve. Done.

---

## How It Works

1. **Templates define structure**
   Store in `.doc-evergreen/` (travels with your project)

2. **AI generates content**
   Reads your source code, writes documentation

3. **You review and approve**
   See exactly what changed before applying

4. **Iterate freely**
   Refine multiple times without restarting

---

## Key Features

- ✅ **Convention-based**: Templates in `.doc-evergreen/`, zero config
- ✅ **Works anywhere**: Run from any project directory
- ✅ **Short commands**: `regen-doc readme` instead of long paths
- ✅ **Preview changes**: See diff before applying
- ✅ **Bootstrap instantly**: `init` creates starter template
- ✅ **Iterative**: Regenerate multiple times in one session

---

## Example

```bash
$ cd /my-project

$ doc-evergreen init --name "My Awesome Project"
✅ Created: .doc-evergreen/readme.json
Next steps:
  1. Review and customize .doc-evergreen/readme.json
  2. Run: doc-evergreen regen-doc readme

$ doc-evergreen regen-doc readme
[1/4] Generating: # Overview
      Sources: README.md, src/main.py (2 files)
      ✓ Complete (3.2s)
...
Showing changes:
+++ README.md
@@ -1,5 +1,12 @@
 # My Awesome Project
+
+A powerful tool for...

Apply these changes? [y/N]: y
✅ Updated: README.md

Regenerate with updated sources? [y/N]: n
Completed 1 iteration
```

---

## Documentation

**Getting Started:**
- **README** (this file) - Quick start and overview
- **[INSTALLATION.md](./INSTALLATION.md)** - Detailed installation, troubleshooting, and uninstall

**Reference Documentation:**
- **[docs/USER_GUIDE.md](./docs/USER_GUIDE.md)** - Complete command reference and workflows
- **[docs/TEMPLATES.md](./docs/TEMPLATES.md)** - Template creation guide
- **[docs/BEST_PRACTICES.md](./docs/BEST_PRACTICES.md)** - Design patterns and best practices

---

## Requirements

- Python 3.11+
- Anthropic API key (for AI generation)

---

## Installation

### Recommended (pipx):
```bash
pipx install git+https://github.com/momuno/doc-evergreen.git
```

### Standard (pip):
```bash
pip install git+https://github.com/momuno/doc-evergreen.git
```

### Development:
```bash
git clone https://github.com/momuno/doc-evergreen.git
cd doc-evergreen
pip install -e .
```

### Uninstall:
```bash
# If installed with pipx (recommended)
pipx uninstall doc-evergreen

# If installed with pip
pip uninstall doc-evergreen
```

See [INSTALLATION.md](./INSTALLATION.md) for troubleshooting and detailed uninstall instructions.

---

## The .doc-evergreen/ Convention

Like `.github/` or `.vscode/`, doc-evergreen uses a convention directory:

```
your-project/
├── .doc-evergreen/     # Templates live here
│   ├── readme.json
│   └── api.json
├── README.md           # Generated docs
└── src/                # Your code
```

**Benefits:**
- Templates travel with project
- Zero configuration
- Short commands: `regen-doc readme`
- Obvious where things go

---

## Commands

### Initialize a project
```bash
doc-evergreen init
doc-evergreen init --name "Project Name"
doc-evergreen init --force  # Overwrite existing
```

Creates `.doc-evergreen/readme.json` starter template.

### Regenerate documentation (Main Command)
```bash
doc-evergreen regen-doc <template-name>
doc-evergreen regen-doc <template-name> --auto-approve
doc-evergreen regen-doc <template-name> --output custom/path.md
```

**This is the primary command you'll use.**

Supports:
- **Short names**: `readme` → `.doc-evergreen/readme.json`
- **Full paths**: `templates/api.json`
- **Absolute paths**: `/path/to/template.json`

### Legacy Commands

The `doc-update` command still exists for backwards compatibility but `regen-doc` is preferred as it provides change preview and approval workflow.

---

## Development

```bash
# Run tests
uv run python -m pytest tests/ -v

# All 119 tests should pass
```

---

## Philosophy

**Convention over Configuration**
No config files. No setup. Just `init` and `regen`.

**cwd = Project Root**
Run from your project. Sources relative to where you are.

**Template Location Irrelevant**
Store templates anywhere. Convention makes common case simple.

---

## Support

- **Issues**: https://github.com/momuno/doc-evergreen/issues
- **Questions**: See [docs/USER_GUIDE.md](./docs/USER_GUIDE.md)

---

## License

MIT (see LICENSE file)

---

**Get started in 5 minutes. Zero configuration. Works with any project.**
