# Doc-Evergreen 101: Quick Start Guide


# Introduction

**doc-evergreen** is an AI-powered documentation generation tool that solves one of the most persistent challenges in software development: keeping documentation synchronized with your evolving codebase. As your code changes and grows, manually updating documentation becomes a time-consuming burden that often gets neglected, leading to outdated docs that confuse developers and waste valuable time.

This tool eliminates documentation drift by using a template-based approach combined with AI intelligence. You define the structure and sections of your documentation using simple template files, specify which source code files should inform each section, and doc-evergreen automatically generates clear, accurate content by analyzing your code with Claude AI. The result is documentation that can be regenerated whenever your code changes, ensuring it always reflects your current implementation.

By the end of this tutorial, you'll have doc-evergreen set up in your repository and understand how to create templates that automatically generate comprehensive documentation from your source code. You'll learn to define documentation sections, specify relevant source files, and use the regeneration workflow to keep your docs fresh with minimal manual effort. Whether you're documenting APIs, README files, or technical guides, you'll have a powerful system that makes documentation maintenance effortless rather than burdensome.

The tool is designed with developer productivity in mind, featuring a convention-based workflow, change previews before applying updates, and the ability to iteratively refine output until it meets your standards. You'll discover how this approach transforms documentation from a maintenance headache into an automated asset that enhances your project's accessibility and developer experience.

# Prerequisites

Before you can start using doc-evergreen, ensure your system meets the following technical requirements:

## Python Version

doc-evergreen requires **Python 3.11 or higher**. The tool is tested and supported on Python versions 3.11, 3.12, and 3.13. You can check your Python version by running:

```bash
python3 --version
```

