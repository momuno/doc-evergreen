# Doc-Evergreen Quick Start Guide


# What You'll Accomplish

By the end of this guide, you'll have doc-evergreen installed and running in your project, with your first documentation template generating content automatically from your source code. doc-evergreen is an AI-powered tool that eliminates documentation drift by using templates to define structure and Claude AI to generate accurate, up-to-date content from your codebase.

This quick start will walk you through the essential workflow: setting up the convention-based `.doc-evergreen/` directory, creating your first template that specifies which code files to analyze, and using the `regen-doc` command to generate documentation with a preview-and-approve process. You'll learn how to define documentation sections with targeted prompts, specify source files using glob patterns, and regenerate content whenever your code evolves.

Rather than wrestling with outdated documentation that becomes a maintenance burden, you'll establish a system where keeping docs fresh is as simple as running a single command. Whether you're generating README files, API documentation, or technical guides, you'll have a powerful foundation for maintaining synchronized documentation that actually helps developers instead of confusing them.
show-template
# Prerequisites

Before you can install and use doc-evergreen, ensure your system meets the following requirements:

## Python Version

**Python 3.11 or higher** is required. doc-evergreen supports Python 3.11, 3.12, and 3.13. Check your Python version:

```bash
python3 --version
```

If you need to upgrade Python, visit [python.org](https://python.org/downloads/) or use your system's package manager.

## System Dependencies

**pipx (Strongly Recommended)**: While not strictly required, pipx is the recommended installation method as it handles virtual environments automatically and works on all systems, including those with externally-managed Python environments like modern Debian/Ubuntu systems.

```bash
# Install pipx if you don't have it
pip install --user pipx
# or on Debian/Ubuntu:
apt install pipx
```

## API Access

**Anthropic API Key**: doc-evergreen uses Anthropic's Claude AI for content generation, so you'll need an active Anthropic account and API key. You can obtain one from the [Anthropic Console](https://console.anthropic.com/) after creating an account.

# Installation

## Using pipx (Recommended)

**pipx is STRONGLY recommended** - it handles virtual environments automatically and works on all systems including those with externally-managed Python (Debian/Ubuntu).

```bash
# Install doc-evergreen
pipx install git+https://github.com/momuno/doc-evergreen.git

# Or from local clone:
git clone https://github.com/momuno/doc-evergreen.git
pipx install -e ./doc-evergreen
```

## Using pip (Alternative Method)

⚠️ **Modern Linux systems block pip install to system Python.** Use pipx instead.

If you're in a virtual environment or sure you want to proceed:

```bash
pip install git+https://github.com/momuno/doc-evergreen.git
```

## Development Installation

For contributing to doc-evergreen:

```bash
git clone https://github.com/momuno/doc-evergreen.git
cd doc-evergreen

# Use pipx (recommended)
pipx install -e .

# Or create dedicated venv
python3 -m venv ~/.venvs/doc-evergreen
~/.venvs/doc-evergreen/bin/pip install -e .
```

## Verify Installation

Confirm that doc-evergreen installed successfully:

```bash
doc-evergreen --help
```

You should see the help output starting with:
```
Usage: doc-evergreen [OPTIONS] COMMAND [ARGS]...

  doc-evergreen - AI-powered documentation generation.
```

If the command is not found, ensure that pipx's bin directory is in your PATH, or restart your terminal session.

# Basic Usage

## Setup API Key

Before generating documentation, you need to configure your Anthropic API key. doc-evergreen looks for your API key in a specific location:

```bash
# Create the directory
mkdir -p ~/.claude

# Add your API key to the file
echo "your-api-key-here" > ~/.claude/api_key.txt
```

The API key file supports both plain key format and key=value format. doc-evergreen will automatically load this key when running commands that require AI generation.

## Essential Commands

The most common workflow involves three core commands:

```bash
# Initialize a new template in your project
doc-evergreen init

# Generate documentation from your template
doc-evergreen generate .doc-evergreen/readme.json

# Preview changes before applying them
doc-evergreen generate .doc-evergreen/readme.json --preview
```

## Quick Start Workflow

Here's the typical process to get documentation generated for your project:

1. **Navigate to your project directory** and initialize a template:
   ```bash
   cd your-project
   doc-evergreen init
   ```

2. **Edit the generated template** in `.doc-evergreen/readme.json` to define your documentation structure and specify which source files to analyze.

3. **Generate your documentation**:
   ```bash
   doc-evergreen generate .doc-evergreen/readme.json
   ```

4. **Review the output** in your specified output file (typically `README.md` or `docs/api.md`). If you want to see what would change before writing files, use the `--preview` flag to see a diff of proposed changes.

The `generate` command will analyze your source files, send the relevant code context to Claude AI along with your section prompts, and produce documentation that reflects your current codebase. As your code evolves, simply re-run the generate command to keep your documentation synchronized.

## Essential Commands

Based on the CLI source code, here are the core commands you'll use regularly:

### Core Commands

**`doc-evergreen init`** - Creates a new documentation template in your project's `.doc-evergreen/` directory. This interactive command sets up the basic structure for your documentation generation, including section definitions and source file specifications.

```bash
doc-evergreen init
```

**`doc-evergreen generate <template>`** - Generates documentation using the specified template file. This is the primary command for creating or updating your documentation based on your current codebase.

```bash
doc-evergreen generate .doc-evergreen/readme.json
doc-evergreen generate .doc-evergreen/readme.json --preview  # See changes without writing
```

**`doc-evergreen validate <template>`** - Validates your template file structure and configuration without generating documentation. Useful for catching template syntax errors before running generation.

```bash
doc-evergreen validate .doc-evergreen/readme.json
```

**`doc-evergreen detect-changes <template>`** - Analyzes your source files to identify what has changed since the last documentation generation. Helps you understand which sections might need updates.

```bash
doc-evergreen detect-changes .doc-evergreen/readme.json
```

### Command Options

Most commands support common options like `--help` for detailed usage information. The `generate` command specifically supports `--preview` to show a diff of proposed changes without modifying files, and `--verbose` for detailed logging during the generation process.

## Configuration

doc-evergreen uses a simple YAML configuration file to customize its behavior. While the tool works with sensible defaults out of the box, you can create a `.doc-evergreen.yaml` file in your project root to override specific settings.

The minimal configuration requires no file at all - doc-evergreen will automatically detect your project structure and use Claude 3.5 Sonnet as the default AI model. However, if you want to customize the experience, create a `.doc-evergreen.yaml` file in your project root:

```yaml
# Optional: Specify a custom directory for templates
template_dir: ".doc-evergreen"

# Optional: Set default source files for all templates
default_sources:
  - "src/**/*.py"
  - "lib/**/*.js"

# Optional: Configure LLM settings
llm:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"

# Optional: Per-file configurations
files:
  "README.md":
    template: "readme.json"
    sources:
      - "src/main.py"
      - "docs/examples/"
```

The configuration system is designed to be forgiving - if your `.doc-evergreen.yaml` file is missing or contains errors, the tool will log a warning and continue with default settings. This ensures that doc-evergreen remains functional even in projects without explicit configuration, making it easy to get started quickly and add customization only when needed.

# Working with Templates

Templates are JSON files that define the structure, content, and generation instructions for your documentation. They act as blueprints that tell doc-evergreen what sections to create, which source files to analyze, and how to generate each part of your documentation. This template-based approach ensures consistent documentation that can be regenerated as your codebase evolves.

## Template Structure

Every template follows a standard JSON structure with three main components: document metadata, section definitions, and source file specifications. Here's the basic format:

```json
{
  "document": {
    "title": "API Reference Guide",
    "output": "docs/api-reference.md",
    "sections": [
      {
        "heading": "Authentication",
        "prompt": "Explain how to authenticate API requests with examples",
        "sources": ["src/auth.py", "docs/examples/auth.md"]
      },
      {
        "heading": "Endpoints",
        "prompt": "Document all available API endpoints with parameters",
        "sources": ["src/api/routes.py", "src/api/models.py"]
      }
    ]
  }
}
```

The `document` object contains the overall document configuration, while each section in the `sections` array defines a specific part of your documentation. The `heading` becomes the section title, the `prompt` instructs the AI on what to generate, and `sources` specifies which files provide context for that section.

## Writing Effective Prompts

The `prompt` field in each section is crucial for generating high-quality documentation. Write prompts that are specific and actionable rather than generic. Instead of "Document this code," use prompts like "Provide step-by-step installation instructions including prerequisites and troubleshooting common issues" or "Explain the authentication flow with code examples showing both successful and error responses."

Good prompts specify the audience, format, and level of detail needed. For example: "Create a beginner-friendly tutorial showing how to set up the development environment, including screenshots and expected output at each step." This gives the AI clear guidance on tone, content type, and what to include.

## Nested Sections and Organization

Templates support nested sections for complex documentation structures. Add a `sections` array within any section to create subsections:

```json
{
  "heading": "API Reference",
  "prompt": "Overview of the API structure and conventions",
  "sources": ["src/api/"],
  "sections": [
    {
      "heading": "User Endpoints",
      "prompt": "Document user management endpoints",
      "sources": ["src/api/users.py"]
    },
    {
      "heading": "Data Endpoints", 
      "prompt": "Document data retrieval and manipulation endpoints",
      "sources": ["src/api/data.py"]
    }
  ]
}
```

This hierarchical structure helps organize large documents and allows you to provide specific context and instructions for each subsection while maintaining the overall document flow.

## Using Built-in Templates

doc-evergreen comes with several built-in templates that you can use immediately or customize for your needs. These templates cover common documentation scenarios and serve as excellent starting points for your own documentation projects.

To see all available built-in templates, use the `list-templates` command:

```bash
doc-evergreen list-templates
```

This displays each template's name, title, and description, helping you identify which template best fits your documentation needs. The built-in templates include options for API documentation, user guides, technical specifications, and other common documentation types.

Once you've identified a template you want to use, you can apply it directly to your project or copy it for customization. To use a built-in template directly, reference it by name in the generate command:

```bash
doc-evergreen generate --template api-reference
```

If you want to customize a built-in template, copy it to your project first and then modify it:

```bash
doc-evergreen copy-template api-reference my-custom-api-docs.json
```

This creates a local copy of the template that you can edit to match your specific requirements. The copied template includes all the original structure, prompts, and source specifications, which you can then adapt to your codebase and documentation style. Built-in templates are designed to work with common project structures, but copying them allows you to fine-tune the prompts, adjust the sections, and specify your exact source files.

## Document Types

doc-evergreen supports the four document types defined by the [Diataxis framework](https://diataxis.fr/), which categorizes documentation based on user needs and learning contexts. Each type serves a distinct purpose and requires different approaches to content creation.

**Tutorial** documents are learning-oriented and designed to guide newcomers through their first successful experience with your project. These step-by-step guides focus on building confidence and getting users to a working state quickly. **How-to** documents are goal-oriented and help users solve specific problems or accomplish particular tasks. They assume some familiarity with the system and provide direct, practical solutions.

**Reference** documents are information-oriented and provide comprehensive technical descriptions of APIs, functions, classes, and other system components. They serve as authoritative sources of truth about what the system does and how it behaves. **Explanation** documents are understanding-oriented and focus on clarifying concepts, design decisions, and the "why" behind your system's architecture and behavior.

When generating documentation, you can specify the document type to ensure the AI creates content appropriate for your intended audience and use case. For example, a tutorial will include more context and explanation for beginners, while a reference document will focus on precise technical details and complete coverage of functionality. This framework helps ensure your documentation serves users effectively across different stages of their journey with your project.

# Your First Documentation

Let's walk through creating your first documentation with doc-evergreen using a complete, real-world example. This tutorial will show you exactly what commands to run and what output to expect at each step.

## Setting Up the Example

For this walkthrough, we'll create documentation for a Python project with the following structure:

```
my-project/
├── README.md
├── pyproject.toml
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── main.py
└── docs/
    └── api.md
```

First, let's create a template that will generate a comprehensive README for our project. Create the `.doc-evergreen/` directory and your first template:

```bash
mkdir .doc-evergreen
```

Create `.doc-evergreen/readme.json` with this content:

```json
{
  "title": "Project README",
  "description": "Main project documentation",
  "output_file": "README.md",
  "document_type": "explanation",
  "sections": [
    {
      "name": "overview",
      "title": "Overview",
      "prompt": "Provide a clear project overview including purpose and key features"
    },
    {
      "name": "installation",
      "title": "Installation", 
      "prompt": "Generate installation instructions based on the pyproject.toml configuration"
    },
    {
      "name": "usage",
      "title": "Usage",
      "prompt": "Create usage examples based on the main module and any example code found"
    }
  ],
  "sources": [
    "pyproject.toml",
    "src/myapp/__init__.py", 
    "src/myapp/main.py",
    "docs/api.md"
  ]
}
```

## Generating Your First Documentation

Now let's generate the documentation. Run the generate command:

```bash
doc-evergreen generate readme
```

You'll see output like this:

```
🔍 Gathering context from source files...
✓ Found pyproject.toml
✓ Found src/myapp/__init__.py  
✓ Found src/myapp/main.py
⚠ docs/api.md not found, skipping

🤖 Generating documentation...
📝 Section: Overview [1/3]
📝 Section: Installation [2/3] 
📝 Section: Usage [3/3]

✅ Documentation generated successfully!
📄 Output saved to: README.md

Preview changes with: doc-evergreen diff readme
```

## Previewing the Results

Before the new content overwrites your existing README, preview what changed:

```bash
doc-evergreen diff readme
```

This shows a detailed diff of what will be added, removed, or modified:

```diff
--- README.md (current)
+++ README.md (generated)
@@ -1,3 +1,25 @@
-# My Project
-
-A simple example project.
+# My Project
+
+## Overview
+
+My Project is a Python application designed to demonstrate modern project structure
+and documentation practices. The project features a clean modular architecture with
+comprehensive tooling for development and deployment.
+
+## Installation
+
+Install the project using pip:
+
+```bash
+pip install my-project
+```
+
+For development installation:
+
+```bash
+pip install -e .
+```
```

## Applying the Changes

If you're satisfied with the generated content, apply it:

```bash
doc-evergreen apply readme
```

The output confirms the update:

```
✅ Applied changes to README.md
📊 Stats: 15 lines added, 2 lines removed
```

Your README.md now contains the AI-generated documentation based on your actual source code. The generated content reflects the real structure and dependencies found in your `pyproject.toml` and source files, ensuring accuracy and relevance to your specific project.

# Verification

After generating documentation, it's important to verify that doc-evergreen is working correctly and producing the expected results.

## Checking Successful Generation

When doc-evergreen runs successfully, you'll see clear progress indicators and confirmation messages:

```
🔍 Gathering context from source files...
✓ Found pyproject.toml
✓ Found src/myapp/__init__.py  
✓ Found src/myapp/main.py

🤖 Generating documentation...
📝 Section: Overview [1/3]
📝 Section: Installation [2/3] 
📝 Section: Usage [3/3]

✅ Documentation generated successfully!
📄 Output saved to: README.md
```

The checkmarks (✓) indicate successful file discovery, while the progress counter shows each section being processed. A final success message confirms the output file location.

## Validating Generated Content

To verify the quality of generated documentation, check that:

- **Content is relevant**: Generated text should reference actual files, dependencies, and code structure from your project
- **Code examples work**: Any generated commands or code snippets should be executable and accurate
- **Structure is logical**: Sections should flow naturally and follow the document type conventions
- **Sources are reflected**: Content should incorporate information from the specified source files

Use the `diff` command to review changes before applying them, ensuring the AI understood your codebase correctly.

## Common Issues and Solutions

**Template not found errors**: Verify your template file is in `.doc-evergreen/` with a `.json` extension and valid JSON syntax. Check the template name matches what you're passing to the generate command.

**Missing source files**: The tool will skip files that don't exist with a warning (⚠). Update your template's `sources` array to remove non-existent files or create the missing files.

**Empty or poor quality output**: This usually indicates insufficient context in source files or overly broad prompts. Add more detailed comments to your code, include example files, or refine your section prompts to be more specific about what you want generated.

**API rate limiting**: If generation fails with API errors, wait a few moments and retry. Consider breaking large templates into smaller ones to reduce the load per request.

# Next Steps

Now that you've successfully generated your first documentation, here are several paths to explore more advanced capabilities and customize doc-evergreen for your specific needs.

## Advanced Features

Explore the **Advanced Usage** section in the [User Guide](docs/USER_GUIDE.md) to discover powerful features like conditional content generation, multi-file templates, and custom AI prompts. Learn how to create sophisticated documentation workflows that adapt to different project types and team requirements.

The **Workflows** section demonstrates how to integrate doc-evergreen into CI/CD pipelines, set up automated documentation updates, and establish review processes for AI-generated content. These patterns help teams maintain consistent, up-to-date documentation at scale.

## Customization and Templates

Dive deeper into template creation by studying the **Examples** section, which showcases real-world templates for API documentation, user guides, and technical specifications. Each example includes detailed explanations of prompt engineering techniques and source file selection strategies.

For teams with specific documentation standards, the **Best Practices** section covers template organization, naming conventions, and collaborative workflows. Learn how to create reusable template libraries and establish documentation governance across multiple projects.

## Community and Support

Join the growing community of doc-evergreen users to share templates, discuss advanced use cases, and get help with complex documentation challenges. The **Troubleshooting** section provides solutions to common issues, while the project's issue tracker offers direct support for technical problems and feature requests.