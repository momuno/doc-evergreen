# Doc-Evergreen 101: Quick Start Guide


# Introduction

**doc-evergreen** is an AI-powered documentation generation tool that automatically transforms your repository code into up-to-date documentation. Instead of manually writing and maintaining docs that quickly become outdated, you define the structure once in a template, and doc-evergreen uses AI to generate the actual content by analyzing your source code.

The tool solves the critical problem of **documentation drift** - when code evolves but documentation doesn't, leading to confusion and wasted developer time. With doc-evergreen, keeping your docs fresh becomes effortless: just run a single command to regenerate documentation from your templates whenever your code changes.

By the end of this tutorial, you'll know how to create documentation templates, generate AI-powered content from your codebase, preview changes before applying them, and establish a workflow that keeps your documentation automatically synchronized with your code. You'll transform documentation from a maintenance burden into an automated asset that actually helps your team and users.

# Prerequisites

Before installing doc-evergreen, ensure your system meets the following requirements:

## System Requirements

- **Python 3.11 or higher** - doc-evergreen requires Python 3.11, 3.12, or 3.13
- **Git** - Required for cloning the repository and managing your documentation projects
- **pipx** (strongly recommended) - For isolated installation that avoids Python environment conflicts

## Required Setup

You'll need:

- **An Anthropic API key** - doc-evergreen uses Claude AI for content generation. You can obtain one from https://console.anthropic.com/
- **A code repository** - Have a project repository ready that you want to generate documentation for. This can be any codebase where you want to create or update documentation

## Environment Considerations

If you're on a modern Linux distribution (Debian, Ubuntu, etc.), note that these systems use externally-managed Python environments that prevent direct pip installations to the system Python. This is why pipx is the recommended installation method - it automatically handles virtual environment creation and isolation.

Verify your Python version before proceeding:
```bash
python3 --version  # Should show 3.11.x or higher
```

# Installation

The quickest and most reliable way to install doc-evergreen is using **pipx**, which automatically handles virtual environments and works seamlessly on all systems, including modern Linux distributions with externally-managed Python.

## Install with pipx (Recommended)

First, install pipx if you don't already have it:

```bash
# On most systems
pip install --user pipx

# On Debian/Ubuntu
apt install pipx
```

Then install doc-evergreen directly from the GitHub repository:

```bash
pipx install git+https://github.com/momuno/doc-evergreen.git
```

## Alternative: Install from Local Clone

If you prefer to clone the repository first:

```bash
git clone https://github.com/momuno/doc-evergreen.git
pipx install -e ./doc-evergreen
```

## Verify Installation

Confirm that doc-evergreen installed successfully by running:

```bash
doc-evergreen --help
```

You should see output similar to:

```
Usage: doc-evergreen [OPTIONS] COMMAND [ARGS]...

  doc-evergreen - AI-powered documentation generation.
  ...
```

If the command is not found, try restarting your terminal or running `pipx ensurepath` to add pipx binaries to your PATH.

## Configure Your API Key

Since you have your Anthropic API key ready from the prerequisites, set it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

To make this permanent, add it to your shell profile:

