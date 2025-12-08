# Doc-Evergreen 101: Quick Start Guide


# Introduction

**doc-evergreen** is an AI-powered documentation generation tool that automatically keeps your documentation synchronized with your codebase. Instead of manually updating docs every time your code changes, you define the structure once in a template, and doc-evergreen uses AI to generate fresh, accurate content by analyzing your source code.

The tool solves the critical problem of **documentation drift** - when code evolves but documentation becomes outdated, leading to confusion and wasted developer time. With doc-evergreen, you can regenerate documentation with a single command, preview exactly what will change, and ensure your docs always reflect your current implementation.

By the end of this tutorial, you'll know how to create documentation templates, generate content from your source code, and establish a workflow that keeps your project documentation evergreen. You'll be able to turn any repository into a self-documenting codebase that maintains accuracy without manual maintenance overhead.

# Prerequisites

Before installing doc-evergreen, ensure your system meets the following requirements:

**Python Version**
- Python 3.11 or higher is required
- Supported versions: 3.11, 3.12, and 3.13

**Installation Tools**
- **pipx** (strongly recommended) - handles virtual environments automatically and works on all systems including those with externally-managed Python
- Alternatively, **pip** if working within a virtual environment

**API Access**
- An Anthropic API key for Claude AI integration (required for documentation generation)
- Active internet connection for AI API calls

**Project Repository**
- A code repository or project directory that you want to generate documentation for
- Source code files that doc-evergreen can analyze to create documentation content

**System Compatibility**
- Works on Linux, macOS, and Windows
- Note: Modern Linux distributions (Debian/Ubuntu) may block direct pip installations to system Python, making pipx the preferred installation method

# Installation

The quickest way to get doc-evergreen running is through **pipx**, which automatically handles virtual environments and works reliably across all operating systems, including modern Linux distributions that restrict system Python installations.

## Install with pipx (Recommended)

First, ensure pipx is available on your system:

```bash
# Install pipx if you don't have it
pip install --user pipx
# On Debian/Ubuntu, you can also use: apt install pipx
```

Then install doc-evergreen directly from the GitHub repository:

```bash
pipx install git+https://github.com/momuno/doc-evergreen.git
```

For development work or if you want to modify the tool, clone the repository first:

```bash
git clone https://github.com/momuno/doc-evergreen.git
pipx install -e ./doc-evergreen
```

## Alternative: Install with pip

If you're working within a virtual environment or have a system that allows direct pip installations, you can use:

```bash
pip install git+https://github.com/momuno/doc-evergreen.git
```

**Note:** Modern Linux systems typically block pip installations to system Python, so pipx remains the most reliable option.

## Verify Installation

Confirm that doc-evergreen installed correctly by running:

```bash
doc-evergreen --help
```

You should see the help output starting with:
```
Usage: doc-evergreen [OPTIONS] COMMAND [ARGS]...

  doc-evergreen - AI-powered documentation generation.
```

## Configure Your API Key

Before generating documentation, set up your Anthropic API key. The simplest approach for getting started is to export it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

Verify the key is properly configured:

```bash
echo $ANTHROPIC_API_KEY
```

For permanent setup, add the export command to your shell profile (`~/.bashrc` or `~/.zshrc`). Once your API key is configured, you're ready to start generating documentation from your codebase.

# Quick Start

Now that you have doc-evergreen installed and your API key configured, let's walk through creating your first documentation. This example will take you from an empty project to generated README content in just a few commands.

## Your First Documentation Generation

Start by navigating to any code project directory. For this example, we'll create a simple Python project:

```bash
mkdir my-project
cd my-project
echo "# Main application file" > main.py
```

Initialize doc-evergreen in your project directory:

```bash
doc-evergreen init --name "My Project"
```

This creates a `.doc-evergreen/` directory with a default README template. You'll see output confirming the initialization and the template file location.

Now generate your first documentation:

```bash
doc-evergreen regen-doc readme --auto-approve
```

The `--auto-approve` flag skips the confirmation prompt, making the process seamless. Doc-evergreen will analyze your project files, apply the template, and generate a complete README.md file tailored to your codebase.

## Understanding What Happened

The `init` command created a template configuration at `.doc-evergreen/readme.json` that defines the structure and content requirements for your README. The `regen-doc` command used this template along with your source code to generate contextually relevant documentation. You can inspect the generated README.md to see how doc-evergreen interpreted your project structure and created appropriate sections like installation instructions, usage examples, and feature descriptions based on your actual code.

To regenerate documentation after code changes, simply run the `regen-doc` command again. Doc-evergreen will detect changes in your codebase and update the documentation accordingly, ensuring it stays synchronized with your project's evolution.

## Initialize Your Repository

Navigate to your project directory and run the initialization command:

```bash
doc-evergreen init
```

This command sets up doc-evergreen in your repository by creating the necessary configuration structure. You'll see output confirming the initialization process and the location of created files.

