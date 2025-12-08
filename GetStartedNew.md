# Doc-Evergreen 101: Quick Start Guide


# Introduction

**doc-evergreen** is an AI-powered documentation generation tool that solves one of software development's most persistent challenges: keeping documentation synchronized with your evolving codebase. As developers update code, documentation often falls behind, creating confusion and wasted time. doc-evergreen eliminates this "documentation drift" by automatically generating fresh, accurate documentation from your source code whenever you need it.

The tool works by combining the structure you define with AI-generated content. You create template files that specify what sections your documentation should have and which source code files to analyze. When you run doc-evergreen, it reads your templates, examines your code, and uses AI (Claude) to generate clear, relevant content for each section. Before making any changes, it shows you exactly what will be updated with a detailed preview, giving you full control over the final output.

By the end of this tutorial, you'll know how to set up doc-evergreen in your project, create templates that define your documentation structure, and use the command-line interface to generate and regenerate documentation as your code evolves. You'll learn the `.doc-evergreen/` convention that makes templates portable across projects, understand how to preview and approve changes, and discover workflows that keep your documentation effortlessly up-to-date.

Whether you're maintaining a README, API documentation, or technical guides, doc-evergreen transforms documentation from a manual chore into an automated process that scales with your development workflow.

# Prerequisites

Before installing doc-evergreen, ensure your system meets the following requirements and you have the necessary components ready.

## System Requirements

**Python Version:** doc-evergreen requires Python 3.11 or higher. The tool supports Python versions 3.11, 3.12, and 3.13. You can check your Python version by running `python3 --version` in your terminal.

**Package Manager:** While you can use pip, **pipx is strongly recommended** for installation. pipx automatically handles virtual environments and works seamlessly on all systems, including those with externally-managed Python installations (like Debian/Ubuntu). If you don't have pipx installed, you can get it via `pip install --user pipx` or `apt install pipx` on Ubuntu/Debian systems.

## Required Setup

**Anthropic API Key:** doc-evergreen uses Anthropic's Claude AI for documentation generation, so you'll need a valid API key from https://console.anthropic.com/. Have this ready before installation, as the tool won't function without it. You'll need to sign up for an Anthropic account if you don't already have one.

**Git Access:** Since doc-evergreen is currently distributed via GitHub, ensure you have git installed and can access GitHub repositories. The installation process will clone or download directly from the repository.

## What to Have Ready

**Target Repository:** Identify the code repository or project directory where you want to generate documentation. doc-evergreen works by analyzing your codebase and generating documentation based on templates, so having a clear project structure will help you get the most out of the tool.

**Development Environment:** If you plan to contribute to doc-evergreen or need a development installation, ensure you have a clean environment for creating virtual environments and can run development tools like pytest for testing.

# Installation

The fastest and most reliable way to install doc-evergreen is using **pipx**, which automatically handles virtual environments and works on all systems, including modern Linux distributions with externally-managed Python environments.

## Prerequisites

Before installing doc-evergreen, ensure you have Python 3.7+ installed on your system. You'll also need pipx, which you can install with:

```bash
# Install pipx if you don't have it
pip install --user pipx
# Or on Debian/Ubuntu systems:
apt install pipx
```

## Installation Steps

### Step 1: Install doc-evergreen

Install doc-evergreen directly from the GitHub repository using pipx:

```bash
pipx install git+https://github.com/momuno/doc-evergreen.git
```

Alternatively, if you prefer to clone the repository first:

```bash
git clone https://github.com/momuno/doc-evergreen.git
pipx install -e ./doc-evergreen
```

### Step 2: Verify Installation

Confirm that doc-evergreen was installed successfully by running:

```bash
doc-evergreen --help
```

You should see output similar to:

```
Usage: doc-evergreen [OPTIONS] COMMAND [ARGS]...

  doc-evergreen - AI-powered documentation generation.
  ...
```

### Step 3: Configure API Key

doc-evergreen requires an Anthropic API key to function. First, obtain your API key from https://console.anthropic.com/, then set it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

For permanent configuration, add this line to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

Verify your API key is properly configured:

```bash
echo $ANTHROPIC_API_KEY
```

This should display your API key, confirming that doc-evergreen is ready to use.

# Quick Start

This guide walks you through creating your first documentation with doc-evergreen in just a few commands. You'll initialize a project, customize the template, and generate a complete README file.

## Prerequisites

Before starting, you'll need an Anthropic API key for Claude. Create the file `~/.claude/api_key.txt` and add your API key:

```bash
mkdir -p ~/.claude
echo "your-api-key-here" > ~/.claude/api_key.txt
```

## Step 1: Initialize Your Project

Navigate to your project directory and run the init command:

```bash
cd your-project
doc-evergreen init --name "My Awesome Project"
```

This creates a `.doc-evergreen/` directory with a `readme.json` template file. The template includes placeholders for your project name and references to your source files.

## Step 2: Generate Documentation

Generate your README using the template's short name:

```bash
doc-evergreen regen-doc readme --auto-approve
```

The `--auto-approve` flag skips the confirmation prompt and generates the documentation immediately. doc-evergreen will analyze your source files, apply the template, and create a comprehensive README.md file.

