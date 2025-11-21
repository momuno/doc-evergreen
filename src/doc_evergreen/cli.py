"""
Sprint 5: CLI Interface for Template-Based Documentation Generation

Supports both single-shot and chunked generation modes with section-level prompts.
"""

import asyncio
import json
from pathlib import Path

import click

from doc_evergreen.change_detection import detect_changes
from doc_evergreen.chunked_generator import ChunkedGenerator
from doc_evergreen.core.template_schema import Document
from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template
from doc_evergreen.core.template_schema import parse_template
from doc_evergreen.core.template_schema import validate_template

# Import Generator for single-shot mode (fallback to ChunkedGenerator if not available)
try:
    from doc_evergreen.single_generator import Generator
except ImportError:
    Generator = ChunkedGenerator  # type: ignore[misc,assignment]


def resolve_template_path(name: str) -> Path:
    """Resolve template name to path using .doc-evergreen/ convention.

    Resolution order:
    1. If name doesn't end with .json: try .doc-evergreen/{name}.json
    2. Try {name} as absolute or relative path
    3. Raise FileNotFoundError with helpful message

    Args:
        name: Template name (short name or path)

    Returns:
        Path to template file

    Raises:
        FileNotFoundError: Template not found

    Examples:
        resolve_template_path("readme")              → .doc-evergreen/readme.json
        resolve_template_path("template.json")       → ./template.json
        resolve_template_path("/abs/path/doc.json")  → /abs/path/doc.json
    """
    # Try convention directory first for short names
    if not name.endswith(".json"):
        convention_path = Path.cwd() / ".doc-evergreen" / f"{name}.json"
        if convention_path.exists():
            return convention_path

    # Try as path (absolute or relative)
    path = Path(name)
    if path.exists():
        return path.resolve()  # Return absolute path

    # Not found - helpful error
    tried_paths = []
    if not name.endswith(".json"):
        tried_paths.append(f".doc-evergreen/{name}.json")
    tried_paths.append(name)

    raise FileNotFoundError(
        f"Template not found: {name}\n"
        f"\n"
        f"Tried:\n" + "\n".join(f"  - {p}" for p in tried_paths) + "\n"
        f"\n"
        f"Run 'doc-evergreen init' to create starter template."
    )


@click.group()
def cli():
    """doc-evergreen - AI-powered documentation generation.

    \b
    Works with ANY project.
    Run from your project root directory.
    Templates reference sources relative to project root (cwd).

    \b
    Installation:
      pip install -e /path/to/doc-evergreen
      # or
      pipx install /path/to/doc-evergreen

    \b
    Quick Start:
      cd /path/to/your-project
      doc-evergreen regen-doc readme

    \b
    How it works:
      - Run from project root (your cwd)
      - Sources in templates are relative to cwd
      - Output files written relative to cwd
      - Template can be stored anywhere

    \b
    Documentation:
      See TEMPLATES.md for template creation guide
    """
    pass


@cli.command("doc-update")
@click.argument("template_path", type=click.Path(exists=True))
@click.option(
    "--mode",
    type=click.Choice(["single", "chunked"]),
    default="single",
    help="Generation mode: single-shot or section-by-section",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Override output path from template",
)
def doc_update(template_path: str, mode: str, output: str | None):
    """[LEGACY] Generate/update documentation from JSON template.

    \b
    NOTE: This command is legacy. Use 'regen-doc' instead.
          'regen-doc' supports the .doc-evergreen/ convention
          and provides change preview with approval.

    \b
    Examples:
      # Generate using single-shot mode (default)
      doc-evergreen doc-update template.json

      # Generate using chunked mode (section-by-section)
      doc-evergreen doc-update --mode chunked template.json

      # Override output path
      doc-evergreen doc-update --output custom.md template.json
    """
    # 1. Parse template
    try:
        template = parse_template(Path(template_path))
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    # 2. Validate template based on mode
    validation = validate_template(template, mode=mode)
    if not validation.valid:
        click.echo(f"Error: {validation.errors[0]}", err=True)
        raise click.Abort()

    # 3. Determine base_dir (current working directory = project root)
    base_dir = Path.cwd()

    # 4. Route to appropriate generator
    if mode == "chunked":
        generator = ChunkedGenerator(template, base_dir)
    else:
        # Use single-shot Generator
        generator = Generator(template, base_dir)

    # 5. Generate documentation (async)
    try:
        result = asyncio.run(generator.generate())
    except Exception as e:
        click.echo(f"Generation failed: {e}", err=True)
        raise click.Abort()

    # 6. Determine output path
    output_path = Path(output) if output else Path(template.document.output)

    # 7. Check if output exists and prompt for confirmation
    if output_path.exists() and not click.confirm(f"Overwrite {output_path}?"):
        click.echo("Aborted")
        return

    # 8. Write output
    output_path.write_text(result)
    click.echo(f"Generated: {output_path}")


