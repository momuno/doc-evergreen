# doc-evergreen

**AI-powered documentation that stays in sync with your code**

Keep your documentation fresh without the manual grind. Define templates once, regenerate as your code evolves.

---

## Quick Start

```bash
# 1. Install (pipx handles everything)
pipx install git+https://github.com/momuno/doc-evergreen.git

# 2. Set up API key (required for AI generation)
export ANTHROPIC_API_KEY=your_key_here
# Get key from: https://console.anthropic.com/

# 3. Bootstrap your project
cd /your-project
doc-evergreen init

# 4. Generate docs
doc-evergreen regen-doc readme
```

**Works with any project.** Customize the generated template to fit your needs.

**Need help?** See [INSTALLATION.md](./INSTALLATION.md) for detailed setup, troubleshooting, and alternative install methods.

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

**Start here (5 min read):**
- This README - Quick overview
- [INSTALLATION.md](./INSTALLATION.md) - Install instructions & troubleshooting

**Detailed reference (for AI or deep dives):**
- [docs/USER_GUIDE.md](./docs/USER_GUIDE.md) - Complete workflows (19kb)
- [docs/TEMPLATES.md](./docs/TEMPLATES.md) - Template creation (17kb)
- [docs/BEST_PRACTICES.md](./docs/BEST_PRACTICES.md) - Design patterns (21kb)

**Upgrading from v0.3.0?**
- [docs/MIGRATION_v0.3_to_v0.4.md](./docs/MIGRATION_v0.3_to_v0.4.md) - Breaking changes & migration guide

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

See [INSTALLATION.md](./INSTALLATION.md) for troubleshooting.

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
doc-evergreen init [--name "Project Name"] [--force]
```

Creates `.doc-evergreen/readme.json` starter template.

### Regenerate documentation
```bash
doc-evergreen regen-doc <template-name>
doc-evergreen regen-doc <template-name> --auto-approve
doc-evergreen regen-doc <template-name> --output custom/path.md
```

Supports:
- Short names: `readme` → `.doc-evergreen/readme.json`
- Full paths: `templates/api.json`
- Absolute paths: `/path/to/template.json`

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