## What Files Are Created

The init command creates a `.doc-evergreen/` directory in your project root containing:

- **Configuration file**: A `.doc-evergreen.yaml` file that stores your project settings, including template directories, file configurations, and LLM provider settings
- **Template directory**: A templates folder with starter templates for common documentation types like README files
- **Default settings**: Initial configuration using sensible defaults (Claude 3.5 Sonnet as the LLM provider, empty source file lists, and basic file mappings)

## Expected Output

After running the init command, your project structure will include:

```
your-project/
├── .doc-evergreen.yaml
├── .doc-evergreen/
│   └── templates/
│       └── readme.json
└── (your existing project files)
```

The `.doc-evergreen.yaml` file becomes the project root marker that doc-evergreen uses to locate your configuration. You can customize this file later to specify custom template directories, default source files to analyze, or different LLM settings. The initialization process ensures your repository is ready for documentation generation with minimal setup required.

## Understanding Templates

Templates are the core mechanism that drives doc-evergreen's documentation generation. A template is a JSON configuration file that acts as a blueprint, defining exactly what documentation sections to create, what content should go in each section, and which source files to analyze for context. Think of templates as recipes that tell doc-evergreen how to transform your codebase into structured, meaningful documentation.

The template system works by combining three key elements: structure definition (what sections your document needs), generation instructions (specific prompts that guide the AI in creating relevant content), and source mapping (which files contain the information needed for each section). When you run `regen-doc`, doc-evergreen reads the template, analyzes the specified source files, and uses AI to generate content that matches your template's requirements.

Here's a simple template structure that demonstrates the core concepts:

```json
{
  "document": {
    "title": "API Documentation",
    "output": "docs/api.md",
    "sections": [
      {
        "heading": "## Authentication",
        "prompt": "Explain how users authenticate with this API",
        "sources": ["src/auth.py", "README.md"]
      },
      {
        "heading": "## Endpoints",
        "prompt": "List and describe all available API endpoints",
        "sources": ["src/routes.py", "src/api.py"]
      }
    ]
  }
}
```

This template tells doc-evergreen to create an API documentation file with two sections. For each section, it specifies the heading that will appear in the final document, provides clear instructions about what content to generate, and identifies which source files contain relevant information. The beauty of this approach is that as your code evolves, running the same template will produce updated documentation that reflects your current codebase.

## Generate Your First Document

Now that you have doc-evergreen initialized in your project, let's generate your first piece of documentation. The generation process uses the `regen-doc` command, which reads a template file and produces documentation based on your current codebase.

To generate documentation, run the following command from your project root:

```bash
doc-evergreen regen-doc .doc-evergreen/templates/readme.json
```

This command tells doc-evergreen to process the readme template that was created during initialization. You'll see output similar to this:

```
✓ API key loaded from /home/user/.claude/api_key.txt (64 chars)
📖 Generating documentation from template: .doc-evergreen/templates/readme.json
📝 Output file: README.md
🔍 Processing section: ## Project Overview
🔍 Processing section: ## Installation
🔍 Processing section: ## Usage
✅ Documentation generated successfully!
```

The command processes each section defined in your template sequentially, using AI to analyze your source files and generate appropriate content. The entire process typically takes 30-60 seconds depending on your project size and the number of sections in your template.

Once generation completes, you'll find your new documentation file at the location specified in the template's output field. For the default readme template, this creates a `README.md` file in your project root. Open this file in your text editor or view it directly on GitHub to see the generated documentation. The content will be structured according to your template's sections and tailored to your specific codebase, providing an up-to-date overview of your project that reflects its current state.

# Customizing for Your Repository

Once you've generated your first documentation, you'll likely want to customize doc-evergreen to better fit your repository's specific needs. The configuration system provides flexible options to tailor the tool's behavior without requiring complex setup.

The primary way to customize doc-evergreen is through the `.doc-evergreen.yaml` configuration file in your project root. This file controls global settings that apply across all your documentation templates. Here's a basic configuration that demonstrates the key options:

```yaml
# Global template directory (optional)
template_dir: ".doc-evergreen/templates"

# Default source files to include in all templates
default_sources:
  - "README.md"
  - "src/"
  - "docs/architecture.md"

# LLM provider settings
llm:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"

# File-specific configurations
files:
  "docs/api.md":
    template: "api-template.json"
    sources:
      - "src/api/"
      - "src/routes.py"
  "CONTRIBUTING.md":
    sources:
      - ".github/"
      - "tests/"
```

The `default_sources` setting is particularly useful for establishing a baseline set of files that should be considered for all documentation generation. This saves you from repeatedly specifying common files like your README or main source directories in every template. File-specific configurations under the `files` section allow you to override these defaults or specify particular templates for certain output files, giving you fine-grained control over how different parts of your documentation are generated.