## What Happens Next

After running these commands, you'll have:
- A `.doc-evergreen/readme.json` template file you can customize
- A generated `README.md` file tailored to your project
- A foundation for keeping your documentation synchronized with code changes

You can edit the template file to modify sections, add custom prompts, or change the output format. Simply run `regen-doc` again whenever you want to refresh your documentation with the latest code changes.

## Initialize Your Repository

To set up doc-evergreen in your repository, navigate to your project directory and run the initialization command:

```bash
doc-evergreen init
```

This command creates a `.doc-evergreen.yaml` configuration file in your project root. The file contains default settings that you can customize for your project's needs. Here's what a basic configuration looks like:

```yaml
# Template directory (optional - uses built-in templates by default)
template_dir: null

# Default source files to analyze for all documentation
default_sources: []

# LLM configuration
llm:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"

# File-specific configurations
files: {}
```

After running `init`, doc-evergreen will automatically detect your project root by looking for the `.doc-evergreen.yaml` file. If you're working in a Git repository, it can also use the `.git` directory as a fallback to determine the project boundaries. You can now customize the configuration file to specify which source files should be analyzed, set up custom templates, or adjust the LLM settings to match your preferences.

The configuration file serves as the central control point for all doc-evergreen operations in your repository. You can add file-specific settings under the `files` section and define default source patterns that apply to all your documentation generation tasks.

## Understanding Templates

Templates are the core building blocks of doc-evergreen. They are JSON files that define exactly what documentation you want to generate, how it should be structured, and where the AI should look for information about your project. Think of a template as a blueprint that tells doc-evergreen: "Generate a README with these specific sections, using these source files as context, and save the result here."

Each template contains a document definition with three essential components: a title for human reference, an output path specifying where to save the generated documentation, and an array of sections that define the structure and content. The real power lies in the sections - each one includes a heading that appears in your final document, a detailed prompt that instructs the AI on what to write, and a list of source files that provide the necessary context about your codebase.

Here's a simple template structure to illustrate how this works:

```json
{
  "document": {
    "title": "Quick Start Guide",
    "output": "QUICKSTART.md",
    "sections": [
      {
        "heading": "# Quick Start",
        "prompt": "Write a friendly 5-minute getting started guide. Cover what this project does, prerequisites, installation, and a simple first example.",
        "sources": ["README.md", "pyproject.toml", "examples/**"]
      },
      {
        "heading": "## Your First Steps",
        "prompt": "Provide 3-5 concrete first tasks a new user should try. Each task should be completable in under 2 minutes.",
        "sources": ["README.md", "examples/**", "src/**/cli.py"]
      }
    ]
  }
}
```

This template would generate a quickstart guide with two main sections, drawing information from your existing README, project configuration, examples, and CLI code. The AI uses these source files to understand your project and create relevant, accurate documentation that stays in sync with your actual codebase.

## Generate Your First Document

Now that you have your template configured, let's generate your first documentation. The `doc-evergreen generate` command will analyze your codebase and create documentation based on your template.

Run the following command in your project directory:

```bash
doc-evergreen generate
```

You should see output similar to this:

```
✓ API key loaded from /home/user/.claude/api_key.txt (64 chars)
✓ Template loaded: README.md (tutorial)
✓ Analyzing codebase...
✓ Generating section: Project Overview
✓ Generating section: Installation
✓ Generating section: Quick Start
✓ Documentation generated: README.md
```

The command automatically detects your `doc_template.json` file and generates documentation according to your template structure. Each section is processed individually, allowing for focused and relevant content generation based on your actual code.

Once generation completes, you'll find your new documentation file in the project root directory. Open `README.md` (or whatever filename you specified in your template) to review the generated content. The documentation will be tailored to your specific codebase, following the doc type you selected (tutorial, howto, reference, or explanation) and including relevant code examples and explanations drawn from your source files.

# Customizing for Your Repository

Doc-evergreen works out of the box with sensible defaults, but you can customize it to fit your repository's specific needs. The tool looks for a `.doc-evergreen.yaml` configuration file in your project root (the same directory as your `.git` folder) to override default settings.

## Configuration File Structure

Create a `.doc-evergreen.yaml` file in your project root to customize doc-evergreen's behavior. Here's a complete example showing all available options:

```yaml
# Directory containing your documentation templates
template_dir: "docs/templates"

# Default source files to include for all documentation
default_sources:
  - "src/**/*.py"
  - "README.md"
  - "pyproject.toml"

# LLM provider settings
llm:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"

# Per-file configuration
files:
  "docs/api-reference.md":
    template: "api-template.md"
    sources:
      - "src/api/*.py"
      - "src/models/*.py"
  
  "docs/installation.md":
    template: "install-template.md"
    sources:
      - "pyproject.toml"
      - "requirements.txt"
```

## Essential Configuration Options

**Template Directory**: Set `template_dir` to specify where your documentation templates are stored. If not specified, doc-evergreen will look for templates in common locations like `docs/templates/` or `.doc-evergreen/templates/`.

**Default Sources**: Use `default_sources` to define which files should be included as context for all documentation generation. This typically includes your main source code, configuration files, and key documentation. Glob patterns like `src/**/*.py` are supported.