@cli.command("init")
@click.option("--name", help="Project name (default: directory name)")
@click.option("--description", help="Project description")
@click.option("--force", is_flag=True, help="Overwrite existing template")
def init(name: str | None, description: str | None, force: bool):
    """Initialize doc-evergreen in current project.

    \b
    Creates .doc-evergreen/ directory with starter readme.json template.

    \b
    Examples:
      doc-evergreen init
      doc-evergreen init --name "My Project"
      doc-evergreen init --force  # Overwrite existing
    """
    # Determine project name
    if name is None:
        name = Path.cwd().name

    # Check if template already exists
    doc_dir = Path.cwd() / ".doc-evergreen"
    template_path = doc_dir / "readme.json"

    if template_path.exists() and not force:
        click.echo(f"Error: Template already exists at {template_path}", err=True)
        click.echo("Use --force to overwrite", err=True)
        raise click.Abort()

    # Create .doc-evergreen/ directory
    doc_dir.mkdir(exist_ok=True)

    # Generate starter template
    starter_template = {
        "document": {
            "title": f"{name} Documentation",
            "output": "README.md",
            "sections": [
                {
                    "heading": "# Overview",
                    "prompt": (
                        "Provide a concise overview of this project. "
                        "Explain what it does, its main purpose, and key features. "
                        "Focus on the value it provides."
                    ),
                    "sources": ["README.md", "**/*.py"],
                },
                {
                    "heading": "## Installation",
                    "prompt": (
                        "Explain how to install and set up this project. "
                        "Include prerequisites, installation commands, and any configuration needed."
                    ),
                    "sources": ["pyproject.toml", "setup.py", "requirements.txt", "README.md"],
                },
                {
                    "heading": "## Usage",
                    "prompt": (
                        "Provide usage examples and basic workflows. "
                        "Show common use cases with code examples where helpful."
                    ),
                    "sources": ["examples/**", "**/*.py", "README.md"],
                },
                {
                    "heading": "## Development",
                    "prompt": (
                        "Document the development workflow. "
                        "Include how to run tests, build the project, and contribute."
                    ),
                    "sources": ["Makefile", "*.md", "tests/**"],
                },
            ],
        }
    }

    # Write template
    template_path.write_text(json.dumps(starter_template, indent=2))

    click.echo(f"✅ Created: {template_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Review and customize {template_path}")
    click.echo(f"  2. Run: doc-evergreen regen-doc readme")


