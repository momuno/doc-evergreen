# Doc-Evergreen 101: Quick Start Guide


# Introduction

*[Generated content for: Provide a clear, beginner-friendly introduction to doc-evergreen. Explain what it is, what problem i...]*


**Sources used:**

- `README.md`: Contains the project overview and fundamental workflow explanation that forms the conceptual foundation for beginners

- `docs/USER_GUIDE.md`: Provides the existing explanation of what doc-evergreen is and core concepts that can be adapted for beginners

# Prerequisites

*[Generated content for: List the system requirements and prerequisites needed before installing doc-evergreen. Include Pytho...]*


**Sources used:**

- `pyproject.toml`: Contains Python version requirement (>=3.11) and project metadata essential for installation prerequisites

- `docs/INSTALLATION.md`: Contains installation requirements and system setup information

# Installation

*[Generated content for: Provide step-by-step installation instructions for doc-evergreen. Focus on the quickest, most reliab...]*


**Sources used:**

- `docs/INSTALLATION.md`: Contains the quick install instructions and pipx recommendations for beginner-friendly setup

# Quick Start

*[Generated content for: Walk users through their first successful use of doc-evergreen from start to finish. This should be ...]*


**Sources used:**

- `tests/test_full_workflow_init_to_regen.py`: Demonstrates the complete workflow from initialization to regeneration, showing the practical steps users need

- `src/doc_evergreen/cli.py`: Contains the CLI commands and interface that users will interact with for their first experience

## Initialize Your Repository

*[Generated content for: Show how to run the init command to set up doc-evergreen in a repository. Explain what files are cre...]*


**Sources used:**

- `src/doc_evergreen/config.py`: Defines the configuration mechanism and .doc-evergreen.yaml file that gets created during initialization

## Understanding Templates

*[Generated content for: Explain what templates are and how they work in doc-evergreen. Show a simple example of a template s...]*


**Sources used:**

- `docs/TEMPLATES.md`: Explains how to create and use JSON templates, which is essential for users to understand the core feature

- `src/doc_evergreen/templates/tutorial-quickstart.json`: Provides a concrete example of template structure that demonstrates the JSON format and key fields

## Generate Your First Document

*[Generated content for: Walk through running the document generation command. Show the exact command to run and what output ...]*


**Sources used:**

- `src/doc_evergreen/cli.py`: Contains the CLI commands for document generation that users need to run

- `src/doc_evergreen/generate/doc_type.py`: Shows the available documentation types users can generate, which they'll need to specify in commands

# Customizing for Your Repository

*[Generated content for: Show users how to adapt doc-evergreen for their specific repository needs. Cover the essential confi...]*


**Sources used:**

- `src/doc_evergreen/config.py`: Defines the core configuration options that users need to understand for customizing doc-evergreen

- `.docignore`: Shows a practical example of how to exclude files and directories from documentation generation

## Configuration Basics

*[Generated content for: Explain the key configuration options in the .doc-evergreen.yaml file that users are most likely to ...]*


**Sources used:**

- `src/doc_evergreen/config.py`: Contains the FileConfig structure and configuration loading that defines what users can customize

## Controlling What Gets Documented

*[Generated content for: Show users how to include or exclude specific files and directories from documentation generation. E...]*


**Sources used:**

- `.docignore`: Provides a real-world example of excluding directories and files from documentation

- `src/doc_evergreen/context.py`: Shows what files doc-evergreen looks at by default, helping users understand what should be in their repository

# Next Steps

*[Generated content for: Guide users on what to do after completing this tutorial. Point them to additional resources, advanc...]*


**Sources used:**

- `docs/USER_GUIDE.md`: Contains information about advanced usage and workflows that users can explore after mastering the basics

- `src/doc_evergreen/templates/howto-contributing-guide.json`: Shows an example of other types of documentation users can generate once they're comfortable with the basics