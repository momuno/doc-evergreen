"""
Sprint 5: CLI Interface for Template-Based Documentation Generation

Supports section-by-section documentation generation with explicit prompts.
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


def _get_output_path(template_meta) -> str:
    """Extract output path from template for display.
    
    Note: This is a display helper. Actual output path comes from loading full template.
    For --list, we show a representative path based on template type.
    
    Args:
        template_meta: TemplateMetadata instance
        
    Returns:
        Representative output path string for display
    """
    # Common patterns based on template name
    if template_meta.name.startswith("tutorial-quickstart"):
        return "QUICKSTART.md"
    elif template_meta.name.startswith("howto-contributing"):
        return "CONTRIBUTING.md"
    elif template_meta.name.startswith("howto-ci"):
        return "docs/CI_INTEGRATION.md"
    elif template_meta.name.startswith("howto-custom"):
        return "docs/PROMPT_GUIDE.md"
    elif template_meta.name.startswith("reference-cli"):
        return "docs/CLI_REFERENCE.md"
    elif template_meta.name.startswith("reference-api"):
        return "docs/API.md"
    elif template_meta.name.startswith("explanation-architecture"):
        return "docs/ARCHITECTURE.md"
    elif template_meta.name.startswith("explanation-concepts"):
        return "docs/CONCEPTS.md"
    elif template_meta.name.startswith("tutorial-first"):
        return "docs/FIRST_TEMPLATE.md"
    else:
        return "README.md"  # Default fallback


def interactive_template_selection(registry) -> str | None:
    """Display interactive template menu and get user selection.
    
    Shows templates organized by Divio documentation quadrants with emoji
    indicators. User can select by number (1-9) or quit with 'q'.
    
    Args:
        registry: TemplateRegistry instance
        
    Returns:
        Template name (e.g., "tutorial-quickstart") if selected
        None if user quits
        
    Example:
        >>> from doc_evergreen.template_registry import TemplateRegistry
        >>> registry = TemplateRegistry()
        >>> # User would see interactive menu
        >>> name = interactive_template_selection(registry)
    """
    # Get all templates
    templates = registry.list_templates()
    
    if not templates:
        click.echo("No templates available in registry.")
        return None
    
    # Group templates by quadrant
    quadrants = {
        "tutorial": [],
        "howto": [],
        "reference": [],
        "explanation": [],
    }
    
    for template in templates:
        if template.quadrant in quadrants:
            quadrants[template.quadrant].append(template)
    
    # Build display with numbering
    click.echo("\n? What type of documentation do you want to create?\n")
    
    template_map = {}  # Maps number to template name
    current_number = 1
    
    # Define quadrant display info
    quadrant_info = {
        "tutorial": ('📚 TUTORIALS (Learning-oriented - "Take me on a journey")', "tutorial"),
        "howto": ('🎯 HOW-TO GUIDES (Goal-oriented - "Show me how to...")', "howto"),
        "reference": ('📖 REFERENCE (Information-oriented - "Tell me facts")', "reference"),
        "explanation": ('💡 EXPLANATION (Understanding-oriented - "Help me understand")', "explanation"),
    }
    
    # Display templates by quadrant
    for quadrant_key in ["tutorial", "howto", "reference", "explanation"]:
        if quadrants[quadrant_key]:
            display_name, _ = quadrant_info[quadrant_key]
            click.echo(f"{display_name}")
            
            for template in quadrants[quadrant_key]:
                # Format: "  1. template-name - Description (200-400 lines)"
                click.echo(f"  {current_number}. {template.name} - {template.description} ({template.estimated_lines})")
                template_map[str(current_number)] = template.name
                current_number += 1
            
            click.echo()  # Blank line between quadrants
    
    # Get user input with validation loop
    while True:
        try:
            choice = click.prompt("Choose [1-9] or 'q' to quit", type=str, show_default=False)
            
            # Handle quit
            if choice.lower() == 'q':
                return None
            
            # Validate number choice
            if choice in template_map:
                return template_map[choice]
            else:
                click.echo(f"Invalid choice. Please enter a number between 1 and {len(template_map)} or 'q' to quit.")
        except click.Abort:
            # User pressed Ctrl+C
            return None


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
    """Generate documentation from templates organized by the Divio Documentation System.

    \b
    Quick Start:
      # Interactive template selection (recommended)
      $ doc-evergreen init
      
      # List all available templates
      $ doc-evergreen init --list
      
      # Use a specific template
      $ doc-evergreen init --template tutorial-quickstart
      
      # Generate documentation
      $ doc-evergreen regen-doc <template-name>
    """
    pass


@cli.command("init")
@click.option("--list", "list_templates", is_flag=True, help="List all available templates with descriptions")
@click.option("--template", help="Template name (e.g., tutorial-quickstart)")
@click.option("--yes", is_flag=True, help="Skip all confirmation prompts")
@click.option("--force", is_flag=True, help="Overwrite existing template without asking")
@click.option("--name", help="[DEPRECATED] Project name - use template customization instead")
@click.option("--description", help="[DEPRECATED] Project description - use template customization instead")
def init(
    list_templates: bool,
    template: str | None,
    yes: bool,
    force: bool,
    name: str | None,
    description: str | None,
):
    """Initialize doc-evergreen with a template.
    
    By default, shows an interactive menu to help you choose the right template
    based on your documentation needs. Templates are organized by the Divio
    Documentation System (Tutorials, How-to Guides, Reference, Explanation).
    
    \b
    Examples:
    
        # Interactive selection (recommended)
        $ doc-evergreen init
        
        # List all templates
        $ doc-evergreen init --list
        
        # Use specific template
        $ doc-evergreen init --template tutorial-quickstart
        
        # Non-interactive with default
        $ doc-evergreen init --yes
    """
    from doc_evergreen.template_registry import TemplateRegistry, TemplateNotFoundError
    
    # Import TemplateValidationError at the top if needed later
    from doc_evergreen.template_registry import TemplateValidationError

    # Initialize registry
    registry = TemplateRegistry()

    # Handle --list flag
    if list_templates:
        templates = registry.list_templates()
        
        if not templates:
            click.echo("No templates available in registry.")
            click.echo("\nTemplates will be added in Sprint 1.3.")
            return
        
        click.echo("\nAvailable templates (grouped by Divio quadrant):\n")
        
        # Group templates by quadrant with enhanced display
        quadrants = {
            "tutorial": ("📚 TUTORIALS", 'Learning-oriented - "Take me on a journey"'),
            "howto": ("🎯 HOW-TO GUIDES", 'Goal-oriented - "Show me how to..."'),
            "reference": ("📖 REFERENCE", 'Information-oriented - "Tell me facts"'),
            "explanation": ("💡 EXPLANATION", 'Understanding-oriented - "Help me understand"')
        }
        
        # Display templates by quadrant
        for quadrant_key, (emoji_title, description) in quadrants.items():
            # Get templates for this quadrant
            quadrant_templates = [t for t in templates if t.quadrant == quadrant_key]
            
            if quadrant_templates:
                click.echo(f"{emoji_title} ({description})")
                for template in quadrant_templates:
                    click.echo(f"  {template.name}")
                    click.echo(f"    {template.description}")
                    click.echo(f"    Output: {_get_output_path(template)} | Estimated: {template.estimated_lines}")
                    click.echo(f"    Use when: {template.use_case}")
                    click.echo()  # Blank line between templates
                click.echo()  # Blank line between quadrants
        
        click.echo("💡 Tip: Not sure which to use? Run 'doc-evergreen init' for interactive selection.\n")
        return

    # Determine template name
    # Priority: --template flag > --name flag (deprecated) > interactive selection > default
    if template:
        # User specified template via --template flag
        template_name = template
    elif name:
        # Legacy --name flag (deprecated but supported)
        click.echo("Warning: --name is deprecated, use --template instead")
        template_name = name
    elif yes:
        # --yes without --template: use default (skip interactive)
        template_name = "tutorial-quickstart"
    else:
        # Interactive mode - show menu and get selection
        template_name = interactive_template_selection(registry)
        
        # User cancelled
        if template_name is None:
            click.echo("Cancelled.")
            return

    # Load template from registry
    try:
        template_with_meta = registry.load_template(template_name)
    except TemplateNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nRun 'doc-evergreen init --list' to see available templates.", err=True)
        raise click.Abort()
    except TemplateValidationError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    # Show template info
    meta = template_with_meta.meta
    click.echo(f"Template: {meta.name}")
    click.echo(f"Description: {meta.description}")
    click.echo(f"Use case: {meta.use_case}")
    click.echo(f"Quadrant: {meta.quadrant}")
    click.echo(f"Estimated lines: {meta.estimated_lines}")
    click.echo()

    # Determine output path
    doc_dir = Path.cwd() / ".doc-evergreen"
    template_path = doc_dir / f"{template_name}.json"

    # Check if template already exists
    already_confirmed = False
    if template_path.exists() and not force:
        click.echo(f"Template already exists: {template_path}", err=True)
        if not yes and not click.confirm("Overwrite existing template?"):
            click.echo("Aborted", err=True)
            raise click.Abort()
        already_confirmed = True  # User confirmed overwrite, don't ask again

    # Ask for confirmation (unless --yes or already confirmed overwrite)
    if not yes and not already_confirmed:
        if not click.confirm(f"\nWrite template to {template_path}?"):
            click.echo("Aborted")
            return

    # Create .doc-evergreen/ directory
    doc_dir.mkdir(exist_ok=True)

    # Write template to file
    template_json = {
        "_meta": {
            "name": meta.name,
            "description": meta.description,
            "use_case": meta.use_case,
            "quadrant": meta.quadrant,
            "estimated_lines": meta.estimated_lines,
        },
        "document": {
            "title": template_with_meta.template.document.title,
            "output": template_with_meta.template.document.output,
            "sections": _sections_to_dict(template_with_meta.template.document.sections),
        },
    }

    template_path.write_text(json.dumps(template_json, indent=2))

    click.echo(f"✅ Created: {template_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Review and customize {template_path}")
    click.echo(f"  2. Run: doc-evergreen regen-doc {template_name}")


def _sections_to_dict(sections) -> list[dict]:
    """Convert Section objects to dictionaries for JSON serialization."""
    result = []
    for section in sections:
        section_dict = {
            "heading": section.heading,
        }
        if section.prompt is not None:
            section_dict["prompt"] = section.prompt
        if section.sources:
            section_dict["sources"] = section.sources
        if section.sections:
            section_dict["sections"] = _sections_to_dict(section.sections)
        result.append(section_dict)
    return result


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