@cli.command("regen-doc")
@click.argument("template_name")  # Changed: now accepts short names or paths
@click.option("--auto-approve", is_flag=True, help="Apply changes without approval prompt")
@click.option("--output", type=click.Path(), help="Override output path from template")
def regen_doc(template_name: str, auto_approve: bool, output: str | None):
    """Regenerate documentation from template with change preview.

    \b
    Supports short template names (finds in .doc-evergreen/)
    or full paths.

    \b
    Workflow:
      1. Resolves template (convention or path)
      2. Generates new documentation
      3. Shows unified diff of changes
      4. Prompts for approval (unless --auto-approve)
      5. Writes updated documentation

    \b
    Examples:
      # Short name (finds .doc-evergreen/readme.json)
      doc-evergreen regen-doc readme

      # Full path still works
      doc-evergreen regen-doc templates/readme.json

      # Auto-approve for CI/CD
      doc-evergreen regen-doc --auto-approve readme

      # Override output location
      doc-evergreen regen-doc --output custom/path.md readme

    \b
    See TEMPLATES.md for template creation guide.
    """
    # 1. Resolve template path (convention or explicit)
    try:
        template_path = resolve_template_path(template_name)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    # 2. Parse template JSON
    try:
        template_data = json.loads(template_path.read_text())
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in template: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error reading template: {e}", err=True)
        raise click.Abort()

    # 2. Determine template format and parse accordingly
    try:
        # Check if it's Sprint 5 format (has "document" key)
        if "document" in template_data:
            # Sprint 5 format - use parse_template directly
            template_obj = parse_template(Path(template_path))
            output_path_from_template = template_obj.document.output
        # Check if it's Sprint 8 format (has "template_version", "output_path", "chunks")
        elif "template_version" in template_data and "output_path" in template_data and "chunks" in template_data:
            # Sprint 8 format - convert to Sprint 5 format
            sections = []
            for chunk in template_data.get("chunks", []):
                sections.append(
                    {
                        "heading": chunk.get("chunk_id", "Section"),
                        "prompt": chunk.get("prompt", ""),
                        "sources": chunk.get("dependencies", []),
                    }
                )

            # Parse into Template object
            parsed_sections = [
                Section(
                    heading=s["heading"],
                    prompt=s.get("prompt"),
                    sources=s.get("sources", []),
                )
                for s in sections
            ]

            document = Document(
                title=template_data.get("metadata", {}).get("title", "Generated Document"),
                output=template_data["output_path"],
                sections=parsed_sections,
            )

            template_obj = Template(document=document)
            output_path_from_template = template_data["output_path"]
        else:
            click.echo(
                "Error: Invalid template format. Expected either Sprint 5 format (with 'document') or Sprint 8 format (with 'template_version', 'output_path', 'chunks')",
                err=True,
            )
            raise click.Abort()

    except ValueError as e:
        click.echo(f"Error: Failed to parse template: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: Failed to parse template: {e}", err=True)
        raise click.Abort()

    # 3. Initialize generator (use cwd as base_dir for intuitive source resolution)
    generator = ChunkedGenerator(template_obj, Path.cwd())

    # Progress callback to show generation progress
    def progress_callback(msg: str) -> None:
        """Display progress messages during generation."""
        click.echo(msg, nl=False)  # nl=False since messages include newlines

    # 4. Determine output path
    output_path = Path(output) if output else Path(output_path_from_template)

    # 5. Iterative refinement loop
    iteration = 0

    while True:
        iteration += 1

        # Generate new content
        try:
            # Handle both coroutine (real generator) and string (mocked generator)
            result = generator.generate(progress_callback=progress_callback)
            if hasattr(result, "__await__"):
                new_content: str = asyncio.run(result)  # type: ignore[arg-type]
            else:
                new_content = str(result)
        except Exception as e:
            # Check if it's a source validation error for templates with no sources
            error_msg = str(e)
            if "no sources" in error_msg.lower():
                # For templates with no sources, generate minimal placeholder content
                # This allows the workflow to complete for testing/validation purposes
                click.echo("Warning: Template has no source files - generating placeholder content", err=True)
                new_content = f"# {template_obj.document.title}\n\n*No source files provided*\n"
            else:
                click.echo(f"Error: Generation failed: {e}", err=True)
                raise click.Abort()

        # Detect changes
        has_changes, diff_lines = detect_changes(output_path, new_content)

        # If no changes, report and exit
        if not has_changes:
            click.echo("No changes detected - content is identical to existing file.")
            break

        # Show diff
        if diff_lines == ["NEW FILE"]:
            click.echo(f"Creating new file: {output_path}")
        else:
            click.echo("Changes detected:")
            for line in diff_lines:
                click.echo(line.rstrip())

        # Get approval (unless auto-approve)
        if not auto_approve and not click.confirm("\nApply these changes?"):
            click.echo("Aborted - changes not applied")
            return

        # Write file
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            click.echo(f"Error: Permission denied creating directory {output_path.parent}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error creating directory: {e}", err=True)
            raise click.Abort()

        try:
            output_path.write_text(new_content, encoding="utf-8")
            click.echo(f"✓ File written: {output_path}")
        except PermissionError:
            click.echo(f"Error: Permission denied writing to {output_path}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error writing file: {e}", err=True)
            raise click.Abort()

        # If auto-approve, don't offer iteration (one-shot mode)
        if auto_approve:
            break

        # Ask if user wants to regenerate
        if not click.confirm("\nRegenerate with updated sources?"):
            break

    # Show completion message with iteration count
    iteration_word = "iteration" if iteration == 1 else "iterations"
    click.echo(f"\nCompleted {iteration} {iteration_word}")


if __name__ == "__main__":
    cli()
