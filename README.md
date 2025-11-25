# Project Overview

**doc-evergreen** is an AI-powered documentation generation tool that keeps your documentation synchronized with your codebase. It eliminates the manual burden of updating documentation by using templates to define structure and AI to generate content from your source code.

## What It Does

doc-evergreen generates and regenerates documentation by:

1. **Reading template files** that define your documentation structure (sections, headings, prompts)
2. **Analyzing your source code** files specified in the template
3. **Using AI (Claude)** to generate clear, accurate content for each section
4. **Showing you a preview** of all changes before applying them
5. **Writing the updated documentation** to your project

## Main Purpose

The tool solves a critical problem in software development: **documentation drift**. As code evolves, documentation becomes outdated, leading to confusion and wasted developer time. doc-evergreen makes it effortless to keep docs fresh by regenerating them from templates whenever your code changes.

## Key Features

- **Convention-based workflow**: Templates live in `.doc-evergreen/` directory, making setup intuitive and portable across projects
- **Section-by-section generation**: Documents are generated incrementally with context awareness between sections
- **Change preview and approval**: See exactly what will change with unified diffs before applying updates
- **Iterative refinement**: Regenerate multiple times in one session to refine output
- **Smart source resolution**: Supports glob patterns, relative paths, and automatic exclusion of virtual environments
- **Template validation**: Validates all source files upfront (fail-fast approach) before generation begins
- **Short command syntax**: Use `regen-doc readme` instead of long paths for common templates
- **Auto-approve mode**: Perfect for CI/CD pipelines with `--auto-approve` flag
- **Context management**: Previous sections inform later sections for coherent, flowing documentation
- **Bootstrap command**: `init` creates starter templates to get you productive immediately

## Value Proposition

**For Developers:**
- Spend minutes updating docs instead of hours
- Confidence that documentation matches current code
- Preview changes before committing
- Works with any project structure

**For Teams:**
- Documentation stays current as code evolves
- Consistent documentation style across projects
- Easy onboarding (templates are self-documenting)
- Integrates into existing CI/CD workflows

**For Projects:**
- Better developer experience through accurate docs
- Reduced maintenance burden
- Templates live with code in version control
- No vendor lock-in (templates are simple JSON)

# Installation and Setup

## Prerequisites

Before installing doc-evergreen, ensure you have:

- **Python 3.11 or higher** - Check your version with `python --version` or `python3 --version`
- **Anthropic API key** - Required for AI-powered documentation generation
  - Get your key from: https://console.anthropic.com/
  - You'll need to create an account if you don't have one

## Installation Methods

### Recommended: Using pipx