**File-Specific Settings**: The `files` section lets you customize individual documentation files. Each file can have its own template and source files, overriding the defaults for that specific document.

## Excluding Files from Processing

Create a `.docignore` file in your project root to exclude files and directories from documentation generation:

```
# Exclude build artifacts and caches
.pytest_cache/
.ruff_cache/
.venv/
dist/
build/

# Exclude internal tooling
.doc-evergreen/working/
.beads/

# Exclude test files
**/test_*.py
TEST_*.md
```

The `.docignore` file uses the same syntax as `.gitignore`, supporting glob patterns and comments. This helps keep your documentation focused on relevant source code while avoiding temporary files and build artifacts.

## Configuration Basics

The `.doc-evergreen.yaml` file controls how doc-evergreen processes your documentation. Here are the most important configuration options you'll likely want to customize:

**File-specific settings** let you configure individual documentation files. Use the `files` section to specify which source files each documentation file should reference and which template to use:

```yaml
files:
  README.md:
    template: "readme_template.md"
    sources:
      - "src/main.py"
      - "src/config.py"
  docs/api.md:
    sources:
      - "src/api/"
```

**Default sources** apply to all documentation files unless overridden. This is useful when most of your docs reference the same core files:

```yaml
default_sources:
  - "src/"
  - "tests/"
```

**LLM configuration** controls which AI model generates your documentation. The default uses Claude 3.5 Sonnet, but you can specify different providers and models:

```yaml
llm:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"
```

**Template directory** tells doc-evergreen where to find your custom templates. If not specified, the tool will look for templates in the same directory as your documentation files:

```yaml
template_dir: "templates/"
```

## Controlling What Gets Documented

By default, doc-evergreen processes all files in your repository, but you often want to exclude certain directories and files from documentation generation. The tool provides several ways to control what gets documented, with the `.docignore` file being the primary method for filtering content.

### Using .docignore Files

Create a `.docignore` file in your project root to specify files and directories that should be excluded from documentation. This file uses gitignore-style syntax with glob patterns:

```
# Exclude internal tooling from doc generation
.beads/
.amplifier/
.doc-evergreen/
.pytest_cache/
.ruff_cache/
.venv/
./claude/

# Exclude test artifacts
.doc-evergreen/working/
TEST_*.md
```

Each line in the `.docignore` file represents a pattern to exclude. You can use comments (lines starting with `#`) to organize your exclusions. Common patterns include excluding virtual environments (`.venv/`), cache directories (`.pytest_cache/`, `.ruff_cache/`), build artifacts, and temporary files.

### Context Source Selection

In addition to excluding files, doc-evergreen uses a curated list of source files to provide context for documentation generation. The tool focuses on key files that typically contain the most relevant information about your project structure and purpose. You can see which files are prioritized by examining the `SOURCES` list in the context gathering module, which includes essential files like `README.md`, main package files, and configuration files like `pyproject.toml`.

# Next Steps

Congratulations! You've successfully set up doc-evergreen and generated your first documentation. Now you're ready to explore the full potential of AI-powered documentation that stays in sync with your code.

## Explore More Templates

You've likely started with a basic template, but doc-evergreen offers many specialized options. Try generating different types of documentation using the built-in templates:

- **API Documentation**: `doc-evergreen generate --template reference-api-docs` for comprehensive API reference
- **Contributing Guidelines**: `doc-evergreen generate --template howto-contributing-guide` to help onboard new contributors
- **Architecture Overviews**: `doc-evergreen generate --template explanation-architecture` for high-level system design docs
- **User Guides**: `doc-evergreen generate --template tutorial-user-guide` for step-by-step user instructions

Browse all available templates with `doc-evergreen list-templates` and experiment with different documentation types to see what works best for your project.

## Create Custom Templates

Once you're comfortable with the built-in templates, consider creating your own custom templates in the `.doc-evergreen/` directory. Start by copying an existing template that's similar to what you need, then modify the sections, prompts, and source files to match your specific requirements. Custom templates give you complete control over structure, tone, and content focus while still leveraging AI generation.

## Set Up Automated Workflows

Take your documentation to the next level by integrating doc-evergreen into your development workflow. Set up Git hooks to remind you to update docs when code changes, or create CI/CD workflows that generate documentation previews for pull requests. The `--preview` flag is particularly useful in automated contexts, allowing you to see what would change without actually modifying files.

## Advanced Features and Best Practices

Dive deeper into the [User Guide](docs/USER_GUIDE.md) to learn about advanced features like custom source file patterns, template inheritance, and optimization techniques for large codebases. Pay special attention to the Best Practices section, which covers strategies for writing effective prompts, organizing templates, and maintaining documentation quality over time. The Troubleshooting section will help you resolve common issues and understand how to debug template problems.

## Join the Community

Share your experience, ask questions, and contribute back to the project. Consider contributing new templates that others might find useful, reporting bugs you encounter, or suggesting improvements to existing functionality. Your feedback helps make doc-evergreen better for everyone, and contributing templates is a great way to give back to the community while showcasing your documentation expertise.