```bash
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

Verify the API key is configured correctly:

```bash
echo $ANTHROPIC_API_KEY
```

This should display your API key, confirming that doc-evergreen can access the Claude AI service for content generation.

# Quick Start

Now that you have doc-evergreen installed and configured, let's walk through creating your first documentation project. This example will take you from an empty directory to generated documentation in just a few commands.

## Initialize Your First Project

Navigate to any code repository or create a new project directory, then initialize doc-evergreen:

```bash
cd your-project-directory
doc-evergreen init --name "My Awesome Project"
```

This creates a `.doc-evergreen/` directory with a default README template. The template includes placeholders for common documentation sections like project overview, installation instructions, and usage examples. You can inspect the generated template at `.doc-evergreen/readme.json` to see how doc-evergreen structures documentation templates.

## Generate Your First Documentation

With the template in place, generate your README documentation:

```bash
doc-evergreen regen-doc readme --auto-approve
```

The `readme` argument refers to the template name (without the `.json` extension), and `--auto-approve` skips the confirmation prompt for a streamlined experience. Doc-evergreen will analyze your project files, understand the codebase structure, and generate contextually relevant documentation based on the template structure.

## Review and Iterate

Check the generated `README.md` file in your project root. The AI has created documentation tailored to your specific codebase, filling in project details, code examples, and usage instructions based on what it discovered in your files. If you want to refine the output, you can modify the template in `.doc-evergreen/readme.json` and run the regeneration command again - doc-evergreen is designed for iterative improvement of your documentation.

## Initialize Your Repository

Run the initialization command in your project directory to set up doc-evergreen:

```bash
doc-evergreen init
```

This command creates the essential configuration structure for your project. You'll see a new `.doc-evergreen.yaml` configuration file appear in your project root, which serves as the central configuration hub for all documentation generation settings.

The initialization process also establishes your project root directory. Doc-evergreen uses this location to understand your project structure and will automatically detect it in future commands by looking for either the `.doc-evergreen.yaml` file or a `.git` directory when searching up the directory tree.

After running the init command, you can customize your setup by editing the `.doc-evergreen.yaml` file. This configuration file allows you to specify template directories, define file-specific settings, set default source files for documentation generation, and configure LLM provider preferences. The file uses a simple YAML structure that's easy to modify as your documentation needs evolve.

Your project is now ready for template creation and documentation generation. The configuration file will guide doc-evergreen's behavior for all subsequent operations, ensuring consistent documentation generation across your entire project.

## Understanding Templates

Templates are the core building blocks of doc-evergreen's documentation generation system. A template is a JSON file that acts as a blueprint, defining exactly what documentation you want to create, how each section should be generated, and which source files provide the necessary context. Think of templates as recipes that tell doc-evergreen's AI what ingredients (your source files) to use and what cooking instructions (prompts) to follow for each part of your documentation.

The power of templates lies in their ability to make documentation generation repeatable and consistent. As your codebase evolves, you can regenerate documentation using the same template structure, ensuring that your docs stay current with your code changes while maintaining a consistent format and style across all sections.

Here's a simple template structure that demonstrates the key components:

```json
{
  "document": {
    "title": "API Reference Guide",
    "output": "docs/api-reference.md",
    "sections": [
      {
        "heading": "## Authentication",
        "prompt": "Explain how users authenticate with the API, including required headers and token format",
        "sources": ["src/auth.py", "README.md"]
      },
      {
        "heading": "## Endpoints",
        "prompt": "Document all available API endpoints with request/response examples",
        "sources": ["src/routes.py", "tests/test_api.py"]
      }
    ]
  }
}
```

Each template contains a document object with three essential elements: a human-readable title, an output path specifying where the generated documentation will be saved, and an array of sections that define the structure. Each section includes a heading that appears in the final document, a prompt that instructs the AI on what content to generate, and a sources array listing the files that provide context for that particular section. This modular approach allows you to mix and match different source files for different sections, ensuring each part of your documentation draws from the most relevant code and existing documentation.

## Generate Your First Document

Now that you have a template ready, let's generate your first document. The `generate` command is where doc-evergreen's AI capabilities come to life, transforming your template blueprint into actual documentation by analyzing your source files and following the prompts you've defined.

Run the following command from your project root directory:

```bash
doc-evergreen generate path/to/your-template.json
```

For example, if you saved your template as `templates/api-guide.json`, you would run:

```bash
doc-evergreen generate templates/api-guide.json
```

When you execute this command, you'll see output similar to this:

```
✓ API key loaded from /home/user/.claude/api_key.txt (45 chars)
📖 Generating documentation from template: templates/api-guide.json
📄 Output will be written to: docs/api-reference.md