[pipx](https://pipx.pypa.io/) is the recommended installation method as it installs doc-evergreen in an isolated environment, preventing dependency conflicts:

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install doc-evergreen
pipx install git+https://github.com/momuno/doc-evergreen.git

# Verify installation
doc-evergreen --help
```

### Alternative: Using pip

You can also install with pip, though pipx is preferred:

```bash
pip install git+https://github.com/momuno/doc-evergreen.git

# Verify installation
doc-evergreen --help
```

### For Development

If you want to contribute or modify doc-evergreen:

```bash
# Clone the repository
git clone https://github.com/momuno/doc-evergreen.git
cd doc-evergreen

# Install in editable mode
pip install -e .

# Run tests to verify
python -m pytest tests/ -v
```

## Configuration

### Setting Up Your API Key

doc-evergreen requires an Anthropic API key to generate documentation. Set it as an environment variable:

**Linux/macOS:**
```bash
export ANTHROPIC_API_KEY=your_key_here
```

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=your_key_here
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
```

For permanent configuration, add the export command to your shell profile (`.bashrc`, `.zshrc`, etc.) or system environment variables.

### Initializing Your First Project

Once installed, navigate to your project directory and initialize doc-evergreen:

```bash
# Navigate to your project
cd /path/to/your-project

# Create initial template
doc-evergreen init

# Or specify a project name
doc-evergreen init --name "My Project"
```

This creates `.doc-evergreen/readme.json` - a starter template you can customize.

### Directory Structure

doc-evergreen uses a convention-based approach. After initialization, your project will have:

```
your-project/
├── .doc-evergreen/          # Template directory (convention)
│   └── readme.json          # Created by init command
├── README.md                # Will be generated/updated
└── src/                     # Your source code
```

The `.doc-evergreen/` directory travels with your project and should be committed to version control.

## Verification

Test your installation with a quick documentation generation:

```bash
# Generate documentation from the default template
doc-evergreen regen-doc readme

# You'll see output like:
# [1/4] Generating: # Overview
#       Sources: README.md, src/main.py (2 files)
#       ✓ Complete (3.2s)
# ...
# Apply these changes? [y/N]:
```

If you see the generation progress and change preview, your installation is working correctly!

## Troubleshooting

### Command Not Found

If `doc-evergreen` isn't recognized after installation:

- **pipx users**: Run `pipx ensurepath` and restart your terminal
- **pip users**: Ensure your Python scripts directory is in PATH
- Try using the full path: `python -m doc_evergreen.cli`

### API Key Issues

If you get authentication errors:

- Verify your API key is set: `echo $ANTHROPIC_API_KEY`
- Ensure the key has no extra spaces or quotes
- Check your key is valid at https://console.anthropic.com/

### Python Version Error

If installation fails due to Python version:

- Check your version: `python --version`
- doc-evergreen requires Python 3.11 or higher
- Consider using [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions

### Installation Fails with Dependency Errors

If you encounter dependency conflicts:

- Use pipx instead of pip (installs in isolation)
- Create a virtual environment: `python -m venv venv && source venv/bin/activate`
- Update pip: `pip install --upgrade pip`

## Uninstallation

### Remove with pipx
```bash
pipx uninstall doc-evergreen
```

### Remove with pip
```bash
pip uninstall doc-evergreen
```

Your project templates in `.doc-evergreen/` will remain untouched during uninstallation.

## Next Steps

Now that doc-evergreen is installed:

1. **Customize your template** - Edit `.doc-evergreen/readme.json` to match your needs
2. **Generate documentation** - Run `doc-evergreen regen-doc readme`
3. **Learn advanced features** - See [docs/USER_GUIDE.md](./docs/USER_GUIDE.md) for complete reference
4. **Explore templates** - Read [docs/TEMPLATES.md](./docs/TEMPLATES.md) for template creation guide

For detailed installation options and advanced troubleshooting, see [INSTALLATION.md](./INSTALLATION.md).

# Usage

## Basic Workflow

The typical doc-evergreen workflow consists of four steps:

1. **Initialize** - Create a starter template in your project
2. **Customize** - Edit the template to define your documentation structure
3. **Generate** - Run the regeneration command to create content
4. **Review** - Preview changes and approve or iterate

### Step-by-Step Example

```bash
# 1. Navigate to your project
cd /path/to/your-project

# 2. Set your API key (if not already set)
export ANTHROPIC_API_KEY=your_key_here

# 3. Initialize doc-evergreen
doc-evergreen init
# ✅ Created: .doc-evergreen/readme.json

# 4. (Optional) Customize the template
nano .doc-evergreen/readme.json

# 5. Generate documentation
doc-evergreen regen-doc readme
```

## Common Use Cases

### Generate README Documentation

The most common use case is generating or updating your project's README:

```bash
# Generate from the default readme template
doc-evergreen regen-doc readme

# The command will:
# - Read .doc-evergreen/readme.json
# - Analyze your source files
# - Generate content section by section
# - Show you a diff of changes
# - Prompt for approval
```

**Example output:**
```
[1/4] Generating: # Overview
      Sources: README.md, src/main.py (2 files)
      ✓ Complete (3.2s)
[2/4] Generating: ## Installation
      Sources: pyproject.toml, setup.py (2 files)
      ✓ Complete (2.1s)
[3/4] Generating: ## Usage
      Sources: README.md, examples/**, src/**/*.py (15 files)
      ✓ Complete (4.8s)
[4/4] Generating: ## Development
      Sources: README.md, pyproject.toml, tests/**/*.py (8 files)
      ✓ Complete (2.9s)

Changes detected:
+++ README.md
@@ -1,5 +1,12 @@
 # My Project
+
+A powerful tool for automated documentation generation...
+
+## Key Features
+- AI-powered content generation
+- Template-based structure

Apply these changes? [y/N]: y
✓ File written: README.md

Regenerate with updated sources? [y/N]: n
Completed 1 iteration
```

### Iterative Refinement

After reviewing generated content, you can regenerate immediately with the updated documentation as context:

```bash
# First generation
doc-evergreen regen-doc readme
# Review changes, approve

# Prompt appears: "Regenerate with updated sources?"
# Answer 'y' to iterate

# The generator now sees:
# - Your updated README.md
# - Original source files
# - Can refine inconsistencies or add missing details
```

This is useful when:
- The first pass missed important details
- You want to refine the tone or style
- Changes revealed inconsistencies with other sections

### CI/CD Integration

For automated pipelines, use `--auto-approve` to skip the confirmation prompt:

```bash
# In your CI/CD pipeline
doc-evergreen regen-doc readme --auto-approve
```

**Example GitHub Actions workflow:**
```yaml
name: Update Documentation
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'pyproject.toml'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install doc-evergreen
        run: pipx install git+https://github.com/momuno/doc-evergreen.git
      
      - name: Regenerate documentation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: doc-evergreen regen-doc readme --auto-approve
      
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add README.md
          git commit -m "docs: auto-update README" || exit 0
          git push
```

### Custom Output Locations

Override the output path specified in your template:

```bash
# Generate to a different location
doc-evergreen regen-doc readme --output docs/README.md

# Useful for:
# - Testing changes before overwriting main README
# - Generating variants (README.md vs docs/index.md)
# - Multi-language documentation (README.en.md, README.ja.md)
```

### Multiple Documentation Files

Create separate templates for different documentation needs:

```bash
# Initialize with default readme template
doc-evergreen init

# Create additional templates manually
nano .doc-evergreen/api-reference.json
nano .doc-evergreen/user-guide.json

# Generate each independently
doc-evergreen regen-doc readme
doc-evergreen regen-doc api-reference
doc-evergreen regen-doc user-guide
```

**Directory structure:**
```
your-project/
├── .doc-evergreen/
│   ├── readme.json          # Main README
│   ├── api-reference.json   # API docs
│   └── user-guide.json      # User guide
├── README.md
├── docs/
│   ├── API_REFERENCE.md
│   └── USER_GUIDE.md
└── src/
```

### Using Full Paths

While short names are convenient, full paths still work:

```bash
# Short name (convention-based)
doc-evergreen regen-doc readme
# → Looks for .doc-evergreen/readme.json

# Relative path
doc-evergreen regen-doc templates/custom.json

# Absolute path
doc-evergreen regen-doc /path/to/templates/special.json
```

## Command Reference

### `doc-evergreen init`

Initialize doc-evergreen in the current project.

**Options:**
- `--name TEXT` - Project name (defaults to directory name)
- `--description TEXT` - Project description
- `--force` - Overwrite existing template

**Examples:**
```bash
# Basic initialization
doc-evergreen init

# With custom project name
doc-evergreen init --name "My Awesome Project"

# Force overwrite existing template
doc-evergreen init --force
```

### `doc-evergreen regen-doc`

Regenerate documentation from a template.

**Arguments:**
- `TEMPLATE_NAME` - Template name or path (required)

**Options:**
- `--auto-approve` - Apply changes without confirmation prompt
- `--output PATH` - Override output path from template

**Examples:**
```bash
# Basic usage with short name
doc-evergreen regen-doc readme

# Auto-approve for CI/CD
doc-evergreen regen-doc readme --auto-approve

# Custom output location
doc-evergreen regen-doc readme --output custom/path.md

# Using full path
doc-evergreen regen-doc .doc-evergreen/readme.json
```

### `doc-evergreen doc-update` (Legacy)

**Note:** This command is deprecated. Use `regen-doc` instead for the improved workflow with change previews and approval.

```bash
# Legacy command (still works)
doc-evergreen doc-update template.json

# Prefer new command
doc-evergreen regen-doc readme
```

## Template Resolution

Doc-evergreen resolves template names using a convention-based approach:

1. **Short names without `.json`** - Looks in `.doc-evergreen/{name}.json`
   ```bash
   regen-doc readme → .doc-evergreen/readme.json
   regen-doc api    → .doc-evergreen/api.json
   ```

2. **Names with `.json`** - Treated as relative or absolute paths
   ```bash
   regen-doc template.json           → ./template.json
   regen-doc templates/custom.json   → ./templates/custom.json
   regen-doc /abs/path/doc.json      → /abs/path/doc.json
   ```

3. **Error handling** - Clear messages when template not found
   ```bash
   $ doc-evergreen regen-doc missing
   Error: Template not found: missing
   
   Tried:
     - .doc-evergreen/missing.json
     - missing
   
   Run 'doc-evergreen init' to create starter template.
   ```

## Working Directory Conventions

Doc-evergreen uses your **current working directory** as the project root:

- **Source paths** in templates are relative to `cwd`
- **Output files** are written relative to `cwd`
- **Template location** doesn't affect path resolution

**Example:**
```json
{
  "document": {
    "output": "README.md",
    "sections": [
      {
        "heading": "# Overview",
        "sources": ["src/**/*.py", "pyproject.toml"]
      }
    ]
  }
}
```

When you run `doc-evergreen regen-doc readme`:
- Reads from `./src/**/*.py` and `./pyproject.toml`
- Writes to `./README.md`
- All paths relative to where you ran the command

**Best practice:** Always run doc-evergreen from your project root directory.

## Next Steps

- **Customize templates** - See [TEMPLATES.md](./TEMPLATES.md) for template syntax and structure
- **Best practices** - See [BEST_PRACTICES.md](./BEST_PRACTICES.md) for design patterns
- **Complete reference** - See [USER_GUIDE.md](./USER_GUIDE.md) for full documentation

# Development Workflow

This guide covers testing, building, and contributing to doc-evergreen.

## Running Tests

The project uses **pytest** for testing with full test coverage across all components.

### Prerequisites

```bash
# Install development dependencies
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Running All Tests

```bash
# Run complete test suite
uv run python -m pytest tests/ -v

# Expected output: All 119 tests should pass
# ✓ 119 passed in ~X.Xs
```

### Running Specific Test Files

```bash
# Test specific component
uv run pytest tests/test_chunked_generator.py -v

# Test CLI commands
uv run pytest tests/test_cli_installation.py -v

# Test template parsing
uv run pytest tests/test_package_config.py -v
```

### Test Categories

The test suite is organized by component:

- **Core Functionality**
  - `test_chunked_generator.py` - Section-by-section generation
  - `test_context_manager.py` - Context flow between sections
  - `test_source_validator.py` - Source file validation
  - `test_change_detection.py` - Diff generation

- **CLI & Workflow**
  - `test_cli_installation.py` - CLI entry point verification
  - `test_init_command.py` - Project initialization
  - `test_full_workflow_init_to_regen.py` - Complete workflows
  - `test_iterative_refinement.py` - Multi-iteration generation
  - `test_progress_feedback.py` - Progress reporting

- **Template System**
  - `test_template_discovery.py` - Convention-based path resolution
  - `test_cwd_path_resolution.py` - Working directory handling
  - `test_cross_directory_usage.py` - Multi-project isolation

- **Integration**
  - `test_integration_regen_workflow.py` - End-to-end regeneration
  - `test_package_config.py` - Package configuration

### Running Tests Without API Key

Most tests use `TestModel` from `pydantic-ai` to run without requiring an Anthropic API key:

```python
@pytest.fixture
def test_model():
    """Provide TestModel for tests without API key."""
    return TestModel()
```

Integration tests that require actual API calls are skipped when no key is present.

## Test-Driven Development (TDD)

This project follows **strict TDD** methodology:

### Red-Green-Refactor Cycle

```
🔴 RED   → Write failing test first
🟢 GREEN → Write minimal code to pass
🔵 REFACTOR → Improve while tests protect
```

### Example Test Structure

```python
class TestFeatureName:
    """Test description of feature."""

    def test_specific_behavior(self, fixtures):
        """
        Given: Initial conditions
        When: Action is performed
        Then: Expected outcome occurs
        """
        # Arrange - Set up test conditions
        ...
        
        # Act - Perform the action
        result = function_under_test(...)
        
        # Assert - Verify expectations
        assert result == expected
```

### Test Organization

Each test file includes:
- **Fixtures** - Reusable test setup
- **Test Classes** - Grouped by feature area
- **Docstrings** - Given/When/Then format
- **Assertions** - Clear, specific expectations

## Building the Project

### Package Structure

```
doc-evergreen/
├── doc_evergreen/           # Main package
│   ├── cli.py              # CLI commands
│   ├── chunked_generator.py # Generation engine
│   ├── context_manager.py   # Section context
│   ├── change_detection.py  # Diff generation
│   └── core/               # Core components
│       ├── template_schema.py
│       └── source_validator.py
├── tests/                   # Test suite
├── pyproject.toml          # Package configuration
└── README.md
```

### Package Configuration

The project uses **hatchling** as the build backend (defined in `pyproject.toml`):

```toml
[project]
name = "doc-evergreen"
version = "0.4.1"
requires-python = ">=3.11"

[project.scripts]
doc-evergreen = "doc_evergreen.cli:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Building Distribution

```bash
# Build source and wheel distributions
python -m build

# Output: dist/doc-evergreen-0.4.1.tar.gz
#         dist/doc_evergreen-0.4.1-*.whl
```

### Installing Locally

```bash
# Development mode (editable install)
pip install -e .

# From wheel
pip install dist/doc_evergreen-0.4.1-*.whl

# From source tarball
pip install dist/doc-evergreen-0.4.1.tar.gz
```

## Contributing

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/momuno/doc-evergreen.git
   cd doc-evergreen
   ```

2. **Install with development dependencies**
   ```bash
   # Using uv (recommended)
   uv sync --dev
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Set up API key**
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```

4. **Verify installation**
   ```bash
   doc-evergreen --help
   uv run pytest tests/ -v
   ```

### Contribution Workflow

1. **Write tests first** (TDD approach)
   - Create test in appropriate `test_*.py` file
   - Run test to confirm it fails (🔴 RED)

2. **Implement minimal solution**
   - Write code to make test pass
   - Run test to confirm success (🟢 GREEN)

3. **Refactor and improve**
   - Clean up implementation
   - Tests protect against regressions (🔵 REFACTOR)

4. **Ensure all tests pass**
   ```bash
   uv run pytest tests/ -v
   ```

5. **Submit pull request**
   - Clear description of changes
   - Reference related issues
   - Include test coverage

### Code Style

- **Type hints** - Use Python type annotations
- **Docstrings** - Document public APIs
- **Comments** - Explain "why", not "what"
- **Naming** - Descriptive, consistent conventions

### Testing Guidelines

- **Test behavior**, not implementation
- **One assertion per test** (when possible)
- **Clear test names** - Describe what's tested
- **Use fixtures** - Reusable test setup
- **Mock external dependencies** - Tests should be fast

### Where to Start

Good first contributions:

1. **Documentation improvements**
   - Fix typos or unclear sections
   - Add examples to docs
   - Improve error messages

2. **Test coverage**
   - Add edge case tests
   - Test error conditions
   - Integration test scenarios

3. **Bug fixes**
   - Check open issues
   - Reproduce bug with test
   - Fix and verify

4. **Feature enhancements**
   - Discuss in issue first
   - Write tests before code
   - Update documentation

### Submitting Issues

Include:
- **Clear description** of problem/feature
- **Steps to reproduce** (for bugs)
- **Expected vs actual behavior**
- **Environment details** (Python version, OS)
- **Test case** (if applicable)

## CI/CD Integration

### Automated Testing in Pipelines

```yaml
# Example GitHub Actions workflow
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v
```

### Automated Documentation Updates

```yaml
# Generate docs on push to main
name: Update Docs
on:
  push:
    branches: [main]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install doc-evergreen
      - env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: doc-evergreen regen-doc readme --auto-approve
      - uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "docs: auto-update README"
```

## Project Conventions

### Directory Structure

```
.doc-evergreen/     # Template storage (convention)
├── readme.json     # README template
├── api.json        # API docs template
└── guide.json      # User guide template
```

### Path Resolution

- **Templates** - Resolved from `.doc-evergreen/` or as paths
- **Sources** - Always relative to current working directory (cwd)
- **Output** - Written relative to cwd

### Template Format

Templates use JSON schema defined in `template_schema.py`:

```json
{
  "document": {
    "title": "Project Name",
    "output": "README.md",
    "sections": [
      {
        "heading": "## Overview",
        "prompt": "Describe the project",
        "sources": ["src/**/*.py", "README.md"]
      }
    ]
  }
}
```

See `docs/TEMPLATES.md` for complete reference.

## Troubleshooting Development Issues

### Tests Fail with Import Errors

```bash
# Ensure package installed in development mode
pip install -e .

# Or reinstall with dev dependencies
pip install -e ".[dev]"
```

### Tests Fail with API Key Errors

Most tests use `TestModel` and don't require API keys. If tests fail:

```bash
# Check if test needs API key (integration tests)
grep -r "ANTHROPIC_API_KEY" tests/

# Set key for integration tests
export ANTHROPIC_API_KEY=your_key
```

### CLI Command Not Found

```bash
# Verify installation
pip show doc-evergreen

# Reinstall entry point
pip install --force-reinstall --no-deps doc-evergreen

# Or use direct invocation
python -m doc_evergreen.cli --help
```

### Tests Pass Locally but Fail in CI

- Check Python version consistency
- Verify dependencies in `pyproject.toml`
- Ensure tests don't depend on local files
- Check for timezone/locale issues

## Additional Resources

- **Template Reference**: `docs/TEMPLATES.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **Best Practices**: `docs/BEST_PRACTICES.md`
- **Issue Tracker**: https://github.com/momuno/doc-evergreen/issues

---

**Questions?** Open an issue or check existing documentation in the `docs/` directory.