If you need to upgrade Python, visit [python.org](https://python.org) for installation instructions specific to your operating system.

## System Dependencies

The core tool has minimal system dependencies beyond Python. However, you'll need:

- **Git** - Required for cloning the repository and version control operations
- **pipx** (strongly recommended) - For isolated installation and virtual environment management
- **Internet connection** - Required for AI API calls and initial installation

On Debian/Ubuntu systems, you can install pipx using your package manager:
```bash
apt install pipx
```

## Required API Access

doc-evergreen uses **Anthropic's Claude AI** for content generation, which requires:

- **Anthropic Console Account** - Sign up at [console.anthropic.com](https://console.anthropic.com/)
- **API Key** - Generate an API key from your Anthropic dashboard
- **API Credits** - Ensure your account has sufficient credits for AI requests

The API key must be configured as the `ANTHROPIC_API_KEY` environment variable before using the tool. Without this key, doc-evergreen cannot generate documentation content.

# Installation

## Recommended Installation Method

The preferred way to install doc-evergreen is using **pipx**, which automatically manages virtual environments and works reliably across all systems, including modern Linux distributions with externally-managed Python environments.

First, ensure pipx is installed on your system:

```bash
# Install pipx if you don't have it
pip install --user pipx
# On Debian/Ubuntu, you can also use: apt install pipx
```

Then install doc-evergreen directly from the GitHub repository:

```bash
pipx install git+https://github.com/momuno/doc-evergreen.git
```

For development work or if you want to modify the tool, you can install from a local clone:

```bash
git clone https://github.com/momuno/doc-evergreen.git
pipx install -e ./doc-evergreen
```

## Alternative Installation Methods

If you're working within an existing virtual environment or have specific requirements, you can use pip directly:

```bash
pip install git+https://github.com/momuno/doc-evergreen.git
```

**Note:** Modern Linux systems typically block pip installations to the system Python for security reasons. If you encounter externally-managed environment errors, use pipx instead.

## Verifying Your Installation

After installation completes, verify that doc-evergreen is properly installed and accessible:

```bash
doc-evergreen --help
```

You should see the help output displaying available commands and options:

```
Usage: doc-evergreen [OPTIONS] COMMAND [ARGS]...

  doc-evergreen - AI-powered documentation generation.
  ...
```

If the command is not found, ensure that pipx's binary directory is in your system PATH, or restart your terminal session to refresh environment variables.

# Quick Start

Now that you have doc-evergreen installed, let's walk through generating your first documentation. This example will create a complete README.md file for a sample project, showing you the full workflow from template creation to final output.

## Setting Up Your API Key

Before generating any documentation, you need to configure your Anthropic API key. Create the required directory and file:

```bash
mkdir -p ~/.claude
echo "your-api-key-here" > ~/.claude/api_key.txt
```

Replace `your-api-key-here` with your actual API key from the Anthropic Console. The tool will automatically load this key when needed.

## Creating Your First Template

Let's create a simple but complete documentation template. First, create the `.doc-evergreen` directory in your project:

```bash
mkdir -p .doc-evergreen
```

Now create a template file at `.doc-evergreen/readme.json`:

```json
{
  "meta": {
    "name": "Project README",
    "description": "Main project documentation",
    "output_path": "README.md"
  },
  "sections": [
    {
      "id": "overview",
      "title": "Project Overview",
      "prompt": "Analyze the codebase and write a clear project overview. Include what the project does, its main purpose, and key features. Base this on the actual code structure and functionality you can observe.",
      "sources": ["src/", "*.py", "package.json", "pyproject.toml"]
    },
    {
      "id": "installation",
      "title": "Installation",
      "prompt": "Create installation instructions based on the project's dependency files and setup configuration. Include any prerequisites and step-by-step installation commands.",
      "sources": ["requirements.txt", "pyproject.toml", "setup.py", "package.json"]
    },
    {
      "id": "usage",
      "title": "Usage",
      "prompt": "Provide practical usage examples by analyzing the main entry points, CLI interfaces, or API endpoints in the code. Show concrete examples that users can run.",
      "sources": ["src/", "examples/", "*.py"]
    }
  ]
}
```

## Generating Your Documentation

With your template in place, generate the documentation:

```bash
doc-evergreen generate .doc-evergreen/readme.json
```

You'll see real-time progress as each section is generated:

```
✓ API key loaded from /home/user/.claude/api_key.txt (45 chars)
📄 Generating documentation from template: .doc-evergreen/readme.json
🎯 Output will be written to: README.md

🔄 Generating section: Project Overview
✅ Section 'overview' completed (1,247 characters)

🔄 Generating section: Installation  
✅ Section 'installation' completed (892 characters)

🔄 Generating section: Usage
✅ Section 'usage' completed (1,456 characters)

📝 Documentation generated successfully!
💾 Written to: README.md
```

## Reviewing and Iterating

Open the generated `README.md` file to review the content. If you want to refine any section, simply run the generate command again - it will regenerate all sections with fresh AI analysis of your current codebase.

For more targeted updates, you can modify the prompts in your template to be more specific about what you want, then regenerate. The tool will detect that your template has changed and update the documentation accordingly.

This basic workflow - create template, generate, review, iterate - forms the foundation of using doc-evergreen effectively. You can expand this approach to create multiple templates for different types of documentation as your project grows.

## Understanding Templates

Templates are the heart of doc-evergreen - they're JSON files that define what documentation to generate, how to generate it, and where to save it. Think of a template as a blueprint that tells the AI exactly what sections to create, what questions to answer in each section, and which source files to analyze for context. This approach ensures your documentation stays consistent and comprehensive as your codebase evolves.

The power of templates lies in their reusability and precision. Instead of manually writing documentation or giving vague instructions to an AI, templates provide structured prompts that produce reliable results. Each template specifies the exact sections you want (like "Installation," "API Reference," or "Contributing Guidelines"), includes tailored prompts for each section, and points to relevant source files that contain the information needed.

## Viewing Available Templates

Doc-evergreen comes with several built-in templates designed for common documentation needs. To see what's available, use the list command:

```bash
doc-evergreen list-templates
```

This shows all available templates with their descriptions and intended use cases. For example, you might see templates like `tutorial-quickstart` for creating brief getting-started guides, `api-reference` for comprehensive API documentation, or `contributing-guide` for project contribution guidelines.

You can also examine any template in detail to understand its structure:

```bash
doc-evergreen show-template tutorial-quickstart
```

This displays the complete template JSON, showing you exactly what sections it creates and what prompts it uses.

## Choosing the Right Template

Select templates based on your documentation goals and audience needs. The built-in `tutorial-quickstart` template works well when you need a brief, beginner-friendly guide that gets users productive in 5 minutes. It creates sections focused on immediate value: what the project does, essential prerequisites, one-command installation, and a simple first example.

For more comprehensive documentation, you might choose templates that include additional sections like detailed configuration options, troubleshooting guides, or advanced usage patterns. Consider your project's complexity, your users' technical level, and how much detail they need to be successful.

You can also use templates as starting points for customization. Copy a built-in template to your `.doc-evergreen` directory and modify the sections, prompts, or source file references to match your specific needs. This approach gives you the benefit of proven template structures while allowing complete customization for your project's unique requirements.

## Setting Up Your Repository

To use doc-evergreen with your own repository, you'll need to create a configuration file that tells the tool which files to analyze and how to generate your documentation. The configuration file uses YAML format and should be named `.doc-evergreen.yaml` in your project's root directory.

Create your configuration file by adding a `.doc-evergreen.yaml` file to your repository root. Here's a basic configuration structure:

```yaml
# Optional: Custom template directory
template_dir: "docs/templates"

# Default source files to analyze for all documentation
default_sources:
  - "src/**/*.py"
  - "README.md"
  - "pyproject.toml"

# LLM provider settings
llm:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"

# File-specific configurations
files:
  "docs/quickstart.md":
    template: "tutorial-quickstart"
    sources:
      - "src/main.py"
      - "examples/basic_usage.py"
  "docs/api.md":
    template: "api-reference"
    sources:
      - "src/**/*.py"
```

Doc-evergreen automatically discovers your project root by looking for either a `.doc-evergreen.yaml` file or a `.git` directory, then searches upward through parent directories until it finds one. This means you can run doc-evergreen commands from anywhere within your project structure, and it will find the correct configuration.

You can also create a `.docignore` file to exclude certain files and directories from analysis, similar to how `.gitignore` works. This is particularly useful for excluding build artifacts, virtual environments, or internal tooling that shouldn't influence your documentation. Common exclusions include `.venv/`, `__pycache__/`, `.pytest_cache/`, and any temporary or generated files that don't represent your actual project structure.

## Generating Your First Document

Now that your repository is configured, let's generate your first piece of documentation. This example assumes you have a Python project with source files and want to create a quick-start guide.

Run the following command from your project root directory:

```bash
doc-evergreen generate docs/quickstart.md --template tutorial-quickstart
```

Doc-evergreen will analyze your source files and generate documentation section by section. You'll see output similar to this:

```
✓ API key loaded from /home/user/.claude/api_key.txt (64 chars)
✓ Template 'tutorial-quickstart' loaded successfully
✓ Validating source files...
✓ Found 12 source files to analyze
✓ Generating section: Introduction (1/4)
✓ Generating section: Installation (2/4)  
✓ Generating section: Quick Start (3/4)
✓ Generating section: Next Steps (4/4)
✓ Documentation generated: docs/quickstart.md
```

The generation process typically takes 30-60 seconds depending on your project size and complexity. Doc-evergreen processes each section sequentially, building context from your source files to create coherent, accurate documentation that reflects your actual codebase.

To verify the generation was successful, check that your output file exists and contains the expected sections:

```bash
ls -la docs/quickstart.md
head -20 docs/quickstart.md
```

You should see a well-structured markdown file with sections like "What is [Your Project]", "Installation", "Your First Example", and "What's Next". The content will be tailored to your specific project based on the source files doc-evergreen analyzed. If you need to regenerate or update the documentation later, simply run the same command again - doc-evergreen will detect any changes in your source files and update the documentation accordingly.

# Understanding the Output

When you run doc-evergreen, it produces structured markdown documentation along with detailed analysis files that help you understand how the tool made its decisions. The primary output is your requested documentation file (e.g., `docs/quickstart.md`), but doc-evergreen also generates a `.doc-evergreen/` directory containing analysis metadata and relevance scoring information.

## What Gets Generated

Doc-evergreen creates documentation based on the **Diataxis framework**, which categorizes documentation into four distinct types: **tutorial** (learning-oriented), **howto** (goal-oriented), **reference** (information-oriented), and **explanation** (understanding-oriented). When you specify a documentation type, the tool tailors both its content analysis and output structure to match that category's specific purpose and audience needs.

The generated documentation includes sections that are dynamically determined based on your project's structure and the documentation type you've requested. For example, a tutorial might include "Getting Started," "Your First Example," and "Next Steps" sections, while a reference document would focus on API descriptions, parameter lists, and technical specifications. Each section is populated with content extracted and synthesized from your actual source files, ensuring the documentation accurately reflects your current codebase.

## Understanding File Selection

Doc-evergreen uses an intelligent relevance analyzer to determine which files from your project should influence the documentation generation. The tool examines each file and assigns it a relevance score from 0-100 based on factors like file type, content preview, naming patterns, and how well the file aligns with your specified documentation purpose. Only files that meet a relevance threshold are included in the final analysis, which helps focus the documentation on the most important parts of your codebase.

You can review these decisions by examining the analysis files in the `.doc-evergreen/` directory after generation. These files contain detailed reasoning for why each file was included or excluded, along with the specific content excerpts that influenced the documentation. This transparency allows you to understand the tool's decision-making process and adjust your source files or configuration if certain important files are being overlooked or irrelevant files are being included.

# Next Steps

Now that you've successfully generated your first documentation, you're ready to explore doc-evergreen's more powerful capabilities. The basic workflow you just completed—running a single command to generate documentation—is just the beginning. Doc-evergreen offers a rich ecosystem of templates, advanced configuration options, and workflow integrations that can transform how your team approaches documentation maintenance.

## Exploring Advanced Templates

Doc-evergreen includes over a dozen specialized templates beyond the basic quickstart guide you just created. Each template is designed for specific documentation needs and follows the Diataxis framework. Try generating a **Contributing Guide** with `doc-evergreen generate howto-contributing-guide` to create comprehensive contributor documentation, or use `doc-evergreen generate reference-api` to build detailed API reference documentation. You can also create **explanation-architecture** documents to describe your system's design decisions, or **tutorial-advanced** guides for complex workflows. Each template analyzes different aspects of your codebase and produces documentation tailored to its specific purpose and audience.

## Creating Custom Templates

Once you're comfortable with the built-in templates, you can create your own custom templates in the `.doc-evergreen/` directory. Custom templates give you complete control over documentation structure, content focus, and output format. Start by examining the JSON structure of existing templates in `src/doc_evergreen/templates/`, then create your own template file following the same pattern. You can specify exactly which source files to analyze, define custom section headings and prompts, and even create templates for specialized documentation like deployment guides, troubleshooting manuals, or team onboarding documents.

## Workflow Integration and Automation

To maximize doc-evergreen's value, consider integrating it into your development workflow. Set up GitHub Actions or other CI/CD pipelines to automatically regenerate documentation when code changes, ensuring your docs never fall behind your implementation. You can also use the preview and iteration features to refine documentation through multiple passes—run generation, review the output, adjust your source code comments or template configuration, then regenerate until the documentation meets your standards. The tool's ability to show exactly what changed between generations makes this iterative process both efficient and transparent.

## Learning Resources and Community

For deeper mastery of doc-evergreen, explore the comprehensive examples in the `docs/` directory and study the **Advanced Usage** section of the User Guide. The tool's convention-based approach means you can learn from other projects using doc-evergreen by examining their `.doc-evergreen/` directories. As you become more proficient, consider contributing your own templates back to the project or sharing documentation patterns that work well for your team's specific needs and project types.