🔄 Processing section 1/2: ## Authentication
   📁 Analyzing sources: src/auth.py, README.md
   ✅ Generated 247 words

🔄 Processing section 2/2: ## Endpoints  
   📁 Analyzing sources: src/routes.py, tests/test_api.py
   ✅ Generated 412 words

✅ Documentation generated successfully!
📍 View your documentation: docs/api-reference.md
```

The generation process works section by section, as indicated by the progress messages. For each section, doc-evergreen loads and analyzes the specified source files, sends the content along with your prompt to the AI model, and generates the documentation text. The tool provides real-time feedback showing which sources are being processed and how much content was generated for each section.

Once generation completes, you can find your new documentation at the output path specified in your template. Open the file in your preferred text editor or markdown viewer to see the results. The generated document will contain all your defined section headings with AI-generated content that draws from your source files, creating comprehensive documentation that reflects your actual codebase rather than generic examples.

# Customizing for Your Repository

Now that you've generated your first document, you'll likely want to customize doc-evergreen to work seamlessly with your specific repository structure and workflow. The tool provides flexible configuration options through a `.doc-evergreen.yaml` file that you can place in your project root.

Create a `.doc-evergreen.yaml` file in your repository's root directory to define project-wide settings. Here's a basic configuration that covers the most common customizations:

```yaml
# Directory containing your template files
template_dir: "docs/templates"

# Default source files to include for all sections (unless overridden)
default_sources:
  - "README.md"
  - "src/"

# LLM provider settings
llm:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"

# File-specific configurations
files:
  "docs/api-reference.md":
    template: "api-guide.json"
    sources: ["src/api/", "tests/test_api.py"]
  "docs/user-guide.md":
    template: "user-documentation.json"
    sources: ["README.md", "examples/"]
```

The `template_dir` setting tells doc-evergreen where to look for your template files, allowing you to organize them in a dedicated directory rather than specifying full paths each time. The `default_sources` array defines files and directories that should be analyzed for every documentation section unless explicitly overridden in a template, which is particularly useful for including foundational files like your README across multiple documents.

You can also control which files doc-evergreen analyzes by creating a `.docignore` file in your project root, similar to how `.gitignore` works. This file uses glob patterns to exclude directories and files that shouldn't be considered as documentation sources:

```
# Exclude build artifacts and dependencies
node_modules/
dist/
build/
.venv/

# Exclude internal tooling
.pytest_cache/
.ruff_cache/
.doc-evergreen/

# Exclude test artifacts
TEST_*.md
temp_*.py
```

The configuration system includes automatic project root detection, searching upward from your current directory for either a `.doc-evergreen.yaml` file or a `.git` directory. This means you can run doc-evergreen commands from any subdirectory within your project, and the tool will automatically find and apply your project-wide settings. If no configuration file is found, doc-evergreen falls back to sensible defaults, ensuring the tool works out of the box while still providing extensive customization options when needed.

## Configuration Basics

The `.doc-evergreen.yaml` configuration file provides several key settings that control how doc-evergreen processes your documentation. Understanding these core options will help you tailor the tool to your project's specific needs and structure.

The most fundamental configuration options are `template_dir` and `default_sources`. The `template_dir` setting specifies where doc-evergreen should look for your template files, allowing you to organize all templates in a dedicated directory like `docs/templates` or `config/doc-templates`. The `default_sources` array defines files and directories that should be analyzed for every documentation generation unless explicitly overridden in individual templates. This is particularly useful for including foundational files like your main README, core source directories, or important configuration files across all your documentation:

```yaml
template_dir: "docs/templates"
default_sources:
  - "README.md"
  - "src/"
  - "pyproject.toml"