You can also control which files and directories doc-evergreen ignores by creating a `.docignore` file in your project root. This works similarly to `.gitignore`, using glob patterns to exclude files from documentation analysis. Common exclusions include build artifacts, cache directories, and internal tooling that shouldn't influence your documentation content. This helps keep the AI focused on relevant source code and prevents noise from temporary or generated files.

## Configuration Basics

The `.doc-evergreen.yaml` configuration file provides several key settings to customize how doc-evergreen processes your project. Understanding these options will help you tailor the tool's behavior to match your specific documentation needs.

The most commonly used configuration options include `template_dir` for specifying a custom location for your template files, and `default_sources` for defining which files and directories should be analyzed by default across all templates. For example, setting `default_sources: ["src/", "README.md", "docs/"]` ensures these locations are always considered when generating documentation, eliminating the need to specify them in each individual template.

The `llm` section controls which AI provider and model to use for content generation. The default configuration uses `provider: "claude"` with `model: "claude-3-5-sonnet-20241022"`, but you can adjust these settings based on your preferences or API access. The provider setting determines which AI service processes your code, while the model setting specifies the particular version or capability level to use.

File-specific configurations under the `files` section allow you to override global settings for particular documentation outputs. Each entry can specify a custom `template` file and `sources` list that will be used instead of the defaults. This is particularly useful when generating specialized documentation like API references or contributing guides that need to focus on specific parts of your codebase. For instance, you might configure `"docs/api.md"` to use only your `src/api/` directory as a source, ensuring the generated content stays focused on API-related code rather than your entire project.

## Controlling What Gets Documented

You can control which files and directories doc-evergreen includes in its analysis using several filtering mechanisms. The most common approach is creating a `.docignore` file in your project root, which works similarly to `.gitignore` by using glob patterns to exclude specific paths from documentation generation.

The `.docignore` file supports standard glob patterns and comments. For example, you can exclude entire directories like `.venv/` and `.pytest_cache/`, or use patterns like `TEST_*.md` to exclude files matching specific naming conventions. This is particularly useful for filtering out build artifacts, cache directories, virtual environments, and internal tooling that shouldn't influence your documentation content. Each line in the file represents a separate exclusion rule, and lines starting with `#` are treated as comments.

```
# Exclude development environments and caches
.venv/
.pytest_cache/
.ruff_cache/

# Exclude internal tooling
.beads/
.amplifier/

# Exclude test artifacts
TEST_*.md
```

In addition to the `.docignore` file, you can control file inclusion through the `sources` configuration in your templates and configuration files. When you specify sources in a template or the `default_sources` setting, doc-evergreen will only consider those specific files and directories, effectively creating an inclusion list rather than relying solely on exclusion patterns. This dual approach gives you flexibility to either broadly include content while excluding specific items, or to narrowly focus on particular parts of your codebase while ignoring everything else.

The filtering system processes exclusions before inclusions, so files matching `.docignore` patterns will be excluded even if they're explicitly listed in your sources configuration. This ensures that sensitive or irrelevant files remain excluded regardless of how your sources are configured, providing an additional layer of control over what content reaches the AI for documentation generation.

# Next Steps

Congratulations on completing your first doc-evergreen setup! You now have the foundation for maintaining synchronized documentation that evolves with your codebase. The real power of doc-evergreen becomes apparent as you continue developing your project and need to keep documentation current without manual overhead.

## Explore Advanced Features

Now that you're comfortable with basic generation, consider exploring some of doc-evergreen's more sophisticated capabilities. The **template library** includes specialized templates like `howto-contributing-guide` for developer onboarding, `reference-api` for technical specifications, and `tutorial-getting-started` for user guides. You can discover available templates using `doc-evergreen list-templates` and experiment with different documentation types that match your project's needs. Each template is designed for specific use cases and audiences, helping you create comprehensive documentation suites rather than just basic README files.

The **configuration system** offers extensive customization options beyond the basic setup. Try experimenting with file-specific configurations to generate different types of documentation from the same codebase, or explore different AI providers and models to find the combination that works best for your writing style and technical domain. The `.docignore` functionality becomes particularly valuable as your project grows, allowing you to fine-tune which parts of your codebase influence documentation generation.

## Integrate into Your Workflow

Consider integrating doc-evergreen into your development workflow for maximum benefit. Many teams run `doc-evergreen generate --preview` before major releases to ensure documentation reflects recent changes, or set up automated checks to remind developers when documentation might need updates. The preview functionality makes it safe to experiment with regeneration frequently, as you can always review changes before applying them.

## Additional Resources

For deeper understanding, explore the comprehensive [User Guide](docs/USER_GUIDE.md) which covers advanced usage patterns, troubleshooting common issues, and best practices from real-world implementations. The guide includes detailed examples of complex template configurations, workflow integration strategies, and tips for maintaining high-quality documentation at scale. As you encounter specific challenges or want to contribute improvements, the project's own documentation serves as an excellent example of doc-evergreen in action.