```

The `llm` section controls which AI provider and model doc-evergreen uses for content generation. The default configuration uses Claude 3.5 Sonnet, but you can customize both the provider and specific model version. The `provider` field currently supports "claude" as the primary option, while the `model` field allows you to specify the exact model version you prefer for your documentation generation needs.

File-specific configurations through the `files` section provide the most granular control over your documentation generation. Each entry maps an output file path to its specific template and source files, overriding the default settings for that particular document. This allows you to create specialized documentation that draws from different parts of your codebase - for example, API documentation that focuses on your source code and tests, while user guides might emphasize examples and README content. These file-specific settings take precedence over the global defaults, giving you precise control over what content informs each piece of documentation.

## Controlling What Gets Documented

Doc-evergreen provides flexible filtering mechanisms to control exactly which files and directories are included in your documentation generation process. The primary method for excluding content is through a `.docignore` file placed in your project root, which works similarly to `.gitignore` by using glob patterns to specify what should be omitted from analysis.

The `.docignore` file supports both directory and file exclusions using standard glob syntax. Directory exclusions should end with a forward slash and will prevent doc-evergreen from scanning entire folder trees that contain build artifacts, dependencies, or internal tooling. For example, excluding `.venv/`, `.pytest_cache/`, and `.ruff_cache/` prevents the tool from analyzing virtual environments and cache directories that don't contribute meaningful content to documentation. File-level exclusions use glob patterns like `TEST_*.md` to filter out temporary files or test artifacts that shouldn't appear in your final documentation.

Comments in `.docignore` files help organize your exclusion rules and make them maintainable over time. You can group related exclusions together, such as separating build artifacts from test files, making it easier to understand and modify your filtering rules as your project evolves. The tool processes these patterns efficiently, scanning only the relevant parts of your project structure.

Beyond `.docignore`, doc-evergreen also supports programmatic source selection through configuration files and template-specific source lists. When you specify sources explicitly in your configuration or templates, the tool focuses only on those designated files and directories, effectively creating an inclusion-based approach rather than exclusion-based filtering. This dual approach gives you maximum flexibility - use `.docignore` for broad exclusions across your entire project, and use explicit source lists when you need precise control over what gets analyzed for specific documentation outputs.

# Next Steps

Congratulations! You've successfully set up doc-evergreen and generated your first AI-powered documentation. Now that you understand the basics of templates, configuration, and content control, you're ready to explore more advanced capabilities and integrate doc-evergreen into your development workflow.

## Explore Advanced Templates

Beyond the basic templates you've used, doc-evergreen includes specialized templates for different documentation needs. Try the `howto-contributing-guide` template to create comprehensive contributor documentation that automatically stays current with your development setup and testing procedures. Explore the API documentation templates if you're building libraries or services that need detailed interface documentation. Each template in the `.doc-evergreen/templates/` directory serves different use cases - experiment with the `reference`, `tutorial`, and `explanation` quadrants to find the best fit for your project's documentation strategy.

## Integrate with Your Development Workflow

Consider adding doc-evergreen to your continuous integration pipeline to catch documentation drift early. Many teams run `doc-evergreen generate --dry-run` in their CI checks to verify that documentation stays current with code changes. You can also set up pre-commit hooks to remind developers to update documentation when making significant changes. The preview functionality makes it safe to regenerate docs frequently - you'll always see exactly what changed before applying updates.

## Advanced Configuration and Customization

As your documentation needs grow more sophisticated, explore the advanced configuration options covered in the User Guide. Experiment with custom source file selections for different types of documentation, and consider creating project-specific templates that match your team's documentation standards. The file-specific configuration options allow you to fine-tune how different documents are generated, letting you create specialized documentation that draws from different parts of your codebase.

## Join the Community and Get Help

If you encounter challenges or want to share your doc-evergreen setup with others, check the project's GitHub repository for examples, issue discussions, and community contributions. The troubleshooting section in the User Guide covers common scenarios, while the examples directory provides real-world templates you can adapt for your projects. Consider contributing your own templates back to the community - your documentation patterns might help other developers facing similar challenges.